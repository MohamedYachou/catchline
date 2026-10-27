"""ART-6 source-art packaging. Mechanical crops, resampling and kit composition only."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import importlib.util,json,sys,hashlib
P=Path(__file__).resolve().parent
EX=P.parent; ART=EX.parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
J=EX/'s9/jobs'; B=EX/'badges'
spec=importlib.util.spec_from_file_location('kit',EX/'s2-call/package.py')
k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
def dump(p,v):k.dump(p,v)
def baseline():
 p=P/'preservation-baseline.json'
 if p.exists():return
 paths=list(EX.rglob('*.png'))+list(EX.rglob('manifest.json'))+list((ART/'concepts').glob('*.png'))
 paths=[p for p in paths if not any(p.is_relative_to(q) for q in [P,J,B])]
 dump(p,{str(p.relative_to(ROOT)).replace('\\','/'):k.sha(p) for p in paths})
def export(folder,name,src,logical=None,cap=None,borders=None):
 return k.export(folder,name,src,logical=logical,contain=cap,borders=borders)
def use(uses,e,rect,screen='phone',suffix='',z=10):
 uses.append(dict(name=e['name'],use=suffix or e['name'],screen=screen,rect=rect,z=z))
def paint(im,folder,e,r):
 spr=Image.open(folder/e['file']).convert('RGBA')
 if e.get('borders'):
  spr=k.sliced(spr,(r[2]*3,r[3]*3),e['borders']);im.alpha_composite(spr,(r[0]*3,r[1]*3))
 else:k.put(im,spr,r)
def text(im,styles,fits,id,screen,msg,r,size=14,align='left',fill='#173F57'):
 t=k.label(id,screen,msg,r,size,align,fill);styles.append(t);fits.append(k.drawtext(im,t))
def finish(folder,entries,layouts,styles,fits):
 for e in entries:
  u=[u for l in layouts for u in l['placements'] if u['name']==e['name']]
  if u:e['rect']=u[0]['rect']
 dump(folder/'manifest.json',entries)
 dump(folder/'layout.json',dict(screens=layouts,origin='top-left',units='logical pixels; exports 3x',notes='Art placement proofs only. Text remains live and separate.'))
 dump(folder/'text-styles.json',dict(styles=styles,notes='Live illustrative labels; Fredoka-Bold. Keep text out of sprites.'))
 dump(folder/'text-measurements.json',fits)
 dump(folder/'slices.json',dict(sprites=[dict(name=e['name'],borders=e['borders'],border_order='left,bottom,right,top',units='3x export pixels') for e in entries if e.get('borders')]))
 contact(folder,entries)
def contact(folder,entries):
 # Backgrounds have dedicated full-size reviews, keep cut contact compact.
 entries=[e for e in entries if not e.get('opaque')]
 out=Image.new('RGBA',(1000,max(1,len(entries))*160),'#eae3d4');d=ImageDraw.Draw(out)
 for i,e in enumerate(entries):
  a=Image.open(folder/e['file']).convert('RGBA');large=ImageOps.contain(a,(530,110));out.alpha_composite(large,(15,i*160+8))
  tiny=ImageOps.contain(a,(420,95)); tiny=a.resize(tuple(e['logicalSize']),Image.Resampling.LANCZOS) if max(e['logicalSize'])<=420 else tiny
  out.alpha_composite(tiny,(570,i*160+8));d.text((15,i*160+126),e['name'],font=ImageFont.truetype(str(k.FONT),18),fill='#173F57')
 out.convert('RGB').save(folder/'contact-sheet.jpg',quality=96)
def slice_proof(folder,e,sizes,file):
 out=Image.new('RGBA',(max(w for w,h in sizes)*3+60,sum(h for w,h in sizes)*3+len(sizes)*45),'#eae3d4');y=15
 for w,h in sizes:
  a=k.sliced(Image.open(folder/e['file']),(w*3,h*3),e['borders']);out.alpha_composite(a,(30,y));y+=h*3+45
 out.resize((out.width//3,out.height//3),Image.Resampling.LANCZOS).convert('RGB').save(folder/file,quality=96)
def transitions():
 entries=[];layouts=[];styles=[];fits=[]
 band=export(P,'v2-transition-title-band',EX/'s6/v2-s6-income-summary.png',logical=(600,90));band['borders']=[90,75,90,75];entries.append(band)
 for kind,title,subtitle in [('evening','Evening falls',"The lanterns are lit. Time to welcome your guests."),('morning','Good morning','A fresh day at the harbour. Mira has your plan.')]:
  src=P/'provenance'/(kind+'.png')
  for screen,canvas,r,ts,ss in [('phone',[844,390],[122,284,600,90],30,16),('desktop',[1440,900],[270,712,900,144],50,24)]:
   name='v2-transition-'+kind+'-'+screen
   original=Image.open(src).convert('RGBA'); fitted=ImageOps.fit(original,tuple(v*3 for v in canvas),Image.Resampling.LANCZOS,centering=(.5,.55))
   fitted.save(P/(name+'.png'))
   # Explicit source crop makes both responsive compositions reproducible.
   ratio=canvas[0]/canvas[1];w,h=original.size
   if w/h>ratio:cw=h*ratio;ch=h;left=(w-cw)*.5;top=0
   else:cw=w;ch=w/ratio;left=0;top=(h-ch)*.55
   e=dict(name=name,file=name+'.png',logicalSize=canvas,size=[v*3 for v in canvas],borders=None,opaque=True,sha256=k.sha(P/(name+'.png')),provenance=dict(source=str(src.relative_to(ROOT)),sourceSha256=k.sha(src),sourceCrop=[left,top,cw,ch],method='Built-in ImageGen painting; ImageOps.fit centre crop and 3x resample'),native3xDetailClaim=False)
   entries.append(e);im=fitted.copy();uses=[];use(uses,e,[0,0,*canvas],screen,'full-bleed-'+kind,z=0);use(uses,band,r,screen,'separate-title-band',z=10);paint(im,P,band,r)
   tr=[r[0]+24,r[1]+7,r[2]-48,40] if screen=='phone' else [r[0]+36,r[1]+10,r[2]-72,68]
   sr=[r[0]+22,r[1]+51,r[2]-44,27] if screen=='phone' else [r[0]+32,r[1]+87,r[2]-64,38]
   text(im,styles,fits,kind+'-title',kind+'-'+screen,title,tr,ts,'center')
   text(im,styles,fits,kind+'-subtitle',kind+'-'+screen,subtitle,sr,ss,'center')
   layout=dict(screen=kind+'-'+screen,canvas=canvas,placements=uses,titleRect=tr,subtitleRect=sr,notes='No extra action button. Caller owns timing and flow; fade/cut for reduced motion. Subtitle stays on one line.')
   for u in uses:u['screen']=layout['screen']
   layouts.append(layout);im.save(P/(kind+'-'+screen+'-reconstructed-3x.png'))
   im.resize(tuple(canvas),Image.Resampling.LANCZOS).convert('RGB').save(ART/'concepts'/('ui-transition-'+kind+'-'+screen+'.png'))
 finish(P,entries,layouts,styles,fits)
 slice_proof(P,band,[(600,90),(900,144)],'title-band-slice-review.jpg')
 print('A packaged',len(entries),'exports; 4 responsive paintings, live labels fit')
def jobs():
 entries=[];styles=[];fits=[];uses=[]
 for id in ['host','cook','waiter','dishwasher','barista','handyman']:
  e=export(J,'v2-s9-job-'+id,J/'provenance'/(id+'.png'),cap=(28,28));e['accessibleName']=id.title();entries.append(e)
 tag=export(J,'v2-s9-job-tag',EX/'s9/v2-s9-job-field.png',logical=(166,34),borders=[24,24,24,24]);entries.append(tag)
 im=Image.open(ART/'concepts/ui-9-crew-priorities.png').convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST)
 # A standalone role legend proves all six words, including the long Dishwasher label.
 proof=Image.new('RGBA',(844*3,390*3),'#EAE3D4');proofuses=[];proofstyles=[];prooffits=[]
 for i,e in enumerate(entries[:6]):
  y=[90,133,176,222,268,313][i];r=[210,y,122,27];use(uses,tag,r,suffix='crew-'+str(i)+'-tag');paint(im,J,tag,r)
  w,h=e['logicalSize'];ir=[216,y+(27-h)//2,w,h];use(uses,e,ir,suffix='crew-'+str(i)+'-role');paint(im,J,e,ir)
  label=['Host','Cook','Waiter','Waiter','Barista','Handyman'][i]
  # S9 fixed rows remain the reference roster: second waiter row uses its waiter icon.
  if i==3:
   uses.pop();paint(im,J,tag,r);we=entries[2];w,h=we['logicalSize'];ir=[216,y+(27-h)//2,w,h];use(uses,we,ir,suffix='crew-3-role');paint(im,J,we,ir)
  text(im,styles,fits,'row-'+str(i)+'-job','phone',label,[249,y+3,79,21],14)
  x=35+(i%3)*270; yy=105+(i//3)*110;rr=[x,yy,240,58];use(proofuses,tag,rr,'legend','legend-'+str(i)+'-tag');paint(proof,J,tag,rr)
  w,h=e['logicalSize'];ir=[x+14,yy+(58-h)//2,w,h];use(proofuses,e,ir,'legend','legend-'+str(i)+'-role');paint(proof,J,e,ir)
  text(proof,proofstyles,prooffits,'job-'+str(i),'legend',e['accessibleName'],[x+52,yy+15,177,28],22)
 text(proof,proofstyles,prooffits,'legend-title','legend','Restaurant jobs',[35,24,774,45],32)
 text(proof,proofstyles,prooffits,'legend-caption','legend','Job and task icons for your crew',[35,330,774,30],19)
 layouts=[dict(screen='phone',canvas=[844,390],background='../../../concepts/ui-9-crew-priorities.png',backgroundSha256=k.sha(ART/'concepts/ui-9-crew-priorities.png'),placements=uses),dict(screen='legend',canvas=[844,390],placements=proofuses)]
 finish(J,entries,layouts,styles+proofstyles,fits+prooffits)
 im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(J/'actual-size-context.jpg',quality=97)
 proof.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(J/'all-jobs-actual-size.jpg',quality=97)
 slice_proof(J,tag,[(122,27),(166,34),(240,58)],'job-tag-slice-review.jpg')
 dump(J/'job-bindings.json',dict(icons={'Reception':'v2-s9-job-host','Cook':'v2-s9-job-cook','Waiter':'v2-s9-job-waiter','Barista':'v2-s9-job-barista','Handyman':'v2-s9-job-handyman'},auxiliary={'dishwashing-task':'v2-s9-job-dishwasher'},notes='Dishwasher is a requested presentation/task icon, not a new RestaurantData.Job. Helper may use a caller-chosen task icon; no new fixed job invented.'))
 print('B packaged',len(entries),'exports; roster and six-role legend')
def badges():
 entries=[export(B,'v2-hud-count-badge',B/'provenance/count.png',logical=(30,22)),export(B,'v2-hud-new-flag',B/'provenance/new.png',logical=(45,24))]
 entries[0]['borders']=[27,27,27,27];entries[1]['borders']=[24,21,42,21]
 im=Image.open(ART/'concepts/ui-6-dashboard.png').convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST);uses=[];styles=[];fits=[]
 for e,r,msg,sz,id in [(entries[0],[345,54,30,22],'12',14,'dashboard-count'),(entries[1],[787,319,45,24],'New',13,'upgrades-new')]:
  use(uses,e,r,suffix=id);paint(im,B,e,r);tr=[r[0]+3,r[1]+2,r[2]-(12 if 'flag' in e['name'] else 6),r[3]-4]
  text(im,styles,fits,id,'phone',msg,tr,sz,'center','#FFF4DC')
 finish(B,entries,[dict(screen='phone',canvas=[844,390],background='../../concepts/ui-6-dashboard.png',backgroundSha256=k.sha(ART/'concepts/ui-6-dashboard.png'),placements=uses)],styles,fits)
 im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(B/'actual-size-context.jpg',quality=97)
 proof=Image.new('RGBA',(844*3,225*3),'#eae3d4');pf=[]
 for i,(msg,w) in enumerate([('1',22),('9',22),('12',30),('99',30)]):
  r=[30+i*90,55,w,22];paint(proof,B,entries[0],r);t=k.label('count-'+msg,'proof',msg,[r[0]+3,r[1]+2,r[2]-6,18],14,'center','#FFF4DC');pf.append(k.drawtext(proof,t))
 for i,w in enumerate([45,64]):
  r=[465+i*120,55,w,24];paint(proof,B,entries[1],r);t=k.label('new-'+str(w),'proof','New',[r[0]+3,r[1]+2,r[2]-12,20],13,'center','#FFF4DC');pf.append(k.drawtext(proof,t))
 text(proof,[],pf,'caption','proof','Live 1-2 digit counts and separate New labels',[30,125,770,30],21)
 proof.resize((844,225),Image.Resampling.LANCZOS).convert('RGB').save(B/'count-and-flag-state-review.jpg',quality=97);dump(B/'state-text-fits.json',pf)
 dump(B/'behavior-notes.json',dict(count='Hide at zero; 1-9 use22x22,10-99 use30x22; for higher counts use99 or wider caller-defined label. Noninteractive overlay; do not create a tiny tap target.',new='Live localisable word New; blank swallowtail flag grows horizontally. Hide when acknowledged.',accessibility='Parent button owns accessible name, count/new state, and full44px+ tap target. Never communicate availability with colour alone.'))
 slice_proof(B,entries[0],[(22,22),(30,22),(45,22)],'count-slice-review.jpg');slice_proof(B,entries[1],[(45,24),(64,24)],'flag-slice-review.jpg')
 print('C packaged 2 exports, live count/new state proofs')
if __name__=='__main__':
 baseline()
 for arg in sys.argv[1:] or ['A','B','C']:{'A':transitions,'B':jobs,'C':badges}[arg]()
