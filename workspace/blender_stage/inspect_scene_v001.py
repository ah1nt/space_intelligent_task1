from pathlib import Path

import bpy
from mathutils import Vector


OUT = Path(r"D:\space_intelligent\workspace\blender_stage\scene_assembly_v001_inspection.txt")


def world_bbox(obj):
    return [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]


def bbox_summary(obj):
    pts = world_bbox(obj)
    xs = [p.x for p in pts]
    ys = [p.y for p in pts]
    zs = [p.z for p in pts]
    return {
        "min": (min(xs), min(ys), min(zs)),
        "max": (max(xs), max(ys), max(zs)),
    }


def write(line=""):
    with OUT.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def inspect_object(obj_name):
    obj = bpy.data.objects.get(obj_name)
    if obj is None:
        write(f"[MISSING] {obj_name}")
        return

    box = bbox_summary(obj)
    write(f"[OBJECT] {obj.name}")
    write(f"  type={obj.type}")
    write(f"  location={tuple(round(v, 4) for v in obj.location)}")
    write(f"  rotation_deg={tuple(round(v * 57.2958, 2) for v in obj.rotation_euler)}")
    write(f"  scale={tuple(round(v, 4) for v in obj.scale)}")
    write(f"  dimensions={tuple(round(v, 4) for v in obj.dimensions)}")
    write(f"  bbox_min={tuple(round(v, 4) for v in box['min'])}")
    write(f"  bbox_max={tuple(round(v, 4) for v in box['max'])}")
    write(f"  hide_viewport={obj.hide_viewport} hide_render={obj.hide_render}")
    if obj.type == "MESH":
        mesh = obj.data
        write(f"  verts={len(mesh.vertices)} faces={len(mesh.polygons)} materials={len(mesh.materials)}")
        for i, mat in enumerate(mesh.materials):
            if mat is None:
                write(f"    material[{i}]=None")
                continue
            write(f"    material[{i}]={mat.name}")
            if mat.use_nodes and mat.node_tree:
                images = []
                for node in mat.node_tree.nodes:
                    if node.type == "TEX_IMAGE" and getattr(node, "image", None):
                        images.append(node.image.filepath)
                if images:
                    for path in images:
                        write(f"      image={path}")


def inspect_camera():
    cam = bpy.context.scene.camera
    if cam is None:
        write("[MISSING] scene camera")
        return
    write(f"[CAMERA] {cam.name}")
    write(f"  location={tuple(round(v, 4) for v in cam.location)}")
    write(f"  rotation_deg={tuple(round(v * 57.2958, 2) for v in cam.rotation_euler)}")
    for constraint in cam.constraints:
        write(f"  constraint={constraint.type} target={getattr(constraint.target, 'name', None)}")


def inspect_world():
    world = bpy.context.scene.world
    if world is None:
        write("[WORLD] None")
        return
    write(f"[WORLD] {world.name}")
    write(f"  use_nodes={world.use_nodes}")


def main():
    OUT.write_text("", encoding="utf-8")
    write("[SCENE INSPECTION]")
    inspect_world()
    inspect_camera()
    for name in ["BG_ENV", "OBJ_A_REF", "OBJ_B", "OBJ_C", "SceneTarget", "KeySun"]:
        inspect_object(name)


if __name__ == "__main__":
    main()
