import math
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector


WORKSPACE = Path(r"D:\space_intelligent\workspace\blender_stage")
OUTPUT_BLEND = WORKSPACE / "scene_assembly_v003.blend"


def get_required_object(name: str):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Required object not found: {name}")
    return obj


def world_bbox(obj):
    return [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]


def min_z(obj) -> float:
    return min(v.z for v in world_bbox(obj))


def max_scene_extent(objects):
    points = []
    for obj in objects:
        points.extend(world_bbox(obj))
    if not points:
        return 1.0
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    zs = [p.z for p in points]
    return max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), 1.0)


def center_of_objects(objects):
    points = []
    for obj in objects:
        points.extend(world_bbox(obj))
    if not points:
        return Vector((0.0, 0.0, 0.0))
    total = Vector((0.0, 0.0, 0.0))
    for p in points:
        total += p
    return total / len(points)


def set_ground(obj, z: float = 0.0) -> None:
    bpy.context.view_layer.update()
    obj.location.z += z - min_z(obj)
    bpy.context.view_layer.update()


def ensure_simple_material(obj, material_name: str, base_color, roughness=0.45):
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
    principled.inputs["Specular IOR Level"].default_value = 0.3
    links.new(principled.outputs["BSDF"], output.inputs["Surface"])

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def ensure_a_visibility_proxy(a_obj):
    if len(a_obj.data.polygons) > 0:
        return a_obj

    proxy_name = "OBJ_A_PROXY"
    existing = bpy.data.objects.get(proxy_name)
    if existing is not None:
        existing.hide_viewport = False
        existing.hide_render = False
        a_obj.hide_viewport = True
        a_obj.hide_render = True
        return existing

    source_vertices = a_obj.data.vertices
    vertex_count = len(source_vertices)
    sample_target = 3500
    step = max(vertex_count // sample_target, 1)
    sampled = [source_vertices[i].co.copy() for i in range(0, vertex_count, step)]
    if len(sampled) < 4:
        return a_obj

    mesh = bpy.data.meshes.new(proxy_name)
    proxy = bpy.data.objects.new(proxy_name, mesh)
    bpy.context.scene.collection.objects.link(proxy)

    bm = bmesh.new()
    for co in sampled:
        bm.verts.new(co)
    bm.verts.ensure_lookup_table()
    bmesh.ops.convex_hull(bm, input=bm.verts[:])
    bm.to_mesh(mesh)
    bm.free()

    proxy.matrix_world = a_obj.matrix_world.copy()
    ensure_simple_material(proxy, "A_proxy_light", (0.92, 0.92, 0.95, 1.0), roughness=0.7)
    proxy.hide_viewport = False
    proxy.hide_render = False

    a_obj.hide_viewport = True
    a_obj.hide_render = True
    return proxy


def configure_world():
    scene = bpy.context.scene
    world = scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    bg = nodes.get("Background")
    if bg is not None:
        bg.inputs[0].default_value = (0.055, 0.055, 0.06, 1.0)
        bg.inputs[1].default_value = 0.9


def configure_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.eevee.taa_render_samples = 16
    configure_world()


def adjust_objects(a_obj, b_obj, c_obj):
    a_obj.location = Vector((-132.0, -2.0, a_obj.location.z))
    a_obj.scale = tuple(v * 1.65 for v in a_obj.scale)
    set_ground(a_obj)

    b_obj.location = Vector((0.0, 4.0, b_obj.location.z))
    b_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(8.0))
    set_ground(b_obj)

    c_obj.location = Vector((132.0, 8.0, c_obj.location.z))
    c_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(-12.0))
    c_obj.scale = tuple(v * 1.06 for v in c_obj.scale)
    set_ground(c_obj)


def hide_background_for_visibility(bg_obj):
    bg_obj.hide_render = True
    bg_obj.hide_viewport = True


def setup_camera_and_light(a_obj, b_obj, c_obj):
    focus_objects = [a_obj, b_obj, c_obj]
    center = center_of_objects(focus_objects)
    extent = max_scene_extent(focus_objects)

    target = get_required_object("SceneTarget")
    target.location = center + Vector((0.0, 2.0, 12.0))

    cam = get_required_object("SceneCamera")
    orbit = bpy.data.objects.get("CameraOrbit")
    if orbit is not None:
        orbit.location = target.location
        orbit.rotation_euler = (0.0, 0.0, 0.0)
        cam.parent = orbit
        cam.matrix_parent_inverse = orbit.matrix_world.inverted()

    cam.location = (0.0, -extent * 2.2, extent * 0.92)
    cam.data.type = "PERSP"
    cam.data.lens = 28

    for constraint in cam.constraints:
        if constraint.type == "TRACK_TO":
            constraint.target = target

    sun = get_required_object("KeySun")
    sun.rotation_euler = (math.radians(42.0), 0.0, math.radians(-22.0))
    if hasattr(sun.data, "energy"):
        sun.data.energy = 5.2


def main():
    configure_scene()

    bg_obj = get_required_object("BG_ENV")
    a_obj = get_required_object("OBJ_A_REF")
    b_obj = get_required_object("OBJ_B")
    c_obj = get_required_object("OBJ_C")
    a_visible = ensure_a_visibility_proxy(a_obj)

    hide_background_for_visibility(bg_obj)
    adjust_objects(a_visible, b_obj, c_obj)
    ensure_simple_material(b_obj, "B_visibility_blue", (0.25, 0.78, 0.92, 1.0), roughness=0.45)
    ensure_simple_material(c_obj, "C_visibility_orange", (0.95, 0.42, 0.12, 1.0), roughness=0.5)
    setup_camera_and_light(a_visible, b_obj, c_obj)

    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))


if __name__ == "__main__":
    main()
