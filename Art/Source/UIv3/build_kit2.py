"""Deterministic v3 UI geometry: editable SVG originals, transparent PNGs and Unity metas.

Extends the supplied rounded paper/brass/enamel kit. No baked words or numerals.
Run with /home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit2.py.
"""
from pathlib import Path
import json
import uuid
import re
import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent / 'kit-2'
OUT = ROOT / 'Assets/Art/UI'
SOURCE.mkdir(exist_ok=True)
NAVY, TEAL, CORAL = '#173f57', '#168f9f', '#df7257'
DEFS = '''<defs>
 <linearGradient id="paper" x2="0" y2="1"><stop stop-color="#fffaf0"/><stop offset="1" stop-color="#f3e9d5"/></linearGradient>
 <linearGradient id="brass" x2=".7" y2="1"><stop stop-color="#ffe8a5"/><stop offset=".45" stop-color="#d6ad65"/><stop offset="1" stop-color="#936a32"/></linearGradient>
 <linearGradient id="steel" x2=".6" y2="1"><stop stop-color="#f6f7e9"/><stop offset=".45" stop-color="#c7d9d9"/><stop offset="1" stop-color="#7796a2"/></linearGradient>
 <linearGradient id="wood" x2="0" y2="1"><stop stop-color="#dfb77a"/><stop offset="1" stop-color="#b67c43"/></linearGradient>
 <linearGradient id="ice" x2=".8" y2="1"><stop stop-color="#f5fff9"/><stop offset=".5" stop-color="#afe2e5"/><stop offset="1" stop-color="#64b8c8"/></linearGradient>
</defs>'''

def pin(x, y, r=10):
    return f'<circle cx="{x}" cy="{y+2}" r="{r+1}" fill="#715731" opacity=".22"/><circle cx="{x}" cy="{y}" r="{r}" fill="url(#brass)" stroke="#9d763d" stroke-width="1.5"/><ellipse cx="{x-2}" cy="{y-3}" rx="{r*.44}" ry="{r*.22}" fill="#fff0bd"/>'

def paper(x,y,w,h,r=18):
    return f'<rect x="{x}" y="{y+4}" width="{w}" height="{h}" rx="{r}" fill="#403e36" opacity=".18"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#paper)" stroke="#a68755" stroke-width="2"/><rect x="{x+3}" y="{y+3}" width="{w-6}" height="{h-6}" rx="{r-2}" fill="none" stroke="#fffdf5" stroke-width="2"/>'

def fish(x,y,s):
    return f'<g transform="translate({x} {y}) scale({s})" fill="{NAVY}"><path d="M-50 0 Q-20 -33 22 -22 L34 -38 37 -19 Q53 -12 61 0 Q53 12 37 19 L31 35 17 22 Q-22 33 -50 0 L-74 -21 -68 0 -74 21Z"/><circle cx="43" cy="-4" r="3" fill="#f9f1df"/></g>'

manifest = {}
def asset(name,w,h,body,border=(0,0,0,0),safe=None):
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{DEFS}{body}</svg>'
    (SOURCE / f'{name}.svg').write_text(svg)
    target = OUT / f'v3-{name}.png'
    cairosvg.svg2png(bytestring=svg.encode(),write_to=str(target),output_width=w*2,output_height=h*2)
    meta=target.with_suffix('.png.meta')
    if not meta.exists():
        template=(OUT/'v3-card.png.meta').read_text()
        template=re.sub(r'guid: [a-f0-9]+',f'guid: {uuid.uuid4().hex}',template,count=1)
        template=template.replace('spriteMode: 0','spriteMode: 1')
        template=template.replace('spriteBorder: {x: 0, y: 0, z: 0, w: 0}',f'spriteBorder: {{x: {border[0]*2}, y: {border[1]*2}, z: {border[2]*2}, w: {border[3]*2}}}')
        meta.write_text(template)
    template=meta.read_text()
    template=re.sub(r'spriteBorder: \{[^}]+\}',f'spriteBorder: {{x: {border[0]*2}, y: {border[1]*2}, z: {border[2]*2}, w: {border[3]*2}}}',template)
    meta.write_text(template)
    manifest[name]={'png':str(target.relative_to(ROOT)), 'size':[w*2,h*2], 'slice_pixels':[v*2 for v in border], 'safe_text_svg_units':safe}

