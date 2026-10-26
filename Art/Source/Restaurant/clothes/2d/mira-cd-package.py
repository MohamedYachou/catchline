"""Mechanical crops, resizes and review composites; generated painting unchanged."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json, hashlib
R=Path(__file__).resolve().parent
records=[]
for ident in ['mira-c','mira-d']:
    raw=R/'provenance'/f'{ident}-generated.png'
    im=Image.open(raw).convert('RGBA')
    assert im.getchannel('A').getextrema()[0]==0, ident
    box=im.getchannel('A').getbbox(); body=im.crop(box)
    body.save(R/f'{ident}-front.png')
    w,h=body.size
    crop=[round(w*.18),0,round(w*.82),round(h*.37)]
    bust=body.crop(crop); bust=bust.crop(bust.getchannel('A').getbbox()); native=bust.size
    scale=768/max(native); bust=bust.resize(tuple(round(v*scale) for v in native),Image.Resampling.LANCZOS)
    bust=bust.crop(bust.getchannel('A').getbbox()); bust.save(R/f'{ident}-bust.png')
    sheet=Image.new('RGBA',(body.width+80+bust.width,max(body.height,bust.height)))
    sheet.alpha_composite(body,(0,0)); sheet.alpha_composite(bust,(body.width+80,0)); sheet.save(R/f'{ident}-sheet.png')
    comp=Image.new('RGB',(1280,1100),'#eee2c8'); d=ImageDraw.Draw(comp)
    d.text((24,18),ident+' / existing Mira identity | new full-body | bust + actual 88px preview',fill='#173f57')
    for source,area,pos in [(R/'mira-a-front.png',(240,900),(15,90)),(R/f'{ident}-front.png',(580,980),(280,65)),(R/f'{ident}-bust.png',(370,550),(890,60)),(R/f'{ident}-bust.png',(88,88),(1010,770))]:
        art=ImageOps.contain(Image.open(source).convert('RGBA'),area,Image.Resampling.LANCZOS); comp.paste(art,pos,art)
    comp.save(R/f'{ident}-compare.jpg',quality=95)
    rec={'id':ident,'source':str(raw.relative_to(R)),'sourceSize':im.size,'alphaCrop':box,'bodySize':body.size,'bustCropInBody':crop,'bustNativeSize':native,'bustSize':bust.size,'resampleScale':scale,'sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'exports':[]}
    for suffix in ['front','bust','sheet']:
        p=R/f'{ident}-{suffix}.png'; a=Image.open(p); alpha=a.getchannel('A'); bb=alpha.getbbox()
        assert alpha.getextrema()[0]==0 and min(bust.size)>=264
        if suffix!='sheet': assert bb==(0,0,a.width,a.height),(p,bb)
        rec['exports'].append({'file':p.name,'size':a.size,'alphaRange':alpha.getextrema(),'bounds':bb,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    records.append(rec)
ids=['mira-a','mira-b','mira-c','mira-d','noor','ines']
font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',22)
canvas=Image.new('RGB',(1920,820),'#eee2c8'); draw=ImageDraw.Draw(canvas)
draw.text((28,20),'MIRA A-D / HOST OPTIONS   |   NOOR / WAITER   |   INES / BARISTA',fill='#173f57',font=font)
for i,ident in enumerate(ids):
    x=i*320
    art=ImageOps.contain(Image.open(R/f'{ident}-front.png'),(300,520),Image.Resampling.LANCZOS)
    canvas.paste(art,(x+(320-art.width)//2,70+520-art.height),art)
    draw.text((x+24,610),ident.upper(),fill='#173f57',font=font)
    bust=ImageOps.contain(Image.open(R/f'{ident}-bust.png'),(88,88),Image.Resampling.LANCZOS)
    canvas.paste(bust,(x+116,660),bust)
draw.text((28,778),'Actual 88px busts. C: evening dress. D: tailored host. Review options; no outfit selected.',fill='#173f57',font=font)
canvas.save(R/'mira-ad-noor-ines-compare.jpg',quality=96)
(R/'mira-cd-manifest.json').write_text(json.dumps({'artOnly':True,'tool':'built-in imagegen','pass':True,'records':records},indent=2))
print(json.dumps({'variants':len(records),'exports':6,'alphaTight3xPass':True}))
