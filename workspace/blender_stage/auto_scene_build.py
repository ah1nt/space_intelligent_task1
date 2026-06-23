import math
from pathlib import Path

import bpy
from mathutils import Vector


WORKSPACE = Path(r"D:\space_intelligent\workspace\blender_stage")
OUTPUT_BLEND = WORKSPACE / "scene_assembly_v001.blend"
OUTPUT_LOG = WORKSPACE / "scene_assembly_v001_log.txt"

BACKGROUND_CANDIDATES = [
    Path(r"D:\space_intelligent\outputs\background_3dgs_low_resource\point_cloud\iteration_5000\point_cloud.ply"),
    Path(r"D:\space_intelligent\outputs\background_3dgs_low_resource\point_cloud\iteration_3000\point_cloud.ply"),
]
A_PATH = Path(r"D:\space_intelligent\outputs\object_a_3dgs\point_cloud\iteration_7000\point_cloud.ply")
B_PATH = Path(
    r"D:\space_intelligent\external\threestudio\outputs\object_b_text3d\a_cute_toy_robot,_white_ceramic_body,_round_head,_two_glowing_blue_eyes,_simple_silhouette,_centered,_studio_lighting\save\it5000-export\object_b_5000_textured.obj"
)
C_PATH = Path(
    r"D:\space_intelligent\external\threestudio\outputs\object_c_zero123\[64]_foreground.png\save\it600-export\object_c_600_obj.obj"
)


def log(message: str) -> None:
    print(message)
    with OUTPUT_LOG.open("a", encoding="utf-8") as f:
        f.write(message + "\n")


def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def imported_objects(before_names):
    return [obj for obj in bpy.data.objects if obj.name not in before_names]


def import_ply(filepath: Path, name: str):
    before = {obj.name for obj in bpy.data.objects}
    bpy.ops.wm.ply_import(filepath=str(filepath))
    new_objects = imported_objects(before)
    if not new_objects:
        raise RuntimeError(f"PLY import created no objects: {filepath}")
    obj = new_objects[0]
    obj.name = name
    log(f"Imported PLY: {filepath}")
    return obj


def import_obj(filepath: Path, name: str):
    before = {obj.name for obj in bpy.data.objects}
    bpy.ops.wm.obj_import(filepath=str(filepath))
    new_objects = imported_objects(before)
    if not new_objects:
        raise RuntimeError(f"OBJ import created no objects: {filepath}")
    obj = new_objects[0]
    obj.name = name
    log(f"Imported OBJ: {filepath}")
    return obj


def world_bbox(obj):
    return [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]


def min_z(obj) -> float:
    return min(v.z for v in world_bbox(obj))


def set_ground(obj, z: float = 0.0) -> None:
    obj.location.z += z - min_z(obj)
    bpy.context.view_layer.update()


def max_dimension(obj) -> float:
    bpy.context.view_layer.update()
    return max(obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)


def scale_to_max_dimension(obj, target: float) -> None:
    current = max_dimension(obj)
    if current <= 0 or target <= 0:
        return
    factor = target / current
    obj.scale = [s * factor for s in obj.scale]
    bpy.context.view_layer.update()


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


def position_objects(a_obj, b_obj, c_obj, ref_size: float) -> None:
    a_obj.location.x = 0.0
    a_obj.location.y = 0.0
    set_ground(a_obj)

    b_obj.location.x = ref_size * 1.2
    b_obj.location.y = ref_size * 0.15
    set_ground(b_obj)

    c_obj.location.x = -ref_size * 1.2
    c_obj.location.y = ref_size * 0.15
    set_ground(c_obj)
    bpy.context.view_layer.update()


def add_camera_and_light(focus_objects, ref_size: float) -> None:
    target = center_of_objects(focus_objects)

    cam_data = bpy.data.cameras.new("SceneCamera")
    cam_obj = bpy.data.objects.new("SceneCamera", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location = (0.0, -ref_size * 4.5, ref_size * 2.3)

    empty = bpy.data.objects.new("SceneTarget", None)
    empty.location = target
    bpy.context.scene.collection.objects.link(empty)

    constraint = cam_obj.constraints.new(type="TRACK_TO")
    constraint.target = empty
    constraint.track_axis = "TRACK_NEGATIVE_Z"
    constraint.up_axis = "UP_Y"
    bpy.context.scene.camera = cam_obj

    light_data = bpy.data.lights.new("KeySun", type="SUN")
    light_obj = bpy.data.objects.new("KeySun", light_data)
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.rotation_euler = (math.radians(50), 0.0, math.radians(35))
    light_data.energy = 3.0


def configure_scene() -> None:
    scene = bpy.context.scene
    scene.unit_settings.system = "NONE"
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False


def main() -> None:
    OUTPUT_LOG.write_text("", encoding="utf-8")
    log("Starting Blender scene build")
    clear_scene()
    configure_scene()

    background_obj = None
    for candidate in BACKGROUND_CANDIDATES:
        if not candidate.exists():
            continue
        try:
            background_obj = import_ply(candidate, "BG_ENV")
            set_ground(background_obj)
            log(f"Background selected: {candidate}")
            break
        except Exception as exc:
            log(f"Background import failed: {candidate} :: {exc}")

    if background_obj is None:
        raise RuntimeError("No usable background PLY could be imported")

    a_obj = import_ply(A_PATH, "OBJ_A_REF")
    set_ground(a_obj)
    ref_size = max_dimension(a_obj)
    if ref_size <= 0:
        ref_size = 1.0
    log(f"A reference size: {ref_size:.4f}")

    b_obj = import_obj(B_PATH, "OBJ_B")
    scale_to_max_dimension(b_obj, ref_size * 0.60)
    set_ground(b_obj)

    c_obj = import_obj(C_PATH, "OBJ_C")
    scale_to_max_dimension(c_obj, ref_size * 0.70)
    set_ground(c_obj)

    position_objects(a_obj, b_obj, c_obj, ref_size)
    add_camera_and_light([a_obj, b_obj, c_obj], ref_size)

    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))
    log(f"Saved blend: {OUTPUT_BLEND}")
    log("Scene build completed")


if __name__ == "__main__":
    main()
