"""SERVICE-UI-KIT-6: editable SVG -> CairoSVG 2x -> Unity sprites.

WSL: /home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit6.py --stage 1..3
Stages are cumulative, in brief order. Other builders are never imported.
All lettering and sample ratings occur only in review evidence.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import math
import random
import re
import uuid
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent / 'kit-6'
OUT = ROOT / 'Assets/Art/UI'
REVIEW = SOURCE / 'review'
CAPTURE = ROOT.parent / 'Catchline-ui2-sim/Logs/uiv2-native/day-service-late-1440.png'
PHONE = CAPTURE.with_name('day-service-late-844.png')
NAVY, TEAL, CORAL = '#173f57', '#168f9f', '#df7257'
CREAM, NIGHT, IVORY = '#f4efe3', '#182f3a', '#fffaf0'
PAPER, BRASS, STEEL = [f'url(#{s})' for s in ('paper', 'brass', 'steel')]
tree = ast.parse((SOURCE.parent / 'build_kit2.py').read_text())
DEFS = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'DEFS' for t in n.targets))
RESAMPLE = Image.Resampling.LANCZOS


def path(d, fill=NAVY, stroke='none', width=3, **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def ellipse(x, y, rx, ry, fill, stroke='none', width=3, **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def circle(x, y, r, fill, stroke='none', width=3, **attrs):
    return ellipse(x, y, r, r, fill, stroke, width, **attrs)


def rect(x, y, w, h, r, fill, stroke='none', width=3, **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def star_path(x, y, r, inner=.46, points=5):
    coords = []
    for i in range(points*2):
        a = -math.pi/2 + math.pi*i/points
        radius = r if i % 2 == 0 else r*inner
        coords.append((x+math.cos(a)*radius, y+math.sin(a)*radius))
    return 'M' + ' L'.join(f'{x:.3f} {y:.3f}' for x, y in coords) + 'Z'


def chip(color):
    return (circle(48, 50, 43, NAVY, opacity='.18')
            + circle(48, 47, 43, color, NAVY, 2.6)
            + path('M13 34 A37 37 0 0 1 60 12', 'none', '#fff0bd', 2, opacity='.8')
            + circle(48, 47, 34.5, PAPER, NAVY, 1.8)
            + path('M23 27 A31 31 0 0 1 68 22', 'none', '#fffdf5', 1.8))


def assets_for(stage):
    assets = []

    def add(name, body, size, group, safe=None, note='', repeat=False):
        assets.append(dict(name=name, body=body, size=size, stage=group,
                           safe=safe, note=note, repeat=repeat))

    for kind, color in [('gadget', TEAL), ('dish', BRASS), ('night', CORAL)]:
        add('chip-'+kind, chip(color), (96, 96), 1,
            {'illustration': [14.4, 13.4, 67.2, 67.2], 'empty_face_circle': [48, 47, 33.5]},
            'Blank cream centre. Whole kit5 illustration at70% chip width; no glyph baked in.')
    burst = (path(star_path(20, 21, 17, .78, 10), NAVY, opacity='.18')
             + path(star_path(20, 19, 17, .78, 10), BRASS, NAVY, 1.8)
             + path('M10 12 Q15 6 21 7', 'none', '#fff0bd', 2))
    add('chip-new', burst, (40, 40), 1, note='Wordless ten-point brass burst; display14px on a40px chip.')
    if stage >= 2:
        critic_assets(add)
    if stage >= 3:
        rain_assets(add)
    return assets


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


STAR_RECTS = [[88+i*40, 35, 32, 32] for i in range(5)]
REVIEW_BODY = [28, 101, 264, 48]


def beret():
    return (path('M36 48 Q31 31 48 28 Q62 13 83 27 Q99 29 98 43 Q96 50 80 50Z', NAVY)
            + path('M51 29 Q61 23 73 26', 'none', '#416c80', 3)
            + path('M70 23 L73 17', 'none', NAVY, 4))


def critic_assets(add):
    outline = 'M49 104 A49 49 0 1 1 79 104 L64 121Z'
    glyph = (path('M39 95 Q41 79 55 77 H75 Q92 81 94 95Z', TEAL, NAVY, 3)
             + path('M56 76 L65 85 75 77 71 95 H59Z', PAPER, NAVY, 2)
             + ellipse(64, 61, 20, 21, PAPER, NAVY, 3)
             + beret()
             + circle(55, 60, 8.5, IVORY, NAVY, 3)
             + circle(76, 60, 8.5, IVORY, NAVY, 3)
             + path('M64 59 H67 M43 58 L47 59 M84 59 L88 56', 'none', NAVY, 2.5)
             + path('M66 68 L64 73 H68 M57 77 Q64 81 71 76', 'none', NAVY, 2)
             + '<g transform="rotate(-8 84 86)">'
             + rect(73, 76, 28, 25, 2, CORAL, NAVY, 2.5)
             + rect(78, 76, 23, 22, 1, PAPER, NAVY, 2)
             + path('M82 78 V95', 'none', '#d6ad65', 1.5)
             + path('M95 86 L104 72 107 74 98 89 94 91Z', BRASS, NAVY, 1.5) + '</g>')
    pin = (path(outline, NAVY, opacity='.23', transform='translate(0 3)')
           + path(outline, PAPER, NAVY, 4)
           + path('M24 37 A43 43 0 0 1 91 22', 'none', '#fffdf5', 3) + glyph)
    add('svc-critic', pin, (128, 128), 2,
        {'anchor_tip': [64, 121]}, 'Kit4 pointed paper disc; round glasses, navy beret, teal coat and blank notebook. Display32-40px square.')
    torn = ('M12 14 L40 10 65 14 91 10 120 14 148 11 176 14 207 10 235 14 264 11 292 14 308 11 '
            'L306 38 310 62 307 88 310 114 307 139 310 165 306 185 '
            'L280 190 254 186 228 190 200 186 171 191 143 187 116 191 87 187 59 191 34 187 11 190 '
            'L14 164 10 140 13 115 10 89 13 65 10 39Z')
    clipping = (path(torn, NAVY, opacity='.18', transform='translate(0 3)')
                + path(torn, PAPER, '#a68755', 1.4)
                + path('M21 23 L301 20 M20 176 L298 179', 'none', '#fffdf5', 2)
                + circle(47, 45, 24, 'none', TEAL, 2)
                + circle(47, 45, 20.5, 'none', TEAL, 1, opacity='.4')
                + '<g transform="translate(17 24) scale(.45)">' + beret() + '</g>'
                + path('M27 83 H293', 'none', NAVY, 1.6)
                + path('M28 86 H292 M28 162 H292', 'none', '#d6c49c', 1))
    for x, y, w, h in STAR_RECTS:
        clipping += path(star_path(x+w/2, y+h/2, 14), '#f0e5cf', '#a68755', 1.5)
    add('svc-critic-review', clipping, (320, 200), 2,
        {'stars': STAR_RECTS, 'body': REVIEW_BODY},
        'Newspaper scrap, beret seal, five empty outlined star slots; live single line in body. Simple, no slicing.')


def critic_reviews():
    # Same crop is used for the rain proof. Downsample the supersampled capture once.
    service = Image.open(CAPTURE).convert('RGB').crop((1240, 450, 2776, 1474)).resize((768, 512), RESAMPLE)
    proof = service.copy()
    # Tip at logical service(878,348), just above the first round table.
    paste(proof, load('svc-critic', (32, 32)), (242, 93))
    save(proof, '02-critic-service-32px.png')
    sheet = Image.new('RGB', (1200, 830), CREAM)
    d = ImageDraw.Draw(sheet)
    d.text((28, 18), 'The critic / stays above the table all night', font=font(28), fill=NAVY)
    d.text((28, 57), 'Actual 32 px marker over the supplied service capture. Sample review below is live UI.', font=font(18), fill=NAVY)
    sheet.paste(proof, (24, 94))
    d.rounded_rectangle((812, 94, 1176, 606), radius=18, fill=NIGHT)
    d.text((836, 116), 'Service sizes', font=font(22), fill=IVORY)
    for i, size in enumerate((28, 32, 40)):
        paste(sheet, load('svc-critic', (size, size)), (842+i*105, 169))
        d.text((842+i*105, 220), f'{size} px', font=font(18), fill=IVORY)
    paste(sheet, load('svc-critic', (224, 224)), (871, 303))
    d.text((836, 555), 'Beret / glasses / notebook', font=font(18), fill=IVORY)
    clipping = load('svc-critic-review', (320, 200))
    # The only filled rating stars and words are on this review-only copy.
    gold_svg = '<svg xmlns="http://www.w3.org/2000/svg" width="320" height="200">' + DEFS
    for x, y, w, h in STAR_RECTS[:4]:
        gold_svg += path(star_path(x+w/2, y+h/2, 13), BRASS, '#936a32', .8)
    gold_svg += '</svg>'
    from io import BytesIO
    clipping.alpha_composite(Image.open(BytesIO(cairosvg.svg2png(bytestring=gold_svg.encode()))).convert('RGBA'))
    cd = ImageDraw.Draw(clipping)
    cd.text((160, 125), 'A warm welcome. A fine catch.', font=font(15), fill=NAVY, anchor='mm')
    paste(sheet, clipping, (26, 600))
    d.text((380, 628), 'Four sample gold stars; fifth slot remains empty.', font=font(21), fill=NAVY)
    d.text((380, 666), 'Star slots, live line and all safe rects are in the README.', font=font(18), fill=NAVY)
    d.text((380, 704), 'Production art contains no words, scores or numerals.', font=font(18), fill=NAVY)
    save(sheet, '02-critic-and-review.png')
    shipping_preview(['svc-critic', 'svc-critic-review'], '02-critic-blank.png')
    return {'room_crop_source_pixels': [1240, 450, 2776, 1474],
            'room_crop_logical_1440': [620, 225, 1388, 737],
            'critic_display_px': 32, 'critic_anchor_logical_1440': [878, 348],
            'star_slots_svg_units': STAR_RECTS, 'review_line_svg_units': REVIEW_BODY}


def rain_geometry(cols=1, rows=1):
    """A toroidal field. Edge-crossing strokes continue into the neighbouring tile.

    cols/rows also allow an independent extended vector render for seam validation.
    Softness comes from nested faint round strokes, never opaque fog or a flat wash.
    """
    rng = random.Random(62810)
    streaks = []
    for i in range(42):
        x, y = rng.uniform(0, 256), rng.uniform(0, 256)
        length, width = rng.uniform(17, 33), rng.uniform(.65, 1.05)
        dx, dy = length*math.sin(math.radians(15)), length*math.cos(math.radians(15))
        alpha = .4 if i in (7, 30) else rng.uniform(.22, .31)
        for tx in range(-1, cols+1):
            for ty in range(-1, rows+1):
                xx, yy = x+256*tx, y+256*ty
                line = f'M{xx+dx:.4f} {yy:.4f} L{xx:.4f} {yy+dy:.4f}'
                streaks.append(path(line, 'none', '#afe2e5', width+1.3, opacity='.025'))
                streaks.append(path(line, 'none', '#c7d9d9', width+.55, opacity='.035'))
                streaks.append(path(line, 'none', '#f5fff9', width, opacity=f'{alpha:.4f}'))
    return ''.join(streaks)


def rain_assets(add):
    add('fx-rain', rain_geometry(), (256, 256), 3, repeat=True,
        note='Final512x512px seamless tile; 15deg from vertical, pale soft streaks at authored alpha. Draw256 logical pixels per tile with Repeat UVs, white tint alpha1.')
    splash = ''
    radii = [1.8, 3.8, 6.1, 8.4, 10.6, 12.4, 13.6, 14]
    alphas = [.38, .64, .57, .47, .35, .23, .10, 0]
    for i, (r, alpha) in enumerate(zip(radii, alphas)):
        frame = ''
        if alpha:
            frame += ellipse(16, 21.7, r, r*.31, 'none', TEAL, 1.1, opacity=f'{alpha*.4:.3f}')
            frame += ellipse(16, 21, r, r*.31, 'none', '#afe2e5', .9, opacity=str(alpha))
            frame += path(f'M{16-r*.8:.3f} 20.8 Q16 {21-r*.31:.3f} {16+r*.5:.3f} {21-r*.19:.3f}',
                          'none', '#f5fff9', .7, opacity=f'{alpha*.75:.3f}')
            if i < 4:
                h = [2.5, 7, 9, 6][i]
                frame += path(f'M{13-i} {18-h} l-1 -2 M{19+i} {18-h+1} l1 -2',
                              'none', '#afe2e5', 1, opacity=f'{alpha*.8:.3f}')
        splash += f'<g transform="translate({i*32} 0)">{frame}</g>'
    add('fx-rain-splash', splash, (256, 32), 3,
        {'frames': [[i*32, 0, 32, 32] for i in range(8)], 'contact_point_per_frame': [16, 21]},
        'Final512x64 strip, eight64x64px frames left-to-right; last frame fully transparent for a clean one-shot end. Clamp, Simple, runtime UV selection.')


def tiled_rain():
    tile = load('fx-rain')
    repeated = Image.new('RGBA', (1536, 1024))
    for y in range(2):
        for x in range(3):
            repeated.alpha_composite(tile, (x*512, y*512))
    return repeated


def rain_reviews():
    repeated = tiled_rain()
    base = Image.open(CAPTURE).convert('RGBA').crop((1240, 450, 2776, 1474))
    # Include both the new critic presence marker and an incumbent kit4 order pin.
    # These are on the room layer in this conservative proof, so rain passes over them too.
    base.alpha_composite(load('svc-critic', (64, 64)), (484, 186))
    base.alpha_composite(load('svc-order', (64, 64)), (906, 184))
    rainy = Image.alpha_composite(base, repeated)
    save(rainy, '03-rain-tiled-3x2.png')
    logical = rainy.resize((768, 512), RESAMPLE)
    dry = base.resize((768, 512), RESAMPLE)
    sheet = Image.new('RGB', (1600, 840), CREAM)
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), 'Rain over service / no mist, no room-darkening wash', font=font(30), fill=NAVY)
    d.text((24, 58), 'Same crop: dry at left; 3 x 2 seamless512px tiles at authored alpha at right. Actual service scale.', font=font(20), fill=NAVY)
    sheet.paste(dry.convert('RGB'), (24, 104))
    sheet.paste(logical.convert('RGB'), (808, 104))
    d.text((24, 632), 'Splash strip / eight64x64px PNG frames, left to right; last frame clear', font=font(21), fill=NAVY)
    d.rounded_rectangle((24, 674, 1568, 814), radius=16, fill=NIGHT)
    paste(sheet, load('fx-rain-splash'), (44, 702))
    for i in range(8):
        d.text((76+i*64, 780), str(i+1), font=font(16), fill=IVORY, anchor='mm')
    # Runtime-size sample splashes on the same visible deck; no screen-space text in shipping art.
    deck = Image.open(CAPTURE).convert('RGBA').resize((1440, 900), RESAMPLE).crop((700, 665, 1000, 745))
    strip = load('fx-rain-splash')
    for i in range(1, 7):
        frame = strip.crop((i*64, 0, (i+1)*64, 64)).resize((32, 32), RESAMPLE)
        deck.alpha_composite(frame, (8+(i-1)*47, 18))
    paste(sheet, deck, (628, 697))
    d.text((962, 705), '32px display frames on deck', font=font(20), fill=IVORY)
    d.text((962, 745), '0.32 seconds / one-shot / stagger spawns', font=font(18), fill=IVORY)
    save(sheet, '03-rain-and-splashes.png')

    tileproof = Image.new('RGB', (1100, 630), CREAM)
    td = ImageDraw.Draw(tileproof)
    td.rectangle((550, 0, 1100, 630), fill=NIGHT)
    for x, fg in [(20, NAVY), (570, IVORY)]:
        td.text((x, 15), 'Actual512px tile / authored alpha', font=font(21), fill=fg)
        paste(tileproof, load('fx-rain'), (x, 56))
    save(tileproof, '03-rain-tile-blank.png')
    frames = Image.new('RGB', (1200, 400), NIGHT)
    fd = ImageDraw.Draw(frames)
    fd.text((24, 18), 'Splash / original strip and individual2x loupes', font=font(25), fill=IVORY)
    paste(frames, strip, (24, 64))
    for i in range(8):
        frame = strip.crop((i*64, 0, (i+1)*64, 64))
        paste(frames, frame.resize((128, 128), Image.Resampling.NEAREST), (24+i*146, 176))
        fd.text((88+i*146, 330), f'{i+1}', font=font(20), fill=IVORY, anchor='mm')
    save(frames, '03-splash-frames.png')
    return {'rain_tiling': [3, 2], 'rain_proof_source_size': [1536, 1024],
            'rain_draw_tile_logical': [256, 256], 'rain_tint_alpha': 1,
            'rain_angle_degrees_from_vertical': 15, 'rain_streaks_per_tile': 42,
            'splash_png_frame_rects': [[i*64, 0, 64, 64] for i in range(8)],
            'rain_proof_note': 'Same source crop. Room unchanged; critic/order pins composited before rain, conservatively demonstrating legibility even under rain.'}


def contact():
    panels = [Image.open(REVIEW/name).convert('RGB') for name in
              ('01-chips-40px.png', '02-critic-and-review.png', '03-rain-and-splashes.png')]
    # Keep every proof at its native evidence scale; avoid shrinking the40/32px tests.
    canvas = Image.new('RGB', (1600, 96+sum(p.height for p in panels)+24*len(panels)), CREAM)
    d = ImageDraw.Draw(canvas)
    d.text((24, 15), 'Catchline / service kit 6', font=font(34), fill=NAVY)
    d.text((24, 58), 'Kept cards, the critic and rain. Text and sample scores below are live-layout evidence only.', font=font(20), fill=NAVY)
    y = 96
    for im in panels:
        canvas.paste(im, ((1600-im.width)//2, y))
        y += im.height+24
    canvas.save(REVIEW/'contact-sheet.png')
    canvas.save(ROOT/'docs/screens/ui-v3/art-kit-6.png')


def font(size):
    return ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts/Fredoka-SemiBold.ttf'), size)


def load(name, size=None):
    im = Image.open(OUT/f'v3-{name}.png').convert('RGBA')
    return im.resize(size, RESAMPLE) if size else im


def paste(im, other, xy):
    im.paste(other, xy, other)


def save(im, name):
    im.convert('RGB').save(REVIEW/name)


def shipping_preview(names, filename):
    """Openable originals on cream and sea, with their transparency retained in Assets."""
    canvas = Image.new('RGB', (1100, 440), CREAM)
    d = ImageDraw.Draw(canvas)
    d.rectangle((550, 0, 1100, 440), fill=NIGHT)
    for side, fg in [(0, NAVY), (550, IVORY)]:
        d.text((side+24, 16), 'Blank shipping art / no live overlay', font=font(21), fill=fg)
        for i, name in enumerate(names):
            im = load(name)
            im.thumbnail((220, 220), RESAMPLE)
            x, y = side+20+(i % 2)*270, 56+(i//2)*185
            if len(names) > 2:
                im.thumbnail((142, 142), RESAMPLE)
            paste(canvas, im, (x, y))
            d.text((x, y+im.height+6), name, font=font(16), fill=fg)
    save(canvas, filename)


def chip_composite(kind, illustration, size=40, new=False):
    # First compose at source-pixel resolution, then downsample as one runtime image.
    im = load('chip-'+kind)
    art = load('ncard-'+illustration, (134, 134))
    im.alpha_composite(art, (29, 27))
    im = im.resize((size, size), RESAMPLE)
    if new:
        overlay = Image.new('RGBA', (size+5, size+5))
        overlay.alpha_composite(im, (0, 5))
        overlay.alpha_composite(load('chip-new', (14, 14)), (size-9, 0))
        return overlay
    return im


def chip_reviews():
    sheet = Image.new('RGB', (1200, 610), CREAM)
    d = ImageDraw.Draw(sheet)
    d.text((28, 18), 'Kept by the house / service rail chips', font=font(28), fill=NAVY)
    d.text((28, 57), 'Actual 40 px. Kit 5 art at 70%. Brass burst marks the latest keep.', font=font(19), fill=NAVY)
    actual_rail = Image.open(CAPTURE).convert('RGB').getpixel((2000, 1620))
    examples = [('gadget', 'warming-lamp'), ('dish', 'ice-cream'), ('night', 'rain')]
    for row, (bg, fg, caption) in enumerate([(actual_rail, NAVY, 'Sampled cream crew rail'), (NIGHT, IVORY, 'Night sea')]):
        y = 104+row*188
        d.rounded_rectangle((20, y, 1180, y+171), radius=20, fill=bg)
        d.text((42, y+15), caption, font=font(19), fill=fg)
        for col, (kind, art) in enumerate(examples):
            x = 64+col*380
            paste(sheet, chip_composite(kind, art, 40, new=(col == 0)), (x, y+65))
            d.text((x+58, y+69), kind, font=font(20), fill=fg)
            # A nearest-neighbour loupe proves the actual40 raster rather than a fresh large rendering.
            small = chip_composite(kind, art, 40, new=(col == 0))
            paste(sheet, small.resize((small.width*2, small.height*2), Image.Resampling.NEAREST), (x+210, y+53))
    rail = Image.open(CAPTURE).convert('RGB').resize((1440, 900), RESAMPLE).crop((560, 770, 1400, 860))
    for col, (kind, art) in enumerate(examples):
        paste(rail, chip_composite(kind, art, 40, new=col == 0), (650+col*58, 23))
    sheet.paste(rail, (28, 503))
    d.text((891, 522), 'Right of the crew', font=font(18), fill=NAVY)
    save(sheet, '01-chips-40px.png')
    shipping_preview(['chip-gadget', 'chip-dish', 'chip-night', 'chip-new'], '01-chips-blank.png')
    return {'cream_rail_rgb': actual_rail, 'rail_crop_logical_1440': [560, 770, 1400, 860],
            'capture': str(CAPTURE), 'capture_size': Image.open(CAPTURE).size,
            'phone_capture_size': Image.open(PHONE).size, 'capture_sha256': sha(CAPTURE)}


def export(a):
    name, (w, h) = a['name'], a['size']
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{DEFS}{a["body"]}</svg>'
    source = SOURCE/f'{name}.svg'
    source.write_text(svg)
    target = OUT/f'v3-{name}.png'
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(target), output_width=w*2, output_height=h*2)
    meta = target.with_suffix('.png.meta')
    template = meta.read_text() if meta.exists() else (OUT/'v3-card.png.meta').read_text()
    if not meta.exists():
        template = re.sub(r'guid: [a-f0-9]+', f'guid: {uuid.uuid4().hex}', template, count=1)
    template = template.replace('spriteMode: 0', 'spriteMode: 1')
    template = re.sub(r'spriteBorder: \{[^}]+\}', 'spriteBorder: {x: 0, y: 0, z: 0, w: 0}', template)
    for axis in 'UVW':
        template = re.sub(rf'wrap{axis}: \d+', f'wrap{axis}: {0 if a["repeat"] else 1}', template)
    meta.write_text(template)
    return dict(png=str(target.relative_to(ROOT)), svg=str(source.relative_to(ROOT)),
                size=[w*2, h*2], viewBox=[0, 0, w, h], stage=a['stage'],
                slice_pixels=[0, 0, 0, 0], safe_rects_svg_units=a['safe'],
                wrap='Repeat' if a['repeat'] else 'Clamp', note=a['note'],
                sha256=sha(target), guid=re.search(r'^guid: (\w+)', template, re.M)[1])


def write_readme(stage):
    (SOURCE/'README.md').write_text('''# Service kit 6 - kept cards, the critic, rain

SERVICE-UI-KIT-6 / Codex 1 (Windows app) / 2026-10-28.
SVG geometry, exact kit-2 DEFS and kit-4/5 palette; CairoSVG exports at 2x.
Shipping art has no baked words, numerals, scores or filled rating stars.
Review lettering, sample rating and kit-5 illustration overlays are evidence only.

## Chips - item 1

| Key (in Assets/Art/UI) | SVG viewBox | PNG pixels | Use |
| --- | --- | --- | --- |
| v3-chip-gadget | 96x96 | 192x192 | Teal rim, blank cream face |
| v3-chip-dish | 96x96 | 192x192 | Brass rim, blank cream face |
| v3-chip-night | 96x96 | 192x192 | Coral rim, blank cream face |
| v3-chip-new | 40x40 | 80x80 | Wordless brass starburst |

All rectangles here are **x/y/width/height from top-left, in SVG units**.
Double for source PNG pixels. The blank cream face is a circle centred at
`(48,47)`, radius `33.5`. Fit the **whole** kit-5 illustration texture inside
`(14.4,13.4,67.2,67.2)` (70% of chip width); keep its own transparent padding.
At a 40px chip the illustration rect is `(6,5.5833,28,28)`.

For the last-kept flag, draw the entire burst texture in a 14x14 display rect
at `(chipLeft+31,chipTop-5)` relative to a 40px chip. Reserve five pixels of
overflow above/right and disable clipping there. Layer chip, illustration,
then burst. The proof includes all three actual40px on the sampled cream rail
and night sea, plus one burst and the actual rail-right crop. Chip colours
identify kind; the separately drawn illustration identifies the actual card.

## Critic - item 2

| Key | SVG viewBox | PNG pixels | Use |
| --- | --- | --- | --- |
| v3-svc-critic | 128x128 | 256x256 | Kit-4 pointed paper pin, beret, round glasses, notebook |
| v3-svc-critic-review | 320x200 | 640x400 | Torn newspaper clipping, beret seal and five empty star slots |

Keep the critic pin square, usually **32x32 display pixels** (28/32/40 proofs).
Its tip is `(64,121)`, normalized `(0.5,0.9453125)` from top-left, matching kit4.
Keep it anchored over the critic's table throughout the night. It conveys
presence independently of a changing order/task marker; runtime owns placement.

The clipping's live rating slots are:

| Star, left to right | SVG rect | Source PNG rect |
| --- | --- | --- |
| 1 | (88,35,32,32) | (176,70,64,64) |
| 2 | (128,35,32,32) | (256,70,64,64) |
| 3 | (168,35,32,32) | (336,70,64,64) |
| 4 | (208,35,32,32) | (416,70,64,64) |
| 5 | (248,35,32,32) | (496,70,64,64) |

Each empty five-point outline has outer radius14, inner/outer ratio0.46,
starts at twelve o'clock, and is centred in its slot. Overlay a filled gold
five-point star of outer radius13 in the same centre (2-3px slot inset).
The proof fills four and leaves the fifth empty. Keep any gameplay score live.

**Live body safe rect `(28,101,264,48)`**, PNG `(56,202,528,96)`.
Use one centred navy line, e.g. Fredoka SemiBold15 at logical320px card width.
Fit/localize the line within264px, vertically centred at125; sample copy is
only in review images. For Unity bottom-left coordinates use
`yBottom = viewBoxHeight - yTop - height` before applying display scale.

## Import and draw contract

Chips, burst, pin and clipping: Image Type **Simple**, preserve aspect.
**All slice borders are `(0,0,0,0)` source pixels, L/B/R/T. No nine-slicing.**
Sprite/Single, Full Rect mesh, centred pivot,100PPU, sRGB, straight alpha with
alpha transparency enabled, bilinear filtering, no mipmaps, no NPOT scaling,
uncompressed default platform. Clamp except the repeating rain tile, if present.
GUIDs are retained on regeneration; runtime-only resources are not copied here.
Do not atlas the rain tile when repeating UVs across its whole texture.

## Regeneration and evidence

```sh
/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit6.py --stage 3
```

Requires CairoSVG/Pillow and the existing Fredoka font. Stages1/2/3 are cumulative
in brief priority order. Builders from older kits are parsed/read, never imported.
Only assigned kit6 paths are written. `manifest.json` contains exact sizes,
safe rectangles, GUIDs, wraps and hashes; `audit.json` checks structure/imports
and incumbent hashes. `visual-review.json` records personally opened image hashes;
regeneration cannot itself grant visual approval.

Review files `01-*` show actual40px composited and blank chips; `02-*` show
the actual32px service pin, sample live rating/line and blank shipping critic art.
Capture: sibling `Catchline-ui2-sim/Logs/uiv2-native/day-service-late-1440.png`,
actual2880x1800 pixels. Native logical1440x900 is obtained by2x downsampling.
Room crop source pixels `(1240,450,2776,1474)` gives1536x1024, or768x512 logical.
The unchanged source includes existing order pins. Crop pixels are not tinted
or darkened. Phone capture `day-service-late-844.png` is2532x1170 and was inspected
as context; no rail is fabricated on that different layout.

Art evidence is separate from Unity import, gameplay wiring and native acceptance,
which remain Claude's work. No C#, Resources, other-kit, Crew, Restaurant model
or RestaurantService writes, no Git commands/commit and no Unity execution.
''')
    if stage >= 3:
        with (SOURCE/'README.md').open('a') as f:
            f.write('''

## Rain - item 3

| Key | SVG viewBox | PNG pixels | Wrap |
| --- | --- | --- | --- |
| v3-fx-rain | 256x256 | **512x512** | Repeat U/V |
| v3-fx-rain-splash | 256x32 | **512x64** | Clamp |

These requested512px dimensions are the final textures. Both are2x exports:
the splash's eight logical32x32 cells become64x64 PNG frames. No extra scaling
or duplicate texture is needed. Both have zero slice borders; use Simple/UVs.

Rain:42 soft pale ice/steel streaks per tile, falling **15 degrees from vertical,
down-left**. Main stroke authored alpha is0.22-0.31; two are0.40, with much
fainter soft shoulders. Fully transparent between streaks; no fog/mist/wash.
Use normal straight-alpha blending, **white tint alpha1**; alpha is baked into
each streak. Intended repeat size **256x256 logical/display pixels** at1440x900,
equivalent to512x512 source-capture pixels. Proof uses exactly3x2 unscaled PNG
tiles over the1536x1024 source crop, displayed at768x512 for the service-scale
comparison. Keep tile aspect square; repeat UVs instead of stretching one tile
over the room. Suggested scroll direction UV(-0.067,+0.25) tiles/second in
top-left coordinates; for bottom-left UV flip the V sign. Speed is runtime-owned.

Draw rain above the room but below service pins, labels, dialogs and the crew
rail; mask it to the room/deck viewport. Disable raycast/input on rain and
splashes. The conservative proof also puts rain over the sample critic/order
pins, so their legibility is visible even with that layering. Do not atlas the
tile or sample only a subrect when repeating. Repeat importer is supplied.

Splash: eight64x64 source-pixel frames, left-to-right. Exact source rects:
`(0,0,64,64)`, `(64,0,64,64)`, `(128,0,64,64)`, `(192,0,64,64)`,
`(256,0,64,64)`, `(320,0,64,64)`, `(384,0,64,64)`, `(448,0,64,64)`.
Per-frame contact centre **PNG(32,42)**, logical(16,21), normalized(0.5,0.65625)
top-left; bottom-left normalized(0.5,0.34375). Keep contact anchored to the
puddle as the elliptical ring expands. Display32x32 logical pixels per frame,
or uniformly smaller for depth; retain the transparent cell padding. Atlas UV
width1/8, full height; inset each UV sample by half a source texel when using
bilinear UV quads to prevent frame bleed. The supplied importer is Sprite/Single
for the entire strip; runtime owns frame UV selection, no auto-slicing expected.

Suggested **0.04s/frame,0.32s one-shot**; frame8 is fully transparent. Spawn
sparingly on visible deck/puddle positions with staggered times and small scale
variation; do not synchronize the strip across the floor or loop one fixed ring.
The eight-frame proof includes actual strip pixels and separate enlarged frames.

`review/03-rain-tiled-3x2.png` is the exact512px3x2 overlay; `03-rain-and-splashes.png`
compares dry/rainy at actual service scale and shows the strip/deck samples;
`03-rain-tile-blank.png` shows the raw tile over cream/night; `03-splash-frames.png`
shows every frame. `review/contact-sheet.png` is byte-identical to
`docs/screens/ui-v3/art-kit-6.png`, joining all three items without downscaling
the40/32px evidence. Final manually opened images are hashed in visual-review.json.
''')


def audit(assets, manifest):
    for a in assets:
        m = manifest[a['name']]
        source = ROOT/m['svg']
        assert DEFS in source.read_text()
        assert not ET.parse(source).findall('.//{http://www.w3.org/2000/svg}text')
        im = Image.open(ROOT/m['png'])
        assert im.mode == 'RGBA' and list(im.size) == m['size']
        assert im.getchannel('A').getextrema()[0] == 0
        meta = (ROOT/m['png']).with_suffix('.png.meta').read_text()
        for setting in ('spriteMode: 1', 'spriteMeshType: 1', 'textureType: 2',
                        'enableMipMap: 0', 'alphaIsTransparency: 1', 'nPOTScale: 0',
                        'filterMode: 1', 'spriteBorder: {x: 0, y: 0, z: 0, w: 0}'):
            assert setting in meta, (a['name'], setting)
        assert f'wrapU: {0 if a["repeat"] else 1}' in meta
        if a['name'].startswith('chip-') and a['name'] != 'chip-new':
            assert im.getpixel((96, 94))[3] == 255
            # Centre has no illustration/glyph: exactly the paper gradient, uniform across each row.
            assert im.getpixel((68, 94)) == im.getpixel((96, 94)) == im.getpixel((124, 94))
    preserved = {p: sha(ROOT/p) == h for p, h in json.loads((SOURCE/'preservation.json').read_text()).items()}
    assert all(preserved.values()), preserved
    report = dict(assets=len(assets), rgba_2x=True, exact_kit2_defs=True,
                no_baked_svg_text=True, simple_zero_slices=True, importers=True,
                blank_chip_centres=True, preserved_files=len(preserved),
                visual_review='Manual image opening required, never granted by this audit.')
    if any(a['name'] == 'fx-rain' for a in assets):
        from io import BytesIO
        # Render one continuous3x2 vector field, with no internal clipping at tile boundaries.
        # Compare to six copies of the independently rasterized tile, including every seam.
        svg = '<svg xmlns="http://www.w3.org/2000/svg" width="768" height="512" viewBox="0 0 768 512">' + DEFS + rain_geometry(3, 2) + '</svg>'
        continuous = Image.open(BytesIO(cairosvg.svg2png(bytestring=svg.encode(), output_width=1536, output_height=1024))).convert('RGBA')
        diff = ImageChops.difference(continuous, tiled_rain())
        # Transparent RGB can differ at antialiased edges; compare alpha and premultiplied RGB.
        a1, a2 = continuous.getchannel('A'), tiled_rain().getchannel('A')
        alpha_error = ImageChops.difference(a1, a2).getextrema()[1]
        premul_errors = [ImageChops.difference(ImageChops.multiply(continuous.getchannel(c), a1),
                                             ImageChops.multiply(tiled_rain().getchannel(c), a2)).getextrema()[1] for c in 'RGB']
        assert alpha_error <= 1 and max(premul_errors) <= 1, (alpha_error, premul_errors)
        tile = load('fx-rain')
        hist = tile.getchannel('A').histogram()
        assert tile.size == (512, 512)
        assert hist[0]/(512*512) > .94
        strip = load('fx-rain-splash')
        assert strip.size == (512, 64)
        assert strip.crop((448, 0, 512, 64)).getchannel('A').getbbox() is None
        for i in range(7):
            bounds = strip.crop((i*64, 0, (i+1)*64, 64)).getchannel('A').getbbox()
            assert bounds and bounds[0] > 0 and bounds[1] > 0 and bounds[2] < 64 and bounds[3] < 64
        report.update(rain_continuous_vector_vs_six_raster_tiles_max_alpha_error=alpha_error,
                      rain_premultiplied_rgb_max_errors=premul_errors,
                      rain_transparent_fraction=round(hist[0]/(512*512), 5),
                      rain_max_alpha=tile.getchannel('A').getextrema()[1],
                      splash_8_frames=True, splash_last_frame_clear=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', type=int, choices=(1, 2, 3), default=3)
    args = parser.parse_args()
    SOURCE.mkdir(exist_ok=True)
    REVIEW.mkdir(exist_ok=True)
    baseline = SOURCE/'preservation.json'
    if not baseline.exists():
        protected = [SOURCE.parent/f'build_kit{k}.py' for k in (2, 4, 5)]
        for kit in (2, 4, 5):
            protected += [SOURCE.parent/f'kit-{kit}/README.md']
            protected += sorted((SOURCE.parent/f'kit-{kit}').glob('*.svg'))
            protected += [ROOT/f'docs/screens/ui-v3/art-kit-{kit}.png']
        protected += sorted(OUT.glob('v3-ncard-*'))
        protected += [p for p in OUT.glob('v3-svc-*') if not p.name.startswith('v3-svc-critic')]
        protected += [OUT/'v3-card.png.meta']
        baseline.write_text(json.dumps({str(p.relative_to(ROOT)): sha(p) for p in protected}, indent=2)+'\n')
    assets = assets_for(args.stage)
    manifest = {a['name']: export(a) for a in assets}
    (SOURCE/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    evidence = chip_reviews()
    if args.stage >= 2:
        evidence.update(critic_reviews())
    if args.stage >= 3:
        evidence.update(rain_reviews())
        contact()
    write_readme(args.stage)
    (SOURCE/'review-evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    report = audit(assets, manifest)
    (SOURCE/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
