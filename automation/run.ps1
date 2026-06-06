# Policy Tracker Signal Pipeline — Daily Runner
# Called by Windows Task Scheduler at 8:00 AM

$AutoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = Join-Path $AutoDir "pipeline.log"

Add-Content $LogFile "[$((Get-Date).ToString('o'))] === Task Scheduler triggered ==="

Set-Location $AutoDir

# Install dependencies if node_modules is missing
if (-not (Test-Path "node_modules")) {
    Add-Content $LogFile "[$((Get-Date).ToString('o'))] Installing npm dependencies..."
    npm install 2>&1 | Out-File $LogFile -Append
}

# Run the pipeline
node pipeline.js 2>&1 | Out-File $LogFile -Append

Add-Content $LogFile "[$((Get-Date).ToString('o'))] === Run complete. Exit: $LASTEXITCODE ==="
