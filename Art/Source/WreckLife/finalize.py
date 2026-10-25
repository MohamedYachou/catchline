"""Validate existing WRECK-LIFE-1 evidence, then bind the current delivery.

Does not author a visual-review record or invoke Blender/Unity.
"""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Art/Models/WreckLife'
SRC = ROOT / 'Art/Source/WreckLife'
NAMES = {'Gannet': 1500, 'DiveSplash': 300, 'CardinalBuoy': 700, 'HerringBoil': 400}
VIEWS = {'three-quarter', 'front', 'right', 'back', 'top'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def verify():
    dependencies = read(OUT / 'metrics/dependencies.json')
    for rel, digest in dependencies.items():
        assert sha(ROOT / rel) == digest, ('dependency changed', rel)
    expected_pngs = {}
    counts = {}
    for name, limit in NAMES.items():
        build = read(OUT / 'metrics' / (name + '-build.json'))
        audit = read(OUT / 'metrics' / (name + '-audit.json'))
        assert audit['result'] == 'PASS'
        assert build['triangles'] == audit['source']['triangles'] == audit['imported']['triangles'] <= limit
        counts[name] = build['triangles']
        for ext in ('blend', 'fbx'):
            assert sha(OUT / (name + '.' + ext)) == audit['sha256'][ext] == build['sha256'][ext], (name, ext)
        for step, marker in [('build', 'WRECK BUILT'), ('audit', 'WRECK AUDIT PASS'), ('render', 'WRECK RENDERS')]:
            log = (SRC / (name + '-' + step + '.log')).read_text(errors='replace')
            assert marker in log and 'Traceback' not in log, (name, step)
        manifest = read(OUT / 'renders' / (name + '.json'))
        studios = [r for r in manifest if 'action' not in r]
        assert len(studios) == 5 and {r['view'] for r in studios} == VIEWS
        assert all(r['projection'] == 'orthographic' and r['size'] == [720, 600] for r in studios)
        for row in manifest:
            assert row['file'] not in expected_pngs
            expected_pngs[row['file']] = row['size']
        if name == 'Gannet':
            for action, frames, seconds, loop in [('Glide', [1, 23, 46, 68, 91], 3., True), ('Dive', [1, 13, 25, 37, 49], 1.6, False)]:
                rows = [r for r in manifest if r.get('action') == action]
                assert [r['frame'] for r in rows] == frames
                assert all(r['size'] == [640, 480] and abs(r['seconds'] - (r['frame']-1)/30) < 1e-9 for r in rows)
                clip = audit['animation'][action]
                for version in ('source', 'imported'):
                    assert clip[version]['seconds'] == seconds and clip[version]['loop'] is loop
                    assert clip[version]['root_stationary_all_frames'] is True
                assert len(clip['samples']) == 5 and all(v['result'] == 'PASS' for v in clip['samples'].values())
            assert len(manifest) == 15
        else:
            assert len(manifest) == 5
    assembly = read(OUT / 'renders/Assembly.json')
    assert len(assembly['views']) == 2
    assert {tuple(v['size']) for v in assembly['views']} == {(1440, 900), (844, 390)}
    assert {p[0] for p in assembly['placements']} == set(NAMES)
    assert {(p[3], p[4]) for p in assembly['placements'] if p[0] == 'Gannet'} == {('Glide', 24), ('Dive', 49)}
    for row in assembly['views']:
        assert row['projection'] == 'orthographic' and row['horizontal_span_m'] == 10.24 and row['down_degrees'] == 45
        b = row['asset_projected_bounds_01']
        assert 0 <= b[0] < b[2] <= 1 and 0 <= b[1] < b[3] <= 1
        expected_pngs[row['file']] = row['size']
    log = (SRC / 'Assembly-render.log').read_text(errors='replace')
    assert 'WRECK RENDERS Assembly 2' in log and 'Traceback' not in log
    review = read(OUT / 'visual-review.json')
    assert len(review['images']) == len(expected_pngs) == 32
    assert {r['file'] for r in review['images']} == set(expected_pngs)
    assert {p.relative_to(OUT).as_posix() for p in (OUT/'renders').rglob('*.png')} == set(expected_pngs)
    for row in review['images']:
        p = OUT / row['file']
        data = p.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        assert list(struct.unpack('>II', data[16:24])) == row['size'] == expected_pngs[row['file']]
        assert row['opened_individually'] is True and row['review'] and sha(p) == row['sha256'], row['file']
    report = (OUT / 'REPORT.md').read_text()
    links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', report)
    for link in links:
        p = OUT / link
        assert p.is_file() or link == 'delivery-receipt.json', ('report link', link)
    for n in ('build', 'audit', 'render', 'run', 'finalize'):
        p = SRC / (n + '.py')
        compile(p.read_text(), str(p), 'exec')
    return {'result': 'PASS', 'triangles': counts, 'reviewed_pngs': 32, 'local_report_links': len(links), 'unchanged_dependencies': len(dependencies), 'limits': 'Blender source/actual-FBX and individual artist image review only; no Unity/native acceptance.'}


if __name__ == '__main__':
    import sys
    result = verify()
    if '--preflight' in sys.argv:
        print('WRECK PREFLIGHT PASS', json.dumps(result))
    else:
        assert not list(SRC.glob('temporary-*-backup')), 'Remove scoped temporary backups after successful preflight.'
        assert not list(OUT.rglob('*.blend1'))
        files = {}
        for base in (OUT, SRC):
            for p in sorted(base.rglob('*')):
                if p.is_file() and p.name != 'delivery-receipt.json' and '__pycache__' not in p.parts:
                    files[p.relative_to(ROOT).as_posix()] = {'bytes': p.stat().st_size, 'sha256': sha(p)}
        receipt = {'task': 'WRECK-LIFE-1', 'owner': 'Codex 2 (WSL CLI)', 'checks': result, 'dependencies_sha256': read(OUT/'metrics/dependencies.json'), 'files': files}
        path = OUT / 'delivery-receipt.json'
        path.write_text(json.dumps(receipt, indent=2) + '\n')
        reread = read(path)
        for rel, entry in reread['files'].items():
            p = ROOT / rel
            assert p.stat().st_size == entry['bytes'] and sha(p) == entry['sha256'], rel
        print('WRECK DELIVERY PASS', len(files), 'bound files;', result['local_report_links'], 'report links; receipt', sha(path))
