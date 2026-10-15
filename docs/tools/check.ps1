param([string]$Name = 'resume', [string]$Method = 'Catchline.EditorTools.PrototypeTools.VoyageSim', [int]$Voyages = 30, [int]$Showcase = 0)
$ErrorActionPreference = 'Stop'
$source = 'C:\Users\momoy\Projects\Catchline'
$scratch = 'C:\Users\momoy\Projects\Catchline-sim'
$unity = 'C:\Program Files\Unity\Hub\Editor\6000.3.25f1\Editor\Unity.exe'
if (!(Test-Path "$scratch\ProjectSettings\ProjectVersion.txt")) { throw 'Missing scratch Unity project' }
robocopy "$source\Assets" "$scratch\Assets" /MIR /XD Resources /NFL /NDL /NJH /NJS | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Asset copy failed: $LASTEXITCODE" }
$log = "$scratch\Logs\check-$Name.log"
$shot = "$scratch\Logs\$Name.png"
$arguments = @('-batchmode', '-quit', '-projectPath', "`"$scratch`"", '-executeMethod', $Method, '-voyages', $Voyages, '-showcase', $Showcase, '-snapshotPath', "`"$shot`"", '-logFile', "`"$log`"")
$process = Start-Process -FilePath $unity -ArgumentList $arguments -PassThru -WindowStyle Hidden
$process.WaitForExit()
Get-Content $log | Select-String '\[Catchline\]|error CS|Exception|executeMethod'
if (Select-String -Path $log -Pattern 'error CS|Skiff check failed|First voyage check failed|executeMethod.*(could not|failed)|NullReferenceException') { throw 'Unity check failed; read log' }
$expected = if ($Method.Contains('SkiffChecks.')) { 'SKIFF CHECKS PASSED' } elseif ($Method.EndsWith('FirstVoyageChecks.Run')) { 'FIRST VOYAGE CHECKS PASSED' } elseif ($Method.EndsWith('FirstVoyageChecks.Regression')) { 'FIRST VOYAGE REGRESSION PASSED' } elseif ($Method.EndsWith('FirstVoyageChecks.BuildPreview')) { 'PLAYABLE PREVIEW BUILT:' } else { 'Snapshot written to' }
if (!(Select-String -Path $log -SimpleMatch $expected)) { throw "Missing completion evidence; Unity exit $($process.ExitCode)" }
Write-Output "Verified $Name (Unity exit $($process.ExitCode)); log $log"
