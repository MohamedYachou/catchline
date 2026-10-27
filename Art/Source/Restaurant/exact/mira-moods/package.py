"""ART-7 mechanical alpha cuts, kit reuse and review composition. No Assets writes."""
from pathlib import Path
import importlib.util,json,sys,shutil
from PIL import Image,ImageDraw,ImageFont,ImageOps
P=Path(__file__).resolve().parent; EX=P.parent; ART=EX.parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
B=EX/'s3/special';C=EX/'s2/pause'; FOLDERS=[P,B,C]
spec=importlib.util.spec_from_file_location('kit',EX/'s2-call/package.py');k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
def dump(p,v):k.dump(p,v)
def baseline():
 p=P/'preservation-baseline.json'
 if not p.exists():
  files=[*ART.glob('concepts/*.png'),*EX.rglob('*.png'),*EX.rglob('manifest.json')]
  dump(p,{str(f.relative_to(ROOT)):k.sha(f) for f in files if not any(f.is_relative_to(d) for d in FOLDERS)})
def ent(folder,name,source,logical,borders=None):return k.export(folder,name,source,logical,borders)
def put(im,folder,e,r):
 a=Image.open(folder/e['file']).convert('RGBA')
 if e.get('borders'):im.alpha_composite(k.sliced(a,(r[2]*3,r[3]*3),e['borders']),(r[0]*3,r[1]*3))
 else:k.put(im,a,r)
def use(entries,index,screen,r,role,z=20):return dict(name=entries[index]['name'],screen=screen,rect=r,use=role,z=z)
def lab(id,screen,text,r,size=16,align='center',fill='#173F57',wrap=False):return k.label(id,screen,text,r,size,align,fill,wrap)
def meta(folder,entries,screens,styles):
 dump(folder/'manifest.json',entries);dump(folder/'layout.json',dict(screens=screens,coordinates='top-left x,y,w,h in logical mockup pixels; z ascending'))
 dump(folder/'text-styles.json',dict(styles=styles,notes='Live labels; examples are illustrative, not new game rules.'))
 dump(folder/'slices.json',[e for e in entries if e.get('borders')])
 fits=[]
 for s in screens:
  im=render(folder,entries,s,styles,fits)
  im.save(folder/(s['screen']+'-reconstructed-3x.png'))
  im.resize(tuple(s['canvas']),Image.Resampling.LANCZOS).convert('RGB').save(ART/'concepts'/s['concept'])
 dump(folder/'text-measurements.json',fits)
 contact(folder,entries)
def render(folder,entries,s,styles,fits=None):
 bg=ROOT/s['background']; im=Image.open(bg).convert('RGBA').resize(tuple(v*3 for v in s['canvas']),Image.Resampling.NEAREST)
 if s.get('dim'):
  im=Image.alpha_composite(im,Image.new('RGBA',im.size,(9,31,48,s['dim'])))
 es={e['name']:e for e in entries}
 for u in sorted(s['placements'],key=lambda v:v['z']):
  if u.get('external'):
   a=Image.open(ROOT/u['external']).convert('RGBA');r=u['rect']
   if u.get('externalBorders'):im.alpha_composite(k.sliced(a,(r[2]*3,r[3]*3),u['externalBorders']),(r[0]*3,r[1]*3))
   else:k.put(im,a,r)
  else:put(im,folder,es[u['name']],u['rect'])
 for t in styles:
  if t['screen']==s['screen']:
   f=k.drawtext(im,t);f['screen']=s['screen']
   if fits is not None:fits.append(f)
 return im
def contact(folder,entries):
 # Row height is driven by actual logical bounds; no tall-art overlap.
 width=1000;rows=[]
 for start in range(0,len(entries),2):rows.append((entries[start:start+2],max(e['logicalSize'][1] for e in entries[start:start+2])+58))
 out=Image.new('RGB',(width,sum(h for _,h in rows)+12),'#EAE3D4');d=ImageDraw.Draw(out);font=ImageFont.truetype(str(k.FONT),14);y=8
 for es,h in rows:
  for col,e in enumerate(es):
   x=col*500+18;d.text((x,y),e['name']+' / 1x',font=font,fill='#173F57')
   a=Image.open(folder/e['file']).convert('RGBA').resize(tuple(e['logicalSize']),Image.Resampling.LANCZOS);out.paste(a,(x,y+28),a)
  y+=h
 out.save(folder/'contact-sheet.jpg',quality=96)
