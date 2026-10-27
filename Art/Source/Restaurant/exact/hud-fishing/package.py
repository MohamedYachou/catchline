"""HUD-V3-CUT-1 deterministic source cuts, text separation, metadata and proofs.
Dependencies Pillow, numpy, opencv-python-headless. No game/runtime code.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np, cv2, json, hashlib, math
P=Path(__file__).resolve().parent;EX=P.parent;ART=EX.parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
FONT=ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
SCALE=844/1920

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(ROOT).as_posix()
def rectbox(r):x,y,w,h=r;return (x,y,x+w,y+h)
def matte(im,mode='panel'):
 a=np.array(im.convert('RGB'));h,w=a.shape[:2]
 if mode=='panel':
  mask=Image.new('L',(w,h));ImageDraw.Draw(mask).rounded_rectangle((1,1,w-2,h-2),radius=min(32,min(w,h)//3),fill=255);out=im.convert('RGBA');out.putalpha(mask);return out
 if mode=='cream':
  hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV);cream=(a[:,:,0]>150)&(a[:,:,1]>135)&(a[:,:,2]>100)&(hsv[:,:,1]<100);n,cc,stats,_=cv2.connectedComponentsWithStats(cream.astype('uint8'));edge=set(cc[0,:])|set(cc[-1,:])|set(cc[:,0])|set(cc[:,-1]);outside=np.isin(cc,list(edge-{0}));out=im.convert('RGBA');out.putalpha(Image.fromarray(np.where(outside,0,255).astype('uint8')));return out
 m=np.full((h,w),cv2.GC_PR_FGD,np.uint8)
 m[:2,:]=m[-2:,:]=cv2.GC_BGD;m[:,:2]=m[:,-2:]=cv2.GC_BGD
 if mode in ['icon','portrait']:
  hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV)
  cream=(a[:,:,0]>160)&(a[:,:,1]>140)&(a[:,:,2]>100)&(hsv[:,:,1]<100)
  n,cc,stats,_=cv2.connectedComponentsWithStats(cream.astype('uint8'));edge=set(cc[0,:])|set(cc[-1,:])|set(cc[:,0])|set(cc[:,-1]);outside=np.isin(cc,list(edge-{0}));m[outside]=cv2.GC_PR_BGD
  good=((hsv[:,:,1]>100)|(a.min(axis=2)<90));m[good]=cv2.GC_PR_FGD
 else:
  pad=min(8,max(3,min(h,w)//8));m[pad:h-pad,pad:w-pad]=cv2.GC_FGD
 if mode in ['icon','portrait']:
  teal=(a[:,:,1]>125)&(a[:,:,2]>110)&(a[:,:,0]*1.35<a[:,:,1]);
  if mode=='portrait':
   n,cc,stats,_=cv2.connectedComponentsWithStats(teal.astype('uint8'));edge=set(cc[0,:])|set(cc[-1,:])|set(cc[:,0])|set(cc[:,-1]);m[np.isin(cc,list(edge-{0}))]=cv2.GC_BGD
  if mode=='portrait':
   m[15:30,45:80]=cv2.GC_FGD
   m[44:78,116:]=cv2.GC_BGD
   m[-4:,:]=cv2.GC_BGD
   m[h-24:h-8,45:100]=cv2.GC_FGD
  if h<65 and w<80:m[h//5:2*h//5,w//4:3*w//4]=cv2.GC_PR_FGD
 m[:2,:]=m[-2:,:]=cv2.GC_BGD;m[:,:2]=m[:,-2:]=cv2.GC_BGD
 cv2.setRNGSeed(42);cv2.grabCut(a,m,None,np.zeros((1,65)),np.zeros((1,65)),5,cv2.GC_INIT_WITH_MASK)
 mask=np.where((m==cv2.GC_FGD)|(m==cv2.GC_PR_FGD),255,0).astype('uint8')
 # Keep meaningful islands, discard disconnected one-pixel matte debris.
 n,labels,stats,_=cv2.connectedComponentsWithStats(mask)
 for i in range(1,n):
  if stats[i,cv2.CC_STAT_AREA]<max(3,w*h*.00012):mask[labels==i]=0
 out=im.convert('RGBA');out.putalpha(Image.fromarray(mask));return out

def nine(im,size,b):
 if not b:return im.resize(size,Image.Resampling.LANCZOS)
 l,bot,r,t=b;w,h=im.size;dw,dh=size
 if dw<l+r or dh<t+bot:return im.resize(size,Image.Resampling.LANCZOS)
 out=Image.new('RGBA',size);xs=[0,l,w-r,w];ys=[0,t,h-bot,h];dx=[0,l,dw-r,dw];dy=[0,t,dh-bot,dh]
 for j in range(3):
  for i in range(3):out.alpha_composite(im.crop((xs[i],ys[j],xs[i+1],ys[j+1])).resize((dx[i+1]-dx[i],dy[j+1]-dy[j]),Image.Resampling.LANCZOS),(dx[i],dy[j]))
 return out

class Pack:
 def __init__(self,kind):
  self.kind=kind;self.p=EX/('hud-'+kind);self.p.mkdir(exist_ok=True);self.src=ART/'concepts'/('ui-v3-'+('17' if kind=='fishing' else '18')+'-hud-'+kind+'.png');self.im=Image.open(self.src).convert('RGBA');self.donor=Image.open(self.p/'provenance/textless-tool-result.png').convert('RGBA');self.es=[];self.uses=[];self.text=[]
  self.texture=self.donor.crop((210,205,350,285)) if kind=='fishing' else self.donor.crop((145,128,350,167))
 def cut(self,id,r,mode='icon',blank=False,borders=None,patch=None):
  a=matte(self.im.crop(rectbox(r)),mode)
  if blank:
   if id=='shop-row':
    right=a.crop((a.width//2,0,a.width,a.height));rebuilt=Image.new('RGBA',(right.width*2,right.height));rebuilt.alpha_composite(right.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(0,0));rebuilt.alpha_composite(right,(right.width,0));a=rebuilt.resize(a.size)
   pad=12 if min(a.size)>130 else 13
   inset=(pad,pad,a.width-pad,a.height-pad)
   alpha=a.getchannel('A');a.paste(self.texture.resize((inset[2]-inset[0],inset[3]-inset[1]),Image.Resampling.LANCZOS),inset[:2]);a.putalpha(alpha)
  if patch:
   for box in patch:
    x,y,w,h=box;a.paste(self.texture.resize((w,h),Image.Resampling.LANCZOS),(x,y))
  return self.export(id,a,r,borders,method='original concept crop and foreground matte'+('; blank centre from textless built-in ImageGen cream donor; original rim retained' if blank else ''))
 def export(self,id,a,r,borders=None,method='direct cut',source=None):
  bb=a.getchannel('A').getbbox();assert bb,id;originalRect=list(r);aw,ah=a.size;a=a.crop(bb)
  r=[round(r[0]+bb[0]*r[2]/aw),round(r[1]+bb[1]*r[3]/ah),round((bb[2]-bb[0])*r[2]/aw),round((bb[3]-bb[1])*r[3]/ah)]
  logical=[max(1,round(r[2]*SCALE)),max(1,round(r[3]*SCALE))];size=[v*3 for v in logical]
  a=a.resize(size,Image.Resampling.LANCZOS);a.putalpha(a.getchannel('A').point(lambda v:v if v>=8 else 0));bbox=a.getchannel('A').getbbox();a=a.crop(bbox).resize(size,Image.Resampling.LANCZOS)
  name='v3-hud-'+self.kind+'-'+id;f=self.p/(name+'.png');a.save(f)
  b=[max(3,round(v*SCALE*3)) for v in borders] if borders else None
  e=dict(name=name,file=f.name,logicalSize=logical,size=size,borders=b,border_order='left,bottom,right,top',sourceRect=r,registrationRect=originalRect,sha256=sha(f),provenance=dict(source=rel(source or self.src),sourceSha256=sha(source or self.src),method=method),native3xDetailClaim=False)
  self.es.append(e);return name
 def reuse(self,id,path,r,borders=None):
  p=EX/path;im=Image.open(p);name='v3-hud-'+self.kind+'-'+id
  self.es.append(dict(name=name,external=rel(p),sha256=sha(p),size=list(im.size),logicalSize=[v/3 for v in im.size],sourceRect=r,borders=borders,border_order='left,bottom,right,top',reuse=True));return name
 def use(self,n,r,role=None,z=10):
  e=next(e for e in self.es if e['name']==n);rr=e.get('registrationRect',r);sr=e['sourceRect']
  if e.get('registrationRect'):r=[round(r[0]+(sr[0]-rr[0])*r[2]/rr[2]),round(r[1]+(sr[1]-rr[1])*r[3]/rr[3]),round(sr[2]*r[2]/rr[2]),round(sr[3]*r[3]/rr[3])]
  self.uses.append(dict(name=n,sourceRect=r,use=role or n,z=z))
 def label(self,id,text,r,size,align='left',colour='#112D52',weight='Bold'):
  self.text.append(dict(id=id,text=text,sourceRect=r,sourceFontSize=size,font='Fredoka',weight=weight,align=align,colour=colour,live=True))
 def base(self,id,r,borders=[24,24,24,24]):
  if id.startswith('crew-'):
   a=matte(self.im.crop(rectbox(r)),'panel');right=a.crop((a.width//2,0,a.width,a.height));a=Image.new('RGBA',(right.width*2,right.height));a.alpha_composite(right.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(0,0));a.alpha_composite(right,(right.width,0));alpha=a.getchannel('A');a.paste(self.texture.resize((a.width-38,a.height-30)),(19,15));a.putalpha(alpha);n=self.export(id,a,r,borders,method='original strip right cap mirrored to restore rim occluded by portrait; textless cream interior')
  else:n=self.cut(id,r,'panel',True,borders)
  self.use(n,r,z=1);return n
 def icon(self,id,r):n=self.cut(id,r);self.use(n,r,z=20);return n
 def finish(self):
  screens=[];texts=[];fit=[]
  for sc,canvas in [('phone',[844,390]),('desktop',[1440,900])]:
   sx=canvas[0]/1920;sy=canvas[1]/1080
   def conv(r):return [round(r[0]*sx),round(r[1]*sy),max(1,round(r[2]*sx)),max(1,round(r[3]*sy))]
   ps=[dict(name=u['name'],rect=conv(u['sourceRect']),use=u['use'],z=u['z']) for u in self.uses]
   screen=dict(screen=sc,canvas=canvas,concept=rel(self.src),sourceCanvas=[1920,1080],placements=ps,coordinateSpace='top-left device pixels',adaptation='Measured source boxes mapped independently to requested frame axes; preserves concept composition. Device layouts are source proposals, not native captures.')
   screens.append(screen)
   im=self.im.resize((canvas[0]*3,canvas[1]*3),Image.Resampling.LANCZOS)
   for u in sorted(ps,key=lambda u:u['z']):
    e=next(e for e in self.es if e['name']==u['name']);p=ROOT/e['external'] if e.get('external') else self.p/e['file'];a=Image.open(p).convert('RGBA');x,y,w,h=u['rect'];im.alpha_composite(nine(a,(w*3,h*3),e['borders']),(x*3,y*3))
   for t in self.text:
    t=dict(t,screen=sc,rect=conv(t['sourceRect']),fontSize=max(7,round(t['sourceFontSize']*min(sx,sy))),lineHeight=max(8,round(t['sourceFontSize']*min(sx,sy)*1.12)))
    texts.append(t);x,y,w,h=t['rect'];d=ImageDraw.Draw(im);font=ImageFont.truetype(str(FONT),t['fontSize']*3);bb=d.textbbox((0,0),t['text'],font=font,stroke_width=0);tw=bb[2]-bb[0];th=bb[3]-bb[1]
    tx=x*3+(w*3-tw)/2 if t['align']=='center' else (x+w)*3-tw if t['align']=='right' else x*3
    d.text((tx,y*3+(h*3-th)/2-bb[1]),t['text'],font=font,fill=t['colour'],stroke_width=1,stroke_fill='#FFF7E7' if t['colour']!='#FFF4DC' else '#A04416')
    fit.append(dict(id=t['id'],screen=sc,rect=t['rect'],textSize=[round(tw/3,2),round(th/3,2)],fits=tw<=w*3 and th<=h*3))
   im.save(self.p/(sc+'-reconstructed-3x.png'));im.resize(tuple(canvas),Image.Resampling.LANCZOS).convert('RGB').save(self.p/(sc+'-actual-size.jpg'),quality=97)
   side=Image.new('RGB',(canvas[0]*2,canvas[1]+28),'#EAE3D4');side.paste(self.im.resize(tuple(canvas)),(0,28));side.paste(im.resize(tuple(canvas)).convert('RGB'),(canvas[0],28));dd=ImageDraw.Draw(side);font=ImageFont.truetype(str(FONT),13);dd.text((8,4),'Concept / proportional frame mapping',font=font,fill='#173F57');dd.text((canvas[0]+8,4),'Cut reconstruction / live sample labels',font=font,fill='#173F57');side.save(self.p/(sc+'-comparison.jpg'),quality=97)
  dump(self.p/'manifest.json',self.es);dump(self.p/'layout.json',screens);dump(self.p/'text-styles.json',texts);dump(self.p/'text-measurements.json',fit);dump(self.p/'slices.json',[e for e in self.es if e['borders']])
  # Contact at phone reference size, clean art with no live labels baked into PNG.
  rows=[max(70,round(e['sourceRect'][3]*SCALE)+35) for e in self.es];out=Image.new('RGB',(850,sum(rows)+10),'#D9D4C8');d=ImageDraw.Draw(out);y=5;f=ImageFont.truetype(str(FONT),12)
  for e,rh in zip(self.es,rows):
   p=ROOT/e['external'] if e.get('external') else self.p/e['file'];a=Image.open(p).convert('RGBA');w,h=[round(v*SCALE) for v in e['sourceRect'][2:]];a=nine(a,(max(1,w)*3,max(1,h)*3),e['borders']).resize((max(1,w),max(1,h)),Image.Resampling.LANCZOS)
   d.text((10,y),e['name']+(' (reuse)' if e.get('reuse') else ''),font=f,fill='#173F57');out.paste(a,(10,y+22),a);y+=rh
  out.save(self.p/'contact-actual-size.jpg',quality=97)
  print(self.kind,len(self.es),'pieces',len(self.uses),'uses',len(self.text),'labels',sum(not f['fits'] for f in fit),'text fit failures')

def fishing():
 k=Pack('fishing')
 k.base('status-panel',[33,25,519,381],[30,30,30,30])
 k.label('location','Harbour mouth',[74,45,430,45],43)
 for id,r in [('cooler',[70,102,48,47]),('food',[71,152,48,44]),('bait',[70,198,51,42]),('rod',[70,243,50,44]),('fish',[71,294,50,37]),('goal',[72,338,46,47])]:k.icon('status-'+id,r)
 for id,txt,r,sz in [('cooler','Cooler 6/10',[139,108,171,34],28),('food','Food  4.2 min',[139,155,174,35],28),('bait','Bait 12   ·   Stocks 79%',[139,203,363,34],28),('rod','Rod 1: BITE!    Rod 2: ready',[139,250,375,34],27),('fish','Mackerel  3/8   ·   2 voyages',[139,297,380,34],27),('goal','Deliver fresh fish at harbour',[139,345,376,34],26)]:k.label('status-'+id,txt,r,sz)
 # Dynamic gauges: unfilled right track cap mirrored to a symmetric track;
 # original coloured fill caps retained independently, no sample fraction baked in backing.
 a=matte(k.im.crop((434,112,513,140)),'panel');right=a.crop((a.width//2,0,a.width,a.height));left=right.transpose(Image.Transpose.FLIP_LEFT_RIGHT);track=Image.new('RGBA',(right.width*2,right.height));track.alpha_composite(left,(0,0));track.alpha_composite(right,(right.width,0))
 n=k.export('meter-track',track,[318,111,196,30],[15,10,15,10],method='unfilled concept track right cap, mirrored to opposite cap; independent dynamic track')
 for id,r,fr in [('cooler',[318,111,196,30],[320,114,111,24]),('food',[318,159,196,29],[320,162,133,23])]:
  k.use(n,r,role=id+'-track');a=matte(k.im.crop(rectbox(fr)),'panel');f=k.export('meter-'+id+'-fill',a,fr,[12,8,12,8]);k.use(f,fr,role=id+'-sample-fill',z=15)
 # Wallet and action backing reuse existing accepted restaurant kit; no duplicate PNG.
 n=k.reuse('wallet','s1-s2/v2-wallet-pill.png',[1584,19,315,83],[30,27,30,27]);k.use(n,[1584,19,315,83]);k.icon('wallet-coin',[1583,19,81,80]);k.label('coins','380 coins',[1672,37,207,49],40,'center','#FFF4DC')
 n=k.base('home-button',[1584,111,316,91],[28,25,28,25]);k.icon('home-anchor',[1602,119,67,66]);k.label('home','Head home',[1678,133,199,47],38,'center')
 for id,r,ic,txt,tr in [('fish',[634,300,181,103],[653,309,49,55],'Fish',[714,317,82,44]),('carry',[1095,481,199,106],[1112,497,57,41],'Carry',[1172,501,108,43])]:
  a=k.im.crop(rectbox(r)).convert('RGBA');w,h=a.size;mask=Image.new('L',(w,h));d=ImageDraw.Draw(mask);d.rounded_rectangle((1,1,w-2,75),radius=34,fill=255);d.polygon([(w//2-22,67),(w//2,101),(w//2+23,67)],fill=255);a.paste(k.texture.resize((w-36,51)),(18,12));a.putalpha(mask);n=k.export('bubble-'+id,a,r,None,method='original pointed bubble frame; measured rounded body and pointer matte; textless cream interior');k.use(n,r);k.icon(id+'-icon',ic);k.label('action-'+id,txt,tr,38,'center')
 for id,r,portrait,tx1,tx2 in [('captain',[32,803,514,107],[43,755,136,149],'Captain (you)','Watching rod 1'),('sam',[32,933,514,109],[43,902,136,134],'Sam · 2 voyages left','Baiting rod 2')]:
  k.base('crew-'+id+'-card',r,[34,24,34,24]);n=k.cut('crew-'+id+'-portrait',portrait,'portrait');k.use(n,portrait,z=20);k.label(id+'-name',tx1,[190,r[1]+16,333,39],32);k.label(id+'-task',tx2,[190,r[1]+57,333,29],26)
 # Strike panel: exact original frame, original water art cropped as separate non-stretching illustration.
 k.base('strike-panel',[600,732,721,317],[35,35,35,35]);k.label('strike-title','The bobber is under!',[672,752,578,48],43,'center')
 # Illustration donor removes TAP and footer labels; keep the concept's bobber identity as a fixed illustration.
 a=k.donor.crop((529,658,1185,852));n=k.export('strike-water',a,[616,798,690,185],method='textless built-in ImageGen water/bobber illustration cleanup');k.use(n,[616,798,690,185],z=12)
 k.label('strike-tap','TAP!',[1106,855,130,58],50,'center');k.label('strike-help','Tap anywhere now',[792,945,341,39],31,'center')
 # Dynamic red timer uses accepted restaurant meter primitives, no filled fraction baked.
 for id,path,r in [('strike-track','s3-s5/v2-bar-track.png',[669,990,581,32])]:n=k.reuse(id,path,r,[15,12,15,12]);k.use(n,r,z=15)
 n=k.cut('strike-timer-fill',[670,990,386,30],'panel',borders=[15,10,15,10]);k.use(n,[670,990,386,30],z=16)
 k.finish()

if __name__=='__main__':fishing()
