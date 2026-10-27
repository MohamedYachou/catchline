"""Independently inspect actual PNG edges and every proof cell, build labelled comparisons."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np,json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3];rows=[]
for n in (1024,2048):
 t=Image.open(O/f'sea1-night-water-{n}.png');a=np.asarray(t);assert t.mode=='RGB' and t.size==(n,n)
 assert np.array_equal(a[0],a[-1]) and np.array_equal(a[:,0],a[:,-1])
 p=Image.open(O/f'sea1c-tiling-proof-{n}-4x4.png');assert p.size==(4*n,4*n)
 for x in range(4):
  for y in range(4):assert np.array_equal(np.asarray(p.crop((x*n,y*n,(x+1)*n,(y+1)*n))),a)
 rows.append({'size':n,'exact_X':True,'exact_Y':True,'corners_equal':bool(np.array_equal(a[0,0],a[-1,-1])),'proof_cells_checked':16,'mode':'RGB'})
(O/'sea1c-independent-audit.json').write_text(json.dumps({'pass':True,'textures':rows},indent=2))
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
def sheet(name,items,w=720,h=450):
 out=Image.new('RGB',(2*w,((len(items)+1)//2)*(h+45)),(15,23,31));d=ImageDraw.Draw(out)
 for i,(label,path) in enumerate(items):
  im=Image.open(path).convert('RGB');im.thumbnail((w,h));x=(i%2)*w;y=(i//2)*(h+45);out.paste(im,(x+(w-im.width)//2,y+45+(h-im.height)//2));d.text((x+12,y+10),label,font=font,fill='white')
 out.save(O/name,quality=95)
painting=R/'Art/Source/Restaurant/concepts/ui-service-desktop.png'
sheet('sea1c-review.jpg',[
 ('Reference painting - water hue target',painting),
 ('Native BEFORE r127 - near-black sea1b',R/'docs/screens/restaurant-ui/r127/day-service-orders-1440.png'),
 ('Blender AFTER 1440x900 - source proof',O/'sea1c-renders/sea1c-room-1440x900.png'),
 ('Blender AFTER 844x390 - source proof',O/'sea1c-renders/sea1c-room-844x390.png')])
sheet('sea1c-before-after.jpg',[
 ('Previous exact-periodic sea1b',O/'sea1c-provenance/prior-tile-review.jpg'),
 ('SEA-1C azure/cyan repaint',O/'sea1-night-water-1024.png'),
 ('Same V4 Blender BEFORE',O/'sea1b-renders/sea1b-room-1440x900.png'),
 ('Same V4 Blender AFTER',O/'sea1c-renders/sea1c-room-1440x900.png')])
print('SEA1C INDEPENDENT PIXEL/CELL AUDIT PASS')
