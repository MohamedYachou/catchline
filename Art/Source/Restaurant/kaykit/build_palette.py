"""UV-exact palette export: affine RGB remap retains the source ramp and inset details."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
INV=json.loads((OUT/'source-inventory.json').read_text())
def rgb(s):return np.array(tuple(bytes.fromhex(s.strip('#'))),dtype=float)
def hx(v):return '#'+''.join(f'{int(x):02X}' for x in v)
# Each target is the bright endpoint then shaded endpoint. Identical colours across
# neighbouring cells deliberately share the same mapping to retain inset continuity.
WOOD=('DFB77A','8C5A36','Honey timber; replace diner orange without changing food.')
WOOD2=('E8C891','9C6B42','Lighter timber shelves/frames; retain original recessed panel pattern.')
NAVY=('2A6685','102F43','Catchline navy paint; cool deep values with readable lit bevels.')
TEAL=('64C7C4','126773','Restaurant teal paint/upholstery; calmer than mint or bright blue.')
CREAM=('F4EFE3','B8B09C','Warm cream paint/linen; cooler white steel remains separate.')
PALETTES={
 'restaurant':{'R2C2':NAVY,'R2C3':TEAL,'R4C6':CREAM,'R4C7':WOOD,'R4C8':CREAM},
 'furniture':{'R1C1':WOOD,'R1C2':WOOD,'R1C3':WOOD,'R1C4':WOOD2,'R1C5':WOOD2,'R1C6':CREAM,'R1C8':CREAM,'R2C1':NAVY,'R2C2':NAVY,'R2C3':TEAL,'R2C4':TEAL,'R2C5':CREAM,'R2C6':CREAM,'R2C7':CREAM,'R3C1':CREAM,'R3C2':CREAM,'R3C4':CREAM},
}
FONT='C:/Windows/Fonts/segoeui.ttf'
def font(n):return ImageFont.truetype(FONT,n)
manifest={};audit={}
for pack,info in INV.items():
    source=Image.open(ROOT/info['source']).convert('RGBA');a=np.array(source);b=a.copy()
    records=[]
    for cell in info['cells']:
        key=cell['id'];x,y,w,h=cell['rect'];old=a[y:y+h,x:x+w,:3].astype(float)
        target=PALETTES[pack].get(key)
        if target:
            # Original per-pixel value preserves ramp nonlinearities and local inset
            # deviations. No cell resampling, filtering, coordinate changes or flips.
            high=np.array(cell['top'],float);low=np.array(cell['bottom'],float)
            t=np.clip((old.mean(2)-low.mean())/(high.mean()-low.mean()),0,1)
            new=rgb(target[1])+t[...,None]*(rgb(target[0])-rgb(target[1]))
            b[y:y+h,x:x+w,:3]=np.rint(new).astype('uint8')
        before=[hx(a[y,x+64,:3]),hx(a[y+255,x+64,:3])]
        after=[hx(b[y,x+64,:3]),hx(b[y+255,x+64,:3])]
        records.append(dict(id=key,rect=cell['rect'],changed=bool(target),before_bright_shadow=before,after_bright_shadow=after,reason=target[2] if target else 'Preserved byte-for-byte: steel, food, glass, neutral or natural secondary material.',models=list(cell['uses'])[:12]))
    path=OUT/f'{pack}bits_texture-catchline.png';Image.fromarray(b).save(path)
    manifest[pack]=dict(source=info['source'],output=path.name,size=[1024,1024],mode='RGBA',coordinates='image origin top-left; R1C1 upper-left; each cell128x256',method='source-ramp mean RGB value, affine target endpoints; original pixel positions/alpha unchanged',cells=records)
    # Readable side-by-side maps, eight rows of four cells split across two pages.
    for page in range(2):
        proof=Image.new('RGB',(1600,1160),'#F4EFE3');d=ImageDraw.Draw(proof)
        d.text((24,14),f'{pack.upper()} / UV-preserving Catchline palette / {page+1} of 2',font=font(26),fill='#173F57')
        for i,record in enumerate(records[page*16:page*16+16]):
            col=i%4;row=i//4;px=20+col*396;py=65+row*270;x,y,w,h=record['rect']
            for j,img in enumerate((source,Image.fromarray(b))):
                crop=img.crop((x,y,x+w,y+h)).resize((100,200))
                proof.paste(crop,(px+j*108,py+30))
            d.text((px,py),record['id']+('  CHANGE' if record['changed'] else '  KEEP'),font=font(17),fill='#173F57')
            d.text((px,py+232),'Original',font=font(14),fill='#173F57');d.text((px+108,py+232),'Catchline',font=font(14),fill='#173F57')
            d.text((px+218,py+50),' -> '.join([record['before_bright_shadow'][0],record['after_bright_shadow'][0]]),font=font(12),fill='#173F57')
            d.text((px+218,py+78),' -> '.join([record['before_bright_shadow'][1],record['after_bright_shadow'][1]]),font=font(12),fill='#173F57')
        proof.save(OUT/f'{pack}-swatch-map-{page+1}.jpg',quality=95)
    proof=Image.new('RGB',(2096,1120),'#F4EFE3');proof.paste(source.convert('RGB'),(16,70));proof.paste(Image.fromarray(b).convert('RGB'),(1056,70));d=ImageDraw.Draw(proof);d.text((20,18),f'{pack} original',font=font(30),fill='#173F57');d.text((1060,18),'Catchline / identical UV layout',font=font(30),fill='#173F57');proof.save(OUT/f'{pack}-atlas-before-after.jpg',quality=95)
(OUT/'swatch-map.json').write_text(json.dumps(manifest,indent=2))
lines=['# KayKit Catchline swatch map','','Coordinates: image origin top-left, R1C1 upper-left. 8 columns x 4 rows; cells128x256. Endpoint hex pairs are bright / shade.','']
for pack,info in manifest.items():
    lines+=['## '+pack,'','| Cell | Original bright/shade | Catchline bright/shade | Reason |','|---|---|---|---|']
    for c in info['cells']:lines.append(f"| {c['id']} | {' / '.join(c['before_bright_shadow'])} | {' / '.join(c['after_bright_shadow'])} | {c['reason']} |")
    lines+=['']
(OUT/'SWATCH-MAP.md').write_text('\n'.join(lines))
print('Exported both1024RGBA atlases,64 swatch records,6 comparison maps')
