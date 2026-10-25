"""Extend editable CardsV1 artwork without changing incumbent assets."""
from pathlib import Path
from PIL import Image
import resvg_py,numpy as np
from package import *
base=(ROOT/'Art/Models/CardsV1/art108-frame-purple.svg').read_text()
palettes={'white':('#DAD9CE','#FFF9E6','#8A9290'),'green':('#399376','#A8E6B4','#205C50'),'mythic':('#9B3241','#F1CA76','#591E2B')}
files=[]
for n,(c,hi,lo) in palettes.items():
 s=base.replace('#8E44AD',c).replace('#E0BAF4',hi).replace('#54216E',lo)
 if n=='mythic':
  studs=''
  for x,y in [(31,40),(449,40),(31,584),(449,584)]:
   studs+=f'<path d="M{x} {y-11}l8 11-8 11-8-11Z" fill="#EFC66D" stroke="#173F57" stroke-width="2"/><path d="M{x} {y-7}l4 7-4 6-4-6Z" fill="#B7F0E8"/><path d="M{x} {y-7}l4 7h-4Z" fill="#F4FFF7"/>'
  s=s.replace('</svg>',studs+'</svg>')
 p=OUT/f'svg/art108-frame-{n}.svg';p.write_text(s)
 dst=OUT/f'art108-frame-{n}.png';dst.write_bytes(resvg_py.svg_to_bytes(svg_string=s,width=480,height=640));files.append(dst.name)
shine='''<svg xmlns="http://www.w3.org/2000/svg" width="480" height="640" viewBox="0 0 480 640"><defs><linearGradient id="s"><stop stop-color="#FFF4CE" stop-opacity="0"/><stop offset=".38" stop-color="#FFF4CE" stop-opacity=".04"/><stop offset=".5" stop-color="#FFF9E8" stop-opacity=".58"/><stop offset=".54" stop-color="#FFFFFF" stop-opacity=".75"/><stop offset=".62" stop-color="#FFF4CE" stop-opacity=".12"/><stop offset="1" stop-color="#FFF4CE" stop-opacity="0"/></linearGradient><clipPath id="c"><rect x="14" y="9" width="452" height="610" rx="35"/></clipPath></defs><g clip-path="url(#c)"><path d="M210 -80H450L80 720H-160Z" fill="url(#s)"/></g></svg>'''
(OUT/'svg/art108-frame-mythic-shine.svg').write_text(shine)
(OUT/'art108-frame-mythic-shine.png').write_bytes(resvg_py.svg_to_bytes(svg_string=shine,width=480,height=640))
files.append('art108-frame-mythic-shine.png')
# Independent intended aperture checks; exact alpha geometry of palette variants.
ref=np.asarray(Image.open(ROOT/'Assets/Art/UI/Cards/art108-frame-purple.png'))[:,:,3]
checks={}
for n in palettes:
 a=np.asarray(Image.open(OUT/f'art108-frame-{n}.png'))[:,:,3]
 assert a[150,240]==0 and a[300,100]==0 and a[350,240]>250
 # Different rasterizers may differ at antialiasing edges, never in the solid mask.
 checks[n]=dict(windowTransparent=bool(np.all(a[80:310,75:405]==0)),solidMaskMismatch=int(np.count_nonzero((a>128)!=(ref>128))))
 assert checks[n]['windowTransparent']
(OUT/'frame-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
inventory('B',files,'BUILT, pending opened contact-sheet review. Exact incumbent SVG layout, portrait aperture [51,57,378,270], name band [49,337,382,36], ability slots y=388/460/532. Mythic adds small gem studs outside the aperture. Shine is an alpha light streak, clipped to the outer card shape; animate/tint in UI. Editable SVGs included. Blue/purple/gold untouched. See frame-checks.json for independent mask comparison.')
sheet('B',files,cols=2,refs=[ROOT/'Assets/Art/UI/Cards/art108-frame-blue.png',ROOT/'Assets/Art/UI/Cards/art108-frame-purple.png',ROOT/'Assets/Art/UI/Cards/art108-frame-gold.png',ROOT/'Assets/Art/UI/v2-portrait-mira.png'])
report();print(checks)
