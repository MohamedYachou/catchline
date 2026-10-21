$ErrorActionPreference='Stop'
$source='C:\Users\momoy\Projects\Catchline-sim\Builds\Tier033'
$target='C:\Users\momoy\Projects\Catchline-play\Tier033'
$backup='C:\Users\momoy\Projects\Catchline-play\Tier033-prep047-backup'
# Never overwrite a live player, real installation or real save.
$players=Get-CimInstance Win32_Process | Where-Object {$_.Name -eq 'Catchline.exe' -and $_.ExecutablePath -eq "$target\Catchline.exe"}
foreach($player in $players){
 if($player.CommandLine -notmatch '-prepboat-trial'){throw 'Unexpected non-test player; install not started'}
 $p=Get-Process -Id $player.ProcessId
 if(!$p.CloseMainWindow() -or !$p.WaitForExit(15000)){throw 'Test still running; install not started'}
}
$w=New-Object -ComObject WScript.Shell
$link="$env:USERPROFILE\Desktop\Catchline - Tier 4 Test.lnk"
$s=$w.CreateShortcut($link)
if($s.TargetPath -ne "$target\Catchline.exe" -or $s.Arguments -ne '-prepboat-trial -native-display'){throw 'Unexpected Tier4 shortcut'}
if(Test-Path -LiteralPath $backup){throw 'Existing backup; install not started'}
robocopy $target $backup /E /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
if($LASTEXITCODE -ge 8){throw 'Backup failed'}
robocopy $source $target /MIR /XD Catchline_BurstDebugInformation_DoNotShip /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
if($LASTEXITCODE -ge 8){throw 'Install failed; backup retained'}
$proof=foreach($f in (Get-ChildItem -LiteralPath $source -Recurse -File | Where-Object {$_.FullName -notmatch 'Catchline_BurstDebugInformation_DoNotShip'})){
 $rel=$f.FullName.Substring($source.Length+1);$installed=Join-Path $target $rel
 if(!(Test-Path -LiteralPath $installed)){throw "Missing installed $rel"}
 $sha=(Get-FileHash -LiteralPath $f.FullName).Hash
 if($sha -ne (Get-FileHash -LiteralPath $installed).Hash){throw "Hash mismatch $rel"}
 [pscustomobject]@{File=$rel;SHA256=$sha;Match=$true}
}
[pscustomobject]@{Build='netstats-codex3-final';Files=$proof;ShortcutTarget=$s.TargetPath;Arguments=$s.Arguments;RealSaveUntouched=$true} | ConvertTo-Json -Depth 5 | Set-Content 'C:\Users\momoy\Projects\Catchline\docs\screens\prep047\installed-build.json'
if([IO.Path]::GetFullPath($backup) -ne 'C:\Users\momoy\Projects\Catchline-play\Tier033-prep047-backup'){throw 'Unexpected cleanup path'}
Remove-Item -LiteralPath $backup -Recurse -Force
Write-Output "PREP047 installed; $($proof.Count) files hash-match verified build; shortcut unchanged."
