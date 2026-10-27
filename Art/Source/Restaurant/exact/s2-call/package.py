"""RESTAURANT-ART-2 source-art crops/composition only; no runtime changes.
Run: uv run --with pillow python Art/Source/Restaurant/exact/s2-call/package.py
"""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib,re,shutil,math
P=Path(__file__).resolve().parent
ART=P.parent.parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
S15=P.parent/'s15';EV=S15/'events';HUD=ART/'concepts/hud-v3-review'
FONT=ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def crop(p):
 im=Image.open(p).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda a:a if a>=8 else 0));box=im.getchannel('A').getbbox();assert box
 return im.crop(box),box
def fit_size(im,box):
 w,h=box;s=min(w/im.width,h/im.height);return max(1,round(im.width*s)),max(1,round(im.height*s))
def sliced(im,size,borders):
 l,b,r,t=borders;w,h=im.size;dw,dh=size;assert dw>=l+r and dh>=t+b
 out=Image.new('RGBA',size);sx=[0,l,w-r,w];sy=[0,t,h-b,h];dx=[0,l,dw-r,dw];dy=[0,t,dh-b,dh]
 for y in range(3):
  for x in range(3):
   tile=im.crop((sx[x],sy[y],sx[x+1],sy[y+1])).resize((dx[x+1]-dx[x],dy[y+1]-dy[y]),Image.Resampling.LANCZOS)
   out.alpha_composite(tile,(dx[x],dy[y]))
 return out
def export(folder,name,source,logical=None,borders=None,contain=None):
 im,box=crop(source)
 if contain:logical=fit_size(im,contain)
 assert logical
 size=tuple(x*3 for x in logical)
 im=sliced(im,size,borders) if borders else im.resize(size,Image.Resampling.LANCZOS)
 im.putalpha(im.getchannel('A').point(lambda a:a if a>=2 else 0));im=im.crop(im.getchannel('A').getbbox())
 if im.size!=size:im=im.resize(size,Image.Resampling.LANCZOS)
 file=name+'.png';im.save(folder/file)
 assert im.getchannel('A').getbbox()==(0,0,*size)
 return dict(name=name,file=file,logicalSize=list(logical),size=list(size),borders=borders,border_order='left,bottom,right,top',sha256=sha(folder/file),provenance=dict(source=str(source.relative_to(ROOT)),sourceSha256=sha(source),sourceAlphaCrop=list(box),method='accepted painted kit reuse or built-in ImageGen; mechanical alpha crop, aspect-preserving resize / nine-slice'),native3xDetailClaim=False)
def put(im,sprite,rect):
 x,y,w,h=rect;im.alpha_composite(sprite.resize((w*3,h*3),Image.Resampling.LANCZOS),(x*3,y*3))
def label(id,screen,text,rect,size=14,align='left',fill='#173F57',wrap=False):
 return dict(id=id,screen=screen,text=text,rect=rect,font='Fredoka-Bold',weight=700,size=size,fill=fill,stroke_width=0,align=align,vertical_align='middle',wrap=wrap,lineHeight=size+2)
def lines(text,font,width,d):
 out=['']
 for word in text.split():
  test=(out[-1]+' '+word).strip()
  if d.textlength(test,font=font)<=width:out[-1]=test
  else:out.append(word)
 return out
