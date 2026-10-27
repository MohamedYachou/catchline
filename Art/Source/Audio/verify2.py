"""Independent SOUND-2 PCM/inventory readback and protected SOUND-1 byte audit."""
from pathlib import Path
import sys,json,wave,hashlib,platform
sys.dont_write_bytecode=True
import numpy as np
import scipy
from scipy import signal
from PIL import Image
from dsp import FS,loudness
R=Path(__file__).resolve().parents[3];O=R/'Art/Audio';D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def run():
 baseline=json.loads((D/'baseline2.json').read_text());m=json.loads((O/'metrics-sound2.json').read_text());syn=json.loads((O/'synthesis-sound2.json').read_text())
 names=['Puffin','Foghorn','DogBark','Meow','Stitch','PotDrop']
 expected={f'SFX/{n}_{v}.wav' for n in names for v in range(3)}|{f'Ambience/{n}.wav' for n in ['HarbourDusk','LighthouseRock']}
 oldwav={str(Path(p).relative_to('Art/Audio')) for p in baseline['files'] if p.endswith('.wav')}
 assert len(expected)==20 and len(oldwav)==66
 assert {p.relative_to(O).as_posix() for p in O.rglob('*.wav')}==expected|oldwav
 assert m['result']=='PASS' and {r['file'] for r in m['files']}==expected=={r['file'] for r in syn['files']}
 byfile={r['file']:r for r in syn['files']};result=[];spectrum={}
 for row in m['files']:
  p=O/row['file'];h=sha(p);assert h==row['sha256']==byfile[row['file']]['sha256']
  with wave.open(str(p),'rb') as w:
   c=w.getnchannels();frames=w.getnframes();assert w.getframerate()==FS and w.getsampwidth()==2 and w.getcomptype()=='NONE'
   assert c==(2 if p.parent.name=='Ambience' else 1) and c==row['channels'] and frames==row['frames']
   pcm=np.frombuffer(w.readframes(frames),dtype='<i2').reshape(-1,c).astype('int32')
  dur=frames/FS;family=p.stem.rsplit('_',1)[0];x=pcm/32768.
  assert not np.any(np.abs(pcm)>=32767)
  assert np.max(abs(x))<10**(-3/20) and np.max(abs(signal.resample_poly(x,4,1,axis=0)))<10**(-3/20)
  assert np.max(abs(x.mean(axis=0)))<.0007
  measured,_=loudness(x);assert abs(measured-row['integrated_lufs'])<1e-7
  if c==2:
   assert frames==30*FS and np.array_equal(pcm[0],pcm[-1]) and np.array_equal(pcm[1]-pcm[0],pcm[-1]-pcm[-2])
   local=np.r_[x[-441:],x[:441]];assert np.all(np.sqrt(np.mean(local**2,axis=0))/np.sqrt(np.mean(x**2,axis=0))>.05)
   assert abs(np.corrcoef(x.T)[0,1])<.98
  else:
   assert not np.any(pcm[[0,-1]]) and np.max(abs(pcm[1]))<=3 and np.max(abs(pcm[-2]))<=3
   if family=='Puffin':assert .5<=dur<=.9
   elif family=='Foghorn':assert 2.5<=dur<=3.5
   else:assert abs(dur-{'DogBark':.25,'Meow':.4,'Stitch':.2,'PotDrop':.8}[family])<=1/FS
  # Decode-level evidence for low/distant horn; not semantic listening approval.
  if family=='Foghorn':
   freq,power=signal.welch(x[:,0],FS,nperseg=16384);dominant=float(freq[np.argmax(power)])
   below=float(power[freq<=600].sum()/power.sum());assert 35<dominant<80 and below>.94,(dominant,below)
   spectrum[p.stem]={'dominant_bin_hz':dominant,'power_fraction_below600hz':below}
  result.append({'file':row['file'],'sha256':h,'decoded_frames':frames,'channels':c})
 assert len(m['sheets'])==20 and {s['file'] for s in m['sheets']}=={p.relative_to(O).as_posix() for p in (O/'review').glob('SOUND2-*.png')}
 for s in m['sheets']:
  assert sha(O/s['file'])==s['sha256']
  with Image.open(O/s['file']) as im:assert list(im.size)==s['size'] and im.format=='PNG';im.verify()
 for name in names:
  rows=[r for r in m['files'] if r['family']==name];assert len(rows)==3 and len({r['sha256'] for r in rows})==3
  spread=max(r['integrated_lufs'] for r in rows)-min(r['integrated_lufs'] for r in rows);assert spread<2
 events=syn['ambience_events'];bells=[e for e in events['HarbourDusk'] if 'bell' in e['kind']]
 assert len(bells)==1 and bells[0]['start_seconds']==20.1
 assert {e['kind'] for e in events['HarbourDusk']}=={'piling-lap','far-gull','rope','one-far-church-bell-stroke'}
 assert {e['kind'] for e in events['LighthouseRock']}=={'rock-surf','far-puffin'}
 assert len([e for e in events['LighthouseRock'] if e['kind']=='far-puffin'])==5
 protected=[]
 for name,row in baseline['files'].items():
  if name not in baseline['aggregate_exceptions']:
   assert sha(R/name)==row['sha256'] and (R/name).stat().st_size==row['bytes'],name
   protected.append(name)
 aggregate=json.loads((O/'metrics.json').read_text());extension=aggregate.pop('sound2',None)
 assert canonical(aggregate)==baseline['sound1_metrics_canonical_sha256']
 if extension is not None:assert extension==m
 report=(O/'REPORT.md').read_bytes();prefix=report[:baseline['sound1_report_prefix_bytes']]
 assert hashlib.sha256(prefix).hexdigest()==baseline['sound1_report_prefix_sha256']
 t=np.arange(3*FS)/FS;tone=.1*np.sin(2*np.pi*1000*t);mono,_=loudness(tone);stereo,_=loudness(np.column_stack([tone,tone]))
 assert abs(mono+23)<.15 and abs(stereo+20)<.15
 receipt={'task':'SOUND-2','result':'PASS','files_verified':len(result),'sheets_verified':20,'inventory_total_wavs':86,
  'protected_unchanged_files':protected,'sound1_metrics_preserved':True,'sound1_report_prefix_preserved':True,'aggregate_extension_present':extension is not None,
  'known_tone':{'mono_1khz_minus20dbfs_lufs':mono,'stereo_1khz_minus20dbfs_lufs':stereo,'expected_mono':-23,'expected_stereo':-20,'tolerance_lu':.15},
  'low_horn_spectral_checks':spectrum,'recipe_event_contract':'one dusk bell at20.1s; two far gulls; five distant puffins; no crickets or foghorn in ambience recipe',
  'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},'decoded_files':result,
  'limits':'Decoded file and synthesis-recipe evidence only. Ear/mix/native acceptance external.'}
 (O/'verification-sound2.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('SOUND2 VERIFY PASS',len(result),'WAV20PNG',len(protected),'protected files; calibration',mono,stereo,flush=True)
if __name__=='__main__':run()
