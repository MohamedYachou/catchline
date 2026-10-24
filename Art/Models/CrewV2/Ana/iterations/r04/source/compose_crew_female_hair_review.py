"""Compose unaltered six supplied-script renders and the identity reference."""
from pathlib import Path
import argparse,json
from PIL import Image,ImageDraw,ImageFont,ImageOps
p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
r=Path(__file__).resolve().parents[2];o=r/'Art/Models/CrewV2'/a.name
m=json.loads((o/'build-manifest.json').read_text());h=json.loads((o/'hair-coverage-hits.json').read_text())
assert h['revision']==m['revision'] and h['skin_first_hits']==0
pre=o/'iterations'/m['revision']/'headshots'
froot=Path('/mnt/c/Windows/Fonts')
f=lambda size:ImageFont.truetype(str(froot/'segoeui.ttf'),size)
W,H=2240,470;sheet=Image.new('RGB',(W,H),'#F4EFE3');d=ImageDraw.Draw(sheet)
d.text((15,8),f"{a.name} | {m['revision']} | {h['scalp_samples']} scalp rays, zero skin-first hits",font=f(27),fill='#173F57')
ref=r/'Art/Source/UIv2/crew-styles'/('portrait-'+a.name.lower()+'.png')
if a.name=='CaptainF':im=Image.open(r/'docs/screens/crew-styles/lineup-2d.png').crop((1410,92,1765,540))
else:im=Image.open(ref)
views=[('2D reference',im)]+[(label,Image.open(pre/(a.name+'_'+view+'.png'))) for view,label in [('front','Front'),('q_left','Three-quarter'),('left','Their left'),('back','Back'),('right','Their right'),('q_back','Rear three-quarter')]]
for i,(label,im) in enumerate(views):
 thumb=ImageOps.contain(im.convert('RGB'),(310,355));sheet.paste(thumb,(i*320+(320-thumb.width)//2,55+(355-thumb.height)//2));d.text((i*320+10,420),label,font=f(22),fill='#173F57')
sheet.save(o/(a.name+'-hair-review.png'))
print(o/(a.name+'-hair-review.png'))
