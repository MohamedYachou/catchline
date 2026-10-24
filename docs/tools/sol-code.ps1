# Launches one fresh Sol 6.1 (medium) code session on a brief. Usage:
#   powershell -File docs\tools\sol-code.ps1 -Brief docs\briefs\SOL-CODE-1.txt
# Uses the Windows Codex account (same as Codex 1): start it only when Codex 1 is idle or Mo says so.
param([string]$Brief = 'docs\briefs\SOL-CODE-1.txt')
$p = 'C:\Users\momoy\Projects\Catchline'; Set-Location $p
$bin = (Get-ChildItem "$env:LOCALAPPDATA\OpenAI\Codex\bin\*\codex.exe" | Sort-Object LastWriteTime -Descending | Select-Object -First 1).FullName
$out = "$p\docs\briefs\_sol"; New-Item -ItemType Directory -Force $out | Out-Null
$a = @('exec','-C',$p,'-m','gpt-6.1-sol','-c','model_reasoning_effort="medium"','-c','model_auto_compact_token_limit=120000','-o',"$out\last-message.txt",'-')
Get-Content "$p\$Brief" -Raw -Encoding UTF8 | & $bin @a 2>&1 | Out-File "$out\run.log" -Encoding utf8
