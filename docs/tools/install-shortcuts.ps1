# Installs the latest Catchline build (Catchline/Build Game in a scratch editor) and
# points exactly two desktop shortcuts at it: the real game and the save-free test.
param([string]$Built = 'C:\Users\momoy\Projects\Catchline-lead-sim\Builds\Catchline')
$ErrorActionPreference = 'Stop'
$play = 'C:\Users\momoy\Projects\Catchline-play'
$desktop = [Environment]::GetFolderPath('Desktop')
$wsh = New-Object -ComObject WScript.Shell
Add-Type -AssemblyName Microsoft.VisualBasic
# Older Catchline shortcuts (per-tier tests, DASH, ...) go to the Recycle Bin.
Get-ChildItem $desktop -Filter 'Catchline*.lnk' | Where-Object { $_.Name -notin 'Catchline.lnk', 'Catchline - Test.lnk' } |
    ForEach-Object { [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($_.FullName, 'OnlyErrorDialogs', 'SendToRecycleBin') }
foreach ($mode in 'Real', 'Test') {
    $sourceExe = "$Built\$mode\Catchline.exe"
    if (!(Test-Path $sourceExe)) { throw "Build missing: $sourceExe" }
    $destination = "$play\$mode"
    robocopy "$Built\$mode" $destination /MIR /NFL /NDL /NJH /NJS | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Install $mode failed" }
    $exe = "$destination\Catchline.exe"
    if ((Get-FileHash $exe).Hash -ne (Get-FileHash $sourceExe).Hash) { throw 'Installed executable hash mismatch' }
    $name = if ($mode -eq 'Real') { 'Catchline' } else { 'Catchline - Test' }
    $link = $wsh.CreateShortcut((Join-Path $desktop "$name.lnk"))
    $link.TargetPath = $exe
    $link.WorkingDirectory = $destination
    $link.Arguments = '-native-display'
    $link.IconLocation = "$exe,0"
    $link.Description = if ($mode -eq 'Real') { 'Play Catchline. Progress is saved.' } else { 'Catchline test build: pick a tier on the title screen. Never reads or writes your save.' }
    $link.Save()
    [pscustomobject]@{ Mode = $mode; Shortcut = "$name.lnk"; Target = $exe; Built = (Get-Item $sourceExe).LastWriteTime }
}

$global:LASTEXITCODE = 0
