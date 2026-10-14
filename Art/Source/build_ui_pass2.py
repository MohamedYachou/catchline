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

def part2():
    name='title-backdrop'; src=SRC/'title-backdrop-render.png'
    im=Image.open(src).convert('RGBA');assert im.size==(1920,1080)
    U.save_png(im,OUT/(name+'.png'),'Art/Source/render_title_backdrop.py; staged existing Gull Harbour models; no Unity')
    U.MAN[name]={'file':name+'.png','source':'Art/Source/render_title_backdrop.py','intended_size':[960,540],'export_size':[1920,1080],'border_px':None,'task':5,'opaque':True,'use':'Golden-hour harbour. Menu safe rectangle export x=80..650, y=420..940. Full-screen opaque RGBA backdrop; preserve aspect ratio.'}

def placed(body,x,y,scale=1):return f'<g transform="translate({x} {y}) scale({scale})">{body}</g>'
def fishshape(species='herring'):
    # Side view, head left. Shape and markings carry species recognition at 64px.
    if species=='conger':
        return path('M19 63 C18 35 53 39 77 60 C98 82 109 57 116 53 C112 93 88 99 66 78 C45 60 32 83 19 63Z',N)+line('M29 59 C63 48 76 89 103 75',S,8)+ellipse(28,58,3,4,I)+ellipse(28,58,1.5,2,N)
    if species=='plaice':
        b=path('M18 62 Q48 19 89 49 L115 40 L108 64 L115 89 L88 78 Q48 111 18 62Z','#8C5A36')+path('M26 56 Q52 28 85 52 L90 66 Q54 95 26 71Z',W)
        for x,y in [(44,47),(59,63),(43,77),(77,56),(69,80)]:b+=ellipse(x,y,3,2,O)
        return b+ellipse(27,57,3,3,N)+ellipse(30,66,3,3,N)
    back={'herring':T,'mackerel':'#2A6685','pollock':'#477A56','seabass':N,'cod':'#477A56','unknown':N}[species]
    top=38 if species in ('cod','seabass') else 45
    b=path(f'M14 64 Q40 {top-19} 89 52 L116 37 L109 64 L116 91 L88 77 Q42 105 14 64Z',back)
    if species=='unknown':return b+lettering('?',58,78,43,I)
    b+=path('M16 65 Q49 63 89 66 L88 77 Q43 102 16 65Z','#BAC9C6')
    b+=path(f'M47 {top+4} L57 {top-15} L66 {top-2} L78 {top-10} L84 50Z',back)
    b+=path('M52 77 L65 94 L69 78Z',S)+ellipse(28,59,5,5,I)+ellipse(27,59,2.8,3,N)+line('M37 54 Q46 65 37 77',back,2)+line('M15 67 L24 69',N,2)
    if species=='mackerel':
        for x in range(45,89,8): b+=line(f'M{x} 48 l-3 12',N,3)
    if species=='cod':b+=line('M29 79 Q23 93 33 90',W,3)+path('M72 45 L79 25 L89 49Z',back)
    return b

def part3():
    names=[('market','Fish Market'),('harbourmaster','Harbour Master'),('crewoffice','Crew Office'),('chandlery','Chandlery'),('supplies','Supplies')]
    for i,(slug,title) in enumerate(names):
        # Broad illustrated counter strip: inset silhouette, warm shelves, purpose-specific stock.
        b=rect(10,10,1220,194,34,C)+rect(28,25,1184,125,22,I)
        b+=rect(38,140,1164,54,15,W)+rect(40,140,1160,12,5,'#DFB77A')
        for x in (88,1000):b+=rect(x,48,150,10,4,W)+rect(x,110,150,10,4,W)
        if i==0:
            b+=placed(fishshape('mackerel'),75,52,1.2)+placed(fishshape('plaice'),1000,52,1.15)
            b+=rect(68,145,200,36,10,T)+line('M87 155 H246',I,3)
        elif i==1:
            b+=placed(chart_icon(),70,36,1.25)+placed(anchor_icon(),1015,25,1.1)
        elif i==2:
            b+=placed(portrait('captain'),70,18,1.18)+placed(portrait('deckhand'),1015,18,1.18)
        elif i==3:
            b+=placed(anchor_icon(),80,25,1.2)+placed(net_icon(),1005,30,1.2)
        else:
            for x in (88,165,1010,1085):b+=rect(x,66,57,69,10,T if x%2 else O)+rect(x+7,53,43,18,5,I)
            b+=placed(gift_icon(),1030,90,.65)
        b+=lettering(title,630,120,62,N)
        emit('header-'+slug,1240,220,b,title+' illustrated counter banner. Fredoka shop name baked; no slice.')

