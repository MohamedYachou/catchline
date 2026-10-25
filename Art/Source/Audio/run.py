"""Sequential local build/check runner; no package install, network or Unity."""
import sys,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
for step in sys.argv[1:] or ['build','analyze','verify']:
    assert step in {'build','analyze','verify'},step
    with (D/(step+'.log')).open('w') as f:
        p=subprocess.run([sys.executable,str(D/(step+'.py'))],stdout=f,stderr=subprocess.STDOUT)
    log=(D/(step+'.log')).read_text()
    assert p.returncode==0 and 'SOUND '+{'build':'BUILD','analyze':'ANALYSIS','verify':'VERIFY'}[step]+' PASS' in log and 'Traceback' not in log,(step,p.returncode,log[-6000:])
    print(step,'PASS',flush=True)
