"""New-only SOUND-2 runner. Never invokes original build/analyze/finalize scripts."""
import sys,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
for step in sys.argv[1:]:
 assert step in ['build','analyze','verify']
 with (D/(step+'2.log')).open('w') as log:p=subprocess.run([sys.executable,'-B',str(D/(step+'2.py'))],stdout=log,stderr=subprocess.STDOUT)
 msg=(D/(step+'2.log')).read_text();assert p.returncode==0 and 'SOUND2 '+({'analyze':'ANALYSIS'}.get(step,step.upper()))+' PASS' in msg and 'Traceback' not in msg,(step,msg[-4000:])
 print('SOUND2',step,'PASS',flush=True)
