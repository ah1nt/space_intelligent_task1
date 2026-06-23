from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common import ensure_dir, load_config, print_block, project_root_from_config


def copy_tree_contents(src_dir: Path, dst_dir: Path) -> None:
    ensure_dir(dst_dir)
    for item in src_dir.iterdir():
        dst = dst_dir / item.name
        if item.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(item, dst)
        else:
            shutil.copy2(item, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync object A COLMAP outputs into 3DGS source layout.")
    parser.add_argument("--config", default="d:/space_intelligent/configs/pipeline.json")
    parser.add_argument("--execute", action="store_true", help="Actually copy files.")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = project_root_from_config(config)

    object_root = project_root / "data" / "object_a"
    frame_dir = object_root / "frames"
    sparse_zero_dir = object_root / "colmap" / "sparse" / "0"
    gs_source_images = object_root / "gs_source" / "images"
    gs_source_sparse_zero = object_root / "gs_source" / "sparse" / "0"

    missing: list[str] = []
    if not frame_dir.exists():
        missing.append(str(frame_dir))
    if not sparse_zero_dir.exists():
        missing.append(str(sparse_zero_dir))

    print_block(
        "Object A Sync Paths",
        [
            f"frame_dir: {frame_dir}",
            f"sparse_zero_dir: {sparse_zero_dir}",
            f"gs_source_images: {gs_source_images}",
            f"gs_source_sparse_zero: {gs_source_sparse_zero}",
        ],
    )

    if missing:
        print_block("Missing Inputs", missing)
        return

    print_block(
        "Sync Plan",
        [
            f"copy images -> {gs_source_images}",
            f"copy sparse/0 -> {gs_source_sparse_zero}",
        ],
    )

    if args.execute:
        copy_tree_contents(frame_dir, gs_source_images)
        copy_tree_contents(sparse_zero_dir, gs_source_sparse_zero)
        print("sync done")


if __name__ == "__main__":
    main()