def moods():
 entries=[]
 source=ART/'clothes/busts/v2-rbust-mira.png'
 for mood in ['happy','worried','excited','proud']:
  src=source if mood=='happy' else P/'provenance'/(mood+'.png')
  for variant,size in [('call',[38,51]),('coach',[102,136])]:
   e=ent(P,'v2-mira-'+mood+'-'+variant,src,size)
   e.update(mood=mood,variant=variant,identity='Mira / accepted D host outfit',binding=dict(happy='default',worried='out of stock / breakdown',excited='birthday / tour / full house',proud='closing / best night')[mood])
   entries.append(e)
 # Happy defaults are exact accepted exports rather than another resampling.
 for e,src in [(entries[0],EX/'s2-call/v2-s2-call-mira.png'),(entries[1],EX/'coach-card/v2-coach-mira.png')]:
  shutil.copy2(src,P/e['file']);e['sha256']=k.sha(P/e['file']);e['provenance']['acceptedExactCopy']=str(src.relative_to(ROOT))
 screens=[];styles=[]
 for screen,canvas,bg,cr,mr,br,pr,tr in [
  ('phone',[844,390],'ui-2-mira-call-phone.png',[511,47,38,51],[674,113,102,136],[176,132,548,160],[486,236,116,40],[196,148,365,72]),
  ('desktop',[1440,900],'ui-2-mira-call-desktop.png',[879,80,49,66],[1105,518,146,195],[380,555,800,220],[873,700,160,52],[412,580,520,100])]:
  # Coach and strip shown together only as a component demonstration.
  placements=[dict(name='v2-coach-panel',external=str((EX/'coach-card/v2-coach-panel.png').relative_to(ROOT)),screen=screen,rect=br,use='coach-speech',z=20),dict(name='v2-coach-got-it',external=str((EX/'coach-card/v2-coach-got-it.png').relative_to(ROOT)),screen=screen,rect=pr,use='coach-acknowledge',z=21)]
  # External sliceable pieces need nine-slice rather than a flattened resize.
  placements[0]['externalBorders']=[48,48,114,48];placements[1]['externalBorders']=[48,30,48,30]
  placements += [use(entries,4,screen,cr,'excited-call',25),use(entries,7,screen,mr,'proud-coach',26)]
  placements[-2]['alternatives']=[e['name'] for e in entries if e['variant']=='call']
  placements[-1]['alternatives']=[e['name'] for e in entries if e['variant']=='coach']
  fs=16 if screen=='phone' else 23
  styles += [lab('coach-line',screen,'You kept the kitchen moving and every table smiling. What a lovely service!',tr,fs,'left',wrap=True),lab('got-it',screen,'Got it',[pr[0],pr[1]+3,pr[2],pr[3]-6],18 if screen=='phone' else 25,fill='#FFF4DC')]
  screens.append(dict(screen=screen,canvas=canvas,background=str((ART/'concepts'/bg).relative_to(ROOT)),backgroundSha256=k.sha(ART/'concepts'/bg),concept='ui-mira-moods-'+screen+'.png',placements=placements,notes='Two expression examples only; retain accepted call/coach layout and swap same-size sprites by mood.'))
 # Mood contact includes every state; context only needs one of each component.
 meta(P,entries,screens,styles)
 # Dedicated same-framing comparison at large and tiny consumption sizes.
 out=Image.new('RGB',(1000,480),'#EAE3D4');d=ImageDraw.Draw(out);f=ImageFont.truetype(str(k.FONT),18)
 for col,mood in enumerate(['happy','worried','excited','proud']):
  x=col*250+20;d.text((x,8),mood,font=f,fill='#173F57')
  for suffix,pos,size in [('coach',(x,40),(204,272)),('coach',(x,328),(102,136)),('call',(x+142,342),(38,51))]:
   a=Image.open(P/('v2-mira-'+mood+'-'+suffix+'.png')).convert('RGBA').resize(size,Image.Resampling.LANCZOS);out.paste(a,pos,a)
 out.save(P/'expression-review.jpg',quality=97)
 dump(P/'framing.json',dict(acceptedCall=[38,51],acceptedCoach=[102,136],notes='All alpha crops are normalized to identical logical silhouette bounds. Common head tilt and wardrobe are visually checked; generated facial features are not pixel-identical landmarks. Happy is a byte-identical accepted copy.'))
