"""ART-8 mechanical cuts, accepted kit composition and source-art metadata only."""
from pathlib import Path
import importlib.util, json, sys
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parent; EX=P.parent; ART=EX.parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
B=EX/'s3/reservation'
spec=importlib.util.spec_from_file_location('kit',EX/'s2-call/package.py'); k=importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
spec=importlib.util.spec_from_file_location('meta',EX/'mira-moods/package.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def dump(p,v):k.dump(p,v)
def baseline():
 p=P/'preservation-baseline.json'
 if not p.exists():
  files=[*ART.glob('concepts/*.png'),*EX.rglob('*.png'),*EX.rglob('manifest.json'),*ART.glob('clothes/**/*.png')]
  dump(p,{str(f.relative_to(ROOT)):k.sha(f) for f in files if not f.is_relative_to(P) and not f.is_relative_to(B)})
def entry(folder,name,source,size,borders=None,opaque=False):
 e=k.export(folder,name,source,size,borders); e['opaque']=opaque; return e
def use(es,i,screen,r,role,z=20):return dict(name=es[i]['name'],screen=screen,rect=r,use=role,z=z)
def lab(id,screen,text,r,size=16,align='left',fill='#173F57',wrap=False):return k.label(id,screen,text,r,size,align,fill,wrap)
def external(path,r,screen,role,z=25):return dict(name=path.stem,external=str(path.relative_to(ROOT)),externalSha256=k.sha(path),rect=r,screen=screen,use=role,z=z)
def finish(folder,es,screens,ts):
 for e in es:
  places=[u for s in screens for u in s['placements'] if u['name']==e['name']]
  e['rect']=places[0]['rect']
  e['uses']=[u['use'] for u in places]
 m.meta(folder,es,screens,ts)
 # One row per sprite keeps full-width backgrounds/title signs at actual size.
 rows=[max(68,e['logicalSize'][1]+42) for e in es]
 im=Image.new('RGB',(1000,sum(rows)+10),'#EAE3D4');d=ImageDraw.Draw(im);y=6
 for e,rh in zip(es,rows):
  d.text((14,y),e['name']+' / actual 1x',font=ImageFont.truetype(str(k.FONT),14),fill='#173F57')
  a=Image.open(folder/e['file']).convert('RGBA').resize(tuple(e['logicalSize']),Image.Resampling.LANCZOS)
  im.paste(a,(14,y+25),a);y+=rh
 im.save(folder/'contact-sheet.jpg',quality=97)
def week():
 # The full painted first pass is retained in provenance; exact reconstruction
 # replaces painted data/Jo with clean accepted kit and live sample labels.
 es=[]
 arrow=EX/'s6/v2-s6-chevron-left.png';Image.open(arrow).convert('RGBA').transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(P/'provenance/right-chevron.png')
 dump(P/'provenance/derived-sources.json',dict(rightChevron=dict(source=str(arrow.relative_to(ROOT)),sha256=k.sha(arrow),operation='horizontal flip only')))
 specs=[
  ('background',EX/'s6/v2-s6-background.png',[844,390],None,True),
  ('title-sign',EX/'s6/v2-s6-title-sign.png',[524,61],[100,24,190,30],False),
  ('income-panel',EX/'s6/v2-s6-panel.png',[430,222],[80,60,80,70],False),
  ('award-panel',EX/'s6/v2-s6-panel.png',[366,102],[80,60,80,70],False),
  ('summary-panel',EX/'s6/v2-s6-panel.png',[430,68],[80,48,80,70],False),
  ('total-panel',EX/'s6/v2-s6-panel.png',[178,68],[80,48,80,70],False),
  ('primary',EX/'s3-s5/v2-btn-primary.png',[174,60],[60,45,60,45],False),
  ('bar-teal',EX/'s6/v2-s6-bar-teal.png',[34,100],[12,12,12,12],False),
  ('bar-gold',EX/'s6/v2-s6-bar-gold.png',[34,136],[12,12,12,12],False),
  ('medal',P/'provenance/medal.png',list(k.fit_size(k.crop(P/'provenance/medal.png')[0],(53,68))),None,False),
  ('dish-slot',EX/'s3/special/v2-s3-special-dish-slot.png',[108,72],[27,27,27,27],False),
  ('crew-slot',EX/'s3-s5/v2-review-card.png',[92,92],[24,24,24,24],False),
  ('star',EX/'s3-s5/v2-star-full.png',[38,36],None,False),
  ('coin',EX/'s6/v2-s6-coin.png',[39,24],None,False),
  ('axis',EX/'s6/v2-s6-divider-horizontal.png',[370,2],None,False),
  ('arrow',P/'provenance/right-chevron.png',[16,20],None,False)]
 for n,s,sz,br,op in specs:es.append(entry(P,'v2-s16-'+n,s,sz,br,op))
 sc='week';u=[use(es,0,sc,[0,0,844,390],'wall',0),use(es,1,sc,[160,3,524,61],'week-title',10),use(es,2,sc,[18,73,430,222],'seven-night-income',10),use(es,3,sc,[460,73,366,102],'best-dish-card',10),use(es,3,sc,[460,183,366,112],'crew-card',10),use(es,4,sc,[18,306,430,68],'popularity-summary',10),use(es,5,sc,[460,306,178,68],'week-total',10),use(es,6,sc,[652,309,174,60],'next-week',10),use(es,9,sc,[475,94,53,68],'best-dish-medal',22),use(es,10,sc,[535,91,108,72],'best-dish-slot',20),use(es,11,sc,[474,194,92,92],'crew-bust-slot',20),use(es,12,sc,[33,323,38,36],'popularity-star',22),use(es,13,sc,[472,321,39,39],'total-coin',22),use(es,14,sc,[44,266,378,2],'income-baseline',20)]
 # Existing dish and crew identity are example content slots, not new duplicates.
 u += [external(EX/'s3-s5/v2-dish-grilled-fish.png',[540,99,*k.fit_size(Image.open(EX/'s3-s5/v2-dish-grilled-fish.png'),(98,58))],sc,'example-best-dish'),external(ART/'clothes/busts/v2-rbust-jo.png',[480,196,*k.fit_size(Image.open(ART/'clothes/busts/v2-rbust-jo.png'),(83,90))],sc,'example-crew-jo')]
 u += [use(es,15,sc,[241,328,16,20],'popularity-direction',23)]
 for v in u:
  if v['name']=='v2-s16-medal':v['rect']=[475,94,*es[9]['logicalSize']]
  if v['name']=='v2-s16-coin':v['rect']=[472,331,39,24]
 ts=[lab('title',sc,"A week at Mira's",[185,19,420,36],31,'center','#FFF4DC'),lab('income-title',sc,'Seven lovely nights',[42,88,376,30],23),lab('best-dish',sc,'Best dish',[654,87,154,24],20),lab('dish-name',sc,'Grilled fish',[654,116,154,23],20),lab('dish-count',sc,'48 served',[654,144,154,20],16),lab('crew-title',sc,'Crew of the week',[579,198,228,28],21),lab('crew-name',sc,'Jo',[579,226,218,28],27),lab('crew-quote',sc,'Always one step ahead.',[579,261,226,20],15),lab('popularity-title',sc,'Popularity',[82,315,100,22],17),lab('popularity-start-end',sc,'40 → 46',[184,317,146,38],31),lab('popularity-delta',sc,'+6 this week',[334,329,101,21],13,fill='#007B77'),lab('total-title',sc,'Week total',[516,314,110,22],16),lab('total-coins',sc,'2,840',[515,338,111,30],28),lab('next-week',sc,'Next week',[666,324,146,32],24,'center','#FFF4DC')]
 ts=[t for t in ts if t['id']!='popularity-start-end']
 ts += [lab('popularity-start',sc,'40',[184,317,48,38],31),lab('popularity-end',sc,'46',[267,317,58,38],31)]
 values=[280,360,320,410,450,560,460];days=['M','T','W','T','F','S','S']
 for i,(v,day) in enumerate(zip(values,days)):
  x=50+i*53;h=round(v/560*136)
  u.append(use(es,8 if i==5 else 7,sc,[x,266-h,34,h],'night-'+str(i+1),21))
  ts += [lab('night-'+str(i+1)+'-coins',sc,str(v),[x-7,244-h,48,19],16,'center'),lab('night-'+str(i+1)+'-day',sc,day,[x,270,34,19],14,'center')]
 screens=[dict(screen=sc,canvas=[844,390],background=str((EX/'s6/v2-s6-background.png').relative_to(ROOT)),backgroundSha256=k.sha(EX/'s6/v2-s6-background.png'),concept='ui-16-week.png',placements=u,hitRects={'next-week':[652,309,174,60]},notes='Shown after seventh closing. Seven income values sum to2840; Saturday is highlighted as best night. Example stars/popularity, best dish and crew are live content. No new economy rules. Empty nights use zero-height hidden bars, value0 and day label. Dynamic bars nine-slice vertically; hide below minimum cap height instead of inverting borders.')]
 finish(P,es,screens,ts)
 dump(P/'sample-data.json',dict(nightTakings=values,totalCoins=sum(values),bestDish=dict(id='grilled-fish',served=48),crewOfWeek='jo',popularityStart=40,popularityEnd=46,illustrative=True))
 # Caps and panel corners at multiple widths/heights.
 proof=Image.new('RGBA',(850*3,350*3),'#EAE3D4')
 for i,(w,h) in enumerate([(34,25),(34,70),(34,136)]):m.put(proof,P,es[7],[20+i*70,180-h,w,h])
 for i,(w,h) in enumerate([(260,92),(366,102)]):m.put(proof,P,es[3],[230,12+i*125,w,h])
 proof.resize((850,350),Image.Resampling.LANCZOS).convert('RGB').save(P/'slice-proof.jpg',quality=96)
def reservation():
 es=[]
 specs=[('card',EX/'s3-s5/v2-ticket.png',[168,222],[42,42,42,66]),('face-slot',EX/'s3-s5/v2-review-card.png',[40,40],[18,18,18,18]),('dish-slot',EX/'s3/special/v2-s3-special-dish-slot.png',[51,37],[21,21,21,21]),('accept',EX/'s3-s5/v2-btn-accept.png',[144,44],[45,30,45,30]),('decline',EX/'s3-s5/v2-btn-secondary.png',[144,44],[45,30,45,30])]
 for n,s,sz,br in specs:es.append(entry(B,'v2-s3-reservation-'+n,s,sz,br))
 wall=EX/'s3-s5/v2-bg-plan.png';a=Image.open(wall).convert('RGBA').resize((2532,1170),Image.Resampling.LANCZOS).crop((665*3,65*3,844*3,295*3));a.save(B/'provenance/wall-patch.png')
 es.append(entry(B,'v2-s3-reservation-wall-patch',B/'provenance/wall-patch.png',[179,230],opaque=True))
 es[-1]['contextOnly']=True
 dump(B/'provenance/derived-sources.json',dict(wallPatch=dict(source=str(wall.relative_to(ROOT)),sha256=k.sha(wall),operation='Resize to2532x1170, crop top-left logical [665,65,179,230]; context removal of old ticket only. Runtime hides old request rather than painting a patch.')))
 sc='plan';u=[use(es,0,sc,[669,70,168,222],'special-reservation',30),use(es,1,sc,[680,101,40,40],'guest-face-slot',31),use(es,2,sc,[680,148,51,37],'wished-dish-slot',31),use(es,3,sc,[680,192,144,44],'accept-reservation',31),use(es,4,sc,[680,240,144,44],'decline-reservation',31),external(ART/'clothes/guests/v2-guest-ada.png',[682,103,36,36],sc,'example-guest-ada',32),external(EX/'s3-s5/v2-dish-grilled-fish.png',[683,151,45,30],sc,'example-wished-dish',32)]
 u.insert(0,use(es,5,sc,[665,65,179,230],'context-remove-old-ticket',29))
 for v in u:
  if v['use']=='guest-face-slot':v['rect']=[680,103,32,32]
  if v['use']=='example-guest-ada':v['rect']=[682,105,28,28]
  if v['use']=='wished-dish-slot':v['rect']=[680,158,51,29]
  if v['use']=='example-wished-dish':v['rect']=[683,160,*k.fit_size(Image.open(EX/'s3-s5/v2-dish-grilled-fish.png'),(45,25))]
 ts=[lab('reservation-heading',sc,'Reservation',[682,80,140,22],18,'center'),lab('guest-name',sc,'Ada',[721,105,100,25],19),lab('party-size-time',sc,'4 guests · 19:30',[682,137,140,19],13,'center'),lab('wished-dish',sc,'Grilled fish',[735,158,87,26],14,wrap=True),lab('accept',sc,'Accept',[691,200,122,27],20,'center','#FFF4DC'),lab('decline',sc,'Decline',[691,248,122,27],20,'center')]
 screens=[dict(screen=sc,canvas=[844,390],background=str((ART/'concepts/ui-3-mira-plan.png').relative_to(ROOT)),backgroundSha256=k.sha(ART/'concepts/ui-3-mira-plan.png'),concept='ui-3-reservation.png',placements=u,hitRects={'accept':[680,192,144,44],'decline':[680,240,144,44]},notes='Replaces the existing right-hand request ticket only. Accept/Decline are localised live labels; use existing special-request actions, no new penalty/rule. Existing Got it button and central plan remain source reference. Guest and requested dish are external content slots. Card and special chalkboard are alternatives, never stack.')]
 finish(B,es,screens,ts)
 proof=Image.new('RGBA',(660*3,310*3),'#EAE3D4')
 for i,w in enumerate([168,226,226]):
  if i==2:break
  m.put(proof,B,es[0],[12+i*250,10,w,278 if i else 222])
 proof.resize((660,310),Image.Resampling.LANCZOS).convert('RGB').save(B/'slice-proof.jpg',quality=96)
if __name__=='__main__':
 baseline();mode=sys.argv[1] if len(sys.argv)>1 else'all'
 if mode in('a','all'):week()
 if mode in('b','all'):reservation()
 print('ART-8',mode,'packaged')
