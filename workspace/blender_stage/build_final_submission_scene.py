import math
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector


WORKSPACE = Path(r"D:\space_intelligent\workspace\blender_stage")
OUTPUT_BLEND = WORKSPACE / "scene_submission_final.blend"
BACKGROUND_IMAGE = Path(r"D:\space_intelligent\data\background\garden\images_8\DSC07956.JPG")


def get_required_object(name: str):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Required object not found: {name}")
    return obj


def delete_object(name: str):
    obj = bpy.data.objects.get(name)
    if obj is None:
        return
    bpy.data.objects.remove(obj, do_unlink=True)


def world_bbox(obj):
    return [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]


def min_z(obj) -> float:
    return min(v.z for v in world_bbox(obj))


def set_ground(obj, z: float = 0.0) -> None:
    bpy.context.view_layer.update()
    obj.location.z += z - min_z(obj)
    bpy.context.view_layer.update()


def ensure_simple_material(obj, material_name: str, base_color, roughness=0.45, metallic=0.0):
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        mat = bpy.data.materials.new(material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type="ShaderNodeOutputMaterial")
    principled = nodes.new(type="ShaderNodeBsdfPrincipled")
    principled.inputs["Base Color"].default_value = base_color
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Specular IOR Level"].default_value = 0.35
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return mat


