$ErrorActionPreference='Stop'
$base='C:\Users\momoy\Projects\Catchline-sim'
$frames='C:\Users\momoy\Projects\Catchline\docs\screens\prep047'
$log="$base\Logs\prep047-native.log"
$arguments=@('-prepboat-trial','-capture-prep047',"`"$frames`"",'-screen-width','640','-screen-height','360','-force-d3d11','-screen-fullscreen','0','-logFile',"`"$log`"")
$p=Start-Process "$base\Builds\Tier033\Catchline.exe" -ArgumentList $arguments -PassThru -WindowStyle Hidden
Write-Output "PREP047 native PID $($p.Id)"
$p.WaitForExit()
if($p.ExitCode -ne 0){throw "Native exit $($p.ExitCode)"}
if(!(Select-String -Path $log -SimpleMatch 'PREP047 NATIVE CAPTURES COMPLETE')){throw 'Missing native completion'}
if(Select-String -Path $log -Pattern 'NullReferenceException|MissingReferenceException|IndexOutOfRangeException|ArgumentException'){throw 'Native exception'}
Get-Content $log | Select-String '\[Catchline\].*(Launch mode|PREP047 NATIVE)'
