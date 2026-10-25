"""Deterministically synthesize original PCM assets; never uses an external sample."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
import numpy as np
from scipy.io import wavfile
from dsp import FS,RECIPES,AMBIENCE_RECIPES,UI,cue,ambience,master
R=Path(__file__).resolve().parents[3];O=R/'Art/Audio'
def save(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    q=np.rint(x*32767).astype('<i2');wavfile.write(p,FS,q)
    return {'file':p.relative_to(O).as_posix(),'frames':len(q),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
rows=[]
for name in RECIPES:
    for v in range(3):
        target=(-32 if name in UI else -27 if name in {'Gull','SealBark','Horn','Bell'} else -24)+(v-1)*.2
        rows.append(save(O/f'SFX/{name}_{v}.wav',master(cue(name,v),target)))
    print(name,'built',flush=True)
for name in AMBIENCE_RECIPES:
    rows.append(save(O/f'Ambience/{name}.wav',master(ambience(name),-28)))
    print(name,'built',flush=True)
(O/'synthesis.json').write_text(json.dumps({'sample_rate':FS,'method':'Original deterministic numpy/scipy offline synthesis, no downloads, recordings, TTS or audio source files.','seed_policy':'fixed task/family/variant seed in dsp.py','files':rows},indent=2)+'\n')
print('SOUND BUILD PASS',len(rows),flush=True)
