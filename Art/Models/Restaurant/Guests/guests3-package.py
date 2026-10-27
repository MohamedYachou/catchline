from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3];font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
rows=json.loads((O/'guests3-metrics.json').read_text())['guests'];bg='#eae3d2';ink='#173f57'
# Eight faces next to full-front bodies: exact landscape-phone sheet, four pairs per row.
out=Image.new('RGB',(844,390),bg);d=ImageDraw.Draw(out)
for i,row in enumerate(rows):
 x=(i%4)*211;y=(i//4)*195;d.text((x+8,y+5),row['name'].replace('Guest_','')+' / '+str(i+9).zfill(2),font=font,fill=ink)
 face=Image.open(R/'Art/Source/Restaurant/clothes/guests'/row['face']).convert('RGBA');face.thumbnail((66,66),Image.Resampling.LANCZOS);out.paste(face,(x+8,y+63),face)
 im=Image.open(O/'renders-guests3'/(row['name']+'-front.png')).convert('RGB');im.thumbnail((124,168),Image.Resampling.LANCZOS);out.paste(im,(x+81,y+22))
out.save(O/'guests3-front-lineup-844x390.png')
# Larger three-pose sheets include the actual face reference; inspect all eight identities.
for row in rows:
 out=Image.new('RGB',(1040,470),bg);d=ImageDraw.Draw(out);d.text((14,10),row['name']+' | original review '+row['face']+' | fresh FBX: Idle / Sit / Eat',font=font,fill=ink)
 face=Image.open(R/'Art/Source/Restaurant/clothes/guests'/row['face']);out.paste(face,(12,100),face)
 for i,label in enumerate(['front','sit','eat']):
  im=Image.open(O/'renders-guests3'/(row['name']+'-'+label+'.png'));im.thumbnail((264,420));out.paste(im,(220+i*270,38))
 out.save(O/(row['name']+'-guests3-poses.jpg'),quality=94)
print('guests3 contacts ready')
