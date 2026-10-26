$ErrorActionPreference='Stop'
# check.ps1 intentionally preserves generated scratch Resources; copy the new
# production shader resource explicitly before the MAP9 tests/build.
$map9Root=(Resolve-Path '.').Path
$map9Scratch=(Resolve-Path '../Catchline-sim').Path
Copy-Item -LiteralPath (Join-Path $map9Root 'Assets/Resources/Shaders') -Destination (Join-Path $map9Scratch 'Assets/Resources') -Recurse -Force
Copy-Item -LiteralPath (Join-Path $map9Root 'Assets/Resources/Shaders.meta') -Destination (Join-Path $map9Scratch 'Assets/Resources/Shaders.meta') -Force
Get-ChildItem (Join-Path $map9Root 'Assets/Resources/Shaders') -File -Recurse | ForEach-Object {
    $relative=$_.FullName.Substring($map9Root.Length+1)
    if((Get-FileHash -LiteralPath $_.FullName).Hash -ne (Get-FileHash -LiteralPath (Join-Path $map9Scratch $relative)).Hash){throw "Scratch resource mismatch: $relative"}
}
Write-Output 'MAP9 scratch shader resources match production'

