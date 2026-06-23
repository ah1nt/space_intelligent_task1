import math
from pathlib import Path

import bpy
from mathutils import Vector


WORKSPACE = Path(r"D:\space_intelligent\workspace\blender_stage")
OUTPUT_BLEND = WORKSPACE / "scene_assembly_v002.blend"


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


def set_location_xy(obj, x: float, y: float) -> None:
    obj.location.x = x
    obj.location.y = y
    bpy.context.view_layer.update()


def get_required_object(name: str):
    obj = bpy.data.objects.get(name)
    if obj is None:
        raise RuntimeError(f"Required object not found: {name}")
    return obj


def adjust_background(bg_obj, ref_extent: float) -> None:
    bg_obj.scale = (10.0, 10.0, 10.0)
    bpy.context.view_layer.update()
    set_location_xy(bg_obj, 10.0, ref_extent * 2.2)
    set_ground(bg_obj)


def adjust_subjects(a_obj, b_obj, c_obj) -> None:
    set_location_xy(a_obj, -22.0, -10.0)
    set_ground(a_obj)

    set_location_xy(b_obj, 56.0, 10.0)
    set_ground(b_obj)

    set_location_xy(c_obj, 108.0, 34.0)
    set_ground(c_obj)


def adjust_camera_and_light(a_obj, b_obj, c_obj) -> None:
    focus_objects = [a_obj, b_obj, c_obj]
    center = center_of_objects(focus_objects)
    extent = max_scene_extent(focus_objects)

    target = get_required_object("SceneTarget")
    target.location = center + Vector((0.0, 10.0, 10.0))

    orbit = bpy.data.objects.get("CameraOrbit")
    cam = get_required_object("SceneCamera")
    if orbit is not None:
        orbit.location = target.location
        orbit.rotation_euler = (0.0, 0.0, 0.0)
        cam.location = (0.0, -extent * 2.1, extent * 0.95)
    else:
        cam.location = (0.0, -extent * 2.1, extent * 0.95)

    cam.data.lens = 70

    sun = get_required_object("KeySun")
    if hasattr(sun.data, "energy"):
        sun.data.energy = 5.0
    sun.rotation_euler = (math.radians(46.0), 0.0, math.radians(18.0))


def configure_scene():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080


def main():
    configure_scene()

    bg_obj = get_required_object("BG_ENV")
    a_obj = get_required_object("OBJ_A_REF")
    b_obj = get_required_object("OBJ_B")
    c_obj = get_required_object("OBJ_C")

    ref_extent = max_scene_extent([a_obj, b_obj, c_obj])
    adjust_background(bg_obj, ref_extent)
    adjust_subjects(a_obj, b_obj, c_obj)
    adjust_camera_and_light(a_obj, b_obj, c_obj)

    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT_BLEND))


if __name__ == "__main__":
    main()
