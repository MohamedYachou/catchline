"""Cross-file handoff checks and slice inventory; reads art only."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).resolve().parent
manifest=json.loads((P/'manifest.json').read_text())
layout=json.loads((P/'layout.json').read_text())
texts=json.loads((P/'text-styles.json').read_text(encoding='utf-8'))['styles']
names={j['name'] for j in manifest};assert len(manifest)==len(names)==31
assert len(layout['placements'])==51 and len(texts)==49
assert len({t['id'] for t in texts})==49
assert all(p['name'] in names and p.get('use') for p in layout['placements'])
assert all((P/'provenance'/(n+'-generated.json')).exists() for n in names)
layout['measured_assets']=[{k:j[k] for k in ['name','screen','rect','size','borders']} for j in manifest]
(P/'layout.json').write_text(json.dumps(layout,indent=2)+'\n')
for p in layout['placements']+texts:
    x,y,w,h=p['rect'];assert 0<=x<x+w<=844 and 0<=y<y+h<=390
others=[]
for f in P.parent.rglob('v2-s6-*.png'):
    if P not in f.parents and not {'references','provenance'}.intersection(f.parts):others.append(str(f))
assert not others,others
slices=[]
for j in manifest:
    if j['borders']:
        l,b,r,t=j['borders'];w,h=j['size']
        assert l+r<w and t+b<h
        slices.append(dict(name=j['name'],size=j['size'],borders=j['borders'],order='left,bottom,right,top',units='PNG pixels',mode='Sliced',referenceRect=j['rect']))
(P/'slices.json').write_text(json.dumps(slices,indent=2)+'\n')
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
for start in range(0,len(slices),8):
    page=Image.new('RGB',(1440,880),'#E9E2D2');d=ImageDraw.Draw(page)
    for k,s in enumerate(slices[start:start+8]):
        x=(k%2)*720;y=(k//2)*220
        d.text((x+10,y+5),s['name']+' L,B,R,T='+str(s['borders']),font=font,fill='#10263D')
        im=Image.open(P/(s['name']+'.png'));scale=min(670/im.width,170/im.height)
        target=(max(1,round(im.width*scale)),max(1,round(im.height*scale)))
        xx=x+20;yy=y+30;page.paste(im.resize(target,Image.Resampling.LANCZOS),(xx,yy),im.resize(target,Image.Resampling.LANCZOS))
        l,b,r,t=s['borders'];w,h=s['size']
        for lineX in [l,w-r]:d.line((xx+round(lineX*scale),yy,xx+round(lineX*scale),yy+target[1]),fill='#FF00DE',width=2)
        for lineY in [t,h-b]:d.line((xx,yy+round(lineY*scale),xx+target[0],yy+round(lineY*scale)),fill='#FF00DE',width=2)
    page.save(P/('slices-review-'+str(start//8+1)+'.jpg'),quality=94)
audit=json.loads((P/'audit.json').read_text());assert audit['complete']
audit.update(textEntries=49,uniqueTextIds=True,allRectsNativeBounds=True,allPlacementNamesResolve=True,allUsesNamed=True,externalFilenameCollisions=others,slicedSprites=len(slices),opaqueBackground=True,review='all31export/crop contacts;3layout overlays;3text overlays;offline reconstruction opened; no Unity acceptance',fileHashes={f:hashlib.sha256((P/f).read_bytes()).hexdigest() for f in ['manifest.json','layout.json','text-styles.json','slices.json']})
(P/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print(json.dumps({k:audit[k] for k in ['complete','completed','placements','textEntries','slicedSprites','externalFilenameCollisions']}))
