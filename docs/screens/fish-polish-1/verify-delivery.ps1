$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-lead-sim'
$play='C:\Users\momoy\Projects\Catchline-play'
$evidence=Join-Path $project 'docs\screens\fish-polish-1'
function Hash($p){(Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash}
$files=@('Assets/Scripts/Game/VoyageUiV2Capture.cs')
foreach($f in 'Minigame/VoyageRodView.cs','Minigame/RodViewAtmosphere.cs','Minigame/VoyageFishPolishCapture.cs',
 'Minigame/Resources/RodViewSky.shader','Minigame/Resources/RodViewCue.shader'){
 $files+="Assets/Scripts/Game/$f"; $files+="Assets/Scripts/Game/$f.meta"
}
foreach($f in 'FishPolishChecks.cs','HarbourImportChecks.cs'){$files+="Assets/Editor/$f";$files+="Assets/Editor/$f.meta"}
$sources=foreach($f in $files){
 $a=Hash (Join-Path $project $f);$b=Hash (Join-Path $scratch $f)
 if($a -ne $b){throw "Source differs: $f"}
 [pscustomobject]@{Path=$f;SHA256=$a}
}
$wsh=New-Object -ComObject WScript.Shell
$installed=foreach($mode in 'Real','Test'){
 $binaries=foreach($f in 'Catchline.exe','Catchline_Data/Managed/Assembly-CSharp.dll'){
  $a=Hash (Join-Path "$scratch/Builds/Catchline/$mode" $f);$b=Hash (Join-Path "$play/$mode" $f)
  if($a -ne $b){throw "Installed binary differs: $mode/$f"}
  [pscustomobject]@{Path=$f;SHA256=$a}
 }
 $name=if($mode -eq 'Real'){'Catchline.lnk'}else{'Catchline - Test.lnk'}
 $link=$wsh.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) $name))
 if($link.TargetPath -ne "$play\$mode\Catchline.exe" -or $link.Arguments -ne '-native-display'){throw "Wrong shortcut $name"}
 [pscustomobject]@{Mode=$mode;Binaries=$binaries;Shortcut=$name;Target=$link.TargetPath;Arguments=$link.Arguments}
}
$before=Get-Content (Join-Path $evidence 'save-before.json') -Raw | ConvertFrom-Json
$save=Get-Item -LiteralPath $before.Path
$after=[pscustomobject]@{Path=$save.FullName;SHA256=(Hash $save.FullName);Length=$save.Length;LastWriteUtc=$save.LastWriteTimeUtc.ToString('o')}
if($after.SHA256 -ne $before.SHA256 -or $after.Length -ne $before.Length -or $after.LastWriteUtc -ne $before.LastWriteUtc){throw 'Player save changed'}
$after | ConvertTo-Json | Set-Content (Join-Path $evidence 'save-after.json') -Encoding utf8
$native=Get-Content (Join-Path $evidence 'native.log') -Raw
if($native -notmatch 'FISH POLISH CAPTURES COMPLETE' -or $native -match 'Exception|Shader error|NullReference'){throw 'Native capture failed'}
$run=Get-Content (Join-Path $evidence 'native-run.json') -Raw | ConvertFrom-Json
if($run.Executable -ne "$play\Test\Catchline.exe" -or $run.ExecutableSHA256 -ne (Hash "$play/Test/Catchline.exe") -or $run.AssemblySHA256 -ne (Hash "$play/Test/Catchline_Data/Managed/Assembly-CSharp.dll")){throw 'Capture producer differs from final installed Test'}
$build=Get-Content (Join-Path $evidence 'check-build.log') -Raw
$checks=Get-Content (Join-Path $evidence 'final-check.log') -Raw
if($checks -notmatch 'FISH POLISH CHECKS PASS' -or $checks -notmatch 'return code 0' -or ([regex]::Matches($build,'\[Catchline\] GAME BUILT')).Count -ne 2 -or $build -notmatch 'return code 0'){throw 'Checks/build did not complete'}
Add-Type -AssemblyName System.Drawing
$reviewed=@(Get-Content (Join-Path $evidence 'reviewed-images.txt'))
$pngs=@(Get-ChildItem $evidence -File -Filter '*.png' | Sort-Object Name)
if($pngs.Count -ne 12 -or @($reviewed | Select-Object -Unique).Count -ne 12){throw 'Expected 12 native images and unique review records'}
$frames=foreach($f in $pngs){
 if($f.LastWriteTimeUtc -lt [DateTime]::Parse($run.LaunchUtc).ToUniversalTime()){throw "Stale capture: $($f.Name)"}
 if($reviewed -notcontains $f.Name){throw "Image not reviewed: $($f.Name)"}
 $im=[System.Drawing.Image]::FromFile($f.FullName)
 try{
  $expected=if($f.Name -like '*-1440.png'){@(1440,900)}else{@(844,390)}
  if($im.Width -ne $expected[0] -or $im.Height -ne $expected[1]){throw "Wrong dimensions: $($f.Name)"}
  $nonBlack=$false
  for($y=0;$y -lt $im.Height -and -not $nonBlack;$y+=20){
   for($x=0;$x -lt $im.Width;$x+=20){
    $pixel=$im.GetPixel($x,$y)
    if(($pixel.R+$pixel.G+$pixel.B) -gt 15){$nonBlack=$true;break}
   }
  }
  if(-not $nonBlack){throw "Black native frame: $($f.Name)"}
  [pscustomobject]@{File=$f.Name;Width=$im.Width;Height=$im.Height;SHA256=(Hash $f.FullName)}
 }finally{$im.Dispose()}
}
$frames | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $evidence 'frames.json') -Encoding utf8
[pscustomobject]@{Sources=$sources;Installed=$installed;SaveUnchanged=$true;Producer=$run;Images=$frames;
 Limits='Items3-5 only; installed TEST clock-controlled fixture, no hand-played Real/physical touch acceptance. Harbour evidence and other rod polish belong to the lead.'} |
 ConvertTo-Json -Depth 8 | Set-Content (Join-Path $evidence 'verification-receipt.json') -Encoding utf8
Write-Output "PASS: $($sources.Count) source pairs; Real/Test installed binaries and exact shortcuts; unchanged save;12 reviewed native images."
