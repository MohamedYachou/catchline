"""Resume B without rerunning or replacing the accepted A text measurements."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, math, hashlib, shutil
R=Path(__file__).resolve().parent; S=R.parent/'s1-s2'; C=R.parents[1]/'concepts'
d=json.loads((S/'layout.json').read_text())
names=['icon-group','icon-order-dish','icon-tile1','icon-tile2','meter-ring-fill-orange','icon-cross']
for row in d['placements']:
    if row['asset']=='v2-icon-cross': row['asset']='v2-s12x-icon-cross'
records=[]
for short in names:
    key='v2-s12x-'+short; original='v2-'+short
    src=S/'provenance'/(original+'-generated.png')
    im=Image.open(src).convert('RGBA')
    # Remove only wholly transparent canvas. Keep every nonzero alpha pixel.
    box=im.getchannel('A').getbbox(); native=im.crop(box)
    uses=[p for p in d['placements'] if p['asset']==key]; assert uses,key
    mw=max(p['rect'][2]*3 for p in uses); mh=max(p['rect'][3]*3 for p in uses)
    scale=max(mw/native.width,mh/native.height)
    for _ in range(10):
        art=native.resize((math.ceil(native.width*scale),math.ceil(native.height*scale)),Image.Resampling.LANCZOS)
        art=art.crop(art.getchannel('A').getbbox())
        if art.width>=mw and art.height>=mh:break
        scale*=max(mw/art.width,mh/art.height)*1.01
    assert art.width>=mw and art.height>=mh
    art.save(R/(key+'.png'))
    shutil.copy2(S/'provenance'/(original+'-receipt.json'),R/(key+'-source-receipt.json'))
    records.append(dict(asset=key,source=str(src.relative_to(R.parents[4])),crop=list(box),size=list(art.size),minimum3x=[mw,mh],method='nonzero-alpha crop; uniform Lanczos resample; final nonzero-alpha crop',nativeDetailUpscaled=scale>1,sha256=hashlib.sha256((R/(key+'.png')).read_bytes()).hexdigest()))
    p=uses[0]; x,y,w,h=p['rect']; ref=Image.open(C/d['screens'][p['screen']]['file']).crop((x,y,x+w,y+h)).convert('RGBA')
    board=Image.new('RGB',(640,270),'#d4cec1')
    for n,img in enumerate((ref.copy(),art.copy())):
        img.thumbnail((295,215));board.paste(img,(n*320+(320-img.width)//2,12),img)
    ImageDraw.Draw(board).text((8,240),key+' | reference crop / export',fill='black')
    board.save(R/(key+'-compare.jpg'))
(S/'layout.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'crop-manifest.json').write_text(json.dumps(records,indent=2)+'\n')
(R/'slices.json').write_text(json.dumps({r['asset']:dict(sourceSize=r['size'],borderLTRB=[0,0,0,0],sliceMode='single; radial clipping at runtime for ring; never nine-slice') for r in records},indent=2)+'\n')
issues=[]; uses=set()
for p in d['placements']:
    x,y,w,h=p['rect']; sw,sh=d['screens'][p['screen']]['size']; k=(p['screen'],p['use'])
    if min(x,y)<0 or min(w,h)<=0 or x+w>sw or y+h>sh:issues.append(['bounds',p])
    if k in uses:issues.append(['duplicate use',k])
    uses.add(k)
    if not any((root/(p['asset']+'.png')).exists() for root in (R,S)):issues.append(['missing',p['asset']])
for r in records:
    im=Image.open(R/(r['asset']+'.png')); assert im.mode=='RGBA'; assert im.getchannel('A').getbbox()==(0,0,*im.size)
    assert im.getchannel('A').getextrema()[0]==0
audit=dict(placements=len(d['placements']),screens={s:sum(p['screen']==s for p in d['placements']) for s in d['screens']},newExports=6,allResolved=not issues,boundsAndUsesPass=not issues,newExports3xAndTightPass=True,issues=issues)
(R/'layout-audit.json').write_text(json.dumps(audit,indent=2)+'\n'); assert not issues,issues
print(json.dumps(audit))
