"""Requested mechanical packaging/composition; paintings from built-in ImageGen, kit unchanged."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib,sys
R=Path(__file__).resolve().parents[6]
# Resolve checkout by marker instead of relying on path depth.
R=next(p for p in Path(__file__).resolve().parents if (p/'Assets').exists())
P=R/'Art/Source/Restaurant/exact/s11';D=P/'later-stages'
fontpath=R/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
baseline=json.loads((P/'spec.json').read_text(encoding='utf-8'))
for stage in [3,4]:
 O=D/f'stage{stage}';O.mkdir(exist_ok=True)
 prefix=f'v2-s11-stage{stage}-'
 s=json.loads(json.dumps(baseline))
 # No edits to accepted Bistro spec/assets.
 s['variant']=stage;s['concept']=f'ui-11-stage{stage}-preview.png'
 for p in s['pieces']:
  if p['id']=='illustration':p.pop('sourceBox',None);p.pop('atlas',None);p['copy']=str((D/'provenance'/f'stage{stage}.png').relative_to(R))
  elif p['id']=='unlock-1' and stage==3:p['copy']='Art/Source/Restaurant/exact/s10/v2-s10-task-seat.png'
  elif p['id']=='unlock-2' and stage==4:p['copy']='Art/Source/Restaurant/exact/s10/v2-s10-order-grilled-fish.png'
 names={3:'Restaurant',4:'Seafood house'}
 changes={3:{'title':'Welcome to the Restaurant!','stage':'Bistro > Restaurant','reward':'A room to grow!','unlock-0':'12 x 5 floor plan','unlock-1':'Booths for six','unlock-2':'Joined next-door house'},
          4:{'title':'Welcome to the Seafood house!','stage':'Restaurant > Seafood house','reward':'Our harbour landmark!','unlock-0':'14 x 5 floor plan','unlock-1':'5 x 5 kitchen','unlock-2':'Landmark fish sign'}}
 for t in s['texts']:
  if t[0] in changes[stage]:t[1]=changes[stage][t[0]]
  if t[0]=='title':t[2]=[215,13,422,33];t[3]=27
  if t[0]=='stage':t[2]=[443,86,336,26];t[3]=23
  if t[0]=='reward':t[3]=24
 # Painted sign intentionally blank. Floating live label is separate on illustration, measured after painting.
 sign=json.loads((D/'sign-rects.json').read_text())[str(stage)]
 s['texts'].append(['building-sign',names[stage],sign,12,'#FFF8DE'])
 placements=[];manifest=[]
 im=Image.new('RGBA',(2532,1170))
 for p in sorted(s['pieces'],key=lambda p:p.get('z',20)):
  name=prefix+p['id'];src=R/p['copy'];a=Image.open(src).convert('RGBA')
  a.putalpha(a.getchannel('A').point(lambda x:x if x>=24 else 0));box=a.getchannel('A').getbbox();assert box
  a=a.crop(box);x,y,w,h=p['rect'];a=a.resize((w*3,h*3),Image.Resampling.LANCZOS)
  for _ in range(5):
   a.putalpha(a.getchannel('A').point(lambda x:x if x>=24 else 0));b=a.getchannel('A').getbbox()
   if b==(0,0,*a.size):break
   a=a.crop(b).resize((w*3,h*3),Image.Resampling.LANCZOS)
  assert a.getchannel('A').getbbox()==(0,0,*a.size)
  file=P/(name+'.png');a.save(file,optimize=True)
  place=dict(name=name,screen=11,variant=stage,use='primary',rect=p['rect'],z=p.get('z',20));placements.append(place)
  borders=[v*3 for v in p['slice']] if 'slice' in p else None
  manifest.append(dict(name=name,file=file.name,rect=p['rect'],size=a.size,borders=borders,border_order='left,bottom,right,top',source=str(src.relative_to(R)),sourceSha256=sha(src),sha256=sha(file),native3xDetailClaim=False))
  im.alpha_composite(a,(x*3,y*3))
 styles=[];d=ImageDraw.Draw(im)
 for ident,value,rect,size,fill in s['texts']:
  x,y,w,h=rect;sw=1 if fill=='#FFF8DE' else 0
  for n in range(size,0,-1):
   f=ImageFont.truetype(str(fontpath),n*3);b=d.textbbox((0,0),value,font=f,stroke_width=sw*3)
   if b[2]-b[0]<=w*3 and b[3]-b[1]<=h*3:break
  t=dict(id=ident,screen=11,variant=stage,text=value,rect=rect,font='Fredoka Bold',weight=700,size=n,fill=fill,stroke='#10263D',stroke_width=sw,align='left',shadow=[0,0,'#00000000'])
  styles.append(t);d.text((x*3-b[0],y*3+(h*3-b[3]+b[1])//2-b[1]),value,font=f,fill=fill,stroke_width=sw*3,stroke_fill='#10263D')
 im.save(O/'reconstructed-3x.png',optimize=True)
 im.resize((844,390),Image.Resampling.LANCZOS).save(O/s['concept'])
 dump(O/'spec.json',s);dump(O/'manifest.json',manifest);dump(O/'layout.json',dict(screen=11,variant=stage,canvas=[844,390],origin='top-left',assetRoot='../..',placements=placements))
 dump(O/'text-styles.json',dict(screen=11,variant=stage,canvas=[844,390],styles=styles))
 dump(O/'slices.json',[m for m in manifest if m['borders']])
 # Contact: original generator painting vs export, all reusable cuts on checker.
 contact=Image.new('RGB',(1440,900),'#F4EFE3');dd=ImageDraw.Draw(contact);f=ImageFont.truetype(str(fontpath),18)
 for i,m in enumerate(manifest):
  x=i%4*360;y=i//4*300;dd.text((x+6,y+5),m['name'],font=f,fill='#173F57')
  for yy in range(y+35,y+265,12):
   for xx in range(x+6,x+350,12):dd.rectangle((xx,yy,xx+11,yy+11),fill=['#B9C7CC','#E0E6E4'][((xx-x)//12+(yy-y)//12)%2])
  a=ImageOps.contain(Image.open(P/m['file']),(330,220));contact.paste(a,(x+15+(330-a.width)//2,y+40+(220-a.height)//2),a)
 contact.save(O/'cuts-review.jpg',quality=94)
 measure=im.resize((1688,780)).convert('RGB');dd=ImageDraw.Draw(measure)
 for i,t in enumerate(styles):
  x,y,w,h=t['rect'];dd.rectangle((x*2,y*2,(x+w)*2,(y+h)*2),outline='#FF0088',width=2);dd.text((x*2,y*2),str(i+1),font=f,fill='#168F9F')
 measure.save(O/'text-measure.jpg',quality=94)
 dump(O/'audit.json',dict(complete=True,sprites=len(manifest),textEntries=len(styles),tightRGBA3x=True,hashes={m['file']:m['sha256'] for m in manifest},visualReview='PENDING actual opens'))
 print('stage',stage,len(manifest),'sprites',len(styles),'texts')

