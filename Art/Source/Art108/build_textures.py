from pathlib import Path
import sys,base64,json,hashlib
sys.path.insert(0,str(Path.home()/'.codex/tmp/art108-python'))
import resvg_py
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[3];S=R/'Art/Source/Art108/imagery';G=R/'Assets/Art/UI/v2';rows=[]
def uri(p):return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
def save(id,w,h,body,seam=None):
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'
 src=S/f'texture-{id}.svg';src.write_text(svg);dst=G/f'art108-texture-{id}.png';dst.write_bytes(resvg_py.svg_to_bytes(svg_string=svg));im=Image.open(dst).convert('RGBA')
 assert im.size==(w,h)
 errors={}
 for axis in (seam or []):
  a=list(im.crop((0,0,1,h) if axis=='x' else (0,0,w,1)).getdata());b=list(im.crop((w-1,0,w,h) if axis=='x' else (0,h-1,w,h)).getdata());e=max(abs(v-u) for p,q in zip(a,b) for u,v in zip(p,q));errors[axis]=e;assert e==0,(id,axis,e)
 rows.append(dict(id='texture-'+id,file=dst.relative_to(R).as_posix(),source=src.relative_to(R).as_posix(),logicalSize=[w,h],seamMaxPixelDifference=errors,sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
 return im
p=uri(S/'texture-plank-original.png');base=f'<image width="512" height="512" href="{p}"/>'
plank=save('plank',1024,1024,base+f'<g transform="translate(1024 0) scale(-1 1)">{base}</g><g transform="translate(0 1024) scale(1 -1)">{base}</g><g transform="translate(1024 1024) scale(-1 -1)">{base}</g>',['x','y'])
f=S/'texture-rope-h-original.png';im=Image.open(f).convert('RGBA');bb=im.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();x,y,r,b=bb
base=f'<svg x="0" y="32" width="512" height="64" viewBox="{x} {y} {r-x} {b-y}" preserveAspectRatio="none"><image width="{im.width}" height="{im.height}" href="{uri(f)}"/></svg>'
ropebody=base+f'<g transform="translate(1024 0) scale(-1 1)">{base}</g>'
rope=save('rope-h',1024,128,ropebody,['x']);vertical=save('rope-v',128,1024,f'<g transform="translate(128 0) rotate(90)">{ropebody}</g>',['y'])
f=S/'texture-nail-original.png';im=Image.open(f).convert('RGBA');bb=im.getchannel('A').point(lambda a:255 if a>16 else 0).getbbox();x,y,r,b=bb
nail=save('nail',64,64,f'<svg x="4" y="4" width="56" height="56" viewBox="{x} {y} {r-x} {b-y}"><image width="{im.width}" height="{im.height}" href="{uri(f)}"/></svg>')
(S/'texture-manifest.json').write_text(json.dumps(rows,indent=2))
# Repeat-plate compositing for visual QA only; output pixels are rendered from SVGs.
plate=Image.new('RGB',(1200,850),'#eee8da');d=ImageDraw.Draw(plate)
small=plank.resize((300,300))
for yy in range(2):
 for xx in range(2):plate.paste(small,(xx*300,yy*300))
for j in range(4):plate.paste(rope,(70,650+j*40),rope)
for j in range(4):plate.paste(vertical,(630+j*128,-190),vertical)
plate.paste(nail,(25,770),nail);d.text((10,610),'Plank 2x2 repeats | four vertical ropes | horizontal repeats',fill='black');plate.save(S/'textures-review.png')
print('ART108 TEXTURES PASSED',len(rows),'exact seamless edge checks')
