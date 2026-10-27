"""ART-5 source-art packaging only. Run A, B, C; then audit_delivery.py."""
from pathlib import Path
import importlib.util,json,hashlib,math,sys,random
from PIL import Image,ImageDraw,ImageFont,ImageOps
P=Path(__file__).resolve().parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
EX=ROOT/'Art/Source/Restaurant/exact';ART=EX.parent
B=EX/'s7/states';C=EX/'s11/celebrate'
spec=importlib.util.spec_from_file_location('kit',EX/'s2-call/package.py')
k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)

def source(folder,id):return folder/'provenance'/(id+'.png')
def export(folder,name,id,cap=None,logical=None,borders=None):
 return k.export(folder,name,source(folder,id),contain=cap,logical=logical,borders=borders)
def blank(screen):return Image.open(ART/'concepts'/screen).convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST)
def placement(entries,uses,name,rect,use,z=60,**kw):
 e=next(e for e in entries if e['name']==name)
 uses.append(dict(name=name,rect=rect,use=use,z=z,**kw));return e
def paint(im,folder,e,rect,slice=False):
 a=Image.open(folder/e['file']).convert('RGBA')
 if slice and e.get('borders'):a=k.sliced(a,(rect[2]*3,rect[3]*3),e['borders']);im.alpha_composite(a,(rect[0]*3,rect[1]*3))
 else:k.put(im,a,rect)
def reuse(im,folder,file,rect,uses,z=30):
 k.put(im,Image.open(EX/folder/file),rect)
 uses.append(dict(name=Path(file).stem,file='../'+file if folder in ['s7','s8','s11'] else str((EX/folder/file).relative_to(EX)),rect=rect,use='accepted-kit-reuse',z=z,external=True))
def text(im,styles,fits,id,screen,msg,rect,size=14,align='left',fill='#173F57'):
 t=k.label(id,screen,msg,rect,size,align,fill);styles.append(t);fits.append(k.drawtext(im,t))
def finish(folder,entries,uses,styles,fits,im,bg,notes):
 for e in entries:
  found=[u for u in uses if u['name']==e['name']]
  if found:e['rect']=found[0]['rect']
 k.dump(folder/'manifest.json',entries)
 k.dump(folder/'layout.json',dict(screen='phone',canvas=[844,390],origin='top-left',background='../../../concepts/'+bg,backgroundSha256=k.sha(ART/'concepts'/bg),placements=uses,notes=notes))
 k.dump(folder/'text-styles.json',dict(styles=styles,notes='All labels separate/live; preview strings are illustrative.'))
 k.dump(folder/'text-measurements.json',fits)
 k.dump(folder/'slices.json',dict(sprites=[dict(name=e['name'],borders=e['borders'],border_order='left,bottom,right,top',units='export pixels; divide by3 for logical') for e in entries if e.get('borders')],notes='Fixed icons preserve aspect. Atlas frame sprites use explicit frameRects/pivots; never stretch the entire strip.'))
 im.save(folder/'reconstructed-3x.png')
 im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(folder/'actual-size-context.jpg',quality=97)
 # A bespoke contact avoids clipping the very long animation strips.
 heights=[210 if e.get('animation') else max(210,e['logicalSize'][1]+90) for e in entries]
 contact=Image.new('RGBA',(1260,sum(heights)),'#EAE3D4');d=ImageDraw.Draw(contact)
 y=0
 for i,e in enumerate(entries):
  a=Image.open(folder/e['file']).convert('RGBA')
  if e.get('animation'):
   for j,f in enumerate(e['animation']['frames']):
    x,yy,w,h=f['rect'];q=a.crop((x,yy,x+w,yy+h));q.thumbnail((155,145));contact.alpha_composite(q,(16+j*185,y+30))
  else:
   q=ImageOps.contain(a,(600,135));contact.alpha_composite(q,(16,y+27))
   tiny=a.resize(tuple(e['logicalSize']),Image.Resampling.LANCZOS);contact.alpha_composite(tiny,(700,y+40))
  d.text((16,y+heights[i]-35),e['name'],font=ImageFont.truetype(str(k.FONT),19),fill='#173F57')
  y+=heights[i]
 contact.convert('RGB').save(folder/'contact-sheet.jpg',quality=96)

