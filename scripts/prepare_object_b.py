from __future__ import annotations

import argparse
import os

from common import check_exists, load_config, print_block, project_root_from_config, resolve_command, resolve_path, run_command


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare object B with text-to-3D threestudio workflow.")
    parser.add_argument("--config", default="d:/space_intelligent/configs/pipeline.json")
    parser.add_argument("--execute", action="store_true", help="Execute command when repo path is configured.")
    args = parser.parse_args()

    config = load_config(args.config)
    project_root = project_root_from_config(config)
    object_cfg = config["object_b"]
    python_cmd = resolve_command(project_root, config["tools"].get("python", ""), "python")
    threestudio_root = resolve_path(project_root, config["repos"].get("threestudio", ""))
    output_root = project_root / "outputs" / object_cfg.get("workspace_name", "object_b_text3d")

    missing: list[str] = []
    check_exists(threestudio_root, "repos.threestudio", missing)

    print_block(
        "Object B Settings",
        [
            f"prompt: {object_cfg.get('prompt', '')}",
            f"threestudio_root: {threestudio_root or '<empty>'}",
            f"output_root: {output_root}",
        ],
    )

    command: list[str] | None = None
    if threestudio_root is not None:
        command = [
            python_cmd,
            str(threestudio_root / "launch.py"),
            "--config",
            str(threestudio_root / object_cfg.get("threestudio_config", "configs/prolificdreamer.yaml")),
            "--train",
            f"system.prompt_processor.prompt={object_cfg.get('prompt', '')}",
            "use_timestamp=false",
            f"name={object_cfg.get('workspace_name', 'object_b_text3d')}",
        ]
        for extra_arg in object_cfg.get("launch_args", []):
            command.append(str(extra_arg))

    print_block("Command Plan", [" ".join(command)] if command else ["暂无可生成命令"])

    if missing:
        print_block("Missing Config", missing)
        return

    if args.execute and command is not None:
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
