"""Service kit 4. Same SVG -> 2x CairoSVG -> Unity importer pipeline as kit 2.

Run using /home/mo/.venvs/catchline-ui/bin/python. --stage 1..4 is cumulative.
Only assigned kit-4/service-art/contact-sheet paths are written. No Unity or Git.
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
SOURCE = Path(__file__).resolve().parent / 'kit-4'
OUT = ROOT / 'Assets/Art/UI'
REVIEW = SOURCE / 'review'
NAVY, TEAL, CORAL = '#173f57', '#168f9f', '#df7257'
# Read literals only: importing build_kit2 would regenerate another owner's kit.
tree = ast.parse((SOURCE.parent / 'build_kit2.py').read_text())
DEFS = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'DEFS' for t in n.targets))
PAPER = 'url(#paper)'
BRASS = 'url(#brass)'


def path(d, fill=NAVY, stroke='none', width=4, **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def circle(x, y, r, fill, stroke='none', width=4):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def rect(x, y, w, h, r, fill, stroke='none', width=4):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def disc(glyph):
    outline = 'M49 104 A49 49 0 1 1 79 104 L64 121Z'
    return (path(outline, NAVY, opacity='.23', transform='translate(0 3)')
            + path(outline, PAPER, NAVY, 4)
            + path('M24 37 A43 43 0 0 1 91 22', 'none', '#fffdf5', 3)
            + glyph)


def coin(x, y, r=19):
    return (circle(x, y, r, BRASS, NAVY, 4)
            + path(f'M{x-r*.5} {y-r*.2} Q{x-r*.35} {y-r*.64} {x+r*.2} {y-r*.6}', 'none', '#fff0bd', 3)
            + path(f'M{x-5} {y+5} L{x+5} {y-5}', 'none', '#936a32', 4))


def drink():
    return (path('M44 30 H82 L77 77 Q64 87 51 77Z', TEAL, NAVY, 4)
            + path('M49 40 H77', 'none', '#afe2e5', 4)
            + path('M64 83 V94 M51 95 H77', 'none', NAVY, 5))


def dessert():
    return (path('M36 78 L42 49 H87 L94 78Z', CORAL, NAVY, 4)
            + path('M42 49 Q46 35 58 39 Q64 25 75 39 Q89 35 87 49Z', PAPER, NAVY, 4)
            + path('M33 85 H97', 'none', NAVY, 5))


ASSETS = []


def add(name, body, stage, size=(128, 128), border=(0, 0, 0, 0), safe=None, note=''):
    ASSETS.append(dict(name='svc-' + name, body=body, stage=stage, size=size,
                       border=border, safe=safe, note=note))


# 1: large, deliberately different task silhouettes on the same pointed paper disc.
add('seat', disc(rect(41, 28, 46, 35, 9, TEAL, NAVY)
    + rect(34, 62, 60, 13, 5, TEAL, NAVY)
    + path('M42 77 V94 M86 77 V94', 'none', NAVY, 7)), 1,
    note='Chair: seat a waiting party. Tail tip (64,121).')
add('order', disc(rect(40, 25, 48, 68, 6, PAPER, NAVY)
    + rect(53, 21, 22, 12, 4, BRASS, NAVY, 3)
    + path('M51 48 H77 M51 64 H77 M51 80 H67', 'none', TEAL, 5)), 1,
    note='Order pad, three broad lines. Tail tip (64,121).')
add('pour', disc(path('M39 27 H67 V53 L78 64 V78 Q78 87 68 87 H39 Q30 87 30 78 V48Z', TEAL, NAVY)
    + path('M42 35 H62 M40 56 V74', 'none', '#afe2e5', 4)
    + path('M68 44 H83 L91 56', 'none', NAVY, 6)
    + path('M94 65 Q78 83 94 91 Q110 83 94 65Z', CORAL, NAVY, 3)), 1,
    note='Pitcher and falling drop: pour drinks. Tail tip (64,121).')
add('plate', disc(path('M35 76 Q64 91 93 76 M39 87 Q64 98 89 87', 'none', TEAL, 6)
    + path('M30 65 H98 Q91 79 64 79 Q37 79 30 65Z', 'url(#steel)', NAVY)
    + path('M39 62 Q39 36 64 36 Q89 36 89 62Z', TEAL, NAVY)
    + path('M61 28 H67', 'none', NAVY, 6)
    + path('M48 55 Q49 45 58 44', 'none', '#afe2e5', 4)), 1,
    note='Covered ready plate above stacked dishes: carry from pass. Tail tip (64,121).')
add('wipe', disc(path('M28 71 L58 39 Q63 33 69 39 L97 67 67 94Z', TEAL, NAVY)
    + path('M29 71 L58 73 67 94', 'none', NAVY, 4)
    + path('M67 45 L86 64', 'none', '#afe2e5', 4)
    + path('M29 37 H42 M26 48 H35 M85 88 H98', 'none', CORAL, 5)), 1,
    note='Folded cleaning cloth and broad wipe strokes: clear table. Tail tip (64,121).')
add('pay', disc(coin(49, 68, 23) + coin(77, 50, 23)), 1,
    note='Two brass coins: collect payment. Tail tip (64,121).')
add('cook', disc(path('M30 62 H79 Q78 83 57 83 Q35 83 30 62Z', TEAL, NAVY)
    + path('M79 64 L101 48', 'none', NAVY, 8)
    + path('M46 55 Q31 42 48 23 Q47 36 58 33 Q69 45 60 55Z', CORAL, NAVY, 3)
    + path('M40 91 H74', 'none', NAVY, 5)), 1,
    note='Pan and coral flame: cook station. Tail tip (64,121).')
add('repair', disc(path('M82 27 Q59 22 54 45 L57 56 30 82 Q25 89 32 95 Q38 100 45 93 L72 65 Q96 68 101 46 L84 56 73 45Z',
    'url(#steel)', NAVY, 5)
    + circle(38, 87, 4, NAVY)), 1,
    note='Single diagonal open wrench: repair station. Tail tip (64,121).')
add('wash', disc(circle(59, 62, 30, 'url(#steel)', NAVY)
    + circle(59, 62, 19, PAPER, TEAL, 4)
    + path('M88 23 Q66 48 88 58 Q110 48 88 23Z', TEAL, NAVY, 3)), 1,
    note='Plate and large water drop: wash dishes. Tail tip (64,121).')

# 2: empty queue centre; ring has a truly transparent centre for Radial360.
add('queue', circle(64, 67, 51, NAVY, width=0).replace('fill="'+NAVY+'"', 'fill="'+NAVY+'" opacity=".22"')
    + circle(64, 63, 51, CORAL, NAVY, 4)
    + path('M29 43 A40 40 0 0 1 75 24', 'none', '#ffe8a5', 4), 2,
    safe=[35, 34, 58, 58], note='Live queue number only, centred; coral enamel badge.')
add('ring', circle(64, 64, 52, 'none', NAVY, 10)
    + circle(64, 64, 52, 'none', TEAL, 6), 2,
    note='Unsliced concentric annulus. Overlay a second copy with Image.Filled Radial360 (top origin), tint for patience. Keep square; transparent centre radius47. Source ring band20px including navy edging.')

# 3: moments. Only these backplates/bubbles receive live lettering.
burst = []
for i in range(24):
    a = -math.pi / 2 + i * math.pi / 12
    radius = 58 if i % 2 == 0 else 49
    burst.append(f'{64+math.cos(a)*radius:.2f} {64+math.sin(a)*radius:.2f}')
add('combo', path('M'+' L'.join(burst)+'Z', CORAL, NAVY, 4)
    + rect(20, 43, 88, 42, 18, CORAL), 3,
    safe=[21, 44, 86, 39], note='Burst behind live Combo! text. Centre intentionally empty.')
add('perfect', circle(64, 64, 47, 'none', NAVY, 22)
    + circle(64, 64, 47, 'none', '#ffe8a5', 16)
    + circle(64, 64, 47, 'none', BRASS, 8)
    + path('M64 4 V16 M64 112 V124 M4 64 H16 M112 64 H124', 'none', '#ffe8a5', 4), 3,
    note='Golden halo with3-unit navy edge, transparent centre radius36; place behind dish. No opaque disc; square only.')
add('burnt', path('M25 99 Q8 93 15 77 Q3 59 23 50 Q17 27 40 28 Q43 7 64 20 Q86 7 96 30 Q120 28 116 53 Q132 69 114 81 Q121 99 103 103Z',
    '#7796a2', NAVY, 4)
    + path('M38 54 Q28 69 44 78 M72 35 Q86 48 75 62', 'none', NAVY, 5), 3,
    note='Solid scalloped smoke puff, broad navy curls; burnt dish.')
add('gull', disc(path('M28 73 Q42 41 67 59 Q69 35 86 36 Q101 37 99 53 L110 60 97 66 Q92 86 61 85 L35 91Z', PAPER, NAVY, 4)
    + path('M42 72 Q61 59 77 72 L62 81Z', TEAL)
    + path('M98 53 L112 60 97 64Z', CORAL, NAVY, 3)
    + circle(87, 48, 3, NAVY)
    + path('M70 87 V96 M84 85 V95', 'none', CORAL, 4)), 3,
    note='Gull warning on pointed paper. Broad wing/beak silhouette; no warning text.')


def thought(body):
    return (path('M24 87 C0 77 5 55 17 48 C9 22 34 12 48 19 C62 4 86 10 91 23 C120 17 130 45 116 60 C128 87 99 100 82 93 C61 108 39 99 24 87Z',
                 PAPER, NAVY, 4)
            + circle(28, 108, 7, PAPER, NAVY, 3)
            + circle(16, 121, 3, PAPER) + body)


add('upsell-drink', thought('<g transform="translate(7 -3) scale(.9)">'+drink()+'</g>'), 3,
    note='Small thought bubble: stemmed teal drink. Not a task-disc tail.')
add('upsell-dessert', thought('<g transform="translate(2 -3) scale(.95)">'+dessert()+'</g>'), 3,
    note='Small thought bubble: coral cake with cream top. Not a task-disc tail.')
add('coins', coin(39, 85, 23) + coin(79, 88, 24) + coin(65, 56, 25), 3,
    note='Three brass coin pickup, no baked currency glyph or numeral.')

# 4: slice line is strictly right of the fixed pause cell and brass separator.
pill = (rect(4, 8, 312, 80, 38, NAVY, width=0)
        + rect(4, 4, 312, 80, 38, PAPER, NAVY, 4)
        + rect(10, 10, 67, 68, 32, TEAL, NAVY, 3)
        + rect(30, 28, 9, 31, 3, '#fffaf0')
        + rect(48, 28, 9, 31, 3, '#fffaf0')
        + path('M89 24 V64', 'none', '#d6ad65', 4))
add('clock-pill', pill, 4, (320, 96), (100, 43, 43, 43),
    safe={'clock': [106, 19, 167, 50], 'pause_hit': [9, 9, 69, 69]},
    note='Fixed pause symbol/cell. Stretch only horizontal centre; preserve96 logical height aspect baseline. Border order left/bottom/right/top. Pause hit should be >=44 screen px; live clock can be 2:14 or3 left. No baked text.')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def font(size):
    return ImageFont.truetype(str(ROOT/'Assets/Resources/Fonts/Fredoka-SemiBold.ttf'), size)


def export(a):
    name, (w, h) = a['name'], a['size']
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{DEFS}{a["body"]}</svg>'
    (SOURCE/f'{name}.svg').write_text(svg)
    target = OUT/f'v3-{name}.png'
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(target), output_width=w*2, output_height=h*2)
    meta = target.with_suffix('.png.meta')
    if not meta.exists():
        template = (OUT/'v3-card.png.meta').read_text()
        template = re.sub(r'guid: [a-f0-9]+', f'guid: {uuid.uuid4().hex}', template, count=1)
        template = template.replace('spriteMode: 0', 'spriteMode: 1')
    else:
        template = meta.read_text()
    border = [v*2 for v in a['border']]
    template = re.sub(r'spriteBorder: \{[^}]+\}', f'spriteBorder: {{x: {border[0]}, y: {border[1]}, z: {border[2]}, w: {border[3]}}}', template)
    meta.write_text(template)
    return dict(png=str(target.relative_to(ROOT)), size=[w*2, h*2],
                slice_pixels=border, safe_text_svg_units=a['safe'], viewBox=[0, 0, w, h],
                stage=a['stage'], note=a['note'], sha256=sha(target),
                guid=re.search(r'^guid: (\w+)', template, re.M)[1])


def review_item(a, capture):
    name = a['name']
    im = Image.open(OUT/f'v3-{name}.png').convert('RGBA')
    sheet = Image.new('RGB', (960, 520), '#f4efe3')
    d = ImageDraw.Draw(sheet)
    d.rectangle((480, 0, 959, 250), fill='#182f3a')
    d.text((18, 10), f'v3-{name} / cream', font=font(20), fill=NAVY)
    d.text((498, 10), 'Same asset / night', font=font(20), fill='#fffaf0')
    thumb = im.copy()
    thumb.thumbnail((420, 185), Image.Resampling.LANCZOS)
    for x in (0, 480):
        sheet.paste(thumb, (x+(480-thumb.width)//2, 48+(185-thumb.height)//2), thumb)
    # Real room crop, unchanged/un-darkened; icon sizes are exact, not magnified.
    room = capture.crop((1000, 330, 1224, 474)).convert('RGB')
    for i, px in enumerate((28, 32, 36)):
        tile = room.copy()
        icon = im.copy()
        icon.thumbnail((px, px), Image.Resampling.LANCZOS)
        tile.paste(icon, ((224-icon.width)//2, 40), icon)
        sheet.paste(tile, (12+i*236, 290))
        d.text((18+i*236, 260), f'{px}px / service crop', font=font(17), fill=NAVY)
    tile32 = room.copy()
    icon = im.copy()
    icon.thumbnail((32, 32), Image.Resampling.LANCZOS)
    tile32.paste(icon, ((224-icon.width)//2, 40), icon)
    tile32.save(REVIEW/f'{name}-service-32.png')
    # Nearest-neighbour enlargement exposes the actual32px raster edges.
    zoom = tile32.crop((88, 32, 136, 80)).resize((192, 192), Image.Resampling.NEAREST)
    sheet.paste(zoom, (754, 290))
    d.text((754, 260), '32px / 4x loupe', font=font(17), fill=NAVY)
    d.text((18, 463), 'Original art has no baked words or numerals. Labels belong to review only.', font=font(18), fill=NAVY)
    sheet.save(REVIEW/f'{name}-review.png')


def contact(assets):
    cols, cellw, cellh = 5, 256, 210
    rows = math.ceil(len(assets)/cols)
    half = 60+rows*cellh
    sheet = Image.new('RGB', (cols*cellw, half*2), '#f4efe3')
    d = ImageDraw.Draw(sheet)
    for panel, bg, fg, label in ((0, '#f4efe3', NAVY, 'cream'), (1, '#182f3a', '#fffaf0', 'dark service night')):
        y0 = panel*half
        d.rectangle((0, y0, cols*cellw, y0+half), fill=bg)
        d.text((24, y0+15), f'UI v3 / Service kit 4 / {label}', font=font(25), fill=fg)
        for i, a in enumerate(assets):
            x, y = (i % cols)*cellw, y0+60+(i//cols)*cellh
            im = Image.open(OUT/f'v3-{a["name"]}.png').convert('RGBA')
            im.thumbnail((230, 155), Image.Resampling.LANCZOS)
            sheet.paste(im, (x+(cellw-im.width)//2, y+(155-im.height)//2), im)
            d.text((x+16, y+165), a['name'], font=font(19), fill=fg)
    sheet.save(ROOT/'docs/screens/ui-v3/art-kit-4.png')
    sheet.crop((0, 0, cols*cellw, half)).save(REVIEW/'contact-cream.png')
    sheet.crop((0, half, cols*cellw, half*2)).save(REVIEW/'contact-night.png')


def functional_preview(assets):
    """Review-only live labels, radial clipping and actual nine-slice stretches."""
    names = {a['name'] for a in assets}
    sheet = Image.new('RGB', (1000, 820), '#182f3a')
    d = ImageDraw.Draw(sheet)
    d.text((24, 16), 'Review only / live text + radial fill + nine-slice', font=font(25), fill='#fffaf0')
    if 'svc-queue' in names:
        d.text((24, 66), 'Queue: actual32px +48px', font=font(18), fill='#fffaf0')
        queue = Image.open(OUT/'v3-svc-queue.png').convert('RGBA')
        for i, size in enumerate((32, 32, 32, 48, 48, 48)):
            x, y = 30+i*62, 103
            im = queue.resize((size, size), Image.Resampling.LANCZOS)
            sheet.paste(im, (x, y), im)
            d.text((x+size/2, y+size*.49), str(i%3+1), font=font(round(size*.48)), fill=NAVY, anchor='mm')
        d.text((480, 66), 'Patience:100% /66% /25%', font=font(18), fill='#fffaf0')
        ring = Image.open(OUT/'v3-svc-ring.png').convert('RGBA')
        for i, fraction in enumerate((1, .66, .25)):
            dim = ring.copy()
            dim.putalpha(dim.getchannel('A').point(lambda v: round(v*.22)))
            x, y = 500+i*104, 103
            dim = dim.resize((64, 64), Image.Resampling.LANCZOS)
            sheet.paste(dim, (x, y), dim)
            mask = Image.new('L', ring.size)
            ImageDraw.Draw(mask).pieslice((0, 0, 256, 256), -90, -90+360*fraction, fill=255)
            active = ring.copy()
            active.putalpha(ImageChops.multiply(active.getchannel('A'), mask))
            active = active.resize((64, 64), Image.Resampling.LANCZOS)
            sheet.paste(active, (x, y), active)
    if 'svc-combo' in names:
        d.text((24, 196), 'Moment with live text / transparent halo behind a sample plate', font=font(18), fill='#fffaf0')
        im = Image.open(OUT/'v3-svc-combo.png').convert('RGBA').resize((128, 128), Image.Resampling.LANCZOS)
        sheet.paste(im, (30, 233), im)
        d.text((94, 297), 'Combo!', font=font(20), fill=NAVY, anchor='mm')
        halo = Image.open(OUT/'v3-svc-perfect.png').convert('RGBA').resize((128, 128), Image.Resampling.LANCZOS)
        sheet.paste(halo, (300, 233), halo)
        d.ellipse((331, 264, 397, 330), fill='#fffaf0', outline=TEAL, width=5)
        d.ellipse((347, 280, 381, 314), fill=CORAL)
    if 'svc-clock-pill' in names:
        original = Image.open(OUT/'v3-svc-clock-pill.png').convert('RGBA')

        def sliced(width):
            target = Image.new('RGBA', (width, 96))
            sx, sy = [0, 200, 554, 640], [0, 86, 106, 192]
            dx, dy = [0, 100, width-43, width], [0, 43, 53, 96]
            for row in range(3):
                for col in range(3):
                    patch = original.crop((sx[col], sy[row], sx[col+1], sy[row+1]))
                    patch = patch.resize((dx[col+1]-dx[col], dy[row+1]-dy[row]), Image.Resampling.LANCZOS)
                    target.paste(patch, (dx[col], dy[row]))
            return target

        d.text((24, 400), 'Clock: true nine-slice at320x96 /448x96 /224x48', font=font(18), fill='#fffaf0')
        for y, width, label in ((438, 320, '2:14'), (550, 448, '3 left')):
            pill = sliced(width)
            pd = ImageDraw.Draw(pill)
            pd.text(((106+width-47)/2, 44), label, font=font(38), fill=NAVY, anchor='mm')
            sheet.paste(pill, (24, y), pill)
            if width == 448:
                small = pill.resize((224, 48), Image.Resampling.LANCZOS)
                sheet.paste(small, (24, 675), small)
        d.text((500, 470), 'Pause cell + brass divider stay fixed.', font=font(19), fill='#fffaf0')
        d.text((500, 510), 'Only the blank clock cell stretches.', font=font(19), fill='#fffaf0')
        d.text((500, 550), 'Keep a44px minimum pause hit target.', font=font(19), fill='#fffaf0')
    d.text((24, 778), 'Raster proofs only. Runtime wiring and touch acceptance remain with Claude.', font=font(19), fill='#fffaf0')
    sheet.save(REVIEW/'functional-preview.png')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', type=int, choices=range(1, 5), default=4)
    args = parser.parse_args()
    SOURCE.mkdir(exist_ok=True)
    REVIEW.mkdir(exist_ok=True)
    baseline_path = SOURCE/'preservation.json'
    if not baseline_path.exists():
        protected = [SOURCE.parent/'build_kit2.py', SOURCE.parent/'kit-2/README.md',
                     OUT/'v3-card.png.meta', ROOT/'Assets/Scripts/Game/VoyageRestaurantUi.cs']
        baseline_path.write_text(json.dumps({str(p.relative_to(ROOT)): sha(p) for p in protected}, indent=2)+'\n')
    capture_path = ROOT/'Catchline-ui2-sim/Logs/uiv2-native/day-service-1440.png'
    if not capture_path.exists():
        capture_path = ROOT/'docs/screens/restaurant-mood/r157/day-service-1440.png'
    capture = Image.open(capture_path).convert('RGB')
    assets = [a for a in ASSETS if a['stage'] <= args.stage]
    manifest = {}
    for a in assets:
        manifest[a['name']] = export(a)
        review_item(a, capture)
    (SOURCE/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    contact(assets)
    functional_preview(assets)
    evidence = dict(capture=str(capture_path.relative_to(ROOT)), capture_sha256=sha(capture_path),
                    crop=[1000, 330, 1224, 474], note='Untouched source pixels; actual28/32/36px bounds; separate4x loupe.',
                    files={str(p.relative_to(ROOT)): sha(p) for p in sorted(REVIEW.glob('*.png'))})
    (SOURCE/'review-evidence.json').write_text(json.dumps(evidence, indent=2)+'\n')
    # Structural checks are meaningful asset invariants; visual acceptance is manual.
    guids = []
    for a in assets:
        m = manifest[a['name']]
        svg = ET.parse(SOURCE/f'{a["name"]}.svg').getroot()
        assert not svg.findall('.//{http://www.w3.org/2000/svg}text')
        im = Image.open(ROOT/m['png'])
        assert list(im.size) == m['size'] and im.mode == 'RGBA'
        assert im.getchannel('A').getextrema() == (0, 255)
        assert DEFS in (SOURCE/f'{a["name"]}.svg').read_text()
        guids.append(m['guid'])
    assert len(set(guids)) == len(guids)
    # Source owner may legitimately edit C# concurrently; report, never overwrite.
    preservation = {p: sha(ROOT/p) == h for p, h in json.loads(baseline_path.read_text()).items()}
    report = dict(assets=len(assets), transparent_rgba_2x=True, no_svg_text=True,
                  exact_kit2_defs=True, unique_guids=True, protected_files=preservation,
                  visual_review='Pending manual inspection; see visual-review.json when sealed.')
    (SOURCE/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
