$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
$frames="$project\docs\screens\management078"
$log="$frames\native.log"
$args=@('-tier5-trial','-capture-management078',"`"$frames`"",'-screen-width','640','-screen-height','360','-force-d3d11','-screen-fullscreen','0','-logFile',"`"$log`"")
$p=Start-Process "$scratch\Builds\Management078\Test\Catchline.exe" -ArgumentList $args -PassThru -WindowStyle Hidden
Write-Output "Management native PID $($p.Id)"
if(!$p.WaitForExit(180000)){throw 'Capture running; inspect PID before retry'}
if($p.ExitCode -ne 0){throw "Native capture exit $($p.ExitCode)"}
if(!(Select-String -Path $log -Pattern 'MANAGEMENT078 NATIVE CAPTURES COMPLETE' -SimpleMatch)){throw 'Capture marker missing'}
if(Select-String -Path $log -Pattern 'NullReferenceException|MissingReferenceException|Error:|Shader error'){throw 'Native error in capture'}
foreach($width in @(1440,844)){foreach($state in @('entry','warmup','flow','fishing','larger','blocked','full')){if(!(Test-Path "$frames\$state-$width.png")){throw "Missing $state $width"}}}
Write-Output 'All14 actual native captures present; no listed runtime exceptions.'
