$ErrorActionPreference='Stop'
Add-Type @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public static class Deep104WindowClose {
 public delegate bool Callback(IntPtr window,IntPtr param);
 [DllImport("user32.dll")] public static extern bool EnumWindows(Callback callback,IntPtr param);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr window,out uint process);
 [DllImport("user32.dll")] public static extern int GetClassName(IntPtr window,StringBuilder value,int capacity);
 [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr window,uint message,IntPtr w,IntPtr l);
 public static bool Close(int process) { bool sent=false;EnumWindows((window,param)=>{uint owner;GetWindowThreadProcessId(window,out owner);if(owner==(uint)process){var name=new StringBuilder(256);GetClassName(window,name,256);if(name.ToString().Contains("UnityWndClass"))sent|=PostMessage(window,0x0010,IntPtr.Zero,IntPtr.Zero);}return true;},IntPtr.Zero);return sent; }
}
"@

$root='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
$e="$root\docs\screens\deep104"
foreach($test in @(@('regression.log','DEEP104 REGRESSION PASSED'),@('native-Test.log','DEEP104 NATIVE CAPTURES PASSED'),@('native-Real.log','DASH087 REAL SAVE PROBE PASSED'))){if(!(Select-String -Path "$e\$($test[0])" -SimpleMatch $test[1])){throw "Missing verified evidence $($test[0])"}}
$review=Get-Content "$e\native-review.json" -Raw | ConvertFrom-Json
if(!$review.Accepted){throw 'Native visual review has not passed'}
$save=Join-Path $env:USERPROFILE 'AppData\LocalLow\DefaultCompany\Catchline\catchline-save.json'
function Fingerprint {if(Test-Path -LiteralPath $save){return (Get-FileHash -LiteralPath $save).Hash};return 'absent'}
$before=Fingerprint
$sources=@(Get-ChildItem "$root\Assets\Scripts","$root\Assets\Editor","$root\Assets\Art","$root\Assets\Resources\ManagementReference" -Recurse -File|ForEach-Object{
 $relative=$_.FullName.Substring($root.Length+1);$hash=(Get-FileHash -LiteralPath $_.FullName).Hash
 if(!(Test-Path -LiteralPath (Join-Path $scratch $relative)) -or (Get-FileHash -LiteralPath (Join-Path $scratch $relative)).Hash -ne $hash){throw "Source differs from tested scratch: $relative"}
 [pscustomobject]@{File=$relative;SHA256=$hash}
})
$installed=@()
foreach($mode in @('Test','Real')){
 $base="$scratch\Builds\Deep104\$mode";$destination="C:\Users\momoy\Projects\Catchline-play\Deep104\$mode"
 $manifest=@(Get-ChildItem -LiteralPath $base -Recurse -File|Where-Object{$_.FullName -notmatch 'DoNotShip'}|ForEach-Object{[pscustomobject]@{File=$_.FullName.Substring($base.Length+1);SHA256=(Get-FileHash -LiteralPath $_.FullName).Hash}})
 if($manifest.Count -lt 20){throw 'Incomplete candidate player'}
 New-Item -ItemType Directory -Path $destination -Force | Out-Null
 robocopy $base $destination /E /XD Catchline_BurstDebugInformation_DoNotShip /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
 if($LASTEXITCODE -ge 8){throw 'Player copy failed'}
 foreach($file in $manifest){if((Get-FileHash -LiteralPath (Join-Path $destination $file.File)).Hash -ne $file.SHA256){throw 'Installed hash mismatch'}}
 $installed+=[pscustomobject]@{Mode=$mode;Destination=$destination;Files=$manifest}
}
$w=New-Object -ComObject WScript.Shell
$roots=@([Environment]::GetFolderPath('Desktop'),[Environment]::GetFolderPath('StartMenu'),"$env:ProgramData\Microsoft\Windows\Start Menu",'C:\Users\momoy\Projects\Catchline-play',$root)
$links=@(foreach($folder in $roots){Get-ChildItem -LiteralPath $folder -Filter *.lnk -Recurse -File -ErrorAction SilentlyContinue|ForEach-Object{
 $s=$w.CreateShortcut($_.FullName)
 if([IO.Path]::GetFileName($s.TargetPath) -eq 'Catchline.exe'){
  $isReal=$_.Name -match 'Real Game' -or $s.TargetPath -match '\\Real\\'
  if(!$isReal -and $_.Name -notmatch 'Test' -and $s.TargetPath -notmatch '\\Test\\'){throw "Unclassified launcher: $($_.FullName)"}
  $mode=if($isReal){'Real'}else{'Test'}
  [pscustomobject]@{Path=$_.FullName;PreviousTarget=$s.TargetPath;Arguments=$s.Arguments;Target="C:\Users\momoy\Projects\Catchline-play\Deep104\$mode\Catchline.exe"}
 }
}})
if($links.Count -ne 5){throw "Expected five existing launchers; found $($links.Count)"}
$backup=Join-Path $env:TEMP ('deep104-shortcuts-'+[Guid]::NewGuid().ToString());New-Item -ItemType Directory -Path $backup | Out-Null
if(!(Test-Path "$e\launchers-before.json")){$links | ConvertTo-Json -Depth 5 | Set-Content "$e\launchers-before.json"}
$originalLinks=Get-Content "$e\launchers-before.json" -Raw|ConvertFrom-Json
foreach($item in $links){$original=$originalLinks|Where-Object Path -eq $item.Path|Select-Object -First 1;if($original){$item.PreviousTarget=$original.PreviousTarget}}
foreach($item in $links){
 Copy-Item -LiteralPath $item.Path -Destination (Join-Path $backup ([IO.Path]::GetFileName($item.Path)))
 $s=$w.CreateShortcut($item.Path);$s.TargetPath=$item.Target;$s.WorkingDirectory=Split-Path $item.Target;$s.IconLocation="$($item.Target),0";$s.Save()
 $read=$w.CreateShortcut($item.Path)
 if($read.TargetPath -ne $item.Target -or $read.Arguments -ne $item.Arguments -or $read.WorkingDirectory -ne (Split-Path $item.Target)){throw "Launcher readback failed: $($item.Path)"}
}
$links | ConvertTo-Json -Depth 5 | Set-Content "$e\launchers-after.json"
# Startup the installed Test targets with each launcher's original mode flags.
foreach($label in @('DASH Management','Tier 3','Tier 4','Tier 5')){
 $item=$links|Where-Object Path -match $label|Select-Object -First 1
 if(!$item){throw "Missing launcher $label"}
 $name=$label.Replace(' ','');$log="$e\installed-$name.log"
 $p=Start-Process -FilePath $item.Target -WorkingDirectory (Split-Path $item.Target) -ArgumentList ($item.Arguments+' -logFile "'+$log+'"') -PassThru -WindowStyle Hidden
 $marker=if($label -eq 'Tier 3'){'Crew mix trial: compact fisher'}elseif($label -eq 'Tier 4'){'TIER033 trial:'}elseif($label -eq 'Tier 5'){'TEST / no save reads or writes'}else{'TEST / no save reads or writes'}
 $ready=$false
 for($n=0;$n -lt 45;$n++){
  Start-Sleep -Milliseconds 1000;$p.Refresh();if($p.HasExited){throw "$label exited during startup"}
  if((Test-Path $log) -and (Select-String -Path $log -SimpleMatch $marker)){$ready=$true;break}
 }
 if(!$ready -or !(Select-String -Path $log -SimpleMatch 'TEST / no save reads or writes')){throw "$label startup isolation/mode marker missing; PID $($p.Id)"}
 Start-Sleep -Milliseconds 1500
 $p.Refresh()
 if(!$p.HasExited){
  $sent=$p.CloseMainWindow();if(!$sent){$sent=[Deep104WindowClose]::Close($p.Id)}
  if(!$sent -or !$p.WaitForExit(15000)){throw "Could not gracefully close smoke player PID $($p.Id)"}
 }
 if($p.ExitCode -ne 0 -or (Select-String -Path $log -Pattern 'Exception|Error:|Shader error')){throw "$label native failure"}
 Write-Output "Installed $label mode smoke passed"
}
$after=Fingerprint;if($before -ne $after){throw 'Actual player save changed during installation'}
[pscustomobject]@{Version='Deep104';Sources=$sources;Installed=$installed;Launchers=$links;SaveBefore=$before;SaveAfter=$after;RealSaveUntouched=$true;NativeReview=$review} | ConvertTo-Json -Depth 8 | Set-Content "$e\installed-build.json"
Get-ChildItem -LiteralPath $env:TEMP -Directory -Filter "deep104-shortcuts-*" | Remove-Item -Recurse
Write-Output 'DEEP104 INSTALL PASSED: Test + Real, five launchers preserve exact mode arguments, installed native mode checks, real save unchanged.'
