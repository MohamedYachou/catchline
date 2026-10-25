"""Bounded sequential Windows Blender launcher, clean exit and marker required."""
import subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent
for step in sys.argv[1:]:
    win=subprocess.check_output(['wslpath','-w',str(D/(step+'.py'))],text=True).strip()
    with (D/(step+'.log')).open('w') as f:p=subprocess.run(['/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe','-b','-t','6','-P',win],stdout=f,stderr=subprocess.STDOUT)
    s=(D/(step+'.log')).read_text(errors='replace')
    assert p.returncode==0 and {'build':'GUT BUILT'}.get(step,'GUT '+step.upper()) in s and 'Traceback' not in s,(step,p.returncode,s[-6000:])
    print(step,'PASS',flush=True)
