"""UI v2 kit (docs/UI-SYSTEM.md section 6): slabs, cards, buttons, bars, pills, chips, tabs.
Python: pillow, cairosvg (WSL venv ~/.venvs/catchline-ui). Run from any directory.
All geometry is logical px; PNGs are exported at 2x as Assets/Art/UI/v2-<name>.png.
Borders in slices-v2.json are export px (left, bottom, right, top); Skin.cs mirrors them.
Illustrations, planks and rope are generated art, cut by cut_ui_v2.py, not built here.
"""
from pathlib import Path
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import cairosvg, io, json, hashlib

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Assets/Art/UI'; SRC = ROOT / 'Art/Source/UIv2/svg'
SRC.mkdir(parents=True, exist_ok=True)

# Tokens (UI-SYSTEM section 1).
T = dict(Plank='#1E4D7B', PlankDark='#163A5E', Rope='#C9A46A', Brass='#D9A441', Cream='#F4EFE3',
         CreamDeep='#E8E0CC', Ink='#173F57', InkSoft='#52747C', HeaderNavy='#1F4E79', Orange='#E36A35',
         OrangeDeep='#B84D22', Teal='#168F9F', Good='#3E9A5B', Warn='#E6AD38', Bad='#C8443A', White='#FFFFFF',
         Green='#4CAF50', Blue='#3B82F6', Purple='#8E44AD', Gold='#E6B422', Red='#D7263D')
OUTLINE, BEVEL, SHADOW = 3, 2, 4
SLICES = {}


def mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02X}' for x, y in zip(a, b))


def light(c, t=.38): return mix(c, '#FFFFFF', t)
def dark(c, t=.16): return mix(c, '#000000', t)


def rr(x, y, w, h, r, fill, extra=''):
    r = min(r, w / 2, h / 2)
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" {extra}/>'


def bevelled(x, y, w, h, r, base, outline=T['Ink'], ow=OUTLINE, bevel=BEVEL, hi=None, lo=None, uid='b'):
    """Outline, then a body whose top-left rim is lighter and bottom-right rim darker."""
    hi = hi or light(base); lo = lo or dark(base)
    ix, iy, iw, ih, ir = x + ow, y + ow, w - 2 * ow, h - 2 * ow, max(0, r - ow)
    return (rr(x, y, w, h, r, outline) +
            f'<clipPath id="{uid}"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" rx="{min(ir, iw / 2, ih / 2)}"/></clipPath>'
            f'<g clip-path="url(#{uid})">' + rr(ix, iy, iw, ih, ir, lo) + rr(ix - bevel, iy - bevel, iw, ih, ir, hi)
            + rr(ix + bevel, iy + bevel, iw - 2 * bevel, ih - 2 * bevel, max(0, ir - bevel), base) + '</g>')


def shadow(x, y, w, h, r, dy=SHADOW, alpha=.35):
    return rr(x, y + dy, w, h, r, T['PlankDark'], f'fill-opacity="{alpha}"')


def svg(w, h, body): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'


def emit(name, w, h, body, border=None, use=''):
    source = svg(w, h, body)
    (SRC / f'{name}.svg').write_text(source + '\n')
    im = Image.open(io.BytesIO(cairosvg.svg2png(bytestring=source.encode(), output_width=w * 2, output_height=h * 2))).convert('RGBA')
    meta = PngInfo(); meta.add_text('Source', f'Art/Source/UIv2/svg/{name}.svg; build_ui_v2.py; SHA256 ' + hashlib.sha256(source.encode()).hexdigest())
    im.save(OUT / f'v2-{name}.png', pnginfo=meta)
    SLICES['v2-' + name] = {'size': [w, h], 'border': [b * 2 for b in border] if border else None, 'use': use}


def pill(x, y, w, h, fill, outline=None, ow=0):
    return rr(x, y, w, h, h / 2, outline) + rr(x + ow, y + ow, w - 2 * ow, h - 2 * ow, (h - 2 * ow) / 2, fill) if outline else rr(x, y, w, h, h / 2, fill)


