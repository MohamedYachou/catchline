# Copies Assets into the scratch project Catchline-lead-sim and runs one editor method in batchmode (never the main
# project). Waits while another run uses lead-sim. "exit 0" plus PASSED lines = success (exit 3 comes from the grep).
# Captures: set $env:CATCHLINE_SHOTS=<set> and run Catchline.EditorTools.LeadShots.Run (output docs/screens/overnight).
# From WSL: powershell.exe -File 'C:\Users\momoy\Projects\Catchline\docs\tools\run-lead-check.ps1' -Method <method>
param([string]$Method, [string]$Pattern = 'PASS|failed|error CS|Exception')
$scratch = 'C:\Users\momoy\Projects\Catchline-lead-sim\Logs'; New-Item -ItemType Directory -Force $scratch | Out-Null
$deadline = (Get-Date).AddMinutes(8)
while ((Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'Unity.exe' -and $_.CommandLine -match 'lead-sim' }) -and (Get-Date) -lt $deadline) { Start-Sleep 5 }
robocopy 'C:\Users\momoy\Projects\Catchline\Assets' 'C:\Users\momoy\Projects\Catchline-lead-sim\Assets' /MIR /XF ArtLibrary.asset ArtLibrary.asset.meta UiV2Preview.unity UiV2Preview.unity.meta LeadTour.cs LeadTour.cs.meta /XD Temp /NFL /NDL /NJH /NJS | Out-Null
$log = Join-Path $scratch ("check-" + ($Method -replace '.*\.', '') + ".log")
$args = @('-batchmode', '-quit', '-projectPath', '"C:\Users\momoy\Projects\Catchline-lead-sim"', '-logFile', "`"$log`"")
if ($Method) { $args += @('-executeMethod', $Method) }
$p = Start-Process 'C:\Program Files\Unity\Hub\Editor\6000.3.25f1\Editor\Unity.exe' -ArgumentList $args -PassThru -Wait
"exit $($p.ExitCode)"
Select-String -Path $log -Pattern $Pattern | Select-Object -First 30 | ForEach-Object { $_.Line.Substring(0, [Math]::Min(400, $_.Line.Length)) }
