"""Deterministic UI kit and 1920x1080 comps. Python: pillow, cairosvg, fonttools.
Run from any directory. Authored geometry; no generated imagery or Unity APIs.
All layout values are logical px; sprite PNGs are 2x. See UI.md.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from PIL.PngImagePlugin import PngInfo
from fontTools.ttLib import TTFont
import cairosvg
import io, json, math, hashlib

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Assets/Art/UI'; SRC=ROOT/'Art/Source/UI'; CON=ROOT/'Art/Concepts'
for p in (OUT,SRC,CON): p.mkdir(parents=True,exist_ok=True)
C={'cream':'#F4EFE3','navy':'#173F57','orange':'#E36A35','teal':'#168F9F','gold':'#E6AD38','ivory':'#F3F0DC','steel':'#8FA6AC','green':'#3E9A5B','red':'#C8443A','grey':'#C7C5BD'}
FONT=OUT/'Fonts/Fredoka-Medium.ttf'
MAN={}
CMAP=TTFont(FONT).getBestCmap()

def save_png(im,path,source):
    meta=PngInfo(); meta.add(b'sRGB',b'\x00')
    meta.add_text('Software','Catchline authored UI / Pillow + CairoSVG')
    meta.add_text('Source',source)
    im.save(path,pnginfo=meta)

def rect(x,y,w,h,r,fill,stroke=None,sw=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}"' if stroke else '')+'/>'
def path(d,fill,stroke=None,sw=0):
    return f'<path d="{d}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if stroke else '')+'/>'
def ellipse(x,y,rx,ry,fill): return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}"/>'
def line(d,c,w): return path(d,'none',c,w)
def svg(w,h,body): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'
def raster(s,w,h): return Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode(),output_width=w,output_height=h))).convert('RGBA')
def txt(im,x,y,s,size=24,col=None,anchor='lt'):
    assert all(ord(c) in CMAP or c=='\n' for c in s), ('Missing font glyph',s)
    f=ImageFont.truetype(str(FONT),size)
    ImageDraw.Draw(im).text((x,y),s,font=f,fill=col or C['navy'],anchor=anchor,stroke_width=0)
def emit(name,w,h,body,usage,border=None,shadow=False,label=None):
    source=svg(w,h,body)
    (SRC/(name+'.svg')).write_text(source+'\n')
    im=raster(source,w*2,h*2)
    if label: txt(im,w,h,label,int(h*.65),C['navy'],'mm')
    if shadow:
        alpha=im.getchannel('A')
        sh=Image.new('RGBA',im.size,(23,63,87,0))
        a=Image.new('L',im.size); a.paste(alpha,(0,6)); a=a.filter(ImageFilter.GaussianBlur(5)).point(lambda v:int(v*.20))
        sh.putalpha(a); sh.alpha_composite(im); im=sh
    save_png(im,OUT/(name+'.png'),f'Art/Source/UI/{name}.svg; build_ui_kit.py; SVG SHA256 '+hashlib.sha256(source.encode()).hexdigest())
    MAN[name]={'file':name+'.png','source':f'Art/Source/UI/{name}.svg','intended_size':[w,h],'export_size':[w*2,h*2], 'use':usage,'border_px':dict(zip(['left','bottom','right','top'],border)) if border else None}

def build():
    # Caps include transparent shadow gutters. Borders are source PNG pixels.
    for name,fill,stroke in [('panel-cream',C['cream'],None),('card-white','#FFFFFF',None),('card-selected','#FFFFFF',C['orange']),('toast-dark',C['navy'],None),('chip-dark',C['navy'],None)]:
        emit(name,128,128,rect(8,6,112,112,18,fill,stroke,3), 'Reusable panel; keep text in the content inset.',[56,64,56,56],True)
    types=[('primary',C['orange']),('secondary',C['teal']),('disabled',C['grey']),('tab-on',C['navy']),('tab-off','#E2DAC9')]
    for name,col in types:
        for pressed in (False,True):
            state='pressed' if pressed else 'normal'; y=9 if pressed else 6
            # Press changes depth and surface value; geometry is identical at the slice seams.
            c=tuple(int(col[i:i+2],16) for i in (1,3,5)); dark='#'+''.join(f'{int(v*.90):02X}' for v in c)
            body=rect(6,y,116,48,14,dark if pressed else col)
            if not pressed: body+=line('M22 11 H106','#FFFFFF',1.5).replace('stroke-width="1.5"','stroke-width="1.5" opacity=".28"')
            emit(f'button-{name}-{state}',128,64,body,f'{name} button {state}; labels are live text.',[44,40,44,40],True)
    for hot in (False,True):
        n='bubble-hot' if hot else 'bubble-white'; fill=C['gold'] if hot else '#FFFFFF'; edge=C['gold'] if hot else C['orange']
        emit(n,128,64,rect(6,6,116,48,16,fill,edge,3),'Speech body; reserve left 34px for a separate icon. Tail separate.',[48,40,48,40],True)
        emit(n+'-tail',24,18,path('M2 2 H22 L12 16 Z',fill,edge,2.5)+rect(4,0,16,3,0,fill),'Centre under body; overlap 3 logical px to conceal seam.')
    emit('bar-background',64,24,rect(3,3,58,18,9,'#D5DDD7'),'Progress track; always pair state colour with a text value or icon.',[24,18,24,18])
    for n in ('teal','green','red'):
        emit('bar-'+n,64,24,rect(3,3,58,18,9,C[n]),n+' progress fill; use clipping at low values, never squash the caps.',[24,18,24,18])
    # Water at the exact exported 920x440 requested: native HUD is 460x220.
    water=rect(4,3,452,210,18,C['teal'])
    water+='<defs><clipPath id="water"><rect x="4" y="3" width="452" height="210" rx="18"/></clipPath></defs><g clip-path="url(#water)">'
    water+=path('M0 45 Q95 8 192 50 T460 40 V0 H0Z','#239FA9')
    water+=path('M0 155 Q80 110 170 161 T460 146 V220 H0Z','#137F91')
    for d in ('M25 63 Q60 53 100 64','M340 72 Q380 64 415 70','M22 172 Q57 160 86 166','M332 184 Q364 172 407 181'):
        water+=line(d,'#64C7C4',3)
    water+='</g>'
    emit('strike-water',460,220,water,'Strike close-up; no bobber baked in. Export is exactly 920×440.',shadow=True)
    for state in ('floating','dipped','underwater'):
        if state=='underwater':
            body=ellipse(40,44,17,12,'#0E7184')+ellipse(40,40,10,8,'#E36A35')
            body='<g opacity=".46">'+body+'</g>'+line('M14 47 Q40 38 66 47','#64C7C4',3)+ellipse(52,23,3,3,'#64C7C4')+ellipse(58,13,2,2,'#64C7C4')
        else:
            cy=42 if state=='floating' else 51
            body=ellipse(40,58,29,6,'#64C7C4')+ellipse(40,cy,18,16,C['ivory'])+path(f'M22 {cy} Q23 {cy-16} 40 {cy-16} Q57 {cy-16} 58 {cy}Z',C['orange'])+rect(37,cy-34,6,24,3,C['orange'])+ellipse(40,cy-14,7,3,'#F4B47C')
            if state=='dipped': body+=path('M12 56 Q40 48 68 56 V65 H12Z','#168F9F')+line('M14 56 Q40 48 66 56','#64C7C4',3)
        emit('bobber-'+state,80,80,body,'Strike bobber '+state+'; share an 80×80 frame and bottom-centre anchor.')
    emit('fish-shadow',128,64,path('M18 31 Q46 6 92 26 L118 13 L111 32 L118 51 L92 39 Q46 58 18 31Z','#0C586B'),'Fish shadow beneath bobber, rotate around centre. Fixed size; no outlines.')
    emit('ripple-ring',128,128,'<ellipse cx="64" cy="64" rx="54" ry="54" fill="none" stroke="#C1EEDE" stroke-width="4" opacity=".8"/>','Scale uniformly and fade; transparent centre.')
    pts=[]
    for i in range(24):
        a=i*math.tau/24; r=57 if i%2==0 else 45
        pts.append(f'{64+math.cos(a)*r:.2f},{48+math.sin(a)*r*.72:.2f}')
    emit('tap-burst',128,96,'<polygon points="'+' '.join(pts)+'" fill="'+C['gold']+'"/>','Bite-only TAP! burst. Lettering rendered from bundled Fredoka.',label='TAP!')
    icons={}
    icons['coin']=ellipse(64,67,43,43,'#C58B50')+ellipse(64,60,43,43,C['gold'])+ellipse(64,60,30,30,'#F4CD67')+path('M66 36 V84 M78 44 Q51 33 50 52 Q50 62 66 62 Q83 63 77 75 Q68 85 49 74','none','#B17629',7)
    icons['fish']=path('M15 65 Q44 20 85 51 L113 33 L105 65 L113 96 L85 78 Q44 107 15 65Z',C['teal'])+path('M19 66 Q48 77 84 65 L84 78 Q43 105 19 66Z','#BAC9C6')+ellipse(35,58,5,6,C['navy'])+path('M55 38 L68 25 L79 44Z',C['navy'])
    icons['bait-worm']=line('M32 26 Q84 10 75 44 Q68 60 45 62 Q20 63 32 84 Q46 107 91 91',C['orange'],20)+ellipse(31,25,3,4,C['navy'])+line('M44 22 L47 34 M64 22 L64 35 M59 57 L61 70 M33 73 L46 75 M49 88 L48 102 M70 88 L70 102','#F4B47C',3)
    icons['food']=rect(22,27,84,75,16,C['gold'])+path('M28 45 L64 26 L100 45 L64 68Z','#F3F0DC')+path('M28 66 L64 47 L100 66 L64 90Z','#477A56')+path('M28 77 L64 58 L100 77 L64 100Z','#DFB77A')
    icons['cooler']=rect(17,42,94,64,12,C['navy'])+rect(13,27,102,29,10,C['ivory'])+rect(53,46,22,21,4,C['steel'])+rect(32,68,64,20,5,'#2A6685')
    icons['ice']=path('M33 24 L88 17 L111 47 L99 101 L42 111 L18 79Z','#64C7C4')+path('M33 24 L50 51 L111 47 L88 17Z','#B8E6DB')+path('M50 51 L42 111 L18 79 L33 24Z',C['teal'])+line('M62 62 L85 83 M83 60 L64 84 M73 53 V93 M53 73 H93',C['ivory'],5)
    icons['rod']=line('M28 103 Q45 57 100 18',C['navy'],9)+line('M28 103 L43 73','#C58B50',16)+ellipse(51,79,14,14,C['navy'])+ellipse(51,79,8,8,C['gold'])+line('M100 18 L102 80',C['steel'],3)+ellipse(102,87,7,10,C['orange'])
    icons['crew']=path('M20 108 Q23 72 64 72 Q105 72 108 108Z',C['navy'])+ellipse(64,53,27,29,'#B9784B')+path('M34 46 Q25 9 67 14 Q106 16 99 44Z',C['ivory'])+rect(34,36,65,14,6,C['navy'])+ellipse(55,54,3,4,C['navy'])+ellipse(74,54,3,4,C['navy'])+path('M48 82 L64 105 L80 82',C['gold'])
    icons['contract-scroll']=path('M25 22 H91 Q110 22 109 40 H92 V94 Q92 109 73 109 H25 Q40 105 40 91 V40 H19 Q14 22 25 22Z','#DFB77A')+path('M30 20 H87 Q76 25 77 39 V91 H34 V36 Q35 24 30 20Z',C['ivory'])+line('M45 43 H67 M45 54 H67 M45 65 H59',C['navy'],5)+ellipse(75,91,13,13,C['orange'])+path('M69 98 L65 117 L76 111 L84 118 L84 99Z',C['orange'])
    icons['map-pin']=path('M64 115 Q20 66 25 43 Q30 14 64 14 Q98 14 103 43 Q108 66 64 115Z',C['orange'])+ellipse(64,49,18,18,C['ivory'])+ellipse(64,49,9,9,C['navy'])
    icons['home-anchor']=line('M64 31 V104 M44 52 H84 M24 77 Q27 106 64 107 Q101 106 104 77',C['navy'],10)+ellipse(64,24,14,14,C['navy'])+ellipse(64,24,6,6,C['cream'])+path('M13 81 L26 65 L39 85Z',C['navy'])+path('M89 85 L103 65 L116 81Z',C['navy'])
    icons['clock']=ellipse(64,66,47,47,C['navy'])+ellipse(64,66,36,36,C['ivory'])+line('M64 39 V66 L84 80',C['navy'],7)+rect(51,8,26,12,4,C['gold'])
    icons['star']=path('M64 10 L80 43 L116 48 L90 74 L97 111 L64 93 L31 111 L38 74 L12 48 L48 43Z',C['gold'])+path('M64 10 L64 72 L12 48 L48 43Z','#F4CD67')
    icons['lock']=path('M32 62 V39 Q32 9 64 9 Q96 9 96 39 V62 H81 V39 Q81 25 64 25 Q47 25 47 39 V62Z',C['steel'])+rect(23,51,82,65,13,C['navy'])+ellipse(64,78,9,9,C['gold'])+rect(60,81,8,17,3,C['gold'])
    for name,body in icons.items(): emit('icon-'+name,128,128,body,'128px intended icon; 256px PNG (2x). Original authored silhouette.')
    (OUT/'slices.json').write_text(json.dumps({'schema_version':1,'export_scale':2,'border_units':'source PNG pixels, Unity order left/bottom/right/top','sprites':MAN},indent=2)+'\n')


def load(n): return Image.open(OUT/(n+'.png')).convert('RGBA')
def put(im,n,x,y,w,h): im.alpha_composite(load(n).resize((int(w),int(h)),Image.Resampling.LANCZOS),(int(x),int(y)))
def nine(im,n,x,y,w,h):
    w,h=int(w),int(h); src=load(n); sw,sh=src.size
    b=MAN[n]['border_px']; l,t,r,bot=[b[k] for k in ('left','top','right','bottom')]
    # Export 2x, mockup scale 1.5x logical: preserve corners at 0.75 source px.
    scale=min(.75,w/(l+r),h/(t+bot))
    dl,dt,dr,db=[int(v*scale) for v in (l,t,r,bot)]
    assert w>=dl+dr and h>=dt+db,(n,w,h)
    sx=[0,l,sw-r,sw]; sy=[0,t,sh-bot,sh]; dx=[0,dl,w-dr,w]; dy=[0,dt,h-db,h]
    for j in range(3):
        for i in range(3):
            piece=src.crop((sx[i],sy[j],sx[i+1],sy[j+1]))
            ww,hh=dx[i+1]-dx[i],dy[j+1]-dy[j]
            if ww and hh: im.alpha_composite(piece.resize((ww,hh),Image.Resampling.LANCZOS),(int(x)+dx[i],int(y)+dy[j]))
def button(im,label,x,y,w,h=75,kind='primary',size=28):
    nine(im,'button-'+kind+'-normal',x,y,w,h)
    col=C['ivory'] if kind in ('tab-on','secondary') else C['navy']
    # Large labels: navy on orange; ivory on teal/navy.
    txt(im,x+w/2,y+h/2-1,label,size,col,'mm')
def bar(im,x,y,w,value,kind='teal',h=26):
    nine(im,'bar-background',x,y,w,h)
    fill=Image.new('RGBA',(w,h)); nine(fill,'bar-'+kind,0,0,w,h)
    im.alpha_composite(fill.crop((0,0,max(0,round(w*value)),h)),(x,y))
def icon(im,name,x,y,s=42): put(im,'icon-'+name,x,y,s,s)
def bubble(im,label,name,x,y,hot=False):
    nine(im,'bubble-hot' if hot else 'bubble-white',x,y,160,77)
    icon(im,name,x+18,y+16,42); txt(im,x+98,y+36,label,28,anchor='mm')
    put(im,('bubble-hot' if hot else 'bubble-white')+'-tail',x+65,y+64,30,23)

def sheet():
    im=Image.new('RGBA',(1920,1080),C['cream'])
    txt(im,48,30,'Catchline / Build 1 UI kit',42)
    txt(im,48,83,'Reusable pieces · Fredoka Medium · PNGs at 2x · borders in slices.json',22)
    # Parallel columns with actual kit pieces and readable labels, no stock containers.
    txt(im,48,134,'Panels & cards',28)
    for i,n in enumerate(['panel-cream','card-white','card-selected','toast-dark','chip-dark']):
        x=48+i*188; nine(im,n,x,181,176,113); txt(im,x+88,237,['Cream','White','Selected','Toast','Chip'][i],22,C['ivory'] if i>2 else C['navy'],'mm')
    txt(im,48,327,'Buttons / normal & pressed',28)
    for i,n in enumerate(['primary','secondary','disabled','tab-on','tab-off']):
        x=48+i*188
        for j,state in enumerate(['normal','pressed']):
            nine(im,f'button-{n}-{state}',x,372+j*79,176,73)
            txt(im,x+88,408+j*79,['Primary','Secondary','Disabled','Tab on','Tab off'][i],24,C['ivory'] if n in ('tab-on','secondary') or (n=='primary' and state=='pressed') else C['navy'],'mm')
    txt(im,48,553,'One-tap bubbles',28)
    bubble(im,'Fish','rod',48,604); bubble(im,'Carry','fish',235,604); bubble(im,'!','rod',422,604,True)
    txt(im,624,609,'Body + tail',22); txt(im,624,642,'Icon slot on left',21)
    txt(im,48,727,'Progress / values remain live text',28)
    for i,n in enumerate(['background','teal','green','red']):
        nine(im,'bar-'+n,48,778+i*49,310,29); txt(im,380,780+i*49,n.capitalize(),22)
    txt(im,1050,134,'Strike / wait · nibble · bite',28)
    put(im,'strike-water',1030,181,842,403)
    put(im,'fish-shadow',1150,315,170,85)
    for i,n in enumerate(['floating','dipped','underwater']):
        put(im,'bobber-'+n,1310+i*155,312,95,95)
        txt(im,1357+i*155,438,['Floating','Dipped','Under'][i],21,C['ivory'],'mm')
    put(im,'ripple-ring',1700,270,123,123); put(im,'tap-burst',1533,200,160,120)
    txt(im,1048,610,'Icons / 128 px logical, 256 px exported',28)
    names=[n.removeprefix('icon-') for n in MAN if n.startswith('icon-')]
    for i,n in enumerate(names):
        x=1030+(i%7)*122; y=668+(i//7)*151
        icon(im,n,x+19,y,83); txt(im,x+61,y+100,n.replace('contract-scroll','contract').replace('home-anchor','anchor').replace('bait-worm','bait'),19,anchor='mm')
    txt(im,1048,1003,'Aa Bb 0123456789   Fredoka Medium / SIL OFL 1.1',23)
    save_png(im.convert('RGB'),CON/'16-ui-kit.png','Art/Source/build_ui_kit.py / exported kit sprites')


def fishing():
    im=Image.open(SRC/'fishing-background.png').convert('RGBA')
    # 1.5x exact VoyageHud.cs coordinate mapping (1280x720 → 1920x1080).
    nine(im,'panel-cream',24,24,495,324)
    txt(im,48,48,'Harbour mouth',29)
    icon(im,'cooler',48,97,31); txt(im,89,102,'Cooler  6/10',22); bar(im,284,103,203,.6)
    icon(im,'food',48,136,31); txt(im,89,140,'Food  4.2 min',22); bar(im,284,141,203,.7,'green')
    icon(im,'bait-worm',48,178,29); txt(im,88,180,'Bait  12    ·    Stocks  79%',21)
    icon(im,'rod',48,217,29); txt(im,88,220,'Rod 1: BITE!     Rod 2: ready',21)
    icon(im,'contract-scroll',48,260,29); txt(im,88,260,'Mackerel  3/8   ·   2 voyages',21)
    txt(im,88,293,'Deliver fresh fish at harbour',19)
    nine(im,'chip-dark',1626,24,270,69); icon(im,'coin',1646,37,38); txt(im,1723,46,'380 coins',25,C['ivory'])
    button(im,'Head home',1626,105,270,75,'secondary',28)
    icon(im,'home-anchor',1644,124,35)
    # Captain / deckhand chips occupy the original left-bottom region.
    for y,title,status in [(873,'Captain (you)','Watching rod 1'),(963,'Sam · 2 voyages left','Baiting rod 2')]:
        nine(im,'chip-dark',24,y,495,75); icon(im,'crew',44,y+13,46)
        txt(im,108,y+13,title,22,C['ivory']); txt(im,108,y+42,status,19,'#B4D3D3')
    bubble(im,'Fish','rod',648,320); bubble(im,'Carry','fish',1080,481)
    # Strike minigame: [615,726,690,330] matches the actual HUD.
    put(im,'strike-water',615,726,690,330)
    txt(im,960,758,'The bobber is under!',30,C['ivory'],'mt')
    put(im,'fish-shadow',805,837,190,95); put(im,'ripple-ring',936,809,114,114)
    put(im,'bobber-underwater',948,828,90,90); put(im,'tap-burst',1070,807,153,115)
    txt(im,960,971,'Tap anywhere now',24,C['ivory'],'mm'); bar(im,675,1006,570,.68,'red',20)
    save_png(im.convert('RGB'),CON/'17-hud-fishing.png','Art/Source/build_ui_kit.py + render_ui_backgrounds.py / kit sprites + Blender render')


def harbour():
    im=Image.open(SRC/'harbour-background.png').convert('RGBA')
    nine(im,'panel-cream',24,24,540,225)
    txt(im,48,47,'Gull Harbour',40)
    icon(im,'coin',48,101,34); txt(im,96,105,'Voyage 3   ·   380 coins',23)
    txt(im,48,144,'Next hull: skiff refit',22)
    bar(im,48,177,492,(6/16+380/1500)/2,h=22)
    txt(im,48,204,'Land 16 fish (best 6) + 1,500 coins',20)
    # Right panel x=644*1.5, width=620*1.5, 16px margins.
    nine(im,'panel-cream',966,24,930,1032)
    for i,label in enumerate(['Catch','Map','Contracts','Crew','Shop']):
        button(im,label,990+i*178,45,169,60,'tab-on' if label=='Shop' else 'tab-off',23)
    txt(im,1002,137,'Supplies',30)
    for y,title,desc,ic,label in [(186,'Bait · 12 in the bucket','One per cast. Miss the bite, lose the bait.','bait-worm','+10 for 10'),(308,'Food · 4.2 / 6 min','Each sailor eats one minute per minute.','food','Fill up for 4')]:
        nine(im,'card-white',990,y,882,112); icon(im,ic,1013,y+23,61)
        txt(im,1093,y+23,title,26); txt(im,1093,y+63,desc,20)
        button(im,label,1636,y+25,214,64,size=24)
    txt(im,1002,451,'Boat upgrades',30)
    items=[('Rod holder','A second rod. Unattended self-hook: 35%.','rod','250'),('Big cooler','Holds 16 fish instead of 10.','cooler','200'),('Ice box','Keep the full value of your catch.','ice','250'),('Lunch tin','Carry 12 minutes of food instead of 6.','food','100')]
    for i,(title,desc,ic,label) in enumerate(items):
        y=493+i*107
        nine(im,'card-white',990,y,882,101); icon(im,ic,1014,y+20,57)
        txt(im,1093,y+18,title,26); txt(im,1093,y+56,desc,20)
        button(im,label+' coins',1636,y+19,214,64,size=24)
    button(im,'Set sail  ·  Harbour mouth',990,936,882,96,size=34)
    save_png(im.convert('RGB'),CON/'18-hud-harbour.png','Art/Source/build_ui_kit.py + render_ui_backgrounds.py / kit sprites + Blender render')


def docs():
    lines=['# Catchline build 1 UI kit','', 'Authored vector sprites in the STYLE.md palette. PNGs are straight-alpha RGBA, sRGB, at 2x. The three comps are 1920×1080 RGB design references, not Unity screenshots. All labels except TAP! are live text, never baked into buttons.','',
    '## Import contract','', 'Use Sprite (2D and UI), Single, sRGB on, alpha transparency on, Clamp, Bilinear, no mipmaps, no compression for the initial integration. These are recommendations; Unity was not opened and importer settings are not claimed. Set Image type Sliced only for entries with a border. Border values below and in slices.json are **exported PNG pixels**, ordered left, bottom, right, top. PPU 200 gives a 2x sprite a 100-PPU logical size; set explicit UI RectTransforms to the intended logical sizes. Do not trim the transparent gutters; slices include soft shadow padding.','',
    'The native HUD uses 1280×720 virtual coordinates. Comps scale those coordinates 1.5× to 1920×1080, preserving the panel anchors. Strike water is 460×220 logical / exactly 920×440 exported. Icons are 128×128 logical / 256×256 exported. 9-slice specimens are small reusable textures, not forced panel sizes. Do not stretch icons, bobbers, tails, rings or the water panel non-uniformly.','',
    '## Text, states and composition','', 'Fredoka Medium is the one shipped display/UI font. Navy text on cream, white, gold and light grey; ivory text on navy and teal. Use navy on normal orange buttons and ivory on their darker pressed state. Orange and teal button labels must be at least 24px at the 1920px reference size: those pairings meet the 3:1 large-text threshold; body text on cream exceeds 4.5:1. Keep orange for the main action. Selection has a border and active-tab value change; rod states, progress and urgency always retain words/icons. Grey buttons must also be non-interactable. Pressed artwork lowers and darkens the surface. No extra shadow is needed on top of baked sprite shadows.','',
    'Speech bubble: minimum logical 88×42 body plus icon slot, though the styled comps widen to 107×51 to fit the requested icon slot. Tail overlaps body by 3px. Hot body and tail are gold, with ! text and a rod icon. Fish / Watch / Carry / ! labels are code-owned. Fish and Carry appear together with the strike panel to demonstrate all required kit placements; action availability still follows game state.','',
    'Progress: the source bar caps are 12 logical px. Render a full-width sliced fill then clip it to progress; this preserves cap radius below 24px. A fill at zero is hidden. Teal=cooler, green=food/reeling, red=warning/bite timer. Values remain live text.','',
    'Strike: use the same 80×80 logical bobber frame for all states. Waiting=floating, nibble=dipped, bite=underwater + ripple + TAP!; tap anywhere outside UI buttons, as current gameplay specifies. Water has no baked bobber. Ring scales uniformly and fades. These sprites add no timing or animation clips.','',
    '## Files','', '| PNG | Intended px | Export px | Slice L/B/R/T (export px) | Use |','| --- | --- | --- | --- | --- |']
    for n,m in MAN.items():
        dim=lambda v:'×'.join(map(str,v))
        b=m['border_px']; borders='/'.join(str(b[k]) for k in ['left','bottom','right','top']) if b else '—'
        lines.append(f'| `{m["file"]}` | {dim(m["intended_size"])} | {dim(m["export_size"])} | {borders} | {m["use"]} |')
    lines += ['', '## Font and reproducibility','', '`Fonts/Fredoka-Medium.ttf`: unrenamed Fredoka family, static Medium (weight 500, width 100) instantiated from the Google Fonts variable source. `Fonts/OFL.txt`: complete SIL Open Font License 1.1, permits bundling/redistribution. Source: [Google Fonts Fredoka](https://github.com/google/fonts/tree/main/ofl/fredoka). `Fonts/SOURCE.md` records the download URL and static-instance parameters. The original font copyright is retained inside the TTF. No external icon pack or generated art was used.','',
    '`slices.json`: complete manifest of all PNGs, logical/export dimensions, source paths and optional slice borders. `validation.json`: mechanical delivery checks. Every PNG maps to an authored SVG under `Art/Source/UI/`; soft shadows and the TAP! lettering are composed by `Art/Source/build_ui_kit.py`. Original icon geometry belongs to this project. Backgrounds are renders of existing project meshes staged by `Art/Source/render_ui_backgrounds.py`; they contain no UI.','',
    'Rebuild with Python 3.12+ and Pillow/CairoSVG/fontTools: `python Art/Source/build_ui_kit.py`. Render the two backgrounds first in Blender 5.2 using `Art/Source/render_ui_backgrounds.py`. Rebuild model fixes separately with the existing Gull Harbour builder and the six asset arguments. `Art/Source/validate_ui_kit.py` verifies manifest coverage, sizes, alpha and slices.','',
    '## Mockups and live layout reference','', '`Art/Concepts/16-ui-kit.png`: every shipped piece including both states, tails and all 14 icons. `17-hud-fishing.png`: status top left, coin/home top right, crew bottom left, action bubbles and strike bottom centre. `18-hud-harbour.png`: harbour/goal left, five-tab Shop right, Set sail at its foot. Composed from the exported kit using genuine nine-slice raster assembly, not an unrelated painted UI. Example state values are illustrative. Shop prices, names, food and skiff limits follow proto/deck-sim `GameData.cs` / `VoyageHud.cs` as read on 2026-10-14 (47373b7 plus live working copy).','',
    'The harbour and fishing panels follow those HUD anchors; the bubble bodies are slightly wider for the requested icon slot. Unity integration, font import, device testing and final interaction behaviour are a later code pass.']
    (OUT/'UI.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':
    build(); sheet(); docs()
    if (SRC/'fishing-background.png').exists(): fishing(); harbour()
    print('Built',len(MAN),'UI sprites and available mockups')
