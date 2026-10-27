"""ART-9: requested mechanical 3x cuts and accepted painted-kit composition.
No generation, painting or Assets writes. ImageGen originals precede packaging.
"""
from pathlib import Path
import importlib.util, json, sys
from PIL import Image, ImageDraw, ImageFont
P=Path(__file__).resolve().parent; EX=P.parent; ART=EX.parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
G=ART/'clothes/guests'; X=G/'extra'
spec=importlib.util.spec_from_file_location('kit',EX/'s2-call/package.py'); k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)
spec=importlib.util.spec_from_file_location('meta',EX/'mira-moods/package.py'); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def dump(p,v):k.dump(p,v)
def baseline():
 dest=P/'preservation-baseline.json'
 if dest.exists():return
 files=[*ART.glob('concepts/*.png'),*EX.rglob('*.png'),*EX.rglob('manifest.json'),*ART.glob('clothes/**/*.png')]
 dump(dest,{str(f.relative_to(ROOT)):k.sha(f) for f in files if not f.is_relative_to(P) and not f.is_relative_to(X)})
 dump(P/'guest-manifest-before.json',k.load(G/'manifest.json'))
def entry(name,src,sz,br=None,opaque=False):
 e=k.export(P,'v2-s17-'+name,src,sz,br);e['opaque']=opaque;return e