def build():
    # Slab: the panel. Body 120 x 120 inside a 128 canvas; shadow sits in the bottom gutter.
    emit('slab', 128, 128, shadow(2, 2, 124, 120, 18) + bevelled(2, 2, 124, 120, 18, T['Cream'], uid='s'), [40] * 4, 'panel')
    # Header band: navy top band with a cream rule under it; text is live.
    emit('slab-header', 128, 44, rr(0, 0, 128, 44, 15, T['HeaderNavy']) + f'<rect x="0" y="22" width="128" height="22" fill="{T["HeaderNavy"]}"/>'
         + f'<rect x="0" y="0" width="128" height="3" rx="1.5" fill="{light(T["HeaderNavy"], .18)}"/>', [24, 8, 24, 20], 'header band, top radius')
    # Full-slab variant with integral header (ink outline encloses both).
    emit('slab-titled', 128, 128, shadow(2, 2, 124, 120, 18) + bevelled(2, 2, 124, 120, 18, T['Cream'], uid='t')
         + f'<clipPath id="tc"><rect x="5" y="5" width="118" height="114" rx="15"/></clipPath><g clip-path="url(#tc)">'
         + f'<rect x="5" y="5" width="118" height="44" fill="{T["HeaderNavy"]}"/><rect x="5" y="5" width="118" height="2" fill="{light(T["HeaderNavy"], .25)}"/>'
         + f'<rect x="5" y="49" width="118" height="2" fill="{T["Ink"]}"/></g>', [40, 40, 40, 56], 'slab with 44px navy header band')
    # Cards: inner children of a slab. Soft = tan rim (crew rows); ink = item / stage cards.
    emit('card', 96, 96, shadow(2, 2, 92, 88, 14, 3, .18) + bevelled(2, 2, 92, 88, 14, '#FBF7EE', '#D3C6A8', 2, uid='c'), [30] * 4, 'soft card')
    emit('card-ink', 96, 96, shadow(2, 2, 92, 88, 14, 3, .3) + bevelled(2, 2, 92, 88, 14, '#FBF7EE', uid='ci'), [30] * 4, 'outlined card')
    emit('card-selected', 104, 104, rr(0, 0, 104, 100, 20, T['Blue']) + rr(3, 3, 98, 94, 17, '#FFFFFF')
         + bevelled(6, 6, 92, 88, 14, '#EEF4FF', T['Ink'], uid='cs'), [34] * 4, 'selected card: 4px blue ring')
    emit('card-alert', 104, 104, rr(0, 0, 104, 100, 20, T['Bad'], 'fill-opacity=".9"') + rr(3, 3, 98, 94, 17, '#F6D3CC')
         + bevelled(6, 6, 92, 88, 14, '#FBF7EE', uid='ca'), [34] * 4, 'backed-up card: red glow')
    emit('inset', 64, 64, rr(0, 0, 64, 64, 12, dark(T['CreamDeep'], .1)) + rr(0, 3, 64, 61, 12, T['CreamDeep']), [20] * 4, 'recessed well')
    # Buttons: 3D pills. Bottom edge is part of the sprite; pressed loses it and sits 4px lower.
    def button(name, top, edge, outline=T['Ink']):
        hi = light(top, .3)
        up = rr(2, 2, 124, 58, 29, outline) + rr(5, 5, 118, 52, 26, edge) + rr(5, 5, 118, 46, 23, top) \
            + f'<rect x="20" y="9" width="88" height="6" rx="3" fill="{hi}" fill-opacity=".7"/>'
        emit(name, 128, 64, up, [32, 26, 32, 26], 'button')
        down = rr(2, 6, 124, 54, 27, outline) + rr(5, 9, 118, 48, 24, top) + f'<rect x="20" y="13" width="88" height="5" rx="2.5" fill="{hi}" fill-opacity=".5"/>'
        emit(name + '-pressed', 128, 64, down, [32, 26, 32, 26], 'pressed button')
    button('btn-primary', T['Orange'], T['OrangeDeep'])
    button('btn-secondary', T['Cream'], dark(T['CreamDeep'], .08))
    emit('btn-disabled', 128, 64, rr(2, 6, 124, 54, 27, mix(T['InkSoft'], T['Cream'], .45)) + rr(5, 9, 118, 48, 24, T['CreamDeep']), [32, 26, 32, 26], 'disabled')
    # Square-ish secondary for cards / tabs / Details (radius 14).
    emit('btn-card', 96, 56, rr(2, 2, 92, 50, 14, T['Ink']) + rr(5, 5, 86, 44, 11, dark(T['CreamDeep'], .06)) + rr(5, 5, 86, 39, 11, '#FBF7EE'), [24, 22, 24, 18], 'card button')
    emit('btn-card-pressed', 96, 56, rr(2, 5, 92, 47, 14, T['Ink']) + rr(5, 8, 86, 41, 11, '#F1EADB'), [24, 22, 24, 18], 'card button pressed')
    emit('btn-round', 64, 64, f'<circle cx="32" cy="34" r="29" fill="{T["PlankDark"]}" fill-opacity=".35"/>' + f'<circle cx="32" cy="31" r="29" fill="{T["Ink"]}"/>'
         + f'<circle cx="32" cy="31" r="26" fill="{dark(T["Cream"], .1)}"/><circle cx="32" cy="29" r="24" fill="{T["Cream"]}"/>', None, 'round icon button')
    # Tabs: bottom bar cards. On = navy.
    emit('tab-off', 128, 96, shadow(2, 2, 124, 88, 14, 4, .3) + bevelled(2, 2, 124, 88, 14, '#FBF7EE', uid='to'), [34] * 4, 'tab')
    emit('tab-on', 128, 96, shadow(2, 2, 124, 88, 14, 4, .35) + bevelled(2, 2, 124, 88, 14, T['HeaderNavy'], T['Ink'], hi=light(T['HeaderNavy'], .2), uid='tn')
         + rr(6, 6, 116, 80, 11, 'none', f'stroke="{T["Cream"]}" stroke-width="2" stroke-opacity=".9"'), [34] * 4, 'active tab')
    # Page switch capsule and its pills.
    emit('switch', 96, 52, rr(0, 0, 96, 52, 26, T['Ink']) + rr(3, 3, 90, 46, 23, '#FBF7EE'), [26] * 4, 'page switch capsule')
    emit('switch-on', 96, 44, rr(0, 0, 96, 44, 22, T['HeaderNavy']) + rr(3, 3, 90, 6, 3, light(T['HeaderNavy'], .2)), [22] * 4, 'active pill')
    # Bars: recessed track, fills clip by width.
    emit('bar-track', 64, 16, rr(0, 0, 64, 16, 8, dark(T['CreamDeep'], .18)) + rr(1, 2, 62, 13, 6.5, T['CreamDeep']), [8] * 4, 'bar track')
    for n in ('Good', 'Warn', 'Bad', 'Teal'):
        c = T[n]
        emit('bar-' + n.lower(), 64, 16, rr(1, 1, 62, 14, 7, dark(c, .1)) + rr(1, 1, 62, 11, 5.5, c) + rr(6, 3, 52, 3, 1.5, light(c, .45), 'fill-opacity=".8"'), [8] * 4, 'bar fill')
    # Traffic lights and their pills.
    for n, pale in (('Good', '#DCEFD9'), ('Warn', '#FBEDC6'), ('Bad', '#F7D6D0')):
        c = T[n]
        emit('light-' + n.lower(), 16, 16, f'<circle cx="8" cy="8" r="7.5" fill="{dark(c, .3)}"/><circle cx="8" cy="8" r="6" fill="{c}"/><circle cx="6" cy="5.5" r="2" fill="{light(c, .6)}"/>', None, 'status dot')
        emit('pill-' + n.lower(), 64, 32, rr(0, 0, 64, 32, 16, pale), [16] * 4, 'status pill')
    emit('pill-cream', 96, 44, shadow(1, 1, 94, 40, 20, 2, .2) + bevelled(1, 1, 94, 40, 20, '#FBF7EE', '#D3C6A8', 2, uid='pc'), [22] * 4, 'price pill')
    emit('pill-lock', 64, 32, rr(0, 0, 64, 32, 16, '#E4DDCD') + rr(0, 0, 64, 32, 16, 'none', 'stroke="#CFC5AE" stroke-width="2"'), [16] * 4, 'lock chip')
    emit('pill-navy', 128, 64, shadow(2, 2, 124, 56, 28, 4, .35) + rr(2, 2, 124, 56, 28, T['Ink']) + rr(5, 5, 118, 50, 25, T['HeaderNavy'])
         + rr(18, 8, 92, 5, 2.5, light(T['HeaderNavy'], .25)), [32, 32, 32, 28], 'toast')
    # Class chips: cream pill with class-colour rim; toggled state tints the fill.
    for n in ('White', 'Green', 'Blue', 'Purple', 'Gold', 'Red'):
        c = T[n] if n != 'White' else '#B9C3C6'
        emit('chip-' + n.lower(), 96, 36, rr(0, 0, 96, 36, 18, T['Ink']) + rr(2, 2, 92, 32, 16, c) + rr(5, 5, 86, 26, 13, '#FBF7EE'), [18] * 4, 'class chip')
        emit('chip-' + n.lower() + '-on', 96, 36, rr(0, 0, 96, 36, 18, T['Ink']) + rr(2, 2, 92, 32, 16, c) + rr(5, 5, 86, 26, 13, mix(c, '#FFFFFF', .72)), [18] * 4, 'class chip on')
    # Speech bubble and tail.
    for name, fill in (('bubble', '#FBF7EE'), ('bubble-hot', T['Warn'])):
        emit(name, 96, 56, shadow(2, 2, 92, 48, 18, 4, .3) + bevelled(2, 2, 92, 48, 18, fill, uid=name), [26, 24, 26, 22], 'speech bubble')
        emit(name + '-tail', 32, 20, f'<path d="M3 0 L16 17 L29 0 Z" fill="{T["Ink"]}"/><path d="M8 0 L16 11 L24 0 Z" fill="{fill}"/>', None, 'bubble tail')
    # Portrait frame: cream disc with outline; the bust sits inside, clipped round.
    emit('portrait-frame', 64, 64, f'<circle cx="32" cy="32" r="31" fill="{T["Ink"]}"/><circle cx="32" cy="32" r="28" fill="{T["CreamDeep"]}"/>', None, 'portrait disc')
    emit('portrait-ring', 64, 64, f'<circle cx="32" cy="32" r="29.5" fill="none" stroke="{T["Ink"]}" stroke-width="3"/>', None, 'portrait ring over art')
    emit('portrait-square', 96, 96, shadow(2, 2, 92, 88, 16, 3, .3) + bevelled(2, 2, 92, 88, 16, '#FBF7EE', uid='ps'), [30] * 4, 'large portrait frame')
    # Brass nail, tick badge, flow arrow, rope knot dot.
    emit('nail', 16, 16, f'<circle cx="8" cy="8" r="6.5" fill="{dark(T["Brass"], .45)}"/><circle cx="8" cy="7.5" r="5" fill="{T["Brass"]}"/><circle cx="6.5" cy="6" r="1.8" fill="{light(T["Brass"], .6)}"/>', None, 'nail')
    emit('badge-tick', 40, 40, f'<circle cx="20" cy="20" r="19" fill="{T["Ink"]}"/><circle cx="20" cy="20" r="16" fill="{T["HeaderNavy"]}"/>'
         + f'<path d="M11 20.5 L17.5 27 L29 14" fill="none" stroke="#FFFFFF" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>', None, 'selected tick badge')
    emit('arrow-flow', 32, 40, f'<path d="M3 11 H15 V3 L30 20 L15 37 V29 H3 Z" fill="{T["HeaderNavy"]}" stroke="{T["Cream"]}" stroke-width="2.5" stroke-linejoin="round"/>', None, 'stage flow arrow')
    emit('icon-back', 40, 40, f'<path d="M25 7 L12 20 L25 33" fill="none" stroke="{T["Ink"]}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>', None, 'back chevron')
    emit('icon-goal', 40, 40, ''.join(f'<circle cx="20" cy="20" r="{r}" fill="{c}"/>' for r, c in ((19, T['Ink']), (17, T['Bad']), (13, '#FFFFFF'), (9.5, T['Bad']), (5.5, '#FFFFFF'), (2.5, T['Bad']))), None, 'goal target')
    emit('icon-menu', 40, 40, ''.join(f'<rect x="7" y="{y}" width="26" height="5" rx="2.5" fill="{T["Ink"]}"/>' for y in (10, 18, 26)), None, 'menu')
    emit('infinity', 40, 24, f'<path d="M20 12 C14 3 4 3 4 12 C4 21 14 21 20 12 C26 3 36 3 36 12 C36 21 26 21 20 12 Z" fill="none" stroke="#FFFFFF" stroke-width="4.5" stroke-linejoin="round"/>', None, 'infinity glyph, tinted at runtime')
    emit('dim', 8, 8, f'<rect width="8" height="8" fill="{T["PlankDark"]}" fill-opacity=".6"/>', None, 'modal dim')
    emit('rule', 8, 8, f'<rect width="8" height="8" fill="{T["CreamDeep"]}"/>', None, 'divider')
    (ROOT / 'Art/Source/UIv2/slices-v2.json').write_text(json.dumps(SLICES, indent=1) + '\n')
    rows = '\n'.join(f'            ["{k}"] = new Vector4({b[0]}, {b[1]}, {b[2]}, {b[3]}),' for k, v in sorted(SLICES.items()) if (b := v['border']))
    (ROOT / 'Assets/Scripts/Game/SkinSlices.cs').write_text(
        '// Generated by Art/Source/build_ui_v2.py; do not edit. Export-px borders (left, bottom, right, top).\n'
        'using System.Collections.Generic;\nusing UnityEngine;\n\nnamespace Catchline.Game\n{\n    static class SkinSlices\n    {\n'
        '        public static readonly Dictionary<string, Vector4> Border = new()\n        {\n' + rows + '\n        };\n    }\n}\n')
    print(f'{len(SLICES)} sprites -> {OUT}')


if __name__ == '__main__':
    build()
