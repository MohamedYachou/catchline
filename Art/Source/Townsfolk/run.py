import subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent;BL='/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe'
for step in sys.argv[1].split(','):
 win=subprocess.check_output(['wslpath','-w',str(D/(step+'.py'))],text=True).strip();log=D/(step+('-'+sys.argv[2] if step=='render' and len(sys.argv)>2 else '')+'.log')
 with log.open('w') as f:p=subprocess.run([BL,'-b','-t','6','-P',win]+(['--']+sys.argv[2:] if len(sys.argv)>2 else []),stdout=f,stderr=subprocess.STDOUT)
 t=log.read_text(errors='replace');assert p.returncode==0 and 'TOWNSFOLK '+step.upper()+' PASS' in t and 'Traceback' not in t,(step,t[-2600:])
 print(step,'PASS',flush=True)
