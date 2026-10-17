"""Reuse the actual crew portrait pixels from Mo's supplied fish.png HUD.
No generated approximation or enlargement of the source artwork. Each 57x60
fragment keeps its original warm-cream backing, matching the existing row kit.
"""
from pathlib import Path
from PIL import Image
import hashlib
import json
import uuid

ROOT = Path(__file__).resolve().parents[2]
source = ROOT / 'docs/reference-hud024/fish-original.png'
image = Image.open(source).convert('RGBA')
output = ROOT / 'Assets/Resources/FishReference'
records = {}
for role, y in [('captain', 130), ('deckhand', 215), ('fisherman', 301)]:
    box = (1387, y + 8, 1444, y + 68)
    name = 'portrait-' + role
    path = output / (name + '.png')
    image.crop(box).save(path)
    meta = path.with_suffix('.png.meta')
    if not meta.exists():
        template = (output / 'icon-Net.png.meta').read_text()
        lines = template.splitlines()
        lines[1] = 'guid: ' + uuid.uuid4().hex
        meta.write_text('\n'.join(lines) + '\n')
    records[name] = {'bounds': box, 'size': [57, 60], 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
(ROOT / 'docs/screens/crew016').mkdir(parents=True, exist_ok=True)
(ROOT / 'docs/screens/crew016/portraits.json').write_text(json.dumps({
    'source': 'docs/reference-hud024/fish-original.png',
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'method': 'Exact RGBA crop, no resampling or painting; original cream backing retained.',
    'portraits': records,
}, indent=2) + '\n')
print('Extracted three exact reference portraits (57x60).')
