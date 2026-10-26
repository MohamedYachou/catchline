param([string]$Name = 'resume', [string]$Method = 'Catchline.EditorTools.PrototypeTools.VoyageSim', [int]$Voyages = 30, [int]$Showcase = 0, [string]$Scratch = '')
$ErrorActionPreference = 'Stop'
$source = 'C:\Users\momoy\Projects\Catchline'
$scratch = if ([string]::IsNullOrWhiteSpace($Scratch)) { 'C:\Users\momoy\Projects\Catchline-sim' } else { $Scratch }
$unity = 'C:\Program Files\Unity\Hub\Editor\6000.3.25f1\Editor\Unity.exe'
if (!(Test-Path "$scratch\ProjectSettings\ProjectVersion.txt")) { throw 'Missing scratch Unity project' }
robocopy "$source\Assets" "$scratch\Assets" /MIR /XD Resources /NFL /NDL /NJH /NJS | Out-Null
if ($LASTEXITCODE -ge 8) { throw "Asset copy failed: $LASTEXITCODE" }
# Reference HUD assets load by Resources path; keep the generated scratch ArtLibrary.
if (Test-Path -LiteralPath "$source\Assets\Resources\FishReference") {
    Copy-Item -LiteralPath "$source\Assets\Resources\FishReference" -Destination "$scratch\Assets\Resources" -Recurse -Force
    Copy-Item -LiteralPath "$source\Assets\Resources\FishReference.meta" -Destination "$scratch\Assets\Resources\FishReference.meta" -Force
}
if (Test-Path -LiteralPath "$source\Assets\Resources\ManagementReference") {
    Copy-Item -LiteralPath "$source\Assets\Resources\ManagementReference" -Destination "$scratch\Assets\Resources" -Recurse -Force
}
Copy-Item "$source/docs/screens/cliffs-life-1/CliffsCapture.cs" "$scratch/Assets/Scripts/Game/CliffsCapture.cs" -Force
$log = "$scratch\Logs\check-$Name.log"
if (Test-Path -LiteralPath "$source\Assets\Resources\Charts") {
    Copy-Item -LiteralPath "$source\Assets\Resources\Charts" -Destination "$scratch\Assets\Resources" -Recurse -Force
    if (Test-Path -LiteralPath "$source\Assets\Resources\Charts.meta") {
        Copy-Item -LiteralPath "$source\Assets\Resources\Charts.meta" -Destination "$scratch\Assets\Resources\Charts.meta" -Force
    }
}
$shot = "$scratch\Logs\$Name.png"
$arguments = @('-batchmode', '-quit', '-projectPath', "`"$scratch`"", '-executeMethod', $Method, '-voyages', $Voyages, '-showcase', $Showcase, '-snapshotPath', "`"$shot`"", '-logFile', "`"$log`"")
$process = Start-Process -FilePath $unity -ArgumentList $arguments -PassThru -WindowStyle Hidden
$process.WaitForExit()
Get-Content $log | Select-String '\[Catchline\]|error CS|Exception|executeMethod'
if (Select-String -Path $log -Pattern 'error CS|Shader error|Skiff check failed|First voyage check failed|executeMethod.*(could not|failed)|NullReferenceException') { throw 'Unity check failed; read log' }
$expected = if ($Method.Contains('SkiffChecks.')) { 'SKIFF CHECKS PASSED' } elseif ($Method.EndsWith('FirstVoyageChecks.Run')) { 'FIRST VOYAGE CHECKS PASSED' } elseif ($Method.EndsWith('FirstVoyageChecks.Regression')) { 'FIRST VOYAGE REGRESSION PASSED' } elseif ($Method.EndsWith('UrgentCrewChecks.Run')) { 'URGENT CREW CHECKS PASSED' } elseif ($Method.EndsWith('ProgressionLaunchChecks.ValidateAndBuild')) { 'CREW026 COMBINED REGRESSION PASSED' } elseif ($Method.EndsWith('ProgressionLaunchChecks.BuildBoth')) { 'PLAYABLE PREVIEW BUILT:' } elseif ($Method.EndsWith('BuildPreview')) { 'PLAYABLE PREVIEW BUILT:' } else { 'Snapshot written to' }
if (!(Select-String -Path $log -SimpleMatch $expected)) { throw "Missing completion evidence; Unity exit $($process.ExitCode)" }
Write-Output "Verified $Name (Unity exit $($process.ExitCode)); log $log"
