"""Read-only independent kit7 delivery verification; never imports/runs builders."""
from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from PIL import Image, ImageChops

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
OUT = ROOT/'Assets/Art/UI'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    expected = {'ncard-back': (240, 320), 'ncard-shine': (240, 320),
                'event-banner': (640, 200), 'tl-ferry': (48, 56),
                'tl-critic': (48, 56), 'tl-glow': (80, 88)}
    manifest = json.loads((HERE/'manifest.json').read_text())
    assert set(manifest) == set(expected), 'Missing/extra shipping asset'
    guids = []
    for name, size in expected.items():
        entry = manifest[name]
        png = ROOT/entry['png']
        im = Image.open(png)
        assert im.mode == 'RGBA' and im.size == tuple(v*2 for v in size), name
        assert sha(png) == entry['sha256'], name
        alpha = im.getchannel('A')
        assert alpha.getbbox() is not None and alpha.getextrema()[0] == 0
        assert all(alpha.crop(box).getbbox() is None for box in
                   [(0, 0, im.width, 1), (0, im.height-1, im.width, im.height),
                    (0, 0, 1, im.height), (im.width-1, 0, im.width, im.height)]), name
        svg = ET.parse(ROOT/entry['svg']).getroot()
        assert svg.attrib['viewBox'] == '0 0 %s %s' % size
        assert not any(n.tag.rsplit('}', 1)[-1] in ('text', 'image', 'foreignObject') for n in svg.iter())
        meta = png.with_suffix('.png.meta').read_text()
        guid = re.search(r'^guid: ([a-f0-9]{32})$', meta, re.M)[1]
        assert guid == entry['guid']
        guids.append(guid)
        for token in ('spriteMode: 1', 'spriteMeshType: 1', 'spritePixelsToUnits: 100',
                      'spritePivot: {x: 0.5, y: 0.5}', 'enableMipMap: 0',
                      'filterMode: 1', 'wrapU: 1', 'wrapV: 1', 'alphaIsTransparency: 1'):
            assert token in meta, (name, token)
    assert len(set(guids)) == 6
    ui_guids = {}
    for meta_path in OUT.glob('*.meta'):
        match = re.search(r'^guid: ([a-f0-9]{32})$', meta_path.read_text(), re.M)
        if match:
            ui_guids.setdefault(match[1], []).append(meta_path.name)
    for guid in guids:
        matches = ui_guids.get(guid, [])
        assert len(matches) == 1, (guid, matches)
    assert ImageChops.difference(Image.open(OUT/'v3-ncard-back.png').getchannel('A'),
                                Image.open(OUT/'v3-ncard-night.png').getchannel('A')).getbbox() is None
    baseline = json.loads((HERE/'preservation.json').read_text())
    for path, digest in baseline.items():
        assert sha(ROOT/path) == digest, path
    assert sha(HERE/'review/art-kit-7.png') == sha(ROOT/'docs/screens/ui-v3/art-kit-7.png')
    assert Image.open(HERE/'review/art-kit-7.png').size == (1280, 1753)
    reviews = json.loads((HERE/'visual-review.json').read_text(encoding='utf-8-sig'))
    records = {r['path']: r for r in reviews['images']}
    required = [ROOT/m['png'] for m in manifest.values()] + list((HERE/'review').glob('*.png'))
    required += [ROOT/'docs/screens/ui-v3/art-kit-7.png']
    for path in required:
        key = path.relative_to(ROOT).as_posix()
        assert key in records and records[key]['opened'] is True, key
        assert sha(path) == records[key]['sha256'], 'Opened-image hash changed: '+key
    evidence = json.loads((HERE/'review-evidence.json').read_text())
    assert evidence['timeline']['required_width'] == 24
    assert evidence['banner']['banner_widths'] == [640, 420]
    for section in ('banner', 'timeline'):
        e = evidence[section]
        assert sha(ROOT/e['capture']) == e['capture_sha256']
    return dict(result='PASS', shipping_sprites=6, unique_sprite_guids=True,
                preserved_files=len(baseline), personally_opened_images=len(required),
                current_review_hashes=True, mirrored_contact=True,
                runtime_integration='Not tested; Claude owns wiring/native acceptance')


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
