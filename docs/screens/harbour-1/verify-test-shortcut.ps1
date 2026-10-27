$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$expected='C:\Users\momoy\Projects\Catchline-play\Test\Catchline.exe'
if(Get-Process Catchline -ErrorAction SilentlyContinue){throw 'Preserve existing player; run after captures finish'}
$shortcut=Join-Path ([Environment]::GetFolderPath('Desktop')) 'Catchline - Test.lnk'
$wsh=New-Object -ComObject WScript.Shell
$link=$wsh.CreateShortcut($shortcut)
if($link.TargetPath -ne $expected -or $link.Arguments -ne '-native-display'){throw 'Shortcut target/arguments mismatch'}
$started=Get-Date
Start-Process -FilePath $shortcut -WindowStyle Hidden
$deadline=(Get-Date).AddSeconds(20)
$player=$null
do{
 $player=Get-Process Catchline -ErrorAction SilentlyContinue | Where-Object {$_.StartTime -ge $started.AddSeconds(-1) -and $_.Path -eq $expected} | Select-Object -First 1
 if(-not $player){Start-Sleep -Milliseconds 200}
}while(-not $player -and (Get-Date) -lt $deadline)
if(-not $player){throw 'Exact shortcut did not start installed Test'}
try{
 [void]$player.WaitForInputIdle(15000)
 Start-Sleep -Seconds 3
 $player.Refresh()
 $logPath=Join-Path $env:USERPROFILE 'AppData/LocalLow/DefaultCompany/Catchline/Player.log'
 $log=Get-Content -LiteralPath $logPath -Raw
 if((Get-Item -LiteralPath $logPath).LastWriteTime -lt $started -or $log -notmatch 'Launch mode: TEST / no save reads or writes'){throw 'Fresh exact-shortcut launch is not verified SessionOnly'}
 if($log -match 'Exception|Shader error|NullReference'){throw 'Shortcut launch logged runtime error'}
 $log | Set-Content "$project/docs/screens/harbour-1/shortcut-test.log" -Encoding utf8
 [pscustomobject]@{Shortcut=$shortcut;Target=$link.TargetPath;Arguments=$link.Arguments;LaunchedPath=$player.Path;PID=$player.Id;WindowTitle=$player.MainWindowTitle;LaunchUtc=$started.ToUniversalTime().ToString('o');SessionOnlyLogVerified=$true;Limit='Startup only; no hand-play or physical touch acceptance.'} |
  ConvertTo-Json | Set-Content "$project/docs/screens/harbour-1/shortcut-launch.json" -Encoding utf8
}finally{
 if(-not $player.HasExited){
  [void]$player.CloseMainWindow()
  if(-not $player.WaitForExit(10000)){Stop-Process -Id $player.Id}
 }
}
Write-Output 'PASS exact desktop Test shortcut launch; installed path and fresh SessionOnly startup log verified.'
