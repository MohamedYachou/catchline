"""Independent delivery checks. --regenerate also compares a full repeat build.

Does not grant visual approval: every reviewed image hash must already be recorded.
Only writes delivery-check.json, regeneration.json and delivery.sha256 in kit-6.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from PIL import Image

SOURCE = Path(__file__).resolve().parent
ROOT = SOURCE.parents[3]
BUILDER = SOURCE.parent/'build_kit6.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(manifest):
    files = [BUILDER, Path(__file__)]
    files += [p for p in SOURCE.rglob('*') if p.is_file() and p.suffix != '.pyc'
              and p.name not in ('delivery-check.json', 'regeneration.json', 'delivery.sha256')
              and p != Path(__file__)]
    files += [ROOT/'docs/screens/ui-v3/art-kit-6.png']
    for m in manifest.values():
        p = ROOT/m['png']
        files += [p, p.with_suffix('.png.meta')]
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(files))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--regenerate', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((SOURCE/'manifest.json').read_text())
    expected = {'chip-gadget': [192, 192], 'chip-dish': [192, 192],
                'chip-night': [192, 192], 'chip-new': [80, 80],
                'svc-critic': [256, 256], 'svc-critic-review': [640, 400],
                'fx-rain': [512, 512], 'fx-rain-splash': [512, 64]}
    assert set(manifest) == set(expected)
    reviewed = json.loads((SOURCE/'visual-review.json').read_text())
    opened = {str(p.relative_to(ROOT)) for p in (SOURCE/'review').glob('*.png')}
    opened |= {m['png'] for m in manifest.values()}
    opened.add('docs/screens/ui-v3/art-kit-6.png')
    assert set(reviewed) == opened
    assert all(m['opened'] and sha(ROOT/p) == m['sha256'] for p, m in reviewed.items())
    guids = {}
    for name, m in manifest.items():
        p = ROOT/m['png']
        assert sha(p) == m['sha256']
        im = Image.open(p)
        assert im.mode == 'RGBA' and list(im.size) == expected[name]
        assert m['size'] == expected[name]
        assert m['viewBox'][2]*2 == im.width and m['viewBox'][3]*2 == im.height
        assert m['slice_pixels'] == [0]*4
        svg = ET.parse(ROOT/m['svg']).getroot()
        for node in svg.iter():
            assert node.tag.split('}')[-1] not in ('text', 'image', 'foreignObject')
        assert im.getchannel('A').getextrema()[0] == 0
        if name != 'fx-rain':
            b = im.getchannel('A').getbbox()
            assert b and b[0] > 0 and b[1] > 0 and b[2] < im.width and b[3] < im.height
        meta = p.with_suffix('.png.meta').read_text()
        guid = re.search(r'^guid: ([a-f0-9]{32})$', meta, re.M)[1]
        assert guid == m['guid'] and guid not in guids
        guids[guid] = str(p.with_suffix('.png.meta').relative_to(ROOT))
        for setting in ('spriteMode: 1', 'spriteMeshType: 1', 'textureType: 2',
                        'enableMipMap: 0', 'alphaIsTransparency: 1', 'nPOTScale: 0',
                        'filterMode: 1', 'sRGBTexture: 1', 'spritePixelsToUnits: 100',
                        'spritePivot: {x: 0.5, y: 0.5}',
                        'spriteBorder: {x: 0, y: 0, z: 0, w: 0}'):
            assert setting in meta, (name, setting)
        for axis in 'UV':
            assert f'wrap{axis}: {0 if name == "fx-rain" else 1}' in meta
    # Global uniqueness, including old kit GUIDs and other owners' current imports.
    occurrences = {g: [] for g in guids}
    count = 0
    for p in (ROOT/'Assets').rglob('*.meta'):
        count += 1
        match = re.search(r'^guid: ([a-f0-9]{32})$', p.read_text(errors='replace'), re.M)
        if match and match[1] in occurrences:
            occurrences[match[1]].append(str(p.relative_to(ROOT)))
    assert all(v == [guids[g]] for g, v in occurrences.items()), occurrences
    preservation = json.loads((SOURCE/'preservation.json').read_text())
    assert all(sha(ROOT/p) == h for p, h in preservation.items())
    assert sha(SOURCE/'review/contact-sheet.png') == sha(ROOT/'docs/screens/ui-v3/art-kit-6.png')
    review_safe = manifest['svc-critic-review']['safe_rects_svg_units']
    assert review_safe['stars'] == [[88+i*40, 35, 32, 32] for i in range(5)]
    assert review_safe['body'] == [28, 101, 264, 48]
    # No decorative drawing or fake text in the actual live body area.
    clipping = Image.open(ROOT/manifest['svc-critic-review']['png'])
    assert all(clipping.getpixel((80, y)) == clipping.getpixel((320, y)) == clipping.getpixel((540, y))
               for y in range(202, 298))
    before = inventory(manifest)
    if args.regenerate:
        result = subprocess.run([sys.executable, str(BUILDER), '--stage', '3'],
                                cwd=ROOT, capture_output=True, text=True, check=True)
        after = inventory(json.loads((SOURCE/'manifest.json').read_text()))
        assert before == after, {p: (before.get(p), after.get(p)) for p in before.keys() | after.keys() if before.get(p) != after.get(p)}
        (SOURCE/'regeneration.json').write_text(json.dumps(dict(
            byte_identical=True, compared_files=len(before), assets=8,
            stable_guids=True, builder_stdout=json.loads(result.stdout)), indent=2)+'\n')
    report = dict(result='PASS', assets=8, reviewed_images=len(reviewed),
                  reviewed_image_hashes_match=True, exact_dimensions_2x=True,
                  no_text_or_raster_in_svg=True, simple_zero_slices=True,
                  importer_settings=True, unique_delivery_guids=8, guid_scan_metas=count,
                  incumbent_files_preserved=len(preservation),
                  clipping_body_blank=True, safe_rects_match=True,
                  contact_copies_identical=True,
                  native_unity_acceptance='Not performed; Claude owns runtime wiring/import.')
    (SOURCE/'delivery-check.json').write_text(json.dumps(report, indent=2)+'\n')
    final = inventory(manifest)
    final.update({str((SOURCE/name).relative_to(ROOT)): sha(SOURCE/name)
                  for name in ('delivery-check.json', 'regeneration.json') if (SOURCE/name).exists()})
    (SOURCE/'delivery.sha256').write_text(''.join(f'{h}  {p}\n' for p, h in sorted(final.items())))
    for p, h in final.items():
        assert sha(ROOT/p) == h
    print(json.dumps(dict(**report, delivery_inventory_files=len(final))))


if __name__ == '__main__':
    main()
