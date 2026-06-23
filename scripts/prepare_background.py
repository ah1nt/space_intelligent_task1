from __future__ import annotations

import argparse
from pathlib import Path

from common import check_exists, load_config, print_block, project_root_from_config, resolve_command, resolve_path, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare background scene with 3DGS.")
    parser.add_argument("--config", default="d:/space_intelligent/configs/pipeline.json")
    parser.add_argument("--execute", action="store_true", help="Execute command when repo path is configured.")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = project_root_from_config(config)
    scene_cfg = config["background"]
    python_cmd = resolve_command(project_root, config["tools"].get("python", ""), "python")
    gs_root = resolve_path(project_root, config["repos"].get("gaussian_splatting", ""))
    scene_path = resolve_path(project_root, scene_cfg.get("scene_path", ""))
    output_root = project_root / "outputs" / scene_cfg.get("workspace_name", "background_3dgs")
    launch_args = [str(arg) for arg in scene_cfg.get("launch_args", [])]

    missing: list[str] = []
    check_exists(gs_root, "repos.gaussian_splatting", missing)
    check_exists(scene_path, "background.scene_path", missing)

    print_block(
        "Background Scene",
        [
            f"scene_name: {scene_cfg.get('scene_name', '')}",
            f"scene_path: {scene_path or '<empty>'}",
            f"output_root: {output_root}",
        ],
    )

    command: list[str] | None = None
    if gs_root is not None and scene_path is not None:
        command = [
            python_cmd,
            str(gs_root / "train.py"),
            "-s",
            str(scene_path),
            "-m",
            str(output_root),
            *launch_args,
        ]

    print_block("Command Plan", [" ".join(command)] if command else ["暂无可生成命令"])

    if missing:
        print_block("Missing Config", missing)
        return

    if args.execute and command is not None:
        pycache_root = project_root / ".pycache"
        pycache_root.mkdir(parents=True, exist_ok=True)
        run_command(
            command,
            cwd=project_root,
            env_extra={
                "PYTHONDONTWRITEBYTECODE": "1",
                "PYTHONPYCACHEPREFIX": str(Path(pycache_root)),
            },
        )


if __name__ == "__main__":
    main()
