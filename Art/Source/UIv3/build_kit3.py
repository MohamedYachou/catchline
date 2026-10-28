"""v3 versions of the v2 frame pieces that had none (Mo 10-28: every UI element in v3).

Same pixel size as each v2 original, so the code's slices keep working; the look follows the v3 kit:
gradient paper with a tan stroke, coral enamel for "on", deep navy pills, brass. No baked words.
Run with /home/mo/.venvs/catchline-ui/bin/python Art/Source/UIv3/build_kit3.py.
"""
from pathlib import Path
import re
import uuid
import cairosvg

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent / 'kit-3'
OUT = ROOT / 'Assets/Art/UI'
SOURCE.mkdir(exist_ok=True)
DEFS = '''<defs>
 <linearGradient id="paper" x2="0" y2="1"><stop stop-color="#fffaf0"/><stop offset="1" stop-color="#f3e7cf"/></linearGradient>
 <linearGradient id="coral" x2="0" y2="1"><stop stop-color="#ff9a5c"/><stop offset=".5" stop-color="#f2762f"/><stop offset="1" stop-color="#e25a1c"/></linearGradient>
 <linearGradient id="navy" x2="0" y2="1"><stop stop-color="#24507a"/><stop offset="1" stop-color="#173a63"/></linearGradient>
 <linearGradient id="gold" x2="0" y2="1"><stop stop-color="#ffe199"/><stop offset="1" stop-color="#eab54c"/></linearGradient>
 <linearGradient id="teal" x2="0" y2="1"><stop stop-color="#2bb0bf"/><stop offset="1" stop-color="#14808f"/></linearGradient>
 <linearGradient id="good" x2="0" y2="1"><stop stop-color="#e9f6e2"/><stop offset="1" stop-color="#cfe9c7"/></linearGradient>
 <linearGradient id="warn" x2="0" y2="1"><stop stop-color="#fff2cf"/><stop offset="1" stop-color="#f6dc98"/></linearGradient>
 <linearGradient id="bad" x2="0" y2="1"><stop stop-color="#fde3dc"/><stop offset="1" stop-color="#f5c3b6"/></linearGradient>
 <linearGradient id="lock" x2="0" y2="1"><stop stop-color="#f1ebde"/><stop offset="1" stop-color="#ddd3bf"/></linearGradient>
 <linearGradient id="brass" x2=".7" y2="1"><stop stop-color="#ffe8a5"/><stop offset=".45" stop-color="#d6ad65"/><stop offset="1" stop-color="#936a32"/></linearGradient>
</defs>'''


def shape(x, y, w, h, r, fill, stroke='#c9ab7a', shadow=True, gloss=False):
    s = f'<rect x="{x}" y="{y + 3}" width="{w}" height="{h}" rx="{r}" fill="#2a2a22" opacity=".16"/>' if shadow else ''
    s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{fill})" stroke="{stroke}" stroke-width="2"/>'
    if gloss:
        s += f'<rect x="{x + 6}" y="{y + 4}" width="{w - 12}" height="{h * .38}" rx="{min(r - 3, h * .19)}" fill="#ffffff" opacity=".22"/>'
    else:
        s += f'<rect x="{x + 3}" y="{y + 3}" width="{w - 6}" height="{h - 6}" rx="{max(1, r - 2)}" fill="none" stroke="#fffdf5" stroke-width="1.5" opacity=".8"/>'
    return s


def asset(name, w, h, body):
    """w, h are the v2 pixel size; the SVG is drawn at half and rendered at 2x like kit 2."""
    hw, hh = w / 2, h / 2
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{hw}" height="{hh}" viewBox="0 0 {hw} {hh}">{DEFS}{body(hw, hh)}</svg>'
    (SOURCE / f'{name}.svg').write_text(svg)
    target = OUT / f'v3-{name}.png'
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(target), output_width=w, output_height=h)
    meta = target.with_suffix('.png.meta')
    if not meta.exists():
        src = OUT / f'v2-{name}.png.meta'
        template = (src if src.exists() else OUT / 'v3-card.png.meta').read_text()
        meta.write_text(re.sub(r'guid: [a-f0-9]+', f'guid: {uuid.uuid4().hex}', template, count=1))
    print('v3-' + name, w, h)


P = 3  # inset so the drop shadow stays inside the sprite
asset('tab-off', 256, 192, lambda w, h: shape(P, P, w - 2 * P, h - 2 * P - 3, 16, 'paper'))
asset('tab-on', 256, 192, lambda w, h: shape(P, P, w - 2 * P, h - 2 * P - 3, 16, 'coral', '#c24f1b', gloss=True))
asset('switch', 192, 104, lambda w, h: shape(P, P, w - 2 * P, h - 2 * P - 3, (h - 2 * P - 3) / 2, 'lock', '#c9ab7a', shadow=False))
asset('switch-on', 192, 88, lambda w, h: shape(P, P, w - 2 * P, h - 2 * P - 3, (h - 2 * P - 3) / 2, 'navy', '#0f2c4c', gloss=True))
asset('bubble', 192, 112, lambda w, h: shape(P, P, w - 2 * P, h - 2 * P - 3, 14, 'paper'))
asset('bubble-hot', 192, 112, lambda w, h: shape(P, P, w - 2 * P, h - 2 * P - 3, 14, 'gold', '#b9852c', gloss=True))
for tail, fill, stroke in (('bubble-tail', '#f3e7cf', '#c9ab7a'), ('bubble-hot-tail', '#eab54c', '#b9852c')):
    import PIL.Image as _I
    tw, th = _I.open(OUT / f'v2-{tail}.png').size
    asset(tail, tw, th, lambda w, h, f=fill, s=stroke: f'<path d="M1 1 L{w - 1} 1 L{w / 2} {h - 1} Z" fill="{f}" stroke="{s}" stroke-width="1.5" stroke-linejoin="round"/><path d="M2 1.2 L{w - 2} 1.2" stroke="{f}" stroke-width="2.5"/>')
