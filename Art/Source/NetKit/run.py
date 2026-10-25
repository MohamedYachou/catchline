"""Sequential WSL -> Windows Blender runner. Require marker AND clean exit."""
import sys,subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
BL='/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe'
MARKERS={'build':'NET BUILT','audit':'NET AUDIT PASS','render':'NET RENDERS',
         'fixture_audit':'NET FIXTURE AUDIT PASS','axes':'NET AXES PASS','assembly':'NET ASSEMBLY','inspect_refs':'REFERENCE'}
def run(step,name,extra=()):
    win=subprocess.check_output(['wslpath','-w',str(D/f'{step}.py')],text=True).strip()
    path=D/f'{name}-{step}.log'
    with path.open('w') as f:
        p=subprocess.run([BL,'-b','-t','6','-P',win,'--',name,*extra],stdout=f,stderr=subprocess.STDOUT)
    msg=path.read_text(errors='replace')
    assert p.returncode==0 and MARKERS[step] in msg and 'Traceback' not in msg,(step,name,msg[-4500:])
    print(step,name,'PASS',flush=True)
if __name__=='__main__':
    extra=[a for a in sys.argv[2:] if a.startswith('--')]
    for name in [a for a in sys.argv[2:] if not a.startswith('--')]:
        for step in sys.argv[1].split(','):run(step,name,extra)
