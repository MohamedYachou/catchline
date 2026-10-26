"""Offline handoff proof using exported sprites and measured live text, not Unity."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
P=Path(__file__).resolve().parent
layout=json.loads((P/'layout.json').read_text())
styles=json.loads((P/'text-styles.json').read_text(encoding='utf-8'))['styles']
im=Image.new('RGBA',(2532,1170))
for it in layout['placements']:
    path=P/(it['name']+'.png')
    if not path.exists():continue
    sp=Image.open(path).convert('RGBA');x,y,w,h=it['rect']
    if it.get('flipX'):sp=ImageOps.mirror(sp)
    sp=sp.resize((w*3,h*3),Image.Resampling.LANCZOS)
    im.alpha_composite(sp,(x*3,y*3))
d=ImageDraw.Draw(im)
fontpath=str(P.parents[5]/'Assets/Resources/Fonts/Fredoka-Bold.ttf')
# root is resolved independently to keep this art helper portable inside checkout.
fontpath=str(next(parent for parent in P.parents if (parent/'Assets').exists())/'Assets/Resources/Fonts/Fredoka-Bold.ttf')
for t in styles:
    x,y,w,h=t['rect'];n=t['size']*3;stroke=round(t['stroke_width']*3)
    while True:
        f=ImageFont.truetype(fontpath,n);bb=d.textbbox((0,0),t['text'],font=f,stroke_width=stroke)
        if (bb[2]-bb[0]<=w*3 and bb[3]-bb[1]<=h*3) or n<=12:break
        n-=1
    d.text((x*3-bb[0],y*3+(h*3-(bb[3]-bb[1]))//2-bb[1]),t['text'],font=f,fill=t['fill'],stroke_width=stroke,stroke_fill=t['stroke'])
im.save(P/'reconstructed-3x.png',optimize=True)
canvas=Image.new('RGB',(1688,850),'#E9E2D2');canvas.paste(Image.open(P/'../../concepts/ui-6-dashboard.png'),(0,35));canvas.paste(im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB'),(844,35))
d=ImageDraw.Draw(canvas);f=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',18)
d.text((15,8),'Painted mockup',font=f,fill='#10263D');d.text((859,8),'Offline sprite + measured text proof (not Unity)',font=f,fill='#10263D')
# Large enough to inspect both at exact logical display scale.
canvas=canvas.crop((0,0,1688,445));canvas.save(P/'reconstruction-compare.jpg',quality=95)
print('offline reconstruction written')
