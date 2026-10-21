$ErrorActionPreference='Stop'
$base='C:\Users\momoy\Projects\Catchline-sim'
$frames='C:\Users\momoy\Projects\Catchline\docs\screens\balance045'
$log="$base\Logs\balance045-native.log"
$arguments=@('-prepboat-trial','-capture-balance045',"`"$frames`"",'-screen-width','640','-screen-height','360','-force-d3d11','-screen-fullscreen','0','-logFile',"`"$log`"")
$p=Start-Process "$base\Builds\Tier033\Catchline.exe" -ArgumentList $arguments -PassThru -WindowStyle Hidden
Write-Output "BALANCE045 native PID $($p.Id)"
$p.WaitForExit()
Get-Content $log | Select-String '\[Catchline\].*(Launch mode|BALANCE045 NATIVE)|Exception|Error'
if($p.ExitCode -ne 0){throw "Native exit $($p.ExitCode)"}
if(!(Select-String -Path $log -SimpleMatch 'BALANCE045 NATIVE CAPTURES COMPLETE')){throw 'Missing capture completion'}
if(Select-String -Path $log -Pattern 'NullReferenceException|MissingReferenceException|IndexOutOfRangeException|ArgumentException'){throw 'Native exception'}
