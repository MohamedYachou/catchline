"""Cut the generated UI v2 sheets (Art/Source/UIv2/generated) into Assets/Art/UI/v2-*.png.
Deterministic: flood-fill keys the flat grey sheet background from each cell border (enclosed greys such
as the padlock survive), feathers and un-mixes the edge, trims, and exports at a fixed size.
Python: pillow, numpy (WSL venv ~/.venvs/catchline-ui).
"""
from pathlib import Path
from collections import deque
from PIL import Image, ImageFilter
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
GEN = ROOT / 'Art/Source/UIv2/generated'; OUT = ROOT / 'Assets/Art/UI'

ICONS_A = ['coin', 'fish', 'hold', 'fuel', 'chum', 'bait-scraps', 'worms', 'squid', 'rod', 'net', 'cage', 'line',
           'jig', 'sort', 'table', 'haul', 'crew', 'ops']
ICONS_B = ['home', 'map', 'gear', 'supplies', 'market', 'lock', 'tick', 'cycle', 'trash', 'sun', 'moon', 'wheel',
           'radio', 'warning', 'clock', 'anchor', 'engine', 'deep-rig']
STAGES = ['fishing', 'hauling', 'processing', 'table', 'hold', 'chum']
ITEMS = ['bigcooler', 'icebox', 'rodholder', 'lunchtin', 'rodfibreglass', 'rodcarbon', 'netsystem', 'thirddeepline',
         'worms', 'squid', 'fuel', 'net', 'deep-net', 'skiff', 'compact-fisher', 'lantern']
PORTRAITS_A = ['sam', 'jo', 'ana', 'bram', 'kofi', 'lise', 'mats', 'noor', 'pim']
PORTRAITS_B = ['rosa', 'tess', 'yusuf', 'ines', 'dirk', 'mei', 'olaf', 'captain', 'engineer']


