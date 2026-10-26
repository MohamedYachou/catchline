from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3]
checks={}
for n in [0,1,3,4]:
 src=O/'generated'/f'hull{n}-master.png';im=Image.open(src).convert('RGBA')
 # Crop only nearly transparent margin; retain authored colour and antialiased alpha.
 box=im.getchannel('A').point(lambda x:255 if x>8 else 0).getbbox();im=im.crop(box)
 im.thumbnail((432,312),Image.Resampling.LANCZOS)
 out=Image.new('RGBA',(480,360));out.alpha_composite(im,((480-im.width)//2,(360-im.height)//2))
 dst=O/f'v2-item-hull{n}.png';out.save(dst)
 checks[dst.name]={'size':out.size,'mode':out.mode,'alpha_extrema':out.getchannel('A').getextrema(),'alpha_bounds':out.getbbox(),'master_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'cropped_master_bounds':box}
sheet=Image.new('RGB',(1440,820),'#EDE5D6');d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
entries=[('Accepted skiff',R/'Assets/Art/UI/v2-item-skiff.png'),('Accepted compact fisher',R/'Assets/Art/UI/v2-item-compact-fisher.png'),('New hull0 — refined Rowboat',O/'v2-item-hull0.png'),('New hull1 — refined Skiff',O/'v2-item-hull1.png'),('New hull3 — Prep fisher',O/'v2-item-hull3.png'),('New hull4 — Deep-line fisher',O/'v2-item-hull4.png')]
for i,(label,p) in enumerate(entries):
 im=Image.open(p).convert('RGBA');assert im.size==(480,360),(p,im.size)
 x=(i%3)*480;y=(i//3)*410;d.text((x+16,y+12),label,font=font,fill='#172D3C');sheet.paste(im,(x,y+45),im)
sheet.save(O/'comparison-six-cards.png')
(O/'validation.json').write_text(json.dumps(checks,indent=2));print('CARDS PASS',len(checks))
