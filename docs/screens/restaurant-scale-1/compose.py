from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json, shutil, hashlib
P=Path(__file__).parent
rows=json.loads((P/'metrics.json').read_text())['captures']
F='C:/Windows/Fonts/segoeui.ttf'
def font(n):return ImageFont.truetype(F,n)
for r in rows:
 p=P/r['file']; im=Image.open(p).convert('RGB'); d=ImageDraw.Draw(im); w,h=im.size; top,bot=r['topBand'],r['bottomBand'];s=top/44
 d.rectangle((0,0,w,top-1),fill='#F4EFE3');d.rectangle((0,h-bot,w,h),fill='#173F57')
 d.text((round(14*s),round(8*s)),f"RESTAURANT SCALE   {r['roomW']} x {r['roomD']} m   /   {r['pitch']} deg {r['projection']}" ,font=font(round(17*s)),fill='#173F57')
 y=h-bot+round(9*s);x=round(14*s)
 d.text((x,y),f"Back tile {r['tileW']:.1f} x {r['tileD']:.1f} px   |   Crew {r['crewHeight']:.1f} px   |   Stove tops {r['kitchenVisible']}/{r['kitchenSamples']} visible",font=font(round(14*s)),fill='#F4EFE3')
 d.text((x,y+round(25*s)),f"Whole room fits   /   {'44 px PASS' if r['tappable'] else '44 px FAIL - zoom for placement'}   /   warm = kitchen, wood = guests",font=font(round(13*s)),fill='#F4EFE3')
 # A literal 44px reference remains44 at both output sizes; metric compares screen pixels.
 d.rectangle((w-62,h-60,w-18,h-16),outline='#E6AD38',width=2); d.text((w-59,h-48),'44',font=font(14),fill='#E6AD38')
 im.save(p)
for w in (844,1440):
 for rw in (8,10,12,14):
  group=[r for r in rows if r['width']==w and r['roomW']==rw]
  thumbw=560;thumbh=round(group[0]['height']/w*thumbw);sheet=Image.new('RGB',(2*thumbw,3*thumbh),'#173F57')
  for i,r in enumerate(group): # order pitch then perspective/ortho
   im=Image.open(P/r['file']);im.thumbnail((thumbw,thumbh));sheet.paste(im,((i%2)*thumbw,(i//2)*thumbh))
  sheet.save(P/f"contact-{rw}x{group[0]['roomD']}-{w}.png")
assert len(rows)==48
for r in rows:assert Image.open(P/r['file']).size==(r['width'],r['height'])
print('48 overlays and dimensions PASS;8 contact sheets generated')

