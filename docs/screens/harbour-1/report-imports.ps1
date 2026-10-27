$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-lead-sim'
$evidence=Join-Path $project 'docs/screens/harbour-1'
$receipt=Get-Content (Join-Path $evidence 'import-receipt.json') -Raw | ConvertFrom-Json
function Vec($v){'{0:F3}, {1:F3}, {2:F3}' -f $v.x,$v.y,$v.z}
$lines=@('# HarbourV2 Unity import audit','',
 'Imported unchanged into Assets/Art/Models/GullHarbourV2. ArtImport.BuildLibrary and ArtLibrary.M(name) checked in Catchline-lead-sim. Bounds are complete renderer envelopes in metres; pivot and bounds use Unity XYZ. These checks do not establish occupied-berth clearance or runtime placement acceptance.','',
 '| Model | Tris | Bounds min / max (m) | Size XYZ (m) | Pivot | Import notes |',
 '|---|---:|---|---|---|---|')
foreach($r in $receipt.models){
 $source=Join-Path $project "Art/Models/GullHarbour/HarbourV2/$($r.name).fbx"
 $target=Join-Path $project $r.asset
 if((Get-FileHash -LiteralPath $source).Hash -ne $r.sha256 -or (Get-FileHash -LiteralPath $target).Hash -ne $r.sha256){throw "Model changed since audit: $($r.name)"}
 if(!$r.resolves){throw "Lookup failed: $($r.name)"}
 $metric=Get-Content (Join-Path $project "Art/Models/GullHarbour/HarbourV2/metrics/$($r.name).json") -Raw | ConvertFrom-Json
 $triangleNote=if($r.triangles -eq $metric.triangles){'Source triangles match.'}elseif($r.name -eq 'Tier5DeepLines103_VariantBlue' -and $r.triangles -eq 17006 -and $metric.triangles -eq 17096){'Source17096 includes90 inherited zero-area triangles per Codex2 read-only FBX reimport (comms.md);17006 nonzero matches Unity. Degenerate stripping is an inference; no geometry edits.'}else{"QUESTION Codex 2: Unity imports $($r.triangles) triangles; source receipt says $($metric.triangles). Geometry unchanged; discrepancy unresolved."}
 $size=$metric.dimensions_width_depth_height
 if([Math]::Abs($r.size.x-$size[0]) -gt .002 -or [Math]::Abs($r.size.y-$size[2]) -gt .002 -or [Math]::Abs($r.size.z-$size[1]) -gt .002){throw "Scale/axis discrepancy: $($r.name)"}
 $note="M(name) PASS; root rotation $(Vec $r.rootRotation), scale $(Vec $r.rootScale); $($r.notes). Source metre dimensions match. $triangleNote "
 $note+=($metric.notes -join ' ')
 $lines+="| $($r.name) | $($r.triangles) | $(Vec $r.min) / $(Vec $r.max) | $(Vec $r.size) | $(Vec $r.pivot) | $note |"
 $meta=Join-Path $scratch "$($r.asset).meta"
 if(!(Test-Path -LiteralPath "$target.meta")){Copy-Item -LiteralPath $meta -Destination "$target.meta"}
 if((Get-FileHash -LiteralPath $meta).Hash -ne (Get-FileHash -LiteralPath "$target.meta").Hash){throw "Metadata differs: $($r.name)"}
}
$folder='Assets/Art/Models/GullHarbourV2.meta'
if(!(Test-Path -LiteralPath (Join-Path $project $folder))){Copy-Item -LiteralPath (Join-Path $scratch $folder) -Destination (Join-Path $project $folder)}
$lines+=@('',"Audit contains $($receipt.models.Count) models. Full materials, SHA256 and numeric transforms: import-receipt.json. No FBX edits, renames, or material extraction. Four inherited boat variants retain source root X rotation270.0198 degrees and unit scale; runtime placement must retain their import basis. Claude HARBOUR-CODE READY is recorded; native evidence is reviewed separately.")
$lines | Set-Content (Join-Path $evidence 'IMPORT.md') -Encoding utf8
Write-Output "PASS: $($receipt.models.Count) unchanged models; source metre dimensions match; triangle exceptions explicitly recorded; GUID metadata copied back; IMPORT.md written."
