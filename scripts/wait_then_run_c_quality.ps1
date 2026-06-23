$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false

$aPattern = 'D:/space_intelligent/external/gaussian-splatting-win/train.py'
$cScript = 'D:/space_intelligent/scripts/run_c_quality_resume.ps1'

while ($true) {
    $aProcesses = Get-CimInstance Win32_Process | Where-Object {
        $_.Name -eq 'python.exe' -and $_.CommandLine -like "*$aPattern*"
    }

    if (-not $aProcesses) {
        break
    }

    Write-Host ("[{0}] A training still running, wait 30s before starting C..." -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
    Start-Sleep -Seconds 30
}

Write-Host ("[{0}] A training finished, starting C quality resume..." -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
& $cScript
