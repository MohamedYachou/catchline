"""Only alpha trim, proportionate resize/padding, comparisons, inventory and hashes."""
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'manifest.json').read_text())
layout_path=ROOT/'layout.json'
if layout_path.exists():
    for instance in json.loads(layout_path.read_text()).get('repeated_instances',[]):
        for e in manifest:
            if e['name']==instance['name']:
                e['size']=[max(e['size'][i],instance['rect'][i+2]*3) for i in range(2)]
    (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2))
(ROOT/'review').mkdir(exist_ok=True)
try: FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
except OSError: FONT=ImageFont.load_default()
records=[]
for e in manifest:
    name=e['name']; src=ROOT/'provenance'/(name+'.png'); dst=ROOT/(name+'.png')
    if not src.exists(): continue
    im=Image.open(src).convert('RGBA'); original_size=list(im.size)
    # Generator supplied the requested wood strip above unrelated white padding.
    # Keep its untouched original; crop only the actual painted strip for export.
    source_crop=[0,0,2048,261] if name=='v2-prep-topbar' else None
    if source_crop: im=im.crop(source_crop)
    if not dst.exists():
        if e['opaque']:
            out=ImageOps.fit(im,tuple(e['size']),Image.Resampling.LANCZOS,
                centering=(0.5,1.0) if source_crop else (0.5,0.5))
            bounds=[0,0,*im.size]
        else:
            alpha=im.getchannel('A'); bounds=alpha.point(lambda x:255 if x>=32 else 0).getbbox()
            if not bounds: raise ValueError('empty '+name)
            l,t,r,b=bounds; bounds=[max(0,l-12),max(0,t-12),min(im.width,r+12),min(im.height,b+12)]
            content=im.crop(bounds)
            # Insets leave antialias/shadow room; proportionate fitting never warps artwork.
            fit=ImageOps.contain(content,(e['size'][0]-8,e['size'][1]-8),Image.Resampling.LANCZOS)
            out=Image.new('RGBA',tuple(e['size'])); out.alpha_composite(fit,((out.width-fit.width)//2,(out.height-fit.height)//2))
        out.save(dst)
    final=Image.open(dst).convert('RGBA'); ref=Image.open(e['crop']).convert('RGBA')
    # A pair keeps each final next to its actual measured mockup crop, never an invented reference.
    tile=Image.new('RGB',(1200,430),'#20394a'); d=ImageDraw.Draw(tile)
    d.text((14,8),name,fill='#fff4df',font=FONT)
    d.text((14,37),'MOCKUP CROP (includes original text/context)',fill='#d6dde0',font=FONT)
    d.text((612,37),'DELIVERED PIECE (live text removed)',fill='#d6dde0',font=FONT)
    for x,img in [(12,ref),(612,final)]:
        thumb=ImageOps.contain(img,(576,350),Image.Resampling.LANCZOS)
        pos=(x+(576-thumb.width)//2,70+(350-thumb.height)//2)
        tile.paste(thumb,pos,thumb.getchannel('A'))
    tile.save(ROOT/'review'/(name+'.png'))
    alpha=final.getchannel('A'); bbox=alpha.point(lambda x:255 if x>=8 else 0).getbbox()
    records.append(dict(name=name,canvas=list(final.size),native_source=original_size,alpha_extrema=alpha.getextrema(),
        visible_bounds=bbox,sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
        upscaled_canvas=any(final.size[i]>original_size[i] for i in range(2)),source_crop=source_crop,opaque=e['opaque']))
(ROOT/'asset-audit.json').write_text(json.dumps(dict(expected=len(manifest),packaged=len(records),
    missing=[e['name'] for e in manifest if not (ROOT/(e['name']+'.png')).exists()],assets=records),indent=2))
for screen in (3,4,5):
    names=[e['name'] for e in manifest if e['screen']==screen and (ROOT/'review'/(e['name']+'.png')).exists()]
    for start in range(0,len(names),4):
        sheet=Image.new('RGB',(1200,430*min(4,len(names)-start)),'#20394a')
        for row,name in enumerate(names[start:start+4]): sheet.paste(Image.open(ROOT/'review'/(name+'.png')),(0,row*430))
        sheet.save(ROOT/'review'/f'contact-s{screen}-{start//4+1:02}.png')
print(json.dumps(dict(packaged=len(records),expected=len(manifest),missing=len(manifest)-len(records),
    alpha_issues=[r['name'] for r in records if not r['opaque'] and r['alpha_extrema'][0]>0],
    native_sources={str(size):sum(r['native_source']==size for r in records) for size in [r['native_source'] for r in records]})))
