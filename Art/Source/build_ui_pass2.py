"""Task 05 additive sprite builder. Exact export sizes; logical sizes are half.
Run: python3 Art/Source/build_ui_pass2.py <part 1..8>. No Unity dependencies.
Typography is bundled Fredoka converted to editable SVG paths, never system fonts.
"""
from pathlib import Path
import sys,json,math,hashlib
from PIL import Image
from fontTools.pens.svgPathPen import SVGPathPen
import build_ui_kit as U
from build_ui_kit import rect,path,ellipse,line
ROOT=U.ROOT; OUT=U.OUT; SRC=ROOT/'Art/Source/UI/Pass2'; SRC.mkdir(exist_ok=True)
N='#173F57'; I='#F3F0DC'; O='#E36A35'; T='#168F9F'; G='#E6AD38'; W='#C58B50'; S='#8FA6AC'; C='#F4EFE3'
font=U.TTFont(U.FONT); glyphs=font.getGlyphSet(); cmap=font.getBestCmap(); units=font['head'].unitsPerEm

def lettering(text,x,y,size,fill=N,stroke=None,sw=0):
    scale=size/units; advances=[glyphs[cmap[ord(c)]].width for c in text]; left=x-sum(advances)*scale/2
    result=''
    for c,advance in zip(text,advances):
        pen=SVGPathPen(glyphs); glyphs[cmap[ord(c)]].draw(pen)
        result+=f'<g transform="translate({left} {y}) scale({scale} {-scale})">'+path(pen.getCommands(),fill,stroke,sw/scale)+'</g>'
        left+=advance*scale
    return result

def emit(name,w,h,body,use,border=None,shadow=True,extra=None):
    # Build at half the requested export dimensions through the existing emitter.
    U.emit(name,w//2,h//2,f'<g transform="scale(.5)">{body}</g>',use,border,shadow)
    old=U.SRC/(name+'.svg'); target=SRC/old.name; old.replace(target)
    m=U.MAN[name]; m['source']=str(target.relative_to(ROOT)); m['task']=5
    if extra:m.update(extra)
    U.save_png(Image.open(OUT/(name+'.png')),OUT/(name+'.png'),m['source']+'; build_ui_pass2.py; SVG SHA256 '+hashlib.sha256(target.read_bytes()).hexdigest())

def part1():
    b=lettering('Catchline',512,246,211,I,I,20)+lettering('Catchline',512,246,211,N)
    b+=line('M104 116 C71 51 140 29 166 65 C182 94 153 123 133 105',I,12)
    b+=line('M104 116 C71 51 140 29 166 65 C182 94 153 123 133 105',N,5)
    b+=line('M148 106 C181 154 208 244 160 299 C117 348 83 312 102 286 L104 305',I,13)
    b+=line('M148 106 C181 154 208 244 160 299 C117 348 83 312 102 286 L104 305',N,5)
    b+=ellipse(170,198,16,21,O)+path('M154 198 H186 Q185 218 170 219 Q155 218 154 198',I)+line('M170 171 V180',O,6)
    emit('logo-catchline',1024,384,b,'Fredoka wordmark; cream keyline, C fishing line/hook and orange bobber. Preserve aspect ratio.')

def finish():
    p=OUT/'slices.json'; data=json.loads(p.read_text()); data['sprites'].update(U.MAN); p.write_text(json.dumps(data,indent=2)+'\n')
    p=OUT/'UI.md'; text=p.read_text(); marker='## Task 05 — UI pass 2'
    if marker not in text:text+='\n'+marker+'\n\nAdditive illustrated sprites in the existing palette and Fredoka. All listed dimensions are final exported pixels, at 2x (logical size is half). Keep alpha gutters and aspect ratios. Title backdrop is an opaque full-screen RGBA scene; all other additions have transparent margins. Lettering in the logo, shop headers, NEW badge and unknown fish is intentionally baked; gameplay labels remain live. Source SVG lettering uses outlines from the bundled Fredoka font. No new M_ materials.\n\n| PNG | Export px | Logical px | Slice L/B/R/T | Use |\n| --- | --- | --- | --- | --- |\n'
    for name,m in U.MAN.items():
        if f'`{name}.png`' in text: continue
        d=lambda a:'×'.join(map(str,a)); b=m['border_px']; borders='/'.join(str(b[k]) for k in ['left','bottom','right','top']) if b else '—'
        text+=f'| `{name}.png` | {d(m["export_size"])} | {d(m["intended_size"])} | {borders} | {m["use"]} |\n'
    p.write_text(text)

if __name__=='__main__':
    globals()['part'+sys.argv[1]](); finish(); print('Built part',sys.argv[1],list(U.MAN))
