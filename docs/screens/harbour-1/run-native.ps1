param([ValidateSet('harbour','overnight','polish')][string]$Set='harbour',[string]$Only='', [string]$LogName='native.log')
$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$exe='C:\Users\momoy\Projects\Catchline-play\Test\Catchline.exe'
if(Get-Process Catchline -ErrorAction SilentlyContinue){throw 'An existing player is running; preserve it'}
$screens=if($Set -eq 'harbour'){
 'harbour-h0,harbour-h1,harbour-h2,harbour-h3,harbour-h4,depart-lane,chart-leg,sea-entry,arrival-crates'
}else{
 'return-sea,return-chart,return-lane,intro-open,intro-basin,intro-berth,cage-pull,cage-snag,cage-board,net-setting,net-haul,net-bunt'
}
if($Only){$screens=$Only}
$relative=switch($Set){harbour{'docs/screens/harbour-1'}overnight{'docs/screens/overnight/native'}polish{'docs/screens/fish-polish-1'}}
$output=Join-Path $project $relative
New-Item -ItemType Directory -Force -Path $output | Out-Null
# A distinct initial size forces a swapchain resize before the first1440 capture; a hidden launch at1440 produced one black first frame.
$args=@('-screen-fullscreen','0','-screen-width','1280','-screen-height','720','-force-d3d11','-logFile',"`"$output/$LogName`"")
if($Set -eq 'polish'){$args+=@('-capture-fish-polish',"`"$output`"")}
else{$args+=@('-capture-uiv2',"`"$output`"",'-uiv2-screens',$screens)}
$process=Start-Process -FilePath $exe -WorkingDirectory (Split-Path $exe) -ArgumentList $args -WindowStyle Hidden -PassThru
[pscustomobject]@{PID=$process.Id;LaunchUtc=$process.StartTime.ToUniversalTime().ToString('o');Executable=$exe;
 ExecutableSHA256=(Get-FileHash -LiteralPath $exe).Hash;
 AssemblySHA256=(Get-FileHash -LiteralPath (Join-Path (Split-Path $exe) 'Catchline_Data/Managed/Assembly-CSharp.dll')).Hash} |
 ConvertTo-Json | Set-Content "$output/native-run.json" -Encoding utf8
Write-Output "Installed TEST $Set capture PID $($process.Id); $output/$LogName"
