"""Art handoff validation and nine-slice inspection, not runtime checks."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,sys,hashlib
P=Path(sys.argv[1]);M=json.loads((P/'manifest.json').read_text());A=json.loads((P/'audit.json').read_text());N=A['screen']
root=Path('Art/Source/Restaurant/exact');names=[m['file'] for m in M]
collisions={n:[str(p) for p in root.glob('s*/'+n) if p.parent!=P] for n in names};collisions={n:v for n,v in collisions.items() if v};assert not collisions,collisions
for m in M:
 p=P/m['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==m['sha256']
 b=m.get('borders')
 if b:assert b[0]+b[2]<m['size'][0] and b[1]+b[3]<m['size'][1]
def sliced(im,b,target):
 l,bt,r,t=b;xs=[0,l,im.width-r,im.width];ys=[0,t,im.height-bt,im.height];dx=[0,l,target[0]-r,target[0]];dy=[0,t,target[1]-bt,target[1]];out=Image.new('RGBA',target)
 for x in range(3):
  for y in range(3):
   patch=im.crop((xs[x],ys[y],xs[x+1],ys[y+1]));w=dx[x+1]-dx[x];h=dy[y+1]-dy[y]
   if w>0 and h>0 and patch.width>0 and patch.height>0:out.alpha_composite(patch.resize((w,h),Image.Resampling.LANCZOS),(dx[x],dy[y]))
 return out
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16);slices=[m for m in M if m.get('borders')]
for start in range(0,len(slices),8):
 page=Image.new('RGB',(1600,1000),'#CBD4D7');d=ImageDraw.Draw(page)
 for i,m in enumerate(slices[start:start+8]):
  x=(i%2)*800;y=(i//2)*250;d.text((x+10,y+8),m['name']+' | 1.35x width slice stress',font=font,fill='#10263D')
  im=Image.open(P/m['file']);b=m['borders'];scale=min(700/(im.width*1.35),180/im.height,1);im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS);b=[round(v*scale) for v in b]
  out=sliced(im,b,(round(im.width*1.35),im.height));page.paste(out,(x+15,y+45),out)
 page.save(P/f'slice-review-{start//8+1}.jpg',quality=94)
A.update(nameCollisions=collisions,hashesRechecked=True,nineSliceBordersValid=True,slicedSprites=len(slices));(P/'audit.json').write_text(json.dumps(A,indent=2)+'\n')
print(json.dumps(dict(screen=N,sprites=len(M),placements=A['placements'],texts=A['textEntries'],slices=len(slices),collisionCount=len(collisions),hashes='PASS')))
