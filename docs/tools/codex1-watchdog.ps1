# Keeps Codex 1 (Windows) working: whenever no codex exec run is active, start a FRESH session (small context) with the
# standing CONTINUE order. Only a usage-limit error rests (until the reset); any other exit relaunches after 20 s.
# Stop: create C:\Users\momoy\Projects\Catchline\Art\Models\CrewV2\_STOP-WATCHDOGS
$p = 'C:\Users\momoy\Projects\Catchline'; Set-Location $p
$session = '01a16d97-9539-7711-b0d2-959b78ebf3bd'
$log = "$p\Art\Models\CrewV2\_codex1-watchdog.log"
$orders = "$p\Art\Source\UIv2\CONTINUE-CODEX1.txt"; $wake = "$p\Art\Models\CrewV2\_WAKE-CODEX1"
# Rest after a short run (empty quota, error or nothing queued) until the first of: 10 minutes, a new brief in the
# orders file, the team guard's wake file, or 30 s after the usage reset the guard last read (team daemon state).
function Rest {
    $stamp = (Get-Item $orders).LastWriteTimeUtc; $until = (Get-Date).AddSeconds(600); $back = $null
    try {
        $r = (Get-Content '\\wsl.localhost\Ubuntu\home\mo\.cache\team\state.json' -Raw | ConvertFrom-Json).rows.codex1
        if ($r.state -ne 'OUT') { $r = $r.last }
        if ($r -and $r.state -eq 'OUT' -and $r.back) { $back = [DateTimeOffset]::FromUnixTimeSeconds([long]$r.back).LocalDateTime; $until = $back.AddSeconds(30) }
    } catch {}
    Add-Content $log "$(Get-Date -Format s) rest until $(Get-Date $until -Format s)"
    while ((Get-Date) -lt $until -and -not (Test-Path "$p\Art\Models\CrewV2\_STOP-WATCHDOGS")) {
        if (Test-Path $wake) { Remove-Item $wake -ErrorAction SilentlyContinue; break }
        if (-not $back -and (Get-Item $orders).LastWriteTimeUtc -ne $stamp) { break }
        Start-Sleep 15
    }
}
[Console]::OutputEncoding = [Text.Encoding]::UTF8; $OutputEncoding = [Text.Encoding]::UTF8
function CodexBin { (Get-ChildItem "$env:LOCALAPPDATA\OpenAI\Codex\bin\*\codex.exe" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName }
function Running { @(Get-CimInstance Win32_Process -Filter "Name='codex.exe'" | Where-Object { $_.CommandLine -match '_codex1.last-message' }).Count -gt 0 }
while (-not (Test-Path "$p\Art\Models\CrewV2\_STOP-WATCHDOGS")) {
    if (Running) { Start-Sleep 60; continue }
    # Model and effort are re-read every launch from docs\tools\codex-model.conf (Mo: Sol 6.1 medium).
    $conf = @{}; Get-Content "$p\docs\tools\codex-model.conf" | ForEach-Object { $k, $v = $_ -split '=', 2; if ($v) { $conf[$k.Trim()] = $v.Trim() } }
    Remove-Item $wake -ErrorAction SilentlyContinue; $start = Get-Date; Add-Content $log "$(Get-Date -Format s) launch $($conf.MODEL) $($conf.EFFORT)"
    $a = @('exec','-C',$p,'-m',$conf.MODEL,'-c',"model_reasoning_effort=`"$($conf.EFFORT)`"",'-c','model_auto_compact_token_limit=120000','-o',"$p\Art\Models\CrewV2\_codex1\last-message.txt",'-')
    Get-Content "$p\Art\Source\UIv2\CONTINUE-CODEX1.txt" -Raw -Encoding UTF8 | & (CodexBin) @a 2>&1 | Out-File "$p\Art\Models\CrewV2\_codex1\watchdog-run.log" -Encoding utf8
    $took = ((Get-Date) - $start).TotalSeconds
    $tail = (Get-Content "$p\Art\Models\CrewV2\_codex1\watchdog-run.log" -Tail 3) -join ' '
    Add-Content $log "$(Get-Date -Format s) exit $LASTEXITCODE after $([int]$took)s: $tail"
    # Mo (10-26): never sit idle on a timer. Rest only when Codex reports its usage limit; otherwise go again.
    if ($tail -match 'usage limit') { Rest } else { Start-Sleep 20 }
}
Add-Content $log "$(Get-Date -Format s) stop file found, watchdog exits"
