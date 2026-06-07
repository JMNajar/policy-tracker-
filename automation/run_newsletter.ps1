# Policy Tracker — Weekly Newsletter Sender
# Called by Windows Task Scheduler every Monday at 9:00 AM

$AutoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogFile = Join-Path $AutoDir "newsletter.log"

Add-Content $LogFile "[$((Get-Date).ToString('o'))] === Newsletter task triggered ==="

Set-Location $AutoDir

node send_newsletter.js 2>&1 | Out-File $LogFile -Append

Add-Content $LogFile "[$((Get-Date).ToString('o'))] === Newsletter run complete. Exit: $LASTEXITCODE ==="
