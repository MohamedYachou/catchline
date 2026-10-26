$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path '.').Path
$taskScratch=(Resolve-Path '../Catchline-sim').Path
$taskEvidence=Join-Path $taskRoot 'docs/screens/map9-whale-shelf-1'
$taskExe=Join-Path $taskScratch 'Builds/Map9Capture/Catchline.exe'
$taskSources=Get-ChildItem (Join-Path $taskScratch 'Assets/Scripts/Game') -Recurse -Filter *.cs | ForEach-Object {
    $relative=$_.FullName.Substring($taskScratch.Length+1)
    $mainSource=Join-Path $taskRoot $relative
    $hash=(Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
    $mainHash=if(Test-Path $mainSource){(Get-FileHash -LiteralPath $mainSource -Algorithm SHA256).Hash}else{''}
    if ($relative -match 'Map9Capture.cs$|GameData.cs$|Grounds.cs$|SeaNav.cs$|VoyageScenery.cs$' -and $mainHash -ne $hash) {throw "Owned build source drift: $relative"}
    @{path=$relative;sha256=$hash;mainSha256AtLaunch=$mainHash;mainMatchesBuild=($mainHash -eq $hash)}
}
$taskLaunch=[DateTime]::UtcNow.ToString('o')
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList @('-capture-map9',"`"$taskEvidence`"",'-logFile',"`"$taskEvidence/native.log`"") -WindowStyle Hidden -PassThru
@{launchedUtc=$taskLaunch;exe=$taskExe;pid=$taskProcess.Id;sourceHashes=@($taskSources);exeSha256=(Get-FileHash $taskExe).Hash;assemblySha256=(Get-FileHash (Join-Path $taskScratch 'Builds/Map9Capture/Catchline_Data/Managed/Assembly-CSharp.dll')).Hash;sceneLevel0Sha256=(Get-FileHash (Join-Path $taskScratch 'Builds/Map9Capture/Catchline_Data/level0')).Hash;sessionOnly=$true;sourceCount=@($taskSources).Count;mainDriftAtLaunch=@($taskSources | Where-Object {!$_.mainMatchesBuild} | ForEach-Object {$_.path})} | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $taskEvidence 'native-run.json')
Copy-Item ../Catchline-sim/Logs/check-map9-safety-build.log docs/screens/map9-whale-shelf-1/check-map9-safety-build.log -Force
Copy-Item ../Catchline-sim/Logs/check-map9-final-build.log docs/screens/map9-whale-shelf-1/check-map9-final-build.log -Force
Copy-Item ../Catchline-sim/Logs/map9-final-checks.json docs/screens/map9-whale-shelf-1/map9-final-checks.json -Force
Copy-Item ../Catchline-sim/Logs/map9-build.txt docs/screens/map9-whale-shelf-1/map9-build.txt -Force
Write-Output "MAP9 native PID $($taskProcess.Id); sources $(@($taskSources).Count)"
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exitCode=$taskProcess.ExitCode;completedUtc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content (Join-Path $taskEvidence 'native-exit.json')
if($taskProcess.ExitCode -ne 0){throw "MAP9 native exit $($taskProcess.ExitCode)"}
Write-Output 'MAP9 native actual exit 0'

