# ONE Codex 1 (Windows) run: a FRESH session (small context) with the standing CONTINUE order. Mo (10-26): Codex never
# starts by itself, only a Claude starts it, with `team start codex1`. Nothing relaunches this run when it ends; the
# team guard reads the exit line below and rings the lead Claude, who reviews and decides whether to start the next.
param([string]$Starter = 'a Claude')
$p = 'C:\Users\momoy\Projects\Catchline'; Set-Location $p
$log = "$p\Art\Models\CrewV2\_codex1-watchdog.log"
[Console]::OutputEncoding = [Text.Encoding]::UTF8; $OutputEncoding = [Text.Encoding]::UTF8
function CodexBin { (Get-ChildItem "$env:LOCALAPPDATA\OpenAI\Codex\bin\*\codex.exe" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName }
function Running { @(Get-CimInstance Win32_Process -Filter "Name='codex.exe'" | Where-Object { $_.CommandLine -match '_codex1.last-message' }).Count -gt 0 }
if (Running) { Write-Output 'codex1 is already running'; exit 1 }
# Model and effort are re-read every launch from docs\tools\codex-model.conf (Mo: Sol 6.1 medium).
$conf = @{}; Get-Content "$p\docs\tools\codex-model.conf" | ForEach-Object { $k, $v = $_ -split '=', 2; if ($v) { $conf[$k.Trim()] = $v.Trim() } }
$start = Get-Date; Add-Content $log "$(Get-Date -Format s) launch $($conf.MODEL) $($conf.EFFORT) (started by $Starter)"
$a = @('exec','-C',$p,'-m',$conf.MODEL,'-c',"model_reasoning_effort=`"$($conf.EFFORT)`"",'-c','model_auto_compact_token_limit=120000','-o',"$p\Art\Models\CrewV2\_codex1\last-message.txt",'-')
Get-Content "$p\Art\Source\UIv2\CONTINUE-CODEX1.txt" -Raw -Encoding UTF8 | & (CodexBin) @a 2>&1 | Out-File "$p\Art\Models\CrewV2\_codex1\watchdog-run.log" -Encoding utf8
$code = $LASTEXITCODE; $took = ((Get-Date) - $start).TotalSeconds
$tail = (Get-Content "$p\Art\Models\CrewV2\_codex1\watchdog-run.log" -Tail 3) -join ' '
Add-Content $log "$(Get-Date -Format s) exit $code after $([int]$took)s: $tail"
