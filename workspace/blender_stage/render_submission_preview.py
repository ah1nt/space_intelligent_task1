import math
from pathlib import Path

import bpy


WORKSPACE = Path(r"D:\space_intelligent\workspace\blender_stage")
CURRENT_BLEND = Path(bpy.data.filepath) if bpy.data.filepath else WORKSPACE / "scene_submission_final.blend"
FRAMES_DIR = WORKSPACE / f"{CURRENT_BLEND.stem}_preview_frames"


def configure_preview():
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.fps = 12
    scene.frame_start = 1
    scene.frame_end = 24
    scene.eevee.taa_render_samples = 16
    scene.render.image_settings.file_format = "PNG"
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(FRAMES_DIR / "frame_")


def ensure_orbit():
    cam = bpy.data.objects["SceneCamera"]
    target = bpy.data.objects["SceneTarget"]

    orbit = bpy.data.objects.get("SubmissionOrbit")
    if orbit is None:
        orbit = bpy.data.objects.new("SubmissionOrbit", None)
        bpy.context.scene.collection.objects.link(orbit)

    orbit.location = target.location
    orbit.rotation_euler = (0.0, 0.0, 0.0)

    cam.parent = orbit
    cam.matrix_parent_inverse = orbit.matrix_world.inverted()
    return orbit


def animate_camera(orbit):
    orbit.rotation_euler = (0.0, 0.0, math.radians(-6.0))
    orbit.keyframe_insert(data_path="rotation_euler", frame=1)

    orbit.rotation_euler = (0.0, 0.0, math.radians(6.0))
    orbit.keyframe_insert(data_path="rotation_euler", frame=24)


def main():
    configure_preview()
    orbit = ensure_orbit()
    animate_camera(orbit)
    bpy.ops.wm.save_mainfile(filepath=str(CURRENT_BLEND))
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main()
