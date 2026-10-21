$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
$frames="$project\docs\screens\deep104"
$save=Join-Path $env:USERPROFILE 'AppData\LocalLow\DefaultCompany\Catchline\catchline-save.json'
function Fingerprint { if(Test-Path -LiteralPath $save){return (Get-FileHash -LiteralPath $save).Hash};return 'absent' }
$before=Fingerprint
$probe=Join-Path $env:TEMP ('dash087-probe-'+[Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $probe | Out-Null
if(Test-Path -LiteralPath $save){Copy-Item -LiteralPath $save -Destination "$probe\catchline-save.json"}
foreach($mode in @('Test','Real')){
 $log="$frames\native-$mode.log"
 $arguments=if($mode -eq 'Test'){@('-capture-deep104',"`"$frames`"")}else{@('-dashboard087-probe',"`"$frames`"",'-save-check-root',"`"$probe`"")}
 $arguments+=@('-screen-width','640','-screen-height','360','-force-d3d11','-screen-fullscreen','0','-logFile',"`"$log`"")
 $p=Start-Process "$scratch\Builds\Deep104\$mode\Catchline.exe" -ArgumentList $arguments -PassThru -WindowStyle Hidden
 Write-Output "$mode native PID $($p.Id)"
 if(!$p.WaitForExit(180000)){throw "$mode capture still running; inspect PID $($p.Id) before retry"}
 if($p.ExitCode -ne 0){throw "$mode native exit $($p.ExitCode)"}
 $marker=if($mode -eq 'Test'){'DEEP104 NATIVE CAPTURES PASSED'}else{'DASH087 REAL SAVE PROBE PASSED'}
 if(!(Select-String -Path $log -SimpleMatch $marker)){throw "$mode completion missing"}
 if(Select-String -Path $log -Pattern 'Exception|Error:|Shader error'){throw "$mode native error"}
}
foreach($layout in 0..2){foreach($width in @(1440,844)){foreach($state in @('boat','tab0','tab1','tab2','deckhand','chum','chum-classes')){if(!(Test-Path "$frames\layout$layout-$state-$width.png")){throw 'Missing native frame'}}}}
$roundtrip=Get-Content "$probe\catchline-save.json" -Raw | ConvertFrom-Json
$after=Fingerprint;if($after -ne $before){throw 'Player save changed during isolated verification'}
[pscustomobject]@{Version='Deep104';PlayerSaveBefore=$before;PlayerSaveAfter=$after;Unchanged=$true;ProbeHull=$roundtrip.Hull;ProbeVoyage=$roundtrip.Voyage;NativeFrames=46} | ConvertTo-Json | Set-Content "$frames\real-save-probe.json"
Remove-Item -LiteralPath $probe -Recurse
Write-Output '42 Tier5 native frames and 4 Real probe frames; real load/departure/dashboard/return/save passed. Actual player save unchanged.'
