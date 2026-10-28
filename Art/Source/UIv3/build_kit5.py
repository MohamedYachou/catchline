"""Night choice art. SVG -> CairoSVG 2x -> existing Unity sprite importer.

Run with /home/mo/.venvs/catchline-ui/bin/python. --stage 1..3 is cumulative.
Never imports another kit builder (those modules have write side effects).
All words below occur in review images/metadata only, never shipping SVGs/PNGs.
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
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent / 'kit-5'
OUT = ROOT / 'Assets/Art/UI'
REVIEW = SOURCE / 'review'
NAVY, TEAL, CORAL = '#173f57', '#168f9f', '#df7257'
CREAM, NIGHT, IVORY = '#f4efe3', '#182f3a', '#fffaf0'
PAPER, BRASS, STEEL, WOOD = [f'url(#{s})' for s in ('paper', 'brass', 'steel', 'wood')]
tree = ast.parse((SOURCE.parent / 'build_kit2.py').read_text())
DEFS = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Name) and t.id == 'DEFS' for t in n.targets))
TITLE = [25, 66, 190, 34]
BODY = [30, 213, 180, 73]
WINDOW = [24, 107, 192, 102]
ILLUSTRATION = [69, 107, 102, 102]
KIND = [80, 34, 93, 20]
ASSETS = []


def path(d, fill=NAVY, stroke='none', width=5, **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def rect(x, y, w, h, r, fill, stroke='none', width=4, **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def ellipse(x, y, rx, ry, fill, stroke='none', width=5, **attrs):
    extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" {extra}/>'


def circle(x, y, r, fill, stroke='none', width=4):
    return ellipse(x, y, r, r, fill, stroke, width)


def group(body, transform):
    return f'<g transform="{transform}">{body}</g>'


def pin(x, y, r=5):
    return (circle(x, y + 1.5, r + .8, '#936a32') + circle(x, y, r, BRASS, '#936a32', 1)
            + path(f'M{x-r*.4} {y-r*.3} L{x+r*.1} {y-r*.55}', 'none', '#fff0bd', 1.6))


def add(name, body, stage, size=(256, 256), safe=None, note=''):
    ASSETS.append(dict(name='ncard-' + name, body=body, stage=stage, size=size,
                       border=[0, 0, 0, 0], safe=safe, note=note))


def kind_symbol(kind):
    if kind == 'gadget':
        return path('M67 36 Q59 34 57 41 L59 45 51 51 54 54 63 47 Q71 48 72 41 L67 44 63 40Z', IVORY)
    if kind == 'night':
        return path('M67 35 A10 10 0 1 0 72 51 Q58 52 67 35Z', IVORY)
    return (ellipse(62, 48, 12, 3, NAVY, width=0)
            + path('M52 46 Q53 36 62 36 Q71 36 72 46Z', NAVY)
            + circle(62, 34, 2, NAVY))


def frame(kind, color):
    # Same outer paper dimensions/header/body as the day cards. No faux text lines.
    return (rect(12, 12, 216, 304, 16, NAVY, opacity='.18')
            + rect(12, 8, 216, 304, 16, PAPER, '#a68755', 2)
            + rect(16, 12, 208, 296, 13, 'none', '#fffdf5', 2)
            + pin(120, 23, 6)
            + path('M29 35 H57 V58 H29 L36 46Z M183 35 H211 L204 46 211 58 H183Z', color, NAVY, 1.4)
            + path('M42 52 L51 60 V49 M198 52 L189 60 V49', NAVY, opacity='.28')
            + rect(42, 30, 156, 27, 5, color, NAVY, 1.8)
            + path('M47 34 H193', 'none', '#fffaf0', 1.5, opacity='.45')
            + kind_symbol(kind)
            + rect(16, 62, 208, 42, 5, NAVY)
            + path('M20 64 H220', 'none', '#416c80', 1.3)
            + rect(24, 109, 192, 98, 13, '#f3e9d5', '#d6c49c', 1)
            + path('M34 118 H49 M34 118 V131 M206 118 H191 M206 118 V131', 'none', '#fffdf5', 2)
            + path('M37 201 H203', 'none', '#d6c49c', 1)
            + path('M30 211 H210', 'none', '#d6ad65', 1)
            + path('M91 297 H165', 'none', '#d6c49c', 1.5)
            + path('M120 292 L124 297 120 302 116 297Z', color, '#936a32', 1))


for kind, color in (('gadget', TEAL), ('night', CORAL), ('dish', BRASS)):
    add(kind, frame(kind, color), 1, (240, 320),
        safe=dict(title=TITLE, body=BODY, kind=KIND, window=WINDOW, illustration=ILLUSTRATION),
        note='Fixed 3:4 card, Simple image. No nine-slice: scale uniformly. Navy title band accepts ivory live text. Kind ribbon is blank except its identity symbol.')

# Soft brass selection aura: 1-unit nested translucent contours approximate a
# Gaussian edge without SVG filter support differences. Card is inset24 units.
glow = ''
previous_alpha = 0
for spread in range(23, -1, -1):
    alpha = .34 * math.exp(-(spread / 10) ** 2)
    opacity = (alpha - previous_alpha) / (1 - previous_alpha)
    glow += rect(36-spread, 32-spread, 216+2*spread, 304+2*spread,
                 16+spread, '#ffe8a5', opacity=f'{opacity:.6f}')
    previous_alpha = alpha
add('glow', glow, 1, (288, 368), safe=dict(card=[24, 24, 240, 320]),
    note='Behind card, centred, 24 logical units extra padding per side. Same scale as card, never stretch. Soft alpha only; keep below card and text.')


# 2. Large material planes,5-6unit silhouettes, sparse highlights; no baked labels.
add('warming-lamp',
    rect(30, 208, 196, 18, 8, TEAL, NAVY, 5)
    + path('M184 205 V58 Q184 31 155 31 H102 V53', 'none', NAVY, 13)
    + path('M182 193 V58 Q182 36 156 36 H105', 'none', '#7796a2', 4)
    + path('M82 54 H123 L152 113 Q112 127 53 113Z', BRASS, NAVY, 6)
    + ellipse(102, 114, 50, 10, '#ffe8a5', NAVY, 4)
    + path('M86 63 H116 L132 99', 'none', '#fff0bd', 5)
    + path('M73 137 V155 M102 138 V160 M132 137 V155', 'none', CORAL, 7)
    + ellipse(106, 187, 63, 16, STEEL, NAVY, 5)
    + ellipse(106, 182, 50, 10, PAPER, '#7796a2', 3)
    + path('M69 183 Q107 193 144 183', 'none', TEAL, 4)
    + pin(199, 215, 4), 2,
    note='Brass heat shade, three coral heat rays, steel plate, tall arch and enamel base.')

add('plate-rack',
    path('M30 179 L166 159 229 177 93 202Z', WOOD, NAVY, 5)
    + path('M30 179 V210 L93 229 229 204 V177 L93 202Z', WOOD, NAVY, 5)
    + path('M93 204 V226 M39 188 L85 202 M104 213 L218 193', 'none', '#936a32', 4)
    + path('M41 180 V81 M216 178 V69', 'none', NAVY, 9)
    + path('M41 81 L216 69', 'none', TEAL, 11)
    + ellipse(77, 132, 32, 65, STEEL, NAVY, 5)
    + ellipse(77, 132, 21, 49, PAPER, TEAL, 4)
    + ellipse(126, 126, 32, 65, STEEL, NAVY, 5)
    + ellipse(126, 126, 21, 49, PAPER, TEAL, 4)
    + ellipse(175, 120, 32, 65, STEEL, NAVY, 5)
    + ellipse(175, 120, 21, 49, PAPER, TEAL, 4)
    + path('M30 177 L93 198 229 175 V192 L93 215 30 195Z', TEAL, NAVY, 5)
    + path('M42 183 L93 201 215 181', 'none', '#afe2e5', 3)
    + pin(49, 194, 4) + pin(204, 193, 4), 2,
    note='Three upright ivory plates in a teal-and-timber draining rack; bold repeated plate ovals.')

add('service-bell',
    rect(29, 193, 198, 23, 10, NAVY)
    + rect(34, 180, 188, 24, 10, TEAL, NAVY, 5)
    + path('M48 174 Q50 86 128 86 Q206 86 208 174Z', BRASS, NAVY, 6)
    + ellipse(128, 174, 82, 12, BRASS, NAVY, 5)
    + path('M67 147 Q75 105 110 103', 'none', '#fff0bd', 7)
    + rect(117, 67, 22, 22, 7, BRASS, NAVY, 4)
    + ellipse(128, 64, 25, 9, BRASS, NAVY, 5)
    + path('M43 100 L29 83 M211 100 L226 83 M67 65 L61 44 M189 65 L196 44', 'none', CORAL, 8)
    + path('M49 188 H207', 'none', '#afe2e5', 3), 2,
    note='One large brass counter bell, teal base, broad coral ringing strokes.')

net = (ellipse(144, 95, 72, 70, '#c7d9d9', TEAL, 7)
       + path('M99 42 Q84 95 118 153 M125 27 Q108 95 145 164 M151 26 Q139 94 172 159 M177 35 Q170 95 196 143', 'none', '#7796a2', 4)
       + path('M80 65 Q143 87 205 61 M74 95 Q145 115 214 89 M83 126 Q145 146 206 119', 'none', '#7796a2', 4)
       + ellipse(144, 95, 72, 70, 'none', NAVY, 7)
       + path('M93 150 L45 220', 'none', NAVY, 18)
       + path('M76 178 L46 221', 'none', WOOD, 11)
       + path('M116 110 Q126 82 150 92 Q155 68 174 77 Q189 83 181 100 L194 105 177 112 Q160 133 126 128 L107 134Z', PAPER, NAVY, 5)
       + path('M123 112 Q146 100 162 114 L144 124Z', TEAL)
       + path('M181 98 L195 105 180 109Z', CORAL, NAVY, 3)
       + circle(174, 88, 3, NAVY)
       + path('M135 129 L129 139 M151 129 L146 139', 'none', CORAL, 4))
add('gull-net', net, 2, note='Long timber handle, coarse oval landing net and one ivory gull. Grid kept broad and sparse.')

def shoe(color):
    return (path('M43 135 L58 88 89 99 110 130 Q132 137 177 139 Q208 141 216 164 L214 184 H42 Q29 165 43 135Z', color, NAVY, 6)
            + path('M39 168 Q114 184 216 164 V183 Q133 202 42 185Z', PAPER, NAVY, 5)
            + path('M68 109 L89 120 M61 123 L83 134 M104 147 Q130 159 164 153', 'none', IVORY, 5)
            + path('M182 147 Q202 151 205 160', 'none', '#afe2e5', 4))

add('quick-shoes',
    group(shoe(CORAL), 'translate(27 -25) scale(.86) rotate(-13 128 128)')
    + group(shoe(TEAL), 'translate(0 38) rotate(-9 128 128)')
    + path('M32 99 H63 M20 117 H51 M16 139 H37', 'none', CORAL, 8), 2,
    note='Pair of forward-facing coral/teal work sneakers with ivory soles and three speed strokes.')

def pan(color):
    return (rect(117, 18, 26, 103, 10, color, NAVY, 6)
            + rect(124, 29, 12, 26, 5, PAPER)
            + ellipse(130, 159, 78, 61, NAVY, NAVY, 5)
            + ellipse(130, 151, 78, 57, STEEL, NAVY, 5)
            + ellipse(130, 151, 63, 44, '#365367', '#7796a2', 3)
            + path('M82 149 Q88 125 109 119', 'none', '#c7d9d9', 5))

add('second-pan',
    group(pan(CORAL), 'translate(-20 -4) rotate(-32 128 128) scale(.82)')
    + group(pan(TEAL), 'translate(53 44) rotate(28 128 128) scale(.82)'), 2,
    note='Two complete overlapping steel pans, splayed handles in coral and teal; no numeral.')

ferry = (path('M25 158 H231 L209 202 Q190 218 58 210 L31 186Z', NAVY, NAVY, 6)
         + path('M32 168 H224 L215 181 H38Z', CORAL)
         + path('M48 99 H207 L224 158 H34Z', PAPER, NAVY, 6)
         + rect(68, 65, 102, 36, 5, PAPER, NAVY, 5)
         + path('M63 64 H175', 'none', CORAL, 10)
         + rect(182, 69, 21, 30, 3, BRASS, NAVY, 4)
         + path('M92 65 V44 H118 V65', TEAL, NAVY, 4)
         + path('M40 151 H216', 'none', '#d6ad65', 4)
         + path('M23 220 Q48 207 73 220 T123 220 T173 220 T223 220', 'none', TEAL, 8))
for x in (58, 98, 138, 178):
    ferry += rect(x, 112, 26, 25, 4, TEAL, NAVY, 3) + path(f'M{x+5} 117 H{x+20}', 'none', '#afe2e5', 3)
for x in (82, 123):
    ferry += rect(x, 76, 28, 15, 2, TEAL, NAVY, 3)
ferry += circle(64, 184, 10, IVORY, CORAL, 5) + circle(194, 184, 10, IVORY, CORAL, 5)
add('ferry', ferry, 2, note='Wide navy passenger ferry with two decks, four cabin windows, coral rubbing band and life rings.')

critic = (path('M63 225 Q65 180 98 174 H160 Q192 181 195 225Z', TEAL, NAVY, 6)
          + path('M105 171 L128 193 151 171 145 216 H112Z', PAPER, NAVY, 4)
          + path('M95 74 Q83 89 91 129 Q95 166 127 171 Q165 166 171 128 V87Z', PAPER, NAVY, 5)
          + ellipse(89, 121, 10, 16, PAPER, NAVY, 4)
          + ellipse(170, 121, 10, 16, PAPER, NAVY, 4)
          + path('M72 80 Q67 54 94 48 Q112 22 153 39 Q179 41 187 63 Q190 79 164 83Z', NAVY, NAVY, 5)
          + path('M97 50 Q115 39 138 43', 'none', '#416c80', 5)
          + path('M135 37 L139 27', 'none', NAVY, 7)
          + rect(95, 101, 28, 24, 8, IVORY, NAVY, 6)
          + rect(137, 101, 28, 24, 8, IVORY, NAVY, 6)
          + path('M124 109 Q130 105 136 109 M90 106 L95 108 M165 108 L172 104', 'none', NAVY, 5)
          + path('M130 123 L126 135 H134 M115 148 Q130 155 142 146', 'none', NAVY, 4)
          + group(rect(135, 164, 70, 66, 5, CORAL, NAVY, 5)
                  + rect(144, 166, 60, 58, 4, PAPER, NAVY, 3)
                  + path('M157 166 V219', 'none', '#d6ad65', 3)
                  + path('M184 180 L213 147 220 154 192 186 181 190Z', BRASS, NAVY, 3), 'rotate(-9 170 190)'))
add('critic', critic, 2, note='Ivory-faced critic: navy beret, oversized square glasses and blank cream/coral notebook with brass pencil.')

festival = (path('M25 51 Q128 112 231 51 M40 118 Q128 162 216 118', 'none', NAVY, 5)
            + path('M37 58 L52 98 75 76Z', CORAL, NAVY, 4)
            + path('M91 83 L112 117 130 89Z', TEAL, NAVY, 4)
            + path('M145 86 L173 111 181 77Z', BRASS, NAVY, 4)
            + path('M198 70 L225 87 224 55Z', CORAL, NAVY, 4))
for x, y, color in ((74, 167, BRASS), (178, 164, CORAL)):
    festival += (path(f'M{x} {y-32} V{y-15}', 'none', NAVY, 4)
                 + rect(x-26, y-20, 52, 61, 18, color, NAVY, 5)
                 + path(f'M{x-22} {y-7} H{x+22} M{x-22} {y+25} H{x+22}', 'none', '#936a32' if color == BRASS else NAVY, 3)
                 + path(f'M{x-8} {y-13} Q{x-17} {y+7} {x-8} {y+31}', 'none', '#fff0bd', 4)
                 + rect(x-18, y-26, 36, 9, 3, NAVY)
                 + rect(x-18, y+39, 36, 9, 3, NAVY)
                 + path(f'M{x} {y+49} V{y+62}', 'none', CORAL, 5))
add('festival', festival, 2, note='Curving bunting with four large pennants and two hanging brass/coral lanterns. No confetti noise.')

rain = (path('M55 117 Q25 116 30 91 Q31 72 52 67 Q48 34 83 36 Q106 16 128 37 Q160 24 177 57 Q211 51 223 76 Q243 110 209 118Z', STEEL, NAVY, 6)
        + path('M52 80 Q46 91 54 98 M76 50 Q91 39 103 46', 'none', '#f5fff9', 5)
        + path('M127 139 V208 Q127 229 108 229 Q91 229 91 213', 'none', NAVY, 8)
        + path('M49 187 Q65 129 127 128 Q189 129 205 187 Q184 171 166 187 Q147 171 128 187 Q108 171 88 187 Q69 171 49 187Z', CORAL, NAVY, 6)
        + path('M88 182 Q94 148 127 128 Q157 147 166 182', 'none', '#fff0bd', 4)
        + path('M36 139 L27 158 M72 126 L65 141 M191 129 L185 144 M226 136 L217 156', 'none', TEAL, 8))
add('rain', rain, 2, note='Steel rain cloud above a coral open umbrella; four large slanted teal raindrops and hooked handle.')

add('catch', path('M73 176 L52 227 M185 177 L210 227', 'none', NAVY, 11)
         + rect(36, 32, 184, 166, 10, WOOD, NAVY, 6)
         + rect(48, 44, 160, 142, 4, NAVY, '#936a32', 4)
         + path('M42 40 H212 M43 191 H213', 'none', '#fff0bd', 3)
         + path('M91 112 Q119 78 164 91 L175 78 177 98 191 112 178 126 172 142 159 130 Q118 145 91 112 L70 94 75 112 70 132Z', '#f6f7e9')
         + path('M119 103 Q139 95 157 101 M141 126 Q151 124 157 120', 'none', '#7796a2', 4)
         + circle(175, 109, 4, NAVY)
         + path('M61 161 H104', 'none', '#c7d9d9', 5)
         + path('M161 169 L188 164', 'none', '#f6f7e9', 7)
         + pin(45, 40, 3) + pin(212, 40, 3), 2,
    note='Timber A-frame chalkboard with a single ivory fish silhouette and chalk stub; no heading, letters or numbers.')

icecream = (path('M85 126 H172 L136 230 Q130 243 123 230Z', WOOD, NAVY, 6)
            + path('M96 153 L148 188 M106 182 L139 205 M159 150 L112 185 M150 175 L120 207', 'none', '#936a32', 4)
            + path('M89 137 L128 229', 'none', '#fff0bd', 4)
            + path('M61 121 Q42 100 60 79 Q65 54 95 57 Q104 24 135 31 Q162 32 165 58 Q193 56 201 81 Q216 104 195 122Z', PAPER, NAVY, 6)
            + path('M58 110 Q70 96 86 108 Q106 91 121 107 Q143 93 162 109 Q181 94 198 109 V127 Q183 145 166 128 Q145 149 128 131 Q106 151 87 132 Q65 144 58 127Z', CORAL, NAVY, 5)
            + path('M78 78 Q85 66 98 72 M119 50 Q136 41 145 54 M170 76 Q180 76 185 87', 'none', IVORY, 5)
            + path('M147 35 Q148 19 161 18', 'none', TEAL, 5)
            + circle(145, 34, 11, CORAL, NAVY, 4))
add('ice-cream', icecream, 2, note='One tall waffle cone, ivory/coral scoops and a coral cherry with teal stem. Broad waffle strokes survive64px.')


def font(px, regular=False):
    file = 'Fredoka-SemiBold.ttf'
    return ImageFont.truetype(str(ROOT / 'Assets/Resources/Fonts' / file), px)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def export(a):
    name, (w, h) = a['name'], a['size']
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{DEFS}{a["body"]}</svg>'
    (SOURCE / f'{name}.svg').write_text(svg)
    target = OUT / f'v3-{name}.png'
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(target), output_width=w*2, output_height=h*2)
    meta = target.with_suffix('.png.meta')
    template = meta.read_text() if meta.exists() else (OUT / 'v3-card.png.meta').read_text()
    if not meta.exists():
        template = re.sub(r'guid: [a-f0-9]+', f'guid: {uuid.uuid4().hex}', template, count=1)
    template = template.replace('spriteMode: 0', 'spriteMode: 1')
    template = re.sub(r'spriteBorder: \{[^}]+\}', 'spriteBorder: {x: 0, y: 0, z: 0, w: 0}', template)
    meta.write_text(template)
    return dict(png=str(target.relative_to(ROOT)), svg=str((SOURCE / f'{name}.svg').relative_to(ROOT)),
                size=[w*2, h*2], viewBox=[0, 0, w, h], slice_pixels=a['border'],
                safe_rects_svg_units=a['safe'], note=a['note'], stage=a['stage'],
                sha256=sha(target), guid=re.search(r'^guid: (\w+)', template, re.M)[1])


def composite_card(kind, illustration, title, lines, show_safe=False):
    # 2x review composition, downsample as a whole exactly as a native UI would.
    card = Image.open(OUT / f'v3-ncard-{kind}.png').convert('RGBA')
    art = Image.open(illustration).convert('RGBA').resize((204, 204), Image.Resampling.LANCZOS)
    card.alpha_composite(art, (138, 214))
    d = ImageDraw.Draw(card)
    d.text((253, 88), kind.upper(), font=font(26), fill=IVORY, anchor='mm', stroke_width=2, stroke_fill=NAVY)
    d.text((240, 163), title, font=font(35), fill=IVORY, anchor='mm')
    for i, line in enumerate(lines):
        d.text((240, 451+i*35), line, font=font(32, True), fill=NAVY, anchor='mm')
    if show_safe:
        for box in (TITLE, BODY, WINDOW):
            x, y, w, h = box
            d.rectangle((x*2, y*2, (x+w)*2, (y+h)*2), outline=TEAL, width=2)
        x, y, w, h = ILLUSTRATION
        d.rectangle((x*2, y*2, (x+w)*2, (y+h)*2), outline=CORAL, width=2)
    return card


def frame_reviews(final=False):
    if final:
        samples = [('gadget', OUT/'v3-ncard-warming-lamp.png', 'Warming lamp', ['Keep dishes warm.', 'A little help for', 'the next service.']),
                   ('night', OUT/'v3-ncard-ferry.png', 'Ferry night', ['A busier evening.', 'More guests arrive', 'from the harbour.']),
                   ('dish', OUT/'v3-ncard-ice-cream.png', 'Ice cream', ['A sweet new dish.', 'Add a cool finish', 'to the next menu.'])]
    else:
        # Item1 must be finished before new illustrations; incumbent kit2/4 samples.
        samples = [('gadget', OUT/'v3-prep-pan.png', 'Sample gadget', ['Sample body text.', 'A helpful addition', 'for the next night.']),
                   ('night', OUT/'v3-svc-gull.png', 'Sample night', ['Sample body text.', 'A busier evening', 'with richer tips.']),
                   ('dish', OUT/'v3-prep-crate.png', 'Sample dish', ['Sample body text.', 'A new choice for', 'the evening menu.'])]
    prefix = 'cards' if final else 'frames'
    for bg, fg, label in ((CREAM, NAVY, 'cream'), (NIGHT, IVORY, 'night')):
        sheet = Image.new('RGB', (1440, 900), bg)
        d = ImageDraw.Draw(sheet)
        d.text((30, 20), 'Night choices / ' + ('final art' if final else 'frame proof'), font=font(32), fill=fg)
        d.text((30, 64), 'Live lettering is simulated for review; shipping art is blank.', font=font(20, True), fill=fg)
        for i, (kind, art, title, lines) in enumerate(samples):
            x = 28+i*475
            card = composite_card(kind, art, title, lines)
            large = card.resize((288, 384), Image.Resampling.LANCZOS)
            sheet.paste(large, (x+75, 112), large)
            d.text((x+218, 514), f'{kind} / 240 x 320 viewBox', font=font(21), fill=fg, anchor='mm')
            small = card.resize((150, 200), Image.Resampling.LANCZOS)
            # Actual 150px card with a correct scale/centred288x368 glow.
            aura = Image.open(OUT/'v3-ncard-glow.png').convert('RGBA').resize((180, 230), Image.Resampling.LANCZOS)
            sheet.paste(aura, (x+128, 556), aura)
            sheet.paste(small, (x+143, 571), small)
            d.text((x+218, 803), '150 px / selected', font=font(20), fill=fg, anchor='mm')
        d.text((30, 858), 'Review copy is illustrative. Runtime effects and values remain with the game owner.', font=font(19, True), fill=fg)
        sheet.save(REVIEW / f'{prefix}-{label}.png')
    safe = Image.new('RGB', (1120, 480), CREAM)
    d = ImageDraw.Draw(safe)
    d.text((24, 18), 'Safe areas / original day-card text rectangles retained', font=font(25), fill=NAVY)
    for i, (kind, art, title, lines) in enumerate(samples):
        card = composite_card(kind, art, title, lines, True).resize((240, 320), Image.Resampling.LANCZOS)
        safe.paste(card, (40+i*350, 80), card)
    d.text((24, 434), 'Teal: title/body/window. Coral: square illustration slot. Outlines are review only.', font=font(20, True), fill=NAVY)
    safe.save(REVIEW / f'{prefix}-safe-rects.png')


def illustration_reviews():
    for a in (a for a in ASSETS if a['stage'] == 2):
        name = a['name']
        original = Image.open(OUT / f'v3-{name}.png').convert('RGBA')
        sheet = Image.new('RGB', (960, 370), CREAM)
        d = ImageDraw.Draw(sheet)
        for x, bg, fg, label in ((0, CREAM, NAVY, 'cream'), (480, NIGHT, IVORY, 'night')):
            d.rectangle((x, 0, x+479, 369), fill=bg)
            d.text((x+22, 16), name.removeprefix('ncard-') + ' / ' + label, font=font(24), fill=fg)
            art = original.resize((224, 224), Image.Resampling.LANCZOS)
            sheet.paste(art, (x+30, 74), art)
            small = original.resize((64, 64), Image.Resampling.LANCZOS)
            sheet.paste(small, (x+340, 154), small)
            d.text((x+372, 236), '64 px', font=font(22), fill=fg, anchor='mm')
            d.text((x+22, 330), '256 x 256 viewBox / no baked text', font=font(19, True), fill=fg)
        sheet.save(REVIEW / f'{name}-review.png')


def contact():
    sheet = Image.new('RGB', (1440, 1050), CREAM)
    d = ImageDraw.Draw(sheet)
    samples = [('gadget', 'warming-lamp', 'Warming lamp', ['Keep dishes warm.', 'A little help for', 'the next service.']),
               ('night', 'ferry', 'Ferry night', ['A busier evening.', 'More guests arrive', 'from the harbour.']),
               ('dish', 'ice-cream', 'Ice cream', ['A sweet new dish.', 'Add a cool finish', 'to the next menu.'])]
    illustrations = [a for a in ASSETS if a['stage'] == 2]
    for x0, bg, fg, label in ((0, CREAM, NAVY, 'cream'), (720, NIGHT, IVORY, 'night')):
        d.rectangle((x0, 0, x0+719, 1049), fill=bg)
        d.text((x0+28, 20), 'Night cards / kit 5 / ' + label, font=font(30), fill=fg)
        d.text((x0+28, 64), 'Actual 150 px cards / review-only live labels', font=font(20, True), fill=fg)
        for i, (kind, art, title, lines) in enumerate(samples):
            x, y = x0+54+i*225, 113
            aura = Image.open(OUT/'v3-ncard-glow.png').convert('RGBA').resize((180, 230), Image.Resampling.LANCZOS)
            if i == 0:
                sheet.paste(aura, (x-15, y-15), aura)
            card = composite_card(kind, OUT/f'v3-ncard-{art}.png', title, lines)
            card = card.resize((150, 200), Image.Resampling.LANCZOS)
            sheet.paste(card, (x, y), card)
            d.text((x+75, 340), kind, font=font(21), fill=fg, anchor='mm')
        d.text((x0+28, 390), 'Twelve illustrations / actual 64 px', font=font(25), fill=fg)
        for i, a in enumerate(illustrations):
            x, y = x0+28+(i % 4)*174, 448+(i//4)*174
            art = Image.open(OUT/f'v3-{a["name"]}.png').convert('RGBA').resize((64, 64), Image.Resampling.LANCZOS)
            sheet.paste(art, (x+47, y), art)
            name = a['name'].removeprefix('ncard-').replace('-', ' ')
            d.text((x+79, y+91), name, font=font(19), fill=fg, anchor='mm')
        d.text((x0+28, 1005), 'SVG originals / 2x transparent PNGs / unchanged v3 palette', font=font(18, True), fill=fg)
    sheet.save(ROOT/'docs/screens/ui-v3/art-kit-5.png')
    sheet.save(REVIEW/'contact-sheet.png')
    sheet.crop((0, 0, 720, 1050)).save(REVIEW/'contact-cream.png')
    sheet.crop((720, 0, 1440, 1050)).save(REVIEW/'contact-night.png')


def write_readme():
    (SOURCE/'README.md').write_text('''# Kit 5 - between-night choice cards

NIGHT-CARDS-ART-1 / Codex 1 (Windows app) / 2026-10-28.
Sixteen transparent sprites, authored as SVG geometry and exported at 2x with
CairoSVG. Exact kit-2 DEFS, kit-2/4 navy/teal/coral and paper/brass/steel/wood
materials. Shipping SVGs and PNGs contain no words or numerals. All lettering
in review images simulates live UI; sample effects are illustrative copy.

## Files and sizes

Source SVGs live here; matching PNGs and Unity metas are in `Assets/Art/UI/`.
Names below have the `v3-ncard-` prefix in Assets and `ncard-` prefix here.

| Assets | SVG viewBox | PNG pixels | Purpose |
| --- | --- | --- | --- |
| gadget, night, dish | 240 x 320 | 480 x 640 | Teal wrench, coral moon, brass cloche ribbons |
| glow | 288 x 368 | 576 x 736 | Soft brass selection halo behind a card |
| warming-lamp, plate-rack, service-bell | 256 x 256 | 512 x 512 | Gadgets |
| gull-net, quick-shoes, second-pan | 256 x 256 | 512 x 512 | Gadgets |
| ferry, critic, festival, rain | 256 x 256 | 512 x 512 | Night events |
| catch, ice-cream | 256 x 256 | 512 x 512 | Dishes |

`manifest.json` lists every exact file, size, GUID, PNG SHA256 and rectangle.
`audit.json` records structural/import/preservation checks. `preservation.json`
holds hashes of incumbent source/art references, not backup copies.

## Safe rectangles and live layout

Coordinates are `(x, y, width, height)` from the **top-left of the 240 x 320
card viewBox**, including its transparent padding. Multiply all values by 2
for PNG pixels. Existing day-card title/body rectangles are retained exactly.

| Live region | SVG units | PNG pixels |
| --- | --- | --- |
| Title | 25, 66, 190, 34 | 50, 132, 380, 68 |
| Body | 30, 213, 180, 73 | 60, 426, 360, 146 |
| Illustration window | 24, 107, 192, 102 | 48, 214, 384, 204 |
| Centered square illustration slot | 69, 107, 102, 102 | 138, 214, 204, 204 |
| Kind label, after the baked symbol | 80, 34, 93, 20 | 160, 68, 186, 40 |

Fit the **whole** illustration texture in the square slot, preserve aspect,
and center it at `(120,158)`. Its internal transparent breathing room is
intentional. At a 150 px card width the slot is 63.75 px square, matching the
64 px inspection proofs. Do not stretch art across the wide window.

Use ivory text on the navy title band and navy body text. Review samples use
Fredoka SemiBold: title 17.5 logical units, body 16, kind 13. At 150 px width
these render at approximately 10.9, 10 and 8.1 px respectively. Center title
and body text horizontally; wrap body to the reserved width. Three short
body lines are demonstrated, with room for a fourth. Localized copy must be
fitted/wrapped within these rectangles. Keep gameplay values in live text.
Kind labels use ivory with a thin navy outline so brass stays legible.

For a bottom-left Unity coordinate system, convert a region with
`yBottom = 320 - yTop - height`; scale by the displayed width divided by 240.
The full card rect should retain a 3:4 aspect ratio.

## Slice borders and importer contract

**All sixteen slice borders are `(0,0,0,0)` in PNG pixels** (left, bottom,
right, top). Use Image Type **Simple**, preserve aspect; these are fixed
composition cards like the day cards, not scalable panel backgrounds.
Nine-slicing would deform the pin, ribbon, window and bottom ornament.

Metas follow the existing v3-card importer: Sprite/Single, 100 PPU, centered
pivot, Full Rect mesh, sRGB, alpha transparency, bilinear filtering, Clamp,
no mipmaps, NPOT scaling disabled, uncompressed default platform. Existing
GUIDs are retained on regeneration. No Resources copies are made.

Place the glow **behind** a card, centered on the same rect, at
`cardWidth * 288/240` by `cardHeight * 368/320`. It adds 24 logical units on
each side; at a 150 x 200 card its rect is 180 x 230, offset -15,-15. Use
normal alpha blending and preserve the full glow rect. Do not crop its
padding or let it receive pointer input. No selection animation is baked in.

## Evidence and regeneration

The combined [contact sheet](review/contact-sheet.png) shows all three 150 px
cards with final sample illustrations and live lettering on cream and night,
plus all twelve illustrations at actual 64 px on both backgrounds. It is also
published as `docs/screens/ui-v3/art-kit-5.png`.

- `review/cards-cream.png`, `cards-night.png`: larger composites plus actual
  150 px selected cards.
- `review/cards-safe-rects.png`: final composition with safe-area overlays.
- `review/contact-cream.png`, `contact-night.png`: separate background crops.
- `review/ncard-*-review.png`: each illustration at 224 px and actual 64 px,
  on both backgrounds.
- `review/frames-*.png`: item-1 proofs using incumbent kit-2/4 art before new
  illustration work, retained as the ordered review trail.
- `visual-review.json`: personally opened images with hashes. Reopen any
  image whose hash changes; a generator run cannot grant visual acceptance.

Run from the project root in Ubuntu WSL:

```sh
/home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit5.py --stage 3
```

Requires CairoSVG and Pillow plus the existing Fredoka SemiBold font.
Stages are cumulative: 1 frames/glow, 2 all art and final proofs, 3 complete
delivery including this README. Builders from other kits are read, never
imported/executed. Only assigned kit-5/night-card output paths are written.

All originals and proof PNGs were opened before item completion. Structural
checks and small-scale visual reviews passed. Native Unity import, actual
card-pick interaction, localization and runtime acceptance remain with Claude;
no Unity invocation, C# change, Resources write, Git operation or commit was
performed for this art task.
''')


def audit(assets, manifest):
    for a in assets:
        m = manifest[a['name']]
        svg = ET.parse(ROOT/m['svg']).getroot()
        assert not svg.findall('.//{http://www.w3.org/2000/svg}text')
        assert DEFS in (ROOT/m['svg']).read_text()
        im = Image.open(ROOT/m['png'])
        assert im.mode == 'RGBA' and list(im.size) == m['size']
        assert im.getpixel((0, 0))[3] == 0
        assert im.getchannel('A').getextrema()[0] == 0
        if a['name'] != 'ncard-glow':
            assert im.getchannel('A').getextrema()[1] == 255
        bounds = im.getchannel('A').getbbox()
        assert bounds and bounds[0] > 0 and bounds[1] > 0 and bounds[2] < im.width and bounds[3] < im.height
        meta = (ROOT/m['png']).with_suffix('.png.meta').read_text()
        for setting in ('spriteMode: 1', 'spriteMeshType: 1', 'textureType: 2',
                        'enableMipMap: 0', 'alphaIsTransparency: 1', 'nPOTScale: 0',
                        'filterMode: 1', 'wrapU: 1', 'wrapV: 1',
                        'spriteBorder: {x: 0, y: 0, z: 0, w: 0}'):
            assert setting in meta, (m['png'], setting)
    guids = [m['guid'] for m in manifest.values()]
    assert len(set(guids)) == len(guids)
    occurrences = {g: [] for g in guids}
    meta_count = 0
    for meta_path in (ROOT/'Assets').rglob('*.meta'):
        meta_count += 1
        match = re.search(r'^guid: ([a-f0-9]+)', meta_path.read_text(errors='replace'), re.M)
        if match and match[1] in occurrences:
            occurrences[match[1]].append(str(meta_path.relative_to(ROOT)))
    assert all(len(paths) == 1 for paths in occurrences.values()), occurrences
    preserved = {p: sha(ROOT/p) == h for p, h in json.loads((SOURCE/'preservation.json').read_text()).items()}
    assert all(preserved.values()), preserved
    return dict(assets=len(assets), rgba_2x=True, exact_kit2_defs=True, no_baked_svg_text=True,
                borders_all_zero=True, importer_settings=True, no_edge_clipping=True,
                unique_guids=True, guid_scan_metas=meta_count, protected_files=preserved,
                visual_review='Manual inspection required; see visual-review.json for opened evidence.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', type=int, choices=(1, 2, 3), default=3)
    args = parser.parse_args()
    SOURCE.mkdir(exist_ok=True)
    REVIEW.mkdir(exist_ok=True)
    baseline = SOURCE/'preservation.json'
    if not baseline.exists():
        protected = [SOURCE.parent/'build_kit2.py', SOURCE.parent/'build_kit4.py',
                     OUT/'v3-card.png.meta', SOURCE.parent/'kit-2/README.md',
                     ROOT/'docs/screens/ui-v3/art-kit-2.png', ROOT/'docs/screens/ui-v3/art-kit-4.png']
        protected += sorted((SOURCE.parent/'kit-2').glob('*.svg'))
        protected += sorted((SOURCE.parent/'kit-4').glob('*.svg'))
        protected += sorted(OUT.glob('v3-svc-*')) + sorted(OUT.glob('v3-daycard-*'))
        baseline.write_text(json.dumps({str(p.relative_to(ROOT)): sha(p) for p in protected}, indent=2)+'\n')
    assets = [a for a in ASSETS if a['stage'] <= args.stage]
    manifest = {a['name']: export(a) for a in assets}
    (SOURCE/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    frame_reviews(final=args.stage >= 2)
    if args.stage >= 2:
        illustration_reviews()
        contact()
    if args.stage >= 3:
        write_readme()
    report = audit(assets, manifest)
    (SOURCE/'audit.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'protected_files'}))


if __name__ == '__main__':
    main()
