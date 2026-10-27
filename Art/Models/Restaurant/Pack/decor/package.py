from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[4]
M=json.loads((O/'manifest.json').read_text())['items']
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f=lambda n:ImageFont.truetype(font,n)
# Large individual contact: legible geometry, plus exact metre-grid overview separately.
im=Image.new('RGB',(2560,1970),'#F4EFE3');d=ImageDraw.Draw(im)
d.text((24,16),'PACK DECOR / Catchline CC0 kit',font=f(34),fill='#173F57')
d.text((24,60),'Fresh FBX imports | game camera 38 degree pitch, 2 degree yaw | wall faces shown at display yaw 180',font=f(21),fill='#173F57')
for i,r in enumerate(M):
 p=Image.open(O/'renders'/(r['stem']+'.png')).convert('RGB');p.thumbnail((620,520))
 x=(i%4)*640;y=108+(i//4)*615;im.paste(p,(x+(640-p.width)//2,y))
 d.text((x+18,y+518),r['stem'],font=f(25),fill='#173F57')
 w,h,dep=r['size_unity_m'];d.text((x+18,y+555),f'{w:.2f} W x {dep:.2f} D x {h:.2f} H m / '+r['mount'],font=f(18),fill='#173F57')
im.save(O/'decor-contact.jpg',quality=94)
grid=Image.open(O/'renders/grid.png').convert('RGB');out=Image.new('RGB',(3200,2560),'#F4EFE3');out.paste(grid,(0,115));d=ImageDraw.Draw(out)
d.text((28,18),'PACK DECOR / same-scale game-camera view on a 1 m grid',font=f(37),fill='#173F57')
d.text((28,69),'Wall origins mounted 1.6 m; display yaw 180 only for wall faces / menu / wine rack. Export roots stay identity.',font=f(25),fill='#173F57')
layout=json.loads((O/'grid-layout.json').read_text())
for i,a in enumerate(layout):
 x0,y0,x1,y1=a['pixel_bounds'];x=(x0+x1)/2;y=y1+122
 text=f'{i+1:02d}  {a["stem"]}'
 d.rounded_rectangle((x-140,y-2,x+140,y+34),radius=5,fill='#F4EFE3');d.text((x,y),text,font=f(22),fill='#173F57',anchor='mt')
out.save(O/'decor-grid-contact.jpg',quality=94)
# Phone-width source overview for silhouette review (not native service screenshot).
small=im.copy();small.thumbnail((844,900));small.save(O/'decor-contact-844.jpg',quality=94)
print('PACKAGED3',flush=True)
