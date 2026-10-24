$ErrorActionPreference='Stop'
$base='C:\Users\momoy\Projects\Catchline-ui041-sim'
$frames='C:\Users\momoy\Projects\Catchline\docs\screens\ui041'
$log="$base\Logs\ui041-native.log"
$args=@('-prepboat-trial','-capture-gemini-ui',"`"$frames`"",'-screen-width','640','-screen-height','360','-force-d3d11','-screen-fullscreen','0','-logFile',"`"$log`"")
$p=Start-Process "$base\Builds\Tier033\Catchline.exe" -ArgumentList $args -WindowStyle Hidden -PassThru
Write-Output "UI041 native PID $($p.Id)"
$p.WaitForExit()
Get-Content $log | Select-String '\[Catchline\].*(Launch mode|UI041 NATIVE)|Exception|Error'
if($p.ExitCode -ne 0){throw "Native exit $($p.ExitCode)"}
if(!(Select-String -Path $log -SimpleMatch 'UI041 NATIVE CAPTURES COMPLETE')){throw 'Missing capture completion'}
if(Select-String -Path $log -Pattern 'NullReferenceException|MissingReferenceException|IndexOutOfRangeException|ArgumentException'){throw 'Native exception'}
