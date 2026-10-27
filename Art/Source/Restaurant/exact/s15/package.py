"""Source-art packaging only: crop generated alpha, resize, composite and audit.
No procedural illustration. Run with uv run --with pillow python package.py MODE.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json, hashlib, shutil, sys, math
P=Path(__file__).resolve().parent
ROOT=next(p for p in P.parents if (p/'Assets').exists())
ART=ROOT/'Art/Source/Restaurant'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def clean(p):
    im=Image.open(p).convert('RGBA')
    # Remove only near-invisible fringe, retain painted translucent steam.
    im.putalpha(im.getchannel('A').point(lambda a: a if a>=8 else 0))
    box=im.getchannel('A').getbbox(); assert box
    return im.crop(box),box
def export(raw,out,size):
    im,box=clean(raw);native=im.size
    im=im.resize(size,Image.Resampling.LANCZOS)
    im.putalpha(im.getchannel('A').point(lambda a: a if a>=2 else 0))
    # Resample can produce an empty outer row. Tight alpha is authoritative.
    im=im.crop(im.getchannel('A').getbbox())
    if im.size!=size: im=im.resize(size,Image.Resampling.LANCZOS)
    im.save(out)
    assert im.getchannel('A').getbbox()==(0,0,*im.size),(out,im.getbbox())
    return dict(sourceSize=list(Image.open(raw).size),sourceAlphaCrop=list(box),nativeCropSize=list(native),sourceSha256=sha(raw))
FONT=ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf'
def label(im,text,rect,size=16,fill='#173f57',stroke=0):
    x,y,w,h=rect; d=ImageDraw.Draw(im);f=ImageFont.truetype(str(FONT),size)
    b=d.textbbox((0,0),text,font=f,stroke_width=stroke)
    assert b[2]-b[0]<=w and b[3]-b[1]<=h,(text,rect,b)
    d.text((x-b[0],y+(h-b[3]+b[1])/2-b[1]),text,font=f,fill=fill,stroke_width=stroke,stroke_fill='#173f57')
def contact(folder,entries,name='contact-sheet.jpg',cols=4,cell=(300,230)):
    rows=math.ceil(len(entries)/cols);im=Image.new('RGB',(cols*cell[0],rows*cell[1]),'#eae3d4');d=ImageDraw.Draw(im)
    for k,e in enumerate(entries):
        x=(k%cols)*cell[0];y=(k//cols)*cell[1]
        art=ImageOps.contain(Image.open(folder/e['file']).convert('RGBA'),(cell[0]-24,cell[1]-66))
        im.paste(art,(x+(cell[0]-art.width)//2,y+12),art)
        f=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
        d.text((x+8,y+cell[1]-46),e['name'],font=f,fill='#173f57')
        tiny=ImageOps.contain(Image.open(folder/e['file']).convert('RGBA'),(30,30));im.paste(tiny,(x+cell[0]-38,y+cell[1]-35),tiny)
    im.save(folder/name,quality=95)
def entry(folder,name,rect,raw,screen,**extra):
    file=name+'.png'; meta=export(raw,folder/file,(rect[2]*3,rect[3]*3))
    return dict(name=name,file=file,screen=screen,rect=rect,size=[rect[2]*3,rect[3]*3],borders=None,border_order='left,bottom,right,top',sha256=sha(folder/file),provenance=dict(method='built-in ImageGen; mechanical alpha crop and resize',**meta),native3xDetailClaim=False,**extra)
def weather():
    p=ART/'exact/s12'; w=p/'weather'; w.mkdir(exist_ok=True)
    manifest=p/'manifest.json';baseline=w/'baseline-manifest.json'
    if not baseline.exists():shutil.copy2(manifest,baseline)
    base=read(baseline);sun=next(e for e in base if e['name']=='v2-s12-forecast');entries=[]
    for kind in ['rain','cloud','storm']:
        entries.append(entry(p,'v2-s12-weather-'+kind,sun['rect'],w/'provenance'/f'{kind}.png',12,usage='Interchangeable with v2-s12-forecast; preserve aspect; same logical rect. Cloud/storm are art availability, not new weather rules.'))
    dump(manifest,base+entries);dump(w/'manifest.json',entries)
    contact(p,[sun]+entries,'weather/contact-sheet.jpg',4,(300,230))
    proof=Image.new('RGB',(844,390),'#eae3d4')
    for k,e in enumerate([sun]+entries):
        mock=Image.open(ART/'concepts/ui-12-sleep.png').convert('RGB')
        strip=next(a for a in base if a['name']=='v2-s12-tomorrow-strip');sx,sy,sw,sh=strip['rect']
        blank=Image.open(p/strip['file']).convert('RGBA').resize((sw,sh),Image.Resampling.LANCZOS)
        # Restore underlying accepted blank strip before replacing the sun, so no old rays show through.
        cleanback=blank.crop((426-sx,225-sy,455-sx,251-sy));mock.paste(cleanback,(426,225),cleanback)
        im=Image.open(p/e['file']);im.thumbnail((29,26));mock.paste(im,(426,225),im)
        thumb=mock.resize((422,195),Image.Resampling.LANCZOS);proof.paste(thumb,((k%2)*422,(k//2)*195))
    proof.save(w/'context-review.jpg',quality=95)
    assert all(sha(p/e['file'])==e['sha256'] for e in base)
    dump(w/'audit.json',dict(status='PASS',exports=len(entries),acceptedSpritesPreserved=len(base),logicalRect=sun['rect'],size=sun['size'],nativeRuntimeVerified=False))
    print('Weather PASS:3 exports, accepted sprites preserved')

def markers():
    raw=P/'provenance'; entries=[];placements=[]
    specs={
      'order-bubble':[396,136,66,52],
      'patience-track':[403,183,44,44],
      'patience-fill':[403,183,44,44],
      'tip-pop':[463,203,30,34],
      'question-bubble':[580,146,36,39],
      'broken-warning':[320,66,28,28],
      'task-cook':[191,83,24,24],
      'task-chop':[253,81,24,24],
      'task-wash':[333,82,24,24],
      'task-repair':[414,94,24,24],
      'task-take-order':[457,171,24,24],
      'task-greet':[604,225,24,24],
      'task-wipe':[194,234,24,24],
      'task-pour':[577,213,24,24],
      'task-carry-plate':[364,231,24,24],
    }
    for k,(id,rect) in enumerate(specs.items()):
        if not id.startswith('patience'):
            art,_=clean(raw/(id+'.png'));scale=min(rect[2]/art.width,rect[3]/art.height);w=max(1,round(art.width*scale));h=max(1,round(art.height*scale));rect=[rect[0]+(rect[2]-w)//2,rect[1]+(rect[3]-h)//2,w,h]
        e=entry(P,'v2-s15-'+id,rect,raw/(id+'.png'),15)
        if id.startswith('patience'):
            e.update(radial=dict(origin='top',clockwise=True,pivot=[.5,.5],sourceFullCircle=True,fit='square; track and fill share exact rect',clip='fill only; track always complete'))
        entries.append(e)
        placements.append(dict(name=e['name'],screen=15,use='demo',rect=rect,z=20+k))
    # Steam is one generated 4-frame strip. Preserve frame origins; no arbitrary per-frame stretching.
    steam,box=clean(raw/'steam-strip.png');sw,sh=steam.size
    assert sw>sh*2,('Expected horizontal four-frame original',steam.size)
    cells=[]
    for k in range(4):
        frame=steam.crop((round(k*sw/4),0,round((k+1)*sw/4),sh));b=frame.getchannel('A').getbbox();assert b
        cells.append(frame)
    strip=Image.new('RGBA',(768,192))
    for k,cell in enumerate(cells):
        fitted=ImageOps.contain(cell,(192,192),Image.Resampling.LANCZOS);strip.alpha_composite(fitted,(k*192+(192-fitted.width)//2,192-fitted.height))
    strip.save(P/'v2-s15-steam-strip.png')
    e=dict(name='v2-s15-steam-strip',file='v2-s15-steam-strip.png',screen=15,rect=[0,0,256,64],size=[768,192],borders=None,sha256=sha(P/'v2-s15-steam-strip.png'),provenance=dict(source='provenance/steam-strip.png',sourceSha256=sha(raw/'steam-strip.png'),sourceAlphaCrop=box,sourceSize=[sw,sh],method='generated horizontal4frame strip; mechanical crop/resample'),native3xDetailClaim=False,animation=dict(frames=4,frameSize=[192,192],frameRects=[[k*192,0,192,192] for k in range(4)],origin='bottom-centre',secondsPerFrame=.16,loopSeconds=.64,layoutPadding='Fixed equal cells intentionally retain internal alpha for consistent animation origins'))
    entries.append(e);placements.append(dict(name=e['name'],screen=15,use='demo-steam',rect=[267,110,30,30],sourceFrame=1,z=45))
    dump(P/'manifest.json',entries)
    dump(P/'layout.json',dict(screen=15,canvas=[844,390],origin='top-left',background='../../concepts/ui-2-service.png',backgroundSha256=sha(ART/'concepts/ui-2-service.png'),placements=placements,externalInserts=[dict(file='../s3-s5/v2-dish-grilled-fish.png',rect=[411,145,38,27],use='demo order slot',z=50)],notes='Marker demonstration only; live anchors must follow world positions. Original HUD is unmodified outside overlays.'))
    styles=[dict(id='tip-value',screen=15,text='+12',rect=[491,204,42,24],font='Fredoka-Bold',weight=700,size=20,fill='#FFF1CF',stroke='#173F57',stroke_width=1,align='left',vertical_align='middle')]
    dump(P/'text-styles.json',dict(screen=15,canvas=[844,390],styles=styles));dump(P/'slices.json',dict(border_order='left,bottom,right,top',sprites=[],notes='Icons preserve aspect. Bubble fixed at reference size. Ring uses radial fill; steam uses frame rects, never9slice.'))
    im=Image.open(ART/'concepts/ui-2-service.png').convert('RGBA').resize((2532,1170),Image.Resampling.NEAREST)
    for pl in sorted(placements,key=lambda e:e['z']):
        e=next(e for e in entries if e['name']==pl['name']);s=Image.open(P/e['file']).convert('RGBA');x,y,w,h=pl['rect']
        if 'sourceFrame' in pl:
            q=pl['sourceFrame'];s=s.crop((q*192,0,(q+1)*192,192))
        if e['name'].endswith('patience-fill'):
            # Offline demonstration of Unity-style radial fill; original full-ring export remains intact.
            mask=Image.new('L',s.size);ImageDraw.Draw(mask).pieslice((0,0,s.width-1,s.height-1),-90,165,fill=255)
            from PIL import ImageChops
            s.putalpha(ImageChops.multiply(s.getchannel('A'),mask))
        s=s.resize((w*3,h*3),Image.Resampling.LANCZOS);im.alpha_composite(s,(x*3,y*3))
    dish=Image.open(ART/'exact/s3-s5/v2-dish-grilled-fish.png').convert('RGBA');dish=ImageOps.contain(dish,(114,81),Image.Resampling.LANCZOS);im.alpha_composite(dish,(411*3,145*3))
    for t in styles:label(im,t['text'],[a*3 for a in t['rect']],t['size']*3,t['fill'],3)
    im.save(P/'reconstructed-3x.png');concept=ART/'concepts/ui-15-markers.png';im.resize((844,390),Image.Resampling.LANCZOS).convert('RGB').save(concept)
    contact(P,entries,cols=4,cell=(340,220))
    proof=Image.new('RGB',(1060,400),'#eae3d4')
    for k in range(4):
        frame=strip.crop((k*192,0,(k+1)*192,192));proof.paste(frame,(20+k*260,35),frame)
        label(proof,str(k+1),[20+k*260,250,200,30],20)
    proof.save(P/'steam-review.jpg',quality=95)
    # Radial mask proof at full, 3/4, half, 1/4 and empty, all using shared square rect.
    proof=Image.new('RGB',(1000,240),'#eae3d4');track=Image.open(P/'v2-s15-patience-track.png').resize((140,140));fill=Image.open(P/'v2-s15-patience-fill.png').resize((140,140))
    from PIL import ImageChops
    for k,amount in enumerate([1,.75,.5,.25,0]):
        proof.paste(track,(k*200+30,30),track);mask=Image.new('L',fill.size)
        if amount:ImageDraw.Draw(mask).pieslice((0,0,139,139),-90,-90+360*amount,fill=255)
        f=fill.copy();f.putalpha(ImageChops.multiply(f.getchannel('A'),mask));proof.paste(f,(k*200+30,30),f)
        label(proof,str(int(amount*100))+'%',[k*200+60,185,130,35],24)
    proof.save(P/'radial-review.jpg',quality=95)
    for e in entries:
        a=Image.open(P/e['file']);assert a.mode=='RGBA';assert a.size==tuple(e['size']);assert a.getchannel('A').getextrema()[0]==0
        if 'animation' not in e:assert a.getchannel('A').getbbox()==(0,0,*a.size)
    dump(P/'audit.json',dict(status='PASS',sprites=len(entries),tasks=9,steamFrames=4,placements=len(placements),canvas=[844,390],conceptSha256=sha(concept),nativeRuntimeVerified=False))
    print('Markers PASS:',len(entries),'sprites/9tasks/4steamframes')

def busts():
    p=ART/'clothes/busts';raw=p/'provenance';raw.mkdir(exist_ok=True)
    ids=['mira','noor','tess','rosa','ana','lise','ines','tove','kofi','sam','jo','bram','olaf','yusuf']
    generated={'tess','ana','jo','bram','yusuf'}
    jobs={'mira':'Reception','noor':'Waiter','tess':'Cook','rosa':'Cook','ana':'Waiter','lise':'Cook','ines':'Barista','tove':'Waiter','kofi':'Cook','sam':'Waiter','jo':'Waiter','bram':'Waiter','olaf':'Handyman','yusuf':'Waiter'}
    records=[]
    for id in ids:
        source=raw/(id+'.png')
        if id not in generated:
            accepted=ART/'clothes/2d'/f'{"mira-d" if id=="mira" else id}-bust.png';shutil.copy2(accepted,source)
        art,box=clean(source);scale=768/max(art.size);size=tuple(round(v*scale) for v in art.size)
        name='v2-rbust-'+id;file=name+'.png';meta=export(source,p/file,size)
        srcIdentity=ROOT/f'Assets/Art/UI/v2-portrait-{id}-deck.png'
        records.append(dict(name=name,file=file,id=id,job=jobs[id],jobAuthority='Current assignment wardrobe; absent Cards.All, provisional front-of-house portrait only' if id in {'bram','yusuf'} else ('Current assignment explicitly requests male waiter outfit' if id=='jo' else 'Cards.All role with RestaurantData.NativeJob and Mira/Ines overrides'),size=list(size),logicalBox=[256,256],fit='Contain without distortion; anchor bottom-centre. Tight individual alpha; no square canvas padding.',sha256=sha(p/file),sourceIdentity=str(srcIdentity.relative_to(ROOT)),sourceIdentitySha256=sha(srcIdentity),provenance=dict(source='provenance/'+source.name,method='built-in ImageGen corrective restaurant bust' if id in generated else 'accepted restaurant bust reuse; mechanical alpha crop/resample',**meta),native3xDetailClaim=False))
    dump(p/'manifest.json',dict(artOnly=True,tool='built-in ImageGen + accepted paintings',logicalBox=[256,256],records=records))
    contact(p,records,cols=7,cell=(280,350))
    proof=Image.new('RGB',(1680,1000),'#eae3d4');d=ImageDraw.Draw(proof)
    for k,e in enumerate(records):
        x=k%7*240;y=k//7*500
        before=ImageOps.contain(Image.open(ROOT/e['sourceIdentity']).convert('RGBA'),(105,210));proof.paste(before,(x+5,y+35),before)
        after=ImageOps.contain(Image.open(p/e['file']).convert('RGBA'),(125,230));proof.paste(after,(x+110,y+35),after)
        label(proof,e['id'],[x+5,y+290,230,28],22)
        label(proof,e['job'],[x+5,y+325,230,25],16)
        for q,target in enumerate([32,64,88]):
            a=ImageOps.contain(Image.open(p/e['file']).convert('RGBA'),(target,target));proof.paste(a,(x+5+q*75,y+370),a)
    proof.save(p/'identity-and-size-review.jpg',quality=95)
    for e in records:
        a=Image.open(p/e['file']);assert a.mode=='RGBA' and a.getchannel('A').getbbox()==(0,0,*a.size)
        assert min(a.size)>=264 and max(a.size)==768
    dump(p/'audit.json',dict(status='PASS',exports=len(records),ids=ids,referenceFrame='rc-bust-mira-d; tight head/shoulders/upper chest',sourceIdentityHashes=True,alphaTight=True,nativeRuntimeVerified=False))
    print('Busts PASS:14 tight RGBA exports; identity and32/64/88px proof')

if __name__=='__main__':
    globals()[sys.argv[1]]()
