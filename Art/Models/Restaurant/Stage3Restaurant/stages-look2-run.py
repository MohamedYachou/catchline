"""WSL launcher for the existing Windows Blender, with explicit success checks."""
from pathlib import Path
import subprocess,sys
D=Path(__file__).resolve().parent
for step in sys.argv[1:]:
 script=subprocess.check_output(['wslpath','-w',str(D/(step+'.py'))],text=True).strip()
 with (D/(step+'.log')).open('w') as log:p=subprocess.run(['/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe','-b','-t','6','-P',script],stdout=log,stderr=subprocess.STDOUT)
 s=(D/(step+'.log')).read_text(errors='replace');assert p.returncode==0 and 'Traceback' not in s,s[-3000:];print(step,'PASS',flush=True)
