"""Independent ART-5 asset/metadata/preservation audit; no native acceptance claim."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent;ROOT=next(p for p in P.parents if (p/'Assets').exists());EX=ROOT/'Art/Source/Restaurant/exact'
folders=[P,EX/'s7/states',EX/'s11/celebrate']
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
baseline=load(P/'preservation-baseline.json')
for rel,h in baseline.items():assert sha(ROOT/rel)==h,('Accepted asset changed',rel)
files={}
for f in EX.rglob('v2-*.png'):files.setdefault(f.name,[]).append(str(f))
records=[];frames=[];fits=[]
for folder in folders:
 entries=load(folder/'manifest.json');layout=load(folder/'layout.json');styles=load(folder/'text-styles.json')['styles']
 for e in entries:
  p=folder/e['file'];im=Image.open(p)
  assert im.mode=='RGBA' and list(im.size)==e['size']
  assert list(im.size)==[v*3 for v in e['logicalSize']]
  assert im.getchannel('A').getbbox()==(0,0,*im.size),e['name']
  assert sha(p)==e['sha256'];assert len(files[p.name])==1,(p.name,files[p.name])
  uses=[u for u in layout['placements'] if u['name']==e['name']];assert uses
  for u in uses:
   x,y,w,h=u['rect'];cw,ch=layout['canvas'];assert 0<=x<x+w<=cw and 0<=y<y+h<=ch,(e['name'],u)
   assert u['use']
  prov=e['provenance'];sources=prov.get('sources',[dict(source=prov.get('source'),sourceSha256=prov.get('sourceSha256'))])
  for source in sources:assert sha(ROOT/source['source'])==source['sourceSha256']
  if e.get('animation'):
   a=e['animation'];assert a['frameCount']==(4 if 'purchase' in e['name'] else 6)
   assert len(a['frames'])==a['frameCount'] and sum(f['durationMs'] for f in a['frames'])==a['totalDurationMs']
   hashes=[];lastx=0
   for f in a['frames']:
    x,y,w,h=f['rect'];assert x==lastx and y==0 and x+w<=im.width and y+h<=im.height
    assert [w,h]==[v*3 for v in f['logicalSize']]
    q=im.crop((x,y,x+w,y+h));assert q.getchannel('A').getbbox()==(0,0,w,h)
    assert all(0<=n<=1 for n in f['pivot']);assert f['durationMs']>0
    hashes.append(hashlib.sha256(q.tobytes()).hexdigest());lastx=x+w
   assert lastx==im.width and len(set(hashes))==a['frameCount']
   frames.append(dict(name=e['name'],frames=a['frameCount'],durationMs=a['totalDurationMs'],uniqueFrameHashes=hashes))
  records.append(dict(file=str(p.relative_to(ROOT)),name=e['name'],size=list(im.size),sha256=sha(p)))
 for u in layout['placements']:
  if u.get('external'):assert (folder/u['file']).exists(),u
 ids=set()
 for t in styles:
  assert t['id'] not in ids;ids.add(t['id']);assert t.get('rect') and t.get('screen')
  f=ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'),t['size']*3)
  bb=ImageDraw.Draw(Image.new('RGB',(1,1))).textbbox((0,0),t['text'],font=f)
  assert bb[2]-bb[0]<=t['rect'][2]*3 and bb[3]-bb[1]<=t['rect'][3]*3,t['id']
  fits.append(t['id'])
 for e in load(folder/'slices.json')['sprites']:
  meta=next(m for m in entries if m['name']==e['name']);l,b,r,t=e['borders'];w,h=meta['size'];assert l+r<w and t+b<h
proof=load(P/'visual-review.json')
for item in proof:assert item['actuallyOpened'] is True and sha(ROOT/item['file'])==item['sha256']
assert len(records)==11 and len(frames)==2
result=dict(status='PASS',exports=records,acceptedFilesPreserved=len(baseline),animations=frames,liveTextFits=len(fits),actuallyOpenedReviews=len(proof),checks=['RGBA3x and tight alpha','unique public names','source/export hashes','explicit measured placements','all live labels fit','4/6 distinct tight frames with stable pivot metadata','slices fit source','accepted assets unchanged','actual-open review hashes current'],limits='Source-art audit only; native import, timing/anchors, interaction and lead/Mo acceptance remain unverified.')
(P/'delivery-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS',len(records),'exports;',len(baseline),'accepted files preserved;',len(frames),'animations;',len(fits),'live labels;',len(proof),'opened reviews')
