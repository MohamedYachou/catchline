$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path '.').Path
$taskScratch=(Resolve-Path '../Catchline-sim').Path
$taskEvidence=Join-Path $taskRoot 'docs/screens/map10-seal-cliffs-1'
New-Item -ItemType Directory -Path $taskEvidence -Force | Out-Null
$taskExe=Join-Path $taskScratch 'Builds/Map10Capture/Catchline.exe'
$taskChecks=Get-Content (Join-Path $taskScratch 'Logs/map10-checks.json') -Raw | ConvertFrom-Json
if ($taskChecks.maps -ne 10 -or $taskChecks.hullRoutes -ne 600 -or $taskChecks.lanes -ne 30 -or !$taskChecks.assets -or !$taskChecks.anchors -or !$taskChecks.groundPoolsReady) {throw 'MAP10 check receipt incomplete'}
$taskAssets=Get-ChildItem (Join-Path $taskScratch 'Assets/Art/Models/Environment/GullSealCliffs') -File | Where-Object {$_.Extension -ne '.meta'} | ForEach-Object {
    $relative=$_.FullName.Substring($taskScratch.Length+1)
    $hash=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    $mainHash=(Get-FileHash -LiteralPath (Join-Path $taskRoot $relative) -Algorithm SHA256).Hash
    if($mainHash -ne $hash){throw "Owned build asset drift: $relative"}
    @{path=$relative;sha256=$hash;mainMatchesBuild=$true}
}
$taskSources=Get-ChildItem (Join-Path $taskScratch 'Assets/Scripts/Game') -Recurse -Filter *.cs | ForEach-Object {
    $relative=$_.FullName.Substring($taskScratch.Length+1)
    $mainSource=Join-Path $taskRoot $relative
    $hash=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    $mainHash=if(Test-Path $mainSource){(Get-FileHash -LiteralPath $mainSource -Algorithm SHA256).Hash}else{''}
    if ($relative -match 'Map10Capture.cs$|GameData.cs$|Grounds.cs$|SeaNav.cs$|VoyageScenery.cs$' -and $mainHash -ne $hash) {throw "Owned build source drift: $relative"}
    @{path=$relative;sha256=$hash;mainSha256AtLaunch=$mainHash;mainMatchesBuild=($mainHash -eq $hash)}
}
$taskLaunch=[DateTime]::UtcNow.ToString('o')
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList @('-screen-width','1280','-screen-height','720','-screen-fullscreen','0','-capture-map10',"`"$taskEvidence`"",'-logFile',"`"$taskEvidence/native.log`"") -WindowStyle Hidden -PassThru
@{launchedUtc=$taskLaunch;exe=$taskExe;pid=$taskProcess.Id;assetHashes=@($taskAssets);sourceHashes=@($taskSources);exeSha256=(Get-FileHash $taskExe).Hash;assemblySha256=(Get-FileHash (Join-Path $taskScratch 'Builds/Map10Capture/Catchline_Data/Managed/Assembly-CSharp.dll')).Hash;sceneLevel0Sha256=(Get-FileHash (Join-Path $taskScratch 'Builds/Map10Capture/Catchline_Data/level0')).Hash;sessionOnly=$true;sourceCount=@($taskSources).Count;mainDriftAtLaunch=@($taskSources | Where-Object {!$_.mainMatchesBuild} | ForEach-Object {$_.path})} | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $taskEvidence 'native-run.json')
Copy-Item ../Catchline-sim/Logs/check-map10-build.log (Join-Path $taskEvidence 'check-build.log') -Force
Copy-Item ../Catchline-sim/Logs/map10-checks.json (Join-Path $taskEvidence 'checks.json') -Force
Copy-Item ../Catchline-sim/Logs/map10-build.txt (Join-Path $taskEvidence 'build.txt') -Force
Write-Output "MAP10 native PID $($taskProcess.Id); sources $(@($taskSources).Count)"
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exitCode=$taskProcess.ExitCode;completedUtc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content (Join-Path $taskEvidence 'native-exit.json')
if($taskProcess.ExitCode -ne 0){throw "MAP10 native exit $($taskProcess.ExitCode)"}
Write-Output 'MAP10 native actual exit 0'

