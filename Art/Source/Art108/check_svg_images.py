import sys,io,base64
from pathlib import Path
sys.path.insert(0,str(Path.home()/'.codex/tmp/art108-python'))
import resvg_py
from PIL import Image
b=io.BytesIO();Image.new('RGBA',(10,10),'red').save(b,format='PNG')
encoded=base64.b64encode(b.getvalue()).decode()
for typ in ('href','xlink:href'):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="10" height="10"><image x="0" y="0" width="10" height="10" {typ}="data:image/png;base64,{encoded}"/></svg>'
    o=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=svg)))
    print(typ,o.getextrema())
root=Path(__file__).resolve().parents[3]
original=Image.open(root/'Art/Source/Art108/portraits/ana-original.png').convert('RGBA')
print('original',original.size,original.getextrema())
svg=(root/'Art/Models/CardsV1/art108-ana-portrait.svg').read_text()
for text in (svg,svg.replace(' clip-path="url(#bust)"','')):
    o=Image.open(io.BytesIO(resvg_py.svg_to_bytes(svg_string=text,width=56,height=56)))
    print('actual',o.getextrema())
