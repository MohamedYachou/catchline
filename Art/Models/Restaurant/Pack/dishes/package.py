from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
O=Path(__file__).resolve().parent
F=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
S=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
M=json.loads((O/'manifest.json').read_text())
for mode in ['table','detail']:
 sheet=Image.new('RGB',(1800,1120),'#F4EFE3');d=ImageDraw.Draw(sheet)
 d.text((28,16),'PACK-DISHES-1 | fresh FBX imports | game pitch 38 deg / yaw 2 deg | '+mode,fill='#173F57',font=F)
 for i,r in enumerate(M['items']):
  x=(i%3)*600;y=58+(i//3)*520
  im=Image.open(O/'renders'/(r['name']+'-'+mode+'.png')).convert('RGB');im.thumbnail((580,440),Image.Resampling.LANCZOS)
  sheet.paste(im,(x+(600-im.width)//2,y))
  d.text((x+18,y+445),r['name'].replace('Restaurant_',''),font=F,fill='#173F57')
  a=r['size_unity'];d.text((x+18,y+477),f'{a[0]*100:.1f} W x {a[2]*100:.1f} D x {a[1]*100:.1f} H cm',font=S,fill='#173F57')
 sheet.save(O/f'contact-{mode}.jpg',quality=94)
print('PACKAGED',len(M['items']))
