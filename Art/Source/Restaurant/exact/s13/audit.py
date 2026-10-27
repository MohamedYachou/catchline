from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops
import json,hashlib
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if (p/'Assets').exists());A=R/'Art/Source/Restaurant'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
ms=json.loads((P/'manifest.json').read_text());ps=json.loads((P/'layout.json').read_text())['placements'];ts=json.loads((P/'text-styles.json').read_text())['styles']
assert len(ms)==len({m['name'] for m in ms})==9
assert len(ps)==len({(p['name'],p['use']) for p in ps})==26
assert len(ts)==len({t['id'] for t in ts})==9
by={m['name']:m for m in ms}
for m in ms:
 a=Image.open(P/m['file']);assert a.mode=='RGBA' and a.size==tuple(m['size']) and all(n==l*3 for n,l in zip(a.size,m['logicalSize']))
 assert a.getchannel('A').getbbox()==(0,0,*a.size) and sha(P/m['file'])==m['sha256']
 assert sha(R/m['source'])==m['sourceSha256']
 assert len(list(A.glob('**/'+m['file'])))==1,'name collision'
 if m['borders']:
  l,b,r,t=m['borders'];assert l+r<a.width and t+b<a.height
for p in ps:
 x,y,w,h=p['rect'];assert x>=0 and y>=0 and x+w<=844 and y+h<=390
 assert by[p['name']]['size']==[w*3,h*3]
font=R/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
for t in ts:
 x,y,w,h=t['rect'];assert x>=0 and y>=0 and x+w<=844 and y+h<=390
 b=ImageDraw.Draw(Image.new('RGB',(1,1))).multiline_textbbox((0,0),t['text'],font=ImageFont.truetype(str(font),t['size']*3),spacing=t['spacing']*3,stroke_width=t['stroke_width']*3)
 assert b[2]-b[0]<=w*3 and b[3]-b[1]<=h*3
concept=Image.open(A/'concepts/ui-13-first-night.png').convert('RGBA');recon=Image.open(P/'reconstructed-3x.png').resize((844,390),Image.Resampling.LANCZOS)
assert ImageChops.difference(concept,recon).getbbox() is None
# Resize the EXPORTED slice cells at narrow and wide sizes, preserving actual corners/tail.
sliced=[m for m in ms if m['borders']];proof=Image.new('RGBA',(1688,len(sliced)*230),'#E6E5DA');d=ImageDraw.Draw(proof);f=ImageFont.truetype(str(font),20)
for row,m in enumerate(sliced):
 a=Image.open(P/m['file']);l,b,r,t=m['borders'];sx=[0,l,a.width-r,a.width];sy=[0,t,a.height-b,a.height]
 d.text((8,row*230+4),m['name'],font=f,fill='#10263D')
 for col,w in enumerate([600,960]):
  h=165;out=Image.new('RGBA',(w,h));dx=[0,l,w-r,w];dy=[0,t,h-b,h]
  for yi in range(3):
   for xi in range(3):out.alpha_composite(a.crop((sx[xi],sy[yi],sx[xi+1],sy[yi+1])).resize((dx[xi+1]-dx[xi],dy[yi+1]-dy[yi]),Image.Resampling.LANCZOS),(dx[xi],dy[yi]))
  proof.alpha_composite(out,(8 if col==0 else 680,row*230+35))
proof.convert('RGB').save(P/'slice-proof.jpg',quality=94)
dump(P/'audit.json',dict(passChecks=True,sprites=len(ms),placements=len(ps),texts=len(ts),slices=len(sliced),tightRGBA=True,export3x=True,uniqueNames=True,textFit=True,sourceExportHashes=True,conceptEqualsReconstruction=True,visualReview='PENDING final actual opens',nativeAcceptance=False))
print('PASS9sprites/26placements/9texts/4slices tightRGBA3x unique,text fit,hashes,concept equality')
