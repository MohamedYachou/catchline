"""Readable source-only review sheets, dimensions and mount metadata."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
O=Path(__file__).resolve().parent;M=json.loads((O/'manifest.json').read_text())['items']
f=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
ink='#173F57';cream='#F4EFE3'
im=Image.new('RGB',(2000,1790),cream);d=ImageDraw.Draw(im)
d.text((28,18),'OVERHEAD STRUCTURE / CC0 pack dressing',font=f(37),fill=ink)
d.text((28,73),'Fresh FBX imports | game camera: pitch 38 / yaw 2 | accepted Catchline atlases',font=f(23),fill=ink)
for i,r in enumerate(M):
 p=Image.open(O/'renders'/(r['stem']+'.png')).convert('RGB');p.thumbnail((960,705));x=i%2*1000;y=120+i//2*830;im.paste(p,(x+(1000-p.width)//2,y))
 d.text((x+24,y+710),r['stem'],font=f(30),fill=ink)
 w,h,dep=r['size_unity_m'];d.text((x+24,y+755),f'{w:.2f}W x {dep:.2f}D x {h:.2f}H m / {r["mount"]}',font=f(23),fill=ink)
im.save(O/'structure-detail-contact.jpg',quality=95)
grid=Image.open(O/'renders/grid.png').convert('RGB');out=Image.new('RGB',(2400,1770),cream);out.paste(grid,(0,120));d=ImageDraw.Draw(out)
d.text((25,16),'OVERHEAD STRUCTURE / game camera / 1 m grid',font=f(38),fill=ink)
d.text((25,69),'Overhead / wall mount origins at 2.6 m | small proof mounting pads excluded from FBXs',font=f(25),fill=ink)
for i,a in enumerate(json.loads((O/'grid-layout.json').read_text())):
 x0,y0,x1,y1=a['pixel_bounds'];x=(x0+x1)/2;y=y1+135
 text=f'{i+1:02d} {a["stem"]}';width=d.textlength(text,font=f(27))
 d.rounded_rectangle((x-width/2-10,y-3,x+width/2+10,y+36),radius=4,fill=cream);d.text((x,y),text,font=f(27),fill=ink,anchor='mt')
out.save(O/'structure-contact.jpg',quality=95)
out.resize((844,622),Image.Resampling.LANCZOS).save(O/'structure-contact-844.jpg',quality=95)
keys=['stem','name','mount','mount_height_m','mount_convention','footprint_tiles','size_unity_m','clear_span_unity_m']
(O/'footprints.json').write_text(json.dumps(dict(tile_m=1,size_order='Unity W(X), H(Y), D(Z)',items=[{k:r[k] for k in keys} for r in M]),indent=2))
print('PACKAGED',flush=True)
