$ErrorActionPreference='Stop'
$taskRoot='C:/Users/momoy/Projects/Catchline'
$taskScratch='C:/Users/momoy/Projects/Catchline-sim'
$taskEvidence=$PSScriptRoot
$taskExe="$taskScratch/Builds/Map10Capture/Catchline.exe"
$taskSources=Get-ChildItem "$taskScratch/Assets/Scripts/Game" -Recurse -Filter *.cs | ForEach-Object {
 $relative=$_.FullName.Substring($taskScratch.Length+1)
 $main=Join-Path $taskRoot $relative
 $hash=(Get-FileHash -LiteralPath $_.FullName).Hash
 $mainHash=if(Test-Path -LiteralPath $main){(Get-FileHash -LiteralPath $main).Hash}else{'SCRATCH FIXTURE'}
 if($mainHash -ne 'SCRATCH FIXTURE' -and $hash -ne $mainHash){throw "Game source drift: $relative"}
 @{path=$relative;sha256=$hash;mainSha256=$mainHash}
}
$taskLaunch=[DateTime]::UtcNow.ToString('o')
$taskProcess=Start-Process -FilePath $taskExe -ArgumentList @('-screen-width','1280','-screen-height','720','-screen-fullscreen','0','-capture-integration',"`"$taskEvidence`"",'-logFile',"`"$taskEvidence/native.log`"") -WindowStyle Hidden -PassThru
@{launchedUtc=$taskLaunch;pid=$taskProcess.Id;sessionOnly=$true;exeSha256=(Get-FileHash $taskExe).Hash;assemblySha256=(Get-FileHash "$taskScratch/Builds/Map10Capture/Catchline_Data/Managed/Assembly-CSharp.dll").Hash;sources=@($taskSources)} | ConvertTo-Json -Depth 5 | Set-Content "$taskEvidence/native-run.json"
$taskProcess.WaitForExit()
@{pid=$taskProcess.Id;exitCode=$taskProcess.ExitCode;completedUtc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content "$taskEvidence/native-exit.json"
if($taskProcess.ExitCode -ne 0){throw "Native exit $($taskProcess.ExitCode)"}
Write-Output 'Integration native actual exit 0'
