$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-lead-sim'
$play='C:\Users\momoy\Projects\Catchline-play'
$evidence=Join-Path $project 'docs/screens/harbour-1'
function Hash($p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash}
$inputReceipt=Get-Content "$evidence/build-inputs.json" -Raw | ConvertFrom-Json
foreach($inputFile in $inputReceipt.Inputs){
 if((Hash (Join-Path $project $inputFile.Path)) -ne $inputFile.SHA256 -or (Hash (Join-Path $scratch $inputFile.Path)) -ne $inputFile.SHA256){throw "Build input changed: $($inputFile.Path)"}
}
$imports=Get-Content "$evidence/import-receipt.json" -Raw | ConvertFrom-Json
if(@($imports.models).Count -ne 30){throw 'Expected30 imported harbour models'}
foreach($model in $imports.models){
 if(-not $model.resolves -or $model.looseMaterials -or (Hash (Join-Path $project $model.asset)) -ne $model.sha256 -or (Hash "$project/Art/Models/GullHarbour/HarbourV2/$($model.name).fbx") -ne $model.sha256){throw "Import receipt/source mismatch: $($model.name)"}
}
$initialStages=Get-Content "$evidence/stage-check-initial.log" -Raw
$stageLog=Get-Content "$project/docs/screens/fish-polish-1/harbour-remaining-stage-check.log" -Raw
$passedStages=@([regex]::Matches(($initialStages+$stageLog),'EVIDENCE STAGE PASS ([a-z0-9-]+)') | ForEach-Object {$_.Groups[1].Value} | Select-Object -Unique)
if($passedStages.Count -ne 21 -or $stageLog -notmatch 'EVIDENCE STAGES COMPLETE' -or $stageLog -notmatch 'return code 0'){throw 'Stage checks incomplete'}
$boardCheck=Get-Content "$project/docs/screens/fish-polish-1/board-stage-check.log" -Raw
if($boardCheck -notmatch 'POPULATED SORTING BOARD PASS' -or $boardCheck -notmatch 'return code 0'){throw 'Populated sorting-board evidence not verified'}
$buildLog=Get-Content "$project/docs/screens/fish-polish-1/check-build.log" -Raw
if(([regex]::Matches($buildLog,'\[Catchline\] GAME BUILT')).Count -ne 2 -or $buildLog -notmatch 'return code 0'){throw 'Pair build incomplete'}
$wsh=New-Object -ComObject WScript.Shell
$installed=foreach($mode in 'Real','Test'){
 $builtRoot="$scratch/Builds/Catchline/$mode"
 $installRoot="$play/$mode"
 $builtFiles=@(Get-ChildItem -LiteralPath $builtRoot -File -Recurse)
 if($builtFiles.Count -ne @(Get-ChildItem -LiteralPath $installRoot -File -Recurse).Count){throw "Installed file count mismatch $mode"}
 $files=foreach($file in $builtFiles){
  $relative=$file.FullName.Substring($builtRoot.Length+1).Replace('\','/')
  $sha=Hash $file.FullName
  if($sha -ne (Hash (Join-Path $installRoot $relative))){throw "Installed bytes mismatch $mode/$relative"}
  [pscustomobject]@{Path=$relative;SHA256=$sha;Bytes=$file.Length}
 }
 $name=if($mode -eq 'Real'){'Catchline.lnk'}else{'Catchline - Test.lnk'}
 $link=$wsh.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) $name))
 if($link.TargetPath -ne "$play\$mode\Catchline.exe" -or $link.Arguments -ne '-native-display'){throw "Wrong shortcut $name"}
 [pscustomobject]@{Mode=$mode;Files=$files;Shortcut=$name;Target=$link.TargetPath;Arguments=$link.Arguments}
}
$before=Get-Content "$evidence/save-before.json" -Raw | ConvertFrom-Json
$save=Get-Item -LiteralPath $before.Path
$after=[pscustomobject]@{Path=$save.FullName;SHA256=(Hash $save.FullName);Length=$save.Length;LastWriteUtc=$save.LastWriteTimeUtc.ToString('o')}
if($after.SHA256 -ne $before.SHA256 -or $after.Length -ne $before.Length -or $after.LastWriteUtc -ne $before.LastWriteUtc){throw 'Player save changed'}
$after | ConvertTo-Json | Set-Content "$evidence/save-after.json" -Encoding utf8
$shortcutLaunch=Get-Content "$evidence/shortcut-launch.json" -Raw | ConvertFrom-Json
if(-not $shortcutLaunch.SessionOnlyLogVerified -or $shortcutLaunch.LaunchedPath -ne "$play\Test\Catchline.exe"){throw 'Exact Test shortcut startup not verified'}
Add-Type -AssemblyName System.Drawing
$sets=foreach($set in @(@{Directory=$evidence;Count=18},@{Directory="$project/docs/screens/overnight/native";Count=24})){
 $directory=$set.Directory
 $run=Get-Content "$directory/native-run.json" -Raw | ConvertFrom-Json
 if($run.Executable -ne "$play\Test\Catchline.exe" -or $run.ExecutableSHA256 -ne (Hash "$play/Test/Catchline.exe") -or $run.AssemblySHA256 -ne (Hash "$play/Test/Catchline_Data/Managed/Assembly-CSharp.dll")){throw "Capture producer differs from final installed Test: $directory"}
 $log=Get-Content "$directory/native.log" -Raw
 if($log -notmatch 'UIV2 CAPTURES COMPLETE' -or $log -match 'Exception|Shader error|NullReference|stage failed'){throw "Native capture failed $directory"}
 $reviewed=@(Get-Content "$directory/reviewed-images.txt")
 $pngs=@(Get-ChildItem -LiteralPath $directory -File -Filter '*.png' | Sort-Object Name)
 if($pngs.Count -ne $set.Count -or @($reviewed | Select-Object -Unique).Count -ne $set.Count){throw "Frame/review count mismatch $directory"}
 $frames=foreach($file in $pngs){
  if($file.LastWriteTimeUtc -lt [DateTime]::Parse($run.LaunchUtc).ToUniversalTime()){throw "Stale capture: $($file.Name)"}
  if($reviewed -notcontains $file.Name){throw "Not reviewed $($file.Name)"}
  $im=[System.Drawing.Image]::FromFile($file.FullName)
  try{
   $size=if($file.Name -like '*-1440.png'){@(1440,900)}else{@(844,390)}
   if($im.Width -ne $size[0] -or $im.Height -ne $size[1]){throw "Wrong dimensions $($file.Name)"}
   # A hidden initial swapchain once emitted an all-black image. Reject that known failure.
   $nonBlack=$false
   for($y=0;$y -lt $im.Height -and -not $nonBlack;$y+=20){
    for($x=0;$x -lt $im.Width;$x+=20){
     $pixel=$im.GetPixel($x,$y)
     if(($pixel.R+$pixel.G+$pixel.B) -gt 15){$nonBlack=$true;break}
    }
   }
   if(-not $nonBlack){throw "Black native frame $($file.Name)"}
   [pscustomobject]@{File=$file.Name;Width=$im.Width;Height=$im.Height;SHA256=(Hash $file.FullName)}
  }finally{$im.Dispose()}
 }
 $frames | ConvertTo-Json | Set-Content "$directory/frames.json" -Encoding utf8
 [pscustomobject]@{Directory=$directory;Producer=$run;Frames=$frames}
}
[pscustomobject]@{BuildInputsVerified=$inputReceipt.Inputs.Count;UnchangedImportsVerified=$imports.models.Count;Installed=$installed;ExactTestShortcutLaunch=$shortcutLaunch;SaveUnchanged=$true;EvidenceSets=$sets;Limits='Clock-controlled installed TEST native GPU frames. No hand-played Real or physical touch acceptance; documented model/layout questions remain.'} |
 ConvertTo-Json -Depth 9 | Set-Content "$evidence/verification-receipt.json" -Encoding utf8
Write-Output 'PASS: complete Real/Test installation byte manifests, exact shortcuts, unchanged player save,42 individually reviewed native frames at both required sizes.'
