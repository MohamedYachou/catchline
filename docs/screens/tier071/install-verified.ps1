$ErrorActionPreference='Stop'
$root='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
$e="$root\docs\screens\tier071"
$build=Get-Content "$e\build-manifest.json" -Raw | ConvertFrom-Json
$sources=Get-Content "$e\source-verification.json" -Raw | ConvertFrom-Json
if($build.Build -ne 'tier071-delivery' -or $sources.Build -ne $build.Build){throw 'Unreviewed build receipt'}
if(!(Select-String -Path "$scratch\Logs\tier071-native.log" -SimpleMatch -Pattern 'TIER071 NATIVE CAPTURES COMPLETE')){throw 'Native completion missing'}
foreach($file in $sources.Files){
 foreach($base in @($root,$scratch)){
  if((Get-FileHash -LiteralPath (Join-Path $base $file.File)).Hash -ne $file.SHA256){throw "Verified source changed $($file.File)"}
 }
}
$destination='C:\Users\momoy\Projects\Catchline-play\Tier071'
if(Test-Path $destination){throw 'Versioned destination already exists; inspect before overwrite'}
foreach($mode in @('Test','Real')){
 foreach($file in $build.Modes.$mode){
  if((Get-FileHash -LiteralPath (Join-Path "$scratch\Builds\Tier071\$mode" $file.File)).Hash -ne $file.SHA256){throw "Verified build changed $mode $($file.File)"}
 }
}
$save=Join-Path $env:USERPROFILE 'AppData\LocalLow\DefaultCompany\Catchline\catchline-save.json'
function SaveFingerprint {
 if(Test-Path -LiteralPath $save){return [pscustomobject][ordered]@{Exists=$true;SHA256=(Get-FileHash -LiteralPath $save).Hash;Length=(Get-Item -LiteralPath $save).Length}}
 return [pscustomobject][ordered]@{Exists=$false;SHA256=$null;Length=0}
}
$before=SaveFingerprint
$w=New-Object -ComObject WScript.Shell;$desktop=[Environment]::GetFolderPath('Desktop')
$realLink=Join-Path $desktop 'Catchline - Real Game.lnk'
$testLink=Join-Path $desktop 'Catchline - Tier 5 Test.lnk'
$shortcutBackup=Join-Path $e 'shortcut-backup'
if(Test-Path $shortcutBackup){throw 'Existing task backup; inspect first'}
New-Item -ItemType Directory -Path $shortcutBackup | Out-Null
foreach($link in @($realLink,$testLink)){
 if(Test-Path -LiteralPath $link){
  $current=$w.CreateShortcut($link)
  if(!$current.TargetPath.StartsWith('C:\Users\momoy\Projects\Catchline-play\',[StringComparison]::OrdinalIgnoreCase)){throw 'Shortcut outside Catchline installs'}
  Copy-Item -LiteralPath $link -Destination $shortcutBackup
 }
}
$verified=@{}
foreach($mode in @('Test','Real')){
 $target="$destination\$mode"
 New-Item -ItemType Directory -Force -Path $target | Out-Null
 robocopy "$scratch\Builds\Tier071\$mode" $target /E /XD Catchline_BurstDebugInformation_DoNotShip /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
 if($LASTEXITCODE -ge 8){throw "Install copy failed $mode"}
 $proof=foreach($file in $build.Modes.$mode){
  if((Get-FileHash -LiteralPath (Join-Path $target $file.File)).Hash -ne $file.SHA256){throw "Installed mismatch $mode $($file.File)"}
  [pscustomobject]@{File=$file.File;SHA256=$file.SHA256;Match=$true}
 }
 $verified[$mode]=@($proof)
 $link=if($mode -eq 'Real'){$realLink}else{$testLink}
 $s=$w.CreateShortcut($link);$s.TargetPath="$target\Catchline.exe";$s.WorkingDirectory=$target
 $s.Arguments=if($mode -eq 'Real'){'-native-display'}else{'-tier5-trial -native-display'}
 $s.IconLocation="$target\Catchline.exe,0";$s.Description=if($mode -eq 'Real'){'Catchline with Tier5 shipyard refit; existing progress retained.'}else{'Tier5 boat: six crew, rods/net module, two buoys, processor and engineer. Save-isolated preview.'};$s.Save()
 $check=$w.CreateShortcut($link)
 if($check.TargetPath -ne $s.TargetPath -or $check.Arguments -ne $s.Arguments){throw 'Shortcut readback mismatch'}
}
$after=SaveFingerprint
if(($before|ConvertTo-Json -Compress) -ne ($after|ConvertTo-Json -Compress)){throw 'Real save fingerprint changed'}
[pscustomobject]@{Build=$build.Build;Files=$verified;SaveBefore=$before;SaveAfter=$after;RealSaveUntouched=$true;TestShortcut=$testLink;RealShortcut=$realLink} | ConvertTo-Json -Depth 7 | Set-Content "$e\installed-build.json"
Remove-Item -LiteralPath $shortcutBackup -Recurse -Force
Write-Output "Installed $($verified['Test'].Count) Test + $($verified['Real'].Count) Real files; shortcuts verified; real save unchanged."