def part4():
    for s in ['herring','mackerel','pollock','seabass','conger','plaice','cod','unknown']:
        emit('fish-'+s,256,256,placed(fishshape(s),0,0,2),s+' side portrait, head left. Species shapes and markings; fixed shared frame, not common physical scale.')

def anchor_icon():
    return line('M64 29 V101 M43 50 H85 M25 76 Q26 102 64 104 Q102 102 103 76',S,10)+ellipse(64,25,13,13,S)+ellipse(64,25,5,5,C)+path('M15 81 L26 64 L39 82Z',S)+path('M89 82 L103 64 L116 81Z',S)
def chart_icon():
    return path('M20 22 L48 29 L80 18 L109 26 V107 L80 99 L48 111 L20 103Z',I)+path('M20 22 L48 29 V111 L20 103Z','#DFB77A')+path('M80 18 L109 26 V107 L80 99Z','#64C7C4')+line('M35 83 Q70 36 95 60',T,4)+ellipse(71,56,8,8,O)+path('M71 74 L63 58 H79Z',O)
def net_icon():
    b=path('M26 28 Q64 38 101 25 L112 101 Q63 114 16 100Z',T)
    for x in range(30,103,14):b+=line(f'M{x} 34 L{x-9} 98',I,2)
    for y in range(43,101,14):b+=line(f'M24 {y} Q64 {y+9} 104 {y-2}',I,2)
    b+=line('M26 28 Q64 38 101 25',W,6)
    for x in (28,53,78,101):b+=ellipse(x,29,6,8,O)
    return b

def gift_icon():
    return rect(22,49,84,63,10,T)+rect(17,39,94,23,6,'#64C7C4')+rect(57,39,14,73,3,G)+line('M62 40 C18 41 27 6 48 20 L64 38 C108 40 104 6 81 20Z',O,9)

def portrait(role):
    skin={'captain':'#B9784B','deckhand':'#D99C6A','fisherman':'#8F573A','veteran':'#B9784B'}[role]
    b=path('M15 116 Q18 79 64 79 Q110 79 113 116Z',G if role=='deckhand' else N)
    b+=ellipse(33,61,8,10,skin)+ellipse(95,61,8,10,skin)+rect(54,77,20,18,8,skin)+ellipse(64,58,31,34,skin)
    b+=path('M33 51 Q23 15 52 15 Q80 3 96 33 L94 55 L81 33 Q68 48 54 32 L43 54Z','#8C5A36' if role!='veteran' else S)
    b+=ellipse(53,59,3,4,N)+ellipse(76,59,3,4,N)+ellipse(66,68,5,4,'#E4AE7D')+line('M56 78 Q65 83 74 77',N,2.5)
    if role=='captain':
        b+=path('M30 35 Q19 9 64 9 Q108 9 99 35Z',I)+rect(31,29,67,13,5,N)+path('M42 39 Q64 55 92 39Z',N)+ellipse(65,24,5,6,G)
        b+=path('M42 91 L54 110 L59 88 M86 91 L74 110 L69 88',I)
    elif role=='deckhand':
        b+=path('M31 34 Q28 7 63 9 Q100 8 98 34Z',O)+rect(29,29,71,16,7,O)+ellipse(64,10,10,8,O)+line('M44 14 L42 29 M61 12 V29 M80 15 L83 29','#F4B47C',3)+rect(36,96,10,20,3,O)+rect(82,96,10,20,3,O)
    elif role=='fisherman':
        b+=path('M29 39 Q33 8 65 13 Q98 13 101 40Z',G)+rect(24,33,83,12,5,G)+path('M42 94 L56 117 H76 L88 94Z',T)
    else:
        b+=path('M32 34 Q25 13 61 12 Q98 9 101 37Z',N)+rect(29,31,72,13,5,N)+path('M38 73 Q52 93 64 87 Q79 93 91 71 Q88 105 64 102 Q41 102 38 73Z',S)+path('M48 74 Q57 66 65 73 Q77 67 83 76 L65 79Z',I)+line('M47 51 L58 53 M72 53 L83 51',S,3)
    return b

if __name__=='__main__':
    globals()['part'+sys.argv[1]](); finish(); print('Built part',sys.argv[1],list(U.MAN))
