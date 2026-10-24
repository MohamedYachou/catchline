# Keeps Codex 1 (Windows) working: whenever no codex exec run is active, resume its crew session with the
# standing CONTINUE order. A run that ends within 3 minutes means an empty quota or an error: wait 10 minutes.
# Stop: create C:\Users\momoy\Projects\Catchline\Art\Models\CrewV2\_STOP-WATCHDOGS
$p = 'C:\Users\momoy\Projects\Catchline'; Set-Location $p
$session = '01a16d97-9539-7711-b0d2-959b78ebf3bd'
$log = "$p\Art\Models\CrewV2\_codex1-watchdog.log"
[Console]::OutputEncoding = [Text.Encoding]::UTF8; $OutputEncoding = [Text.Encoding]::UTF8
function CodexBin { (Get-ChildItem "$env:LOCALAPPDATA\OpenAI\Codex\bin\*\codex.exe" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName }
function Running { @(Get-CimInstance Win32_Process -Filter "Name='codex.exe'" | Where-Object { $_.CommandLine -match '\bexec\b' }).Count -gt 0 }
while (-not (Test-Path "$p\Art\Models\CrewV2\_STOP-WATCHDOGS")) {
    if (Running) { Start-Sleep 60; continue }
    $start = Get-Date; Add-Content $log "$(Get-Date -Format s) launch"
    $a = @('exec','resume',$session,'-c','model_reasoning_effort="high"','-o',"$p\Art\Models\CrewV2\_codex1\last-message.txt",'-')
    Get-Content "$p\Art\Source\UIv2\CONTINUE-CODEX1.txt" -Raw -Encoding UTF8 | & (CodexBin) @a 2>&1 | Out-File "$p\Art\Models\CrewV2\_codex1\watchdog-run.log" -Encoding utf8
    $took = ((Get-Date) - $start).TotalSeconds
    $tail = (Get-Content "$p\Art\Models\CrewV2\_codex1\watchdog-run.log" -Tail 3) -join ' '
    Add-Content $log "$(Get-Date -Format s) exit $LASTEXITCODE after $([int]$took)s: $tail"
    if ($took -lt 180) { Start-Sleep 600 }
}
Add-Content $log "$(Get-Date -Format s) stop file found, watchdog exits"
