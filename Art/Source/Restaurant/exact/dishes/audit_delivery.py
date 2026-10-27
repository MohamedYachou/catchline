"""Independent ART-4 source-art delivery audit."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
P=Path(__file__).resolve().parent;EX=P.parent;ROOT=EX.parents[3]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
base=load(P/'preservation-baseline.json');keep=[]
for rel,h in base.items():
 p=ROOT/rel
 if rel.replace('\\','/').endswith('exact/s15/manifest.json'):
  before=load(EX/'s15/moods/baseline-manifest.json');now=load(p)
  assert now[:len(before)]==before
  assert sha(EX/'s15/moods/baseline-manifest.json')==h
 else:assert sha(p)==h,rel
 keep.append(rel)
allnames={}
for folder in EX.iterdir():
 if folder.is_dir():
  for p in folder.glob('*.png'):allnames.setdefault(p.name,[]).append(str(p))
records=[]
for folder in [P,EX/'s15/moods',EX/'s5']:
 entries=load(folder/'manifest.json');layout=load(folder/'layout.json')
 places=layout['placements'];styles=load(folder/'text-styles.json')['styles']
 for e in entries:
  path=(folder/e['file']).resolve();im=Image.open(path)
  assert im.mode=='RGBA';assert list(im.size)==e['size']
  assert e['size']==[v*3 for v in e['logicalSize']]
  assert im.getchannel('A').getbbox()==(0,0,*im.size)
  assert sha(path)==e['sha256'];assert len(allnames[path.name])==1,path.name
  assert sum(p['name']==e['name'] for p in places)==1
  pp=next(p for p in places if p['name']==e['name']);assert pp.get('use')
  assert pp['rect'][2:]==e['logicalSize']
  x,y,w,h=pp['rect'];cw,ch=layout['canvas'];assert 0<=x<x+w<=cw and 0<=y<y+h<=ch
  source=ROOT/e['provenance']['source'];assert sha(source)==e['provenance']['sourceSha256']
  records.append(dict(name=e['name'],file=str(path.relative_to(ROOT)),sha256=sha(path),size=list(im.size)))
 for t in styles:
  font=ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'),t['size']*3)
  b=ImageDraw.Draw(Image.new('RGB',(1,1))).textbbox((0,0),t['text'],font=font)
  assert b[2]-b[0]<=t['rect'][2]*3 and b[3]-b[1]<=t['rect'][3]*3
 steam=EX/'s15/v2-s15-steam-strip.png'
 assert sha(steam)==base[str(steam.relative_to(ROOT))]
proof=load(P/'visual-review.json')
for item in proof:
 assert sha(ROOT/item['file'])==item['sha256'] and item['actuallyOpened'] is True
assert len(records)==14
result=dict(status='PASS',exports=records,acceptedFilesPreserved=len(keep),openedReviews=len(proof),checks=['tight RGBA3x','unique public names','manifest/source hashes','layout coverage and bounds','live text fit','accepted art and steam preserved','opened review hashes current'],limits='Source-art checks only; no Unity import/native interaction or lead/Mo acceptance.')
(P/'delivery-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS14 exports;',len(keep),'accepted files preserved;',len(proof),'opened reviews current')
