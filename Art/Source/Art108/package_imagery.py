"""Self-contained SVG placement sources and correctly sized illustrated PNGs."""
from pathlib import Path
import sys,base64,io,json,hashlib
sys.path.insert(0,str(Path.home()/'.codex/tmp/art108-python'))
import resvg_py
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];SRC=ROOT/'Art/Source/Art108/imagery';GAME=ROOT/'Assets/Art/UI/v2'
rows=[]
for original in sorted(SRC.glob('*-original.png')):
    id=original.stem.replace('-original','')
    if id.startswith('texture-'):continue
    im=Image.open(original).convert('RGBA');alpha=im.getchannel('A')
    assert alpha.getextrema()[0]==0,(id,'expected transparent background')
    bb=alpha.point(lambda a:255 if a>16 else 0).getbbox();assert bb,(id,'blank')
    size=(64,64) if id.startswith('event-') else (96,96) if id.startswith('stage-') else ((320,200) if id.startswith('buyer-shop-') else ((120,120) if id.startswith('buyer-face-') else (160,120)))
    w,h=size;pad=6;factor=min((w-2*pad)/(bb[2]-bb[0]),(h-2*pad)/(bb[3]-bb[1]));x=(w-(bb[2]-bb[0])*factor)/2-bb[0]*factor;y=(h-(bb[3]-bb[1])*factor)/2-bb[1]*factor
    b=io.BytesIO();im.save(b,format='PNG');encoded=base64.b64encode(b.getvalue()).decode()
    crop='<defs><clipPath id="bust" clipPathUnits="objectBoundingBox"><path d="M0 0H1V.87Q.5 1.01 0 .87Z"/></clipPath></defs>' if id.startswith('buyer-face-') else ''
    clip=' clip-path="url(#bust)"' if crop else ''
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{crop}<image{clip} x="{x}" y="{y}" width="{im.width*factor}" height="{im.height*factor}" href="data:image/png;base64,{encoded}"/></svg>'
    src=SRC/f'{id}.svg';dst=GAME/f'art108-{id}.png'
    if not src.exists() or src.read_text()!=svg or not dst.exists():
        src.write_text(svg);dst.write_bytes(resvg_py.svg_to_bytes(svg_string=svg))
    out=Image.open(dst);a=out.getchannel('A');assert out.size==size and a.getextrema()[1]>=250 and a.getbbox()
    assert out.getpixel((0,0))[3]==0
    rows.append(dict(id=id,file=dst.relative_to(ROOT).as_posix(),source=src.relative_to(ROOT).as_posix(),logicalSize=list(size),sourceAlphaBounds=list(bb),sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
for extra in [ROOT/'Art/Models/StationsV1/effects-manifest.json',SRC/'texture-manifest.json']:
    if extra.exists():rows.extend(json.loads(extra.read_text()))
shopRefs={a[0]:a[1] for a in json.loads((SRC/'shop-specs.json').read_text())}
eventBatches={a['id']:a['batch'] for a in json.loads((SRC/'event-specs.json').read_text())}
for row in rows:
    if row['id'] in shopRefs:row['sourceReference']=shopRefs[row['id']]
    if row['id'] in eventBatches:row['planBatch']=eventBatches[row['id']];row['bindingStatus']='Art name only; Events table ID mapping pending code owner'
manifest={'schema':1,'assets':rows,'nativeBinding':'Pending UI owner; images only, no code mutations.'}
(GAME/'art108-manifest.json').write_text(json.dumps(manifest,indent=2));(SRC/'manifest.json').write_text(json.dumps(manifest,indent=2))
def plate(name,items,cols=5,cw=200,ch=170):
    if not items:return
    sheet=Image.new('RGB',(cols*cw,max(ch,((len(items)+cols-1)//cols)*ch)),'#F4EFE3');draw=ImageDraw.Draw(sheet)
    for i,row in enumerate(items):
        x=(i%cols)*cw;y=(i//cols)*ch;im=Image.open(ROOT/row['file']);sheet.paste(im,(x+(cw-im.width)//2,y+6),im);draw.text((x+10,y+ch-30),row['id'],fill='#173F57')
    sheet.save(SRC/name)
small=[r for r in rows if max(r['logicalSize'])<=320]
plate('review.png',small,3,360,250)
plate('shops-review.png',[r for r in rows if r['id'].startswith('buyer-shop-')],3,360,250)
plate('buyers-review.png',[r for r in rows if r['id'].startswith('buyer-face-')])
plate('items-review.png',[r for r in rows if r['id'].startswith(('item-','product-'))])
plate('stages-review.png',[r for r in rows if r['id'].startswith('stage-')])
plate('night-review.png',[r for r in rows if r['id'].startswith('night-')])
print('ART108 IMAGERY PACKAGED',len(rows),'assets')

plate('chests-review.png',[r for r in rows if r['id'].startswith('chest-')],3)
plate('events-review.png',[r for r in rows if r['id'].startswith('event-')],8,130,110)
