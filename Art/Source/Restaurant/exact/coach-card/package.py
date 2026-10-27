"""ART-3 source-art packaging only; accepted paintings reused, no Assets edits."""
from pathlib import Path
import importlib.util, json, hashlib, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
P=Path(__file__).resolve().parent
EX=P.parent; ART=EX.parent; ROOT=ART.parents[2]
spec=importlib.util.spec_from_file_location('kit_helpers',EX/'s2-call/package.py')
k=importlib.util.module_from_spec(spec); spec.loader.exec_module(k)
S=EX/'s1-card-states'; C=EX/'closed-sign'
def save(p,v):k.dump(p,v)
def capture_baseline():
 f=P/'preservation-baseline.json'
 if not f.exists():
  files=[*ART.glob('concepts/*.png'), *EX.glob('*/*.png'), *EX.glob('*/manifest.json')]
  save(f,{str(p.relative_to(ROOT)):k.sha(p) for p in files})
def init(folder):
 folder.mkdir(exist_ok=True); (folder/'provenance').mkdir(exist_ok=True)
def entry(folder,name,source,logical=None,borders=None,contain=None):
 return k.export(folder,name,source,logical,borders,contain)
def t(id,screen,text,rect,size=16,align='left',fill='#173F57',wrap=False):
 return k.label(id,screen,text,rect,size,align,fill,wrap)
def composite(im,folder,e,rect):
 spr=Image.open(folder/e['file']).convert('RGBA')
 if e['borders']:
  spr=k.sliced(spr,(rect[2]*3,rect[3]*3),e['borders']);im.alpha_composite(spr,(rect[0]*3,rect[1]*3))
 else:k.put(im,spr,rect)
def package_meta(folder,entries,screens,styles,fits):
 save(folder/'manifest.json',entries);save(folder/'layout.json',dict(screens=screens,coordinates='top-left x,y,w,h; logical mockup pixels; z ascending'))
 save(folder/'text-styles.json',dict(styles=styles,notes='All labels rendered live; exported sprites contain no text.'))
 save(folder/'slices.json',[e for e in entries if e['borders']]);save(folder/'text-measurements.json',fits)
 k.contact(folder,entries,folder/'contact-sheet.jpg')
