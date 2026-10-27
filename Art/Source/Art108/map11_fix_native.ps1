$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path '.').Path
$taskScratch=(Resolve-Path '../Catchline-sim').Path
$taskEvidence=Join-Path $taskRoot 'docs/screens/map11-kelp-forest-1/fix'
New-Item -ItemType Directory -Path $taskEvidence -Force | Out-Null
$taskExe=Join-Path $taskScratch 'Builds/Map11Capture/Catchline.exe'
$taskReceipt=Get-Content (Join-Path $taskScratch 'Logs/map11-final-checks.json') -Raw | ConvertFrom-Json
if($taskReceipt.hullRoutes -ne 60 -or !$taskReceipt.anchors -or !$taskReceipt.chartPurchase){throw 'MAP11 checks incomplete'}
$taskInputs=@(Get-ChildItem (Join-Path $taskScratch 'Assets/Scripts/Game') -Filter *.cs -Recurse)
$taskInputs+=@(Get-ChildItem (Join-Path $taskScratch 'Assets/Art/Models/Environment/GullKelpForest') -File)
$taskHashes=@($taskInputs | ForEach-Object {
    $rel=$_.FullName.Substring($taskScratch.Length+1)
    $hash=(Get-FileHash -LiteralPath $_.FullName).Hash
    $mainPath=Join-Path $taskRoot $rel
    $mainHash=if(Test-Path -LiteralPath $mainPath){(Get-FileHash -LiteralPath $mainPath).Hash}else{''}
    if($rel -match 'VoyageKelpLife.cs$|VoyageCliffsLife.cs$|Map11Capture.cs$|GullKelpForest[\\/]' -and $hash -ne $mainHash){throw "Owned source/asset drift $rel"}
    @{path=$rel;sha256=$hash;mainSha256=$mainHash;matchesMain=($hash -eq $mainHash)}
})
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList @('-screen-width','1280','-screen-height','720','-screen-fullscreen','0','-capture-map11',"`"$taskEvidence`"",'-logFile',"`"$taskEvidence/native.log`"") -WindowStyle Hidden -PassThru
@{utc=[DateTime]::UtcNow.ToString('o');pid=$taskProcess.Id;sessionOnly=$true;exe=$taskExe;exeSha256=(Get-FileHash $taskExe).Hash;assemblySha256=(Get-FileHash (Join-Path $taskScratch 'Builds/Map11Capture/Catchline_Data/Managed/Assembly-CSharp.dll')).Hash;inputs=$taskHashes} | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $taskEvidence 'native-run.json')
Write-Output "MAP11 fix native PID $($taskProcess.Id)"
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exitCode=$taskProcess.ExitCode;utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content (Join-Path $taskEvidence 'native-exit.json')
if($taskProcess.ExitCode -ne 0){throw "Native failure $($taskProcess.ExitCode)"}
if(!(Select-String -LiteralPath (Join-Path $taskEvidence 'native.log') -SimpleMatch 'MAP11 LIVE MOTION PASS')){throw 'Missing motion evidence'}
Write-Output 'MAP11 fix native exit 0 and live motion PASS'
