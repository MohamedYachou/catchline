"""Mechanical crop/scale/metadata/review only. Art is authored by ImageGen.
Usage: handoff.py <screen-folder> prepare|finish
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json, sys, math, hashlib
P=Path(sys.argv[1]).resolve(); mode=sys.argv[2]
S=json.loads((P/'spec.json').read_text(encoding='utf-8'))
N=S['screen']; prefix=f'v2-s{N}-'
ROOT=next(p for p in P.parents if (p/'Assets').exists())
source=Image.open(P/'provenance/mockup.png').convert('RGBA')
def dump(name,value): (P/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def crop(rect):
    x,y,w,h=rect
    return source.crop((round(x*source.width/844),round(y*source.height/390),round((x+w)*source.width/844),round((y+h)*source.height/390)))
def rectcheck(r):
    x,y,w,h=r; assert min(x,y)>=0 and w>0 and h>0 and x+w<=844 and y+h<=390,r
for j in S['pieces']:
    rectcheck(j['rect']);j['name']=prefix+j['id']
placements=[]
for j in S['pieces']:
    placements.append(dict(name=j['name'],screen=N,use='primary',rect=j['rect'],z=j.get('z',20)))
    for use in j.get('uses',[]): placements.append(dict(name=j['name'],screen=N,**use,z=j.get('z',20)))
for p in placements:rectcheck(p['rect'])
assert len({(p['name'],p['use']) for p in placements})==len(placements)
styles=[]; fp=str(ROOT/'Assets/Resources/Fonts/Fredoka-Bold.ttf')
for i,t in enumerate(S['texts']):
    ident,value,rect,size,*color=t;rectcheck(rect)
    fill=color[0] if color else '#10263D';stroke=1 if fill.startswith('#FFF') else 0
    fitted=1
    for v in range(1,72):
        b=ImageFont.truetype(fp,v).getbbox(value,stroke_width=stroke)
        if b[2]-b[0]<=rect[2] and b[3]-b[1]<=rect[3]:fitted=v
    fitted=min(fitted,size)
    styles.append(dict(id=ident,screen=N,text=value,rect=rect,size=fitted,painted_size_estimate=size,font='Fredoka Bold',weight=700,fill=fill,stroke='#10263D',stroke_width=stroke,shadow=[0,0,'#00000000'],align='left',vertical_align='middle'))
assert len({t['id'] for t in styles})==len(styles)
dump('layout.json',dict(screen=N,canvas=[844,390],origin='top-left',sourceSize=source.size,placements=sorted(placements,key=lambda p:p['z'])))
dump('text-styles.json',dict(screen=N,canvas=[844,390],styles=styles,fontIdentification='closest supplied face, calibrated to measured regions; painted lettering not proven identical'))
(P/'references').mkdir(exist_ok=True)
for j in S['pieces']:crop(j['rect']).save(P/'references'/(j['name']+'.png'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for kind,items in [('layout',placements),('text',styles)]:
    for start in range(0,len(items),18):
        im=source.resize((1688,780)).convert('RGB');d=ImageDraw.Draw(im)
        for i,it in enumerate(items[start:start+18]):
            x,y,w,h=it['rect'];col=['#FF0088','#00FF77','#FFAA00','#00DDFF'][i%4]
            d.rectangle((x*2,y*2,(x+w)*2,(y+h)*2),outline=col,width=2)
            d.text((x*2,max(0,y*2-14)),str(start+i+1),font=font,fill=col)
        im.save(P/f'{kind}-measure-{start//18+1}.jpg',quality=93)
if mode=='prepare':
    print(json.dumps(dict(screen=N,pieces=len(S['pieces']),placements=len(placements),text=len(styles),source=source.size)));sys.exit()
manifest=[]
for j in S['pieces']:
    if 'copy' in j:
        path=ROOT/j['copy'];im=Image.open(path).convert('RGBA');original=im.size;bb=im.getchannel('A').getbbox();im=im.crop(bb)
        origin=dict(method='unchanged accepted artwork, mechanical alpha crop/resize',source=str(path),sha256=sha(path))
    else:
        path=P/'provenance'/j['atlas'];atlas=Image.open(path).convert('RGBA')
        col,row,cols,rows=j.get('cell',[0,0,1,1]);box=j.get('sourceBox',(round(col*atlas.width/cols),round(row*atlas.height/rows),round((col+1)*atlas.width/cols),round((row+1)*atlas.height/rows)))
        im=atlas.crop(box);original=im.size
        if not j.get('opaque'):im.putalpha(im.getchannel('A').point(lambda a:a if a>=32 else 0))
        bb=im.getchannel('A').getbbox();assert bb,j['id'];im=im.crop(bb)
        origin=dict(method='ImageGen isolation/text removal; grid cell then visible-alpha crop; alpha<32 removed; Lanczos to 3x largest use',source=path.name,sourceSize=atlas.size,cellPixelRect=box,sha256=sha(path))
    uses=[p for p in placements if p['name']==j['name']]
    target=(3*max(p['rect'][2] for p in uses),3*max(p['rect'][3] for p in uses))
    im=im.resize(target,Image.Resampling.LANCZOS)
    for _ in range(6):
        if not j.get('opaque'):im.putalpha(im.getchannel('A').point(lambda a:a if a>=32 else 0))
        b=im.getchannel('A').getbbox()
        if b==(0,0,*im.size):break
        im=im.crop(b).resize(target,Image.Resampling.LANCZOS)
    assert im.getchannel('A').getbbox()==(0,0,*im.size),j['id']
    assert j.get('opaque') or im.getchannel('A').getextrema()[0]==0,j['id']
    out=P/(j['name']+'.png');im.save(out,optimize=True)
    borders=[v*3 for v in j['slice']] if 'slice' in j else None
    if borders:
        l,b,r,t=borders;assert l+r<im.width and b+t<im.height
    manifest.append(dict(name=j['name'],file=out.name,screen=N,rect=j['rect'],size=im.size,borders=borders,border_order='left,bottom,right,top',opaque=bool(j.get('opaque')),alphaCrop=bb,sourceCellSize=original,provenance=origin,sha256=sha(out),native3xDetailClaim=False,pixelExactClaim=False))
dump('manifest.json',manifest)
dump('slices.json',[m for m in manifest if m['borders']])
for start in range(0,len(manifest),6):
    page=Image.new('RGB',(1440,900),'#E9E2D2');d=ImageDraw.Draw(page)
    for i,m in enumerate(manifest[start:start+6]):
        x=i%3*480;y=i//3*450
        d.text((x+12,y+8),m['name'],font=font,fill='#10263D')
        a=ImageOps.contain(Image.open(P/'references'/(m['name']+'.png')),(450,170));page.paste(a,(x+15+(450-a.width)//2,y+40),a)
        for yy in range(y+225,y+415,12):
            for xx in range(x+12,x+468,12):d.rectangle((xx,yy,xx+11,yy+11),fill=['#A4B5BE','#DAE1E3'][((xx-x)//12+(yy-y)//12)%2])
        a=ImageOps.contain(Image.open(P/m['file']),(450,175));page.paste(a,(x+15+(450-a.width)//2,y+230+(175-a.height)//2),a)
        d.text((x+12,y+424),str(m['size'])+' | crop above / export below',font=font,fill='#10263D')
    page.save(P/f'review-{start//6+1}.jpg',quality=94)
im=Image.new('RGBA',(2532,1170))
for p in sorted(placements,key=lambda p:p['z']):
    sp=Image.open(P/(p['name']+'.png'));x,y,w,h=p['rect'];sp=sp.resize((w*3,h*3),Image.Resampling.LANCZOS)
    if p.get('flipX'):sp=ImageOps.mirror(sp)
    im.alpha_composite(sp,(x*3,y*3))
d=ImageDraw.Draw(im)
for t in styles:
    x,y,w,h=t['rect'];f=ImageFont.truetype(fp,t['size']*3);sw=t['stroke_width']*3;b=d.textbbox((0,0),t['text'],font=f,stroke_width=sw)
    d.text((x*3-b[0],y*3+(h*3-b[3]+b[1])//2-b[1]),t['text'],font=f,fill=t['fill'],stroke_width=sw,stroke_fill=t['stroke'])
im.save(P/'reconstructed-3x.png',optimize=True)
page=Image.new('RGB',(1688,425),'#E9E2D2');d=ImageDraw.Draw(page)
d.text((12,5),'Painted reference',font=font,fill='#10263D');d.text((856,5),'Offline sprites + measured live text (not Unity)',font=font,fill='#10263D')
page.paste(source.resize((844,390)).convert('RGB'),(0,30));page.paste(im.resize((844,390)).convert('RGB'),(844,30));page.save(P/'reconstruction-compare.jpg',quality=94)
for m in manifest:
    a=Image.open(P/m['file']);assert a.mode=='RGBA' and a.getchannel('A').getbbox()==(0,0,*a.size)
    assert all(a.width>=3*p['rect'][2] and a.height>=3*p['rect'][3] for p in placements if p['name']==m['name'])
dump('audit.json',dict(screen=N,complete=True,sprites=len(manifest),placements=len(placements),textEntries=len(styles),allRectsNativeBounds=True,allUsesUnique=True,allTextIdsUnique=True,allExportsTightRGBA3x=True,slicedSprites=sum(bool(m['borders']) for m in manifest),visualReview='PENDING actual opens',hashes={m['file']:m['sha256'] for m in manifest}))
print(json.dumps(dict(screen=N,sprites=len(manifest),placements=len(placements),texts=len(styles),reviewPages=math.ceil(len(manifest)/6))))