def drawtext(im,t):
 d=ImageDraw.Draw(im);x,y,w,h=t['rect'];f=ImageFont.truetype(str(FONT),t['size']*3)
 parts=lines(t['text'],f,w*3,d) if t.get('wrap') else [t['text']]
 metrics=[d.textbbox((0,0),s,font=f) for s in parts];lh=t['lineHeight']*3
 contenth=metrics[0][3]-metrics[0][1]+(len(parts)-1)*lh
 assert contenth<=h*3,(t['id'],parts,contenth,h*3)
 for i,(s,b) in enumerate(zip(parts,metrics)):
  tw=b[2]-b[0];assert tw<=w*3,(t['id'],tw,w*3)
  xx=x*3+(w*3-tw)//2 if t['align']=='center' else x*3
  d.text((xx-b[0],y*3+(h*3-contenth)//2+i*lh-b[1]),s,font=f,fill=t['fill'])
 return dict(id=t['id'],lines=parts,widthPx=max(b[2]-b[0] for b in metrics)/3,heightPx=contenth/3,rect=t['rect'],passFit=True)
def contact(folder,entries,file):
 out=Image.new('RGB',(1000,270*math.ceil(len(entries)/2)),'#eae3d4');d=ImageDraw.Draw(out)
 for i,e in enumerate(entries):
  x=(i%2)*500;y=(i//2)*270;a=Image.open(folder/e['file']).convert('RGBA');big=ImageOps.contain(a,(440,155));out.paste(big,(x+(500-big.width)//2,y+6),big)
  d.text((x+8,y+166),e['name'],font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12),fill='#173f57')
  tiny=a.resize(tuple(e['logicalSize']),Image.Resampling.LANCZOS);out.paste(tiny,(x+8,y+190),tiny)
 out.save(file,quality=95)
def recover():
 for rec in load(P/'provenance/generation-records.json'):
  path=Path(rec['hint'].split(' as ')[1].split(' by default.')[0])
  if rec['id']=='door':dst=P/'provenance/door.png'
  elif rec['id'].startswith('hud-'):dst=HUD/(rec['id']+'-original.png')
  else:dst=EV/'provenance'/(rec['id']+'.png')
  shutil.copy2(path,dst)
 dump(EV/'provenance/prompts.json',[r for r in load(P/'provenance/generation-records.json') if r['id'] in ['birthday','regular','tour','captain']])
 dump(HUD/'prompts.json',[r for r in load(P/'provenance/generation-records.json') if r['id'].startswith('hud-')])
def service():
 kit=P.parent/'s1-s2';entries=[]
 entries.append(export(P,'v2-s2-call-bubble',P.parent/'s13/v2-s13-speech-bubble.png',[320,44],[48,36,114,36]))
 entries.append(export(P,'v2-s2-call-mira',ART/'clothes/busts/v2-rbust-mira.png',contain=(38,52)))
 entries.append(export(P,'v2-s2-close-door-button',kit/'v2-speed-idle.png',[97,32],[24,24,24,24]))
 entries.append(export(P,'v2-s2-close-door-icon',P/'provenance/door.png',contain=(18,24)))
 dump(P/'manifest.json',entries);dump(P/'slices.json',[e for e in entries if e['borders']])
 layouts=[];styles=[];fits=[]
 configs=[('phone',[844,390],'ui-2-service.png',[190,50,320,44],[511,47,38,52],[421,6,97,32],[429,10,18,24],[450,9,62,26],12,14,[207,56,278,32]),('desktop',[1440,900],'ui-service-desktop.png',[444,86,430,54],[879,80,49,67],[804,14,121,50],[814,23,24,32],[843,22,76,34],15,18,[465,94,370,38])]
 for screen,canvas,bg,bubble,mira,button,door,close,cs,ts,calltext in configs:
  original=Image.open(ART/'concepts'/bg).convert('RGBA');im=original.resize((canvas[0]*3,canvas[1]*3),Image.Resampling.NEAREST)
  # Header reflow is confined to measured rects. Static reference timeline is demonstration only.
  if screen=='phone':
   patch=[167,0,357,44];timelineSource=[177,0,326,40];timelineRect=[176,0,238,40];blankSource=[164,0,174,44]
  else:
   patch=[102,0,828,80];timelineSource=[545,0,330,75];timelineRect=[467,0,330,75];blankSource=[875,0,905,80]
  bar=original.crop(tuple(blankSource));put(im,bar,patch)
  x,y,w,h=timelineSource;timeline=original.crop((x,y,x+w,y+h));put(im,timeline,timelineRect)
  if screen=='desktop':
   title=label('service-title',screen,"Mira's · Service",[115,18,340,48],34,fill='#FFF4DC');styles.append(title);fits.append(drawtext(im,title))
  placements=[]
  for e,rect,use in zip(entries,[bubble,mira,button,door],['reusable-call-bubble','accepted-host-bust','top-bar-close-door','door-icon']):
   sprite=Image.open(P/e['file']).convert('RGBA')
   if e['borders']:sprite=sliced(sprite,(rect[2]*3,rect[3]*3),e['borders']);im.alpha_composite(sprite,(rect[0]*3,rect[1]*3))
   else:put(im,sprite,rect)
   placements.append(dict(name=e['name'],screen=screen,use=use,rect=rect,z=20+len(placements)))
  s=[label('mira-call',screen,"A birthday table! Let's make it special.",calltext,ts,wrap=True),label('close-door',screen,'Close door',close,cs,'center','#FFF4DC',True)]
  styles+=s
  for t in s:fits.append(drawtext(im,t))
  layouts.append(dict(screen=screen,canvas=canvas,origin='top-left',background='../../concepts/'+bg,backgroundSha256=sha(ART/'concepts'/bg),placements=placements,headerReflow=dict(patchRect=patch,blankSourceBox=blankSource,timelineSourceRect=timelineSource,timelineRect=timelineRect,notes='Reflow live timeline into destination; reference crop is demonstration only. Desktop title shortened, back/wallet/stars/speeds untouched.'),protectedWorldBelowY=100 if screen=='phone' else 150))
  im.save(P/(screen+'-reconstructed-3x.png'));im.resize(tuple(canvas),Image.Resampling.LANCZOS).convert('RGB').save(ART/'concepts'/('ui-2-mira-call-'+screen+'.png'))
 dump(P/'layout.json',dict(screens=layouts,notes='Call is non-blocking; anchors fixed below topbar. Text wraps at measured width; queue controls lifetime in code. Closed state/disabled logic is runtime-owned.'))
 dump(P/'text-styles.json',dict(styles=styles));dump(P/'text-measurements.json',fits)
 # Representative 40-character queue lines and both sliced bubble widths.
 proof=Image.new('RGBA',(1440*3,190*3),'#eae3d4');tests=[]
 for i,(screen,canvas,bg,b,m,bt,dr,cl,cs,ts,tr) in enumerate(configs):
  for j,msg in enumerate(["A birthday table! Let's make it special.",'Your next guests are here. Greet them now!']):
   x=20+i*700;y=12+j*88;r=[x,y,b[2],b[3]];spr=sliced(Image.open(P/entries[0]['file']),(r[2]*3,r[3]*3),entries[0]['borders']);proof.alpha_composite(spr,(x*3,y*3));t=label('line-'+screen+'-'+str(j),screen,msg,[x+17,y+6,tr[2],tr[3]],ts,wrap=True);tests.append(drawtext(proof,t))
 proof.resize((1440,190),Image.Resampling.LANCZOS).convert('RGB').save(P/'line-length-slice-review.jpg',quality=96);dump(P/'line-fit.json',tests)
 contact(P,entries,P/'contact-sheet.jpg')
 print('Service packaged',len(entries),'sprites; text/line fits PASS')
def events():
 baseline=EV/'baseline-manifest.json'
 if not baseline.exists():shutil.copy2(S15/'manifest.json',baseline)
 base=load(baseline);entries=[];placements=[]
 rects=[[369,179,30,34],[534,181,30,30],[588,230,28,34],[441,241,30,34]]
 for kind,slot in zip(['birthday','regular','tour','captain'],rects):
  e=export(S15,'v2-s15-event-'+kind,EV/'provenance'/(kind+'.png'),contain=(slot[2],slot[3]));e.update(screen=15,event=kind,usage='World-anchored event indicator; preserve aspect, hide when event inactive.')
  w,h=e['logicalSize'];r=[slot[0]+(slot[2]-w)//2,slot[1]+(slot[3]-h)//2,w,h];e['rect']=r;entries.append(e);placements.append(dict(name=e['name'],screen=15,use='event-demo',rect=r,z=40))
 dump(EV/'manifest.json',entries);dump(S15/'manifest.json',base+entries)
 layout=dict(screen=15,canvas=[844,390],origin='top-left',background='../../../concepts/ui-2-service.png',backgroundSha256=sha(ART/'concepts/ui-2-service.png'),placements=placements)
 dump(EV/'layout.json',layout);dump(EV/'text-styles.json',dict(screen=15,styles=[],notes='Event markers are text-free. Accessible names: Birthday, Regular guest, Tour group, Captain table.'))
 dump(EV/'slices.json',dict(sprites=[],notes='Preserve aspect; do not slice icons.'))
 im=Image.open(ART/'concepts/ui-2-service.png').convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST)
 for e in entries:put(im,Image.open(S15/e['file']),e['rect'])
 im.save(EV/'reconstructed-3x.png');im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(EV/'event-context.png');contact(S15,entries,EV/'contact-sheet.jpg')
 assert all(sha(S15/e['file'])==e['sha256'] for e in base)
 print('Events packaged; accepted',len(base),'sprite hashes preserved')
def huds():
 for kind,id in [('fishing','17-hud-fishing'),('harbour','18-hud-harbour')]:
  original=HUD/('hud-'+kind+'-corrected.png')
  if not original.exists():original=HUD/('hud-'+kind+'-original.png')
  im=Image.open(original).convert('RGB');im.resize((1920,1080),Image.Resampling.LANCZOS).save(ART/'concepts'/('ui-v3-'+id+'.png'))
 print('HUD proposal sources persisted; visual review pending')
if __name__=='__main__':recover();service();events();huds()
