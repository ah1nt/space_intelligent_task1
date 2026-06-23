from __future__ import annotations

import argparse
import os
from pathlib import Path

from common import check_exists, ensure_dir, load_config, print_block, project_root_from_config, resolve_command, resolve_path, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare object C with single-image Zero123 workflow.")
    parser.add_argument("--config", default="d:/space_intelligent/configs/pipeline.json")
    parser.add_argument("--execute", action="store_true", help="Execute command when repo path is configured.")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = project_root_from_config(config)
    object_cfg = config["object_c"]
    repo_cfg = config["repos"]
    python_cmd = resolve_command(project_root, config["tools"].get("python", ""), "python")

    object_root = ensure_dir(project_root / "data" / "object_c")
    input_root = ensure_dir(object_root / "inputs")
    prepared_root = ensure_dir(object_root / "prepared")
    output_root = project_root / "outputs" / object_cfg.get("workspace_name", "object_c_zero123")

    image_path = resolve_path(project_root, object_cfg.get("image_path", ""))
    foreground_image_path = resolve_path(project_root, object_cfg.get("foreground_image_path", ""))
    mask_path = resolve_path(project_root, object_cfg.get("mask_path", ""))
    threestudio_root = resolve_path(project_root, repo_cfg.get("threestudio", ""))
    zero123_root = resolve_path(project_root, repo_cfg.get("zero123", ""))

    missing: list[str] = []
    if image_path is None:
        missing.append("object_c.image_path")
    if foreground_image_path is None:
        missing.append("object_c.foreground_image_path")
    check_exists(threestudio_root, "repos.threestudio", missing)

    print_block(
        "Object C Paths",
        [
            f"image_path: {image_path or '<empty>'}",
            f"foreground_image_path: {foreground_image_path or '<empty>'}",
            f"mask_path: {mask_path or '<empty>'}",
            f"input_root: {input_root}",
            f"prepared_root: {prepared_root}",
            f"output_root: {output_root}",
            f"zero123_root: {zero123_root or '<optional>'}",
        ],
    )

    if foreground_image_path is not None:
        print_block(
            "Foreground Requirement",
            [
                "建议使用已经去背景的 PNG 前景图作为 Zero123 输入。",
                "如已有 alpha 通道，可直接将该文件填入 object_c.foreground_image_path。",
                f"可将最终输入放入: {prepared_root / 'foreground.png'}",
            ],
        )

    command: list[str] | None = None
    if threestudio_root is not None and foreground_image_path is not None:
        command = [
            python_cmd,
            str(threestudio_root / "launch.py"),
            "--config",
            str(threestudio_root / object_cfg.get("threestudio_zero123_config", "configs/zero123.yaml")),
            "--train",
            f"data.image_path={foreground_image_path}",
            "use_timestamp=false",
            f"name={object_cfg.get('workspace_name', 'object_c_zero123')}",
        ]

    print_block("Command Plan", [" ".join(command)] if command else ["暂无可生成命令"])

    if missing:
        print_block("Missing Config", missing)
        return

    if args.execute and command is not None:
        ensure_dir(threestudio_root / "custom")
        extra_paths = [str(threestudio_root), str(threestudio_root.parent / "tiny-cuda-nn" / "bindings" / "torch")]
        existing_pythonpath = os.environ.get("PYTHONPATH", "")
        pythonpath_entries = [path for path in extra_paths if path]
        if existing_pythonpath:
            pythonpath_entries.append(existing_pythonpath)
        msvc_bin = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\bin\HostX64\x64"
        windows_sdk_bin = r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64"
        msvc_include = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\include"
        msvc_aux_include = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\VS\include"
        windows_sdk_includes = [
            r"C:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt",
            r"C:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um",
            r"C:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared",
            r"C:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt",
            r"C:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt",
        ]
        msvc_lib = r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207\lib\x64"
        windows_sdk_libs = [
            r"C:\Program Files (x86)\Windows Kits\10\lib\10.0.26100.0\ucrt\x64",
            r"C:\Program Files (x86)\Windows Kits\10\lib\10.0.26100.0\um\x64",
        ]
        path_entries = [msvc_bin, windows_sdk_bin]
        existing_path = os.environ.get("PATH", "")
        if existing_path:
            path_entries.append(existing_path)
        include_entries = [msvc_include, msvc_aux_include, *windows_sdk_includes]
        existing_include = os.environ.get("INCLUDE", "")
        if existing_include:
            include_entries.append(existing_include)
        lib_entries = [msvc_lib, *windows_sdk_libs]
        existing_lib = os.environ.get("LIB", "")
        if existing_lib:
            lib_entries.append(existing_lib)
        run_command(
            command,
            cwd=threestudio_root,
            env_extra={
                "PYTHONPATH": os.pathsep.join(pythonpath_entries),
                "PATH": os.pathsep.join(path_entries),
                "INCLUDE": os.pathsep.join(include_entries),
                "LIB": os.pathsep.join(lib_entries),
                "TORCH_CUDA_ARCH_LIST": "12.0",
            },
        )


if __name__ == "__main__":
    main()
