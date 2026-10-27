from PIL import Image, ImageDraw
from pathlib import Path
import json, hashlib
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
rows=[]
for p in (ROOT/'docs/screens/restaurant-ui').glob('r*/*.png'):
    try: r=int(p.parent.name[1:])
    except ValueError: continue
    rows.append((r,p))
latest={}
for r,p in sorted(rows): latest[p.name]=p
sel={k:v for k,v in latest.items() if int(v.parent.name[1:])>=85}
data=[]
for name,p in sorted(sel.items()):
    im=Image.open(p)
    data.append(dict(path=p.relative_to(ROOT).as_posix(),size=im.size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(OUT/'capture-inventory.json').write_text(json.dumps(data,indent=2))
for device in ('844','1440'):
    items=[x for x in data if x['path'].endswith('-'+device+'.png')]
    w=600; h=310 if device=='844' else 410
    sheet=Image.new('RGB',(w*3,h*((len(items)+2)//3)), '#243e4b'); d=ImageDraw.Draw(sheet)
    for i,item in enumerate(items):
        x=i%3*w;y=i//3*h
        im=Image.open(ROOT/item['path']).convert('RGB'); im.thumbnail((590,h-35))
        sheet.paste(im,(x,y+28)); d.text((x+5,y+5),item['path'].split('restaurant-ui/')[1],fill='white')
    sheet.save(OUT/('inventory-'+device+'.jpg'),quality=92)
print('latest captures',len(data))
