$python = 'D:/Anaconda/envs/nedge/python.exe'
$projectRoot = 'D:/space_intelligent'
$config = 'D:/space_intelligent/configs/pipeline.json'
$workspace = 'D:/space_intelligent/workspace/blender_stage'

Write-Host '=== Next Stage ==='
Write-Host "project_root: $projectRoot"
Write-Host "workspace: $workspace"
Write-Host ''

Write-Host '=== Background Dry Run ==='
& $python 'D:/space_intelligent/scripts/prepare_background.py' --config $config
Write-Host ''

Write-Host '=== Scene Startup Files ==='
Write-Host 'workspace/blender_stage/README.md'
Write-Host 'workspace/blender_stage/import_manifest.md'
Write-Host ''

Write-Host '=== Current Main Inputs ==='
Write-Host 'A: outputs/object_a_3dgs/point_cloud/iteration_7000/point_cloud.ply'
Write-Host 'B: external/threestudio/outputs/object_b_text3d/.../save/it5000-export/object_b_5000_textured.obj'
Write-Host 'C: external/threestudio/outputs/object_c_zero123/[64]_foreground.png/save/it600-export/object_c_600_obj.obj'
