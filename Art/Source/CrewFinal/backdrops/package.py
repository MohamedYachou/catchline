"""Deterministic export/proofs only; paintings originate in built-in ImageGen."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageChops
import json, hashlib

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
RARITIES=['white','green','blue','purple','gold','mythic']
CREW=['mira','ines','noor','sam','ana','olaf']
L=Image.Resampling.LANCZOS
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def font(s):return ImageFont.truetype(str(ROOT/'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'),s)
def label(im,xy,t,s=24):ImageDraw.Draw(im).text(xy,t,font=font(s),fill='#173F57')
mapping=json.loads((OUT/'generation.json').read_text())
manifest=[]
mask=Image.new('L',(756*4,540*4));ImageDraw.Draw(mask).rounded_rectangle((0,0,756*4-1,540*4-1),radius=44*4,fill=255)
mask=mask.resize((756,540),L)
for n in RARITIES:
    src=OUT/mapping[n]['raw']
    im=Image.open(src).convert('RGBA')
    # Match intended aspect without distortion; generation requested1.4:1.
    from PIL import ImageOps
    im=ImageOps.fit(im,(756,540),method=L,centering=(.5,.5))
    im.putalpha(mask)
    dst=OUT/f'v2-card-back-{n}.png';im.save(dst,optimize=True)
    manifest.append(dict(id=dst.stem,file=dst.name,size=[756,540],logicalSize=[378,270],cornerRadius=44,frameRect480=[51,57,378,270],slice=None,sha256=sha(dst),source=mapping[n]['raw']))
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

def card(n,who,new):
    c=Image.new('RGBA',(960,1280))
    if new:back=Image.open(OUT/f'v2-card-back-{n}.png').convert('RGBA')
    else:
        back=Image.new('RGBA',(756,540),'#1C3A5A');back.putalpha(mask)
    c.alpha_composite(back,(102,114))
    frame=Image.open(ROOT/f'Assets/Art/UI/Cards/art108-frame-{n}.png').convert('RGBA').resize((960,1280),L)
    c.alpha_composite(frame)
    # Same runtime PortraitSquare: min(window.w,window.h), centred,bottom-aligned.
    bust=Image.open(ROOT/f'Assets/Art/UI/Portraits/art108-{who}.png').convert('RGBA').resize((540,540),L)
    c.alpha_composite(bust,(210,114))
    d=ImageDraw.Draw(c);d.text((480,705),who.title(),anchor='mm',font=font(42),fill='#FFF3DA')
    for y,t in [(824,'Level 8'),(969,'Crew member'),(1113,'Blueprint ready')]:d.text((238,y),t,font=font(35),fill='#173F57')
    return c.resize((400,533),L)

sheet=Image.new('RGB',(2880,1800),'#F4EFE3')
label(sheet,(48,20),'CREW CARD BACKDROPS / 400px cards on a 2880 x 1800 screen',36)
label(sheet,(48,75),'Top: flat navy baseline. Middle: painted rarity harbour. Bottom: unobstructed backdrop. Source proof; no native glow/rays.',22)
for i,(n,who) in enumerate(zip(RARITIES,CREW)):
    x=80+i*460
    label(sheet,(x,118),n.upper()+' / '+who.title(),25)
    for y,new in [(165,False),(760,True)]:
        c=card(n,who,new);sheet.paste(c,(x,y),c)
    b=Image.open(OUT/f'v2-card-back-{n}.png').resize((400,286),L)
    sheet.paste(b,(x,1365),b)
label(sheet,(80,1700),'All six backdrops: 756 x 540 RGBA; rounded r44; art aperture [51,57,378,270] at 480 x 640. Existing crew/frame paintings unchanged.',24)
sheet.save(OUT/'contact-actual-size-2880x1800.jpg',quality=95,subsampling=0)
small=Image.new('RGB',(1320,1020),'#F4EFE3')
for i,n in enumerate(RARITIES):
    x=25+(i%3)*440;y=15+(i//3)*500
    label(small,(x,y),n.upper(),24)
    im=Image.open(OUT/f'v2-card-back-{n}.png').resize((410,293),L);small.paste(im,(x,y+45),im)
    # All rarities with the same accepted Mira for direct readability comparison.
    bust=Image.open(ROOT/'Assets/Art/UI/Portraits/art108-mira.png').convert('RGBA').resize((293,293),L)
    small.paste(bust,(x+58,y+45),bust)
small.save(OUT/'contact-mira-all-six.jpg',quality=95,subsampling=0)
checks=[]
for e in manifest:
    p=OUT/e['file'];im=Image.open(p);a=im.getchannel('A')
    assert im.mode=='RGBA' and im.size==(756,540)
    assert a.getbbox()==(0,0,756,540) and a.getpixel((0,0))==0
    assert a.getpixel((378,270))==255
    assert ImageChops.difference(a,mask).getbbox() is None
    checks.append(dict(file=p.name,sha256=sha(p),mode=im.mode,size=list(im.size),alphaExtrema=a.getextrema(),passDimensionsAlpha=True))
baseline=json.loads((OUT/'preservation-baseline.json').read_text())
assert all(sha(ROOT/p)==v for p,v in baseline.items()),'Accepted reference changed since baseline; inspect concurrent lead changes'
(OUT/'audit.json').write_text(json.dumps(dict(passed=True,files=checks,preservedReferences=len(baseline),proofSize=[2880,1800],cardWidth=400),indent=2)+'\n')
print('PASS: six RGBA756x540/r44; references unchanged:',len(baseline))
