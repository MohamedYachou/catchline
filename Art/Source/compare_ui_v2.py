"""Side-by-side review sheet: concept (docs/screens/ui-concept) beside native 1440 and 844 captures."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / 'docs/screens/ui-v2'; CONCEPTS = ROOT / 'docs/screens/ui-concept'
CONCEPT = {'voyage': 'voyage-hud', 'operations': 'operations', 'crew': 'crew', 'crew-deckhand': 'crew', 'shop-gear': 'chandlery'}
FONT = ROOT / 'Assets/Art/UI/Fonts/Fredoka-Medium.ttf'


def sheet(screen):
    native = Image.open(SHOTS / f'{screen}-1440.png').convert('RGB')
    phone = Image.open(SHOTS / f'{screen}-844.png').convert('RGB')
    concept = CONCEPTS / f'{CONCEPT.get(screen, "")}.webp'
    h = 720
    panels = [('Native 1440x900', native.resize((round(native.width * h / native.height), h)))]
    if concept.is_file():
        c = Image.open(concept).convert('RGB')
        panels.insert(0, ('Concept', c.resize((round(c.width * h / c.height), h))))
    top = sum(p.width for _, p in panels) + 24 * (len(panels) - 1)
    ph = phone.resize((round(phone.width * 360 / phone.height), 360))
    out = Image.new('RGB', (max(top, ph.width) + 48, h + 360 + 120), (22, 58, 94))
    d = ImageDraw.Draw(out); f = ImageFont.truetype(str(FONT), 26)
    x = 24
    for label, p in panels:
        d.text((x, 10), label, font=f, fill=(244, 239, 227)); out.paste(p, (x, 48)); x += p.width + 24
    d.text((24, h + 62), 'Native 844x390', font=f, fill=(244, 239, 227)); out.paste(ph, (24, h + 100))
    out.save(SHOTS / f'{screen}-compare.png', optimize=True)


for s in (sys.argv[1:] or ['voyage']):
    sheet(s)
    print('compare', s)
