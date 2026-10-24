from pathlib import Path
import sys,json,hashlib
sys.path.insert(0,str(Path.home()/'.codex/tmp/art108-python'))
import resvg_py
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
defs='''<defs><radialGradient id="pool"><stop stop-color="#FFD593" stop-opacity=".65"/><stop offset=".35" stop-color="#FFD593" stop-opacity=".40"/><stop offset=".72" stop-color="#F4C77E" stop-opacity=".12"/><stop offset="1" stop-color="#F4C77E" stop-opacity="0"/></radialGradient></defs>'''
pool=f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">{defs}<circle cx="128" cy="128" r="124" fill="url(#pool)"/></svg>'
lines=[]
for i in range(28):
    x=24+(i*137)%970;y=20+(i*83)%450;length=28+(i%4)*13
    lines.append(f'<path d="M{x} {y}l-12 {length}" stroke="#B9D5DF" stroke-opacity="{.12+(i%4)*.035}" stroke-width="{1+(i%2)}" stroke-linecap="round"/>')
rain='<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="512" viewBox="0 0 1024 512">'+''.join(lines)+'</svg>'
rows=[]
for name,svg,dest,use in [('DeckLightPool',pool,'Assets/Art/Models/StationsV1/DeckLightPool.png','Optional soft station light decal; centre pivot, project on XZ deck, bind material/power in code.'),('SquallOverlay',rain,'Assets/Art/UI/v2/art108-squall-overlay.png','Transparent rain streak sprite; scroll/crossfade by event code, no flashing or baked scene dimming.')]:
    src=ROOT/'Art/Models/StationsV1'/f'{name}.svg';src.write_text(svg);png=ROOT/dest;data=resvg_py.svg_to_bytes(svg_string=svg);png.write_bytes(data)
    im=Image.open(png);a=im.getchannel('A');assert a.getextrema()[0]==0 and a.getextrema()[1]>30 and im.getpixel((0,0))[3]==0
    rows.append(dict(id=name,file=dest,source=src.relative_to(ROOT).as_posix(),logicalSize=list(im.size),use=use,sha256=hashlib.sha256(data).hexdigest()))
(ROOT/'Art/Models/StationsV1/effects-manifest.json').write_text(json.dumps(rows,indent=2));print('ART108 EFFECTS PASSED',len(rows))
