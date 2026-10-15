"""Assemble real rendered turnaround and animation frames, bundled Fredoka."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/CrewRig';PRE=OUT/'Previews'
font=ImageFont.truetype(str(ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'),28)
small=ImageFont.truetype(str(ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'),20)
navy='#173F57';cream='#F4EFE3'
roles=['Captain','Deckhand','Fisherman','Veteran']
im=Image.new('RGB',(1600,1770),cream);d=ImageDraw.Draw(im);d.text((25,18),'CATCHLINE / shared crew · 0.95m · four outfit turnarounds',font=font,fill=navy)
for y,role in enumerate(roles):
 for x,view in enumerate(['front','right','back','left']):
  im.paste(Image.open(PRE/f'Outfit_{role}-{view}.png'),(x*400,80+y*420))
  d.text((x*400+16,80+y*420),role+' / '+view,font=small,fill=navy)
im.save(PRE/'outfit-turnarounds.png')
m=json.loads((OUT/'manifest.json').read_text());im=Image.new('RGB',(1600,11*340+90),cream);d=ImageDraw.Draw(im)
d.text((25,18),'CATCHLINE / 24fps animation · game-angle renders · in place',font=font,fill=navy)
for i,c in enumerate(m['clips']):
 y=90+i*340;d.text((22,y+35),c['name'],font=font,fill=navy)
 d.text((22,y+77),f"1–{c['end']} / "+('loop' if c['loop'] else 'one shot'),font=small,fill=navy)
 for j in range(3):
  frame=1+j*((c['end']-1)//3);x=360+j*400
  im.paste(Image.open(PRE/f"{c['name']}-{j+1}.png").resize((320,320)),(x,y))
  d.text((x+8,y+300),f'frame {frame}',font=small,fill=navy)
im.save(PRE/'animation-contact-sheet.png')
# Gameplay-scale thumbnail inspection: 11 rows, each figure around 80px tall.
im.resize((800,round(im.height/2)),Image.Resampling.LANCZOS).save(PRE/'animation-contact-sheet-small.png')
print('Contact sheets assembled')
