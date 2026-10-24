$ErrorActionPreference='Stop'
$base='C:\Users\momoy\Projects\Catchline-sim'
$frames='C:\Users\momoy\Projects\Catchline\docs\screens\fish050'
$log="$base\Logs\fish050-native.log"
$arguments=@('-prepboat-trial','-capture-gemini-ui',"`"$frames`"",'-fish050-only','-screen-width','640','-screen-height','360','-force-d3d11','-screen-fullscreen','0','-logFile',"`"$log`"")
$p=Start-Process "$base\Builds\Tier033\Catchline.exe" -ArgumentList $arguments -PassThru -WindowStyle Hidden
Write-Output "FISH050 native PID $($p.Id)"
if(!$p.WaitForExit(180000)){throw 'Native capture still running; inspect before retrying'}
if($p.ExitCode -ne 0){throw "Native exit $($p.ExitCode)"}
if(!(Select-String -Path $log -SimpleMatch 'UI041 NATIVE CAPTURES COMPLETE')){throw 'Missing native completion'}
if(Select-String -Path $log -Pattern 'Exception|Error:|Shader error'){throw 'Native error; inspect log'}
foreach($width in @(1440,844)){
 foreach($fish in @('YellowfinTuna','Barracuda','MahiMahi','Monkfish')){
  if(!(Test-Path "$frames\catch-$fish-$width.png")){throw "Missing $fish / $width capture"}
 }
}
Get-Content $log | Select-String '\[Catchline\].*(Launch mode|NATIVE CAPTURES COMPLETE)'