for i,(name,color) in enumerate((('easy',TEAL),('medium',CORAL),('hard',NAVY))):
    body=paper(8,11,224,294,16)
    body+=f'<path d="M12 63 H228 V93 Q228 104 217 104 H23 Q12 104 12 93Z" fill="{color}"/><path d="M14 65 H226" stroke="#fff" opacity=".32" stroke-width="2"/>'
    body+=pin(120,25,9)
    # A route diagram above the lower writing area. Difficulty encoded by count and fish size.
    if i:
        body+=f'<path d="M{120-i*30} 135 H{120+i*30}" stroke="#b49b73" stroke-width="3" stroke-dasharray="5 6"/>'
    for k in range(i+1):
        body+=f'<circle cx="{120+(k-i/2)*60}" cy="135" r="9" fill="{color}"/><circle cx="{118+(k-i/2)*60}" cy="132" r="3" fill="#fff8df" opacity=".55"/>'
    body+=fish(125,185,.53+i*.24)
    body+='<path d="M36 229 H204 M36 260 H204" stroke="#d4c5a9" stroke-width="1.5"/>'
    asset('daycard-'+name,240,320,body,safe={'header':[25,66,190,34],'body':[30,213,180,73]})

def route(done=False):
    c=TEAL if done else CORAL
    b=f'<path d="M48 92 C42 84 13 58 13 36 A35 35 0 0 1 83 36 C83 58 54 84 48 92Z" fill="#173f57" opacity=".2" transform="translate(0 3)"/><path d="M48 90 C42 82 14 57 14 36 A34 34 0 0 1 82 36 C82 57 54 82 48 90Z" fill="{c}" stroke="#173f57" stroke-width="2"/><path d="M24 26 Q30 9 48 9" fill="none" stroke="#fff2cf" stroke-width="3" stroke-linecap="round" opacity=".65"/><circle cx="48" cy="36" r="23" fill="url(#paper)" stroke="#b1905c" stroke-width="2"/>'
    if done: b+='<path d="M34 36 L44 46 63 26" fill="none" stroke="#168f9f" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
    return b
asset('route-pin',96,100,route(),safe=[27,16,42,40])
asset('stop-done',96,100,route(True))
# Three fixed dashes: left/right caps stay intact and the centre is a single stretchable dash.
asset('route-dash',96,24,'<path d="M5 13 H18 M32 13 H64 M78 13 H91" stroke="#685b44" opacity=".2" stroke-width="6" stroke-linecap="round"/><path d="M5 11 H18 M32 11 H64 M78 11 H91" stroke="#d4ad69" stroke-width="5" stroke-linecap="round"/>',(28,8,28,8))
can='<path d="M29 20 L38 11 H61 V26 H72 V76 Q72 84 64 84 H24 Q16 84 16 76 V34Z" fill="#168f9f" stroke="#173f57" stroke-width="3"/><path d="M42 18 H55 V25 H35Z" fill="#fff3d6"/><path d="M26 39 L62 70 M62 39 L26 70" stroke="#0b6677" stroke-width="5"/><path d="M24 36 V72" stroke="#77d1cf" stroke-width="3"/><path d="M19 22 L27 14 36 23 28 31Z" fill="url(#brass)" stroke="#8b692f" stroke-width="2"/>'
asset('fuel-chip',256,96,paper(4,5,248,82,20)+can,safe=[86,18,150,56])
banner='<path d="M3 16 H61 V108 H3 L20 62Z M387 16 H445 L428 62 445 108 H387Z" fill="#d7bb87" stroke="#9f804b" stroke-width="2"/>'+paper(27,8,394,100,14)+pin(46,30,8)+pin(402,30,8)
asset('arrival-banner',448,124,banner,(66,28,66,42),safe=[70,26,308,60])
# Prep glyphs share the same 256-square optical bounds and material vocabulary.
knife='<g transform="rotate(-32 128 128)"><path d="M58 53 H143 V160 Q82 158 58 116Z" fill="url(#steel)" stroke="#173f57" stroke-width="4"/><path d="M61 58 V114 Q88 147 139 151" fill="none" stroke="#fffdf0" stroke-width="5"/><rect x="125" y="145" width="28" height="77" rx="10" fill="#173f57" stroke="#0e2c40" stroke-width="3"/><path d="M130 154 V207" stroke="#416c80" stroke-width="4"/><circle cx="140" cy="162" r="4" fill="url(#brass)"/><circle cx="140" cy="197" r="4" fill="url(#brass)"/></g>'
asset('prep-knife',256,256,knife)
ice=''
for x,y,r in ((55,72,-14),(126,92,12),(88,148,-8)):
    ice+=f'<g transform="translate({x} {y}) rotate({r})"><rect width="80" height="72" rx="13" fill="url(#ice)" stroke="#629aa9" stroke-width="3"/><path d="M12 56 V17 Q12 10 20 10 H59" fill="none" stroke="#f9fff6" stroke-width="6" stroke-linecap="round"/><path d="M24 64 H67 V25" fill="none" stroke="#66a9b6" stroke-width="3"/></g>'
