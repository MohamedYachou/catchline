"""SERVICE-UI-KIT-8 / editable SVG -> exact 2x PNG -> Unity Sprite/Single.

Run in WSL: /home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit8.py --stage 1..3
Stages are cumulative, in assignment order. No previous builder is executed.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import math
import re
import shutil
import uuid
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent / 'kit-8'
REVIEW = SOURCE / 'review'
OUT = ROOT / 'Assets/Art/UI'
NAVY, TEAL, CORAL = '#173f57', '#168f9f', '#df7257'
CREAM, IVORY, NIGHT = '#f4efe3', '#fffaf0', '#182f3a'
PAPER, BRASS = 'url(#paper)', 'url(#brass)'
R = Image.Resampling.LANCZOS
tree = ast.parse((SOURCE.parent / 'build_kit2.py').read_text())
DEFS = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'DEFS' for t in n.targets))
KINDS = ['serve', 'coins', 'perfect', 'combo', 'upsell', 'gulls', 'walkout', 'critic']


def attrs(values):
    return ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in values.items())


def path(d, fill=NAVY, stroke='none', width=2.5, **kw):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {attrs(kw)}/>'


def circle(x, y, r, fill, stroke='none', width=2.5, **kw):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {attrs(kw)}/>'


def ellipse(x, y, rx, ry, fill, stroke='none', width=2.5, **kw):
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {attrs(kw)}/>'


def rect(x, y, w, h, r, fill, stroke='none', width=2, **kw):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {attrs(kw)}/>'


def badge_shell():
    return (circle(32, 33, 29, NAVY, opacity='.20')
            + circle(32, 31, 28.5, BRASS, NAVY, 1.5)
            + circle(32, 31, 24.5, PAPER, NAVY, 1.7)
            + path('M10 21 A24 24 0 0 1 37 8', 'none', '#fffdf5', 1.7))


def sparkle(x, y, r, fill=BRASS):
    return path(f'M{x} {y-r} Q{x+1} {y-1} {x+r} {y} Q{x+1} {y+1} {x} {y+r} Q{x-1} {y+1} {x-r} {y} Q{x-1} {y-1} {x} {y-r}Z', fill)


def plate(x, y, rx=16, ry=7):
    return (ellipse(x, y+2, rx, ry, TEAL, NAVY, 2.4)
            + ellipse(x, y, rx, ry, IVORY, NAVY, 2.4)
            + ellipse(x, y, rx-4.5, ry-2.6, 'none', '#7796a2', 1.7))


def glyphs():
    serve = (circle(21, 20, 4.8, NAVY) + circle(43, 20, 4.8, NAVY)
             + path('M14 38 V31 Q14 26 19 26 H22 Q26 27 26 33 V35 H18 V45 M50 38 V31 Q50 26 45 26 H42 Q38 27 38 33 V35 H46 V45',
                    'none', NAVY, 3.2)
             + path('M22 36 H42 M32 37 V47 M27 47 H37', 'none', NAVY, 2.7)
             + ellipse(32, 32, 9, 3.6, TEAL, NAVY, 2)
             + ellipse(32, 31, 6, 2.4, IVORY))
    coins = (rect(14, 32, 22, 11, 4, BRASS, NAVY, 2.2)
             + ellipse(25, 32, 11, 4.6, BRASS, NAVY, 2.2)
             + path('M16 38 Q25 42 34 38', 'none', '#936a32', 1.6)
             + circle(39, 27, 13, BRASS, NAVY, 2.7)
             + circle(39, 27, 8.8, 'none', '#936a32', 1.5)
             + path('M34 20 Q39 17 43 21', 'none', IVORY, 2)
             + sparkle(16, 19, 4, TEAL))
    perfect = (plate(30, 37, 17, 8) + sparkle(39, 20, 9)
               + sparkle(22, 18, 4, TEAL)
               + path('M48 28 L51 25', 'none', CORAL, 2.6))
    combo = (plate(34, 42, 16, 5.5) + plate(32, 34, 16, 5.5)
             + plate(30, 26, 16, 5.5)
             + path('M12 18 H19 M10 25 H15 M45 18 L50 13 M46 24 H53', 'none', CORAL, 2.8))
    upsell = (path('M37 21 H50 L48 43 Q43 47 39 43Z', TEAL, NAVY, 2.4)
              + path('M44 22 L47 13 H53', 'none', NAVY, 2.4)
              + path('M17 32 H32 L27 43 H22Z', BRASS, NAVY, 2.3)
              + path('M24.5 43 V48 M19 48 H30', 'none', NAVY, 2.3)
              + path('M17 32 Q12 28 18 25 Q15 20 22 20 Q25 15 29 21 Q35 22 32 27 Q37 30 32 32Z', IVORY, NAVY, 2.3)
              + circle(26, 20, 2.7, CORAL)
              + path('M40 29 H48', 'none', '#afe2e5', 2))
    gulls = (path('M15 25 Q21 20 29 24 Q30 18 35 19 L39 22 44 22 40 26 Q39 30 35 32 '
                  'L48 38 Q36 41 28 32 L15 33 20 29Z', IVORY, NAVY, 2.5)
             + circle(35, 23, 1.3, NAVY)
             + path('M29 27 Q20 16 14 17 L20 26', TEAL, NAVY, 2.2)
             + path('M18 47 L19 40 Q19 37 22 38 L25 42 L25 34 Q26 31 28 34 L30 39 '
                    'L33 35 Q36 34 36 38 L33 46 29 49Z', BRASS, NAVY, 2.2)
             + path('M44 15 L47 11 M48 21 L53 20', 'none', CORAL, 2.8))
    walkout = (rect(15, 13, 24, 36, 2, NAVY)
               + rect(19, 17, 16, 28, 1, PAPER, '#d6ad65', 1.8)
               + circle(30, 31, 1.7, NAVY)
               + path('M12 49 H42', 'none', NAVY, 2.7)
               + path('M43 44 L33 35 C26 27 37 22 43 29 C49 22 59 27 53 35Z', CORAL, NAVY, 2.1)
               + path('M36 30 Q38 28 40 30', 'none', IVORY, 1.7))
    critic = (path('M14 28 C10 18 22 13 32 14 C39 8 50 15 50 23 Q51 29 44 30Z', NAVY)
              + path('M20 28 Q31 31 44 27', 'none', CORAL, 2.8)
              + path('M33 14 Q33 10 38 10', 'none', NAVY, 3)
              + circle(23, 38, 7, 'none', NAVY, 3)
              + circle(42, 38, 7, 'none', NAVY, 3)
              + path('M30 37 Q32 34 35 37 M15 36 L12 33 M49 36 L52 33', 'none', NAVY, 2.5))
    return dict(zip(KINDS, (serve, coins, perfect, combo, upsell, gulls, walkout, critic)))


def assets_for(stage):
    result = []
    for name, glyph in glyphs().items():
        result.append(dict(name='goal-'+name, size=(64, 64), body=badge_shell()+glyph,
                           border=[0]*4, safe={'glyph': [10, 9, 44, 43]}, stage=1))
    for name, color, mark in [('tick', TEAL, 'M9 16 L14 21 23 11'),
                              ('broken', CORAL, 'M11 11 L21 21 M21 11 L11 21')]:
        body = (circle(16, 17, 14, NAVY, opacity='.2')
                + circle(16, 15.5, 13.5, color, IVORY, 1.7)
                + path(mark, 'none', IVORY, 3.6))
        result.append(dict(name='goal-'+name, size=(32, 32), body=body,
                           border=[0]*4, safe={}, stage=1))
    if stage >= 2:
        result.extend(board_assets())
    if stage >= 3:
        result.extend(tally_assets())
    return result


def board_assets():
    board = (rect(2, 4, 196, 164, 12, NIGHT, opacity='.24')
             + rect(2, 2, 196, 164, 12, NAVY, '#caa161', 1.5)
             + rect(7, 33, 186, 128, 8, PAPER)
             + path('M16 30 H184', 'none', '#cfaa6b', 1)
             + path('M14 7 H186', 'none', '#527485', 1))
    result = [dict(name='goal-board', size=(200,170), body=board, border=[12,12,12,34], stage=2,
                   safe={'title':[14,7,172,22], 'rows':[[10,y,180,40] for y in [36,80,124]]})]
    for done in [False, True]:
        body = (rect(2,3,176,35,17,NAVY,opacity='.10')
                + rect(2,2,176,35,17,'#f1dfb0' if done else PAPER,
                       '#b58a46' if done else '#c9bfa8',1.3)
                + path('M20 5 H160','none',IVORY,1,opacity='.7'))
        result.append(dict(name='goal-row'+('-done' if done else ''),size=(180,40),body=body,
                           border=[20,18,20,18],stage=2,
                           safe={'badge':[5,6,28,28], 'text':[39,5,92,30],
                                 'progress':[134,8,38,24]}))
    return result


def sliced(name, size):
    a = next(a for a in assets_for(3 if name=='goal-tally' else 2) if a['name']==name)
    src = load(name, a['size'])
    l,b,r,t = a['border']
    assert size[0]>=l+r and size[1]>=t+b
    sx=[0,l,src.width-r,src.width]; sy=[0,t,src.height-b,src.height]
    dx=[0,l,size[0]-r,size[0]]; dy=[0,t,size[1]-b,size[1]]
    out=Image.new('RGBA',size)
    for y in range(3):
        for x in range(3):
            tile=src.crop((sx[x],sy[y],sx[x+1],sy[y+1]))
            out.paste(tile.resize((dx[x+1]-dx[x],dy[y+1]-dy[y]),R),(dx[x],dy[y]))
    return out


def board_sample():
    im=sliced('goal-board',(200,170))
    label(im,(14,8),"Mira's goals",16,IVORY)
    rows=[('serve','tick','Serve 30 guests','Goal met','30/30'),
          ('perfect',None,'Perfect plates','Keep it clean','2/4'),
          ('walkout','broken','Lose fewer than 8','Goal lost','8/7')]
    for y,(kind,state,title,sub,progress) in zip([36,80,124],rows):
        paste(im,sliced('goal-row-done' if state=='tick' else 'goal-row',(180,40)),(10,y))
        paste(im,stamped(kind,28,state),(15,y+6))
        label(im,(49,y+5),title,11)
        label(im,(49,y+20),sub,10,CORAL if state=='broken' else TEAL if state=='tick' else '#57717a')
        label(im,(163,y+19),progress,11,NAVY,anchor='mm')
    return im


def board_reviews():
    screen=capture('day-service-late-1440')
    paste(screen,board_sample(),(16,392))
    sheet=Image.new('RGB',(1200,760),CREAM)
    label(sheet,(24,12),'Live goal board / actual desktop position',30)
    label(sheet,(24,55),'200 x 170 at (16,392); three goals, three states. Sample text is live-layer evidence.',18)
    sheet.paste(screen.crop((0,80,720,680)).convert('RGB'),(24,106))
    label(sheet,(780,108),'Sliced / 260 x 210',23)
    paste(sheet,sliced('goal-board',(260,210)),(780,152))
    label(sheet,(794,161),'Header stays 34 px',17,IVORY)
    for y in [194,244,294]:
        paste(sheet,sliced('goal-row-done' if y==194 else 'goal-row',(240,44)),(790,y))
    label(sheet,(780,397),'Actual-size detail',23)
    paste(sheet,board_sample(),(780,443))
    label(sheet,(780,644),'Done / in progress / failed',18)
    label(sheet,(24,722),'Unchanged native capture underneath; no existing HUD pixels painted out.',18)
    save(sheet,'02-board-native-and-sliced.png')
    proof=Image.new('RGB',(1200,600),NIGHT)
    label(proof,(24,12),'Blank board + rows / shipping art and safe rectangles',28,IVORY)
    paste(proof,load('goal-board'),(24,74))
    paste(proof,load('goal-row'),(466,74)); paste(proof,load('goal-row-done'),(466,184))
    label(proof,(466,297),'Rows are 180 x 40 logical / 360 x 80 PNG',20,IVORY)
    detail=board_sample().resize((400,340),R)
    draw=ImageDraw.Draw(detail)
    a=board_assets()[0]
    for box in [a['safe']['title']]+a['safe']['rows']:
        x,y,w,h=box; draw.rectangle((2*x,2*y,2*(x+w),2*(y+h)),outline=CORAL,width=1)
    for yy in [36,80,124]:
        for key in ['badge','text','progress']:
            x,y,w,h=board_assets()[1]['safe'][key]
            draw.rectangle((2*(10+x),2*(yy+y),2*(10+x+w),2*(yy+y+h)),outline=TEAL,width=1)
    paste(proof,detail,(24,74))
    label(proof,(24,454),'Coral: board title/row slots. Teal: each badge/text/progress rect.',20,IVORY)
    label(proof,(24,500),'Native title 16 px; goal 11 px; state 10 px; progress 11 px.',20,IVORY)
    label(proof,(24,540),'Only art is exported. Header, numbers, state labels and safe guides are review layers.',18,IVORY)
    save(proof,'02-board-shipping-and-safe-rects.png')
    return dict(position=[16,392,200,170], native_crop=[0,80,720,600],
                states=['met','in_progress','failed'], sliced_expansion=[260,210],
                text_sizes={'title':16,'goal':11,'state':10,'progress':11})


def board_readme():
    return ['', '## HUD board and rows', '',
            'Board200x170; desktop top-left(16,392). Minimum200x170. Header stays34px tall.',
            'Board title(14,7,172,22); row slots(10,36,180,40), (10,80,180,40), (10,124,180,40).',
            'Row/row-done180x40; minimum180x40; sliced corners20x18. Done uses a soft gold wash/brass edge.',
            'Each row local badge(5,6,28,28), text(39,5,92,30), progress(134,8,38,24).',
            'Two text baselines at local y5 and20; title11px/state10px; progress11px centred(153,20).',
            'Board title16px. Local badge/stamp applies the same normalized lower-right overlay rule.',
            'Fit/localize copy within92px or use two lines; keep the progress rectangle separate.',
            'Fit progress to its38px width:11px normally, down to9px for600/600; abbreviate larger values consistently.',
            'Met: row-done + tick + live Goal met label. Failed: normal row + broken + live Goal lost label.',
            'Progress remains live on failure; example8/7 means 8 lost against maximum7 (fewer than8).',
            'Expansion proof260x210 keeps borders fixed and stretches only centre strips. Reflow rows/text separately.',
            'No completed/failed state is inferred from colour alone. Use semantic labels and overlay shapes.']


def star(x,y,r,fill=IVORY):
    points=[]
    for i in range(10):
        angle=math.pi*i/5-math.pi/2
        rr=r if i%2==0 else r*.45
        points.append((x+math.cos(angle)*rr,y+math.sin(angle)*rr))
    return path('M'+' L'.join(f'{xx:.3f} {yy:.3f}' for xx,yy in points)+'Z',fill)


def tally_assets():
    body=(rect(4,7,552,350,22,NIGHT,opacity='.25')
          + rect(4,3,552,349,22,BRASS,NAVY,2)
          + rect(9,8,542,338,17,PAPER,NAVY,1.3)
          + path('M20 22 L9 17 V67 L24 60 M540 22 L551 17 V67 L536 60',CORAL,NAVY,1.5)
          + rect(19,18,522,49,7,NAVY,'#d3ad6a',1.5)
          + path('M34 23 H526','none','#577a8b',1)
          + path('M32 282 H528','none','#c6ad7e',1))
    for y in [82,136,190]:
        body+=rect(23,y,514,48,15,'#ede4cf','#d0bd96',1)
        body+=path(f'M85 {y+8} V{y+40} M454 {y+8} V{y+40}','none','#d0bd96',1)
    safe={'title':[38,26,422,30],
          'rows':[[24,y,512,48] for y in [82,136,190]],
          'badges':[[35,y+4,40,40] for y in [82,136,190]],
          'goal_text':[[95,y+6,275,36] for y in [82,136,190]],
          'progress':[[375,y+10,72,28] for y in [82,136,190]],
          'rewards':[[465,y+10,60,28] for y in [82,136,190]],
          'coin_badge':[29,247,32,32], 'coin_line':[69,248,260,28],
          'allthree_bonus':[343,248,185,28], 'button':[170,295,220,44],
          'button_text':[187,301,186,29], 'rosette':[475,-28,120,120]}
    # Alternating radii make physical pleats, with a separate inner brass rim.
    points=[]
    for i in range(48):
        angle=math.pi*i/24-math.pi/2
        rr=43 if i%2==0 else 37
        points.append((60+math.cos(angle)*rr,47+math.sin(angle)*rr))
    rosette=(path('M31 66 L21 111 40 102 52 116 62 72',BRASS,NAVY,1.5)
             +path('M60 71 L72 116 85 102 103 111 89 65',BRASS,NAVY,1.5)
             +path('M36 78 L30 102 M82 78 L93 103','none','#fff0bb',2)
             +circle(60,49,43,NAVY,opacity='.16')
             +path('M'+' L'.join(f'{x:.3f} {y:.3f}' for x,y in points)+'Z',BRASS,NAVY,1.5)
             +circle(60,47,33,BRASS,'#936a32',1.3)
             +circle(60,47,27,PAPER,NAVY,1.7)
             +circle(60,47,22,NAVY)
             +star(60,42,11,BRASS)+star(45,55,6,BRASS)+star(75,55,6,BRASS)
             +path('M38 26 A30 30 0 0 1 75 19','none',IVORY,1.5))
    return [dict(name='goal-tally',size=(560,360),body=body,border=[0]*4,safe=safe,stage=3),
            dict(name='goal-allthree',size=(120,120),body=rosette,border=[0]*4,
                 safe={'emblem':[33,20,54,54]},stage=3)]


def tally_sample():
    im=load('goal-tally',(560,360))
    label(im,(38,27),"Mira's evening goals",25,IVORY)
    rows=[('serve','Serve 30 guests','A full house, well fed','32/30'),
          ('perfect','Perfect plates','Every detail counts','4/4'),
          ('walkout','Lose fewer than 8','Everyone felt welcome','2/7')]
    for y,(kind,title,sub,progress) in zip([82,136,190],rows):
        paste(im,stamped(kind,40,'tick'),(35,y+4))
        label(im,(95,y+5),title,18)
        label(im,(95,y+26),sub,12,'#57717a')
        label(im,(411,y+24),progress,18,NAVY,anchor='mm')
        label(im,(495,y+24),'+30',18,TEAL,anchor='mm')
    paste(im,load('goal-coins',(32,32)),(29,247))
    label(im,(69,250),'Goal rewards   +90 coins',18)
    label(im,(343,251),'+1 popularity',17,TEAL)
    # Existing blank kit primary is review-only, drawn into the live button slot.
    button=Image.open(OUT/'v3-btn-primary.png').convert('RGBA').resize((220,44),R)
    paste(im,button,(170,295))
    label(im,(280,317),'Continue',21,IVORY,anchor='mm')
    return im


def tally_scene(width):
    scale=width/560
    card=tally_sample().resize((width,round(360*scale)),R)
    seal=load('goal-allthree',(round(120*scale),round(120*scale)))
    # Crop from the actual closing screen, at its centre; no painted-out pixels.
    bg=capture('day-closing-1440')
    panel_size=(650,450) if width==560 else (490,350)
    x0=(1440-panel_size[0])//2; y0=(900-panel_size[1])//2
    panel=bg.crop((x0,y0,x0+panel_size[0],y0+panel_size[1]))
    origin=(28,62) if width==560 else (22,47)
    paste(panel,card,origin)
    paste(panel,seal,(origin[0]+round(475*scale),origin[1]-round(28*scale)))
    return panel,(x0,y0,*panel_size),origin


def tally_reviews():
    sheet=Image.new('RGB',(1200,670),CREAM)
    label(sheet,(24,12),'Closing tally / three goals earned',30)
    label(sheet,(24,55),'Real closing capture under both cards. All text, totals, goal badges and button are separate live layers.',18)
    label(sheet,(24,102),'Desktop / 560 px card',23)
    label(sheet,(698,102),'Phone / 420 px card',23)
    desktop,dcrop,dorigin=tally_scene(560); phone,pcrop,porigin=tally_scene(420)
    sheet.paste(desktop.convert('RGB'),(24,146)); sheet.paste(phone.convert('RGB'),(698,146))
    label(sheet,(698,525),'90 coins = three met goals x 30.',18)
    label(sheet,(698,557),'All three: rosette + 1 popularity.',18)
    label(sheet,(24,626),'Phone proof keeps the 420 px card width; all layers scale together to 75%.',19)
    save(sheet,'03-tally-desktop-phone.png')
    proof=Image.new('RGB',(1200,620),NIGHT)
    label(proof,(24,12),'Blank tally + gold rosette / shipping art',28,IVORY)
    paste(proof,load('goal-tally',(560,360)),(24,82))
    paste(proof,load('goal-allthree'),(656,82))
    label(proof,(656,343),'120 x 120 logical / 240 x 240 PNG',20,IVORY)
    label(proof,(656,379),'Seal overlaps card at (475,-28).',20,IVORY)
    label(proof,(656,415),'Keep overlay parent unclipped.',20,IVORY)
    label(proof,(24,486),'Header / 3 row slots / reward line / existing primary button slot',21,IVORY)
    label(proof,(24,529),'Card remains proportional: 560 x 360 desktop, 420 x 270 phone. Simple sprite.',19,IVORY)
    label(proof,(24,570),'All-three emblem: three stars, no numerals. Reward rows stay readable without the seal.',19,IVORY)
    save(proof,'03-tally-shipping.png')
    safe=tally_sample()
    draw=ImageDraw.Draw(safe)
    for key,boxes in tally_assets()[0]['safe'].items():
        if key=='rosette': continue
        if isinstance(boxes[0],int): boxes=[boxes]
        for x,y,w,h in boxes:
            draw.rectangle((x,y,x+w,y+h),outline=CORAL if key in ['title','rows','button'] else TEAL,width=1)
    safeproof=Image.new('RGB',(1200,520),CREAM)
    label(safeproof,(24,12),'Tally safe rectangles / live-layer contract',28)
    paste(safeproof,safe,(24,88))
    label(safeproof,(632,96),'Coral: title, rows and button slot.',20)
    label(safeproof,(632,140),'Teal: badge, text, progress, reward.',20)
    label(safeproof,(632,184),'Title ends before the rosette.',20)
    label(safeproof,(632,228),'Coin line and popularity use separate rects.',20)
    label(safeproof,(632,272),'Button keeps the existing kit primary art.',20)
    label(safeproof,(24,475),'Every rectangle is documented in logical units in README.md and manifest.json.',20)
    save(safeproof,'03-tally-safe-rects.png')
    return dict(desktop={'width':560,'capture_crop':dcrop,'card_origin_in_crop':dorigin},
                phone={'width':420,'capture_crop':pcrop,'card_origin_in_crop':porigin,'scale':.75},
                rosette=[475,-28,120,120], primary_button='Assets/Art/UI/v3-btn-primary.png',
                reward_per_met=30,all_three_coins=90,all_three_popularity=1)


def tally_readme():
    lines=['','## Closing tally and all-three rosette','',
           'Tally560x360 Simple, preserve aspect; phone420x270 (all live layers at75%).',
           'Header ribbon/three row slots/coin line/primary button room are blank shipping art.',
           'Use goal badge40x40 and stamp20x20. Draw card first, then live badge/text/coin/button layers.',
           'Rosette120x120 Simple at card-relative(475,-28); overflows right35/top28, parent unclipped.',
           'Show rosette and live +1 popularity only when all three goals are met.',
           'Each met goal pays30 coins; live coin total sums met goals (0/30/60/90), never bake total.',
           'Pending/failed rows use relevant status stamp/text and0 reward; completed rows use tick and+30.',
           'Care goal example fewer than8 means max7;2/7 in tally means two guests lost within budget.',
           'For critic nights replace care badge/text/progress with critic/four-star goal.',
           'Sample live type: title25, goal18, supporting line12, progress/reward18, total18, bonus17, button21.',
           'Live baseline origins: goal(x95,rowY+5), supporting(x95,rowY+26); progress centre(411,rowY+24), reward centre(495,rowY+24).',
           'Existing v3-btn-primary.png is reused only in review, at(170,295,220,44); no button asset is copied or changed.',
           'Tally rect table (all x,y,w,h top-left logical; values scale uniformly on phone):','',
           '| Live layer | Safe rectangles |','|---|---|']
    for key,value in tally_assets()[0]['safe'].items():
        lines.append(f'| {key} | {value} |')
    return lines


def contact():
    names=['01-badges-28-40px.png','02-board-native-and-sliced.png','03-tally-desktop-phone.png']
    panels=[Image.open(REVIEW/n).convert('RGB') for n in names]
    result=Image.new('RGB',(1200,sum(p.height for p in panels)),CREAM)
    y=0
    for panel in panels:
        result.paste(panel,(0,y)); y+=panel.height
    target=REVIEW/'art-kit-8.png'; result.save(target)
    shutil.copyfile(target,ROOT/'docs/screens/ui-v3/art-kit-8.png')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def dump(name, value):
    (SOURCE/name).write_text(json.dumps(value, indent=2)+'\n')


def freeze_sources():
    records = {}
    for name in ['day-service-late-1440.png', 'day-service-late-844.png', 'day-closing-1440.png']:
        dest = REVIEW/('source-'+name)
        primary = ROOT.parent/'Catchline-ui2-sim/Logs/uiv2-native'/name
        chosen = primary if primary.exists() else ROOT/'docs/screens/ui-v2'/name
        if not dest.exists():
            shutil.copyfile(chosen, dest)
        records[name] = {'source': str(chosen), 'frozen': str(dest.relative_to(ROOT)),
                         'sha256': sha(dest), 'pixels': list(Image.open(dest).size),
                         'fallback': not primary.exists()}
    if not (SOURCE/'capture-provenance.json').exists():
        dump('capture-provenance.json', records)
    return json.loads((SOURCE/'capture-provenance.json').read_text())


def preservation():
    p = SOURCE/'preservation.json'
    if not p.exists():
        files = [x for x in OUT.glob('*') if x.is_file() and not x.name.startswith('v3-goal-')]
        files += [SOURCE.parent/f'build_kit{k}.py' for k in [2, 4, 5, 6, 7]]
        dump(p.name, {str(x.relative_to(ROOT)): sha(x) for x in files})
    return json.loads(p.read_text())


def export(a):
    w, h = a['size']
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{DEFS}{a["body"]}</svg>'
    src = SOURCE/(a['name']+'.svg')
    src.write_text(svg)
    target = OUT/('v3-'+a['name']+'.png')
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(target), output_width=2*w, output_height=2*h)
    meta = target.with_suffix('.png.meta')
    template = meta.read_text() if meta.exists() else (OUT/'v3-tl-critic.png.meta').read_text()
    if not meta.exists():
        template = re.sub(r'^guid: \w+', 'guid: '+uuid.uuid4().hex, template, count=1, flags=re.M)
    border = [v*2 for v in a['border']]
    template = re.sub(r'spriteBorder: \{[^}]+\}',
                      'spriteBorder: {'+', '.join(f'{k}: {v}' for k, v in zip('xyzw', border))+'}', template)
    meta.write_text(template)
    return dict(png=str(target.relative_to(ROOT)), svg=str(src.relative_to(ROOT)),
                viewBox=[0, 0, w, h], png_pixels=[w*2, h*2], slice_logical_LBRT=a['border'],
                slice_source_pixels_LBRT=border, safe_rects_top_left_logical=a['safe'],
                stage=a['stage'], image_type='Sliced' if any(border) else 'Simple',
                sha256=sha(target), guid=re.search(r'^guid: (\w+)', template, re.M)[1])


def font(size):
    return ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts/Fredoka-SemiBold.ttf'), size)


def label(im, xy, value, size=18, fill=NAVY, **kw):
    ImageDraw.Draw(im).text(xy, value, font=font(size), fill=fill, **kw)


def load(name, size=None):
    im = Image.open(OUT/('v3-'+name+'.png')).convert('RGBA')
    return im.resize(size, R) if size else im


def paste(im, other, xy):
    if im.mode == 'RGBA':
        im.alpha_composite(other.convert('RGBA'), xy)
    else:
        im.paste(other, xy, other)


def save(im, name):
    im.convert('RGB').save(REVIEW/name)


def capture(name):
    # Desktop screenshots are actual 2880x1800 exports of 1440x900 logical UI.
    return Image.open(REVIEW/('source-'+name+'.png')).convert('RGBA').resize((1440, 900), R)


def stamped(kind, size, state=None):
    im = load('goal-'+kind, (size, size))
    if state:
        stamp_size = size//2
        paste(im, load('goal-'+state, (stamp_size, stamp_size)), (size-stamp_size, size-stamp_size))
    return im


def badge_reviews():
    hud = capture('day-service-late-1440')
    # Untouched bar, including its real navy texture; duplicated crop for the state proof.
    bar = hud.crop((360, 8, 428, 68))
    sheet = Image.new('RGB', (1200, 560), CREAM)
    label(sheet, (24, 14), 'Tonight has a purpose / goal badges', 30)
    label(sheet, (24, 57), 'Actual 28 px on the native HUD crop; actual 40 px on cream. Labels are evidence only.', 18)
    for x, title, states in [(24, 'Clean badges / native navy bar', False),
                              (624, 'State stamps / same native bar', True)]:
        label(sheet, (x, 104), title, 21)
        for row in range(2):
            for col in range(4):
                i = row*4+col
                state = 'tick' if states and i == 0 else 'broken' if states and i == 6 else None
                region = bar.copy()
                paste(region, stamped(KINDS[i], 28, state), (20, 16))
                label(sheet, (x+col*82, 202+row*96), KINDS[i], 14)
                sheet.paste(region.convert('RGB'), (x+col*82, 136+row*96))
    label(sheet, (24, 345), '40 px / cream', 21)
    for i, kind in enumerate(KINDS):
        state = 'tick' if i == 0 else 'broken' if i == 6 else None
        paste(sheet, stamped(kind, 40, state), (28+i*146, 393))
        label(sheet, (25+i*146, 445), kind, 17)
    label(sheet, (24, 493), 'Teal check = met. Coral cross = failed. Overlays occupy the lower-right quarter, inside the badge rect.', 18)
    save(sheet, '01-badges-28-40px.png')
    originals = Image.new('RGB', (1200, 460), NIGHT)
    label(originals, (24, 14), 'Blank shipping badges / 2x exports', 28, IVORY)
    for i, kind in enumerate(KINDS):
        paste(originals, load('goal-'+kind), (24+i*146, 76))
        label(originals, (24+i*146, 218), kind, 17, IVORY)
    for i, state in enumerate(['tick', 'broken']):
        paste(originals, load('goal-'+state), (24+i*146, 282))
        label(originals, (24+i*146, 364), state, 17, IVORY)
    label(originals, (350, 293), '64x64 SVG -> 128x128 PNG', 22, IVORY)
    label(originals, (350, 336), '32x32 stamps -> 64x64 PNG', 22, IVORY)
    save(originals, '01-badges-shipping.png')
    return dict(hud_crop_logical=[360, 8, 68, 60], hud_crop_repeated_per_badge=True, badge_display=[28, 40],
                stamp_display=[14, 20], stamp_anchor_normalized=[1, 1],
                stamp_rect_normalized=[.5, .5, .5, .5])


def write_readme(stage):
    lines = ['# Service UI kit 8 - evening goals', '',
             'SERVICE-UI-KIT-8 / Codex 1 (Windows app) / 2026-10-28.',
             'Exact kit2 DEFS and accepted kit4-7 palette. Editable SVG, CairoSVG 2x exports.',
             'Shipping sprites contain no words or numerals. All sample text/numbers are review-only.', '',
             'All rects are **x,y,width,height from top left in logical SVG units**.',
             'Multiply by 2 for texture pixels; Unity bottom-left y = height - top - rectHeight.', '',
             '## Badges and stamps', '',
             'Eight `v3-goal-{serve,coins,perfect,combo,upsell,gulls,walkout,critic}`:',
             '64x64 SVG / 128x128 PNG, round ivory/brass discs without tails.',
             'Draw entire texture at 28px on the service HUD or 40px on cream.',
             'No live text in the badge. Glyph bounds (10,9,44,43).',
             '`v3-goal-{tick,broken}`: 32x32 SVG / 64x64 PNG, teal/check and coral/cross.',
             'At badge width B, draw stamp at (B/2,B/2,B/2,B/2) relative to badge top-left.',
             'Thus 28px badge: (14,14,14,14); 40px badge: (20,20,20,20).',
             'Stamp is inside the full badge rect, after badge art; no clipping overflow needed.',
             'Keep status text/live progress as a second cue, never color alone.', '',
             '## Sprite import contract', '',
             'Sprite/Single, Full Rect mesh, centre pivot, 100PPU, sRGB, straight alpha,',
             'alphaIsTransparency, bilinear, Clamp U/V/W, no mipmaps, no NPOT scaling,',
             'uncompressed DefaultTexturePlatform. Preserve GUIDs on regeneration.',
             'Simple assets preserve aspect. Sliced assets use Unity Image.Type.Sliced or',
             'equivalent nine-slice; do not stretch a whole texture. border order L/B/R/T.', '',
             'The consumer must map **2 source pixels to 1 logical unit**, including slice borders.',
             'When implementing a UI nine-slice, use the logical table for destination corner sizes',
             'and the doubled source-pixel table for sampling. A 200px rect alone does not halve borders.', '',
             '| Sprite | Logical size | PNG size | Logical slice L/B/R/T | Source-pixel slice |',
             '|---|---|---|---|---|']
    for a in assets_for(stage):
        lines.append(f'| v3-{a["name"]} | {a["size"][0]}x{a["size"][1]} | {a["size"][0]*2}x{a["size"][1]*2} | {a["border"]} | {[v*2 for v in a["border"]]} |')
    lines += ['', '## Rebuild and evidence', '',
              '`/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit8.py --stage 3`',
              'Cumulative stages 1/2/3 follow the brief order. Needs CairoSVG/Pillow and existing Fredoka.',
              '`manifest.json` is machine-readable layout/import/export truth.',
              '`capture-provenance.json` records the three frozen source screenshots and hashes.',
              'All three simulator Logs captures were present at capture time; no fallback used.',
              'Desktop source is 2880x1800, downsampled once to1440x900 logical; phone is2532x1170.',
              'Frozen captures allow reproducible crops during other owners\' capture passes.',
              'No room/HUD pixels are painted out. Composites are art evidence, not runtime gameplay acceptance.',
              'No C#, Resources, Crew, other-kit or RestaurantService/model writes; no Git or Unity invocation.']
    if stage >= 2:
        lines.extend(board_readme())
    if stage >= 3:
        lines.extend(tally_readme())
    (SOURCE/'README.md').write_text('\n'.join(lines)+'\n')


def audit(assets, manifest):
    for a in assets:
        name = a['name']
        m = manifest[name]
        im = load(name)
        assert im.mode == 'RGBA' and list(im.size) == m['png_pixels']
        alpha = im.getchannel('A')
        assert alpha.getextrema()[0] == 0 and alpha.getextrema()[1] == 255
        assert not any(alpha.crop(box).getbbox() for box in [(0,0,im.width,1), (0,im.height-1,im.width,im.height),
                                                            (0,0,1,im.height), (im.width-1,0,im.width,im.height)])
        xml = ET.parse(SOURCE/(name+'.svg'))
        assert not any(e.tag.split('}')[-1] in ['text', 'image', 'foreignObject'] for e in xml.iter())
        assert DEFS in (SOURCE/(name+'.svg')).read_text()
        meta = (OUT/('v3-'+name+'.png.meta')).read_text()
        for setting in ['spriteMode: 1', 'spriteMeshType: 1', 'textureType: 2', 'enableMipMap: 0',
                        'sRGBTexture: 1', 'alphaIsTransparency: 1', 'filterMode: 1', 'nPOTScale: 0',
                        'wrapU: 1', 'wrapV: 1', 'wrapW: 1']:
            assert setting in meta, (name, setting)
    incumbent = preservation()
    changes_file=SOURCE/'concurrent-incumbent-changes.json'
    changes=json.loads(changes_file.read_text()) if changes_file.exists() else []
    expected=dict(incumbent)
    for change in changes:
        p=change['path']
        assert p.startswith('Assets/Art/UI/') and p.endswith('.meta') and '/v3-goal-' not in p
        assert incumbent[p]==change['before']
        expected[p]=change['current']
    assert all(sha(ROOT/p) == digest for p, digest in expected.items())
    guids = [m['guid'] for m in manifest.values()]
    assert len(guids) == len(set(guids))
    return dict(result='PASS', assets=len(assets), export_scale=2, transparent_edges=True,
                no_baked_text=True, exact_kit2_DEFS=True, incumbent_files_unchanged=len(incumbent)-len(changes),
                concurrent_unowned_meta_updates=len(changes))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', type=int, choices=[1,2,3], default=3)
    args = parser.parse_args()
    REVIEW.mkdir(parents=True, exist_ok=True)
    preservation()
    freeze_sources()
    assets = assets_for(args.stage)
    manifest = {a['name']: export(a) for a in assets}
    dump('manifest.json', manifest)
    evidence = {'badges': badge_reviews()}
    if args.stage >= 2:
        evidence['board'] = board_reviews()
    if args.stage >= 3:
        evidence['tally'] = tally_reviews()
        contact()
    dump('review-evidence.json', evidence)
    write_readme(args.stage)
    report = audit(assets, manifest)
    dump('audit.json', report)
    print(json.dumps(report))


if __name__ == '__main__':
    main()