def particle_strip(folder,name,particles,count,kind):
 """Pack individually tight variable-width frames; per-frame pivot keeps playback fixed."""
 rng=random.Random(742 if kind=='sparkle' else 944)
 particles=[k.crop(p)[0] for p in particles]
 trajectories=[]
 n=7 if kind=='sparkle' else 18
 for j in range(n):
  ang=2*math.pi*j/n+rng.uniform(-.16,.16)
  trajectories.append((ang,rng.uniform(.75,1),rng.uniform(8,14) if kind=='sparkle' else rng.uniform(6,11),rng.uniform(-120,120)))
 cropped=[];records=[];restored=[]
 for i in range(count):
  t=i/(count-1);canvas=Image.new('RGBA',(420,420));cx,cy=210,210
  for j,(angle,factor,sz,rotation) in enumerate(trajectories):
   if kind=='sparkle':radius=(10+36*t)*3;alpha=[.6,1,.85,.22][i];ss=sz*[.45,.9,1,.5][i]
   else:radius=(9+43*t)*3;alpha=[.45,1,1,.88,.57,.15][i];ss=sz*(.65+.35*math.sin(math.pi*t))
   sprite=particles[j%len(particles)].copy();w,h=k.fit_size(sprite,(round(ss*3),round(ss*3)))
   sprite=sprite.resize((w,h),Image.Resampling.LANCZOS).rotate(rotation+t*150,resample=Image.Resampling.BICUBIC,expand=True)
   sprite.putalpha(sprite.getchannel('A').point(lambda a:round(a*alpha)))
   xx=cx+math.cos(angle)*radius*factor;yy=cy+math.sin(angle)*radius*factor+(33*t*t if kind=='confetti' else 0)
   canvas.alpha_composite(sprite,(round(xx-sprite.width/2),round(yy-sprite.height/2)))
  canvas.putalpha(canvas.getchannel('A').point(lambda a:a if a>=3 else 0))
  box=canvas.getchannel('A').getbbox();assert box
  q=canvas.crop(box)
  # Quantize each tight frame to integral logical pixels, including alpha extremes.
  wh=[max(1,round(v/3))*3 for v in q.size];q=q.resize(tuple(wh),Image.Resampling.LANCZOS)
  q.putalpha(q.getchannel('A').point(lambda a:a if a>=2 else 0));bb=q.getchannel('A').getbbox();q=q.crop(bb).resize(tuple(wh),Image.Resampling.LANCZOS)
  pivot=[(cx-box[0])/(box[2]-box[0]),(cy-box[1])/(box[3]-box[1])]
  records.append(dict(index=i,rect=None,durationMs=75 if kind=='sparkle' else 100,pivot=pivot,pivotOrigin='top-left',logicalSize=[v//3 for v in wh],sourceCanvas=[140,140],sourceCrop=list(box)))
  cropped.append(q);restored.append(canvas)
 width=sum(q.width for q in cropped);height=max(q.height for q in cropped);atlas=Image.new('RGBA',(width,height));x=0
 for q,rec in zip(cropped,records):
  atlas.alpha_composite(q,(x,0));rec['rect']=[x,0,q.width,q.height];x+=q.width
 atlas.save(folder/(name+'.png'))
 assert atlas.getchannel('A').getbbox()==(0,0,*atlas.size)
 e=dict(name=name,file=name+'.png',size=list(atlas.size),logicalSize=[v//3 for v in atlas.size],borders=None,sha256=k.sha(folder/(name+'.png')),native3xDetailClaim=False,provenance=dict(method='Built-in ImageGen painted particles; deterministic position/rotation/alpha animation; each frame cropped tightly and packed horizontally, no atlas gutters.',sources=[dict(source=str(p.relative_to(ROOT)),sourceSha256=k.sha(p)) for p in particles_paths(folder,kind)]),animation=dict(frameCount=count,loop=False,totalDurationMs=sum(r['durationMs'] for r in records),frames=records,packing='variable-width horizontal; explicit rects required',playback='Place each frame pivot at the same world/UI anchor. Rect/pivot origin top-left. For Unity bottom-left pivots use [x,1-y]. Hide at end; do not hold last frame.',reducedMotion='Skip motion, or show the peak frame for100ms at the fixed anchor.'))
 review=Image.new('RGBA',(count*420,450),'#EAE3D4');d=ImageDraw.Draw(review)
 for i,q in enumerate(restored):
  review.alpha_composite(q,(i*420,0));d.text((i*420+18,427),str(i+1),font=ImageFont.truetype(str(k.FONT),18),fill='#173F57')
 review.convert('RGB').save(folder/(kind+'-frames.jpg'),quality=96)
 # Playback proof, each fixed canvas restored from packed sprite+recorded pivot.
 playback=[]
 for rec in records:
  xx,yy,w,h=rec['rect'];q=atlas.crop((xx,yy,xx+w,yy+h));frame=Image.new('RGBA',(420,420),'#173F57')
  frame.alpha_composite(q,(round(210-rec['pivot'][0]*w),round(210-rec['pivot'][1]*h)));playback.append(frame.convert('RGB'))
 playback[0].save(folder/(kind+'-playback.gif'),save_all=True,append_images=playback[1:],duration=[r['durationMs'] for r in records],loop=0,disposal=2)
 return e
def particles_paths(folder,kind):
 if kind=='sparkle':return [source(folder,'purchase-sparkle')]
 return sorted((folder/'provenance/particles').glob('*.png'))
def cut_confetti():
 # Connected alpha components extract the generated separate paper shapes, never redraw them.
 src,box=k.crop(source(C,'confetti'));small=src.copy();small.thumbnail((700,700));a=small.getchannel('A');pix=a.load();seen=set();pieces=[]
 for y in range(a.height):
  for x in range(a.width):
   if pix[x,y]<30 or (x,y) in seen:continue
   todo=[(x,y)];seen.add((x,y));points=[]
   while todo:
    xx,yy=todo.pop();points.append((xx,yy))
    for nx,ny in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
     if 0<=nx<a.width and 0<=ny<a.height and (nx,ny) not in seen and pix[nx,ny]>=30:seen.add((nx,ny));todo.append((nx,ny))
   if len(points)>45:pieces.append(points)
 assert len(pieces)>=6,('Insufficient separate paper shapes',len(pieces))
 dst=C/'provenance/particles';dst.mkdir(exist_ok=True)
 for i,pts in enumerate(sorted(pieces,key=len,reverse=True)[:18]):
  xs,ys=zip(*pts);r=[max(0,min(xs)-2),max(0,min(ys)-2),min(a.width,max(xs)+3),min(a.height,max(ys)+3)]
  scale=src.width/small.width;rr=[round(v*scale) for v in r];q=src.crop(rr);q.save(dst/('paper-%02d.png'%i))
 k.dump(dst/'extraction.json',dict(method='Connected-component alpha bounding boxes; natural generated silhouettes preserved.',source=str(source(C,'confetti').relative_to(ROOT)),sourceSha256=k.sha(source(C,'confetti')),components=len(pieces)))

def upgrades():
 entries=[export(P,'v2-s8-state-owned-card','muted-card',logical=(270,99)),export(P,'v2-s8-state-owned-check','owned-check',cap=(24,24)),k.export(P,'v2-s8-state-needs-stage',EX/'s1-card-states/v2-s1-state-bistro.png',logical=(126,30),borders=[63,15,24,15])]
 entries[0]['borders']=[54,42,54,42]
 entries.append(particle_strip(P,'v2-s8-purchase-strip',[source(P,'purchase-sparkle')],4,'sparkle'))
 im=blank('ui-8-upgrades.png');uses=[];styles=[];fits=[]
 for e,rect,use in [(entries[0],[16,287,270,99],'owned-fridge-card'),(entries[1],[153,348,24,24],'owned-check'),(entries[2],[422,345,126,30],'stage-gate-tag')]:
  placement(entries,uses,e['name'],rect,use,z=10 if 'card' in e['name'] else 70);paint(im,P,e,rect)
 reuse(im,'s8','v2-s8-fridge.png',[23,295,116,84],uses)
 # Clear original buy price under the check and Owned label using the new blank card.
 text(im,styles,fits,'owned-title','phone','Bigger fridge',[145,297,130,22],17)
 text(im,styles,fits,'owned-effect','phone','+15 portions',[146,319,125,18],13,fill='#4D776B')
 text(im,styles,fits,'owned-label','phone','Owned',[182,347,83,25],17)
 # Rebuild middle card beneath the stage restriction, rather than cover a live price with the tag.
 reuse(im,'s8','v2-s8-upgrade-card.png',[293,287,261,99],uses,z=10)
 reuse(im,'s8','v2-s8-stove.png',[299,296,117,83],uses)
 text(im,styles,fits,'locked-title','phone','Reliable stove',[424,297,125,22],16)
 text(im,styles,fits,'locked-effect','phone','Fewer breakdowns',[424,319,124,17],11,fill='#168F9F')
 # Repaint tag after the reconstruction; z ordering is also recorded for import.
 paint(im,P,entries[2],[422,345,126,30])
 text(im,styles,fits,'needs-stage-label','phone','Needs Bistro',[451,350,91,19],12,'center')
 rec=entries[3]['animation']['frames'][1];xx,yy,w,h=rec['rect'];spr=Image.open(P/entries[3]['file']).crop((xx,yy,xx+w,yy+h));r=[567,287,w//3,h//3]
 k.put(im,spr,r);uses.append(dict(name=entries[3]['name'],use='purchase-success-on-lighting',rect=r,frame=1,z=80,anchor=[r[0]+rec['pivot'][0]*r[2],r[1]+rec['pivot'][1]*r[3]]))
 finish(P,entries,uses,styles,fits,im,'ui-8-upgrades.png','State demo only. Owned and stage-locked examples illustrate independent conditions; original wallet/example economy retained. Purchased item is noninteractive. Never play the burst for a rejected purchase. Preserve existing effect text.')
 slice_proof(P,entries[0],[(270,99),(335,99)],'owned-card-slice-review.jpg')
 slice_proof(P,entries[2],[(126,30),(175,30)],'stage-tag-slice-review.jpg')
 print('A packaged',len(entries),'sprites')

def market():
 entries=[export(B,'v2-s7-state-sold-out','sold-out',cap=(145,42)),export(B,'v2-s7-state-fresh','fresh-tag',cap=(106,28)),export(B,'v2-s7-stepper-idle','stepper-idle',logical=(28,28)),export(B,'v2-s7-stepper-pressed','stepper-pressed',logical=(28,28))]
 im=blank('ui-7-market.png');uses=[];styles=[];fits=[]
 reuse(im,'s7','v2-s7-fish-row.png',[39,100,517,73],uses)
 reuse(im,'s7','v2-s7-fish-mackerel.png',[47,107,143,55],uses)
 text(im,styles,fits,'sold-species','phone','Mackerel',[202,104,130,22],17)
 text(im,styles,fits,'sold-weight','phone','0.0 kg left',[202,132,124,20],14)
 e=entries[0];r=[382,116,*e['logicalSize']];placement(entries,uses,e['name'],r,'row-1-empty');paint(im,B,e,r)
 text(im,styles,fits,'sold-label','phone','Sold out',[r[0]+12,r[1]+4,r[2]-24,r[3]-8],20,'center',fill='#AA3D35')
 reuse(im,'s7','v2-s7-fish-row.png',[39,175,517,73],uses)
 reuse(im,'s7','v2-s7-fish-pollock.png',[48,181,142,55],uses)
 text(im,styles,fits,'fresh-species','phone','Pollock',[202,178,125,22],17)
 text(im,styles,fits,'fresh-weight','phone','3.0 kg',[202,205,64,22],16)
 text(im,styles,fits,'fresh-price','phone','18 / kg',[275,205,64,22],14)
 text(im,styles,fits,'fresh-value','phone','54 coins',[341,205,53,22],13)
 for file,r,label in [('v2-s7-button-sell.png',[398,211,73,32],'Sell'),('v2-s7-button-keep.png',[475,211,76,32],'Keep')]:
  reuse(im,'s7',file,r,uses);text(im,styles,fits,'fresh-action-'+label.lower(),'phone',label,[r[0]+4,r[1]+2,r[2]-8,r[3]-4],17,'center',fill='#FFF4DC' if label=='Sell' else '#173F57')
 e=entries[1];r=[438,177,*e['logicalSize']];placement(entries,uses,e['name'],r,'row-2-fresh');paint(im,B,e,r)
 text(im,styles,fits,'fresh-label','phone','Fresh today',[r[0]+24,r[1]+3,r[2]-28,r[3]-6],11,'center',fill='#286658')
 # One third-row quantity-control demo, replacing the Sell/Keep widgets and old values.
 reuse(im,'s7','v2-s7-fish-row.png',[39,252,517,65],uses)
 reuse(im,'s7','v2-s7-fish-plaice.png',[48,257,142,54],uses)
 text(im,styles,fits,'quantity-species','phone','Plaice',[202,257,105,20],17)
 text(im,styles,fits,'quantity-unit','phone','Sell quantity (kg)',[202,285,143,18],12)
 for idx,(name,x,symbol) in enumerate([('v2-s7-stepper-idle',385,'-'),('v2-s7-stepper-idle',482,'+'),('v2-s7-stepper-pressed',385,'-'),('v2-s7-stepper-pressed',482,'+')]):
  # Alternate preview only: pressed state appears below in dedicated proof, not stacked in context.
  e=next(e for e in entries if e['name']==name);r=[x,274,28,28]
  uses.append(dict(name=name,rect=r,use=('minus' if symbol=='-' else 'plus')+('-idle' if idx<2 else '-pressed'),z=70,variant='idle' if idx<2 else 'pressed',mutuallyExclusive='quantity-stepper-state'))
  if idx<2:
   paint(im,B,e,r);text(im,styles,fits,'qty-'+str(idx),'phone',symbol,[x+3,276,22,23],22,'center')
 text(im,styles,fits,'quantity-value','phone','0.5',[425,275,45,24],18,'center')
 finish(B,entries,uses,styles,fits,im,'ui-7-market.png','Quantity mock values illustrative. Clamp quantity to available unsold kg; disable minus at0 and plus at available. Sold-out removes Sell/Keep actions, does not hide species. Fresh tag demo occupies row2 top-right; no price/buyer change. Both symbols are live text, same shared background for plus/minus.')
 proof=Image.new('RGBA',(844*3,115*3),'#EAE3D4');d=ImageDraw.Draw(proof)
 for j,(e,word) in enumerate([(entries[2],'Idle'),(entries[3],'Pressed')]):
  text(proof,[],[],'proof','proof',word,[20+j*400,12,200,25],17)
  for x,sym in [(20+j*400,'-'),(105+j*400,'+')]:paint(proof,B,e,[x,50,34,34]);text(proof,[],[],'symbol','proof',sym,[x+4,53,26,26],24,'center')
 proof.resize((844,115),Image.Resampling.LANCZOS).convert('RGB').save(B/'stepper-state-review.jpg',quality=97)
 print('B packaged',len(entries),'sprites')

def celebrate():
 cut_confetti()
 entries=[export(C,'v2-s11-celebrate-rays','light-rays',cap=(300,300)),particle_strip(C,'v2-s11-confetti-strip',particles_paths(C,'confetti'),6,'confetti'),k.export(C,'v2-s11-new-stage-ribbon',EX/'s5/v2-s5-best-night-ribbon.png',logical=(194,36))]
 entries[0]['usage']='Radial sprite: uniform scaling only, centre behind facade. No nine-slice; no hard clipping of the rays. Optional slow rotation, max renderOpacity0.55. Reduced motion static.'
 im=blank('ui-11-stage-up.png');uses=[];styles=[];fits=[]
 # Put rays on a fresh accepted left panel, then facade and existing live text.
 reuse(im,'s11','v2-s11-illustration-frame.png',[14,66,358,307],uses,z=10)
 e=entries[0];r=[47,80,*e['logicalSize']];placement(entries,uses,e['name'],r,'behind-new-facade',z=20,renderOpacity=.55)
 rays=Image.open(C/e['file']).convert('RGBA');rays.putalpha(rays.getchannel('A').point(lambda a:round(a*.55)));k.put(im,rays,r)
 reuse(im,'s11','v2-s11-illustration.png',[27,124,332,176],uses,z=30)
 text(im,styles,fits,'facade-heading','phone','A new sign on the quay',[48,84,294,26],20,'center')
 text(im,styles,fits,'facade-footer','phone','Your next chapter begins',[45,343,299,22],17,'center')
 e=entries[2];r=[100,300,194,36];placement(entries,uses,e['name'],r,'new-stage-banner',z=50);paint(im,C,e,r)
 text(im,styles,fits,'new-stage-label','phone','New stage!',[126,307,143,21],18,'center')
 e=entries[1];rec=e['animation']['frames'][2];x,y,w,h=rec['rect'];q=Image.open(C/e['file']).crop((x,y,x+w,y+h));r=[136,148,w//3,h//3];k.put(im,q,r)
 uses.append(dict(name=e['name'],rect=r,use='facade-confetti-peak',frame=2,z=40,anchor=[r[0]+rec['pivot'][0]*r[2],r[1]+rec['pivot'][1]*r[3]]))
 finish(C,entries,uses,styles,fits,im,'ui-11-stage-up.png','Effects behind/over new facade only; right-hand unlock list and Wonderful remain unobscured. Actual-size demo shows peak frame. Labels live. Same effects reuse at all stages. Radial rays scale uniformly rather than nine-slice. Confetti is transient, no input blocking.')
 print('C packaged',len(entries),'sprites')

def slice_proof(folder,e,sizes,file):
 im=Image.new('RGBA',(844*3,150*3),'#EAE3D4');x=12
 for w,h in sizes:paint(im,folder,e,[x,14,w,h],slice=True);x+=w+30
 im.resize((844,150),Image.Resampling.LANCZOS).convert('RGB').save(folder/file,quality=96)
if __name__=='__main__':{'A':upgrades,'B':market,'C':celebrate}[sys.argv[1]]()
