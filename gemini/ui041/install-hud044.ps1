$ErrorActionPreference='Stop'
$source='C:\Users\momoy\Projects\Catchline-ui041-sim\Builds\Tier033'
$target='C:\Users\momoy\Projects\Catchline-play\Tier033'
$backup='C:\Users\momoy\Projects\Catchline-play\Tier033-hud044-backup'
if(Test-Path $backup){throw 'Backup already exists'}
robocopy $target $backup /E /NFL /NDL /NJH /NJS | Out-Null
if($LASTEXITCODE -ge 8){throw 'Backup copy failed'}
robocopy $source $target /MIR /XD Catchline_BurstDebugInformation_DoNotShip /NFL /NDL /NJH /NJS | Out-Null
if($LASTEXITCODE -ge 8){throw 'Install failed'}
$files=@('Catchline.exe','UnityPlayer.dll','Catchline_Data\Managed\Assembly-CSharp.dll','Catchline_Data\resources.assets')
$proof=foreach($f in $files){$a=(Get-FileHash "$source\$f").Hash;$b=(Get-FileHash "$target\$f").Hash;if($a -ne $b){throw "Hash differs: $f"};[pscustomobject]@{File=$f;SHA256=$a;Match=$true}}
$w=New-Object -ComObject WScript.Shell
$s=$w.CreateShortcut("$env:USERPROFILE\Desktop\Catchline - Tier 4 Test.lnk")
if($s.TargetPath -ne "$target\Catchline.exe" -or $s.Arguments -ne '-prepboat-trial -native-display'){throw 'Unexpected Tier4 shortcut'}
$proof | ConvertTo-Json | Set-Content 'C:\Users\momoy\Projects\Catchline\docs\screens\hud044\install-verification.json'
Remove-Item $backup -Recurse -Force
Write-Output 'HUD044 installed and hash-verified; existing Tier4 shortcut unchanged.'
