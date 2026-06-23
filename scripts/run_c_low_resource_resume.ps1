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
$config = 'D:/space_intelligent/external/threestudio/configs/zero123.yaml'
$resume = 'D:/space_intelligent/external/threestudio/outputs/object_c_zero123/[64]_foreground.png/ckpts/last.ckpt'
$image = 'D:/space_intelligent/data/object_c/prepared/foreground.png'
$log = 'D:/space_intelligent/outputs/object_c_zero123_low_resource.log'

$arguments = @(
    $launch,
    '--config', $config,
    '--train',
    "resume=$resume",
    "data.image_path=$image",
    'use_timestamp=false',
    'name=object_c_zero123_low_resource',
    '--gpu', '0',
    'data.height=[96,128]',
    'data.width=[96,128]',
    'data.resolution_milestones=[400]',
    'data.random_camera.height=[64,96]',
    'data.random_camera.width=[64,96]',
    'data.random_camera.batch_size=[1,1]',
    'data.random_camera.resolution_milestones=[400]',
    'data.random_camera.eval_height=256',
    'data.random_camera.eval_width=256',
    'data.random_camera.n_val_views=4',
    'data.random_camera.n_test_views=12',
    'system.renderer.num_samples_per_ray=96',
    'system.loss.lambda_normal_smooth=0.0',
    'system.loss.lambda_3d_normal_smooth=0.0',
    'trainer.max_steps=900',
    'trainer.val_check_interval=200',
    'checkpoint.every_n_train_steps=200'
)

Push-Location $launchCwd
try {
    & $python @arguments *>&1 | Tee-Object -FilePath $log
} finally {
    Pop-Location
}
