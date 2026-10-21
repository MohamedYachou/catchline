$ErrorActionPreference='Stop'
$root='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
$e="$root\docs\screens\dash087"
foreach($test in @(@('unity-check.log','DASH087 CHECKS PASSED'),@('native-Test.log','DASH087 NATIVE CAPTURES PASSED'),@('native-Real.log','DASH087 REAL SAVE PROBE PASSED'))){if(!(Select-String -Path "$e\$($test[0])" -SimpleMatch $test[1])){throw 'Verified evidence missing'}}
$files=@('CatchExpectation','FlowTelemetry','VoyageProcessingPipeline','VoyageManagementForecast','CoastalCanvas','VoyageNetUnload','VoyageManagement','VoyageManagementCapture','VoyageGame','VoyageStorage','VoyageNet','VoyageSecondNetModule','VoyageTier5','VoyageCaptainPrep','VoyagePrepOrders','VoyageInterface','VoyageNetInterface','VoyageHud','VoyageCapture','GameState')|ForEach-Object{"Assets/Scripts/Game/$_.cs"}
$files+=@('Assets/Editor/DashboardChecks.cs','Assets/Editor/DashboardMathChecks.cs','Assets/Editor/ManagementChecks.cs','Assets/Editor/Tier5Checks.cs')
$files+=@(Get-ChildItem "$root\Assets\Resources\ManagementReference" -File|ForEach-Object{"Assets/Resources/ManagementReference/"+$_.Name})
$sources=foreach($file in $files){$hash=(Get-FileHash -LiteralPath (Join-Path $root $file)).Hash;if((Get-FileHash -LiteralPath (Join-Path $scratch $file)).Hash -ne $hash){throw "Changed after verification: $file"};[pscustomobject]@{File=$file;SHA256=$hash}}
$save=Join-Path $env:USERPROFILE 'AppData\LocalLow\DefaultCompany\Catchline\catchline-save.json'
function Fingerprint {if(Test-Path -LiteralPath $save){return (Get-FileHash -LiteralPath $save).Hash};return 'absent'}
$before=Fingerprint
$copied=@()
foreach($mode in @('Test','Real')){
 $base="$scratch\Builds\Dash087\$mode";$destination="C:\Users\momoy\Projects\Catchline-play\Dash087\$mode"
 if(Test-Path -LiteralPath $destination){throw "Version exists: $destination"}
 $manifest=@(Get-ChildItem -LiteralPath $base -Recurse -File|Where-Object{$_.FullName -notmatch 'DoNotShip'}|ForEach-Object{[pscustomobject]@{File=$_.FullName.Substring($base.Length+1);SHA256=(Get-FileHash -LiteralPath $_.FullName).Hash}})
 New-Item -ItemType Directory -Path $destination -Force | Out-Null
 robocopy $base $destination /E /XD Catchline_BurstDebugInformation_DoNotShip /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
 if($LASTEXITCODE -ge 8){throw 'Copy failed'}
 foreach($file in $manifest){if((Get-FileHash -LiteralPath (Join-Path $destination $file.File)).Hash -ne $file.SHA256){throw 'Installed hash mismatch'}}
 $copied+=[pscustomobject]@{Mode=$mode;Destination=$destination;Files=$manifest}
}
$desktop=[Environment]::GetFolderPath('Desktop');$w=New-Object -ComObject WScript.Shell;$links=@();$backups=@()
foreach($mode in @('Real','Test')){
 $name=if($mode -eq 'Real'){'Catchline - Real Game.lnk'}else{'Catchline - DASH Management Test.lnk'}
 $path=Join-Path $desktop $name
 if(Test-Path -LiteralPath $path){$backup=Join-Path $env:TEMP ('dash087-shortcut-'+[Guid]::NewGuid().ToString()+'.lnk');Copy-Item -LiteralPath $path -Destination $backup;$backups+=$backup}
 $link=$w.CreateShortcut($path);$previous=$link.TargetPath
 $target="C:\Users\momoy\Projects\Catchline-play\Dash087\$mode\Catchline.exe"
 $link.TargetPath=$target;$link.WorkingDirectory=Split-Path $target;$link.Arguments='-native-display';$link.IconLocation="$target,0"
 $link.Description=if($mode -eq 'Real'){'Catchline with persistent progress and verified boat-specific Management.'}else{'Fresh rowboat test, isolated from player save. No forced Tier5 boat.'}
 $link.Save();$read=$w.CreateShortcut($path)
 if($read.TargetPath -ne $target -or $read.Arguments -ne '-native-display'){throw 'Shortcut readback mismatch'}
 $links+=[pscustomobject]@{Path=$path;PreviousTarget=$previous;Target=$read.TargetPath;Arguments=$read.Arguments}
}
$after=Fingerprint;if($before -ne $after){throw 'Real save changed during install'}
[pscustomobject]@{Version='Dash087';Sources=$sources;Installed=$copied;Shortcuts=$links;SaveBefore=$before;SaveAfter=$after;RealSaveUntouched=$true} | ConvertTo-Json -Depth 8 | Set-Content "$e\installed-build.json"
foreach($backup in $backups){Remove-Item -LiteralPath $backup}
Write-Output 'Verified Test and Real installs; Real Game now targets Dash087. Dashboard test no longer forces Tier5. Save unchanged.'
