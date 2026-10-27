"""Independent output decode and technical checks; documents no listening claim."""
from pathlib import Path
import sys,json,hashlib,html
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];O=R/'Art/Audio/Real';sys.path.insert(0,str(R/'Art/Source/Audio'))
import analyze
analyze.O=O
from PIL import Image,ImageDraw
from collections import defaultdict
E=json.loads((O/'crewfx-edits.json').read_text());groups=defaultdict(list);metrics=[];sheets=[]
for e in E['files']:
 x,m=analyze.measure(O/e['file']);assert m['sha256']==e['sha256'];m['target_lufs']=e['target_lufs'];assert abs(m['integrated_lufs']-m['target_lufs'])<1,(e['file'],m)
 if m['family']=='CardFlip':assert m['duration_seconds']<.15,m
 metrics.append(m);groups[m['family']].append((x[:,0],m))
for name,rows in groups.items():
 assert len({m['sha256'] for x,m in rows})==len(rows)
 assert max(m['integrated_lufs'] for x,m in rows)-min(m['integrated_lufs'] for x,m in rows)<2
 im=Image.new('RGB',(1300,100+245*len(rows)),'#f0ede3');d=ImageDraw.Draw(im)
 d.text((25,15),'CREW-FX / REAL RECORDINGS / '+name,font=analyze.F22,fill='#142c34')
 d.text((25,50),'Full-scale waveform | log spectrum80Hz–16kHz; technical evidence only, listening pending.',font=analyze.F17,fill='#40555b')
 for k,(x,m) in enumerate(rows):
  y=85+k*245;d.text((25,y),f"{Path(m['file']).stem} | {m['duration_seconds']:.3f}s | {m['integrated_lufs']:.2f}LUFS | {m['true_peak_4x_dbtp']:.2f}dBTP",font=analyze.F17,fill='#142c34')
  analyze.plot_panel(im,x,(25,y+30,590,175));analyze.plot_panel(im,x,(655,y+30,615,175),True)
 p=O/'review'/('crewfx-'+name+'.png');im.save(p);sheets.append({'file':str(p.relative_to(O)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 print(name,'PASS',[(round(m['duration_seconds'],3),round(m['integrated_lufs'],2)) for x,m in rows],flush=True)
(O/'crewfx-metrics.json').write_text(json.dumps({'result':'PASS technical only; listening/native mix pending','method':'Independent PCM16 decode, BS1770 gated loudness (400ms short padding),4x polyphase truepeak estimate; peak<=-3dBFS, DC<.0007, zero endpoints, target within1LU, family spread<2LU.','files':metrics,'sheets':sheets},indent=2)+'\n')
parts=['<!doctype html><meta charset="utf-8"><title>Crew FX recorded cues</title><h1>CREW-FX recording candidates</h1><p>Listen for source background, clicks, horn scale, tonal fit and repetition. No auditory acceptance has been recorded. Puffin excerpts CC BY-SA4; see LICENSES.md.</p>']
for e in E['files']:
 parts.append(f'<p><b>{html.escape(e["file"])}</b> — {html.escape(e["description"])}<br><audio controls preload="none" src="../{html.escape(e["file"])}"></audio></p>')
(O/'review/crewfx-listening.html').write_text('\n'.join(parts)+'\n')
