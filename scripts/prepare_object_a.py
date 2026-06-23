from __future__ import annotations

import argparse
from pathlib import Path

from common import check_exists, ensure_dir, load_config, print_block, project_root_from_config, resolve_command, resolve_path, run_command


def build_ffmpeg_command(ffmpeg_path: Path, video_path: Path, frame_dir: Path, frame_step: int) -> list[str]:
    frame_pattern = frame_dir / "frame_%05d.png"
    return [
        str(ffmpeg_path),
        "-i",
        str(video_path),
        "-vf",
        f"select=not(mod(n\\,{frame_step}))",
        "-vsync",
        "vfr",
        str(frame_pattern),
    ]


def build_colmap_commands(
    colmap_path: Path,
    image_dir: Path,
    database_path: Path,
    sparse_root: Path,
    camera_model: str,
    matcher: str,
) -> list[list[str]]:
    commands = [
        [
            str(colmap_path),
            "feature_extractor",
            "--database_path",
            str(database_path),
            "--image_path",
            str(image_dir),
            "--ImageReader.camera_model",
            camera_model,
            "--FeatureExtraction.use_gpu",
            "0",
        ]
    ]
    matcher_name = "sequential_matcher" if matcher == "sequential" else "exhaustive_matcher"
    commands.append(
        [
            str(colmap_path),
            matcher_name,
            "--database_path",
            str(database_path),
            "--FeatureMatching.use_gpu",
            "0",
        ]
    )
    commands.append(
        [
            str(colmap_path),
            "mapper",
            "--database_path",
            str(database_path),
            "--image_path",
            str(image_dir),
            "--output_path",
            str(sparse_root),
        ]
    )
    return commands


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare object A with COLMAP + 3DGS.")
    parser.add_argument("--config", default="d:/space_intelligent/configs/pipeline.json")
    parser.add_argument("--execute", action="store_true", help="Execute available steps instead of dry-run.")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = project_root_from_config(config)
    object_cfg = config["object_a"]
    tool_cfg = config["tools"]
    repo_cfg = config["repos"]
    python_cmd = resolve_command(project_root, tool_cfg.get("python", ""), "python")
    morph_name = object_cfg.get("morph", "")

    object_root = ensure_dir(project_root / "data" / "object_a")
    frame_dir = ensure_dir(object_root / "frames")
    colmap_root = ensure_dir(object_root / "colmap")
    sparse_root = ensure_dir(colmap_root / "sparse")
    gs_source_root = ensure_dir(object_root / "gs_source")
    ensure_dir(gs_source_root / "images")
    ensure_dir(gs_source_root / "sparse")
    database_path = colmap_root / "database.db"

    video_path = resolve_path(project_root, object_cfg.get("video_path", ""))
    raw_image_dir = resolve_path(project_root, object_cfg.get("image_dir", ""))
    image_dir = raw_image_dir or frame_dir
    ffmpeg_path = resolve_path(project_root, tool_cfg.get("ffmpeg", ""))
    colmap_path = resolve_path(project_root, tool_cfg.get("colmap", ""))
    gs_repo = resolve_path(project_root, repo_cfg.get("gaussian_splatting", ""))
    output_model_dir = project_root / "outputs" / "object_a_3dgs"

    missing: list[str] = []
    if video_path is None and raw_image_dir is None:
        missing.append("object_a.video_path 或 object_a.image_dir")
    check_exists(colmap_path, "tools.colmap", missing)
    check_exists(gs_repo, "repos.gaussian_splatting", missing)
    if video_path is not None:
        check_exists(ffmpeg_path, "tools.ffmpeg", missing)

    print_block(
        "Object A Paths",
        [
            f"project_root: {project_root}",
            f"video_path: {video_path or '<empty>'}",
            f"image_dir: {image_dir}",
            f"frame_dir: {frame_dir}",
            f"colmap_root: {colmap_root}",
            f"gs_source_root: {gs_source_root}",
            f"output_model_dir: {output_model_dir}",
        ],
    )

    commands: list[list[str]] = []
    if video_path is not None and ffmpeg_path is not None:
        commands.append(build_ffmpeg_command(ffmpeg_path, video_path, frame_dir, int(object_cfg.get("frame_step", 4))))
    if colmap_path is not None:
        commands.extend(
            build_colmap_commands(
                colmap_path=colmap_path,
                image_dir=image_dir,
                database_path=database_path,
                sparse_root=sparse_root,
                camera_model=object_cfg.get("camera_model", "OPENCV"),
                matcher=object_cfg.get("matcher", "sequential"),
            )
        )
    if gs_repo is not None:
        train_cmd = [
            python_cmd,
            str(gs_repo / "train.py"),
        ]
        if morph_name:
            train_cmd.extend(["-M", morph_name])
        train_cmd.extend(
            [
                "-s",
                str(gs_source_root),
                "-m",
                str(output_model_dir),
            ]
        )
        commands.append(train_cmd)

    print_block("Need Manual Sync", [f"复制或链接重建后的图片到: {gs_source_root / 'images'}", f"复制 COLMAP sparse/0 到: {gs_source_root / 'sparse' / '0'}"])
    print_block("Command Plan", [" ".join(cmd) for cmd in commands] if commands else ["暂无可生成命令"])

    if missing:
        print_block("Missing Config", missing)
        return

    if args.execute:
        for command in commands:
            run_command(command, cwd=project_root)


if __name__ == "__main__":
    main()
