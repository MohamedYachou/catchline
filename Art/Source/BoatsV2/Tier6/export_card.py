"""Routine alpha-preserving export of generated card; no image repainting."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib,json
S=Path(__file__).resolve().parent;R=S.parents[3]
master=Image.open(S/'card-master.png');assert master.mode=='RGBA'
alpha=master.getchannel('A');assert alpha.getextrema()==(0,255)
bbox=alpha.point(lambda x:255 if x>8 else 0).getbbox();assert bbox
crop=master.crop(bbox);crop.thumbnail((432,312),Image.Resampling.LANCZOS)
card=Image.new('RGBA',(480,360),(0,0,0,0));card.alpha_composite(crop,((480-crop.width)//2,(360-crop.height)//2))
out=R/'Art/Source/BoatsV2/ui/v2-item-hull-tier6.png';card.save(out)
a=card.getchannel('A');b=a.getbbox();assert b[0]>=20 and b[1]>=20 and b[2]<=460 and b[3]<=340
assert a.getextrema()==(0,255)
# Native-size comparison, reference cards are read-only.
compare=Image.new('RGB',(1440,410),'#E9E3D8');d=ImageDraw.Draw(compare)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',19)
for i,(label,path) in enumerate([('Skiff — accepted style',R/'Art/Source/BoatsV2/ui/v2-item-hull1.png'),('Shelter — new tier 6',out),('Prep — accepted style',R/'Art/Source/BoatsV2/ui/v2-item-hull3.png')]):
 im=Image.open(path).convert('RGBA');assert im.size==(480,360)
 compare.paste(im,(480*i,40),im);d.text((480*i+18,12),label,font=font,fill='#173F57')
compare.save(S/'card-review.png')
receipt={'asset':str(out.relative_to(R)),'dimensions':card.size,'mode':card.mode,'alpha_extrema':a.getextrema(),'visible_bounds':b,'master_dimensions':master.size,'master_visible_bounds_threshold8':bbox,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'export':'Alpha bbox >8 crop, Lanczos thumbnail within432x312, centred480x360; alpha preserved; no repainting','visual_review':'Pending final opening; see REPORT.md and comms.md'}
(S/'card-validation.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt,indent=2))
