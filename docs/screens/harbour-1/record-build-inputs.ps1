$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-lead-sim'
$files=@(Get-ChildItem "$project/Assets/Scripts","$project/Assets/Editor","$project/Assets/Art/Models/GullHarbourV2" -Recurse -File | Where-Object {$_.Extension -in '.cs','.shader','.fbx','.meta'})
$rows=foreach($file in $files){
 $relative=$file.FullName.Substring($project.Length+1).Replace('\','/')
 $hash=(Get-FileHash -LiteralPath $file.FullName).Hash
 if($hash -ne (Get-FileHash -LiteralPath (Join-Path $scratch $relative)).Hash){throw "Scratch input differs: $relative"}
 [pscustomobject]@{Path=$relative;SHA256=$hash;Bytes=$file.Length}
}
[pscustomobject]@{CapturedUtc=[DateTime]::UtcNow.ToString('o');Scratch=$scratch;Inputs=$rows} | ConvertTo-Json -Depth 5 |
 Set-Content "$project/docs/screens/harbour-1/build-inputs.json" -Encoding utf8
Write-Output "PASS $($rows.Count) main/scratch source, shader, import and metadata pairs."
