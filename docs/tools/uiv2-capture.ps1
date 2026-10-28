# UI v2 native acceptance captures (docs/UI-SYSTEM.md). Save-isolated TEST player only.
# Builds in the live scratch editor C:\Users\momoy\Projects\Catchline-ui2-sim (never the main project,
# never batchmode), runs Builds\UiV2\Catchline.exe -capture-uiv2 at 1440x900 and 844x390, verifies the
# player's real save is byte-identical, then writes docs/screens/ui-v2/<screen>-{1440,844}.png and
# <screen>-compare.png (concept beside native).
param([string]$Screens = 'voyage', [switch]$SkipBuild)
$ErrorActionPreference = 'Stop'
$project = 'C:\Users\momoy\Projects\Catchline'
$scratch = 'C:\Users\momoy\Projects\Catchline-ui2-sim'
$out = "$project\docs\screens\ui-v2"
$frames = "$scratch\Logs\uiv2-native"
$save = Join-Path $env:USERPROFILE 'AppData\LocalLow\DefaultCompany\Catchline\catchline-save.json'
function Fingerprint { if (Test-Path -LiteralPath $save) { return (Get-FileHash -LiteralPath $save).Hash }; return 'absent' }
$before = Fingerprint
$env:UNITY_NO_BANNER = 1; $env:UNITY_PROJECT_PATH = $scratch
if (!$SkipBuild) {
    robocopy "$project\Assets" "$scratch\Assets" /MIR /XF ArtLibrary.asset UiV2Preview.unity UiV2Preview.unity.meta /NFL /NDL /NJH /NJS | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Asset sync failed: $LASTEXITCODE" }
    unity command editor.playmode stop | Out-Null
    $errors = unity recompile --project-path $scratch | Select-String -NotMatch '^severity'
    if ($errors) { throw "Compile errors: $errors" }
    unity status --until-ready --timeout 60 --project-path $scratch | Out-Null
    # The player stub keeps its template timestamp, so the build writes an explicit marker.
    $marker = "$scratch\Logs\uiv2-build.txt"
    Remove-Item -LiteralPath $marker -ErrorAction SilentlyContinue
    Start-Sleep 5; unity status --until-ready --timeout 60 --project-path $scratch | Out-Null
    unity command editor invoke_menu --path 'Catchline/UI v2 Build Preview' --timeout 1800 | Out-Null
    for ($i = 0; $i -lt 360 -and !(Test-Path $marker); $i++) { Start-Sleep 5 }
    if (!(Test-Path $marker) -or (Get-Content $marker -Raw).Trim() -ne 'Succeeded') { throw 'UIV2 player build did not succeed' }
    unity status --until-ready --timeout 60 --project-path $scratch | Out-Null
}
Remove-Item -LiteralPath $frames -Recurse -Force -ErrorAction SilentlyContinue
$log = "$scratch\Logs\uiv2-native.log"
$arguments = @('-capture-uiv2', "`"$frames`"", '-uiv2-screens', $Screens, '-screen-width', '1440', '-screen-height', '900', '-screen-fullscreen', '0', '-force-d3d11', '-logFile', "`"$log`"")
$p = Start-Process "$scratch\Builds\UiV2\Catchline.exe" -ArgumentList $arguments -PassThru
if (!$p.WaitForExit(600000)) { throw "Capture still running; inspect PID $($p.Id)" }
if (!(Select-String -Path $log -SimpleMatch 'UIV2 CAPTURES COMPLETE')) { throw "Capture incomplete; read $log" }
if (Select-String -Path $log -Pattern 'Exception|Shader error') { throw "Native exception; read $log" }
if (!(Select-String -Path $log -SimpleMatch 'Launch mode: TEST')) { throw 'Player did not run in TEST mode' }
$after = Fingerprint
if ($after -ne $before) { throw "Player save changed during capture ($before -> $after)" }
New-Item -ItemType Directory -Force $out | Out-Null
Copy-Item "$frames\*.png" $out -Force
wsl.exe -d Ubuntu -- /home/mo/.venvs/catchline-ui/bin/python /mnt/c/Users/momoy/Projects/Catchline/Art/Source/compare_ui_v2.py $Screens.Split(',')
Write-Output "UIV2 native captures: $Screens; player save unchanged ($after)"
