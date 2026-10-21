$ErrorActionPreference='Stop'
$root='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
$e="$root\docs\screens\tier071"
Copy-Item "$scratch\Assets\Resources\ArtLibrary.asset" "$root\Assets\Resources\ArtLibrary.asset" -Force
$old=Get-Content "$e\source-verification.json" -Raw | ConvertFrom-Json
$files=foreach($entry in $old.Files){
 $a=Join-Path $root $entry.File;$b=Join-Path $scratch $entry.File
 $hash=(Get-FileHash -LiteralPath $a).Hash
 if((Get-FileHash -LiteralPath $b).Hash -ne $hash){throw "Source mismatch $($entry.File)"}
 [pscustomobject]@{File=$entry.File;SHA256=$hash}
}
$lib='Assets/Resources/ArtLibrary.asset';$hash=(Get-FileHash "$root\$lib").Hash
if((Get-FileHash "$scratch\$lib").Hash -ne $hash){throw 'Library mismatch'}
$files+= [pscustomobject]@{File=$lib;SHA256=$hash}
[pscustomobject]@{Build='tier071-delivery';Files=$files} | ConvertTo-Json -Depth 5 | Set-Content "$e\source-verification.json"
$modes=@{}
foreach($mode in @('Test','Real')){
 $base="$scratch\Builds\Tier071\$mode"
 $modes[$mode]=@(Get-ChildItem $base -Recurse -File | Where-Object {$_.FullName -notmatch 'DoNotShip'} | ForEach-Object {
  [pscustomobject]@{File=$_.FullName.Substring($base.Length+1).Replace('\','/');SHA256=(Get-FileHash -LiteralPath $_.FullName).Hash}
 })
}
[pscustomobject]@{Build='tier071-delivery';Modes=$modes} | ConvertTo-Json -Depth 6 | Set-Content "$e\build-manifest.json"
Write-Output "Source parity: $($files.Count); Test files: $($modes['Test'].Count); Real files: $($modes['Real'].Count)"
