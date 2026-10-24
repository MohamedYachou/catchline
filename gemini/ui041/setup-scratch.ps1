$ErrorActionPreference='Stop'
$root='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-ui041-sim'
New-Item -ItemType Directory -Force -Path $scratch | Out-Null
foreach($name in @('Packages','ProjectSettings','Assets/Resources')) {
    robocopy "$root/$name" "$scratch/$name" /MIR /NFL /NDL /NJH /NJS | Out-Null
    if($LASTEXITCODE -ge 8){throw "Copy failed $name"}
}
& "$root/docs/tools/check.ps1" -Name ui041 -Method Catchline.EditorTools.GeminiUiChecks.ValidateAndBuild -Scratch $scratch
