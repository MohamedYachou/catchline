"""Pillow: source-only ART-011 HUD-footprint composites and plan review."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Art/Models/HarbourMouth11'
MAIN=ROOT.parent/'Catchline';FONT=ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'
HUD={
 'desktop':[(34,32,432,313),(1204,28,1411,67),(1134,27,1174,67),(1201,95,1415,141),(34,800,432,864),(436,603,1004,868)],
 'phone':[(20,19,250,180),(707,18,828,39),(667,17,692,41),(706,54,829,82),(20,332,250,371),(257,247,587,374)]}
for device,rects in HUD.items():
    source=MAIN/'docs/screens/polish-002'/device/'05-bite.png'
    target=OUT/('Runtime-HUD-source-'+device+'.png')
    if not target.exists():shutil.copy2(source,target)
    im=Image.open(OUT/('Beauty-'+device+'.png')).convert('RGB');hud=Image.open(target).convert('RGB')
    assert im.size==hud.size
    for rect in rects:
        tile=hud.crop(rect);mask=Image.new('L',tile.size)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,tile.width-1,tile.height-1),radius=min(20,tile.height//2),fill=255)
        im.paste(tile,rect[:2],mask)
    draw=ImageDraw.Draw(im);font=ImageFont.truetype(str(FONT),14 if device=='desktop' else 10)
    text='REFERENCE COMPOSITE / existing HUD footprints over Blender world / not a Unity capture'
    draw.rectangle((im.width*.30,im.height-21,im.width,im.height),fill='#F4EFE3')
    draw.text((im.width*.30+8,im.height-19),text,font=font,fill='#173F57')
    im.save(OUT/('HUD-overlay-'+device+'.png'))

data=json.loads((OUT/'build-metrics.json').read_text());plans=data['coast_plans_screen_ground']
im=Image.new('RGB',(1300,900),'#168F9F');draw=ImageDraw.Draw(im)
font=ImageFont.truetype(str(FONT),22);small=ImageFont.truetype(str(FONT),17)
def p(s,t):return (650+s*65,450-t*65)
for name,poly in plans.items():
    draw.polygon([p(*v) for v in poly],fill='#729053',outline='#D9C393',width=5)
    center=(sum(x for x,y in poly)/len(poly),sum(y for x,y in poly)/len(poly))
    draw.text(p(*center),name,font=font,fill='#173F57')
for name,half,color in [('desktop',5.12,'#F3F0DC'),('phone',6.4*844/390/2,'#E36A35')]:
    draw.rectangle((*p(-half,3.2),*p(half,-3.2)),outline=color,width=3)
    draw.text(p(-half,3.55 if name=='desktop' else 3.90),name+' exact water-plane footprint',font=small,fill=color)
draw.rectangle((*p(-2.6,1.7),*p(2.6,-1.8)),outline='#DFB77A',width=3)
draw.text(p(-2.45,-1.5),'Clear boat / cast / action channel',font=small,fill='#F3F0DC')
draw.text((24,18),'GULL HARBOUR MOUTH / authored plan and camera margins',font=font,fill='#F3F0DC')
draw.text((24,855),'Plan uses camera ground coordinates; raised terrain projects higher. Bathymetry continues beneath the complete visible area.',font=small,fill='#F3F0DC')
im.save(OUT/'Composition-plan.png')
(OUT/'hud-footprints.json').write_text(json.dumps(dict(source='POLISH-002 native 05-bite captures',
    illustrative_composite=True,desktop_rectangles=HUD['desktop'],phone_rectangles=HUD['phone']),indent=2)+'\n')
print('ART-011 exact-size HUD overlays and composed plan ready')
