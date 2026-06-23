from __future__ import annotations

from pathlib import Path

from torch.utils.cpp_extension import load


def main() -> None:
    repo_root = Path(r"D:\space_intelligent\external\tiny-cuda-nn")
    bindings_root = repo_root / "bindings" / "torch"

    sources = [
        bindings_root / "tinycudann" / "bindings.cpp",
        repo_root / "dependencies" / "fmt" / "src" / "format.cc",
        repo_root / "dependencies" / "fmt" / "src" / "os.cc",
        repo_root / "src" / "cpp_api.cu",
        repo_root / "src" / "common_host.cu",
        repo_root / "src" / "encoding.cu",
        repo_root / "src" / "object.cu",
        repo_root / "src" / "network.cu",
        repo_root / "src" / "cutlass_mlp.cu",
        repo_root / "src" / "fully_fused_mlp.cu",
    ]

    include_dirs = [
        str(repo_root / "include"),
        str(repo_root / "dependencies"),
        str(repo_root / "dependencies" / "cutlass" / "include"),
        str(repo_root / "dependencies" / "cutlass" / "tools" / "util" / "include"),
        str(repo_root / "dependencies" / "fmt" / "include"),
    ]

    definitions = [
        "-DTCNN_PARAMS_UNALIGNED",
        "-DTCNN_MIN_GPU_ARCH=120",
        "-DFMT_UNICODE=0",
    ]

    extra_cflags = [
        "/std:c++17",
        "/utf-8",
        *definitions,
    ]

    extra_cuda_cflags = [
        "-std=c++17",
        "--extended-lambda",
        "--expt-relaxed-constexpr",
        "-Xcompiler",
        "/utf-8",
        "-U__CUDA_NO_HALF_OPERATORS__",
        "-U__CUDA_NO_HALF_CONVERSIONS__",
        "-U__CUDA_NO_HALF2_OPERATORS__",
        "-gencode=arch=compute_120,code=compute_120",
        "-gencode=arch=compute_120,code=sm_120",
        *definitions,
    ]

    module = load(
        name="tinycudann_120_C",
        sources=[str(path) for path in sources],
        extra_include_paths=include_dirs,
        extra_cflags=extra_cflags,
        extra_cuda_cflags=extra_cuda_cflags,
        extra_ldflags=["cuda.lib"],
        verbose=True,
        with_cuda=True,
    )
    print("built:", module.__name__)


if __name__ == "__main__":
    main()
