# Install (or remove) the daily job search as a Windows scheduled task.
#
#   powershell -ExecutionPolicy Bypass -File tools\schedule\install_daily_search.ps1
#   powershell -ExecutionPolicy Bypass -File tools\schedule\install_daily_search.ps1 -Candidate candidates/animesh_murai -Time 07:30
#   powershell -ExecutionPolicy Bypass -File tools\schedule\install_daily_search.ps1 -Uninstall
#
# The task runs as you, while you are signed in (a locked screen is fine). It
# wakes the laptop from sleep if Windows wake timers are allowed (Power
# Options > Sleep > Allow wake timers). If the laptop was off or the run was
# missed, it runs as soon as possible afterwards. Output goes to
# logs\discovery\daily_search.log, the digest to state\daily_jobs\latest.md.

param(
    [string]$Candidate = "candidates/animesh_murai",
    [string]$Time = "02:00",
    [switch]$Uninstall
)

$ErrorActionPreference = "Stop"
$TaskName = "JobApply Daily Search"
$Repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

if ($Uninstall) {
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
    Write-Host "Removed the scheduled task '$TaskName'."
    exit 0
}

$Python = Join-Path $Repo ".venv\Scripts\python.exe"
$Runner = Join-Path $Repo "tools\schedule\run_daily_search.cmd"
$Config = Join-Path $Repo (Join-Path $Candidate "job_search.json")
if (-not (Test-Path $Python)) { throw "Missing $Python. Create the virtual environment first (see requirements.txt)." }
if (-not (Test-Path $Runner)) { throw "Missing $Runner." }
if (-not (Test-Path $Config)) { throw "Missing $Config." }
New-Item -ItemType Directory -Force -Path (Join-Path $Repo "logs\discovery") | Out-Null

$Action = New-ScheduledTaskAction -Execute $Runner -Argument "`"$Candidate`"" -WorkingDirectory $Repo
$Trigger = New-ScheduledTaskTrigger -Daily -At $Time
$Settings = New-ScheduledTaskSettingsSet `
    -WakeToRun `
    -StartWhenAvailable `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -MultipleInstances IgnoreNew
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings `
    -Principal $Principal -Description "Searches job boards for $Candidate and writes state\daily_jobs\latest.md" `
    -Force | Out-Null

$Info = Get-ScheduledTask -TaskName $TaskName | Get-ScheduledTaskInfo
Write-Host "Installed '$TaskName': $Candidate every day at $Time. Next run: $($Info.NextRunTime)"
Write-Host "Run it now with:  Start-ScheduledTask -TaskName '$TaskName'"
