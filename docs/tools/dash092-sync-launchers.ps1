$ErrorActionPreference='Stop'
$root='C:\Users\momoy\Projects\Catchline'
$e="$root\docs\screens\dash092"
New-Item -ItemType Directory -Path $e -Force | Out-Null
$receiptPath="$root\docs\screens\deep104\installed-build.json"
if(!(Test-Path -LiteralPath $receiptPath)){$receiptPath="$root\docs\screens\dash087\installed-build.json"}
$receipt=Get-Content -LiteralPath $receiptPath -Raw | ConvertFrom-Json
$save=Join-Path $env:USERPROFILE 'AppData\LocalLow\DefaultCompany\Catchline\catchline-save.json'
function Fingerprint {if(Test-Path -LiteralPath $save){return (Get-FileHash -LiteralPath $save).Hash};return 'absent'}
$before=Fingerprint
# Reuse the exact already-tested players, including scene persistence mode.
foreach($mode in $receipt.Installed){foreach($file in $mode.Files){if((Get-FileHash -LiteralPath (Join-Path $mode.Destination $file.File)).Hash -ne $file.SHA256){throw "Installed build changed: $($mode.Mode)/$($file.File)"}}}
$test=($receipt.Installed | Where-Object Mode -eq 'Test').Destination+'\Catchline.exe'
$real=($receipt.Installed | Where-Object Mode -eq 'Real').Destination+'\Catchline.exe'
$w=New-Object -ComObject WScript.Shell
$roots=@([Environment]::GetFolderPath('Desktop'),[Environment]::GetFolderPath('StartMenu'),"$env:ProgramData\Microsoft\Windows\Start Menu",'C:\Users\momoy\Projects\Catchline-play',$root)
$links=@(foreach($folder in $roots){Get-ChildItem -LiteralPath $folder -Filter *.lnk -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
 $s=$w.CreateShortcut($_.FullName)
 if([IO.Path]::GetFileName($s.TargetPath) -eq 'Catchline.exe'){
  $isReal=$_.Name -match 'Real Game' -or $s.TargetPath -match '\\Real\\'
  if(!$isReal -and $_.Name -notmatch 'Test' -and $s.TargetPath -notmatch '\\Test\\'){throw "Unclassified launcher: $($_.FullName)"}
  [pscustomobject]@{Path=$_.FullName;PreviousTarget=$s.TargetPath;Arguments=$s.Arguments;Target=$(if($isReal){$real}else{$test});Changed=($s.TargetPath -ne $(if($isReal){$real}else{$test}))}
 }
}})
if($links.Count -lt 5){throw 'Expected all five Catchline launchers'}
$backup=Join-Path $env:TEMP ('dash092-shortcuts-'+[Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $backup | Out-Null
if(!(Test-Path "$e\launchers-before.json")){$links | ConvertTo-Json -Depth 5 | Set-Content "$e\launchers-before.json"}
foreach($item in $links){
 if($item.Changed){
  Copy-Item -LiteralPath $item.Path -Destination (Join-Path $backup ([IO.Path]::GetFileName($item.Path)))
  $s=$w.CreateShortcut($item.Path);$s.TargetPath=$item.Target;$s.WorkingDirectory=Split-Path $item.Target;$s.IconLocation="$($item.Target),0";$s.Save()
 }
 $read=$w.CreateShortcut($item.Path)
 if($read.TargetPath -ne $item.Target -or $read.Arguments -ne $item.Arguments -or $read.WorkingDirectory -ne (Split-Path $item.Target)){throw "Launcher readback failed: $($item.Path)"}
}
$links | ConvertTo-Json -Depth 5 | Set-Content "$e\launchers-after.json"
Write-Output "All $($links.Count) launchers target verified current players; $(@($links|Where-Object Changed).Count) updated, original mode arguments preserved."
# Startup smoke checks use the actual resolved shortcut flags and Test player.
$smokes=@(@('Tier 3','Crew mix trial: compact fisher'),@('Tier 4','TIER033 trial:'))
foreach($smoke in $smokes){
 $item=$links | Where-Object Path -match $smoke[0] | Select-Object -First 1
 if(!$item){throw "Missing $($smoke[0]) launcher"}
 $name=$smoke[0].Replace(' ','');$log="$e\native-$name.log"
 $p=Start-Process -FilePath $item.Target -WorkingDirectory (Split-Path $item.Target) -ArgumentList ($item.Arguments+' -logFile "'+$log+'"') -PassThru
 $ready=$false
 for($n=0;$n -lt 45;$n++){
  Start-Sleep -Milliseconds 1000;$p.Refresh()
  if($p.HasExited){throw "$name exited during startup"}
  if((Test-Path $log) -and (Select-String -Path $log -SimpleMatch $smoke[1])){$ready=$true;break}
 }
 if(!$ready){throw "$name startup marker missing, inspect PID $($p.Id)"}
 if(!(Select-String -Path $log -SimpleMatch 'TEST / no save reads or writes')){throw "$name not isolated"}
 Start-Sleep -Milliseconds 2000
 if(!$p.CloseMainWindow()){throw "Could not close checked $name player PID $($p.Id)"}
 if(!$p.WaitForExit(10000)){throw "$name still closing PID $($p.Id)"}
 if($p.ExitCode -ne 0 -or (Select-String -Path $log -Pattern 'Exception|Error:|Shader error')){throw "$name native error"}
 Write-Output "$name native mode startup and clean shutdown passed."
}
$tier5=$links | Where-Object Path -match 'Tier 5' | Select-Object -First 1
if(!$tier5 -or $tier5.Arguments -notmatch '-tier5-trial'){throw 'Tier5 mode missing'}
$frames="$e\tier5-launcher";New-Item -ItemType Directory -Path $frames -Force | Out-Null
$log="$e\native-Tier5.log"
$captureArguments=$tier5.Arguments -replace '(?<!\S)-native-display(?!\S)',''
# Capture controls its own resolution; borderless desktop would override its first size.
$p=Start-Process -FilePath $tier5.Target -WorkingDirectory (Split-Path $tier5.Target) -ArgumentList ($captureArguments+' -screen-width 640 -screen-height 360 -screen-fullscreen 0 -force-d3d11 -capture-dash087 "'+$frames+'" -logFile "'+$log+'"') -PassThru
if(!$p.WaitForExit(180000)){throw "Tier5 capture still running PID $($p.Id)"}
if($p.ExitCode -ne 0 -or !(Select-String -Path $log -SimpleMatch 'DASH087 NATIVE CAPTURES PASSED') -or (Select-String -Path $log -Pattern 'Exception|Error:|Shader error')){throw 'Tier5 launcher native dashboard capture failed'}
foreach($hull in 0..4){foreach($width in @(1440,844)){foreach($state in @('entry','income','operations')){if(!(Test-Path "$frames\hull$hull-$state-$width.png")){throw 'Missing native management frame'}}}}
$after=Fingerprint;if($before -ne $after){throw 'Player save changed'}
[pscustomobject]@{Version=($receipt.Version+'/DASH092');Roots=$roots;Launchers=$links;ShippingFilesVerified=(@($receipt.Installed[0].Files).Count+@($receipt.Installed[1].Files).Count);NativeStartupModes=@('Tier3 compact fisher / empty crew office','Tier4 prep boat');NativeDashboardLauncher='Tier5';NativeManagementFrames=30;SaveBefore=$before;SaveAfter=$after;SaveUnchanged=$true} | ConvertTo-Json -Depth 6 | Set-Content "$e\launcher-verification.json"
Remove-Item -LiteralPath $backup -Recurse
Write-Output 'All launchers verified. Tier3/4 native startup and Tier5-target cross-hull Management captures passed; real save unchanged. Temporary shortcut backups removed.'
