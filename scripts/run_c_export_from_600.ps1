$ErrorActionPreference = 'Continue'
$PSNativeCommandUseErrorActionPreference = $false

$env:PYTHONPATH = 'D:/space_intelligent/external/threestudio;D:/space_intelligent/external/tiny-cuda-nn/bindings/torch'
$env:PATH = 'C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/HostX64/x64;C:/Program Files (x86)/Windows Kits/10/bin/10.0.26100.0/x64;' + $env:PATH
$env:INCLUDE = 'C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/include;C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/VS/include;C:/Program Files (x86)/Windows Kits/10/include/10.0.26100.0/ucrt;C:/Program Files (x86)/Windows Kits/10/include/10.0.26100.0/um;C:/Program Files (x86)/Windows Kits/10/include/10.0.26100.0/shared;C:/Program Files (x86)/Windows Kits/10/include/10.0.26100.0/winrt;C:/Program Files (x86)/Windows Kits/10/include/10.0.26100.0/cppwinrt;' + $env:INCLUDE
$env:LIB = 'C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/lib/x64;C:/Program Files (x86)/Windows Kits/10/lib/10.0.26100.0/ucrt/x64;C:/Program Files (x86)/Windows Kits/10/lib/10.0.26100.0/um/x64;' + $env:LIB
$env:TORCH_CUDA_ARCH_LIST = '12.0'
$env:PYTHONUTF8 = '1'
$env:TORCH_EXTENSIONS_DIR = 'D:/space_intelligent/.torch_extensions'
$env:MAX_JOBS = '1'

New-Item -ItemType Directory -Force -Path $env:TORCH_EXTENSIONS_DIR | Out-Null

$python = 'D:/Anaconda/envs/nedge/python.exe'
$launch = 'D:/space_intelligent/external/threestudio/launch.py'
$launchCwd = 'D:/space_intelligent/external/threestudio'
$config = 'D:/space_intelligent/external/threestudio/outputs/object_c_zero123/[64]_foreground.png/configs/parsed.yaml'
$resume = 'D:/space_intelligent/external/threestudio/outputs/object_c_zero123/[64]_foreground.png/ckpts/epoch=0-step=600.ckpt'
$log = 'D:/space_intelligent/outputs/object_c_export_from_600.log'

$arguments = @(
    $launch,
    '--config', $config,
    '--export',
    '--gpu', '0',
    "resume=$resume",
    'system.exporter_type=mesh-exporter',
    'system.exporter.context_type=cuda',
    'system.exporter.fmt=obj-mtl',
    'system.exporter.save_name=object_c_600_textured',
    'system.exporter.save_uv=true',
    'system.exporter.save_texture=true',
    'system.exporter.texture_size=1024'
)

Push-Location $launchCwd
try {
    & $python @arguments *>&1 | Tee-Object -FilePath $log
} finally {
    Pop-Location
}
