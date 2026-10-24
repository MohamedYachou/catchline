"""Compose CREW-STYLES review sheets: current ART108 bust beside the role-dressed redesign.
Layout follows Mo's request: the 3x3 comparison grid gains a fourth row of new women (3 columns x 4 rows).
Python: pillow, numpy (WSL venv ~/.venvs/catchline-ui).
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).parent))
from cut_ui_v2 import key_background

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'Art/Source/UIv2/crew-styles'; OUT = ROOT / 'docs/screens/crew-styles'; OUT.mkdir(parents=True, exist_ok=True)
UI = ROOT / 'Assets/Art/UI'; P = UI / 'Portraits'
TITLE = str(UI / 'Fonts/LilitaOne-Regular.ttf'); BODY = str(UI / 'Fonts/Fredoka-Medium.ttf')
NAVY, CREAM, INK, TEAL, ORANGE = (30, 77, 123), (244, 239, 227), (23, 63, 87), (22, 143, 159), (184, 77, 34)
GRID = [('pim', 'Fisher'), ('kofi', 'Fisher'), ('noor', 'Deckhand'),
        ('ana', 'Deckhand'), ('lise', 'Fisher'), ('olaf', 'Engineer'),
        ('dirk', 'Fisher'), ('mats', 'Deckhand'), ('sam', 'Deckhand'),
        ('rosa', 'Fisher'), ('ines', 'Engineer'), ('tess', 'Fisher')]
EXTRA = [('mira', 'Navigator'), ('tove', 'Deckhand'), ('captain', 'Captain')]


def cutout(path):
    if not path.is_file(): return None
    im = Image.open(path)
    im = key_background(im.convert('RGB')) if im.mode != 'RGBA' or im.getchannel('A').getextrema()[0] == 255 else im.convert('RGBA')
    return im.crop(im.getbbox())


def fit(im, box, top=False):
    out = Image.new('RGBA', box, (0, 0, 0, 0))
    if im is None:
        ImageDraw.Draw(out).text((box[0] // 2, box[1] // 2), 'new', font=ImageFont.truetype(TITLE, 30), fill=(170, 160, 140), anchor='mm'); return out
    im = im.copy(); im.thumbnail(box, Image.LANCZOS)
    out.alpha_composite(im, ((box[0] - im.width) // 2, 0 if top else (box[1] - im.height) // 2)); return out


def circle(im, size):
    disc = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(disc)
    d.ellipse((0, 0, size - 1, size - 1), fill=INK); d.ellipse((5, 5, size - 6, size - 6), fill=(232, 224, 204))
    if im is None:
        d.text((size // 2, size // 2), 'new', font=ImageFont.truetype(TITLE, 30), fill=(170, 160, 140), anchor='mm'); return disc
    art = fit(im, (size - 6, size - 6), True)
    mask = Image.new('L', (size, size), 0); ImageDraw.Draw(mask).ellipse((5, 5, size - 6, size - 6), fill=255)
    layer = Image.new('RGBA', (size, size), (0, 0, 0, 0)); layer.alpha_composite(art, (3, 8))
    a = Image.composite(layer.getchannel('A'), Image.new('L', (size, size), 0), mask)
    disc.paste(layer, (0, 0), a); ImageDraw.Draw(disc).ellipse((2, 2, size - 3, size - 3), outline=INK, width=5); return disc


def sheet(title, entries, name, mode, cell=200, cols=3):
    rows = (len(entries) + cols - 1) // cols; pad = 22; head = 116; rh = cell + 70; cw = 230 + 2 * (cell + pad)
    im = Image.new('RGB', (pad + cols * (cw + pad), head + rows * (rh + 12) + pad), NAVY); d = ImageDraw.Draw(im)
    d.text((pad, 18), title, font=ImageFont.truetype(TITLE, 46), fill=CREAM)
    d.text((pad, 72), 'Left: current ART108 bust     Right: new role outfit     Bottom row: new crew women', font=ImageFont.truetype(BODY, 25), fill=(200, 220, 235))
    for i, (n, role) in enumerate(entries):
        x0, y0 = pad + i % cols * (cw + pad), head + i // cols * (rh + 12)
        d.rounded_rectangle((x0, y0, x0 + cw, y0 + rh), 18, fill=CREAM, outline=INK, width=3)
        d.text((x0 + 18, y0 + rh // 2 - 18), n.title(), font=ImageFont.truetype(TITLE, 34), fill=INK, anchor='lm')
        d.text((x0 + 18, y0 + rh // 2 + 18), role, font=ImageFont.truetype(BODY, 24), fill=TEAL, anchor='lm')
        for k, im_ in enumerate((cutout(P / f'art108-{n}.png'), cutout(SRC / f'portrait-{n}.png'))):
            x = x0 + 210 + k * (cell + pad)
            art = circle(im_, cell) if mode == 'circle' else fit(im_, (cell, cell))
            im.paste(art, (x, y0 + 12), art)
            d.text((x + cell // 2, y0 + rh - 24), 'now' if k == 0 else 'new', font=ImageFont.truetype(TITLE, 24), fill=TEAL if k == 0 else ORANGE, anchor='mm')
    im.save(OUT / name, optimize=True); print(name, im.size)


sheet('Crew in the crew rail: role outfits + more women', GRID, 'portraits-rail.png', 'circle')
sheet('Crew portraits: role outfits + more women', GRID, 'portraits-full.png', 'fit', 230)
sheet('Navigator, deckhand and captain', EXTRA, 'portraits-extra.png', 'fit', 230)
line = SRC / 'lineup-2d.png'
if line.is_file():
    base = Image.open(line).convert('RGB')
    women = SRC / 'lineup-2d-women.png'
    if women.is_file():
        # Round 2 redrew the women's row only; keep the approved men's row from round 1.
        w = Image.open(women).convert('RGB').resize(base.size)
        base.paste(w.crop((0, 0, base.width, base.height // 2)), (0, 0))
    cut = key_background(base)
    bg = Image.new('RGBA', cut.size, (*CREAM, 255)); bg.alpha_composite(cut)
    lab = Image.new('RGB', (bg.width, bg.height + 90), NAVY); lab.paste(bg.convert('RGB'), (0, 90)); d = ImageDraw.Draw(lab)
    for k, r in enumerate(['Fisher', 'Deckhand', 'Engineer', 'Navigator', 'Captain']):
        d.text((bg.width * (k + .5) / 5, 45), r, font=ImageFont.truetype(TITLE, 44), fill=CREAM, anchor='mm')
    lab.save(OUT / 'lineup-2d.png', optimize=True); print('lineup-2d.png', lab.size)
