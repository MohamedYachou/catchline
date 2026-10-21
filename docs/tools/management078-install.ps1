$ErrorActionPreference='Stop'
$root='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
$e="$root\docs\screens\management078"
if(!(Select-String -Path "$e\native.log" -SimpleMatch -Pattern 'MANAGEMENT078 NATIVE CAPTURES COMPLETE')){throw 'Native review evidence missing'}
if(!(Select-String -Path "$e\unity-check.log" -SimpleMatch -Pattern 'MANAGEMENT078 CHECKS PASSED')){throw 'Functional completion missing'}
$files=@('FlowTelemetry','VoyageManagement','VoyageManagementCapture','VoyageGame','VoyageStorage','VoyageNet','VoyageSecondNetModule','VoyageTier5','VoyageCaptainPrep','VoyagePrepOrders','VoyageInterface','VoyageHud','VoyageCapture') | ForEach-Object {"Assets/Scripts/Game/$_.cs"}
$files+= 'Assets/Editor/ManagementChecks.cs'
$sourceProof=foreach($file in $files){
 $hash=(Get-FileHash -LiteralPath (Join-Path $root $file)).Hash
 if((Get-FileHash -LiteralPath (Join-Path $scratch $file)).Hash -ne $hash){throw "Source changed after build: $file"}
 [pscustomobject]@{File=$file;SHA256=$hash;ScratchMatches=$true}
}
$save=Join-Path $env:USERPROFILE 'AppData\LocalLow\DefaultCompany\Catchline\catchline-save.json'
function SaveFingerprint {
 if(Test-Path -LiteralPath $save){return [pscustomobject]@{Exists=$true;SHA256=(Get-FileHash -LiteralPath $save).Hash;Length=(Get-Item -LiteralPath $save).Length}}
 return [pscustomobject]@{Exists=$false;SHA256=$null;Length=0}
}
$before=SaveFingerprint
$destination='C:\Users\momoy\Projects\Catchline-play\Management078\Test'
if(Test-Path -LiteralPath $destination){throw 'Versioned target already exists; inspect before overwrite'}
$base="$scratch\Builds\Management078\Test"
$manifest=@(Get-ChildItem -LiteralPath $base -Recurse -File | Where-Object {$_.FullName -notmatch 'DoNotShip'} | ForEach-Object {
 [pscustomobject]@{File=$_.FullName.Substring($base.Length+1);SHA256=(Get-FileHash -LiteralPath $_.FullName).Hash}
})
New-Item -ItemType Directory -Path $destination -Force | Out-Null
robocopy $base $destination /E /XD Catchline_BurstDebugInformation_DoNotShip /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
if($LASTEXITCODE -ge 8){throw 'Versioned preview copy failed'}
foreach($file in $manifest){if((Get-FileHash -LiteralPath (Join-Path $destination $file.File)).Hash -ne $file.SHA256){throw "Installed mismatch $($file.File)"}}
$desktop=[Environment]::GetFolderPath('Desktop')
$link=Join-Path $desktop 'Catchline - Management Test.lnk'
if(Test-Path -LiteralPath $link){throw 'New shortcut already exists; inspect before overwrite'}
$w=New-Object -ComObject WScript.Shell
$s=$w.CreateShortcut($link);$s.TargetPath="$destination\Catchline.exe";$s.WorkingDirectory=$destination
$s.Arguments='-tier5-trial -native-display';$s.IconLocation="$destination\Catchline.exe,0";$s.Description='Boat management: live fish flow, bottlenecks and method output. Save-isolated Tier5 test.';$s.Save()
$read=$w.CreateShortcut($link)
if($read.TargetPath -ne $s.TargetPath -or $read.Arguments -ne $s.Arguments){throw 'Shortcut readback mismatch'}
$after=SaveFingerprint
if(($before|ConvertTo-Json -Compress) -ne ($after|ConvertTo-Json -Compress)){throw 'Real save changed'}
[pscustomobject]@{Version='Management078';Installed=$destination;Shortcut=$link;Sources=$sourceProof;Files=$manifest;SaveBefore=$before;SaveAfter=$after;RealSaveUntouched=$true} | ConvertTo-Json -Depth 6 | Set-Content "$e\installed-build.json"
Write-Output "Installed $($manifest.Count) matching files. New Management Test shortcut verified. Real save unchanged."
