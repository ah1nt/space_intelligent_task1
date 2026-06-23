$ErrorActionPreference = 'Continue'
$PSNativeCommandUseErrorActionPreference = $false

$env:PYTHONPATH = 'D:/space_intelligent/external/threestudio;D:/space_intelligent/external/tiny-cuda-nn/bindings/torch'
$env:PATH = 'C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/bin/HostX64/x64;C:/Program Files (x86)/Windows Kits/10/bin/10.0.26100.0/x64;' + $env:PATH
$env:INCLUDE = 'C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/include;C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Auxiliary/VS/include;C:/Program Files (x86)/Windows Kits/10/include/10.0.26100.0/ucrt;C:/Program Files (x86)/Windows Kits/10/include/10.0.26100.0/um;C:/Program Files (x86)/Windows Kits/10/include/10.0.26100.0/shared;C:/Program Files (x86)/Windows Kits/10/include/10.0.26100.0/winrt;C:/Program Files (x86)/Windows Kits/10/include/10.0.26100.0/cppwinrt;' + $env:INCLUDE
$env:LIB = 'C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC/14.44.35207/lib/x64;C:/Program Files (x86)/Windows Kits/10/lib/10.0.26100.0/ucrt/x64;C:/Program Files (x86)/Windows Kits/10/lib/10.0.26100.0/um/x64;' + $env:LIB
$env:TORCH_CUDA_ARCH_LIST = '12.0'
$env:PYTHONUTF8 = '1'

$python = 'D:/Anaconda/envs/nedge/python.exe'
$launch = 'D:/space_intelligent/external/threestudio/launch.py'
$config = 'D:/space_intelligent/external/threestudio/configs/dreamfusion-sd.yaml'
$resume = 'D:/space_intelligent/external/threestudio/outputs/object_b_text3d/a_cute_toy_robot,_white_ceramic_body,_round_head,_two_glowing_blue_eyes,_simple_silhouette,_centered,_studio_lighting/ckpts/epoch=0-step=3000.ckpt'
$log = 'D:/space_intelligent/outputs/object_b_text3d/train_b_resume_5000.log'

$arguments = @(
    $launch,
    '--config', $config,
    '--train',
    "resume=$resume",
    'system.prompt_processor.prompt=a cute toy robot, white ceramic body, round head, two glowing blue eyes, simple silhouette, centered, studio lighting',
    'use_timestamp=false',
    'name=object_b_text3d',
    '--gpu', '0',
    'data.width=128',
    'data.height=128',
    'data.batch_size=1',
    'trainer.max_steps=5000',
    'trainer.val_check_interval=500',
    'checkpoint.every_n_train_steps=1000',
    'system.background.random_aug=true',
    'system.material.ambient_only_steps=400',
    'system.prompt_processor.pretrained_model_name_or_path=D:/space_intelligent/external/threestudio/load/stable-diffusion-2-base',
    'system.guidance.pretrained_model_name_or_path=D:/space_intelligent/external/threestudio/load/stable-diffusion-2-base'
)

& $python @arguments *>&1 | Tee-Object -FilePath $log
