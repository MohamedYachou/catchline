param([string]$Method='Catchline.EditorTools.FishViewChecks.Run',[string]$Name='editor-check')
$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-lead-sim'
if((Resolve-Path -LiteralPath $scratch).Path -ne $scratch){throw 'Wrong scratch path'}
$busy=Get-CimInstance Win32_Process -Filter "Name='Unity.exe'" | Where-Object {$_.CommandLine -like '*Catchline-lead-sim*' -and $_.CommandLine -notlike '*AssetImportWorker*'}
if($busy){throw 'Assigned scratch editor still running'}
robocopy "$project\Assets\Scripts" "$scratch\Assets\Scripts" /E /NFL /NDL /NJH /NJS | Out-Null
if($LASTEXITCODE -ge 8){throw 'Script sync failed'}
robocopy "$project\Assets\Editor" "$scratch\Assets\Editor" /E /NFL /NDL /NJH /NJS | Out-Null
if($LASTEXITCODE -ge 8){throw 'Editor sync failed'}
$log="$project\docs\screens\fish-view-1\$Name.log"
$args=@('-batchmode','-quit','-projectPath',"`"$scratch`"",'-executeMethod',$Method,'-logFile',"`"$log`"")
$p=Start-Process 'C:\Program Files\Unity\Hub\Editor\6000.3.25f1\Editor\Unity.exe' -ArgumentList $args -WindowStyle Hidden -PassThru
Write-Output "Scratch $Name PID $($p.Id); log $log"
