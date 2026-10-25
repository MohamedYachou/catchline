"""Source-native extensions of Catchline's nautical icon and frame SVG kit."""
from package import OUT
from PIL import Image
import resvg_py
INK='#173F57'
DEFS='''<defs>
<linearGradient id="gold" x1="0" y1="0" x2=".35" y2="1" gradientUnits="objectBoundingBox"><stop stop-color="#FFF1AD"/><stop offset=".48" stop-color="#E9BA55"/><stop offset="1" stop-color="#AC6C29"/></linearGradient>
<linearGradient id="steel" x2=".5" y2="1"><stop stop-color="#F0F5E8"/><stop offset=".45" stop-color="#B9CFCA"/><stop offset="1" stop-color="#607F88"/></linearGradient>
<linearGradient id="navy" x2=".3" y2="1"><stop stop-color="#4C7D94"/><stop offset=".5" stop-color="#28546C"/><stop offset="1" stop-color="#17364B"/></linearGradient>
<linearGradient id="paper" x2=".6" y2="1"><stop stop-color="#FFF9DE"/><stop offset="1" stop-color="#D7BB83"/></linearGradient>
<linearGradient id="red" x2=".4" y2="1"><stop stop-color="#F69B86"/><stop offset=".5" stop-color="#D45459"/><stop offset="1" stop-color="#8A3043"/></linearGradient>
<linearGradient id="teal" x2=".4" y2="1"><stop stop-color="#ADE7D2"/><stop offset=".5" stop-color="#5BAE9F"/><stop offset="1" stop-color="#2C746F"/></linearGradient>
<linearGradient id="wood" x2=".3" y2="1"><stop stop-color="#E7BF7F"/><stop offset=".5" stop-color="#BE8C50"/><stop offset="1" stop-color="#805437"/></linearGradient>
</defs>'''
def path(d,fill='none',stroke=INK,w=6,extra=''):
 return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round" stroke-linecap="round" {extra}/>'
def circle(x,y,r,fill,stroke=INK,w=6):
 return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>'
def ellipse(x,y,rx,ry,fill,stroke=INK,w=6):
 return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>'
def rect(x,y,w,h,r,fill,stroke=INK,sw=6):
 return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def anchor():
 return circle(128,57,18,'url(#gold)')+path('M128 76V194M86 108H170M66 153Q79 201 128 205Q178 201 190 153M66 153L62 181M66 153L92 162M190 153L194 181M190 153L164 162','none',INK,15)+path('M128 78V194M87 108H169M69 158Q84 199 128 199Q173 199 187 158','none','#F3CE78',6)
def export(name,body,size=256,small=True,view='0 0 256 256'):
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="{view}">{DEFS}{body}</svg>'
 (OUT/'svg').mkdir(exist_ok=True);(OUT/'svg'/f'{name}.svg').write_text(svg)
 p=OUT/f'{name}.png';p.write_bytes(resvg_py.svg_to_bytes(svg_string=svg,width=size,height=size))
 files=[p.name]
 if small:
  Image.open(p).resize((64,64),Image.Resampling.LANCZOS).save(OUT/f'{name}-64.png');files.append(f'{name}-64.png')
 return files
