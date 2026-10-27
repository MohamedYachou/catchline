$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-lead-sim'
$play='C:\Users\momoy\Projects\Catchline-play'
$evidence=Join-Path $project 'docs\screens\fish-view-1'
function Hash($p) { (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash }
$files=@('Assets/Scripts/Game/DeckActors.cs','Assets/Scripts/Game/VoyageGame.cs',
    'Assets/Scripts/Game/VoyageInterface.cs','Assets/Scripts/Game/VoyageUiV2Capture.cs',
    'Assets/Editor/FishViewChecks.cs','Assets/Editor/FishViewChecks.cs.meta',
    'Assets/Editor/FishRodImport.cs','Assets/Editor/FishRodImport.cs.meta')
$files+=Get-ChildItem (Join-Path $project 'Assets/Scripts/Game/Minigame') -File -Recurse |
    Where-Object { $_.Name -notlike 'BiteModel*' } | ForEach-Object { $_.FullName.Substring($project.Length+1) }
$files+=Get-ChildItem (Join-Path $project 'Assets/Art/Models/FishRodFP') -File -Recurse |
    ForEach-Object { $_.FullName.Substring($project.Length+1) }
$sources=foreach($f in $files){
    $a=Hash (Join-Path $project $f); $b=Hash (Join-Path $scratch $f)
    if($a -ne $b){throw "Source/scratch mismatch: $f"}
    [pscustomobject]@{Path=$f;SHA256=$a}
}
$wsh=New-Object -ComObject WScript.Shell
$installed=foreach($mode in 'Real','Test'){
    $binaries=foreach($f in 'Catchline.exe','Catchline_Data/Managed/Assembly-CSharp.dll'){
        $a=Hash (Join-Path "$scratch/Builds/Catchline/$mode" $f)
        $b=Hash (Join-Path "$play/$mode" $f)
        if($a -ne $b){throw "Installed binary differs: $mode/$f"}
        [pscustomobject]@{Path=$f;SHA256=$a}
    }
    $name=if($mode -eq 'Real'){'Catchline.lnk'}else{'Catchline - Test.lnk'}
    $link=$wsh.CreateShortcut((Join-Path ([Environment]::GetFolderPath('Desktop')) $name))
    if($link.TargetPath -ne "$play\$mode\Catchline.exe" -or $link.Arguments -ne '-native-display'){throw "Wrong shortcut $name"}
    [pscustomobject]@{Mode=$mode;Binaries=$binaries;Shortcut=$name;Target=$link.TargetPath;Arguments=$link.Arguments}
}
$installed | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $evidence 'install-receipt.json') -Encoding utf8
$before=Get-Content (Join-Path $evidence 'save-before.json') -Raw | ConvertFrom-Json
$item=Get-Item -LiteralPath $before.Path
$after=[pscustomobject]@{Path=$item.FullName;SHA256=(Hash $item.FullName);Length=$item.Length;LastWriteUtc=$item.LastWriteTimeUtc.ToString('o')}
if($after.SHA256 -ne $before.SHA256 -or $after.Length -ne $before.Length -or $after.LastWriteUtc -ne $before.LastWriteUtc){throw 'Player save changed'}
$after | ConvertTo-Json | Set-Content (Join-Path $evidence 'save-after.json') -Encoding utf8
$native=Get-Content (Join-Path $evidence 'native.log') -Raw
if($native -notmatch 'FISH VIEW CAPTURES COMPLETE' -or $native -match 'Non-Legacy|Exception|Shader error|NullReference'){throw 'Native log failed'}
$build=Get-Content (Join-Path $evidence 'native-legacy-check-build.log') -Raw
if($build -notmatch 'FISH VIEW CHECKS PASSED' -or ([regex]::Matches($build,'\[Catchline\] GAME BUILT')).Count -ne 2 -or $build -notmatch 'return code 0'){throw 'Checks/build did not complete'}
Add-Type -AssemblyName System.Drawing
$reviewed=@(Get-Content (Join-Path $evidence 'reviewed-images.txt'))
$pngs=@(Get-ChildItem $evidence -File -Filter '*.png' | Sort-Object Name)
if($pngs.Count -ne 132){throw "Expected 132 final native images, got $($pngs.Count)"}
$frames=foreach($f in $pngs){
    if($reviewed -notcontains $f.Name){throw "Image not individually reviewed: $($f.Name)"}
    $im=[System.Drawing.Image]::FromFile($f.FullName)
    try{
        $expected=if($f.Name -like '*-1440.png'){@(1440,900)}else{@(844,390)}
        if($im.Width -ne $expected[0] -or $im.Height -ne $expected[1]){throw "Wrong dimensions $($f.Name)"}
        [pscustomobject]@{File=$f.Name;Width=$im.Width;Height=$im.Height;SHA256=(Hash $f.FullName)}
    }finally{$im.Dispose()}
}
$frames | ConvertTo-Json -Depth 4 | Set-Content (Join-Path $evidence 'frames.json') -Encoding utf8
[pscustomobject]@{Sources=$sources;Installed=$installed;SaveUnchanged=$true;NativeImages=$frames.Count;
    Limits='Clock-controlled TEST capture; no hand-played Real/touch acceptance. Tips persist only for the current session; save persistence is outside brief scope.'} |
    ConvertTo-Json -Depth 8 | Set-Content (Join-Path $evidence 'verification-receipt.json') -Encoding utf8
Write-Output "Verified $($sources.Count) source files, Real+Test installed pair/shortcuts, unchanged save, $($frames.Count) individually reviewed native PNGs."
