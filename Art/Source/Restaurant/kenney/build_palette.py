"""Technical palette transform: preserves pixel layout, alpha and food colours."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parents[3]
src=R/'Art/Downloads/kenney/food/Models/GLB format/Textures/colormap.png'
im=Image.open(src).convert('RGBA')
def lerp(a,b,t):return tuple(round(a[k]+(b[k]-a[k])*t) for k in range(3))
variants={}
for mode in ['catchline','lemonade','roast']:
 out=im.copy();n=0
 for y in range(im.height):
  for x in range(im.width):
   r,g,b,a=im.getpixel((x,y));rgb=None
   # Neutral white/grey ramp only: tint subtly cream, preserve luminance.
   if max(r,g,b)-min(r,g,b)<8 and min(r,g,b)>100:
    v=max(r,g,b)/255;rgb=(round(v*244),round(v*239),round(v*227))
   # Purple swatch, used by soda-glass and broth bowl trim.
   elif b>r*1.1 and r>g*1.08 and b-g>30:
    v=max(r,g,b)/255
    rgb=tuple(round(v*k) for k in ((242,201,90) if mode=='lemonade' else (45,125,134)))
   # Blue-grey fish skin only in dedicated roasted-fish material variant.
   elif mode=='roast' and b>r and b>g and abs(r-g)<30 and max(r,g,b)-min(r,g,b)<70:
    v=max(r,g,b)/255;rgb=tuple(round(v*k) for k in (213,166,102))
   if rgb:
    out.putpixel((x,y),(*rgb,a));n+=rgb!=(r,g,b)
 out.save(O/f'food-colormap-{mode}.png')
 variants[mode]={'file':f'food-colormap-{mode}.png','changed_pixels':n,'size':list(out.size),'source':str(src.relative_to(R))}
materials={
 'wood':('#C58B50','Warm honey wood; matches KayKit counter surfaces'),
 'woodDark':('#8C5A36','Recessed timber'),
 'carpet':('#256572','Teal upholstery/rug instead of salmon red'),
 'carpetDarker':('#173F57','Navy border'),
 'carpetBlue':('#256572','Same teal family'),
 'carpetWhite':('#F4EFE3','Warm cream'),
 'plant':('#477A56','Natural muted leaf green instead of bright mint'),
 'metal':('#8FA6AC','Retained light steel family'),
 'metalDark':('#28343B','Dark steel'),
 'metalMedium':('#70878C','Mid steel'),
 'metalLight':('#BAC9C6','Pale steel'),
 'lamp':('#F3DEA1','Warm cream diffuser'),
 'glass':('#BAC9C6','Opaque pale glazing; no new transparency dependency')}
(O/'furniture-materials-catchline.json').write_text(json.dumps({'method':'Named material base-colour overrides, sRGB hex. Kenney Furniture GLB has no texture atlas. Convert sRGB to linear for shader factors. No geometry/UV edits.','materials':{k:{'hex':v[0],'reason':v[1]} for k,v in materials.items()}},indent=2))
(O/'palette-map.json').write_text(json.dumps({'food':variants,'unchanged':'All UVs/dimensions/alpha preserved. catchline leaves orange/brown/yellow/green food pixels untouched; purple trim is teal. lemonade and roast are per-model alternatives, never global replacements.','furniture':'furniture-materials-catchline.json'},indent=2))
sheet=Image.new('RGB',(1400,660),'#F4EFE3');d=ImageDraw.Draw(sheet)
sheet.paste(im.convert('RGB').resize((400,400)),(20,50))
sheet.paste(Image.open(O/'food-colormap-catchline.png').convert('RGB').resize((400,400)),(450,50))
d.text((20,20),'FOOD ORIGINAL',fill='#173F57');d.text((450,20),'CATCHLINE - same 512px layout',fill='#173F57')
for i,(k,(hx,reason)) in enumerate(materials.items()):
 x=900+(i%2)*240;y=40+(i//2)*75;d.rectangle((x,y,x+50,y+45),fill=hx);d.text((x+58,y),k,fill='#173F57');d.text((x+58,y+18),hx,fill='#173F57')
d.text((20,480),'Food colours stay natural. Cream crockery; teal trim. Dedicated lemonade / roasted fish atlases are opt-in.',fill='#173F57')
d.text((20,510),'Furniture: named material colours; no texture exists to replace. Apply the JSON overrides on imported material copies.',fill='#173F57')
sheet.save(O/'palette-map.jpg',quality=94)
print('PALETTE_DONE',variants)