asset('prep-ice',256,256,ice)
crate='<path d="M37 83 L121 52 221 80 219 188 133 218 37 185Z" fill="url(#wood)" stroke="#80562e" stroke-width="4"/><path d="M38 84 L134 114 220 81 M134 115 V217" fill="none" stroke="#8d5e33" stroke-width="5"/><path d="M44 111 L128 137 M43 145 L128 171 M143 135 L213 109 M143 169 L212 143 M143 202 L212 176" stroke="#956333" stroke-width="6"/><path d="M44 105 L128 131 M143 129 L212 103" stroke="#f3d8a0" stroke-width="3"/><path d="M57 84 L121 62 200 83 133 106Z" fill="#173f57"/>'+fish(132,87,.44).replace(NAVY,'#c7d9d9')+'<path d="M53 171 V187 M204 179 V195" stroke="#c7c8aa" stroke-width="8"/>'
asset('prep-crate',256,256,crate)
pan='<g transform="rotate(-28 128 128)"><rect x="110" y="28" width="35" height="104" rx="12" fill="#173f57" stroke="#0e2c40" stroke-width="4"/><rect x="118" y="38" width="19" height="25" rx="8" fill="#f5ead3"/><ellipse cx="128" cy="162" rx="85" ry="66" fill="#173f57" stroke="#0e2c40" stroke-width="5"/><ellipse cx="128" cy="153" rx="83" ry="61" fill="url(#steel)" stroke="#e8e9d6" stroke-width="4"/><ellipse cx="128" cy="152" rx="68" ry="47" fill="#365367" stroke="#69818c" stroke-width="3"/><path d="M74 151 Q82 122 109 117" fill="none" stroke="#899eaa" stroke-width="4" stroke-linecap="round"/></g>'
asset('prep-pan',256,256,pan)
(SOURCE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

font=ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts/Fredoka-SemiBold.ttf'),20)
sheet=Image.new('RGB',(1600,1040),'#f4efe3')
d=ImageDraw.Draw(sheet)
for half,bg,fg in ((0,'#f4efe3',NAVY),(1,'#286b84','#fff8e8')):
    yy=half*520
    d.rectangle((0,yy,1600,yy+520),fill=bg)
    d.text((24,yy+10),'UI v3 · Day / route / prep · cream' if half==0 else 'Same transparent assets · sea blue',font=font,fill=fg)
    for i,name in enumerate(manifest):
        x=22+(i%6)*264;y=yy+48+(i//6)*234
        im=Image.open(OUT/f'v3-{name}.png').convert('RGBA')
        im.thumbnail((238,192),Image.Resampling.LANCZOS)
        sheet.paste(im,(x+(238-im.width)//2,y+(192-im.height)//2),im)
        d.text((x,y+197),name,font=font,fill=fg)
sheet.save(ROOT/'docs/screens/ui-v3/art-kit-2.png')
print('Wrote 12 transparent PNGs + metas / SVG originals / manifest / cream + sea contact sheet')