def coach():
 init(P);capture_baseline()
 entries=[entry(P,'v2-coach-panel',EX/'s13/v2-s13-speech-bubble.png',[548,160],[48,48,114,48]),entry(P,'v2-coach-mira',ART/'clothes/busts/v2-rbust-mira.png',contain=(102,138)),entry(P,'v2-coach-got-it',EX/'s1-s2/v2-btn-primary.png',[116,40],[48,30,48,30])]
 # Exactly 110 visible characters, including spaces and punctuation.
 msg="Welcome to our first service! Seat the guests, keep hot plates moving, and tell me when you're ready to close."
 assert len(msg)==110,(len(msg),msg)
 styles=[];screens=[];fits=[]
 configs=[('phone','ui-1-arrange.png',[844,390],[[176,132,548,160],[674,113,102,136],[486,236,116,40]],[196,148,365,72],[486,239,116,32],[620,244,64,24],16,18),('desktop','ui-service-desktop.png',[1440,900],[[380,555,800,220],[1105,518,146,195],[873,700,160,52]],[412,580,520,100],[873,707,160,36],[1052,713,90,28],23,25)]
 for screen,bg,canvas,rects,body,got,skip,fs,bs in configs:
  im=Image.open(ART/'concepts'/bg).convert('RGBA').resize((canvas[0]*3,canvas[1]*3),Image.Resampling.NEAREST)
  placements=[]
  for i,(e,r) in enumerate(zip(entries,rects)):
   composite(im,P,e,r);placements.append(dict(name=e['name'],screen=screen,use=['coach-speech','host-portrait','acknowledge'][i],rect=r,z=20+i))
  labels=[t('coaching-line',screen,msg,body,fs,wrap=True),t('got-it',screen,'Got it',got,bs,'center','#FFF4DC'),t('skip',screen,'Skip',skip,fs,'center')]
  styles+=labels
  for lab in labels:
   fit=k.drawtext(im,lab);fits.append(fit)
   if lab['id']=='coaching-line':assert len(fit['lines'])<=3
  screens.append(dict(screen=screen,canvas=canvas,background='../../concepts/'+bg,backgroundSha256=k.sha(ART/'concepts'/bg),placements=placements,interaction=dict(panel='tutorial focus; optional pause owned by caller',gotItHitRect=got,skipHitRect=[skip[0],skip[1]-10,skip[2],max(44,skip[3])],pointer='right tail preserved by right slice cap',dismissal='Got it advances; Skip exits coaching, never service')))
  im.save(P/(screen+'-reconstructed-3x.png'));im.resize(tuple(canvas),Image.Resampling.LANCZOS).convert('RGB').save(ART/'concepts'/('ui-coach-'+screen+'.png'))
 package_meta(P,entries,screens,styles,fits)
 # Wide coach panel needs a dedicated actual-size review; a two-column generic
 # contact would let its548px width overlap the next column/row.
 contact=Image.new('RGB',(1000,410),'#EAE3D4');d=ImageDraw.Draw(contact);font=ImageFont.truetype(str(k.FONT),16)
 for e,pos in zip(entries,[(20,42),(690,42),(20,300)]):
  d.text((pos[0],pos[1]-26),e['name']+' (actual size)',font=font,fill='#173F57')
  spr=Image.open(P/e['file']).convert('RGBA').resize(tuple(e['logicalSize']),Image.Resampling.LANCZOS);contact.paste(spr,pos,spr)
 contact.save(P/'contact-sheet.jpg',quality=96)
 # Two width proofs use 9-slice, never stretch the portrait/button silhouette.
 proof=Image.new('RGBA',(1440*3,260*3),'#EAE3D4')
 for x,w in [(10,548),(580,800)]:
  r=[x,10,w,220];composite(proof,P,entries[0],r)
 proof.resize((1440,260),Image.Resampling.LANCZOS).convert('RGB').save(P/'slice-proof.jpg',quality=96)
 save(P/'capacity.json',dict(characters=len(msg),maximumLines=3,bodyFits=[f for f in fits if f['id']=='coaching-line'],notes='110 characters is a sample capacity, not a guarantee for every string; wrap and validate localization.'))
 print('A coach:',len(entries),'sprites, 110 characters, phone/desktop <=3 lines PASS')
