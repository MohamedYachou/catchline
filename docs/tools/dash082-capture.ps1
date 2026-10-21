$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
$frames="$project\docs\screens\dash082"
$log="$frames\native.log"
$args=@('-tier5-trial','-capture-management078',"`"$frames`"",'-screen-width','640','-screen-height','360','-force-d3d11','-screen-fullscreen','0','-logFile',"`"$log`"")
$p=Start-Process "$scratch\Builds\Dash082\Test\Catchline.exe" -ArgumentList $args -PassThru -WindowStyle Hidden
Write-Output "Dashboard native PID $($p.Id)"
if(!$p.WaitForExit(180000)){throw 'Capture still running; inspect PID before retry'}
if($p.ExitCode -ne 0){throw "Native capture exit $($p.ExitCode)"}
if(!(Select-String -Path $log -Pattern 'DASH082 NATIVE CAPTURES COMPLETE' -SimpleMatch)){throw 'Capture marker missing'}
if(Select-String -Path $log -Pattern 'NullReferenceException|MissingReferenceException|Error:|Shader error'){throw 'Native error in capture'}
foreach($width in @(1672,1440,844,1024)){foreach($state in @('entry','warmup','operations','income','odds')){if(!(Test-Path "$frames\$state-$width.png")){throw "Missing $state $width"}}}
foreach($width in @(1672,844)){foreach($state in @('blocked','full')){if(!(Test-Path "$frames\$state-$width.png")){throw "Missing $state $width"}}}
if(!(Test-Path "$frames\small-boat-1440.png")){throw 'Small boat capture missing'}
Write-Output 'All25 native captures present; no listed runtime exceptions.'
