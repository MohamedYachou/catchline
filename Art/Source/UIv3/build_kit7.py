"""SERVICE-UI-KIT-7. SVG geometry -> CairoSVG 2x -> Unity sprites.

WSL: /home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit7.py --stage 1..3
Cumulative stages follow brief priority. Incumbent builders are parsed, never run.
All text and sample event contents are restricted to review images.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import json
import math
import re
import uuid
import xml.etree.ElementTree as ET
import cairosvg
from PIL import Image, ImageChops, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent / 'kit-7'
OUT = ROOT / 'Assets/Art/UI'
REVIEW = SOURCE / 'review'
CAPTURE = REVIEW / 'source-service-late-1440.png'
CARDS = ROOT/'docs/screens/ui-v2/day-nightcards-1440.png'
NAVY, TEAL, CORAL = '#173f57', '#168f9f', '#df7257'
CREAM, NIGHT, IVORY = '#f4efe3', '#182f3a', '#fffaf0'
PAPER, BRASS = 'url(#paper)', 'url(#brass)'
RESAMPLE = Image.Resampling.LANCZOS
tree = ast.parse((SOURCE.parent / 'build_kit2.py').read_text())
DEFS = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'DEFS' for t in n.targets))


def attrs(values):
    return ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in values.items())


def path(d, fill=NAVY, stroke='none', width=3, **kw):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {attrs(kw)}/>'


def rect(x, y, w, h, r, fill, stroke='none', width=3, **kw):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {attrs(kw)}/>'


def circle(x, y, r, fill, stroke='none', width=3, **kw):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {attrs(kw)}/>'


def back_and_shine():
    # Exact kit5 outer planes, including its 4-unit downcast shadow.
    body = (rect(12, 12, 216, 304, 16, NAVY, opacity='.18')
            + rect(12, 8, 216, 304, 16, NAVY, '#a68755', 2)
            + rect(16, 12, 208, 296, 13, 'none', '#fffdf5', 2)
            + rect(23, 19, 194, 282, 10, 'none', '#d6ad65', 1.5))
    for y in range(36, 298, 15):
        body += path(f'M29 {y} Q40 {y-5} 51 {y} T95 {y} T139 {y} T183 {y} T211 {y}',
                     'none', '#416c80', 1.1, opacity='.45')
    body += circle(120, 160, 64, NAVY, '#d6ad65', 1.8)
    body += circle(120, 160, 58, 'none', '#416c80', 1.4)
    # Alternating broad brass/ivory compass points, no directional letters.
    for i in range(8):
        angle = math.pi*i/4-math.pi/2
        r = 51 if i % 2 == 0 else 35
        tip = (120+math.cos(angle)*r, 160+math.sin(angle)*r)
        left = (120+math.cos(angle-.50)*12, 160+math.sin(angle-.50)*12)
        right = (120+math.cos(angle+.50)*12, 160+math.sin(angle+.50)*12)
        body += path(f'M120 160 L{left[0]:.3f} {left[1]:.3f} L{tip[0]:.3f} {tip[1]:.3f}Z',
                     BRASS if i % 2 == 0 else '#936a32', NAVY, .6)
        body += path(f'M120 160 L{tip[0]:.3f} {tip[1]:.3f} L{right[0]:.3f} {right[1]:.3f}Z',
                     '#fff0bd' if i % 2 == 0 else '#d6ad65', NAVY, .6)
    body += circle(120, 160, 10, BRASS, NAVY, 2) + circle(120, 160, 3, IVORY)
    for y in (39, 281):
        body += path(f'M98 {y} H111 M129 {y} H142', 'none', '#d6ad65', 1.6)
        body += path(f'M120 {y-5} L124 {y} 120 {y+5} 116 {y}Z', BRASS)
    shine = ('<defs><linearGradient id="sweep" x1="0" x2="1">'
             '<stop stop-color="#fffaf0" stop-opacity="0"/>'
             '<stop offset=".32" stop-color="#fffaf0" stop-opacity=".05"/>'
             '<stop offset=".50" stop-color="#fffaf0" stop-opacity=".34"/>'
             '<stop offset=".60" stop-color="#fffaf0" stop-opacity=".16"/>'
             '<stop offset="1" stop-color="#fffaf0" stop-opacity="0"/>'
             '</linearGradient><clipPath id="card-clip">'
             '<rect x="12" y="8" width="216" height="304" rx="16"/>'
             '</clipPath></defs><g clip-path="url(#card-clip)">'
             + rect(66, -110, 108, 540, 0, 'url(#sweep)', transform='rotate(24 120 160)') + '</g>')
    return [dict(name='ncard-back', body=body, size=(240, 320), stage=1,
                 safe={'flip_pivot': [120, 160]}, note='Exact kit5 outer geometry, neutral navy compass back.'),
            dict(name='ncard-shine', body=shine, size=(240, 320), stage=1,
                 safe={'face_clip': [12, 8, 216, 304]}, note='Soft alpha sweep. Clip translated layer to face silhouette; no input.')]


BANNER_SAFE = dict(window_circle=[114, 100, 69], illustration=[52, 38, 124, 124],
                   title=[227, 55, 354, 40], line=[227, 104, 354, 30])


def banner_assets():
    body = (path('M5 46 H69 V166 H5 L29 106Z M571 46 H635 L611 106 635 166 H571Z', CORAL, NAVY, 3)
            + path('M40 160 L67 182 V154 M600 160 L573 182 V154', '#936a32', NAVY, 2)
            + rect(31, 30, 578, 148, 18, NAVY, opacity='.18')
            + rect(31, 24, 578, 148, 18, CORAL, NAVY, 3)
            + path('M49 31 H591', 'none', '#fff0bd', 2, opacity='.65')
            + path('M210 165 H591', 'none', '#936a32', 2, opacity='.5')
            + rect(209, 45, 389, 107, 11, PAPER, '#936a32', 1.5)
            + rect(213, 49, 381, 99, 8, 'none', IVORY, 1.5)
            + circle(114, 104, 80, NAVY, opacity='.18')
            + circle(114, 100, 80, BRASS, NAVY, 3)
            + circle(114, 100, 74, CORAL, NAVY, 1.5)
            + circle(114, 100, 69, PAPER, NAVY, 2)
            + path('M56 77 A63 63 0 0 1 132 40', 'none', '#fffdf5', 2))
    return [dict(name='event-banner', body=body, size=(640, 200), stage=2,
                 safe=BANNER_SAFE, note='Fixed aspect coral ribbon; separate whole kit5 illustration and live navy title/one line.')]


def assets_for(stage):
    assets = back_and_shine()
    if stage >= 2:
        assets += banner_assets()
    if stage >= 3:
        assets += timeline_assets()
    return assets


def timeline_assets():
    # Ivory silhouette and brass perimeter remain readable against the blue bar.
    shell = (path('M14 42 A21 21 0 1 1 34 42 L24 53Z', PAPER, '#d6ad65', 2.5)
             + circle(24, 23, 17, IVORY, NAVY, 1.5)
             + path('M9 15 A17 17 0 0 1 29 7', 'none', '#fffdf5', 1.5))
    ferry = (rect(14, 16, 20, 11, 2, IVORY, NAVY, 2)
             + rect(18, 12, 11, 5, 1, CORAL, NAVY, 1.8)
             + path('M9 27 H39 L34 34 H15Z', NAVY)
             + path('M13 28 H35', 'none', CORAL, 2)
             + path('M19 20 V23 M25 20 V23 M31 20 V23', 'none', TEAL, 2.7)
             + path('M11 37 Q15 34 19 37 T27 37 T35 37', 'none', TEAL, 2))
    critic = (path('M10 22 C7 15 16 10 24 10 C29 6 37 10 38 17 Q39 21 34 23Z', NAVY)
              + path('M15 22 Q25 24 34 21', 'none', CORAL, 2.7)
              + path('M24 10 Q25 7 29 7', 'none', NAVY, 2.5)
              + circle(17, 30, 5, 'none', NAVY, 2.5)
              + circle(31, 30, 5, 'none', NAVY, 2.5)
              + path('M22 29 Q24 27 26 29 M11 28 L9 26 M37 28 L39 26', 'none', NAVY, 2))
    glow = ('<defs><radialGradient id="arrival-halo">'
            '<stop stop-color="#ffe5a0" stop-opacity=".40"/>'
            '<stop offset=".42" stop-color="#edbc62" stop-opacity=".30"/>'
            '<stop offset=".70" stop-color="#edbc62" stop-opacity=".13"/>'
            '<stop offset="1" stop-color="#edbc62" stop-opacity="0"/>'
            '</radialGradient></defs>' + circle(40, 39, 38, 'url(#arrival-halo)'))
    safe = dict(tip=[24, 53], body_centre=[24, 23], glyph=[8, 7, 32, 32])
    return [dict(name='tl-ferry', body=shell+ferry, size=(48, 56), stage=3,
                 safe=safe, note='Ferry hull, coral cabin and teal windows/water; align tip to due-time curve.'),
            dict(name='tl-critic', body=shell+critic, size=(48, 56), stage=3,
                 safe=safe, note='Beret and spectacles, simplified for22-26px width; align tip to due-time curve.'),
            dict(name='tl-glow', body=glow, size=(80, 88), stage=3,
                 safe=dict(pin_rect=[16, 16, 48, 56], body_centre=[40, 39], tip=[40, 69]),
                 note='Normal alpha soft gold halo.16 logical units of alignment padding around pin rect; no input.')]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def export(a):
    w, h = a['size']
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{DEFS}{a["body"]}</svg>'
    source = SOURCE / f'{a["name"]}.svg'
    source.write_text(svg)
    target = OUT / f'v3-{a["name"]}.png'
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(target), output_width=w*2, output_height=h*2)
    meta = target.with_suffix('.png.meta')
    template = meta.read_text() if meta.exists() else (OUT/'v3-card.png.meta').read_text()
    if not meta.exists():
        template = re.sub(r'guid: [a-f0-9]+', f'guid: {uuid.uuid4().hex}', template, count=1)
    template = template.replace('spriteMode: 0', 'spriteMode: 1')
    template = re.sub(r'spriteBorder: \{[^}]+\}', 'spriteBorder: {x: 0, y: 0, z: 0, w: 0}', template)
    meta.write_text(template)
    return dict(png=str(target.relative_to(ROOT)), svg=str(source.relative_to(ROOT)),
                viewBox=[0, 0, w, h], size=[w*2, h*2], slice_pixels=[0, 0, 0, 0],
                safe_rects_svg_units=a['safe'], note=a['note'], stage=a['stage'],
                sha256=sha(target), guid=re.search(r'^guid: (\w+)', template, re.M)[1])


def font(size):
    return ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts/Fredoka-SemiBold.ttf'), size)


def load(name):
    return Image.open(OUT/f'v3-{name}.png').convert('RGBA')


def text(draw, xy, value, size=20, fill=NAVY, **kw):
    draw.text(xy, value, font=font(size), fill=fill, **kw)


def face():
    im = load('ncard-night')
    im.alpha_composite(load('ncard-ferry').resize((204, 204), RESAMPLE), (138, 214))
    d = ImageDraw.Draw(im)
    text(d, (253, 88), 'TOMORROW', 26, IVORY, anchor='mm', stroke_width=2, stroke_fill=NAVY)
    text(d, (240, 163), 'Ferry night', 35, IVORY, anchor='mm')
    for i, line in enumerate(['A busier evening.', 'More guests arrive', 'from the harbour.']):
        text(d, (240, 451+i*35), line, 32, anchor='mm')
    return im


def reveal_reviews():
    back, front, shine = load('ncard-back'), face(), load('ncard-shine')
    lit = front.copy()
    lit.alpha_composite(shine)
    canvas = Image.new('RGBA', (1200, 694), CREAM)
    d = ImageDraw.Draw(canvas)
    text(d, (26, 20), 'The night-card deal / kit 7', 29)
    text(d, (26, 59), 'Actual 150 x 200 px cards. Five scaleX frames; sample live labels on the face.', 17)
    for row, bg in enumerate((CREAM, NIGHT)):
        y = 105 + row*286
        d.rectangle((0, y-10, 1200, y+265), fill=bg)
        ink = NAVY if row == 0 else IVORY
        frames = [(back, 1, 'back / 1'), (back, .5, 'back / .5'), (back, .1, 'back / .1'),
                  (front, .5, 'face / .5'), (front, 1, 'face / 1'), (lit, 1, 'face + shine')]
        for i, (im, scale, label) in enumerate(frames):
            center = 100+i*200
            # Resize at full card width before the horizontal scale only.
            scaled = im.resize((150, 200), RESAMPLE).resize((round(150*scale), 200), RESAMPLE)
            canvas.alpha_composite(scaled, (center-scaled.width//2, y+8))
            text(d, (center, y+231), label, 18, ink, anchor='mm')
    canvas.convert('RGB').save(REVIEW/'01-reveal-150px.png')
    raw = Image.new('RGBA', (1000, 430), CREAM)
    d = ImageDraw.Draw(raw)
    text(d, (24, 16), 'Shipping back and transparent sweep / 240 x 320 logical', 24)
    for i, (im, bg, label) in enumerate([(back, CREAM, 'Navy + brass'), (shine, NAVY, 'Sweep on navy'), (shine, CORAL, 'Sweep on coral')]):
        x = 24+i*326
        d.rounded_rectangle((x, 62, x+300, 392), 14, fill=bg)
        raw.alpha_composite(im.resize((240, 320), RESAMPLE), (x+30, 66))
        text(d, (x+150, 410), label, 17, anchor='mm')
    raw.convert('RGB').save(REVIEW/'01-back-and-shine.png')
    return dict(card_display=[150, 200], scaleX=[1, .5, .1, .5, 1],
                flip_pivot='centre of full240x320 rect', lettering='Review only, existing Fredoka',
                shine_preview='One centred light sweep at authored opacity')


def banner_composite(art, title, line, show_safe=False):
    im = load('event-banner')
    im.alpha_composite(load('ncard-'+art).resize((248, 248), RESAMPLE), (104, 76))
    d = ImageDraw.Draw(im)
    for key, value, size in [('title', title, 60), ('line', line, 38)]:
        x, y, w, h = BANNER_SAFE[key]
        assert d.textbbox((0, 0), value, font=font(size))[2] <= w*2, (key, value)
        text(d, (x*2, (y+h/2)*2), value, size, anchor='lm')
    if show_safe:
        for key in ('illustration', 'title', 'line'):
            x, y, w, h = BANNER_SAFE[key]
            d.rectangle((x*2, y*2, (x+w)*2, (y+h)*2), outline=TEAL, width=2)
    return im


def banner_reviews():
    capture = Image.open(CAPTURE).convert('RGBA')
    # Source capture2880x1800; every pair of source pixels becomes one display pixel.
    desktop_box, phone_box = (600, 340, 2120, 1140), (1120, 340, 2080, 1140)
    desktop = capture.crop(desktop_box).resize((760, 400), RESAMPLE)
    phone = capture.crop(phone_box).resize((480, 400), RESAMPLE)
    canvas = Image.new('RGBA', (1280, 565), CREAM)
    d = ImageDraw.Draw(canvas)
    text(d, (20, 17), 'The doors open / a night event', 28)
    text(d, (20, 56), 'Same blank coral ribbon. Kit 5 illustration and Fredoka copy are separate live layers.', 17)
    text(d, (20, 98), 'Desktop / banner 640 px', 20)
    text(d, (800, 98), 'Phone / banner 420 px', 20)
    canvas.alpha_composite(desktop, (20, 137))
    canvas.alpha_composite(phone, (800, 137))
    canvas.alpha_composite(banner_composite('ferry', 'Ferry night', 'More guests from the harbour.').resize((640, 200), RESAMPLE), (80, 174))
    canvas.alpha_composite(banner_composite('critic', 'A critic is coming', 'Make every plate count.').resize((420, 131), RESAMPLE), (830, 174))
    canvas.convert('RGB').save(REVIEW/'02-banner-service-420-640.png')
    sheet = Image.new('RGBA', (1280, 470), NIGHT)
    d = ImageDraw.Draw(sheet)
    text(d, (24, 18), 'One ribbon / four event illustrations / 420 px each', 27, IVORY)
    samples = [('ferry', 'Ferry night', 'More guests from the harbour.'),
               ('critic', 'A critic is coming', 'Make every plate count.'),
               ('festival', 'Festival night', 'A bright evening at the harbour.'),
               ('rain', 'Rain tonight', 'A warm welcome out of the rain.')]
    for i, (art, title, line) in enumerate(samples):
        x, y = 36+(i%2)*640, 85+(i//2)*180
        sheet.alpha_composite(banner_composite(art, title, line).resize((420, 131), RESAMPLE), (x, y))
    sheet.convert('RGB').save(REVIEW/'02-banner-four-events.png')
    safe = Image.new('RGBA', (1280, 470), CREAM)
    safe.alpha_composite(banner_composite('ferry', 'Ferry night', 'More guests from the harbour.', True), (0, 0))
    d = ImageDraw.Draw(safe)
    text(d, (24, 427), 'Safe rectangles at source 2x / teal = illustration, title, one-line body. Labels are review only.', 20)
    safe.convert('RGB').save(REVIEW/'02-banner-safe-rects.png')
    return dict(capture=str(CAPTURE.relative_to(ROOT)), capture_sha256=sha(CAPTURE),
                original_fallback='docs/screens/ui-v2/day-service-late-1440.png',
                requested_simulator_logs='disappeared during active capture pass; see comms QUESTION',
                capture_pixels=list(capture.size),
                desktop_source_crop=list(desktop_box), desktop_display=[760, 400],
                phone_source_crop=list(phone_box), phone_display=[480, 400],
                banner_widths=[640, 420], crop_tint='none', sample_copy='review only',
                illustration='Whole kit5 texture fitted inside124x124 square, centred in window with7-unit inset')


def timeline_reviews():
    capture = Image.open(CAPTURE).convert('RGBA')
    box = (900, 0, 1560, 160)
    bar = capture.crop(box).resize((330, 80), RESAMPLE)
    # Tips on the two future segments, leaving current21:00 flag unobstructed.
    tips = [(240, 33), (280, 37)]

    def marked(width=24, halo=True):
        im = bar.copy()
        scale = width/48
        for i, (name, (tx, ty)) in enumerate(zip(('tl-ferry', 'tl-critic'), tips)):
            x, y = round(tx-24*scale), round(ty-53*scale)
            if halo and i == 0:
                im.alpha_composite(load('tl-glow').resize((round(80*scale), round(88*scale)), RESAMPLE),
                                   (x-round(16*scale), y-round(16*scale)))
            im.alpha_composite(load(name).resize((width, round(56*scale)), RESAMPLE), (x, y))
        return im

    sheet = Image.new('RGBA', (1280, 462), CREAM)
    d = ImageDraw.Draw(sheet)
    text(d, (24, 18), 'Coming on the evening curve', 29)
    text(d, (24, 58), 'Actual-size pins on untouched native top-bar pixels. Ferry halo = arrival soon.', 18)
    for i, (title, im) in enumerate([('Original / no overlay', bar), ('24 px / ferry halo', marked()),
                                     ('24 px / no halo', marked(halo=False))]):
        x = 24+i*424
        text(d, (x, 110), title, 21)
        sheet.alpha_composite(im, (x, 151))
    for i, width in enumerate((22, 24, 26)):
        x = 24+i*424
        text(d, (x, 278), f'{width} px width / both events', 21)
        sheet.alpha_composite(marked(width), (x, 319))
    text(d, (24, 427), 'Tips are sample due-time positions. Runtime owns schedule, curve mapping and collision spacing.', 18)
    sheet.convert('RGB').save(REVIEW/'03-timeline-native-24px.png')
    raw = Image.new('RGBA', (1000, 320), NIGHT)
    d = ImageDraw.Draw(raw)
    text(d, (24, 18), 'Shipping timeline art / source pixels (2x)', 26, IVORY)
    raw.alpha_composite(load('tl-ferry'), (92, 96))
    raw.alpha_composite(load('tl-critic'), (350, 96))
    raw.alpha_composite(load('tl-glow'), (642, 64))
    text(d, (140, 253), 'Ferry / 96 x 112', 18, IVORY, anchor='mm')
    text(d, (398, 253), 'Critic / 96 x 112', 18, IVORY, anchor='mm')
    text(d, (722, 253), 'Gold halo / 160 x 176', 18, IVORY, anchor='mm')
    raw.convert('RGB').save(REVIEW/'03-timeline-source.png')
    return dict(capture=str(CAPTURE.relative_to(ROOT)), capture_sha256=sha(CAPTURE),
                source_crop=list(box), display_crop=[330, 80], crop_tint='none',
                pin_widths=[22, 24, 26], required_width=24,
                tip_positions_in_display_crop=tips, halo='Behind ferry, normal alpha, authored opacity',
                source_to_display=0.5, future_schedule='Illustrative positions only; no gameplay timing inferred')


def contact():
    proofs = [Image.open(REVIEW/name).convert('RGB') for name in
              ('01-reveal-150px.png', '02-banner-service-420-640.png', '03-timeline-native-24px.png')]
    sheet = Image.new('RGB', (1280, sum(im.height for im in proofs)+32), CREAM)
    y = 0
    for im in proofs:
        sheet.paste(im, ((1280-im.width)//2, y))
        y += im.height+16
    sheet.save(REVIEW/'art-kit-7.png')
    sheet.save(ROOT/'docs/screens/ui-v3/art-kit-7.png')


def preservation():
    baseline = SOURCE/'preservation.json'
    if not baseline.exists():
        protected = []
        for k in (2, 4, 5, 6):
            protected += [SOURCE.parent/f'build_kit{k}.py', SOURCE.parent/f'kit-{k}/README.md',
                          ROOT/f'docs/screens/ui-v3/art-kit-{k}.png']
            protected += list((SOURCE.parent/f'kit-{k}').glob('*.svg'))
        protected += [p for p in OUT.glob('v3-*') if not p.name.startswith(('v3-ncard-back', 'v3-ncard-shine', 'v3-event-', 'v3-tl-'))]
        protected += [CAPTURE, CARDS]
        baseline.write_text(json.dumps({str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p)
                                       for p in protected if p.exists()}, indent=2)+'\n')
    verified = {p: sha(ROOT/p) == h for p, h in json.loads(baseline.read_text()).items()}
    assert all(verified.values()), [p for p, ok in verified.items() if not ok]
    return len(verified)


def audit(assets, manifest):
    for a in assets:
        m = manifest[a['name']]
        svg = (ROOT/m['svg']).read_text()
        assert DEFS in svg
        tree = ET.fromstring(svg)
        assert not any(e.tag.rsplit('}', 1)[-1] in ('text', 'image', 'foreignObject') for e in tree.iter())
        im = Image.open(ROOT/m['png'])
        assert im.mode == 'RGBA' and list(im.size) == m['size']
        assert im.getchannel('A').getextrema()[0] == 0
        meta = (ROOT/m['png']).with_suffix('.png.meta').read_text()
        for setting in ('spriteMode: 1', 'spriteMeshType: 1', 'textureType: 2', 'enableMipMap: 0',
                        'alphaIsTransparency: 1', 'nPOTScale: 0', 'filterMode: 1', 'wrapU: 1', 'wrapV: 1',
                        'spriteBorder: {x: 0, y: 0, z: 0, w: 0}'):
            assert setting in meta, (a['name'], setting)
    assert ImageChops.difference(load('ncard-back').getchannel('A'), load('ncard-night').getchannel('A')).getbbox() is None
    assert load('ncard-shine').getchannel('A').getextrema()[1] <= 87
    return dict(assets=len(assets), exact_kit2_defs=True, rgba_2x=True, no_svg_text_or_raster=True,
                simple_zero_slices=True, importers=True, back_alpha_exactly_matches_kit5=True,
                preserved_files=preservation(), visual_review='Must personally open images, never granted by generator.')


def write_readme(stage):
    (SOURCE/'README.md').write_text('''# Service kit 7 - the deal, night announcement, timeline

SERVICE-UI-KIT-7 / Codex 1 (Windows app) / 2026-10-28.
Editable SVG geometry, exact kit2 DEFS and accepted kit5/6 palette.
CairoSVG exports at2x; shipping assets have no words or numerals.
Review labels and sample content simulate separate live UI layers only.

## Item 1 - card deal

| Sprite in Assets/Art/UI | SVG viewBox | PNG pixels |
| --- | --- | --- |
| v3-ncard-back |240x320|480x640|
| v3-ncard-shine |240x320|480x640|

Back matches kit5 frame alpha exactly, including its outer brass outline,
ivory inset and4-unit downcast shadow. Neutral navy wave field with a brass
eight-point compass; no card-kind information appears before the flip.
All coordinates below are top-left SVG units. Double them for PNG pixels.
Flip about the **full rect centre(120,160)**. Keep back and face on the same
240x320 rect; horizontal scale only, preserve height and position. Swap sides
while edge-on; use abs(scaleX) on each side so text never becomes mirrored.
Proof sequence is back1,.5,.1 then face.5,1 at actual150x200px.

Suggested runtime choreography (not implemented here): stagger landings by
70-100ms, short settle, then flip each card over about240-300ms. Keep input
ready once faces are readable; reduced motion can reveal without a flip.
Shine uses normal alpha, white tint at1, max alpha<=.34. Draw above card art
and below live text. Slide its rect from -240 to+240 logical units relative
to the card, once in about400ms; keep its240x320 size and clip the moving layer
to the **face rounded rect(12,8,216,304), radius16**. Sprite edges alone do not
clip a translated sweep. At150px card width these offsets become -150/+150px.
Disable input/raycast on the sweep; no additive blend, loop or opaque wash.

## Import contract

Every sprite: Image Type Simple, preserve aspect, zero slice borders L/B/R/T.
Sprite/Single, Full Rect, centre pivot,100PPU, sRGB, straight alpha with alpha
transparency, bilinear, Clamp, no mipmaps or NPOT rescale, default uncompressed.
Regeneration preserves GUIDs. No Resources copies. Runtime wiring and native
gameplay/touch acceptance remain Claude's scope; static proofs do not prove them.

## Regeneration and evidence

```sh
/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit7.py --stage '''+str(stage)+'''
```

Requires existing CairoSVG/Pillow environment and Fredoka SemiBold.
Stages are cumulative in brief order; older builders are read, never imported.
`manifest.json`: dimensions, GUIDs, safe rects and hashes. `audit.json` checks
source/export/import/preservation; `visual-review.json` separately records
personally opened images. Regeneration cannot itself approve an image.
Item1 proofs: `review/01-reveal-150px.png`, `01-back-and-shine.png`.
No C#, Resources, other-kit, Crew or Codex2 art writes; no Git/Unity invocation.
''')
    if stage >= 2:
        with (SOURCE/'README.md').open('a') as f:
            f.write('''

## Item 2 - night-start event ribbon

`v3-event-banner`:640x200 SVG,1280x400 PNG. Fixed3.2:1 aspect, no nine-slice.
Draw640x200 desktop or420x131.25 phone (uniform scale0.65625).
The left window is blank cream. Fit the **whole** kit5 ferry/critic/festival/rain
texture in its illustration slot; preserve its internal transparent padding.

| Region | Top-left SVG x,y,width,height | PNG pixels |
| --- | --- | --- |
| Illustration |52,38,124,124|104,76,248,248|
| Title |227,55,354,40|454,110,708,80|
| One line |227,104,354,30|454,208,708,60|

Window circle centre(114,100), radius69; source PNG centre(228,200),radius138.
The124x124 illustration square has7 units of inset from the circle bounding
square. Kit5's internal padding keeps all four illustrations inside the circle.
Clip any different/new art to the window circle.
Title: navy Fredoka SemiBold30 logical units; line: navy19. At420px banner
width they become19.69/12.47px. Left-align to227 and vertically centre in
the safe rectangles. These are live text layers; fit localized copy to width354.
Use one line for the subtitle; shorten or reduce type to a readable bound.
For Unity bottom-left, yBottom=200-yTop-height. At phone scale multiply all
positions/sizes by420/640. Safe rects include the full text ink, not just baseline.

Suggested reveal: settle the banner below the top bar as doors open, then
release it after the announcement. Runtime owns event timing and dismissal.
Keep it clear of the top-bar controls and staff rail, above the room. The
review's room location is an art-compositing proof, not final gameplay placement.
`02-banner-service-420-640.png` shows both display widths over unmodified crops
of the supplied2880x1800 service image at2source pixels per display pixel.
`review-evidence.json` records crop bounds. `02-banner-four-events.png` shows
all four kit5 illustrations; `02-banner-safe-rects.png` shows live layout.
The requested simulator Logs files vanished during a new capture pass.
Evidence follows saved `docs/screens/ui-v2/day-service-late-1440.png`, frozen
as `review/source-service-late-1440.png` (2880x1800). It has the same inspected
room/top-bar composition; no byte-equivalence to the vanished file is claimed.
Actual source hash and fallback provenance are recorded in review-evidence.json.
''')
    if stage >= 3:
        with (SOURCE/'README.md').open('a') as f:
            f.write('''

## Item 3 - upcoming events on the evening curve

| Sprite | SVG viewBox | PNG pixels | Display width |
| --- | --- | --- | --- |
| v3-tl-ferry |48x56|96x112|22-26px, preferred24px|
| v3-tl-critic |48x56|96x112|22-26px, preferred24px|
| v3-tl-glow |80x88|160x176|40px when pin width24px|

Ivory pointed brass-rim discs: ferry hull/cabin/windows versus critic beret and
spectacles. Keep aspect48:56. A24px-wide pin is24x28 display pixels.
Pin tip **(24,53)**, normalized top-left(0.5,0.9464285714); Unity bottom-left
normalized pivot equivalent(0.5,0.0535714286). Importer remains centre pivot;
set the UI anchor/offset explicitly. Tip at24px display width is(12,26.5).
Place this tip at the event's due-time point on the existing evening curve.
Do not confuse the pin's bottom edge with its tip:3 logical units of padding.
If the full-rect centre is used, offset centre from desired tip by(0,-25)
SVG units, or(0,-12.5) screen pixels at24px width (top-left y positive down).

Halo uses normal alpha, authored max0.40. Match its logical scale to the pin;
its pin rect is(16,16,48,56), so halo top-left=pin top-left-(16,16) logical
units, or-(8,8) pixels at24px pin width. Body centre(40,39) aligns to pin's
(24,23); halo tip reference(40,69) aligns to pin tip. Draw behind the pin,
above the top-bar background, disable raycast/input. Last10 seconds before
arrival: show halo; a restrained opacity pulse is optional. Remove the halo
when the event arrives. Runtime owns the countdown and removal of the pin.
Reduced motion: steady halo. These small markers announce future events;
the larger kit6 critic pin continues to identify the seated critic.

Keep current-time flag, hour labels and controls clear. Multiple nearby events
need runtime spacing/collision handling while preserving due-time tip anchors;
show distinct markers or a deliberate stack, never silently hide an event.
Proof positions are illustrative, not a new schedule or a runtime layout change.
Actual source crop(900,0,1560,160) downsamples2:1 to330x80. Both24px pins are
shown on that real bar with/without halo, plus22/26px checks. Sample due tips
in this crop are(240,33),(280,37); existing21:00 flag remains unobstructed.
No bar repainting, tint or artificial widening. `03-timeline-source.png` shows
the exact exported textures. Final contact `review/art-kit-7.png` is mirrored
at `docs/screens/ui-v3/art-kit-7.png`; proof sections retain their actual sizes.

Independent check (does not import or execute any builder):
`/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/kit-7/verify_delivery.py`
`delivery-audit.json` records export dimensions/alpha padding/importers, unique
UI-folder GUIDs,261 incumbent hashes and all16 personally opened image hashes.
`reproducibility.json` records a second full stage3 run with identical generated
file hashes, including sprite metas and both final contact copies.
''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', type=int, choices=(1, 2, 3), default=3)
    args = parser.parse_args()
    SOURCE.mkdir(exist_ok=True)
    REVIEW.mkdir(exist_ok=True)
    preservation()
    assets = assets_for(args.stage)
    manifest = {a['name']: export(a) for a in assets}
    (SOURCE/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    evidence = {'reveal': reveal_reviews()}
    if args.stage >= 2:
        evidence['banner'] = banner_reviews()
    if args.stage >= 3:
        evidence['timeline'] = timeline_reviews()
        contact()
    write_readme(args.stage)
    (SOURCE/'review-evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    report = audit(assets, manifest)
    (SOURCE/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
