param([string[]]$Names=@())
$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-lead-sim'
$busy=Get-CimInstance Win32_Process -Filter "Name='Unity.exe'" | Where-Object {$_.CommandLine -like '*Catchline-lead-sim*' -and $_.CommandLine -notlike '*AssetImportWorker*'}
if($busy){throw 'Scratch editor still running; do not mutate its assets'}
$source=Join-Path $project 'Art\Models\GullHarbour\HarbourV2'
$destination=Join-Path $project 'Assets\Art\Models\GullHarbourV2'
$scratchDestination=Join-Path $scratch 'Assets\Art\Models\GullHarbourV2'
New-Item -ItemType Directory -Path $destination,$scratchDestination -Force | Out-Null
$copies=foreach($model in Get-ChildItem -LiteralPath $source -File -Filter '*.fbx' | Where-Object {$Names.Count -eq 0 -or $_.BaseName -in $Names}){
 $hash=(Get-FileHash -LiteralPath $model.FullName).Hash
 $target=Join-Path $destination $model.Name
 Copy-Item -LiteralPath $model.FullName -Destination $target
 Copy-Item -LiteralPath $target -Destination (Join-Path $scratchDestination $model.Name)
 if(Test-Path -LiteralPath "$target.meta"){Copy-Item -LiteralPath "$target.meta" -Destination (Join-Path $scratchDestination "$($model.Name).meta")}
 if((Get-FileHash -LiteralPath $target).Hash -ne $hash -or (Get-FileHash -LiteralPath $model.FullName).Hash -ne $hash){throw "Source changed during copy: $($model.Name)"}
 [pscustomobject]@{File=$model.Name;SHA256=$hash;Bytes=$model.Length}
}
$copies | ConvertTo-Json | Set-Content (Join-Path $project 'docs/screens/harbour-1/copy-receipt.json') -Encoding utf8
$copies | Format-Table -AutoSize
& (Join-Path $project 'docs/screens/fish-polish-1/run-scratch.ps1') -Method Catchline.EditorTools.HarbourImportChecks.Run -Name harbour-import
