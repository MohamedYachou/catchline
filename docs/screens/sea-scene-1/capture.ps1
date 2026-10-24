param([switch]$SkipBuild)
$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-ui2-sim'
$out="$project\docs\screens\sea-scene-1"
$frames="$scratch\Logs\sea-scene-1"
$save=Join-Path $env:USERPROFILE 'AppData\LocalLow\DefaultCompany\Catchline\catchline-save.json'
function Fingerprint { if(Test-Path -LiteralPath $save){return (Get-FileHash -LiteralPath $save).Hash}; return 'absent' }
$before=Fingerprint
$env:UNITY_NO_BANNER=1; $env:UNITY_PROJECT_PATH=$scratch
if(!$SkipBuild){
    robocopy "$project\Assets" "$scratch\Assets" /E /XF ArtLibrary.asset UiV2Preview.unity UiV2Preview.unity.meta /NFL /NDL /NJH /NJS | Out-Null
    if($LASTEXITCODE -ge 8){throw "Sync failed $LASTEXITCODE"}
    # /E preserves files deleted by the shared capture-harness cleanup. Prune
    # only script copies whose canonical source no longer exists.
    foreach($area in @('Scripts','Editor')){
        Get-ChildItem "$scratch\Assets\$area" -Filter *.cs -Recurse | ForEach-Object {
            $relative=$_.FullName.Substring(("$scratch\Assets\").Length)
            if(!(Test-Path -LiteralPath "$project\Assets\$relative")){
                Remove-Item -LiteralPath $_.FullName
                Remove-Item -LiteralPath ($_.FullName+'.meta') -ErrorAction SilentlyContinue
            }
        }
    }
    $compile=unity recompile --project-path $scratch --timeout 120 --focus
    if($LASTEXITCODE -ne 0){throw 'Scratch recompile command failed'}
    $compile | Out-File -Encoding utf8 "$out\capture-compile.tsv"
    if($compile -match '(?m)^error\s'){throw 'Scratch compile failed; see capture-compile.tsv'}
    unity status --until-ready --project-path $scratch | Out-Null
    $marker="$scratch\Logs\sea-build.txt"
    Remove-Item -LiteralPath $marker -ErrorAction SilentlyContinue
    unity command script eval --code "Catchline.EditorTools.SeaCaptureBuild.Run();" --timeout 1800 | Out-File "$out\build-command.tsv"
    for($i=0;$i -lt 360 -and !(Test-Path $marker);$i++){Start-Sleep 5}
    if(!(Test-Path $marker) -or (Get-Content $marker -Raw).Trim() -ne 'Succeeded'){throw 'Native build failed'}
}
New-Item -ItemType Directory -Force $frames | Out-Null
$log="$scratch\Logs\sea-scene-1-native.log"
$arguments=@('-capture-sea',"`"$frames`"",'-screen-width','1440','-screen-height','900','-screen-fullscreen','0','-force-d3d11','-logFile',"`"$log`"")
$p=Start-Process "$scratch\Builds\SeaCapture\Catchline.exe" -ArgumentList $arguments -PassThru
if(!$p.WaitForExit(1200000)){throw "Capture still running PID $($p.Id)"}
Copy-Item $log "$out\native.log" -Force
if(!(Select-String -Path $log -SimpleMatch 'SEA CAPTURES COMPLETE')){throw 'Native capture incomplete'}
if(Select-String -Path $log -Pattern 'Exception|Shader error'){throw 'Native errors'}
if(!(Select-String -Path $log -SimpleMatch 'Launch mode: TEST')){throw 'Not TEST mode'}
$after=Fingerprint
if($before -ne $after){throw "Save changed: $before -> $after"}
Copy-Item "$frames\*.png" $out -Force
"TEST native player; save unchanged ($after); exit=$($p.ExitCode); frames=$((Get-ChildItem $frames -Filter *.png).Count)" | Tee-Object -FilePath "$out\capture-result.txt"
