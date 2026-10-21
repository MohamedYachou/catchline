param([string]$Name = 'deep104-core', [ValidateSet('Core','Expanded','Regression','Build')][string]$Mode='Core')
$ErrorActionPreference = 'Stop'
$method=if($Mode -eq 'Expanded'){'Expanded'}elseif($Mode -eq 'Regression'){'Regression'}elseif($Mode -eq 'Build'){'BuildBoth'}else{'Run'}
& "$PSScriptRoot/check.ps1" -Name $Name -Method "Catchline.EditorTools.DeepLine104Checks.$method"
$log = "C:\Users\momoy\Projects\Catchline-sim\Logs\check-$Name.log"
$marker=if($Mode -eq 'Expanded'){'DEEP104 EXPANSION PASSED'}elseif($Mode -eq 'Regression'){'DEEP104 REGRESSION PASSED'}elseif($Mode -eq 'Build'){'Builds\Deep104\Real\Catchline.exe'}else{'DEEP104 CHECKS PASSED'}
if (!(Select-String -LiteralPath $log -SimpleMatch $marker)) { throw "Missing DEEP104 $Mode success marker" }
if(Select-String -LiteralPath $log -Pattern '^Exception:|error CS|executeMethod.*threw exception|NullReferenceException'){throw 'DEEP104 runtime/check failure'}
exit 0