def special():
 original,box=k.crop(B/'provenance/chalkboard.png');size=k.fit_size(original,(486,900));original.resize(size,Image.Resampling.LANCZOS).save(B/'provenance/chalkboard-normalized.png')
 dump(B/'provenance/normalization.json',dict(source='chalkboard.png',sha256=k.sha(B/'provenance/chalkboard.png'),alphaCrop=list(box),resized=list(size),notes='Mechanical aspect-preserving normalization to 162logical width before nine-slicing blank interior.'))
 entries=[ent(B,'v2-s3-special-board',B/'provenance/chalkboard-normalized.png',[162,209],[42,42,42,42]),ent(B,'v2-s3-special-dish-slot',EX/'s3-s5/v2-plan-dish-card.png',[110,78],[27,27,27,27])]
 screen='plan';styles=[lab('special-title',screen,"Today's special",[684,86,140,34],16,fill='#FFF4DC'),lab('dish-name',screen,'Grilled fish',[686,211,136,26],18,fill='#FFF4DC'),lab('special-tips',screen,'+tips',[692,245,124,25],18,fill='#F5CC70')]
 placements=[use(entries,0,screen,[674,75,162,209],'special-chalkboard'),use(entries,1,screen,[700,124,110,78],'dish-slot',21),dict(name='v2-dish-grilled-fish',external=str((EX/'s3-s5/v2-dish-grilled-fish.png').relative_to(ROOT)),screen=screen,rect=[711,131,88,64],use='example-dish',z=22)]
 meta(B,entries,[dict(screen=screen,canvas=[844,390],background=str((ART/'concepts/ui-3-mira-plan.png').relative_to(ROOT)),backgroundSha256=k.sha(ART/'concepts/ui-3-mira-plan.png'),concept='ui-3-special.png',placements=placements,notes='Special card occupies right request slot in this illustrative variant; do not stack over an active request. Live dish, title and tips value supplied by caller.')],styles)
 proof=Image.new('RGBA',(680*3,250*3),'#EAE3D4')
 for x,w in [(10,162),(200,235),(460,205)]:
  put(proof,B,entries[0],[x,10,w,209])
 proof.resize((680,250),Image.Resampling.LANCZOS).convert('RGB').save(B/'slice-proof.jpg',quality=96)
def pause():
 entries=[ent(C,'v2-s2-pause-panel',EX/'s3-s5/v2-plan-paper.png',[360,290],[80,80,80,250]),ent(C,'v2-s2-pause-primary',EX/'coach-card/v2-coach-got-it.png',[280,44],[48,30,48,30]),ent(C,'v2-s2-pause-secondary',EX/'s3-s5/v2-btn-secondary.png',[280,44],[36,30,36,30])]
 screens=[];styles=[]
 for screen,canvas,bg,panel,title,buttons,fs in [
  ('phone',[844,390],'ui-2-service.png',[242,49,360,290],[260,76,324,42],[[282,145,280,44],[282,202,280,44],[282,259,280,44]],20),
  ('desktop',[1440,900],'ui-service-desktop.png',[470,220,500,440],[494,250,452,45],[[520,338,400,64],[520,420,400,64],[520,502,400,64]],27)]:
  placements=[use(entries,0,screen,panel,'pause-paper',20)]
  for j,r in enumerate(buttons):placements.append(use(entries,1 if j==0 else 2,screen,r,['resume','speed-tips','back-harbour'][j],21+j))
  styles.append(lab('pause-title',screen,'Service paused',title,26 if screen=='phone' else 34))
  for id,text,r in zip(['resume','speed-tips','back-harbour'],['Resume','Speed tips','Back to the harbour'],buttons):styles.append(lab(id,screen,text,[r[0]+8,r[1]+4,r[2]-16,r[3]-8],fs,fill='#FFF4DC' if id=='resume' else '#173F57'))
  screens.append(dict(screen=screen,canvas=canvas,background=str((ART/'concepts'/bg).relative_to(ROOT)),backgroundSha256=k.sha(ART/'concepts'/bg),dim=150,concept='ui-pause-'+screen+'.png',placements=placements,hitRects={key:r for key,r in zip(['resume','speed-tips','back-harbour'],buttons)},behavior='Caller pauses service clock and sim, blocks room input, traps focus. Resume and Escape return to service. Speed tips opens caller-owned help. Back to the harbour invokes existing safe-exit/confirmation flow; this art defines no save/discard rules.',dimming='Uniform #091F30 alpha150/255 overlay; caller primitive, no exported fullscreen sprite.'))
 meta(C,entries,screens,styles)
 proof=Image.new('RGBA',(950*3,470*3),'#EAE3D4')
 for r in [[10,10,360,290],[420,10,500,440]]:put(proof,C,entries[0],r)
 proof.resize((950,470),Image.Resampling.LANCZOS).convert('RGB').save(C/'slice-proof.jpg',quality=96)
if __name__=='__main__':
 baseline();mode=sys.argv[1] if len(sys.argv)>1 else 'all'
 if mode in ('a','all'):moods()
 if mode in ('b','all'):special()
 if mode in ('c','all'):pause()
