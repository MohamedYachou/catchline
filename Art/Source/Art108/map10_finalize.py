"""Bind the MAP10 evidence already opened by Codex 1; never confers visual approval."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone
from PIL import Image

root = Path(__file__).resolve().parents[3]
out = root / 'docs/screens/map10-seal-cliffs-1'
art = root / 'Art/Models/Maps/GullSealCliffs'
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert read(out / 'native-exit.json')['exitCode'] == 0
run = read(out / 'native-run.json')
assert run['sessionOnly'] and run['sourceCount'] == 145 and not run['mainDriftAtLaunch']
checks = read(out / 'checks.json')
assert (checks['maps'], checks['hullRoutes'], checks['lanes']) == (10, 600, 30)
assert all(checks[k] for k in ['assets', 'chartPurchase', 'anchors', 'groundPoolsReady'])
assert len(checks['trips']) == 4
for name in ['SeaV2-source-audit.json', 'SeaV2-audit.json', 'SeaV2-anchor-audit.json']:
    assert read(art / name)['allPassed'], name
frames = []
for stage in ['chart', 'sail-out', 'arch-pool', 'seal-cove', 'stack-race']:
    for width, height in [(1440, 900), (844, 390)]:
        p = out / f'{stage}-{width}.png'
        with Image.open(p) as im:
            assert im.size == (width, height), (p, im.size)
            assert im.convert('RGB').getextrema()[0][1] > 100, 'black frame'
        frames.append(dict(path=p.name, width=width, height=height, sha256=sha(p), openedBy='Codex 1 (Windows app)'))
assert len((out / 'capture-complete.txt').read_text().splitlines()) == 10
review = dict(utc=datetime.now(timezone.utc).isoformat(),
    status='owned terrain/import/trips/native evidence complete; lead chart handoff pending',
    frames=frames, findings=[
        'All ten exact-size standalone native frames individually opened by Codex 1.',
        'Departure, three grounded anchors and return complete in the actual SessionOnly player; native exit 0.',
        'Six faceted grey corner rocks render without pink materials; central boat/water and primary controls remain clear at both sizes.',
        'Cliff/arch/cove/stack geometry and surfaced life anchors are separately covered by the 17 opened authoring views.',
        'CHART FAILURE: spot 9 still uses Harbour mouth fallback (.447,.445) and generic gear glyph; labels overlap at both sizes. Claude owns point/glyph.',
        'Production blue water retained. Runtime seals/gulls/spray and installed-player/device/touch acceptance are outside this delivery.'
    ], evidence={p.name:sha(p) for p in [out/'checks.json',out/'check-build.log',out/'build.txt',out/'native-run.json',out/'native-exit.json',out/'native.log',out/'capture-complete.txt']})
(out / 'review.json').write_text(json.dumps(review, indent=2)+'\n', encoding='utf-8')
receipt=read(art/'art-receipt.json')
receipt['status']=review['status']
assert all(sha(root/f['path']) == f['sha256'] for f in receipt['files']), 'art receipt drift'
(art/'art-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print('MAP10 evidence: ten dimensions/hashes, native exit 0, 600 routes/30 lanes/three trips; chart pending.')
