from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json
R=Path(__file__).resolve().parents[4];O=R/'Art/Models/Maps/GullKelpForest'
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
rows=[]
for old in sorted(O.glob('SeaV2-sand-edges-*-old.png')):
 new=old.with_name(old.name.replace('-old.png','-new.png'));a=Image.open(old);b=Image.open(new);assert a.size==b.size
 sheet=Image.new('RGB',(a.width*2,a.height+40),'#142f33');sheet.paste(a,(0,40));sheet.paste(b,(a.width,40));draw=ImageDraw.Draw(sheet)
 label=old.name.removeprefix('SeaV2-sand-edges-').removesuffix('-old.png')
 draw.text((14,8),'ACCEPTED BEFORE | '+label,font=font,fill='#eadfbd');draw.text((a.width+14,8),'SAND EDGES AFTER | '+label,font=font,fill='#eadfbd')
 out=old.with_name(old.name.replace('-old.png','-comparison.png'));sheet.save(out)
 rows.append({'comparison':out.name,'before':old.name,'after':new.name,'capture_resolution':list(a.size)})
(O/'SeaV2-sand-edges-comparisons.json').write_text(json.dumps(rows,indent=2)+'\n');print('PAIRS',len(rows))
