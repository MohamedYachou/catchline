$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
New-Item "$project\docs\screens\dash087" -ItemType Directory -Force | Out-Null
& "$project\docs\tools\check.ps1" -Name dash087 -Method Catchline.EditorTools.DashboardMathChecks.ValidateAndBuild
if(!(Select-String -Path "$scratch\Logs\check-dash087.log" -SimpleMatch -Pattern 'DASH087 CHECKS PASSED')){throw 'Missing math checks'}
Copy-Item "$scratch\Logs\check-dash087.log" "$project\docs\screens\dash087\unity-check.log"
Copy-Item "$scratch\Logs\dash087\*.csv" "$project\docs\screens\dash087" -Force
