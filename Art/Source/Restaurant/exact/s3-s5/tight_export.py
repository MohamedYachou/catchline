"""Mechanical art-bounds copies requested by Claude; no new painted content."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,math,hashlib
R=Path(__file__).resolve().parent
M=json.loads((R/'manifest.json').read_text())
L=json.loads((R/'layout.json').read_text())
(R/'tight').mkdir(exist_ok=True)
records=[]; tiles=[]
try: font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
except OSError: font=ImageFont.load_default()
for e in M:
    p=R/(e['name']+'.png')
    with Image.open(p) as source:
        im=source.convert('RGBA')
    bounds=(0,0,*im.size) if e['opaque'] else im.getchannel('A').point(lambda a:255 if a>=8 else 0).getbbox()
    cut=im.crop(bounds)
    required=[e['rect'][2]*3,e['rect'][3]*3]
    for placement in L['repeated_instances']:
        if placement['name']==e['name']:
            required=[max(required[i],placement['rect'][i+2]*3) for i in range(2)]
    scale=max(1,required[0]/cut.width,required[1]/cut.height)
    size=(math.ceil(cut.width*scale),math.ceil(cut.height*scale))
    out=cut.resize(size,Image.Resampling.LANCZOS) if size!=cut.size else cut
    dest=R/'tight'/(e['name']+'.png'); temporary=dest.with_suffix('.tmp')
    out.save(temporary,format='PNG');temporary.replace(dest)
    body=e.setdefault('body_borders',e['borders'])
    borders=None
    if body:
        # Conservative corner/header reserves on the actual artwork. A tiny
        # horizontal track must leave at least two central pixels stretchable.
        b=[min(body[i],max(0,(cut.size[i%2]-2)//2)) for i in range(4)]
        borders=[round(b[i]*size[i%2]/cut.size[i%2]) for i in range(4)]
        e['borders']=[b[0]+bounds[0],b[1]+bounds[1],b[2]+im.width-bounds[2],b[3]+im.height-bounds[3]]
        assert e['borders'][0]+e['borders'][2]<im.width
        assert e['borders'][1]+e['borders'][3]<im.height
    digest=hashlib.sha256(dest.read_bytes()).hexdigest()
    records.append(dict(name=e['name'],file='tight/'+e['name']+'.png',screen=e['screen'],rect=e['rect'],
        size=list(size),borders=borders,canonical_size=list(im.size),canonical_crop=list(bounds),
        uniform_resample=scale,sha256=digest,required_minimum=required))
    assert out.width>=required[0] and out.height>=required[1]
    # Compare each import file with its actual reference, not an invented view.
    tile=Image.new('RGB',(1200,350),'#20394a');d=ImageDraw.Draw(tile)
    d.text((12,5),e['name']+' | actual mockup crop / tight import',fill='#fff4df',font=font)
    with Image.open(e['crop']) as ref:
        for x,img in [(12,ref.convert('RGBA')),(612,out)]:
            thumb=ImageOps.contain(img,(576,305),Image.Resampling.LANCZOS)
            tile.paste(thumb,(x+(576-thumb.width)//2,35+(305-thumb.height)//2),thumb.getchannel('A'))
    tiles.append(tile)
(R/'manifest.json').write_text(json.dumps(M,indent=2))
(R/'tight-layout.json').write_text(json.dumps(dict(canvas=[844,390],origin='top-left',
    purpose='Claude art-bounds import; same sprite names as canonical files',assets=records,
    repeated_instances=L['repeated_instances'],native_detail='Resampling disclosed per asset; no new painted detail'),indent=2))
index=[]
for start in range(0,len(tiles),6):
    count=min(6,len(tiles)-start);sheet=Image.new('RGB',(1200,350*count),'#20394a')
    for i,t in enumerate(tiles[start:start+count]):sheet.paste(t,(0,i*350))
    filename=f'tight-pass-{start//6+1:02}.png'
    sheet.save(R/'review'/filename)
    index.append(dict(sheet=filename,names=[e['name'] for e in records[start:start+count]],
        hashes={e['name']:e['sha256'] for e in records[start:start+count]}))
(R/'review/tight-pass-index.json').write_text(json.dumps(index,indent=2))
print('90 art-bounds exports, 15 actual-crop contacts, slices and repeat dimensions checked')
