"""Independent ART-6 delivery checks; no image mutation."""
from pathlib import Path
from PIL import Image,ImageFont,ImageDraw,ImageChops
import json,hashlib,importlib.util
P=Path(__file__).resolve().parent;EX=P.parent;ART=EX.parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
folders=[P,EX/'s9/jobs',EX/'badges']
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
exports=[];texts=[];layouts=[];slices=[]
for folder in folders:
 entries=load(folder/'manifest.json');names={e['name']:e for e in entries}
 assert len(names)==len(entries)
 for e in entries:
  p=folder/e['file'];im=Image.open(p)
  assert im.mode=='RGBA',(p,im.mode)
  assert list(im.size)==e['size']==[v*3 for v in e['logicalSize']],p
  assert im.getchannel('A').getbbox()==(0,0,*im.size),p
  assert sha(p)==e['sha256'],p
  if e.get('opaque'):assert im.getchannel('A').getextrema()==(255,255)
  else:assert im.getchannel('A').getextrema()[0]==0,p
  src=ROOT/e['provenance']['source'];assert sha(src)==e['provenance']['sourceSha256'],src
  if e.get('borders'):
   l,b,r,t=e['borders'];assert l+r<im.width and t+b<im.height,p
   slices.append(dict(name=e['name'],borders=e['borders']))
  exports.append(dict(name=e['name'],file=str(p.relative_to(ROOT)),sha256=sha(p),logicalSize=e['logicalSize']))
 seen=set()
 for lay in load(folder/'layout.json')['screens']:
  w,h=lay['canvas'];uses=set()
  for u in lay['placements']:
   assert u['name'] in names,u
   assert u['use'] not in uses,(lay['screen'],u);uses.add(u['use']);seen.add(u['name'])
   x,y,ww,hh=u['rect'];assert min(x,y)>=0 and ww>0 and hh>0 and x+ww<=w and y+hh<=h,u
   assert u['screen']==lay['screen'],u
   if not names[u['name']].get('borders'):assert [ww,hh]==names[u['name']]['logicalSize'],u
  layouts.append(dict(screen=lay['screen'],placements=len(lay['placements'])))
 assert seen==set(names),(folder,seen,set(names))
 ids=set()
 for t in load(folder/'text-styles.json')['styles']:
  assert (t['screen'],t['id']) not in ids;ids.add((t['screen'],t['id']))
  lay=next(l for l in load(folder/'layout.json')['screens'] if l['screen']==t['screen'])
  x,y,w,h=t['rect'];assert x>=0 and y>=0 and x+w<=lay['canvas'][0] and y+h<=lay['canvas'][1],t
  font=ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'),t['size']*3)
  box=font.getbbox(t['text']);assert box[2]-box[0]<=w*3 and box[3]-box[1]<=h*3,t
  texts.append(dict(id=t['id'],screen=t['screen'],width=(box[2]-box[0])/3,height=(box[3]-box[1])/3,rect=t['rect']))
assert len(exports)==14 and len({e['name'] for e in exports})==14
# Public sprite names must not collide with any other delivered root cut.
for e in exports:
 hits=[p for p in EX.rglob(e['name']+'.png') if 'provenance' not in p.parts]
 assert len(hits)==1,(e['name'],hits)
baseline=load(P/'preservation-baseline.json')
for rel,digest in baseline.items():assert sha(ROOT/rel)==digest,rel
reviews=load(P/'visual-review.json')
for rel,digest in reviews['opened'].items():assert sha(ROOT/rel)==digest,rel
assert len(reviews['opened'])==15
# Reconstruct all four transition concepts exclusively from delivered layers + live labels.
spec=importlib.util.spec_from_file_location('kit',EX/'s2-call/package.py');k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
entries={e['name']:e for e in load(P/'manifest.json')}
for lay in load(P/'layout.json')['screens']:
 im=Image.new('RGBA',tuple(v*3 for v in lay['canvas']))
 for u in sorted(lay['placements'],key=lambda u:u['z']):
  e=entries[u['name']];spr=Image.open(P/e['file']).convert('RGBA');x,y,w,h=u['rect']
  if e.get('borders'):spr=k.sliced(spr,(w*3,h*3),e['borders'])
  im.alpha_composite(spr,(x*3,y*3))
 for t in load(P/'text-styles.json')['styles']:
  if t['screen']==lay['screen']:k.drawtext(im,t)
 expected=Image.open(P/(lay['screen']+'-reconstructed-3x.png')).convert('RGBA')
 assert ImageChops.difference(im.convert('RGB'),expected.convert('RGB')).getbbox() is None,lay['screen']
 concept=Image.open(ART/'concepts'/('ui-transition-'+lay['screen']+'.png')).convert('RGB')
 reduced=im.resize(tuple(lay['canvas']),Image.Resampling.LANCZOS).convert('RGB')
 assert ImageChops.difference(concept,reduced).getbbox() is None,lay['screen']
for folder in folders:
 for rec in load(folder/'provenance/generation-records.json'):assert rec['prompt'] and 'Generated images' in rec['result']
result=dict(status='PASS',exports=exports,preservedAcceptedFiles=len(baseline),liveTextFits=texts,slices=slices,layouts=layouts,openedReviews=15,reconstructedTransitionConcepts=4,limits='Source-art audit only. No Unity/native import, interaction, flow or lead/Mo acceptance. 3x resampling is not native3x painted detail.')
(P/'delivery-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS:',len(exports),'exports;',len(baseline),'accepted files preserved;',len(texts),'text fits;15 opened reviews;4 exact concept reconstructions')
