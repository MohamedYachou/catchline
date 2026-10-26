"""Seal the already individually reviewed study; no image generation/editing."""
import ast
import hashlib
import json
from pathlib import Path
from PIL import Image

P = Path(__file__).resolve().parent
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, obj):
    (P / name).write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')

rows = json.loads((P / 'metrics.json').read_text(encoding='utf-8-sig'))['captures']
expected = {(w, d, pitch, projection, width, height)
            for w, d in [(8, 5), (10, 5), (12, 6), (14, 7)]
            for pitch in [45, 52, 60] for projection in ['persp', 'ortho']
            for width, height in [(844, 390), (1440, 900)]}
assert len(rows) == 48
assert {(r['roomW'], r['roomD'], r['pitch'], r['projection'], r['width'], r['height']) for r in rows} == expected
for r in rows:
    assert Image.open(P / r['file']).size == (r['width'], r['height'])
    assert r['fits']
    assert r['tappable'] == (r['tileW'] >= 44 and r['tileD'] >= 44)
assert sum(r['tappable'] for r in rows if r['width'] == 844) == 0
assert sum(r['tappable'] for r in rows if r['width'] == 1440) == 23
images = sorted(P.glob('*.png'))
assert len(images) == 56
save('visual-review.json', {'reviewer': 'Codex 1 (Windows app)',
     'method': 'Each final image individually opened with view_image; receipt records the reviewed bytes.',
     'captures': 48, 'contactSheets': 8,
     'images': [{'file': p.name, 'size': list(Image.open(p).size), 'sha256': sha(p), 'opened': True} for p in images]})
assets = json.loads((P / 'main-assets-verification.json').read_text(encoding='utf-8-sig'))
assert assets['MainAssetsUntouched'] and assets['DifferenceCount'] == 0
assert '[Restaurant] COMPLETE48' in (P / 'unity-capture.log').read_text(encoding='utf-8-sig')
for p in P.glob('*.py'):
    ast.parse(p.read_text(encoding='utf-8-sig'))
scratch = P.parents[3] / 'Catchline-sim' / 'Assets'
assert (scratch / 'Editor/RestaurantScaleStudy.cs').read_bytes() == (P / 'RestaurantScaleStudy.cs.txt').read_bytes()
scratchfiles = [scratch / 'Editor/RestaurantScaleStudy.cs', scratch / 'Editor/RestaurantScaleStudy.cs.meta', scratch / 'RestaurantScaleStudy.unity', scratch / 'RestaurantScaleStudy.unity.meta']
assert all(p.exists() for p in scratchfiles)
files = sorted(p for p in P.iterdir() if p.is_file() and p.name != 'delivery-receipt.json')
save('delivery-receipt.json', {'status': 'PASS', 'captures': 48, 'reviewedImages': 56,
     'mainAssetsFilesUnchanged': assets['BeforeCount'], 'phoneThresholdPass': 0, 'desktopThresholdPass': 23,
     'files': [{'file': p.name, 'sha256': sha(p)} for p in files],
     'scratchFiles': [{'path': str(p), 'sha256': sha(p)} for p in scratchfiles],
     'limits': 'Projection/greybox study only; no game regression, interactive touch, final art or installed acceptance.'})
print(f'PASS: 48 captures, 56 reviewed PNGs, {assets["BeforeCount"]} main Assets files unchanged, {len(files)} sealed evidence files')
