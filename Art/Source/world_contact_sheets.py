"""Actual export previews in labelled sheets for Tasks07/08."""
from pathlib import Path
import json,sys
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]
font=ImageFont.truetype(str(ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'),20)
for batch in sys.argv[1:] or ['WorldPolish','DayBoatKit']:
 out=ROOT/'Art/Models'/batch;data=json.loads((out/'build-metrics.json').read_text())
 groups={a['group'] for a in data['assets']}
 for group in sorted(groups):
  assets=[a for a in data['assets'] if a['group']==group];rows=(len(assets)+3)//4
  im=Image.new('RGB',(1400,rows*380+60),'#F4EFE3');d=ImageDraw.Draw(im)
  d.text((20,15),'CATCHLINE / '+batch+' / '+group,font=font,fill='#173F57')
  for i,a in enumerate(assets):
   x=i%4*350;y=60+i//4*380
   im.paste(Image.open(ROOT/a['preview']).resize((350,350)),(x,y))
   d.text((x+10,y+350),a['asset'],font=font,fill='#173F57')
  im.save(out/(group+'-contact-sheet.png'))
 print(batch,'contact sheets complete')