def use(e,r,role,z=20):return dict(name=e['name'],screen='hire',rect=r,use=role,z=z)
def external(src,r,role,z=30):return dict(name=src.stem,screen='hire',external=str(src.relative_to(ROOT)),externalSha256=k.sha(src),rect=r,use=role,z=z)
def label(id,text,r,size=18,align='left',fill='#173F57'):return k.label(id,'hire',text,r,size,align,fill)
def board():
 assert (P/'provenance/hiring-original.png').exists(),'Paint first'
 es=[entry('background',EX/'s9/v2-s9-background.png',[844,390],opaque=True),
 entry('title-sign',EX/'s9/v2-s9-title-sign.png',[320,58]),
 entry('back',EX/'s9/v2-s9-button-back.png',[128,44],[24,24,24,24]),
 entry('back-arrow',EX/'s9/v2-s9-arrow-back.png',[26,27]),
 entry('wallet',EX/'s9/v2-s9-crew-plaque.png',[140,44],[24,24,24,24]),
 entry('candidate-card',EX/'s16/v2-s16-award-panel.png',[264,280],[66,54,66,54]),
 entry('bust-slot',EX/'s3-s5/v2-review-card.png',[110,150],[24,24,24,24]),
 entry('job-tag',EX/'s9/jobs/v2-s9-job-tag.png',[116,34],[24,24,24,24]),
 entry('rarity-band',EX/'s1-card-states/v2-s1-state-stored.png',[124,30],[72,18,72,18]),
 entry('coin',EX/'s6/v2-s6-coin.png',[24,15]),
 entry('hire',EX/'s3-s5/v2-btn-primary.png',[228,52],[60,45,60,45]),
 entry('footer',EX/'s9/v2-s9-footer.png',[816,32],[30,24,30,24]),
 entry('info',EX/'s9/v2-s9-info.png',[23,23])]
 u=[use(es[0],[0,0,844,390],'blue-plank-wall',0),use(es[1],[262,0,320,58],'hanging-title',10),use(es[2],[10,5,128,44],'back-button',10),use(es[3],[22,14,26,27],'back-icon',20),use(es[4],[690,5,140,44],'wallet',10),use(es[9],[701,19,27,17],'wallet-coin',20),use(es[11],[14,351,816,32],'tomorrow-footer',10),use(es[12],[27,356,23,23],'footer-info',20)]
 ts=[label('title','Hiring board',[296,15,242,33],27,'center','#FFF4DC'),label('back','Back',[54,12,73,29],24,'center'),label('wallet','1,240',[735,13,83,30],25,'center'),label('tomorrow','New faces tomorrow',[61,354,700,25],19)]
 samples=[dict(id='tess',name='Tess',job='Cook',icon='cook',rarity='Common',wage=18,trait='Steady hands'),dict(id='jo',name='Jo',job='Waiter',icon='waiter',rarity='Rare',wage=24,trait='Quick on their feet'),dict(id='ines',name='Ines',job='Barista',icon='barista',rarity='Uncommon',wage=20,trait='A warm welcome')]
 hits={'back':[10,5,128,44]}
 for i,s in enumerate(samples):
  x=14+i*276;key=s['id'];card=[x,66,264,280]
  for idx,r,role in [(5,card,'card'),(6,[x+14,82,110,150],'bust-slot'),(7,[x+133,115,116,34],'job-tag'),(8,[x+129,156,124,30],'rarity'),(9,[x+139,205,24,15],'wage-coin'),(10,[x+18,282,228,52],'hire')]:u.append(use(es[idx],r,key+'-'+role,10 if idx==5 else 20))
  src=ART/'clothes/busts'/('v2-rbust-'+key+'.png');sz=k.fit_size(Image.open(src),(104,142));r=[x+17+(104-sz[0])//2,85+142-sz[1],*sz]
  u.append(external(src,r,key+'-restaurant-bust'))
  src=EX/'s9/jobs'/('v2-s9-job-'+s['icon']+'.png');sz=k.fit_size(Image.open(src),(23,23));u.append(external(src,[x+141,120+(23-sz[1])//2,*sz],key+'-job-icon'))
  ts += [label(key+'-name',s['name'],[x+136,81,112,30],27),label(key+'-job',s['job'],[x+169,119,77,26],18),label(key+'-rarity',s['rarity'],[x+141,159,100,23],15,'center','#FFF4DC'),label(key+'-wage',str(s['wage'])+' / night',[x+169,198,82,29],17),label(key+'-trait',s['trait'],[x+18,245,228,25],18,'center'),label(key+'-hire','Hire',[x+34,293,196,29],25,'center','#FFF4DC')]
  hits[key+'-hire']=[x+18,282,228,52]
 for e in es:
  places=[p for p in u if p['name']==e['name']];e['rect']=places[0]['rect'];e['uses']=[p['use'] for p in places]
 lay=dict(screen='hire',canvas=[844,390],background=str((EX/'s9/v2-s9-background.png').relative_to(ROOT)),backgroundSha256=k.sha(EX/'s9/v2-s9-background.png'),concept='ui-17-hire.png',placements=u,hitRects=hits,notes='All names, jobs, rarity, wages, traits and wallet numbers are live sample content. Fixed jobs follow accepted bust manifest. This screen proposes presentation only; it adds no hiring economy, candidate rotation, duplicate crew or wage rules. Rarity uses a shared blank ribbon; label conveys rarity without colour dependency. All 3 repeated uses are listed. Icons come from accepted S9/jobs.')
 for t in ts:
  t.update(stroke_fill=None,shadow=dict(offset=[0,0],fill='#00000000'),textMode='live; sample content only')
 m.meta(P,es,[lay],ts)
 # Full-row contact prevents large background/card overlaps.
 rows=[max(62,e['logicalSize'][1]+40) for e in es];im=Image.new('RGB',(1000,sum(rows)+10),'#EAE3D4');d=ImageDraw.Draw(im);y=6
 for e,h in zip(es,rows):
  d.text((12,y),e['name']+' / actual 1x',font=ImageFont.truetype(str(k.FONT),14),fill='#173F57');a=Image.open(P/e['file']).convert('RGBA').resize(tuple(e['logicalSize']),Image.Resampling.LANCZOS);im.paste(a,(12,y+25),a);y+=h
 im.save(P/'contact-sheet.jpg',quality=96)
 proof=Image.new('RGBA',(860*3,430*3),'#EAE3D4')
 for r in [[16,12,264,280],[300,12,220,360]]:m.put(proof,P,es[5],r)
 for r in [[552,28,124,30],[552,84,190,30]]:m.put(proof,P,es[8],r)
 for r in [[550,160,228,52],[550,240,280,52]]:m.put(proof,P,es[10],r)
 proof.resize((860,430),Image.Resampling.LANCZOS).convert('RGB').save(P/'slice-proof.jpg',quality=96)
 dump(P/'sample-data.json',dict(illustrative=True,notGameplayRules=True,wallet=1240,candidates=samples,note='Accepted identities and fixed jobs; values and traits are placeholders for the lead to bind. No production hiring data changed.'))
 print('Packaged hiring board:',len(es),'exports;',len(ts),'live labels')
def guests():
 contracts=k.load(X/'descriptions.json');es=[]
 for id,desc in sorted(contracts.items()):
  src=X/'provenance'/('guest-'+id+'.png');im=Image.open(src).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda a:a if a>=24 else 0));box=im.getchannel('A').getbbox();assert box
  cut=im.crop(box).resize((192,192),Image.Resampling.LANCZOS)
  for _ in range(5):
   cut.putalpha(cut.getchannel('A').point(lambda a:a if a>=24 else 0));b=cut.getchannel('A').getbbox()
   if b==(0,0,192,192):break
   cut=cut.crop(b).resize((192,192),Image.Resampling.LANCZOS)
  assert cut.getchannel('A').getbbox()==(0,0,192,192)
  assert all(cut.getpixel(p)[3]==0 for p in [(0,0),(191,0),(0,191),(191,191)])
  path=G/('v2-guest-'+id+'.png');cut.save(path)
  es.append(dict(name=id,file=path.name,size=[192,192],logicalSize=[64,64],intendedMaxUI=[64,64],crop=list(box),description=desc,reference='Art/Source/Restaurant/clothes/guests/v2-guest-hazel.png',referenceSha256=k.sha(G/'v2-guest-hazel.png'),sha256=k.sha(path),source=str(src.relative_to(ROOT)),sourceSha256=k.sha(src),native3xDetailClaim=False,method='Built-in ImageGen; requested mechanical alpha crop/192px Lanczos only. Generated circular alpha retained. No 3D identity match claimed for these additional guests.'))
 old=k.load(P/'guest-manifest-before.json');dump(G/'manifest.json',old+es);dump(X/'manifest.json',es);dump(X/'text-styles.json',dict(styles=[],notes='No labels baked into portraits; contact labels are review-only.'))
 dump(X/'layout.json',dict(logicalSize=[64,64],exportSize=[192,192],anchor='centre',reviewSlot='S5 review face',pieces=[dict(name='v2-guest-'+e['name'],file='../'+e['file'],rect=[0,0,64,64],use='review-'+e['name']) for e in es],notes='Each portrait is an alternative for the same live guest review slot. 09-11 family;12 tourist;13 fisherman;14 young diner;15-16 elegant couple. New guests are source-art concepts, no production guest roster change.'))
 out=Image.new('RGB',(1120,690),'#F4EFE3');d=ImageDraw.Draw(out);font=ImageFont.truetype(str(k.FONT),19);small=ImageFont.truetype(str(k.FONT),14)
 tags=['Mother','Father','Daughter','Tourist','Fisherman','Young diner','Elegant woman','Elegant man']
 for i,e in enumerate(es):
  x=(i%4)*280;y=(i//4)*345;a=Image.open(G/e['file']);d.text((x+15,y+8),e['name']+' / '+tags[i],font=font,fill='#173F57');out.paste(a,(x+44,y+42),a)
  for sz,xx in [(64,x+65),(32,x+157)]:b=a.resize((sz,sz),Image.Resampling.LANCZOS);out.paste(b,(xx,y+249),b)
  d.text((x+54,y+319),'64px / 32px UI review',font=small,fill='#173F57')
 out.save(G/'contact-sheet-extra.jpg',quality=97)
 print('Packaged',len(es),'new guest portraits; preserved',len(old),'accepted entries')
if __name__=='__main__':
 baseline();mode=sys.argv[1] if len(sys.argv)>1 else 'a'
 if mode=='a':board()
 elif mode=='b':guests()
