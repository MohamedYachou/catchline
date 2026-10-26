"""Create labelled, matched evidence from completed Blender render pairs."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[3];name=sys.argv[1];o=R/'Art/Models/BoatsV2'/name;p=o/'renders'
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
views=['front-three-quarter','side','back-three-quarter','top','low-waterline','deck-55','game-exact-45']
for v in views:
 sheet=Image.new('RGB',(1600,656),'#F4EFE3');d=ImageDraw.Draw(sheet)
 for i,label in enumerate(['old','new']):
  sheet.paste(Image.open(p/(label+'-'+v+'.png')).convert('RGB'),(800*i,56));d.text((20+800*i,10),f'{name} / {"CURRENT" if i==0 else "REFINED"} / {v}',font=f,fill='#173F57')
 sheet.save(p/('compare-'+v+'.png'))
contact=Image.new('RGB',(1200,7*270+60),'#F4EFE3');d=ImageDraw.Draw(contact);d.text((18,10),name+' | CURRENT left / REFINED right | matched authoring cameras',font=small,fill='#173F57')
for i,v in enumerate(views):
 im=Image.open(p/('compare-'+v+'.png'));im.thumbnail((640,263));contact.paste(im,(280,52+i*270));d.text((16,120+i*270),v,font=small,fill='#173F57')
contact.save(p/'review-sheet.png');print(name,'7 comparison pairs and review-sheet ready')