def key_background(cell, tol=26):
    """Alpha from a border flood fill of near-background pixels, with an un-mixed, feathered edge."""
    a = np.asarray(cell.convert('RGB')).astype(np.int16)
    h, w, _ = a.shape
    border = np.concatenate([a[0], a[-1], a[:, 0], a[:, -1]])
    bg = np.median(border, axis=0)
    near = np.abs(a - bg).max(axis=2) <= tol
    outside = np.zeros((h, w), bool)
    q = deque((y, x) for y in range(h) for x in (0, w - 1) if near[y, x])
    q.extend((y, x) for x in range(w) for y in (0, h - 1) if near[y, x])
    for y, x in q: outside[y, x] = True
    while q:
        y, x = q.popleft()
        for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
            if 0 <= ny < h and 0 <= nx < w and near[ny, nx] and not outside[ny, nx]:
                outside[ny, nx] = True; q.append((ny, nx))
    solid = ~outside
    # Drop fragments of neighbouring cells: keep components at least 3% of the largest one.
    seen = np.zeros((h, w), bool); comps = []
    for sy, sx in zip(*np.nonzero(solid)):
        if seen[sy, sx]: continue
        pts = [(sy, sx)]; seen[sy, sx] = True; i = 0
        while i < len(pts):
            y, x = pts[i]; i += 1
            for ny, nx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= ny < h and 0 <= nx < w and solid[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True; pts.append((ny, nx))
        comps.append(pts)
    biggest = max(len(c) for c in comps)
    for c in comps:
        if len(c) < biggest * .03:
            ys, xs = zip(*c); solid[list(ys), list(xs)] = False
    alpha = Image.fromarray(np.where(solid, 255, 0).astype(np.uint8))
    # Soften the 1px seam and pull the grey out of semi-transparent edge pixels.
    alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.8))
    al = np.asarray(alpha).astype(np.float32) / 255
    rgb = a.astype(np.float32)
    k = np.clip(al, .2, 1)[..., None]
    rgb = np.clip((rgb - bg * (1 - k)) / k, 0, 255)
    out = np.dstack([rgb, al * 255]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def grid(sheet, cols, rows):
    im = Image.open(GEN / sheet).convert('RGB')
    cw, ch = im.width / cols, im.height / rows
    for r in range(rows):
        for c in range(cols):
            yield im.crop((round(c * cw), round(r * ch), round((c + 1) * cw), round((r + 1) * ch)))


def fit(img, size, pad=.06, square_top=False):
    bbox = img.getbbox()
    img = img.crop(bbox)
    W, H = size
    s = min(W * (1 - 2 * pad) / img.width, H * (1 - 2 * pad) / img.height)
    img = img.resize((max(1, round(img.width * s)), max(1, round(img.height * s))), Image.LANCZOS)
    canvas = Image.new('RGBA', size, (0, 0, 0, 0))
    canvas.alpha_composite(img, ((W - img.width) // 2, round(H * pad) if square_top else (H - img.height) // 2))
    return canvas


def save(img, name):
    img.save(OUT / f'v2-{name}.png', optimize=True)


def deckhand_hat(img):
    """Orange beanie variant: navy hue in the hat band (top of the bust) shifts to safety orange."""
    a = np.asarray(img).astype(np.float32)
    rgb, al = a[..., :3], a[..., 3]
    ys = np.nonzero(al.max(axis=1) > 0)[0]
    top, height = ys.min(), ys.max() - ys.min()
    band = np.zeros(al.shape, bool); band[top: top + int(height * .47)] = True
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    navy = (b > r + 25) & (b > g + 10) & (al > 0)
    m = band & navy
    lum = (.3 * r + .59 * g + .11 * b) / 255
    orange = np.array([227, 106, 53], np.float32)
    shade = np.clip(.45 + lum * 2.2, .35, 1.35)[..., None]
    rgb[m] = np.clip(orange * shade, 0, 255)[m]
    return Image.fromarray(np.dstack([rgb, al]).astype(np.uint8), 'RGBA')


def plank():
    a = np.asarray(Image.open(GEN / 'plank-tile.png').convert('RGB')).astype(np.float32)
    lum = a @ np.array([.3, .59, .11], np.float32)
    # Crop from the first groove to the last so the tile holds whole boards and repeats vertically.
    rows = lum.mean(axis=1); dark = rows < rows.mean() - 2.2 * rows.std()
    grooves = [y for y in range(1, len(rows) - 1) if dark[y] and rows[y] <= rows[y - 1] and rows[y] <= rows[y + 1]]
    top, bottom = grooves[0], grooves[-1]
    lum = lum[top:bottom]
    # Grade by luminance only so the grain keeps the token hue (no colour casts).
    target = np.array([0x1E, 0x4D, 0x7B], np.float32)
    rgb = target * (lum / lum.mean())[..., None]
    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8))
    img = img.resize((1024, round(img.height * 1024 / img.width)), Image.LANCZOS)  # keep board proportions
    a = np.asarray(img).astype(np.float32)
    # Horizontal seam: cross-fade with a half-width roll near the left/right edges.
    shifted = np.roll(a, 512, 1)
    m = np.clip((np.abs(np.linspace(-1, 1, a.shape[1])) - .6) / .35, 0, 1)[None, :, None]
    a = a * (1 - m) + shifted * m
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(OUT / 'v2-plank-tile.png', optimize=True)


def rope():
    cut = key_background(Image.open(GEN / 'rope-tile.png').convert('RGB'))
    cut = cut.crop(cut.getbbox())
    # One repeat period from autocorrelation of the alpha profile along x.
    prof = np.asarray(cut)[..., 3].astype(np.float32).mean(axis=0)
    prof -= prof.mean()
    lags = range(40, len(prof) // 2)
    corr = [np.dot(prof[:-l], prof[l:]) / (len(prof) - l) for l in lags]
    period = lags[int(np.argmax(corr))]
    start = cut.width // 2 - period * 2
    tile = cut.crop((start, 0, start + period * 4, cut.height))
    tile = tile.resize((round(tile.width * 64 / tile.height), 64), Image.LANCZOS)
    tile.save(OUT / 'v2-rope-h.png', optimize=True)
    tile.rotate(90, expand=True).save(OUT / 'v2-rope-v.png', optimize=True)
    return period


def build():
    for sheet, names in (('icons-a.png', ICONS_A), ('icons-b.png', ICONS_B)):
        for cell, name in zip(grid(sheet, 6, 3), names):
            save(fit(key_background(cell), (160, 160)), 'icon-' + name)
    fish = Image.open(OUT / 'v2-icon-fish.png')
    g = np.asarray(fish).astype(np.float32)
    lum = (.3 * g[..., 0] + .59 * g[..., 1] + .11 * g[..., 2]) / 255
    mono = np.clip(70 + lum * 185 * 1.15, 0, 255)
    Image.fromarray(np.dstack([mono, mono, mono, g[..., 3]]).astype(np.uint8), 'RGBA').save(OUT / 'v2-icon-fish-mono.png')
    # Goal target and menu are small glyphs the sheets did not include.
    for cell, name in zip(grid('stages.png', 3, 2), STAGES):
        save(fit(key_background(cell), (288, 288)), 'stage-' + name)
    for cell, name in zip(grid('items.png', 4, 4), ITEMS):
        save(fit(key_background(cell), (480, 360)), 'item-' + name)
    for sheet, names in (('portraits-a.png', PORTRAITS_A), ('portraits-b.png', PORTRAITS_B)):
        for cell, name in zip(grid(sheet, 3, 3), names):
            bust = fit(key_background(cell), (400, 400), .02, True)
            save(bust, 'portrait-' + name)
            if name not in ('captain', 'engineer'): save(deckhand_hat(bust), 'portrait-' + name + '-deck')
    plank()
    print('rope period', rope())
    print('cut', len(list(OUT.glob('v2-*.png'))), 'v2 sprites total')


if __name__ == '__main__':
    build()
