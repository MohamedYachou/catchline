from pathlib import Path
from PIL import Image,ImageFont,ImageChops
import json,hashlib,sys
R=Path('Art/Source/Restaurant');done=[]
for n in map(int,sys.argv[1:]):
 P=R/f'exact/s{n}';M=json.loads((P/'manifest.json').read_text(encoding='utf-8'));L=json.loads((P/'layout.json').read_text(encoding='utf-8'));T=json.loads((P/'text-styles.json').read_text(encoding='utf-8'))['styles'];assert len({m['name'] for m in M})==len(M)
 for m in M:
  f=P/m['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==m['sha256'];im=Image.open(f);assert im.mode=='RGBA' and im.getchannel('A').getbbox()==(0,0,*im.size)
  assert len(list((R/'exact').glob('s*/'+m['file'])))==1
  for p in L['placements']:
   if p['name']==m['name']:assert im.width>=p['rect'][2]*3 and im.height>=p['rect'][3]*3
 for t in T:
  x,y,w,h=t['rect'];assert x>=0 and y>=0 and x+w<=844 and y+h<=390
  font=ImageFont.truetype('Assets/Resources/Fonts/Fredoka-Bold.ttf',t['size']);b=font.getbbox(t['text'],stroke_width=t['stroke_width']);assert b[2]-b[0]<=w and b[3]-b[1]<=h,t['id']
 c=Image.open(R/'concepts'/json.loads((P/'spec.json').read_text(encoding='utf-8'))['concept']).convert('RGBA');re=Image.open(P/'reconstructed-3x.png').convert('RGBA').resize((844,390),Image.Resampling.LANCZOS);assert c.size==(844,390);assert ImageChops.difference(c,re).getbbox() is None
 done.append(dict(screen=n,sprites=len(M),placements=len(L['placements']),texts=len(T),pass_=True,conceptMatchesReconstruction=True,nativeAcceptance=False))
 if n==10:
  names={m['name'] for m in M};assert all('v2-s10-order-'+s in names for s in 'grilled-fish pan-fish fish-chips soup platter crab calamari coffee tea lemonade beer fries bread'.split())
  for state in ['calm','warning','angry']:
   a=Image.open(P/f'v2-s10-patience-{state}.png').getchannel('A');assert a.getpixel((a.width//2,a.height//2))==0
 (P/'independent-audit.json').write_text(json.dumps(done[-1],indent=2),encoding='utf-8')
print(json.dumps(done))
