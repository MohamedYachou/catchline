"""Mechanical requested crops, nine-slice assembly and live text; no generated painting by Python."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
import json,hashlib
P=Path(__file__).resolve().parent;R=next(p for p in P.parents if (p/'Assets').exists());A=R/'Art/Source/Restaurant'
FONT=R/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def tight(a):
 a=a.convert('RGBA');a.putalpha(a.getchannel('A').point(lambda n:n if n>=24 else 0));return a.crop(a.getchannel('A').getbbox())
def sliced(a,size,borders):
 # Source borders measured as fractions of the tight source; destination borders in logical pixels.
 w,h=size;l,b,r,t=borders;sw,sh=a.size
 sx=[0,round(sw*l/(l+r+110)),sw-round(sw*r/(l+r+110)),sw]
 sy=[0,round(sh*t/(t+b+48)),sh-round(sh*b/(t+b+48)),sh]
 dx=[0,l*3,w-r*3,w];dy=[0,t*3,h-b*3,h]
 out=Image.new('RGBA',size)
 for yi in range(3):
  for xi in range(3):out.alpha_composite(a.crop((sx[xi],sy[yi],sx[xi+1],sy[yi+1])).resize((dx[xi+1]-dx[xi],dy[yi+1]-dy[yi]),Image.Resampling.LANCZOS),(dx[xi],dy[yi]))
 return out
pieces=[];places=[];texts=[];cache={}
def piece(ident,source,size,borders=None,box=None):
 src=A/source;a=Image.open(src).convert('RGBA')
 if box:a=a.crop(box)
 a=tight(a);size=tuple(v*3 for v in size)
 a=sliced(a,size,borders) if borders else a.resize(size,Image.Resampling.LANCZOS)
 for _ in range(5):
  a=tight(a)
  if a.size==size:break
  a=a.resize(size,Image.Resampling.LANCZOS)
 assert a.size==size and a.getchannel('A').getbbox()==(0,0,*size)
 name='v2-s13-'+ident;file=P/(name+'.png');a.save(file,optimize=True);cache[ident]=a
 pieces.append(dict(name=name,file=file.name,logicalSize=[v//3 for v in size],size=size,borders=[v*3 for v in borders] if borders else None,border_order='left,bottom,right,top',source=str(src.relative_to(R)),sourceBox=box,sourceSha256=sha(src),sha256=sha(file),native3xDetailClaim=False))
def place(ident,use,rect,z):places.append(dict(name='v2-s13-'+ident,use=use,screen=13,rect=rect,z=z))
def text(ident,value,rect,size,colour='#10263D',align='left'):texts.append(dict(id=ident,screen=13,text=value,rect=rect,size=size,font='Fredoka Bold',weight=700,fill=colour,align=align,stroke_width=1 if colour=='#FFF8DE' else 0,stroke='#10263D'))
piece('background','exact/s9/v2-s9-background.png',(844,390));place('background','sheet',[0,0,844,390],0)
piece('title-sign','exact/s8/v2-s8-title-sign.png',(494,45),[70,12,80,12]);place('title-sign','sheet',[175,4,494,45],5)
text('title','Your first night with Mira',[251,12,360,27],25,'#FFF8DE')
piece('frame','exact/s3-s5/v2-plan-paper.png',(400,151),[18,13,18,17])
piece('service-room','concepts/ui-2-service.png',(386,137),box=[164,54,650,226])
piece('closing-room','exact/s13/provenance/closing-room.png',(386,137),box=[850,240,2048,665])
piece('speech-bubble','exact/s3-s5/v2-bubble-mira.png',(292,54),[16,16,38,16])
piece('mira-host','clothes/2d/mira-d-bust.png',(66,81))
piece('step-label','exact/s3-s5/v2-summary-strip.png',(262,25),[10,8,10,8])
piece('pointer','exact/s13/provenance/pointer.png',(29,29))
frames=[('seat','Seat the guests',"Tap a table to welcome\nour first guests.",(14,59),(260,39)),('cook','The kitchen cooks',"Our cooks turn today's\ncatch into dinner.",(430,59),(99,37)),('serve','Serve',"Take the hot plates\nto their table.",(14,224),(113,42)),('close','Close up',"Last guests gone? Let's\ncount tonight's takings.",(430,224),(295,28))]
for i,(ident,title,line,(x,y),(px,py)) in enumerate(frames,1):
 place('frame',ident,[x,y,400,151],5);place('closing-room' if ident=='close' else 'service-room',ident,[x+7,y+7,386,137],10)
 place('step-label',ident,[x+13,y+10,262,25],20);text(ident+'-title',f'{i}  {title}',[x+24,y+12,240,21],18)
 place('pointer',ident,[x+px,y+py,29,29],25)
 place('speech-bubble',ident,[x+13,y+88,292,54],30);text(ident+'-line',line,[x+25,y+96,249,36],16)
 place('mira-host',ident,[x+317,y+63,66,81],35)
im=Image.new('RGBA',(2532,1170))
for p in sorted(places,key=lambda p:p['z']):
 a=cache[p['name'].removeprefix('v2-s13-')];im.alpha_composite(a,(p['rect'][0]*3,p['rect'][1]*3))
d=ImageDraw.Draw(im)
for t in texts:
 x,y,w,h=t['rect'];sw=t['stroke_width']*3
 for n in range(t['size'],0,-1):
  f=ImageFont.truetype(str(FONT),n*3);b=d.multiline_textbbox((0,0),t['text'],font=f,spacing=2*3,stroke_width=sw)
  if b[2]-b[0]<=w*3 and b[3]-b[1]<=h*3:break
 t['size']=n;t['spacing']=2;t['measuredInkSize']=[round((b[2]-b[0])/3,2),round((b[3]-b[1])/3,2)]
 d.multiline_text((x*3-b[0],y*3+(h*3-b[3]+b[1])//2-b[1]),t['text'],font=f,fill=t['fill'],stroke_width=sw,stroke_fill=t['stroke'],spacing=6)
im.save(P/'reconstructed-3x.png',optimize=True)
im.resize((844,390),Image.Resampling.LANCZOS).save(A/'concepts/ui-13-first-night.png')
dump(P/'manifest.json',pieces);dump(P/'layout.json',dict(screen=13,canvas=[844,390],origin='top-left',placements=places));dump(P/'text-styles.json',dict(screen=13,canvas=[844,390],styles=texts));dump(P/'slices.json',[m for m in pieces if m['borders']]);dump(P/'spec.json',dict(screen=13,frames=[dict(id=z[0],title=z[1],coaching=z[2],origin=z[3],pointerOffset=z[4]) for z in frames],background='ui-2-service.png',model='illustrative coaching sheet, not runtime'))
contact=Image.new('RGB',(1440,900),'#F4EFE3');dd=ImageDraw.Draw(contact);f=ImageFont.truetype(str(FONT),20)
for i,m in enumerate(pieces):
 x=i%3*480;y=i//3*300;dd.text((x+7,y+5),m['name'],font=f,fill='#10263D')
 for yy in range(y+35,y+285,12):
  for xx in range(x+6,x+474,12):dd.rectangle((xx,yy,xx+11,yy+11),fill=['#CBD4D5','#EEF0E8'][((xx-x)//12+(yy-y)//12)%2])
 a=ImageOps.contain(Image.open(P/m['file']),(450,230));contact.paste(a,(x+15+(450-a.width)//2,y+43+(230-a.height)//2),a)
contact.save(P/'cuts-review.jpg',quality=94)
measure=im.resize((1688,780)).convert('RGB');dd=ImageDraw.Draw(measure)
for i,t in enumerate(texts):
 x,y,w,h=t['rect'];dd.rectangle((x*2,y*2,(x+w)*2,(y+h)*2),outline='#FF00AA',width=2)
measure.save(P/'text-measure.jpg',quality=94)
print(len(pieces),'sprites',len(places),'placements',len(texts),'texts')
