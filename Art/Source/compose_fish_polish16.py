"""Asset review only: run with repository Pillow environment. Not a native HUD capture."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
ROOT=Path(__file__).resolve().parents[2];p=ROOT/'Art/Models/FishPolish16'
font_path=ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'
font=ImageFont.truetype(str(font_path),24);small=ImageFont.truetype(str(font_path),18)
im=Image.new('RGB',(1800,690),'#F4EFE3');d=ImageDraw.Draw(im)
d.text((24,16),'CATCHLINE / FISH MODEL & PORTRAIT REVIEW',font=font,fill='#173F57')
d.text((24,51),'Authored asset review, not Unity HUD captures. Transparent portraits rendered from the model sources.',font=small,fill='#173F57')
names=['Herring','Mackerel','Pollock','SeaBass','CongerEel','Plaice','Cod','Whiting','RedMullet','Turbot']
for i,name in enumerate(names):
 r=json.loads((p/name/'validation.json').read_text());x=16+i%5*358;y=94+i//5*285
 d.rounded_rectangle((x,y,x+342,y+265),radius=14,fill='#E9E3D4')
 img=Image.open(next((p/name).glob('fish-*.png'))).convert('RGBA');img.thumbnail((326,200))
 im.paste(img,(x+(342-img.width)//2,y+24+(170-img.height)//2),img)
 label={'SeaBass':'Sea bass','CongerEel':'Conger eel','RedMullet':'Red mullet'}.get(name,name)
 d.text((x+16,y+210),label,font=font,fill='#173F57')
 d.text((x+16,y+242),f"{r['triangles']} triangles · {r['meshes']} meshes · FBX checked",font=small,fill='#173F57')
im.save(p/'Fish-lineup.png')
