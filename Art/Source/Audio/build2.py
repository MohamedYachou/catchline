"""Build ONLY the twenty new SOUND-2 WAV paths; preserve SOUND-1 byte for byte."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
import numpy as np
from scipy.io import wavfile
from dsp import FS,master
from dsp2 import RECIPES,AMBIENCE_RECIPES,TARGETS,cue,ambience
R=Path(__file__).resolve().parents[3];O=R/'Art/Audio'
def save(p,x):
 assert p.stem.split('_')[0] in set(RECIPES)|set(AMBIENCE_RECIPES)
 q=np.rint(x*32767).astype('<i2');wavfile.write(p,FS,q)
 return {'file':p.relative_to(O).as_posix(),'frames':len(q),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def run():
 rows=[];events={}
 for n in RECIPES:
  for v in range(3):rows.append(save(O/f'SFX/{n}_{v}.wav',master(cue(n,v),TARGETS[n]+(v-1)*.2)))
  print(n,'built',flush=True)
 for n in AMBIENCE_RECIPES:
  x,events[n]=ambience(n);rows.append(save(O/f'Ambience/{n}.wav',master(x,TARGETS[n])));print(n,'built',flush=True)
 (O/'synthesis-sound2.json').write_text(json.dumps({'task':'SOUND-2','sample_rate':FS,'method':'Original numpy/scipy offline synthesis only, using unchanged SOUND1 primitives; no downloads, recordings, external samples or TTS.','files':rows,'ambience_events':events},indent=2)+'\n');print('SOUND2 BUILD PASS',len(rows),flush=True)
if __name__=='__main__':run()
