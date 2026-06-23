$ErrorActionPreference = 'Continue'
$PSNativeCommandUseErrorActionPreference = $false

$env:TORCH_CUDA_ARCH_LIST = '12.0'
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'

$python = 'D:/Anaconda/envs/nedge/python.exe'
$train = 'D:/space_intelligent/external/gaussian-splatting-win/train.py'
$log = 'D:/space_intelligent/outputs/object_a_3dgs/train_quality_resume.log'

$arguments = @(
    $train,
    '-M', 'gs_w',
    '-s', 'D:/space_intelligent/data/object_a/gs_source',
    '-m', 'D:/space_intelligent/outputs/object_a_3dgs',
    '--load_iter', '3000',
    '--iterations', '10000',
    '--densify_until_iter', '3000',
    '--save_iterations', '7000', '10000',
    '--test_iterations', '7000', '10000',
    '--checkpoint_iterations', '7000', '10000'
)

& $python @arguments *>&1 | Tee-Object -FilePath $log
