$ErrorActionPreference = 'Stop'
$root = 'C:\Users\momoy\Projects\Catchline'
$scratch = 'C:\Users\momoy\Projects\Catchline-sim'
$out = $PSScriptRoot
$exe = Join-Path $scratch 'Builds/Map10Capture/Catchline.exe'
$sources = @(Get-ChildItem "$scratch/Assets/Scripts/Game" -Recurse -Filter *.cs | ForEach-Object {
    $relative = $_.FullName.Substring($scratch.Length + 1)
    $hash = (Get-FileHash -LiteralPath $_.FullName).Hash
    $main = Join-Path $root $relative
    $mainHash = if (Test-Path -LiteralPath $main) { (Get-FileHash -LiteralPath $main).Hash } else { '' }
    if ($hash -ne $mainHash) { throw "Source changed since scratch sync: $relative" }
    @{path=$relative;sha256=$hash;mainMatchesBuild=$true}
})
$receipt = @{
    launchedUtc=[DateTime]::UtcNow.ToString('o'); sessionOnly=$true
    handoff='Claude MAP10 chart 060ef70'; sourceCount=$sources.Count; sources=$sources
    exeSha256=(Get-FileHash -LiteralPath $exe).Hash
    assemblySha256=(Get-FileHash -LiteralPath "$scratch/Builds/Map10Capture/Catchline_Data/Managed/Assembly-CSharp.dll").Hash
    sceneSha256=(Get-FileHash -LiteralPath "$scratch/Builds/Map10Capture/Catchline_Data/level0").Hash
}
Copy-Item "$scratch/Logs/check-map10-chart-recapture-build.log" "$out/check-build.log" -Force
Copy-Item "$scratch/Logs/map10-build.txt" "$out/build.txt" -Force
$process = Start-Process -FilePath $exe -ArgumentList @('-screen-width','1280','-screen-height','720','-screen-fullscreen','0','-capture-map10',"`"$out`"",'-logFile',"`"$out/native.log`"") -WindowStyle Hidden -PassThru
$receipt.pid = $process.Id
$receipt | ConvertTo-Json -Depth 6 | Set-Content "$out/native-run.json"
Write-Output "SessionOnly MAP10 recapture PID $($process.Id); $($sources.Count) exact source matches"
$process.WaitForExit()
@{pid=$process.Id;exitCode=$process.ExitCode;completedUtc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json | Set-Content "$out/native-exit.json"
if ($process.ExitCode -ne 0) { throw "MAP10 recapture exit $($process.ExitCode)" }
Write-Output 'MAP10 recapture native actual exit 0'
