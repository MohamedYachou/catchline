$ErrorActionPreference='Stop'
# check.ps1 intentionally preserves generated scratch Resources; copy the new
# production shader resource explicitly before the lighthouse tests/build.
$map8Root=(Resolve-Path '.').Path
$map8Scratch=(Resolve-Path '../Catchline-sim').Path
Copy-Item -LiteralPath (Join-Path $map8Root 'Assets/Resources/Shaders') -Destination (Join-Path $map8Scratch 'Assets/Resources') -Recurse -Force
Copy-Item -LiteralPath (Join-Path $map8Root 'Assets/Resources/Shaders.meta') -Destination (Join-Path $map8Scratch 'Assets/Resources/Shaders.meta') -Force
Get-ChildItem (Join-Path $map8Root 'Assets/Resources/Shaders') -File -Recurse | ForEach-Object {
    $relative=$_.FullName.Substring($map8Root.Length+1)
    if((Get-FileHash -LiteralPath $_.FullName).Hash -ne (Get-FileHash -LiteralPath (Join-Path $map8Scratch $relative)).Hash){throw "Scratch resource mismatch: $relative"}
}
Write-Output 'MAP8 scratch shader resources match production'
