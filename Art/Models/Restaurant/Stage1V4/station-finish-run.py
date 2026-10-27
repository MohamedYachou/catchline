"""WSL orchestration; Windows Blender required, no Unity launch."""
from pathlib import Path
import subprocess,sys
O=Path(__file__).resolve().parent
for step in sys.argv[1:]:
 script=O/f'station-finish-{step}.py';win=subprocess.check_output(['wslpath','-w',str(script)],text=True).strip()
 with (O/f'station-finish-{step}.log').open('w') as log:p=subprocess.run(['/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe','-b','-t','6','-P',win],stdout=log,stderr=subprocess.STDOUT)
 tail=(O/f'station-finish-{step}.log').read_text(errors='replace')
 assert p.returncode==0 and 'Traceback' not in tail,(step,p.returncode,tail[-3000:]);print(step,'PASS',flush=True)
