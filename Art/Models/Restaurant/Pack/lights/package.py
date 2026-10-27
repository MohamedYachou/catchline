from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
O=Path(__file__).resolve().parent;M=json.loads((O/'manifest.json').read_text())['items']
f=lambda n:ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
ink='#173F57';cream='#F4EFE3'
im=Image.new('RGB',(2400,1650),cream);d=ImageDraw.Draw(im)
d.text((28,18),'WARM FIXTURES / separate glow mesh + material',font=f(38),fill=ink)
d.text((28,73),'Fresh FBX imports | 38 degree pitch / 2 degree yaw | base colours only, emission binds in Unity',font=f(25),fill=ink)
for i,r in enumerate(M):
 p=Image.open(O/'renders'/(r['stem']+'.png')).convert('RGB');p.thumbnail((780,635));x=i%3*800;y=125+i//3*745;im.paste(p,(x+(800-p.width)//2,y))
 d.text((x+20,y+640),r['stem'],font=f(29),fill=ink)
 w,h,dep=r['size_unity_m'];d.text((x+20,y+682),f'{w:.2f}W x {dep:.2f}D x {h:.2f}H m / {r["mount"]}',font=f(21),fill=ink)
im.save(O/'lights-detail-contact.jpg',quality=95)
grid=Image.open(O/'renders/grid.png').convert('RGB');out=Image.new('RGB',(2400,1770),cream);out.paste(grid,(0,120));d=ImageDraw.Draw(out)
d.text((25,16),'WARM FIXTURES / game camera / 1 m grid',font=f(38),fill=ink)
d.text((25,69),'Wall origins 1.6 m / pendant at 2.5 m / table lamp at .72 m | proof supports excluded from FBXs',font=f(24),fill=ink)
for i,a in enumerate(json.loads((O/'grid-layout.json').read_text())):
 x0,y0,x1,y1=a['pixel_bounds'];x=(x0+x1)/2;y=y1+135
 text=f'{i+1:02d} {a["stem"]}';width=d.textlength(text,font=f(24))
 d.rounded_rectangle((x-width/2-10,y-3,x+width/2+10,y+33),radius=4,fill=cream);d.text((x,y),text,font=f(24),fill=ink,anchor='mt')
out.save(O/'lights-contact.jpg',quality=95)
phone=out.resize((844,622),Image.Resampling.LANCZOS);phone.save(O/'lights-contact-844.jpg',quality=95)
(O/'footprints.json').write_text(json.dumps(dict(tile_m=1,items=[{k:r[k] for k in ['stem','name','mount','mount_height_m','footprint_tiles','size_unity_m','glow_mesh','glow_material']} for r in M]),indent=2))
print('PACKAGED',flush=True)
