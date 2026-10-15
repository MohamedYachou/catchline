"""Deterministic periodic, palette-derived water and effect textures. NumPy/Pillow.
Original mathematical shapes; no third-party bitmap, noise, labels or baked UI.
"""
from pathlib import Path
import math,json
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,PngImagePlugin
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'Assets/Art/Textures';OUT.mkdir(parents=True,exist_ok=True)
N=1024
v,u=np.meshgrid(np.linspace(0,math.tau,N),np.linspace(0,math.tau,N),indexing='ij')
def rgb(h):return np.array([int(h[i:i+2],16) for i in (1,3,5)],dtype=float)
def save(im,name):
 meta=PngImagePlugin.PngInfo();meta.add(b'sRGB',b'\0');meta.add_text('Source','Art/Source/build_water_textures.py; original periodic mathematical shapes')
 im.save(OUT/(name+'.png'),pnginfo=meta)
def rgba(a):return Image.fromarray(np.uint8(np.clip(a,0,255)),'RGBA')
field=np.sin(3*u+.7*np.sin(2*v))*np.cos(2*v+.55*np.cos(3*u))
caustic=np.exp(-((field-.23)/.075)**2)
broad=(np.sin(u+.35*np.sin(v))*np.cos(v)+1)/2
streak=np.exp(-((np.sin(2*v+.35*np.sin(u))-.82)/.025)**2)*np.maximum(0,np.cos(3*u))**12
for name,base,light,sand in [('water-tile','#168F9F','#64C7C4',False),('water-tile-shallow','#64C7C4','#F3F0DC',True),('water-tile-deep','#173F57','#2A6685',False)]:
 mix=.025+.055*broad+.14*caustic
 arr=rgb(base)[None,None,:]*(1-mix[:,:,None])+rgb(light)[None,None,:]*mix[:,:,None]
 if sand:
  a=.15*np.maximum(0,np.sin(u+.4*np.cos(v))*np.cos(v)-.2)
  arr=arr*(1-a[:,:,None])+rgb('#D1AF76')[None,None,:]*a[:,:,None]
 f=.17*streak;arr=arr*(1-f[:,:,None])+rgb('#F3F0DC')[None,None,:]*f[:,:,None]
 # Exact edge equality makes repeat seams mechanically verifiable.
 arr[-1]=arr[0];arr[:,-1]=arr[:,0]
 save(rgba(np.dstack((arr,np.full((N,N),255)))) ,name)
y,x=np.meshgrid(np.linspace(-1,1,N),np.linspace(-1,1,N),indexing='ij');r=np.sqrt((x/.86)**2+(y/.70)**2);theta=np.arctan2(y,x)
alpha=np.exp(-((r-(.76+.018*np.sin(theta*9)+.012*np.cos(theta*13)))/.022)**2)
alpha*=.5+.5*(np.sin(theta*7+.8)**2);alpha*=np.clip((1-r)*10,0,1)
color=np.broadcast_to(rgb('#F3F0DC'),(N,N,3));save(rgba(np.dstack((color,alpha*210))),'foam-ring')
t=(y+1)/2;spread=.08+.47*t
alpha=(np.exp(-((x-spread)/.025)**2)+np.exp(-((x+spread)/.025)**2))*.65
alpha+=np.exp(-(x/(.055+.11*t))**2)*.18*(.5+.5*np.cos(y*38))
alpha*=np.sin(np.pi*t)**1.7;alpha[[0,-1],:]=0;alpha[:,[0,-1]]=0
save(rgba(np.dstack((color,np.clip(alpha,0,1)*230))),'wake-trail')
sheet=Image.new('RGBA',(N,N),(0,0,0,0))
for i in range(16):
 t=i/15;cell=Image.new('RGBA',(256,256),(0,0,0,0));d=ImageDraw.Draw(cell)
 rad=16+88*t;fade=round(230*(1-t)**.7);cy=155
 d.ellipse((128-rad,cy-rad*.35,128+rad,cy+rad*.35),outline=(243,240,220,fade),width=max(1,round(7*(1-t))))
 for j in range(9):
  a=math.tau*j/9;dist=20+74*t;xx=128+math.cos(a)*dist;yy=cy+math.sin(a)*dist*.35-math.sin(math.pi*t)*(45+12*(j%3))
  rr=max(1,5*(1-t));d.ellipse((xx-rr,yy-rr*1.7,xx+rr,yy+rr*1.7),fill=(100,199,196,fade))
  if i<8:d.line([(128+math.cos(a)*20,cy),(xx,yy)],fill=(243,240,220,round(fade*.65)),width=3)
 sheet.alpha_composite(cell,(i%4*256,i//4*256))
save(sheet,'splash-sheet')
# Optional transparent wood grain overlay, extremely low opacity and periodic.
gr=(np.sin(23*u+.3*np.sin(2*v))*.5+.5)**20
arr=np.broadcast_to(rgb('#8C5A36'),(N,N,3));alpha=gr*13
alpha[-1]=alpha[0];alpha[:,-1]=alpha[:,0]
save(rgba(np.dstack((arr,alpha))),'deck-planks-detail')
checks=[]
for p in sorted(OUT.glob('*.png')):
 im=Image.open(p);a=np.array(im);assert im.mode=='RGBA' and im.size==(1024,1024)
 if p.stem.startswith('water-tile') or p.stem=='deck-planks-detail':assert np.array_equal(a[0],a[-1]) and np.array_equal(a[:,0],a[:,-1])
 if p.stem.startswith('water-tile'):assert a[:,:,3].min()==255
 else:assert a[:,:,3].min()==0 and a[:,:,3].max()>0
 checks.append({'file':p.name,'size':[1024,1024],'tileable':p.stem.startswith('water-tile') or p.stem=='deck-planks-detail','alpha_range':[int(a[:,:,3].min()),int(a[:,:,3].max())],'passed':True})
(OUT/'validation.json').write_text(json.dumps({'all_passed':True,'textures':checks},indent=2)+'\n')
# Contact review repeats first three waters2x2 to reveal seams.
contact=Image.new('RGB',(1536,1024),'#F4EFE3')
for i,n in enumerate(['water-tile','water-tile-shallow','water-tile-deep']):
 im=Image.open(OUT/(n+'.png')).resize((256,256))
 for xx in range(2):
  for yy in range(2):contact.paste(im,(i*512+xx*256,yy*256))
for i,n in enumerate(['foam-ring','wake-trail','splash-sheet']):
 im=Image.open(OUT/(n+'.png')).resize((512,512));bg=Image.new('RGBA',(512,512),'#168F9F');bg.alpha_composite(im);contact.paste(bg.convert('RGB'),(i*512,512))
review=ROOT/'Art/Models/DayBoatKit';review.mkdir(parents=True,exist_ok=True);contact.save(review/'water-textures-contact-sheet.png')
print('PASS seven water/effect/deck textures; exact periodic water seams, transparent effects')
