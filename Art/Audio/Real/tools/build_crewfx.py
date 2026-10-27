"""Recording-only CREW-FX edits. No generated excitation or pitch changes."""
from pathlib import Path
import sys,json,subprocess,hashlib,zipfile
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];O=R/'Art/Audio/Real'
sys.path.insert(0,str(R/'Art/Source/Audio'))
import numpy as np
from scipy import signal
import build3
from dsp import FS,edge
INDEX=json.loads((O/'sources/index.json').read_text())+json.loads((O/'sources/crewfx/index.json').read_text())
CACHE={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 if p in CACHE:return CACHE[p]
 for r in INDEX:
  original=R/r['local']
  if p==original or original.suffix=='.zip' and p.is_relative_to(original.parent/'extracted'):
   assert r['clean'] and r['scan_returncode']==0 and sha(original)==r['sha256']
   if p!=original:
    member=p.relative_to(original.parent/'extracted').as_posix()
    with zipfile.ZipFile(original) as z:assert z.read(member)==p.read_bytes(),member
   b=subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ar',str(FS),'-ac','1','pipe:1'])
   CACHE[p]=(np.frombuffer(b,dtype='<f4').astype(float),r);return CACHE[p]
 raise ValueError('No clean matching receipt: '+str(p))
def cut(p,start=0,end=None,trim=False,low=8000):
 x,r=read(p);a=round(start*FS);b=min(len(x),round(end*FS)) if end is not None else len(x)
 if trim:
  active=np.flatnonzero(abs(x[a:b])>max(float(abs(x[a:b]).max())*.012,1e-7))
  if len(active):a0=a;a=max(a,a0+int(active[0])-round(.02*FS));b=min(b,a0+int(active[-1])+round(.08*FS))
 y=signal.sosfilt(signal.butter(2,[45,low],btype='bandpass',fs=FS,output='sos'),x[a:b]);y=edge(y-y.mean(),12)
 return y,{'source':str(p.relative_to(R)),'source_sha256':sha(p),'original':r['local'],'original_sha256':r['sha256'],'source_page':r['source_page'],'author':r['author'],'license':r['license'],'license_url':r['license_url'],'start_seconds':a/FS,'end_seconds':b/FS,'highpass_hz':45,'lowpass_hz':low,'edge_fade_ms':12}
def select_third(p,v,duration,low=8000):
 x,_=read(p);lo=round(v*len(x)/3);hi=round((v+1)*len(x)/3);window=round(duration*FS)
 # Distinct third; start before its largest event, bounded to that third.
 peak=lo+int(np.argmax(abs(x[lo:hi])));a=max(lo,min(peak-round(.05*FS),hi-window));return cut(p,a/FS,min(hi,a+window)/FS,low=low)
def emit(name,v,parts,note,target):
 y,m=build3.layer([(x,meta,at,gain) for (x,meta),at,gain in parts]);build3.write(f'{name}_{v}',y,m,target,note)
def hundred(name):return R/'Art/Audio/Downloads/oga-100-cc0-sfx/extracted'/(name+'.ogg')
def run():
 assert not (O/'crewfx-edits.json').exists(),'Refuse accidental overwrite; remove own manifest explicitly before rebuild.'
 for name,slug,cuts,note in [
 ('Gull','Gull',[(.02,3.35),(6.15,9.1),(10.55,13.8)],'Real herring gull, Long Island; distinct source passages.'),
 ('Puffin','Puffin',[(4.5,6.8),(18.6,21.5),(57.5,60.8)],'Real Atlantic puffin, Lawrence Shove, Skokholm1965; edited excerpts CC BY-SA4.0. Field background retained.'),
 ('Foghorn','Foghorn',[(2.0,11.3),(61.9,71.3),(121.9,131.3)],'Real Gislövsläge compressed-air foghorn; three separately recorded short/long signal cycles.'),
 ('SealBark','SealBark',[(.1,.72)],'One real zoo seal call; species unspecified by source, not a verified grey seal.'),
 ('Horn','ShipHornClean',[(0,1.897)],'One real steamboat Blümlisalp horn; no artificial variants.')]:
  p=O/'sources/crewfx'/(slug+('.wav' if slug=='SealBark' else '.ogg'))
  for v,(a,b) in enumerate(cuts):emit(name,v,[(cut(p,a,b,low=8500),0,1)],note,-27)
 for v in range(3):
  box=cut(hundred('wooded_box_open'),trim=True,low=6000)
  wood=cut(hundred(f'wooden_{v+1:02d}'),trim=True,low=4500)
  squeak=cut(hundred(['door_01','door_02','door_open'][v]),trim=True,low=6000)
  key=cut(hundred('key_open_02' if v==1 else 'key_open_01'),trim=True,low=7000)
  creak=select_third(R/'Art/Audio/Downloads/oga-tree-creaking/tree_creak.flac',v,.72,low=4500)
  emit('ChestCrateOpen',v,[(box,0,1),(wood,.04,.25),(creak,.08,.45)],'Actual wooden-box opening, recorded tree/wood creak and distinct wood contact; same box take reused across variants.',-24)
  emit('ChestHeavyOpen',v,[(key,0,.8),(squeak,.12,1),(wood,.15,.3)],'Recorded key/latch, distinct door movement and wood contact; heavy-chest foley recreation.',-24)
  coin=select_third(R/'Art/Audio/Downloads/oga-coin-sounds/coinsounds011015.wav',v,1.8)
  coin2=select_third(R/'Art/Audio/Downloads/oga-coin-sounds/coinsounds011015.wav',(v+1)%3,1.8)
  coin3=select_third(R/'Art/Audio/Downloads/oga-coin-sounds/coinsounds011015.wav',(v+2)%3,1.8)
  emit('TokenPour',v,[(coin,0,1),(coin2,.12+v*.025,.7),(coin3,.27+v*.02,.5)],'Layered real coin-handling passages for a denser token pour; three montage thirds reused in rotated placements, no new recorded pour.',-24)
  swish=cut(R/f'Art/Audio/Downloads/oga-swishes-sound-pack/extracted/swishes/swish-{v+1}.wav',trim=True,low=9000)
  paper=cut(hundred(f'paper_{v+1:02d}'),0,.10,low=7000)
  emit('CardFlip',v,[(swish,0,1),(paper,.015,.3)],'Recorded hanger/stick air movement and paper movement; short card flip foley.',-32)
  bell=cut(hundred(f'bell_{v+1:02d}'),trim=True,low=10000)
  emit('RewardChime',v,[(bell,0,1)],'Distinct recorded household bell strike; bright single reward ding, no synthesized melody.',-27)
 out={'task':'CREW-FX-ART-1','method':'Recording crops, mono44.1k resample, filters, fades, DC correction, gain-only transient control, real recording layers; no pitch change/synthesis.','files':build3.ROWS}
 (O/'crewfx-edits.json').write_text(json.dumps(out,indent=2)+'\n')
 print('BUILT',len(build3.ROWS),flush=True)
if __name__=='__main__':run()
