"""Independent ART-7 export, preservation, live-text and reconstruction audit."""
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw, ImageChops
import json, hashlib, importlib.util
P=Path(__file__).resolve().parent; EX=P.parent; ART=EX.parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
folders=[P,EX/'s3/special',EX/'s2/pause']
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('kit',EX/'s2-call/package.py')
k=importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
exports=[]; texts=[]; layouts=[]; reconstructed=[]
for folder in folders:
 entries=load(folder/'manifest.json'); names={e['name']:e for e in entries}
 assert len(names)==len(entries)
 for e in entries:
  path=folder/e['file']; im=Image.open(path)
  assert im.mode=='RGBA' and list(im.size)==e['size']==[v*3 for v in e['logicalSize']],path
  assert im.getchannel('A').getbbox()==(0,0,*im.size),path
  assert im.getchannel('A').getextrema()[0]==0,path
  assert sha(path)==e['sha256'],path
  src=ROOT/e['provenance']['source']; assert sha(src)==e['provenance']['sourceSha256'],src
  if e['provenance'].get('acceptedExactCopy'): assert sha(ROOT/e['provenance']['acceptedExactCopy'])==sha(path)
  if e.get('borders'):
   l,b,r,t=e['borders']; assert l+r<im.width and b+t<im.height,path
  exports.append(dict(name=e['name'],file=str(path.relative_to(ROOT)),sha256=sha(path),logicalSize=e['logicalSize']))
 seen=set(); sheetstyles=load(folder/'text-styles.json')['styles']; ids=set()
 for lay in load(folder/'layout.json')['screens']:
  w,h=lay['canvas']; uses=set(); bg=ROOT/lay['background']
  assert sha(bg)==lay['backgroundSha256'],bg
  im=Image.open(bg).convert('RGBA').resize((w*3,h*3),Image.Resampling.NEAREST)
  assert Image.open(bg).size==(w,h),bg
  if lay.get('dim'):im=Image.alpha_composite(im,Image.new('RGBA',im.size,(9,31,48,lay['dim'])))
  mask=Image.new('L',im.size,0); md=ImageDraw.Draw(mask)
  for u in sorted(lay['placements'],key=lambda u:u['z']):
   assert u['screen']==lay['screen'] and u['use'] not in uses,u
   uses.add(u['use']); x,y,ww,hh=u['rect']
   assert min(x,y)>=0 and min(ww,hh)>0 and x+ww<=w and y+hh<=h,u
   if u.get('external'):
    src=ROOT/u['external']; assert src.exists(),src
    spr=Image.open(src).convert('RGBA'); borders=u.get('externalBorders')
   else:
    assert u['name'] in names,u
    e=names[u['name']]; seen.add(e['name']); spr=Image.open(folder/e['file']).convert('RGBA'); borders=e.get('borders')
    for alt in u.get('alternatives',[]):assert alt in names;seen.add(alt)
    if e.get('variant'):
     assert abs(ww/hh-e['logicalSize'][0]/e['logicalSize'][1])<0.015,u
   spr=k.sliced(spr,(ww*3,hh*3),borders) if borders else spr.resize((ww*3,hh*3),Image.Resampling.LANCZOS)
   im.alpha_composite(spr,(x*3,y*3));md.rectangle((x*3,y*3,(x+ww)*3-1,(y+hh)*3-1),fill=255)
  for t in sheetstyles:
   if t['screen']!=lay['screen']:continue
   assert (t['screen'],t['id']) not in ids;ids.add((t['screen'],t['id']))
   x,y,ww,hh=t['rect']; assert min(x,y)>=0 and x+ww<=w and y+hh<=h,t
   font=ImageFont.truetype(str(k.FONT),t['size']*3);d=ImageDraw.Draw(im)
   lines=k.lines(t['text'],font,ww*3,d) if t.get('wrap') else [t['text']]
   metrics=[d.textbbox((0,0),line,font=font) for line in lines]
   tw=max(b[2]-b[0] for b in metrics); th=metrics[0][3]-metrics[0][1]+(len(lines)-1)*t['lineHeight']*3
   assert tw<=ww*3 and th<=hh*3,t
   k.drawtext(im,t);md.rectangle((x*3,y*3,(x+ww)*3-1,(y+hh)*3-1),fill=255)
   texts.append(dict(id=t['id'],screen=t['screen'],lines=lines,width=tw/3,height=th/3,rect=t['rect']))
  for key,r in lay.get('hitRects',{}).items():assert r[2]>=44 and r[3]>=44,(key,r)
  reference=Image.open(folder/(lay['screen']+'-reconstructed-3x.png')).convert('RGB')
  assert ImageChops.difference(im.convert('RGB'),reference).getbbox() is None,(folder,lay['screen'],'3x reconstruction')
  concept=Image.open(ART/'concepts'/lay['concept']).convert('RGB')
  assert ImageChops.difference(im.resize((w,h),Image.Resampling.LANCZOS).convert('RGB'),concept).getbbox() is None,lay['concept']
  if not lay.get('dim'):
   original=Image.open(bg).convert('RGB').resize(im.size,Image.Resampling.NEAREST)
   difference=ImageChops.difference(original,im.convert('RGB'))
   difference.paste((0,0,0),(0,0,*im.size),mask)
   assert difference.getbbox() is None,(folder,'outside declared placements/text')
  layouts.append(dict(folder=str(folder.relative_to(EX)),screen=lay['screen'],placements=len(lay['placements'])))
  reconstructed.append(lay['concept'])
 assert seen==set(names),(folder,seen,set(names))
assert len(exports)==13 and len({e['name'] for e in exports})==13
for e in exports:
 hits=[p for p in EX.rglob(e['name']+'.png') if 'provenance' not in p.parts]
 assert len(hits)==1,(e['name'],hits)
baseline=load(P/'preservation-baseline.json')
for rel,digest in baseline.items():assert sha(ROOT/rel)==digest,rel
reviews=load(P/'visual-review.json')['opened']
for rel,digest in reviews.items():assert sha(ROOT/rel)==digest,rel
assert len(reviews)==11
for folder in [P,EX/'s3/special']:
 for rec in load(folder/'provenance/generation-records.json'):assert rec['prompt'] and 'Generated images' in rec['hint']
result=dict(status='PASS',exports=exports,preservedAcceptedFiles=len(baseline),liveTextFits=texts,layouts=layouts,reconstructedConcepts=reconstructed,openedReviews=len(reviews),limits='Source art only. Native import, state binding, focus/exit flow and lead/Mo acceptance remain unverified. 3x resampling is not native 3x painted detail.')
dump(P/'delivery-audit.json',result)
print(f'PASS: {len(exports)} exports; {len(baseline)} accepted files preserved; {len(texts)} live labels fit; {len(reviews)} opened reviews; {len(reconstructed)} exact reconstructions')
