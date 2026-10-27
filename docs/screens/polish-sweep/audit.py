"""Validate reviewed evidence and links; preserve artwork-only measurements.

Raw Button rectangles exclude invisible child hit Images and cannot measure touch targets.
The separate effective-hit-samples.csv uses production EventSystem raycasts.
"""
import csv, hashlib, json, re
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPORT = ROOT.parents[1] / 'reports' / 'POLISH-SWEEP-1.md'
review = json.loads((ROOT / 'visual-review.json').read_text())
all_png = {p.relative_to(ROOT).as_posix() for p in ROOT.glob('section-*/*.png')}
assert all_png == set(review['frames']), ('unreviewed or missing frames', all_png ^ set(review['frames']))
for name, record in review['frames'].items():
    p = ROOT / name
    assert hashlib.sha256(p.read_bytes()).hexdigest() == record['sha256'], name
    with Image.open(p) as im:
        assert list(im.size) == record['size'], name
        assert im.size in ((1440, 900), (844, 390)), name
    assert record['individually_opened'] is True, name

links = []
for document in (REPORT, ROOT / 'reviewed-index.md'):
    for target in re.findall(r'\]\(([^)]+)\)', document.read_text(encoding='utf-8')):
        if target.startswith(('https:', 'http:', '#')):
            continue
        p = (document.parent / target.split('#')[0]).resolve()
        # First finalization creates the linked audit/receipt outputs after validation.
        # A subsequent standalone run requires every output to exist.
        assert p.exists() or p.name in globals().get('PENDING_OUTPUTS', set()), (str(document), target)
        links.append(str(p))
report_text = REPORT.read_text(encoding='utf-8')
for name in all_png:
    assert '../screens/polish-sweep/' + name in report_text, ('frame absent from report', name)

phone = []
exits = {}
for section in sorted(ROOT.glob('section-*')):
    if not section.is_dir():
        continue
    code = json.loads((section / 'native-exit.json').read_text(encoding='utf-8-sig'))['exitCode']
    # Historical failed crew staging has no screenshots; its corrected replacement is section11.
    assert code == 0 or (section.name == 'section-7' and code == 22 and not list(section.glob('*.png'))), (str(section), code)
    exits[section.name] = code
    complete = (section / 'capture-complete.txt').read_text()
    assert 'STAGING FAILED' not in complete or section.name == 'section-7', section.name
    for row in csv.DictReader((section / 'touch-rects.csv').open()):
        if row['frame'].endswith('-844.png') and row['enabled'] == 'True' and min(float(row['width']), float(row['height'])) < 44:
            phone.append({'section': section.name, **row})
with (ROOT / 'phone-artwork-under44.csv').open('w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['section', 'frame', 'control', 'x', 'y', 'width', 'height', 'enabled'])
    writer.writeheader(); writer.writerows(phone)
result = {'reviewed_frames': len(review['frames']), 'resolved_document_links': len(links), 'native_exits': exits,
          'phone_artwork_under44': len(phone), 'measurement_limit': 'Artwork only, not touch bounds; invisible child hit graphics omitted. See effective-hit-samples.csv for current routed samples.',
          'review_limit': 'Hash integrity does not replace the recorded individual visual review or prove manual touch/device/animation acceptance.'}
(ROOT / 'evidence-check.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
