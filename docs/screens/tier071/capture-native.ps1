$ErrorActionPreference='Stop'
$base='C:\Users\momoy\Projects\Catchline-sim'
$frames='C:\Users\momoy\Projects\Catchline\docs\screens\tier071'
$log="$base\Logs\tier071-native.log"
$arguments=@('-tier5-trial','-capture-tier5',"`"$frames`"",'-screen-width','640','-screen-height','360','-force-d3d11','-screen-fullscreen','0','-logFile',"`"$log`"")
$p=Start-Process "$base\Builds\Tier071\Test\Catchline.exe" -ArgumentList $arguments -PassThru -WindowStyle Hidden
Write-Output "TIER071 native PID $($p.Id)"
if(!$p.WaitForExit(180000)){throw 'Native capture still running; inspect exact PID before retrying'}
if($p.ExitCode -ne 0){throw "Native exit $($p.ExitCode)"}
if(!(Select-String -Path $log -SimpleMatch 'TIER071 NATIVE CAPTURES COMPLETE')){throw 'Missing native completion'}
if(Select-String -Path $log -Pattern 'NullReferenceException|MissingReferenceException|Error:|Shader error'){throw 'Native error; inspect log'}
foreach($width in @(1440,844)){
 foreach($name in @('rods','nets','condition','processing','crew')){
  if(!(Test-Path "$frames\tier5-$name-$width.png")){throw "Missing $name / $width capture"}
 }
}
Get-Content $log | Select-String '\[Catchline\].*(Launch mode|NATIVE CAPTURES COMPLETE)'
