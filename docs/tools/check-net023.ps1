param([string]$Name = 'net023', [string]$Method = 'Catchline.EditorTools.ProgressionLaunchChecks.ValidateAndBuild')
$ErrorActionPreference = 'Stop'
$source = 'C:\Users\momoy\Projects\Catchline'
$scratch = 'C:\Users\momoy\Projects\Catchline-rewards-sim'
$unity = 'C:\Program Files\Unity\Hub\Editor\6000.3.25f1\Editor\Unity.exe'
# Dedicated scratch avoids CHART017's actively owned Catchline-sim and running previews.
New-Item -ItemType Directory -Force -Path "$scratch\Logs" | Out-Null
foreach ($folder in @('Assets','Packages','ProjectSettings')) {
    robocopy "$source\$folder" "$scratch\$folder" /MIR /NFL /NDL /NJH /NJS | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Copy $folder failed: $LASTEXITCODE" }
}
$log = "$scratch\Logs\check-$Name.log"
$args = @('-batchmode','-quit','-projectPath',"`"$scratch`"",'-executeMethod',$Method,'-logFile',"`"$log`"")
$p = Start-Process -FilePath $unity -ArgumentList $args -PassThru -WindowStyle Hidden
$p.WaitForExit()
Get-Content $log | Select-String '\[Catchline\]|error CS|Exception|executeMethod'
if ($p.ExitCode -ne 0) { throw "Unity check failed exit $($p.ExitCode): $log" }
if (!(Select-String -Path $log -SimpleMatch 'PLAYABLE PREVIEW BUILT:')) { throw "No build completion marker: $log" }
Write-Output "Verified $Name (Unity exit0); log $log"