def ensure_image_emission_material(material_name: str, image_path: Path):
    mat = bpy.data.materials.get(material_name)
    if mat is None:
        mat = bpy.data.materials.new(material_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type="ShaderNodeOutputMaterial")
    emission = nodes.new(type="ShaderNodeEmission")
    tex = nodes.new(type="ShaderNodeTexImage")
    tex_coord = nodes.new(type="ShaderNodeTexCoord")
    tex.image = bpy.data.images.load(str(image_path), check_existing=True)
    emission.inputs["Strength"].default_value = 1.0
    links.new(tex_coord.outputs["UV"], tex.inputs["Vector"])
    links.new(tex.outputs["Color"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    return mat


def ensure_background_plane(camera_obj):
    plane_name = "BG_IMAGE_PLANE"
    plane = bpy.data.objects.get(plane_name)
    if plane is None:
        mesh = bpy.data.meshes.new(plane_name)
        mesh.from_pydata(
            [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)],
            [],
            [(0, 1, 2, 3)],
        )
        plane = bpy.data.objects.new(plane_name, mesh)
        bpy.context.scene.collection.objects.link(plane)
    mesh = plane.data
    uv_layer = mesh.uv_layers.get("UVMap") or mesh.uv_layers.new(name="UVMap")
    uv_coords = [(1.0, 0.0), (0.0, 0.0), (0.0, 1.0), (1.0, 1.0)]
    for loop, uv in zip(mesh.loops, uv_coords):
        uv_layer.data[loop.index].uv = uv
    plane.parent = None
    plane.location = (0.0, 340.0, 150.0)
    plane.rotation_euler = (-math.pi / 2.0, 0.0, 0.0)

    image = bpy.data.images.load(str(BACKGROUND_IMAGE), check_existing=True)
    aspect = image.size[0] / max(image.size[1], 1)
    plane.scale = (220.0 * aspect, 220.0, 1.0)
    mat = ensure_image_emission_material("BG_image_emission", BACKGROUND_IMAGE)
    if plane.data.materials:
        plane.data.materials[0] = mat
    else:
        plane.data.materials.append(mat)
    return plane


def ensure_table_disc():
    table_name = "FUSION_TABLE"
    obj = bpy.data.objects.get(table_name)
    if obj is None:
        mesh = bpy.data.meshes.new(table_name)
        bm = bmesh.new()
        bmesh.ops.create_cone(
            bm,
            cap_ends=True,
            cap_tris=False,
            segments=64,
            radius1=112.0,
            radius2=112.0,
            depth=4.0,
        )
        bm.to_mesh(mesh)
        bm.free()
        obj = bpy.data.objects.new(table_name, mesh)
        bpy.context.scene.collection.objects.link(obj)

    obj.location = (0.0, 18.0, 7.0)
    obj.rotation_euler = (0.0, 0.0, 0.0)
    ensure_simple_material(obj, "Fusion_table_wood", (0.19, 0.12, 0.07, 1.0), roughness=0.78)
    return obj


def ensure_a_point_proxy(a_obj):
    delete_object("OBJ_A_PROXY")
    delete_object("OBJ_A_POINT_PROXY")

    source_vertices = a_obj.data.vertices
    vertex_count = len(source_vertices)
    if vertex_count == 0:
        raise RuntimeError("OBJ_A_REF has no vertices")

    sample_target = 900
    step = max(vertex_count // sample_target, 1)
    sampled = [source_vertices[i].co.copy() for i in range(0, vertex_count, step)]

    mesh = bpy.data.meshes.new("OBJ_A_POINT_PROXY")
    proxy = bpy.data.objects.new("OBJ_A_POINT_PROXY", mesh)
    bpy.context.scene.collection.objects.link(proxy)

    radius = max(a_obj.dimensions) / 80.0
    bm = bmesh.new()
    for co in sampled:
        result = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=radius)
        bmesh.ops.translate(bm, verts=result["verts"], vec=co)
    bm.to_mesh(mesh)
    bm.free()

    proxy.matrix_world = a_obj.matrix_world.copy()
    for poly in proxy.data.polygons:
        poly.use_smooth = True
    ensure_simple_material(proxy, "A_point_proxy_mat", (0.87, 0.87, 0.90, 1.0), roughness=0.58)

    a_obj.hide_render = True
    a_obj.hide_viewport = True
    return proxy


def configure_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.eevee.taa_render_samples = 32
    scene.world.use_nodes = True
    world_nodes = scene.world.node_tree.nodes
    bg = world_nodes.get("Background")
    if bg is not None:
        bg.inputs[0].default_value = (0.02, 0.02, 0.025, 1.0)
        bg.inputs[1].default_value = 0.2


def setup_camera_and_lights(target_location: Vector):
    cam = get_required_object("SceneCamera")
    target = get_required_object("SceneTarget")
    target.location = target_location

    cam.parent = None
    cam.location = (0.0, -465.0, 168.0)
    cam.rotation_euler = (math.radians(74.0), 0.0, 0.0)
    cam.data.type = "PERSP"
    cam.data.lens = 34

    for constraint in list(cam.constraints):
        if constraint.type == "TRACK_TO":
            cam.constraints.remove(constraint)
    track = cam.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    sun = get_required_object("KeySun")
    sun.rotation_euler = (math.radians(47.0), 0.0, math.radians(-18.0))
    if hasattr(sun.data, "energy"):
        sun.data.energy = 4.8

    fill = bpy.data.objects.get("FillArea")
    if fill is None:
        light_data = bpy.data.lights.new("FillArea", type="AREA")
        fill = bpy.data.objects.new("FillArea", light_data)
        bpy.context.scene.collection.objects.link(fill)
    fill.location = (0.0, -160.0, 180.0)
    fill.rotation_euler = (math.radians(75.0), 0.0, 0.0)
    fill.data.energy = 1600
    fill.data.shape = "RECTANGLE"
    fill.data.size = 260
    fill.data.size_y = 180

    return cam


def arrange_assets(a_proxy, b_obj, c_obj, table_obj):
    a_proxy.location = (-86.0, 18.0, a_proxy.location.z)
    a_proxy.scale = tuple(v * 1.18 for v in a_proxy.scale)
    set_ground(a_proxy, table_obj.location.z + 2.0)

    b_obj.location = (0.0, 18.0, b_obj.location.z)
    b_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(4.0))
    set_ground(b_obj, table_obj.location.z + 2.1)

    c_obj.location = (86.0, 18.0, c_obj.location.z)
    c_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(-10.0))
    c_obj.scale = tuple(v * 1.08 for v in c_obj.scale)
    set_ground(c_obj, table_obj.location.z + 2.1)


def main():
    configure_scene()

    bg_env = get_required_object("BG_ENV")
    bg_env.hide_render = True
    bg_env.hide_viewport = True

    a_obj = get_required_object("OBJ_A_REF")
    a_obj.hide_render = False
    a_obj.hide_viewport = False
    b_obj = get_required_object("OBJ_B")
    c_obj = get_required_object("OBJ_C")
    ensure_simple_material(c_obj, "C_formal_clay", (0.89, 0.47, 0.20, 1.0), roughness=0.55)

    table_obj = ensure_table_disc()
    a_proxy = ensure_a_point_proxy(a_obj)
    arrange_assets(a_proxy, b_obj, c_obj, table_obj)

    target_location = Vector((0.0, 24.0, 52.0))
    cam = setup_camera_and_lights(target_location)
    ensure_background_plane(cam)

    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))


if __name__ == "__main__":
    main()
