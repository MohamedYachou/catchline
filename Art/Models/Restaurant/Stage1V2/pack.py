"""Technical contact/comparison composition; rendered images remain unretouched."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,math
O=Path(__file__).resolve().parent;R=O.parents[3];P=O/'renders'
font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def f(n):return ImageFont.truetype(font,n)
def title(im,s,sub=''):
 d=ImageDraw.Draw(im);d.text((24,16),s,font=f(26),fill='#f4e9d0');d.text((24,52),sub,font=f(15),fill='#a8c1c9')
def fit(canvas,src,box):
 pic=Image.open(src).convert('RGB');pic.thumbnail((box[2]-box[0],box[3]-box[1]),Image.Resampling.LANCZOS);canvas.paste(pic,(box[0]+(box[2]-box[0]-pic.width)//2,box[1]+(box[3]-box[1]-pic.height)//2))
manifest=json.loads((O/'render-manifest.json').read_text())
items=[r for r in manifest if r['file'].startswith('kit-')]
for idx in range(math.ceil(len(items)/12)):
 rows=items[idx*12:(idx+1)*12];im=Image.new('RGB',(1440,1000),'#152f3b');title(im,'Stage 1 V2 / reusable kit '+str(idx+1),'Fresh FBX imports • shared painted atlas • metre units • base pivots')
 for k,r in enumerate(rows):
  x=(k%4)*360;y=90+(k//4)*300;fit(im,P/r['file'],(x+6,y,x+354,y+258));ImageDraw.Draw(im).text((x+14,y+263),r['file'][4:-4],font=f(16),fill='#f4e9d0')
 im.save(P/('contact-kit-'+str(idx+1)+'.png'))
im=Image.new('RGB',(2880,1030),'#152f3b');title(im,'RESTAURANT-LOOK-DETAIL-2 / service reference and delivered 3D','Left: accepted UI concept. Right: actual reimported FBX, original crew + Mira, 52° orthographic / yaw 0. No HUD or water mesh.')
fit(im,R/'Art/Source/Restaurant/concepts/ui-service-desktop.png',(0,96,1440,996));fit(im,P/'room-1440x900.png',(1440,96,2880,996));im.save(P/'compare-service-desktop.png')
im=Image.new('RGB',(1688,540),'#152f3b');title(im,'Stage 1 V2 / phone readability','Reference scaled to same width (left); 844 × 390 production art proof (right). HUD, touch and Unity lighting are outside this proof.')
fit(im,R/'Art/Source/Restaurant/concepts/ui-service-desktop.png',(0,110,844,500));fit(im,P/'room-844x390.png',(844,110,1688,500));im.save(P/'compare-service-phone.png')
print('COMPOSITIONS COMPLETE',len(items),'individual kit views')

uv=json.loads((O/'UV-proof-data.json').read_text());im=Image.new('RGB',(1536,1170),'#152f3b');title(im,'UV channels / exported geometry','Top: shared atlas UV0. Bottom: independently packed UV1. Shell, prep and service plate representative samples.')
for k,(name,channels) in enumerate(uv.items()):
 x=k*512;ImageDraw.Draw(im).text((x+18,90),name,font=f(20),fill='#f4e9d0')
 for row,channel in enumerate(['UV0','UV1']):
  tile=Image.open(O/'textures/Restaurant_BaseColor.png').convert('RGB').resize((480,480)) if row==0 else Image.new('RGB',(480,480),'#edf0e8')
  d=ImageDraw.Draw(tile)
  for poly in channels[channel]:
   p=[(round(a*479),round((1-b)*479)) for a,b in poly];d.line(p+[p[0]],fill='#193a4b' if row else '#e0e7dc',width=1)
  im.paste(tile,(x+16,125+row*510));ImageDraw.Draw(im).text((x+18,610+row*510),channel,font=f(16),fill='#f4e9d0')
im.save(P/'uv-channels-proof.png')
