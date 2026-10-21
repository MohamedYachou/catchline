$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
New-Item "$project\docs\screens\dash082" -ItemType Directory -Force | Out-Null
& "$project\docs\tools\check.ps1" -Name dash082 -Method Catchline.EditorTools.DashboardChecks.FinalValidateAndBuild
if(!(Select-String -Path "$scratch\Logs\check-dash082.log" -SimpleMatch -Pattern 'DASH082 CHECKS PASSED')){throw 'Missing dashboard checks'}
Copy-Item "$scratch\Logs\check-dash082.log" "$project\docs\screens\dash082\unity-check.log"
