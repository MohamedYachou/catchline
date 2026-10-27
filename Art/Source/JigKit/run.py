import subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent;BL='/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe'
for step in sys.argv[1].split(','):
 for kit in sys.argv[2:]:
  script=D/(step+'.py');win=subprocess.check_output(['wslpath','-w',str(script)],text=True).strip();log=D/(kit+'-'+step+'.log')
  with log.open('w') as f:p=subprocess.run([BL,'-b','-t','6','-P',win,'--',kit],stdout=f,stderr=subprocess.STDOUT)
  txt=log.read_text(errors='replace');assert p.returncode==0 and {'build':'KIT BUILT','audit':'KIT AUDIT PASS','render':'KIT RENDERS'}[step] in txt and 'Traceback' not in txt,(step,kit,txt[-2500:])
  print(step,kit,'PASS',flush=True)
