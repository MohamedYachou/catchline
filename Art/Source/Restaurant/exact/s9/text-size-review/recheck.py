from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,re,hashlib
P=Path(__file__).resolve().parent;S=P.parent;ROOT=next(p for p in S.parents if (p/'Assets').exists())
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
F=ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
def run():
 j=load(S/'text-styles.json');before=json.loads(json.dumps(j));rows=[]
 for t in j['styles']:
  if re.match(r'^[a-z]+-(name|job|rank-[1-3]|task-[1-3])$',t['id']):
   t['size']=18 if t['id'].endswith('-name') else (13 if '-rank-' in t['id'] else 14)
   rows.append(t)
 # Geometry and every unrelated field must be identical.
 changes=[]
 for a,b in zip(before['styles'],j['styles']):
  diff=[k for k in set(a)|set(b) if a.get(k)!=b.get(k)]
  assert not diff or diff==['size'],(a['id'],diff)
  if diff:changes.append(dict(id=a['id'],oldSize=a['size'],size=b['size'],rect=b['rect'],otherFieldsSha256=hashlib.sha256(json.dumps({k:v for k,v in b.items() if k!='size'},sort_keys=True).encode()).hexdigest()))
 # Reconstruct from accepted blank pieces to avoid any painted-letter double exposure.
 im=Image.new('RGBA',(2532,1170));manifest=load(S/'manifest.json');m={e['name']:e for e in manifest}
 for pl in sorted(load(S/'layout.json')['placements'],key=lambda v:v['z']):
  x,y,w,h=pl['rect'];a=Image.open(S/m[pl['name']]['file']).convert('RGBA').resize((w*3,h*3),Image.Resampling.LANCZOS);im.alpha_composite(a,(x*3,y*3))
 d=ImageDraw.Draw(im);fits=[]
 for t in j['styles']:
  if t not in rows:continue
  x,y,w,h=t['rect'];f=ImageFont.truetype(str(F),t['size']*3);sw=round(t.get('stroke_width',0)*3);box=d.textbbox((0,0),t['text'],font=f,stroke_width=sw);tw=box[2]-box[0];th=box[3]-box[1]
  fits.append(dict(id=t['id'],width=tw/3,height=th/3,rect=t['rect'],fits=tw<=w*3 and th<=h*3))
  assert tw<=w*3 and th<=h*3,(t['id'],t['text'],tw/3,th/3,w,h)
  px=x*3+(w*3-tw)/2 if t.get('align')=='center' else x*3
  d.text((px-box[0],y*3+(h*3-th)/2-box[1]),t['text'],font=f,fill=t['fill'],stroke_width=sw,stroke_fill=t.get('stroke','#173F57'))
 im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(P/'uniform-row-review.png')
 # Row-only proof intentionally leaves unrelated headings/buttons blank.
 (S/'text-styles.json').write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
 (P/'audit.json').write_text(json.dumps(dict(status='PASS',rows=len(rows),changedSizes=changes,allOtherFieldsPreserved=True,allRectsPreserved=True,unrelatedStylesPreserved=True,roleSizes=dict(name=18,job=14,rank=13,task=14),fits=fits,finalSha256=sha(S/'text-styles.json')),indent=2)+'\n')
 print('S9 PASS',len(rows),'row styles; size fields only; allrects retained; all textfits')
if __name__=='__main__':run()
