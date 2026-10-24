$ErrorActionPreference='Stop'
$evidence='C:\Users\momoy\Projects\Catchline\docs\screens\fish050'
$source='C:\Users\momoy\Projects\Catchline-sim\Builds\Tier033'
$target='C:\Users\momoy\Projects\Catchline-play\Tier033'
$backup='C:\Users\momoy\Projects\Catchline-play\Tier033-fish050-backup'
$receipt=Get-Content -LiteralPath "$evidence\build-manifest.json" -Raw | ConvertFrom-Json
if($receipt.Build -ne 'fish050-final'){throw 'Wrong reviewed build receipt'}
foreach($f in $receipt.Files){
 $p=Join-Path $source $f.File
 if(!(Test-Path -LiteralPath $p) -or (Get-FileHash -LiteralPath $p).Hash -ne $f.SHA256){throw "Reviewed build changed: $($f.File)"}
}
$sources=Get-Content -LiteralPath "$evidence\source-verification.json" -Raw | ConvertFrom-Json
foreach($f in $sources.Files){
 foreach($root in @('C:\Users\momoy\Projects\Catchline','C:\Users\momoy\Projects\Catchline-sim')){
  if((Get-FileHash -LiteralPath (Join-Path $root $f.File)).Hash -ne $f.SHA256){throw "Verified source changed: $($f.File)"}
 }
}
# Install only the existing save-isolated Tier4 Test distribution.
$players=Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'Catchline.exe' -and $_.ExecutablePath -eq "$target\Catchline.exe"}
foreach($player in $players){
 if($player.CommandLine -notmatch '-prepboat-trial'){throw 'Unexpected non-test player; installation not started'}
 $p=Get-Process -Id $player.ProcessId
 if(!$p.CloseMainWindow() -or !$p.WaitForExit(15000)){throw 'Test still running; installation not started'}
}
$w=New-Object -ComObject WScript.Shell
$s=$w.CreateShortcut("$env:USERPROFILE\Desktop\Catchline - Tier 4 Test.lnk")
if($s.TargetPath -ne "$target\Catchline.exe" -or $s.Arguments -ne '-prepboat-trial -native-display'){throw 'Unexpected Tier4 shortcut'}
if(Test-Path -LiteralPath $backup){throw 'Existing backup; installation not started'}
robocopy $target $backup /E /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
if($LASTEXITCODE -ge 8){throw 'Backup failed'}
robocopy $source $target /MIR /XD Catchline_BurstDebugInformation_DoNotShip /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
if($LASTEXITCODE -ge 8){throw 'Installation failed; backup retained'}
$proof=foreach($f in $receipt.Files){
 $installed=Join-Path $target $f.File
 if(!(Test-Path -LiteralPath $installed) -or (Get-FileHash -LiteralPath $installed).Hash -ne $f.SHA256){throw "Installed file mismatch: $($f.File)"}
 [pscustomobject]@{File=$f.File;SHA256=$f.SHA256;Match=$true}
}
[pscustomobject]@{Build='fish050-final';Files=$proof;ShortcutTarget=$s.TargetPath;Arguments=$s.Arguments;RealSaveUntouched=$true} | ConvertTo-Json -Depth 5 | Set-Content "$evidence\installed-build.json"
if([IO.Path]::GetFullPath($backup) -ne 'C:\Users\momoy\Projects\Catchline-play\Tier033-fish050-backup'){throw 'Unexpected cleanup path'}
Remove-Item -LiteralPath $backup -Recurse -Force
Write-Output "FISH050 installed; $($proof.Count) files match reviewed build; shortcut unchanged."