def states():
 init(S)
 entries=[entry(S,'v2-s1-state-stored',S/'provenance/stored-ribbon.png',contain=(94,26)),entry(S,'v2-s1-state-bistro',S/'provenance/bistro-lock.png',contain=(85,28)),entry(S,'v2-s1-state-price-disabled',S/'provenance/disabled-price.png',contain=(116,30)),entry(S,'v2-s1-state-card',EX/'s1-s2/v2-item-card-idle.png',[148,72],[36,30,36,30])]
 im=Image.open(ART/'concepts/ui-1-arrange.png').convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST)
 placements=[];styles=[];fits=[]
 def use(e,r,u,z):
  composite(im,S,e,r);placements.append(dict(name=e['name'],screen='arrange',use=u,rect=r,z=z))
 # Each replacement stays inside the three original drawer card rectangles.
 for x,kind in [(350,'stored'),(510,'locked'),(670,'poor')]:
  use(entries[3],[x,306,156,73],kind+'-card',20)
  if kind=='stored':
   # Reuse accepted painted table, preserving aspect.
   pic=Image.open(EX/'s1-s2/v2-item-rest-table2.png').convert('RGBA');pw,ph=k.fit_size(pic,(53,42));k.put(im,pic,[x+5,330,pw,ph])
   use(entries[0],[x+54,309,*entries[0]['logicalSize']],'stored-ribbon',22)
   styles += [t('stored-label','arrange','Stored',[x+66,312,70,18],13,'center','#FFF4DC'),t('stored-item','arrange','Table for 2',[x+59,336,88,17],12),t('stored-free','arrange','Place for free',[x+59,356,90,17],11)]
  elif kind=='locked':
   use(entries[1],[x+62,309,*entries[1]['logicalSize']],'locked-stage-tag',22)
   pic=Image.open(EX/'s1-s2/v2-item-rest-table4.png').convert('RGBA');pw,ph=k.fit_size(pic,(57,41));k.put(im,pic,[x+4,332,pw,ph])
   styles += [t('bistro-label','arrange','Bistro',[x+89,314,51,18],12,'center'),t('locked-item','arrange','Table for 4',[x+63,338,86,17],12),t('locked-hint','arrange','Stage 2',[x+63,357,85,16],11,fill='#566878')]
  else:
   use(entries[2],[x+20,330,*entries[2]['logicalSize']],'muted-price',22)
   styles += [t('poor-item','arrange','Booth',[x+11,309,134,20],13,'center'),t('poor-price','arrange','380',[x+60,334,66,20],14,'center','#697778'),t('poor-reason','arrange','Not enough coins',[x+8,360,140,17],12,'center','#65717A')]
 for lab in styles:fits.append(k.drawtext(im,lab))
 # Painted item references are repeated uses too, not flattened hidden content.
 externals=[dict(name='v2-item-rest-table2',file='../s1-s2/v2-item-rest-table2.png',rect=[355,330,*k.fit_size(Image.open(EX/'s1-s2/v2-item-rest-table2.png'),(53,42))],screen='arrange',use='stored-item-illustration',z=21),dict(name='v2-item-rest-table4',file='../s1-s2/v2-item-rest-table4.png',rect=[514,332,*k.fit_size(Image.open(EX/'s1-s2/v2-item-rest-table4.png'),(57,41))],screen='arrange',use='locked-item-illustration',z=21)]
 screens=[dict(screen='arrange',canvas=[844,390],background='../../concepts/ui-1-arrange.png',backgroundSha256=k.sha(ART/'concepts/ui-1-arrange.png'),placements=placements+externals,states=dict(stored='owned item; placing is free',locked='stage-gated; locked item cannot be purchased',poor='disabled price and readable reason; caller tests affordability'),notes='State comparison demo; price/wallet figures are illustrative, not one coherent affordability snapshot. Runtime uses live values.')]
 package_meta(S,entries,screens,styles,fits)
 im.save(S/'reconstructed-3x.png');im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(ART/'concepts/ui-arrange-card-states.png')
 print('B drawer:',len(entries),'sprites,',len(styles),'live labels PASS')
def closed():
 init(C)
 e=entry(C,'v2-closed-sign-board',C/'provenance/closed-board.png',contain=(112,46));entries=[e]
 im=Image.open(ART/'concepts/ui-2-service.png').convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST)
 w,h=e['logicalSize'];r=[602,277,w,h];composite(im,C,e,r)
 # Label stays below the hanging ropes and inside the wooden face.
 lab=t('closed-label','phone','Closed',[r[0]+13,r[1]+round(h*.38),w-26,round(h*.46)],15,'center','#FFF4DC')
 fit=k.drawtext(im,lab)
 screens=[dict(screen='phone',canvas=[844,390],background='../../concepts/ui-2-service.png',backgroundSha256=k.sha(ART/'concepts/ui-2-service.png'),placements=[dict(name=e['name'],screen='phone',use='entrance-closed',rect=r,z=20)],usage='Screen-space demo near entrance; anchor over actual room entrance, hide until door is closed. Request panel and reference guests are untouched background, not a closed-service state simulation.')]
 package_meta(C,entries,screens,[lab],[fit]);im.save(C/'reconstructed-3x.png');im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(ART/'concepts/ui-closed-sign.png')
 print('C closed sign:',e['logicalSize'],'separate live label PASS')
if __name__=='__main__':
 mode=sys.argv[1] if len(sys.argv)>1 else 'all'
 if mode in ('a','all'):coach()
 if mode in ('b','all'):states()
 if mode in ('c','all'):closed()
