"""Mechanical extraction of Mo's fish.png UI, explicitly requested literal reuse.
Static contours/icons/captions are sampled from the original; dynamic text is removed.
No image generation, assets from another game, or resampling of the master reference.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'docs/reference-hud024/fish-original.png'
OUT = ROOT / 'Assets/Resources/FishReference'
OUT.mkdir(parents=True, exist_ok=True)
im = Image.open(SRC).convert('RGBA')
records = {}

def save(name, pic, bounds=None):
    pic.save(OUT / (name + '.png'))
    records[name] = {'size': list(pic.size), 'source_bounds': bounds}

def mask_rounded(pic, radius):
    # Keep original contour RGB inside the shape; discard captured world outside.
    w,h=pic.size
    m=Image.new('L',(w*4,h*4)); ImageDraw.Draw(m).rounded_rectangle((0,0,w*4-1,h*4-1),radius=radius*4,fill=255)
    pic.putalpha(m.resize((w,h),Image.Resampling.LANCZOS)); return pic

def panel(name, box, radius, inset, sample):
    p=im.crop(box); w,h=p.size
    # Blank content using a clean source strip, retaining original edge/outline pixels.
    # The strip's warmth/very slight grain is reused instead of repainting a flat white card.
    strip=im.crop(sample)
    clean=strip.resize((w-2*inset,h-2*inset),Image.Resampling.BILINEAR)
    p.paste(clean,(inset,inset))
    save(name,mask_rounded(p,radius),list(box))

panel('panel-status',(20,25,340,90),18,8,(91,28,170,33))
# Keep the original thin vertical separator at its exact x position.
p=Image.open(OUT/'panel-status.png'); p.alpha_composite(im.crop((176,33,179,83)),(156,8));save('panel-status',p,[20,25,340,90])
panel('panel-goal',(20,130,240,234),14,5,(85,162,225,164))
p=Image.open(OUT/'panel-goal.png'); p.alpha_composite(im.crop((25,164,235,167)),(5,34));save('panel-goal',p,[20,130,240,234])
panel('panel-toolbar',(1407,25,1655,74),18,7,(1510,27,1580,32))
p=Image.open(OUT/'panel-toolbar.png'); p.alpha_composite(im.crop((1608,35,1611,64)),(201,10));save('panel-toolbar',p,[1407,25,1655,74])
panel('panel-crew',(1365,85,1655,653),15,6,(1390,120,1638,125))
panel('panel-row',(1377,130,1645,207),12,5,(1522,146,1594,151))
# Strip ends carry original rounded anti-aliasing and colour variation.
track=Image.new('RGBA',(143,14))
right=im.crop((1584,185,1598,199))
track.paste(im.crop((1576,185,1578,199)).resize((115,14)),(14,0))
track.paste(right.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(0,0));track.paste(right,(129,0))
save('bar-track',track,[1584,185,1598,199])
save('bar-fill',im.crop((1455,185,1557,199)),[1455,185,1557,199])

icons={'Sun':(31,36,75,80),'Coin':(194,37,232,78),'Target':(31,137,55,162),
       'Crate':(30,178,69,221),'Crew':(1470,39,1498,65),'Menu':(1620,39,1642,63),
       'Wheel':(1608,156,1636,183),'Net':(1606,240,1637,269),'Fish':(1606,327,1636,354),
       'Badge':(1418,31,1458,69)}
for name,box in icons.items():
    p=im.crop(box)
    # Preserve original foreground, keyline AND cream pixels exactly. All these
    # marks sit on the same supplied cream family; no generated replacement art.
    save('icon-'+name,p,list(box))
# Exact static lettering, including original cream keyline, on a transparent background.
labels={'Crew Roles':(1395,96,1500,118),'Captain':(1454,137,1519,156),
        'Deckhand':(1454,223,1547,242),'Fisher':(1454,308,1510,328),
        'Crew':(1501,40,1551,63),'Current Goal':(64,139,170,159)}
for name,box in labels.items():
    p=im.crop(box)
    save('caption-'+name.replace(' ','-'),p,list(box))
# Reference title dot extracted with the same colour as the sun.
p=im.crop((1377,100,1388,112));save('title-dot',p,[1377,100,1388,112])
(ROOT/'docs/reference-hud024/extraction.json').write_text(json.dumps({'source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'assets':records,'limits':'Source edge/foreground extraction; removed content is reconstructed from clean source strips. Dynamic glyph font is a measured approximation, not established identity.'},indent=2)+'\n')
print('Extracted',len(records),'reference fragments')

# Optional reproducible font derivation. Default extraction performs no downloads.
if __name__ == '__main__':
    import sys
    if '--fonts' in sys.argv:
        from urllib.request import urlopen
        from io import BytesIO
        from fontTools.ttLib import TTFont
        from fontTools.varLib.instancer import instantiateVariableFont
        url='https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/Nunito%5Bwght%5D.ttf'
        data=urlopen(url).read()
        expected='bb55a5ca5c2042335b3991af27c4d0705d0ef41cac6164ac737fd8f2a1e85207'
        if hashlib.sha256(data).hexdigest()!=expected:
            raise RuntimeError('Upstream font changed; inspect rather than silently changing approved glyphs')
        for suffix,weight,family in [('Regular',500,'Catchline Reference Body'),('Bold',800,'Catchline Reference Heading')]:
            f=instantiateVariableFont(TTFont(BytesIO(data)),{'wght':weight},inplace=False)
            for platform,encoding,lang in [(3,1,0x409),(1,0,0)]:
                for n,text in [(1,family),(2,'Regular'),(3,family+' 2026 UI024'),(4,family),(6,family.replace(' ',''))]:
                    f['name'].setName(text,n,platform,encoding,lang)
            f.recalcTimestamp=False
            f.save(OUT/('Reference'+suffix+'.ttf'))
        (OUT/'OFL.txt').write_bytes(urlopen('https://raw.githubusercontent.com/google/fonts/main/ofl/nunito/OFL.txt').read())
        (ROOT/'docs/reference-hud024/font-derivation.json').write_text(json.dumps({'source':url,'source_sha256':expected,'weights':[500,800],'original_font_identified':False},indent=2)+'\n')
