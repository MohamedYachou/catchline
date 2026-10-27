"""Assemble unmodified before/after native frames and seal final evidence."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json, re

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'docs/screens/map11-kelp-forest-1'
FIX = BASE / 'fix'
LIFE = ROOT / 'docs/screens/kelp-life-1'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    LIFE.mkdir(parents=True, exist_ok=True)
    images = []
    for stage in ('sand-clearing', 'kelp-edge', 'post-line', 'sail-out'):
        for width, height in ((1440, 900), (844, 390)):
            name = f'{stage}-{width}.png'
            old, new = Image.open(BASE / name).convert('RGB'), Image.open(FIX / name).convert('RGB')
            assert old.size == new.size == (width, height), name
            pair = Image.new('RGB', (width * 2, height + 42), '#F4EFE3')
            draw = ImageDraw.Draw(pair)
            draw.text((12, 13), 'BEFORE - rejected sand read', fill='#173F57')
            draw.text((width + 12, 13), 'AFTER - raised bed, map-local optics and anchored life', fill='#173F57')
            pair.paste(old, (0, 42)); pair.paste(new, (width, 42))
            pair.save(FIX / f'compare-{name}')
            images.append(dict(path=name, size=list(new.size), sha256=sha(FIX / name),
                               beforeSha256=sha(BASE / name), comparison=f'compare-{name}'))
    for stage in ('kelp-edge', 'life-kelp-motion', 'post-line', 'life-otter'):
        for width, height in ((1440, 900), (844, 390)):
            name = f'{stage}-{width}.png'
            data = (FIX / name).read_bytes()
            (LIFE / name).write_bytes(data)
            assert Image.open(LIFE / name).size == (width, height)
    native_log = (FIX / 'native.log').read_text(errors='replace')
    assert 'MAP11 LIVE MOTION PASS' in native_log
    assert 'MAP11 NATIVE CAPTURES COMPLETE' in native_log
    assert not re.search(r'NullReferenceException|MAP11 native failed|Shader error|error CS', native_log)
    native_exit = json.loads((FIX / 'native-exit.json').read_text(encoding='utf-8-sig'))
    assert native_exit['exitCode'] == 0
    completed = (FIX / 'capture-complete.txt').read_text().splitlines()
    assert len(completed) == 14, len(completed)
    native_images = []
    for record in completed:
        name = record.split(' ')[0]
        width = int(name.rsplit('-', 1)[1].split('.')[0])
        size = [width, 900 if width == 1440 else 390]
        assert list(Image.open(FIX / name).size) == size, name
        native_images.append(dict(path=name, size=size, sha256=sha(FIX / name)))
    launch = json.loads((FIX / 'native-run.json').read_text(encoding='utf-8-sig'))
    launch_drift = [item for item in launch['inputs'] if not item['matchesMain']]
    assert all(item['path'].replace('\\', '/') == 'Assets/Scripts/Game/VoyageInterfaceVoyage.cs'
               for item in launch_drift), launch_drift
    drift = []
    for item in launch['inputs']:
        path = ROOT / item['path'].replace('\\', '/')
        if not path.is_file() or sha(path).upper() != item['sha256'].upper():
            drift.append(item['path'])
    assert not any(re.search(r'VoyageKelpLife.cs$|VoyageCliffsLife.cs$|Map11Capture.cs$|GullKelpForest[\\/]', p) for p in drift), drift
    receipt = dict(nativeExit=0, liveMotion=True, comparisonCount=8, images=images,
                   nativeImages=native_images, matchedLaunchInputs=sum(item['matchesMain'] for item in launch['inputs']),
                   totalLaunchInputs=len(launch['inputs']), launchMainDifferences=launch_drift, postCaptureMainDrift=drift,
                   lifeFrames=8, model='OtterRaft: two adults, one pup, static model with Floater',
                   supplementalCamera='life-otter only: evidence camera aims at raft; all comparison frames use player camera',
                   limits='Native Windows SessionOnly captures; no installed player or physical touch acceptance.')
    (FIX / 'evidence-verification.json').write_text(json.dumps(receipt, indent=2))
    print('MAP11 evidence integrity PASS: eight pairs, eight life frames, native exit0, live motion')

if __name__ == '__main__':
    main()
