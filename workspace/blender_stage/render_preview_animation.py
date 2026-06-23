import math
from pathlib import Path

import bpy
from mathutils import Vector


WORKSPACE = Path(r"D:\space_intelligent\workspace\blender_stage")
CURRENT_BLEND = Path(bpy.data.filepath) if bpy.data.filepath else WORKSPACE / "scene_preview.blend"
OUTPUT_VIDEO = CURRENT_BLEND.with_name(f"{CURRENT_BLEND.stem}_preview.mp4")
OUTPUT_BLEND = CURRENT_BLEND
FRAMES_DIR = WORKSPACE / f"{CURRENT_BLEND.stem}_preview_frames"


def world_bbox(obj):
    return [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]


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


def get_or_create_camera():
    cam = bpy.data.objects.get("SceneCamera")
    if cam is not None:
        return cam
    cam_data = bpy.data.cameras.new("SceneCamera")
    cam = bpy.data.objects.new("SceneCamera", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


def build_orbit(objects):
    center = center_of_objects(objects)
    extent = max_scene_extent(objects)

    cam = get_or_create_camera()

    target = bpy.data.objects.get("SceneTarget")
    if target is None:
        target = bpy.data.objects.new("SceneTarget", None)
        bpy.context.scene.collection.objects.link(target)
    target.location = center

    orbit = bpy.data.objects.get("CameraOrbit")
    if orbit is None:
        orbit = bpy.data.objects.new("CameraOrbit", None)
        bpy.context.scene.collection.objects.link(orbit)
    orbit.location = center
    orbit.rotation_euler = (0.0, 0.0, 0.0)

    cam.parent = orbit
    cam.matrix_parent_inverse = orbit.matrix_world.inverted()
    cam.location = (0.0, -extent * 3.8, extent * 1.8)

    for constraint in list(cam.constraints):
        if constraint.type == "TRACK_TO":
            cam.constraints.remove(constraint)

    track = cam.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    return orbit


def configure_preview():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.fps = 12
    scene.frame_start = 1
    scene.frame_end = 18
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = str(FRAMES_DIR / "frame_")

    eevee = scene.eevee
    eevee.taa_render_samples = 8


def animate_orbit(orbit):
    orbit.rotation_euler = (0.0, 0.0, 0.0)
    orbit.keyframe_insert(data_path="rotation_euler", frame=1)

    orbit.rotation_euler = (0.0, 0.0, math.radians(30.0))
    orbit.keyframe_insert(data_path="rotation_euler", frame=18)


def main():
    objects = [obj for obj in bpy.data.objects if obj.name in {"OBJ_A_REF", "OBJ_B", "OBJ_C"}]
    if not objects:
        raise RuntimeError("Scene objects OBJ_A_REF / OBJ_B / OBJ_C not found")

    configure_preview()
    orbit = build_orbit(objects)
    animate_orbit(orbit)

    bpy.ops.wm.save_mainfile(filepath=str(OUTPUT_BLEND))
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
