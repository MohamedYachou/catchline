$ErrorActionPreference='Stop'
$project='C:\Users\momoy\Projects\Catchline'
$scratch='C:\Users\momoy\Projects\Catchline-sim'
& "$project\docs\tools\check.ps1" -Name management078 -Method Catchline.EditorTools.ManagementChecks.FinalValidateAndBuild
if(!(Select-String -Path "$scratch\Logs\check-management078.log" -SimpleMatch -Pattern 'MANAGEMENT078 CHECKS PASSED')){throw 'Missing management checks'}

Copy-Item "$scratch\Logs\check-management078.log" "$project\docs\screens\management078\unity-check.log"
