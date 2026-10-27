from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,math,hashlib
O=Path(__file__).resolve().parent
F='C:/Windows/Fonts/segoeui.ttf';B='C:/Windows/Fonts/segoeuib.ttf'
def font(n,b=False):return ImageFont.truetype(B if b else F,n)
M=json.loads((O/'manifest.json').read_text());before=Image.open(O/'renders/before-grid.png').convert('RGB');after=Image.open(O/'renders/after-grid.png').convert('RGB')
layouts={k:{x['name']:x for x in json.loads((O/(k+'-grid-layout.json')).read_text())} for k in ['before','after']}
for key,im in [('before',before),('after',after)]:
 canvas=Image.new('RGB',(3600,2920),'#F4EFE3');canvas.paste(im,(0,100));d=ImageDraw.Draw(canvas)
 d.text((40,20),'PACK-ITEMS-1 / '+('INCUMBENT' if key=='before' else 'CATCHLINE PACK ASSEMBLIES'),font=font(36,True),fill='#173F57')
 d.text((40,65),'Fresh FBX imports | 1 m floor grid | orthographic inspection at game pitch 38 deg, yaw 2 deg | source proof, not Unity',font=font(23),fill='#173F57')
 for name,a in layouts[key].items():
  x,y=a['pixel_origin'];label=name.replace('Restaurant_','');w=d.textbbox((0,0),label,font=font(22,True))[2]
  d.rounded_rectangle((x-w/2-7,y+108,x+w/2+7,y+139),radius=5,fill='#F4EFE3');d.text((x-w/2,y+107),label,font=font(22,True),fill='#173F57')
 canvas.save(O/(key+'-grid-contact.jpg'),quality=94)
pairs=[]
for rec in M['items']:
 n=rec['name'];boxes=[]
 for key in ['before','after']:
  a=layouts[key][n];x,y=a['pixel_origin'];b=a['pixel_bounds'];boxes.append([b[0]-x,b[1]-y,b[2]-x,b[3]-y])
 relative=[min(-200,math.floor(min(a[0] for a in boxes)-35)),math.floor(min(a[1] for a in boxes)-25),max(200,math.ceil(max(a[2] for a in boxes)+35)),math.ceil(max(a[3] for a in boxes)+25)]
 # Origin-aligned equal scale. Grid ordering may differ after selective rebuilds.
 # Orthographic projection preserves identical pixels/metre everywhere.
 crops=[]
 for key,im in [('before',before),('after',after)]:
  x,y=layouts[key][n]['pixel_origin'];x=round(x);y=round(y)
  crops.append(im.crop((relative[0]+x,relative[1]+y,relative[2]+x,relative[3]+y)))
 w,h=crops[0].size
 p=Image.new('RGB',(w*2+30,h+100),'#F4EFE3');p.paste(crops[0],(10,44));p.paste(crops[1],(w+20,44));d=ImageDraw.Draw(p)
 d.text((10,7),n.replace('Restaurant_','')+' | incumbent',font=font(17,True),fill='#173F57');d.text((w+20,7),'Pack | same scale',font=font(17,True),fill='#173F57')
 u=rec['size_unity'];r=rec['reference']['size'];d.text((10,h+50),f'W/H/D: old {r[0]:.2f}/{r[2]:.2f}/{r[1]:.2f} m   pack {u[0]:.2f}/{u[1]:.2f}/{u[2]:.2f} m',font=font(15),fill='#173F57')
 p.save(O/'comparisons'/(n+'.jpg'),quality=94);pairs.append(p)
for j in range(0,len(pairs),6):
 sub=pairs[j:j+6];cw=max(im.width for im in sub)+20;ch=max(im.height for im in sub)+20
 im=Image.new('RGB',(cw*2,ch*math.ceil(len(sub)/2)+85),'#E5DDCB');d=ImageDraw.Draw(im);d.text((24,20),f'PACK-ITEMS-1 / same-camera comparison {j//6+1}',font=font(29,True),fill='#173F57')
 for k,p in enumerate(sub):im.paste(p,((k%2)*cw,(k//2)*ch+85))
 im.save(O/f'comparison-contact-{j//6+1}.jpg',quality=94)
if (O/'renders/front-grid.png').exists():
 im=Image.open(O/'renders/front-grid.png').convert('RGB');im.save(O/'front-grid-contact.jpg',quality=94)
print('PACKAGED',len(pairs),'equal-scale pairs')
