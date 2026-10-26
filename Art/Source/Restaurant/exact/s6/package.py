"""Mechanical alpha trimming, export scaling, metadata, review contacts and audit."""
import json,hashlib,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
jobs=json.loads((P/'jobs.json').read_text())
placements=json.loads((P/'layout.json').read_text())['placements']
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
titlefont=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',16)
manifest=[]
# Borders are L,B,R,T in export pixels, Unity convention. Logical margins below.
margins={'button-back':[15,14,15,14],'tab-selected':[15,13,15,13],'tab-idle':[14,12,14,12],
 'week-selector':[15,13,15,13],'panel':[19,16,19,20],'menu-row':[9,9,9,9],
 'income-summary':[9,8,9,8],'popularity-caption':[9,8,9,8],'upgrade-strip':[22,20,22,20],
 'button-upgrades':[27,22,27,22],'progress-track':[10,10,10,10],'progress-fill':[7,7,7,7],
 'bar-teal':[6,5,6,5],'bar-gold':[6,5,6,5],'divider-horizontal':[1,0,1,0],'divider-vertical':[0,1,0,1]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for j in jobs:
    raw=P/'provenance'/(j['name']+'-generated.png')
    if not raw.exists():continue
    im=Image.open(raw).convert('RGBA');rawsize=im.size
    # Generator outputs can contain alpha1..7 specks far outside visible art.
    # Remove that sub-3%-opacity export noise before measuring tight artwork bounds.
    if not j['opaque']:im.putalpha(im.getchannel('A').point(lambda a:a if a>=8 else 0))
    bbox=(0,0,*im.size) if j['opaque'] else im.getchannel('A').getbbox()
    if not bbox:raise ValueError('Empty '+j['name'])
    im=im.crop(bbox)
    uses=[p for p in placements if p['name']==j['name']]
    target=(3*max(p['rect'][2] for p in uses),3*max(p['rect'][3] for p in uses))
    im=im.resize(target,Image.Resampling.LANCZOS)
    # Resampling can create a transparent outer row. Trim before final size, then stretch
    # back to required dimensions; repeated until actual alpha bounds are the canvas.
    for _ in range(4):
        if not j['opaque']:im.putalpha(im.getchannel('A').point(lambda a:a if a>=8 else 0))
        bb=im.getchannel('A').getbbox()
        if bb==(0,0,*im.size):break
        im=im.crop(bb).resize(target,Image.Resampling.LANCZOS)
    assert im.getchannel('A').getbbox()==(0,0,*im.size)
    out=P/(j['name']+'.png');im.save(out,optimize=True)
    short=j['name'].removeprefix('v2-s6-')
    borders=[v*3 for v in margins[short]] if j['nineSlice'] else None
    if borders:assert borders[0]+borders[2]<im.width and borders[1]+borders[3]<im.height,(short,borders,im.size)
    item={**j,'file':out.name,'size':list(im.size),'borders':borders,'border_order':'left,bottom,right,top' if borders else None,
      'sourceGeneratedSize':rawsize,'alphaCrop':bbox,'alphaNoiseCutoff':8,'sourceSha256':sha(raw),'sha256':sha(out),'exportMethod':'imagegen text removal/isolation; discard alpha below8/255 export specks; visible-alpha trim; Lanczos to 3x largest measured use, no canvas padding','pixelExactClaim':False}
    manifest.append(item)
(P/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
for start in range(0,len(manifest),6):
    page=Image.new('RGB',(1440,900),'#E9E2D2');d=ImageDraw.Draw(page)
    for k,item in enumerate(manifest[start:start+6]):
        col=k%3;row=k//3;x=col*480;y=row*450
        d.text((x+12,y+8),item['name'],font=titlefont,fill='#10263D')
        d.text((x+12,y+30),'reference crop / isolated export',font=font,fill='#10263D')
        ref=Image.open(item['referenceCrop']).convert('RGBA');ref.thumbnail((450,165))
        page.paste(ref,(x+15+(450-ref.width)//2,y+55),ref)
        # Checkerboard makes true alpha visible.
        for cy in range(y+230,y+414,12):
            for cx in range(x+12,x+468,12):
                d.rectangle((cx,cy,cx+11,cy+11),fill=('#A4B5BE' if ((cx-x)//12+(cy-y)//12)%2 else '#DAE1E3'))
        sp=Image.open(P/item['file']);sp.thumbnail((450,178))
        page.paste(sp,(x+15+(450-sp.width)//2,y+232+(178-sp.height)//2),sp)
        d.text((x+12,y+422),str(item['size'])+' tight / 3x max use',font=font,fill='#10263D')
    page.save(P/('review-'+str(start//6+1)+'.jpg'),quality=94)
checks=[]
for item in manifest:
    im=Image.open(P/item['file']);uses=[p for p in placements if p['name']==item['name']]
    alpha=im.getchannel('A')
    assert im.mode=='RGBA'
    assert alpha.getbbox()==(0,0,*im.size)
    assert all(im.width>=3*p['rect'][2] and im.height>=3*p['rect'][3] for p in uses)
    if not item['opaque']:assert alpha.getextrema()[0]==0,item['name']
    else:assert alpha.getextrema()==(255,255),item['name']
    checks.append(dict(name=item['name'],rgba=True,tight=True,min3xEveryUse=True,uses=len(uses),sha256=sha(P/item['file'])))
(P/'audit.json').write_text(json.dumps(dict(expected=len(jobs),completed=len(manifest),placements=len(placements),complete=len(manifest)==len(jobs),checks=checks),indent=2)+'\n')
print(json.dumps(dict(expected=len(jobs),exported=len(manifest),reviewPages=math.ceil(len(manifest)/6))))
