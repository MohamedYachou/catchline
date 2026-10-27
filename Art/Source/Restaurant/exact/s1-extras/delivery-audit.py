from pathlib import Path
import json,hashlib,re,importlib.util
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;EX=P.parent;ART=EX.parent;ROOT=next(p for p in P.parents if (p/'Assets').exists())
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def check_sprite(folder,e,tight=True):
 f=folder/e['file'];a=Image.open(f);assert a.mode=='RGBA' and list(a.size)==e['size'],f
 assert sha(f)==e['sha256'],f
 assert a.getchannel('A').getextrema()[0]==0,f
 if tight:assert a.getchannel('A').getbbox()==(0,0,*a.size),f
 return {'file':str(f.relative_to(ROOT)),'sha256':sha(f)}
def run():
 # Rerun the separate S15 static/radial/frame audit, without rebuilding art.
 spec=importlib.util.spec_from_file_location('marker_audit',EX/'s15/audit_delivery.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.audit()
 files=[]
 for e in load(EX/'s15/manifest.json'):files.append(check_sprite(EX/'s15',e,'animation' not in e))
 bust=ART/'clothes/busts';records=load(bust/'manifest.json')['records'];assert len(records)==14
 for e in records:
  files.append(check_sprite(bust,e));assert max(e['size'])==768
  if e.get('sourceIdentity'):assert sha(ROOT/e['sourceIdentity'])==e['sourceIdentitySha256']
 assert {e['id'] for e in records}==set('mira noor tess rosa ana lise ines tove kofi sam jo bram olaf yusuf'.split())
 for e in load(P/'manifest.json'):
  files.append(check_sprite(P,e));assert all(s>=3*r for s,r in zip(e['size'],e['rect'][2:]))
  old='v2-placement-highlight.png' if 'placement' in e['name'] else 'v2-btn-rotate.png'
  assert Image.open(EX/'s1-s2'/old).size==tuple(e['size'])
 s6=EX/'s6';r=s6/'arrange-entry';base=load(r/'baseline-manifest.json');now=load(s6/'manifest.json');old={e['name']:e for e in base};current={e['name']:e for e in now}
 for name,e in old.items():assert current[name]==e;assert sha(s6/e['file'])==e['sha256']
 assert set(current)-set(old)=={'v2-s6-btn-arrange','v2-s6-arrange-chair'}
 for e in load(r/'manifest.json'):files.append(check_sprite(s6,e))
 assert sha(s6/'v2-s6-btn-arrange.png')==sha(s6/'v2-s6-tab-idle.png')
 assert len(files)==35 and len({Path(e['file']).name for e in files})==35
 # New names are unique across public exact sprite folders; provenance copies excluded.
 for f in files:
  path=ROOT/f['file']
  if path.parent==bust:continue
  assert len(list(EX.glob('s*/'+path.name)))==1,path
 # All measured added labels fit their fixed rectangles including strokes.
 font=ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf';d=ImageDraw.Draw(Image.new('RGB',(1,1)))
 for folder in [P,r]:
  for t in load(folder/'text-styles.json')['styles']:
   b=d.textbbox((0,0),t['text'],font=ImageFont.truetype(str(font),t['size']*3),stroke_width=t.get('stroke_width',0)*3)
   assert b[2]-b[0]<=t['rect'][2]*3 and b[3]-b[1]<=t['rect'][3]*3,t['id']
 s9=EX/'s9';a=load(s9/'text-size-review/audit.json');j=load(s9/'text-styles.json');assert sha(s9/'text-styles.json')==a['finalSha256']
 rows=[t for t in j['styles'] if re.match(r'^[a-z]+-(name|job|rank-[1-3]|task-[1-3])$',t['id'])];assert len(rows)==48
 for t in rows:assert t['size']==(18 if t['id'].endswith('-name') else 13 if '-rank-' in t['id'] else 14)
 for c in a['changedSizes']:
  t=next(t for t in rows if t['id']==c['id']);assert t['rect']==c['rect'];assert hashlib.sha256(json.dumps({k:v for k,v in t.items() if k!='size'},sort_keys=True).encode()).hexdigest()==c['otherFieldsSha256']
 # Actual-open ledgers must still match the delivered proofs.
 proof_count=0
 for folder in [EX/'s15',bust,s9/'text-size-review',P,r]:
  v=load(folder/'visual-review.json');assert v['actuallyOpened']
  for f,h in (v['files'] if 'files' in v else {v['file']:v['sha256']}).items():
   path=ROOT/f if (ROOT/f).exists() else folder/f
   assert sha(path)==h,f;proof_count+=1
 lay=load(P/'layout.json');assert sha(ART/'concepts/ui-1-arrange.png')==lay['backgroundSha256']
 result=dict(status='PASS',exports=35,markers=16,busts=14,arrangeExtras=5,s9UniformRows=48,s6AcceptedEntriesPreserved=len(base),actualOpenProofs=proof_count,uniqueNames=True,files=files,nativeRuntimeVerified=False)
 (P/'delivery-audit.json').write_text(json.dumps(result,indent=2)+'\n');print('FINAL PASS:35exports/48uniformrows/acceptedS6preserved/actualopenhashes. Native runtime pending.')
if __name__=='__main__':run()
