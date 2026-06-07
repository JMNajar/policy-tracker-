# One-time setup: registers the daily pipeline as a Windows Task Scheduler task
# Run this script once as Administrator (or your user account with Task Scheduler access)

$TaskName   = "PolicyTrackerSignalPipeline"
$ScriptPath = Join-Path $PSScriptRoot "run.ps1"
$NodePath   = (Get-Command node -ErrorAction SilentlyContinue)?.Source

if (-not $NodePath) {
    Write-Error "Node.js not found in PATH. Install Node.js first."
    exit 1
}

# Remove existing task if present
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

$Action  = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NonInteractive -ExecutionPolicy Bypass -File `"$ScriptPath`""

$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "6:30AM"

$Settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -MultipleInstances IgnoreNew

$Task = Register-ScheduledTask `
    -TaskName  $TaskName `
    -Action    $Action `
    -Trigger   $Trigger `
    -Settings  $Settings `
    -RunLevel  Highest `
    -Description "GFTO AI Compliance Engine: every Monday 6:30AM — detects signal risk changes, regenerates NotebookLM videos, uploads to YouTube, embeds on policy tracker homepage automatically."

Write-Host "Task registered: $TaskName"
Write-Host "Runs: Every Monday at 6:30 AM (after GitHub Actions 5AM build deploys to Vercel)"
Write-Host "Script: $ScriptPath"
Write-Host ""
Write-Host "IMPORTANT — First-run auth setup required:"
Write-Host "  1. Run pipeline.js manually once: cd automation && node pipeline.js"
Write-Host "  2. When Chrome opens, sign in to jeff@horsepowerai.ai if prompted"
Write-Host "  3. The session is saved to automation\browser-profile\ for all future runs"
Write-Host ""
Write-Host "To run manually at any time:"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
