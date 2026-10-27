"""Independent ART-9 source QA; does not launch Unity or write Assets."""
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFont
import json,hashlib,importlib.util
P=Path(__file__).resolve().parent;EX=P.parent;ART=EX.parent
ROOT=next(p for p in P.parents if (p/'Assets').exists());G=ART/'clothes/guests';X=G/'extra'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('kit',EX/'s2-call/package.py');k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
baseline=load(P/'preservation-baseline.json')
for rel,digest in baseline.items():assert sha(ROOT/rel)==digest,('accepted source changed',rel)
old=load(P/'guest-manifest-before.json');now=load(G/'manifest.json');new=load(X/'manifest.json')
assert len(old)==12 and now[:12]==old and now[12:]==new and len(now)==20
assert {e['name'] for e in new}==set('09 10 11 12 13 14 15 16'.split())
exports=[]
es=load(P/'manifest.json');names={e['name']:e for e in es};assert len(names)==len(es)==13
for e in es:
 path=P/e['file'];im=Image.open(path)
 assert im.mode=='RGBA' and list(im.size)==e['size']==[v*3 for v in e['logicalSize']],path
 assert im.getchannel('A').getbbox()==(0,0,*im.size),path
 assert im.getchannel('A').getextrema()[0]==(255 if e.get('opaque') else 0),path
 assert sha(path)==e['sha256'],path
 src=ROOT/e['provenance']['source'];assert sha(src)==e['provenance']['sourceSha256'],src
 if e.get('borders'):
  l,b,r,t=e['borders'];assert l+r<im.width and b+t<im.height,path
 exports.append(dict(name=e['name'],file=str(path.relative_to(ROOT)),size=list(im.size),sha256=sha(path)))
for e in new:
 path=G/e['file'];im=Image.open(path);assert im.mode=='RGBA' and im.size==(192,192)
 assert e['logicalSize']==[64,64] and e['intendedMaxUI']==[64,64]
 a=im.getchannel('A');assert a.getbbox()==(0,0,192,192) and a.getextrema()==(0,255)
 assert all(a.getpixel(pt)==0 for pt in [(0,0),(191,0),(0,191),(191,191)])
 assert sha(path)==e['sha256'] and sha(ROOT/e['source'])==e['sourceSha256']
 assert sha(ROOT/e['reference'])==e['referenceSha256']
 assert len(list(G.glob(e['file'])))==1
 exports.append(dict(name='v2-guest-'+e['name'],file=str(path.relative_to(ROOT)),size=list(im.size),sha256=sha(path)))
assert len(exports)==21 and len({e['name'] for e in exports})==21
for e in exports:
 hits=[p for p in ART.rglob(e['name']+'.png') if 'provenance' not in p.parts]
 assert len(hits)==1,(e['name'],hits)
seen=set();styles=load(P/'text-styles.json')['styles'];texts=[];ids=set()
lay=load(P/'layout.json')['screens'][0];w,h=lay['canvas'];assert [w,h]==[844,390]
bg=ROOT/lay['background'];assert sha(bg)==lay['backgroundSha256']
im=Image.open(bg).convert('RGBA').resize((w*3,h*3),Image.Resampling.NEAREST);uses=set()
for u in sorted(lay['placements'],key=lambda u:u['z']):
 assert u['screen']=='hire' and u['use'] not in uses;uses.add(u['use'])
 x,y,ww,hh=u['rect'];assert min(x,y)>=0 and min(ww,hh)>0 and x+ww<=w and y+hh<=h,u
 if u.get('external'):
  src=ROOT/u['external'];assert sha(src)==u['externalSha256'];a=Image.open(src).convert('RGBA');borders=None
  # External busts/job icons keep exact aspect to rounding precision.
  assert abs(ww/hh-a.width/a.height)<0.07,u
 else:
  assert u['name'] in names;seen.add(u['name']);e=names[u['name']];a=Image.open(P/e['file']).convert('RGBA');borders=e.get('borders')
 a=k.sliced(a,(ww*3,hh*3),borders) if borders else a.resize((ww*3,hh*3),Image.Resampling.LANCZOS)
 im.alpha_composite(a,(x*3,y*3))
assert seen==set(names)
for t in styles:
 assert t['screen']=='hire' and t['id'] not in ids;ids.add(t['id'])
 x,y,ww,hh=t['rect'];assert min(x,y)>=0 and x+ww<=w and y+hh<=h
 assert 'stroke_width' in t and 'shadow' in t and 'font' in t
 font=ImageFont.truetype(str(k.FONT),t['size']*3);d=ImageDraw.Draw(im);b=d.textbbox((0,0),t['text'],font=font)
 assert b[2]-b[0]<=ww*3 and b[3]-b[1]<=hh*3,t
 k.drawtext(im,t);texts.append(dict(id=t['id'],text=t['text'],rect=t['rect'],width=(b[2]-b[0])/3,height=(b[3]-b[1])/3))
assert len(texts)==22
for name,r in lay['hitRects'].items():assert r[2]>=44 and r[3]>=44,(name,r)
assert len(lay['hitRects'])==4
reference=Image.open(P/'hire-reconstructed-3x.png').convert('RGB')
assert ImageChops.difference(im.convert('RGB'),reference).getbbox() is None,'3x reconstruction'
concept=Image.open(ART/'concepts/ui-17-hire.png').convert('RGB')
assert ImageChops.difference(im.resize((w,h),Image.Resampling.LANCZOS).convert('RGB'),concept).getbbox() is None,'1x reconstruction'
data=load(P/'sample-data.json');assert data['illustrative'] and data['notGameplayRules']
busts={e['id']:e for e in load(ART/'clothes/busts/manifest.json')['records']}
for s in data['candidates']:
 assert s['job']==busts[s['id']]['job']
 for ending in ['card','bust-slot','job-tag','rarity','wage-coin','hire','restaurant-bust','job-icon']:assert s['id']+'-'+ending in uses
 for ending in ['name','job','rarity','wage','trait','hire']:assert s['id']+'-'+ending in ids
 # No repeated card use can quietly disappear from the manifest.
 assert len([u for u in lay['placements'] if u['use']==s['id']+'-card'])==1
reviews=load(P/'visual-review.json')['opened'];assert len(reviews)>=5
for rel,digest in reviews.items():assert sha(ROOT/rel)==digest,('opened review stale',rel)
result=dict(status='PASS',exports=exports,preservedAcceptedFiles=len(baseline),preservedGuestManifestEntries=len(old),liveTextFits=texts,placements=len(lay['placements']),reconstructedConcepts=['ui-17-hire.png'],openedReviews=len(reviews),limits='Source art only. Native import/state binding/hiring economy/guest roster/Unity acceptance remain Claude/Mo work. Original painted draft is provenance; final mockup exactly reconstructs from the delivered kit. 3x resampling is not a claim of native 3x painted detail.')
dump(P/'delivery-audit.json',result)
print(f'PASS: {len(exports)} exports; {len(baseline)} accepted files preserved; {len(texts)} live text fits; 12 original guest entries preserved; {len(reviews)} opened reviews; 1 exact reconstruction')
