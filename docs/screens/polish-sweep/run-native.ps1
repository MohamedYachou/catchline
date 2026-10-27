param([string]$Sections='1,2,3,4,5',[string]$BuildName='PolishSweep')
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path 'C:/Users/momoy/Projects/Catchline').Path
$taskScratch=(Resolve-Path 'C:/Users/momoy/Projects/Catchline-sim').Path
$taskBuild=Join-Path $taskScratch "Builds/$BuildName"
$taskExe=Join-Path $taskBuild 'Catchline.exe'
$taskSources=@(Get-ChildItem (Join-Path $taskScratch 'Assets/Scripts/Game') -Recurse -Filter *.cs | ForEach-Object {
    $relative=$_.FullName.Substring($taskScratch.Length+1)
    $main=Join-Path $taskRoot $relative
    $hash=(Get-FileHash -LiteralPath $_.FullName).Hash
    $mainHash=if(Test-Path -LiteralPath $main){(Get-FileHash -LiteralPath $main).Hash}else{''}
    @{path=$relative;sha256=$hash;mainSha256AtLaunch=$mainHash;mainMatchesBuild=($hash -eq $mainHash)}
})
foreach($taskSection in $Sections.Split(',')) {
    $taskEvidence=Join-Path $taskRoot "docs/screens/polish-sweep/section-$taskSection"
    New-Item -ItemType Directory -Path $taskEvidence -Force | Out-Null
    $taskLaunched=[DateTime]::UtcNow.ToString('o')
    $taskProcess=Start-Process -FilePath $taskExe -ArgumentList @('-capture-polish-sweep',"`"$taskEvidence`"",'-polish-sections',$taskSection,'-logFile',"`"$taskEvidence/native.log`"") -WindowStyle Hidden -PassThru
    @{launchedUtc=$taskLaunched;pid=$taskProcess.Id;sessionOnly=$true;section=$taskSection;sourceHashes=$taskSources;exeSha256=(Get-FileHash -LiteralPath $taskExe).Hash;assemblySha256=(Get-FileHash -LiteralPath (Join-Path $taskBuild 'Catchline_Data/Managed/Assembly-CSharp.dll')).Hash;level0Sha256=(Get-FileHash -LiteralPath (Join-Path $taskBuild 'Catchline_Data/level0')).Hash} | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $taskEvidence 'native-run.json')
    $taskProcess.WaitForExit()
    @{exitCode=$taskProcess.ExitCode;finishedUtc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content (Join-Path $taskEvidence 'native-exit.json')
    Write-Output "Section $taskSection native exit $($taskProcess.ExitCode)"
}
