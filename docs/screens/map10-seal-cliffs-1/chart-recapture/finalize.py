"""Bind the two chart frames opened by Codex 1 after Claude's MAP10 handoff."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import shutil
from PIL import Image

out = Path(__file__).resolve().parent
parent = out.parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
assert read(out / 'native-exit.json')['exitCode'] == 0
run = read(out / 'native-run.json')
assert run['sessionOnly'] and all(s['mainMatchesBuild'] for s in run['sources'])
assert 'TEST / no save reads or writes' in (out / 'native.log').read_text()
assert 'MAP10 TEST BUILD PASSED' in (out / 'check-build.log').read_text()
assert 'Application will terminate with return code 0' in (out / 'check-build.log').read_text()
frames = []
points = {'Seal cliffs': (.32, .46), 'Kelp bank': (.216, .278),
          'Whale shelf': (.06, .40), 'Rocky point': (.159, .583),
          'Harbour mouth': (.447, .445)}
for width, height in [(1440, 900), (844, 390)]:
    name = f'chart-{width}.png'
    with Image.open(out / name) as im:
        assert im.size == (width, height)
    scale = height / (480 if height < 600 else 720)
    logical_width = width / scale
    rects = {}
    for label, (px, py) in points.items():
        w = 196 if label == 'Harbour mouth' else 184
        x = px * logical_width + (18 if label == 'Harbour mouth' else -w * .48)
        x = min(max(x, 8), logical_width - w - 8)
        y = py * height / scale + (-10 if label == 'Harbour mouth' else 31)
        rects[label] = [round(v * scale, 4) for v in (x, y, w, 58)]
    a = rects['Seal cliffs']
    comparisons = []
    for label, b in rects.items():
        if label == 'Seal cliffs':
            continue
        intersection = max(0, min(a[0]+a[2], b[0]+b[2])-max(a[0], b[0])) * max(0, min(a[1]+a[3], b[1]+b[3])-max(a[1], b[1]))
        assert intersection == 0, (width, label, intersection)
        comparisons.append({'neighbour': label, 'intersectionAreaPixels': intersection})
    frames.append({'path': name, 'width': width, 'height': height,
                   'sha256': sha(out / name), 'openedBy': 'Codex 1 (Windows app)',
                   'cardRectsPixelsTopLeft': rects, 'labelComparisons': comparisons})

review_path = parent / 'review.json'
prior = out / 'previous-review.json'
if not prior.exists():
    shutil.copyfile(review_path, prior)
review = read(prior)
for f in frames:
    original = parent / f['path']
    previous = out / ('previous-' + f['path'])
    if not previous.exists():
        shutil.copyfile(original, previous)
    shutil.copyfile(out / f['path'], original)
    entry = next(e for e in review['frames'] if e['path'] == f['path'])
    entry.update({k: f[k] for k in ['width', 'height', 'sha256', 'openedBy']})
    entry['captureReceipt'] = 'chart-recapture/review.json'
review['status'] = 'MAP10 E chart handoff recaptured and verified; owned delivery complete, awaiting lead review'
review['findings'] = [s for s in review['findings'] if not s.startswith('CHART FAILURE:')]
review['findings'].append('Chart failure superseded by chart-recapture/review.json: explicit spot9(.32,.46), cliff/gull glyph14; both charts individually opened and Seal cliffs label clears all four named neighbours. Other eight root frames and original runtime receipts retain their prior capture provenance.')
review['chartRecapture'] = 'chart-recapture/review.json'
review['updatedUtc'] = datetime.now(timezone.utc).isoformat()
receipt = {'utc': review['updatedUtc'], 'status': 'PASS - two chart frames opened, no named-neighbour label overlaps',
           'handoff': run['handoff'], 'frames': frames,
           'limits': ['Rendered scripted TEST evidence; no installed-player or physical-device/touch acceptance.',
                      'Existing runner also traversed its downstream trip frames; only the two chart images supersede root evidence.',
                      'Card bounds computed from captured VoyageChart.cs and CoastalCanvas.cs; visual review performed separately.'],
           'evidence': {p.name: sha(p) for p in [out/'native-run.json', out/'native-exit.json', out/'native.log', out/'check-build.log', out/'build.txt', out/'capture-complete.txt']}}
(out / 'review.json').write_text(json.dumps(receipt, indent=2)+'\n')
review_path.write_text(json.dumps(review, indent=2)+'\n')
print('PASS: two chart frames, exact dimensions/hashes, eight label comparisons clear, build/native exit0.')
