"""Sequential Windows Blender runner, require explicit success markers."""
import subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent;BL='/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe'
for step in sys.argv[1].split(','):
    for name in sys.argv[2:]:
        win=subprocess.check_output(['wslpath','-w',str(D/(step+'.py'))],text=True).strip();log=D/(name+'-'+step+'.log')
        with log.open('w') as f:p=subprocess.run([BL,'-b','-t','6','-P',win,'--',name],stdout=f,stderr=subprocess.STDOUT)
        msg=log.read_text(errors='replace');marker={'build':'LIGHTHOUSE BUILT','audit':'LIGHTHOUSE AUDIT PASS','render':'LIGHTHOUSE RENDERS'}[step]
        assert p.returncode==0 and marker in msg and 'Traceback' not in msg,(name,step,msg[-3000:])
        print(name,step,'PASS',flush=True)
