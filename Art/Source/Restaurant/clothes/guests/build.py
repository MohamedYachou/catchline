"""Mechanical requested crop/3x export/contact. Paintings created by built-in ImageGen."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib
P=Path(__file__).resolve().parent
R=next(p for p in P.parents if (p/'Assets').exists())
names='ada ben cora dan edda finn gus hazel ivo jonas kai lena'.split()
models=R/'Art/Models/Restaurant/Guests'
contracts={}
for fn in ['build-metrics-v2.json','build-metrics-extra.json']:
 for g in json.loads((models/fn).read_text())['guests']:
  contracts[g['name'].split('_')[1].lower()]={k:v for k,v in g.items() if k in ['name','role','hairstyle','skin_srgb','hair_srgb','shirt_srgb']}
font=ImageFont.truetype(str(R/'Assets/Resources/Fonts/Fredoka-Bold.ttf'),24)
small=ImageFont.truetype(str(R/'Assets/Resources/Fonts/Fredoka-Bold.ttf'),18)
contact=Image.new('RGB',(1440,1140),'#F4EFE3');d=ImageDraw.Draw(contact)
manifest=[]
for i,n in enumerate(names):
 src=P/'provenance'/f'{n}.png'
 if not src.exists():continue
 im=Image.open(src).convert('RGBA')
 im.putalpha(im.getchannel('A').point(lambda a:a if a>=24 else 0))
 box=im.getchannel('A').getbbox();assert box
 cut=im.crop(box)
 # Keep generated alpha; trim only empty pixels. 192px supports a 64px review circle.
 cut=cut.resize((192,192),Image.Resampling.LANCZOS)
 cut.putalpha(cut.getchannel('A').point(lambda a:a if a>=24 else 0))
 for _ in range(4):
  b=cut.getchannel('A').getbbox()
  if b==(0,0,*cut.size):break
  cut=cut.crop(b).resize((192,192),Image.Resampling.LANCZOS)
  cut.putalpha(cut.getchannel('A').point(lambda a:a if a>=24 else 0))
 dest=P/f'v2-guest-{n}.png';cut.save(dest,optimize=True)
 assert cut.getchannel('A').getbbox()==(0,0,192,192)
 assert all(cut.getpixel(p)[3]==0 for p in [(0,0),(191,0),(0,191),(191,191)])
 ref=models/('renders-v2' if i<6 else 'renders-extra')/(f'Guest_{n.title()}'+('_v2' if i<6 else '')+'-idle.png')
 x=i%4*360;y=i//4*380
 d.text((x+18,y+6),n.title(),font=font,fill='#173F57')
 a=ImageOps.contain(Image.open(ref).convert('RGBA'),(125,260));contact.paste(a,(x+8,y+55),a)
 contact.paste(cut,(x+148,y+45),cut)
 mini=cut.resize((48,48),Image.Resampling.LANCZOS);contact.paste(mini,(x+190,y+255),mini)
 d.text((x+138,y+320),'64px UI / 192px source',font=small,fill='#173F57')
 manifest.append(dict(name=n,file=dest.name,size=[192,192],intendedMaxUI=[64,64],crop=box,reference=str(ref.relative_to(R)).replace('\\','/'),contract=contracts[n],sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),sourceSha256=hashlib.sha256(src.read_bytes()).hexdigest()))
contact.save(P/'contact-sheet.jpg',quality=95)
(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(P/'audit.json').write_text(json.dumps(dict(complete=len(manifest)==12,count=len(manifest),expected=names,allTightRGBA3x=True,allCornersTransparent=True,method='ImageGen; requested mechanical alpha crop/Lanczos192 export only; generated alpha preserved',visualReview='PENDING actual opens'),indent=2)+'\n')
print(f'Exported {len(manifest)}/12 portraits')

