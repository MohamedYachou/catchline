$ErrorActionPreference='Stop'
$env:UNITY_NO_BANNER=1
$env:UNITY_PROJECT_PATH='C:\Users\momoy\Projects\Catchline-ui2-sim'
$out='C:\Users\momoy\Projects\Catchline\docs\screens\sea-scene-1\final-checks.tsv'
$checks=@('SeaSceneChecks.Assets','SeaModeChecks.Run','M4Checks.Run')
Remove-Item -LiteralPath $out -ErrorAction SilentlyContinue
foreach($check in $checks){
    $code='Catchline.EditorTools.'+$check+'(); return true;'
    $result=unity command script eval --code $code --timeout 1200
    $exit=$LASTEXITCODE
    $result | Tee-Object -FilePath $out -Append
    if($exit -ne 0 -or $result -match '"success":false'){throw "Failed: $check"}
}
