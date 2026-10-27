"""Use unchanged SOUND-1 PCM metering/plot primitives; one sheet for each new file."""
from pathlib import Path
import sys,json,hashlib
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image,ImageDraw
from dsp import FS,db
from dsp2 import RECIPES,AMBIENCE_RECIPES,DURATIONS
from analyze import O,measure,plot_panel,F14,F17,F22,decode

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sheet(x,row):
 name=Path(row['file']).stem;loop=row['channels']==2
 series=[(name,x[:,0],row)] if not loop else [(name+' / '+('left' if c==0 else 'right'),x[:,c],row) for c in range(2)]
 if loop:
  join=np.r_[x[-round(.020*FS):],x[:round(.020*FS)]];zoom=dict(row);zoom['duration_seconds']=len(join)/FS;series.append((name+' / seam +/-20ms (L+R mean)',join.mean(axis=1),zoom))
 height=100+len(series)*245+58;im=Image.new('RGB',(1300,height),'#f0ede3');d=ImageDraw.Draw(im)
 d.text((30,18),'SOUND-2  /  '+name,font=F22,fill='#142c34');d.text((30,51),'Waveform (linear full scale)                                   Spectrogram (80 Hz-16 kHz, -100 to -15 dBFS)',font=F17,fill='#40555b')
 for k,(label,y,m) in enumerate(series):
  at=92+k*245;d.text((30,at),f'{label}  |  {m["duration_seconds"]:.3f}s  |  {m["integrated_lufs"]:.1f} LUFS  |  peak {m["sample_peak_dbfs"]:.1f}dBFS / {m["true_peak_4x_dbtp"]:.1f}dBTP',font=F17,fill='#142c34')
  plot_panel(im,y,(30,at+30,590,175));plot_panel(im,y,(655,at+30,615,175),True)
 note='Loop seam zoom40ms; displayed levels belong to parent30s loop. Live join/no gap.' if loop else 'PCM16 decode; zero endpoints. Short files use400ms zero-padded LUFS; padding recorded.'
 d.text((30,height-36),note,font=F14,fill='#40555b');p=O/f'review/SOUND2-{name}.png';im.save(p)
 return {'file':p.relative_to(O).as_posix(),'sha256':sha(p),'size':list(im.size),'audio_files':[row['file']]}

def run():
 rows=[];sheets=[];spread={}
 for n in RECIPES:
  family=[]
  for v in range(3):
   x,m=measure(O/f'SFX/{n}_{v}.wav');assert abs(m['duration_seconds']-DURATIONS[n][v])<=1/FS
   rows.append(m);family.append(m);sheets.append(sheet(x,m))
  assert len({m['sha256'] for m in family})==3
  spread[n]=max(m['integrated_lufs'] for m in family)-min(m['integrated_lufs'] for m in family);assert spread[n]<2
  print(n,'analyzed',flush=True)
 for n in AMBIENCE_RECIPES:
  x,m=measure(O/f'Ambience/{n}.wav');m['stereo_correlation']=float(np.corrcoef(x.T)[0,1]);assert abs(m['stereo_correlation'])<.98
  rows.append(m);sheets.append(sheet(x,m));print(n,'analyzed',flush=True)
 stress={}
 for hz in [8,12,16]:
  y=np.zeros(2*FS)
  for k,at in enumerate(np.arange(0,1.5,1/hz)):
   x,_,_=decode(O/f'SFX/Stitch_{k%3}.wav');i=round(at*FS);length=min(len(x),len(y)-i);y[i:i+length]+=x[:length,0]
  peak=db(np.max(abs(y)));stress[str(hz)+'Hz']={'unity_gain1_sum_peak_dbfs':peak,'gain065_sum_peak_dbfs':peak+db(.65)}
 assert all(v['gain065_sum_peak_dbfs']<-3 for v in stress.values())
 metrics={'task':'SOUND-2','result':'PASS','method':'Unchanged SOUND1 measure() BS1770 K-weighting,400ms/100ms gating,short clips zero-padded to400ms;4xpolyphase estimated true peak. Not listening or certified hardware meter.','files':rows,'family_lufs_spread':spread,'stitch_overlap':stress,'sheets':sheets}
 (O/'metrics-sound2.json').write_text(json.dumps(metrics,indent=2)+'\n');print('SOUND2 ANALYSIS PASS',len(rows),'files',len(sheets),'sheets',flush=True)
if __name__=='__main__':run()
