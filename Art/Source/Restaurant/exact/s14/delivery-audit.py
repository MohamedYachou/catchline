"""Independent art-only seal for S6 live chart, S14 entry, S9 states."""
from pathlib import Path
import json, hashlib
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[5]
EXACT = ROOT / 'Art/Source/Restaurant/exact'
HERE = Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
packages = [('s6', 'live-chart'), ('s14', ''), ('s9', 'interaction-states')]
exports = []
preserved = 0
for screen, sub in packages:
    folder = EXACT / screen
    evidence = folder / sub
    items = read(evidence / 'manifest.json')
    root_manifest = read(folder / 'manifest.json')
    for item in items:
        path = folder / item['file']
        im = Image.open(path)
        assert im.mode == 'RGBA'
        assert im.size == tuple(item['size']) == tuple(v*3 for v in item['rect'][2:])
        assert im.getchannel('A').getbbox() == (0, 0, *im.size)
        assert sha(path) == item['sha256']
        assert root_manifest.count(item) == 1
        matches = list(EXACT.glob('s*/' + item['file']))
        assert matches == [path], matches
        border = item.get('borders')
        if border:
            l,b,r,t = border
            assert l+r < im.width and t+b < im.height
        exports.append({'file': str(path.relative_to(ROOT)), 'sha256': sha(path)})
    baseline = evidence / 'baseline-manifest.json'
    if baseline.exists():
        for item in read(baseline):
            assert item in root_manifest
            assert sha(folder / item['file']) == item['sha256']
            preserved += 1
    for visual in read(evidence / 'visual-review.json')['opened']:
        assert sha(evidence / visual['file']) == visual['sha256']
original = Image.open(ROOT / 'Art/Concepts/18-hud-harbour.png').convert('RGBA')
concept = Image.open(ROOT / 'Art/Source/Restaurant/concepts/ui-14-harbour-entry.png').convert('RGBA')
assert original.size == concept.size == (1920,1080)
diff = ImageChops.difference(original,concept)
diff.paste((0,0,0,0), (36,276,476,422))
assert not any(channel.getbbox() for channel in diff.split())
for filename in ['v2-s6-trend-segment.png','v2-s6-trend-fill.png']:
    im = Image.open(EXACT/'s6'/filename)
    assert im.crop((0,0,1,im.height)).tobytes() == im.crop((im.width-1,0,im.width,im.height)).tobytes()
slot = Image.open(EXACT/'s9/v2-s9-slot-target.png')
assert slot.getpixel((slot.width//2,slot.height//2))[3] == 0
assert len(exports) == 10
out = dict(status='PASS',exports=exports,acceptedSpritesPreserved=preserved,uniqueNames=True,tightRGBA3x=True,reviewedVisualHashesCurrent=True,harbourOutsideEntryUnchanged=True,chartHorizontalSeamsZero=True,slotCentreTransparent=True,nativeRuntimeVerified=False)
(HERE/'delivery-audit.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(f'PASS: {len(exports)} exports, {preserved} accepted sprites preserved, visual hashes current, seams/alpha/HUD preservation verified')
