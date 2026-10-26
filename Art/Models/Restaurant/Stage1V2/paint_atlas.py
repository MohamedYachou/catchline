"""Authored brush strokes/colour fields; no photographs, random pixel noise or AI source.
Each swatch has 16px bleed. UV0s map to inset cells; roughness/metal/emission in RGB.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
import math,random,json
O=Path(__file__).resolve().parent;T=O/'textures';T.mkdir(exist_ok=True);random.seed(2402)
# 8 columns x4 rows; each cell256x512. Explicit house palette + material-specific strokes.
PALETTE=[
('navy','173F57',.36,0,0,'enamel'),('blue','2A6685',.38,0,0,'enamel'),('ivory','F3F0DC',.42,0,0,'enamel'),('plaster','E7D9BD',.88,0,0,'stone'),
('wood','C58B50',.57,0,0,'wood'),('woodlight','DFB77A',.56,0,0,'wood'),('wooddark','8C5A36',.68,0,0,'wood'),('steel','8FA6AC',.31,.65,0,'steel'),
('dark','28343B',.77,0,0,'flat'),('brass','C99B4A',.3,.7,0,'steel'),('orange','E36A35',.45,0,0,'enamel'),('teal','168F9F',.78,0,0,'cloth'),
('leaf','657745',.85,0,0,'leaf'),('tile1','E8DEC6',.72,0,0,'tile'),('tile2','E5D5B7',.74,0,0,'tile'),('tile3','EFE6D1',.7,0,0,'tile'),
('stone','B0A48E',.91,0,0,'stone'),('stonecool','8F928D',.94,0,0,'stone'),('stonecream','C7B79A',.91,0,0,'stone'),('glow','FFCB64',.55,0,1,'glow'),
('catginger','CA823B',.84,0,0,'flat'),('catgrey','666C71',.85,0,0,'flat'),('fish','BAC9C6',.44,.15,0,'enamel'),('food','C47A3B',.64,0,0,'food'),
('soup','D98936',.45,0,0,'food'),('lettuce','539651',.88,0,0,'leaf'),('white','F3E5CB',.76,0,0,'cloth'),('rope','D1AF76',.86,0,0,'rope'),
('terracotta','AD6948',.86,0,0,'stone'),('glass','486B78',.27,.1,0,'enamel'),('coffee','573B2C',.42,0,0,'flat'),('char','67462E',.8,0,0,'flat')]
base=Image.new('RGB',(2048,2048));surface=Image.new('RGB',(2048,2048));rows=[]
def col(rgb,f,add=0):return tuple(max(0,min(255,round(c*f+add))) for c in rgb)
for idx,(name,h,rough,metal,emission,kind) in enumerate(PALETTE):
 rgb=tuple(bytes.fromhex(h));im=Image.new('RGB',(256,512));dr=ImageDraw.Draw(im)
 # Brush-built broad gradients, rather than a baked directional scene light.
 for y in range(512):
  f=1+.032*math.sin(y/511*math.pi)-.028*math.cos(y/511*2*math.pi)
  dr.line((0,y,255,y),fill=col(rgb,f))
 if kind=='wood':
  for j in range(15):
   x=8+j*17+random.uniform(-4,4);pts=[(x+3*math.sin(y*.018+j)+2*math.sin(y*.041+j),y) for y in range(0,513,8)]
   dr.line(pts,fill=col(rgb,random.uniform(.85,.95)),width=random.choice([1,2,3]));dr.line([(a+3,b) for a,b in pts],fill=col(rgb,1.07),width=1)
  for cx,cy in [(72,147),(182,361)]:
   for r in [5,10,16]:dr.ellipse((cx-r,cy-r*2.5,cx+r,cy+r*2.5),outline=col(rgb,.89),width=2)
 elif kind in ['stone','tile']:
  # Broad irregular paint dabs; all facets/blocks and grout remain actual geometry.
  for j in range(32):
   x=random.randrange(256);y=random.randrange(512);r=random.randrange(8,42)
   dr.ellipse((x-r,y-r*.5,x+r,y+r*.5),fill=col(rgb,random.uniform(.96,1.04)))
  if kind=='tile':
   dr.rounded_rectangle((7,7,248,504),radius=18,outline=col(rgb,1.065),width=6);dr.line((16,489,239,489),fill=col(rgb,.96),width=5)
 elif kind in ['enamel','steel']:
  dr.rounded_rectangle((9,9,246,502),radius=22,outline=col(rgb,1.12,3),width=6)
  dr.line((18,35,18,474),fill=col(rgb,1.055),width=3)
  if kind=='steel':
   for x in range(30,231,20):dr.line((x,36,x,475),fill=col(rgb,1+random.uniform(-.018,.018)),width=3)
 elif kind=='cloth':
  for x in range(15,250,32):dr.line((x,0,x,512),fill=col(rgb,1.035),width=4)
 elif kind=='leaf':
  dr.line((124,0,130,512),fill=col(rgb,1.12),width=5)
 elif kind=='rope':
  for y in range(-64,560,34):dr.line((0,y,256,y+64),fill=col(rgb,.91),width=9)
 im=im.filter(ImageFilter.GaussianBlur(.8));xy=((idx%8)*256,(idx//8)*512);base.paste(im,xy)
 surface.paste(tuple(round(v*255) for v in (rough,metal,emission)),(xy[0],xy[1],xy[0]+256,xy[1]+512))
 rows.append({'name':name,'index':idx,'hex_sRGB':h,'roughness_R':rough,'metallic_G':metal,'emission_B':emission,'kind':kind,'pixel_cell':[xy[0],xy[1],256,512],'UV_inset_pixels':16})
base.save(T/'Restaurant_BaseColor.png');surface.save(T/'Restaurant_Surface.png');(T/'atlas.json').write_text(json.dumps({'size':[2048,2048],'base_sRGB':True,'surface_linear':True,'surface_channels':{'R':'roughness','G':'metallic','B':'emission mask'},'AO':'asset-local baked vertex COLOR_0 RGB','source':'Authored deterministic brush strokes; no photo noise, external or generated image','cells':rows},indent=2));print('ATLAS PASS 2x2048')
