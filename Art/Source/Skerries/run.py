"""WSL sequential asset runner. A Blender Python exception can still exit0: require markers."""
import subprocess,sys
from pathlib import Path
D=Path(__file__).resolve().parent
BL='/mnt/c/Program Files/Blender Foundation/Blender 5.2/blender.exe'
def run(name,steps):
    for step in steps:
        path=D/f'{name}-{step}.log'
        win=subprocess.check_output(['wslpath','-w',str(D/f'{step}.py')],text=True).strip()
        with path.open('w') as f:
            p=subprocess.run([BL,'-b','-t','6','-P',win,'--',name],stdout=f,stderr=subprocess.STDOUT)
        msg=path.read_text(errors='replace')
        marker={'build':'SKERRIES BUILT','audit':'SKERRIES AUDIT PASS','render':'SKERRIES RENDERS'}[step]
        assert p.returncode==0 and marker in msg and 'Traceback' not in msg,(name,step,msg[-5000:])
        print(name,step,'PASS',flush=True)
if __name__=='__main__':
    # First argument is comma-separated steps; subsequent arguments are asset names.
    for name in sys.argv[2:]:run(name,sys.argv[1].split(','))
