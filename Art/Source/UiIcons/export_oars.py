from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
im=Image.open(O/'oars-master.png').convert('RGBA')
box=im.getchannel('A').point(lambda a:255 if a>8 else 0).getbbox()
im=im.crop(box);im.thumbnail((142,142),Image.Resampling.LANCZOS)
out=Image.new('RGBA',(160,160));out.alpha_composite(im,((160-im.width)//2,(160-im.height)//2))
out.save(O/'v2-icon-oars.png');out.save(R/'Assets/Art/UI/v2-icon-oars.png')
sheet=Image.new('RGB',(720,300),'#F0EADD');d=ImageDraw.Draw(sheet)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
for row,size in enumerate([32,64]):
 d.text((12,35+row*140),str(size)+'px',font=font,fill='#182C3B')
 for col,name in enumerate(['fuel','anchor','home','oars']):
  tile=Image.open(R/f'Assets/Art/UI/v2-icon-{name}.png').convert('RGBA');tile.thumbnail((size,size),Image.Resampling.LANCZOS)
  x=100+col*155;y=30+row*140
  sheet.paste(tile,(x+(64-size)//2,y),tile);d.text((x,y+70),name,font=font,fill='#182C3B')
sheet.save(O/'comparison-32-64.png')
checks={'size':out.size,'mode':out.mode,'alpha_extrema':out.getchannel('A').getextrema(),'alpha_bounds':out.getbbox(),'source_alpha_bounds':box,'assets_identical':(O/'v2-icon-oars.png').read_bytes()==(R/'Assets/Art/UI/v2-icon-oars.png').read_bytes(),'sha256':hashlib.sha256((O/'v2-icon-oars.png').read_bytes()).hexdigest(),'native_tested':False}
(O/'validation.json').write_text(json.dumps(checks,indent=2));print(checks)
