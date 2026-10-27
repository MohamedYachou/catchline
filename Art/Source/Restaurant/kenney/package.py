from PIL import Image,ImageDraw,ImageFont,ImageOps
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',15)
dm=json.loads((O/'dish-map.json').read_text());de=json.loads((O/'decor-map.json').read_text())
for prefix,name in [('dish','dish-contact-tables'),('detail','dish-contact-details')]:
 out=Image.new('RGB',(1440,1340),'#F4EFE3');d=ImageDraw.Draw(out)
 d.text((18,12),'KENNEY FIT / 13 menu dishes / KayKit Catchline round table / 38 degree game pitch',font=font,fill='#173F57')
 for i,rec in enumerate(dm['dishes']):
  x=(i%4)*360;y=50+(i//4)*320
  im=Image.open(O/'renders'/f'{prefix}-{rec["dish"]}.png').convert('RGB').resize((360,270),Image.Resampling.LANCZOS);out.paste(im,(x,y))
  d.text((x+10,y+273),rec['label'],font=font,fill='#173F57')
  if rec['dish']=='Crab':d.text((x+10,y+295),'existing Catchline fallback',font=small,fill='#A7552B')
  if rec['dish']=='FishAndChips':d.text((x+10,y+295),'salmon fillet; batter art gap',font=small,fill='#A7552B')
 out.save(O/f'{name}.jpg',quality=95)
for page in range(2):
 recs=de['decor'][page*7:(page+1)*7];out=Image.new('RGB',(1400,1660),'#F4EFE3');d=ImageDraw.Draw(out)
 d.text((18,12),f'HARBOUR BISTRO DECOR / original -> Catchline / page {page+1}',font=font,fill='#173F57')
 for i,rec in enumerate(recs):
  x=(i%2)*700;y=50+(i//2)*395
  for j,var in enumerate(['original','catchline']):
   im=ImageOps.contain(Image.open(O/'renders'/f'decor-{rec["model"]}-{var}.png').convert('RGB'),(350,330),Image.Resampling.LANCZOS);out.paste(im,(x+j*350+(350-im.width)//2,y))
  d.text((x+10,y+332),rec['model'],font=font,fill='#173F57')
  d.text((x+10,y+355),' x '.join(f'{v:g}' for v in rec['display_size_m'])+' m / W x D x H',font=small,fill='#173F57')
 out.save(O/f'decor-contact-{page+1}.jpg',quality=94)
print('PACKAGED 4 final contacts')
