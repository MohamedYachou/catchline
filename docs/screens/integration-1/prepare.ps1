$ErrorActionPreference='Stop'
$taskEvidence=$PSScriptRoot
$taskScratch='C:/Users/momoy/Projects/Catchline-sim'
$taskMain='C:/Users/momoy/Projects/Catchline'
Copy-Item "$taskEvidence/IntegrationChecks.cs" "$taskScratch/Assets/Editor/IntegrationChecks.cs" -Force
Copy-Item "$taskEvidence/IntegrationNative.cs" "$taskScratch/Assets/Scripts/Game/IntegrationNative.cs" -Force
foreach($taskCapture in @('StrikeFxCapture','PetsCapture')) {
 $taskPath="$taskScratch/Assets/Editor/$taskCapture.cs"
 $taskText=[IO.File]::ReadAllText($taskPath)
 $taskText=$taskText.Replace('../Catchline/docs/screens/strike-fx','../Catchline/docs/screens/integration-1/strike-fx').Replace('../Catchline/docs/screens/harbour-pets-1','../Catchline/docs/screens/integration-1/pets')
 [IO.File]::WriteAllText($taskPath,$taskText)
}
Copy-Item "$taskMain/Assets/Resources/*" "$taskScratch/Assets/Resources" -Recurse -Force
