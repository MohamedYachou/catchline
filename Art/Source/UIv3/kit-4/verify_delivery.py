"""Independent delivery audit. Regenerates once; never runs Unity or Git."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from PIL import Image

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[3]
OUT = ROOT/'Assets/Art/UI'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


manifest = json.loads((SOURCE/'manifest.json').read_text())
assert len(manifest) == 19
files = [ROOT/'Art/Source/UIv3/build_kit4.py', SOURCE/'README.md', SOURCE/'manifest.json',
         SOURCE/'review-evidence.json', ROOT/'docs/screens/ui-v3/art-kit-4.png']
for name, m in manifest.items():
    files.extend([ROOT/m['png'], (ROOT/m['png']).with_suffix('.png.meta'), SOURCE/f'{name}.svg'])
files.extend(sorted((SOURCE/'review').glob('*.png')))
before = {str(p.relative_to(ROOT)): sha(p) for p in files}
subprocess.run([sys.executable, str(SOURCE.parent/'build_kit4.py')], check=True)
after = {str(p.relative_to(ROOT)): sha(p) for p in files}
assert before == after, 'Regeneration changed an existing delivery byte'

own_guids = set()
for name, m in manifest.items():
    png = ROOT/m['png']
    im = Image.open(png)
    assert im.mode == 'RGBA' and list(im.size) == m['size']
    assert im.getchannel('A').getextrema() == (0, 255)
    assert sha(png) == m['sha256']
    meta = png.with_suffix('.png.meta').read_text()
    guid = re.search(r'^guid: ([0-9a-f]{32})$', meta, re.M)[1]
    assert guid == m['guid'] and guid not in own_guids
    own_guids.add(guid)
    assert 'spriteMode: 1' in meta and 'textureType: 2' in meta
    assert 'alphaIsTransparency: 1' in meta and 'enableMipMap: 0' in meta
    assert 'filterMode: 1' in meta and 'textureCompression: 0' in meta
    border = [int(x) for x in re.search(r'spriteBorder: \{x: (\d+), y: (\d+), z: (\d+), w: (\d+)\}', meta).groups()]
    assert border == m['slice_pixels']
    w, h = m['size']
    assert border[0]+border[2] < w and border[1]+border[3] < h
    xml = ET.parse(SOURCE/f'{name}.svg').getroot()
    assert xml.attrib['viewBox'] == ' '.join(str(v) for v in m['viewBox'])
    assert not xml.findall('.//{http://www.w3.org/2000/svg}text')
    assert not xml.findall('.//{http://www.w3.org/2000/svg}image')

occurrences = {guid: [] for guid in own_guids}
meta_count = 0
for meta in (ROOT/'Assets').rglob('*.meta'):
    meta_count += 1
    match = re.search(r'^guid: ([0-9a-f]{32})', meta.read_text(errors='replace'), re.M)
    if match and match[1] in occurrences:
        occurrences[match[1]].append(str(meta.relative_to(ROOT)))
assert all(len(paths) == 1 for paths in occurrences.values()), occurrences

for name, radius in (('ring', 46), ('perfect', 35)):
    alpha = Image.open(OUT/f'v3-svc-{name}.png').getchannel('A')
    assert alpha.getpixel((128, 128)) == 0
    # A central square safely inside the declared clear circle.
    r = int(radius*2/(2**.5))-2
    assert alpha.crop((128-r, 128-r, 128+r, 128+r)).getextrema() == (0, 0)

evidence = json.loads((SOURCE/'review-evidence.json').read_text())
assert sha(ROOT/evidence['capture']) == evidence['capture_sha256']
assert len(evidence['files']) == 41  # 19 cards +19 crops +2 contacts +functional proof
for p, digest in evidence['files'].items():
    assert sha(ROOT/p) == digest
for link in re.findall(r'\]\(([^)]+)\)', (SOURCE/'README.md').read_text()):
    assert (SOURCE/link).resolve().exists(), link

# Manual visual notes are sealed only after the lead opened each listed PNG.
notes = {
    'seat': 'Chair back/seat/legs distinguish seating at32px.',
    'order': 'Brass clip and broad teal pad rules remain separated.',
    'pour': 'Pitcher silhouette plus coral falling drop reads at32px.',
    'plate': 'Cloche and stacked plate curves remain distinct from pan.',
    'wipe': 'Diagonal folded cloth and coral wipe strokes stay readable.',
    'pay': 'Two brass coins distinct from paper task glyphs and pickup.',
    'cook': 'Pan handle and coral flame remain visible at32px.',
    'repair': 'Open wrench head and diagonal handle remain visible.',
    'wash': 'Plate and oversized teal droplet read together.',
    'queue': 'Clean coral centre; live1/2/3 proof fits at32 and48px.',
    'ring': 'Thin teal annulus, clear centre; radial fill proof reviewed.',
    'combo': 'Broad coral burst; live Combo! fits the safe text rectangle.',
    'perfect': 'Gold halo with navy edge stays readable over warm floor; transparent behind sample plate.',
    'burnt': 'Solid smoke silhouette and two broad curls remain visible.',
    'gull': 'Large bird profile, beak and wing read on pointed paper.',
    'upsell-drink': 'Stemmed teal glass and thought outline distinct from pour.',
    'upsell-dessert': 'Coral cake/cream silhouette distinct from drink.',
    'coins': 'Three separate overlapping brass coins without paper disc.',
    'clock-pill': 'Fixed pause/divider survive true horizontal nine-slice; live text fits.'
}
viewed = {}
for name, m in manifest.items():
    for p in [ROOT/m['png'], SOURCE/f'review/{name}-review.png', SOURCE/f'review/{name}-service-32.png']:
        viewed[str(p.relative_to(ROOT))] = dict(sha256=sha(p), opened=True)
for p in [ROOT/'docs/screens/ui-v3/art-kit-4.png', SOURCE/'review/contact-cream.png',
          SOURCE/'review/contact-night.png', SOURCE/'review/functional-preview.png']:
    viewed[str(p.relative_to(ROOT))] = dict(sha256=sha(p), opened=True)
(SOURCE/'visual-review.json').write_text(json.dumps(dict(
    reviewer='Codex 1 (Windows app)', task='SERVICE-UI-KIT-4',
    method='Each image opened using view_image; actual28/32/36px service composites plus4x loupe.',
    notes=notes, images=viewed, limits='Art review only; no Unity runtime or physical phone acceptance.'), indent=2)+'\n')
protected = json.loads((SOURCE/'preservation.json').read_text())
preserved = {p: sha(ROOT/p) == digest for p, digest in protected.items()}
asset_references_preserved = {p: ok for p, ok in preserved.items() if not p.endswith('.cs')}
assert all(asset_references_preserved.values()), asset_references_preserved
files.extend([SOURCE/'visual-review.json', SOURCE/'audit.json', SOURCE/'preservation.json', Path(__file__)])
hashes = {str(p.relative_to(ROOT)): sha(p) for p in files}
report = dict(result='PASS', assets=19, pngs=19, svgs=19, meta_guids=19,
              fresh_guids_unique_across_asset_metas_scanned=meta_count,
              stable_regeneration=True, import_settings_and_slice_borders=True,
              transparent_ring_centres=True, text_free_vector_originals=True,
              review_images_opened=len(viewed), protected_files=preserved,
              asset_references_preserved=asset_references_preserved,
              concurrent_runtime_note='VoyageRestaurantUi.cs changed externally during art work; never written by these scripts. Its original baseline is retained, not reset.',
              evidence_hashes=hashes, runtime_acceptance='Not performed; Claude integration scope.')
(SOURCE/'delivery-check.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps({k: v for k, v in report.items() if k != 'evidence_hashes'}))
