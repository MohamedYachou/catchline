$ErrorActionPreference = 'Stop'
$built = 'C:\Users\momoy\Projects\Catchline-sim\Builds\Crew026'
$play = 'C:\Users\momoy\Projects\Catchline-play\Crew026'
$desktop = [Environment]::GetFolderPath('Desktop')
$wsh = New-Object -ComObject WScript.Shell
$results = @()
foreach ($mode in @('Real', 'Test')) {
    $sourceExe = "$built\$mode\Catchline.exe"
    if (!(Test-Path $sourceExe)) { throw "Verified build missing: $sourceExe" }
    $destination = "$play\$mode"
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    robocopy "$built\$mode" $destination /E /NFL /NDL /NJH /NJS | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "Install $mode failed" }
    $exe = "$destination\Catchline.exe"
    if ((Get-FileHash $exe).Hash -ne (Get-FileHash $sourceExe).Hash) { throw 'Installed executable hash mismatch' }
    $name = if ($mode -eq 'Real') { 'Catchline - Real Game' } else { 'Catchline - Tier 3 Test' }
    $linkPath = Join-Path $desktop "$name.lnk"
    if (Test-Path $linkPath) {
        $backup = Join-Path $env:TEMP ("crew026-" + [Guid]::NewGuid().ToString() + '.lnk')
        Copy-Item $linkPath $backup
        Write-Output "Existing shortcut backed up: $backup"
    }
    $link = $wsh.CreateShortcut($linkPath)
    $link.TargetPath = $exe
    $link.WorkingDirectory = $destination
    $link.Arguments = if ($mode -eq 'Real') { '-native-display' } else { '-crew-mix-trial -native-display' }
    $link.IconLocation = "$exe,0"
    $link.Description = if ($mode -eq 'Real') { 'Play Catchline with temporary crew contracts and persistent progress.' } else { 'Tier 3 crew test: choose any three crew contracts. Isolated from your real save.' }
    $link.Save()
    $check = $wsh.CreateShortcut($linkPath)
    if ($check.TargetPath -ne $exe -or $check.Arguments -ne $link.Arguments) { throw 'Shortcut read-back mismatch' }
    $results += [pscustomobject]@{ Mode=$mode; Shortcut=$linkPath; Target=$check.TargetPath; Arguments=$check.Arguments; Hash=(Get-FileHash $exe).Hash }
}
$results | ConvertTo-Json | Set-Content 'C:\Users\momoy\Projects\Catchline-sim\Logs\crew026\shortcuts.json'
$results | Format-List
