from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
O=Path('Art/Models/Restaurant/Pack/decor2');M=json.loads((O/'manifest.json').read_text())['items'];f=lambda n:ImageFont.truetype('C:/Windows/Fonts/arial.ttf',n)
im=Image.new('RGB',(2560,1360),'#F4EFE3');d=ImageDraw.Draw(im)
d.text((24,16),'PACK DECOR 3 / harbour & bistro dressing',font=f(34),fill='#173F57')
d.text((24,60),'Fresh FBX imports | 38 degree pitch / 2 degree yaw | wall pieces mounted at 1.6 m, display yaw 180',font=f(21),fill='#173F57')
for i,r in enumerate(M):
 p=Image.open(O/'renders'/(r['stem']+'.png')).convert('RGB');p.thumbnail((620,520));x=i%4*640;y=106+i//4*615;im.paste(p,(x+(640-p.width)//2,y))
 d.text((x+18,y+518),r['stem'],font=f(25),fill='#173F57');w,h,dep=r['size_unity_m'];d.text((x+18,y+555),f'{w:.2f} W x {dep:.2f} D x {h:.2f} H m / '+r['mount'],font=f(18),fill='#173F57')
im.save(O/'decor2-detail-contact.jpg',quality=95)
grid=Image.open(O/'renders/grid.png').convert('RGB');out=Image.new('RGB',(3200,2160),'#F4EFE3');out.paste(grid,(0,115));d=ImageDraw.Draw(out)
d.text((28,18),'PACK DECOR 3 / same-scale game-camera view on a 1 m grid',font=f(37),fill='#173F57');d.text((28,69),'Wall origins mounted 1.6 m; display yaw 180 exposes -Z faces. Export roots remain identity.',font=f(25),fill='#173F57')
for i,a in enumerate(json.loads((O/'grid-layout.json').read_text())):
 x0,y0,x1,y1=a['pixel_bounds'];x=(x0+x1)/2;y=y1+122;t=f'{i+1:02d}  {a["stem"]}'
 tw=d.textbbox((0,0),t,font=f(23))[2];d.rounded_rectangle((x-tw/2-12,y-2,x+tw/2+12,y+34),radius=5,fill='#F4EFE3');d.text((x,y),t,font=f(23),fill='#173F57',anchor='mt')
out.save(O/'decor2-contact.jpg',quality=95);small=out.copy();small.thumbnail((844,1000));small.save(O/'decor2-contact-844.jpg',quality=95)
footprints={r['stem']:dict(size_unity_m=r['size_unity_m'],mount=r['mount'],footprint_tiles=r['footprint_tiles'],wall_origin_height_m=r['mount_height_m'],front=r['front_fbx'],pivot='rear contact plane, height centre' if r['mount']=='wall' else 'floor contact, footprint centre') for r in M}
(O/'footprints.json').write_text(json.dumps(footprints,indent=2));print('PACKAGED',len(M))
