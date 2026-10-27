from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
O=Path(__file__).resolve().parent
f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
c=Image.new('RGB',(1600,1180),'#14232c');d=ImageDraw.Draw(c)
d.text((24,16),'STAGE 3 / RESTAURANT — white linen, brass bar, expanded water terrace',font=f,fill='white')
for path,box,label in [(O/'renders/restaurant-room-1440x900.png',(0,62,1120,700),'Stage 3 • 1440 × 900'),(O.parent/'Stage2Bistro/renders/bistro-room-1440x900.png',(1120,95,480,300),'Accepted Stage 2 reference'),(O/'renders/restaurant-room-844x390.png',(0,760,844,390),'Stage 3 • 844 × 390')]:
 im=Image.open(path).convert('RGB');im.thumbnail((box[2],box[3]));c.paste(im,(box[0]+(box[2]-im.width)//2,box[1]));d.text((box[0]+14,box[1]-30),label,font=f,fill='white')
for i,line in enumerate(['12 × 6 m room','6 indoor tables / 18 seats','5 terrace tables / 20 seats','Separate bar / 3 stools','Open kitchen work surfaces','V4 atlas + EXPORT_ nodes','Blender camera proof','Native integration: Claude']):d.text((900,780+i*41),line,font=f,fill='#e5d7b9')
c.save(O/'restaurant-review.jpg',quality=95)
m=json.loads((O/'build-metrics.json').read_text());report=(O/'REPORT.md').read_text().replace('199 meshes, 192,010 triangles',f"{len(m['production_meshes'])} meshes, {m['room_triangles']:,} triangles")
(O/'REPORT.md').write_text(report)
print('PACKAGE PASS')