for key in ('good', 'warn', 'bad', 'lock'):
    asset(f'pill-{key}', 128, 64, lambda w, h, k=key: shape(P, P, w - 2 * P, h - 2 * P - 2, (h - 2 * P - 2) / 2, k, {'good': '#9cc58f', 'warn': '#d9b25a', 'bad': '#e0937f', 'lock': '#c9ab7a'}[k], shadow=False))
asset('badge-tick', 80, 80, lambda w, h: f'<circle cx="{w / 2}" cy="{h / 2 + 1.5}" r="{w / 2 - 2}" fill="#2a2a22" opacity=".18"/><circle cx="{w / 2}" cy="{h / 2}" r="{w / 2 - 2}" fill="url(#brass)"/><circle cx="{w / 2}" cy="{h / 2}" r="{w / 2 - 5}" fill="url(#teal)"/><path d="M{w * .3} {h * .52} L{w * .44} {h * .66} L{w * .71} {h * .36}" fill="none" stroke="#fffaf0" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>')
asset('slab-titled', 256, 256, lambda w, h: shape(P, P, w - 2 * P, h - 2 * P - 3, 16, 'paper')
      + f'<path d="M{P + 1} {P + 16} Q{P + 1} {P + 1} {P + 16} {P + 1} L{w - P - 16} {P + 1} Q{w - P - 1} {P + 1} {w - P - 1} {P + 16} L{w - P - 1} {h * .36} L{P + 1} {h * .36} Z" fill="url(#navy)"/>')
asset('rule', 16, 16, lambda w, h: f'<rect x="0" y="{h / 2 - 1}" width="{w}" height="2" fill="#c9ab7a"/>')
asset('nail', 32, 32, lambda w, h: f'<circle cx="{w / 2}" cy="{h / 2 + .8}" r="{w / 2 - 2}" fill="#2a2a22" opacity=".2"/><circle cx="{w / 2}" cy="{h / 2}" r="{w / 2 - 2}" fill="url(#brass)" stroke="#9d763d" stroke-width=".8"/><ellipse cx="{w / 2 - 1.5}" cy="{h / 2 - 2}" rx="{w * .14}" ry="{w * .07}" fill="#fff0bd"/>')


# Full-screen backdrop (Skin.Planks): the v2 blue boards become calm deep water with soft wave lines. Seamless: the
# wave period divides the width and the rows divide the height. The rope edges become a navy band with a brass line.
def sea(w, h):
    s = f'<rect width="{w}" height="{h}" fill="#1c4769"/>'
    rows, period = 6, w / 4
    for k in range(rows):
        y = (k + .5) * h / rows
        d = f'M0 {y:.2f}' + ''.join(f' q{period / 4:.2f} -5 {period / 2:.2f} 0 t{period / 2:.2f} 0' for _ in range(4))
        shift = (period / 2) * (k % 2)
        s += f'<path d="{d}" transform="translate({-shift:.2f} 0)" fill="none" stroke="#2c5f88" stroke-width="2.2" stroke-linecap="round" opacity=".55"/>'
        s += f'<path d="{d}" transform="translate({w - shift:.2f} 0)" fill="none" stroke="#2c5f88" stroke-width="2.2" stroke-linecap="round" opacity=".55"/>'
    return s
asset('plank-tile', 1024, 519, sea)
asset('rope-h', 163, 64, lambda w, h: f'<rect width="{w}" height="{h}" fill="#14334f"/><rect y="{h * .7}" width="{w}" height="1.5" fill="#d6ad65"/>')
# Tutorial coach mark (SkinSlices: ring 96, bubble 48 on all sides at 2x): a coral enamel ring with a soft glow, and
# Mira's speech card in kit paper.
asset('tut-ring', 256, 256, lambda w, h: f'<rect x="7" y="7" width="{w - 14}" height="{h - 14}" rx="30" fill="none" stroke="#ff9a5c" stroke-width="12" opacity=".28"/>'
      + f'<rect x="7" y="7" width="{w - 14}" height="{h - 14}" rx="30" fill="none" stroke="url(#coral)" stroke-width="5"/>'
      + f'<rect x="9.5" y="9.5" width="{w - 19}" height="{h - 19}" rx="27.5" fill="none" stroke="#fff3e2" stroke-width="1.2" opacity=".85"/>')
asset('tut-bubble', 256, 160, lambda w, h: shape(P, P, w - 2 * P, h - 2 * P - 3, 18, 'paper'))
