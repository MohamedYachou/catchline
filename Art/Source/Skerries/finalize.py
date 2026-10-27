"""Validate the reviewed SKERRIES-LIFE-1 artist delivery and bind its evidence.

No Blender/Unity launch or native acceptance claim. Run after audit + real review.
"""
import hashlib
import json
import re
import struct
from pathlib import Path

R = Path(__file__).resolve().parents[3]
O = R / 'Art/Models/Skerries'
D = R / 'Art/Source/Skerries'
NAMES = ('Seal', 'SealColony', 'SealSwimHead', 'ReefBreak_A',
         'ReefBreak_B', 'CrabBuoySet', 'PotStack')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    files = set()
    rows = {}
    pngs = set()
    for ext in ('blend', 'fbx'):
        assert {p.stem for p in O.glob('*.' + ext)} == set(NAMES)
    for name in NAMES:
        metric = O / 'metrics' / (name + '.json')
        manifest = O / 'renders' / (name + '.json')
        row = rows[name] = json.loads(metric.read_text())
        assert row['name'] == name and row['finite']
        assert row['round_trip']['result'] == 'PASS'
        assert row['round_trip']['geometry']['result'] == 'PASS'
        assert row['triangles'] < row['limit']
        for ext in ('blend', 'fbx'):
            p = O / (name + '.' + ext)
            assert p.stat().st_size > 0 and sha(p) == row['sha256'][ext], p
            files.add(p)
        images = json.loads(manifest.read_text())
        accepted = row['visual_review']['images']
        assert row['visual_review']['owner'] == 'Codex 2 (WSL CLI)'
        assert len(images) == len(accepted) == (27 if name == 'Seal' else 9)
        assert len({im['view'] for im in images}) == len(images)
        by_view = {im['view']: im for im in accepted}
        for im in images:
            accepted_im = by_view[im['view']]
            assert all(accepted_im[k] == v for k, v in im.items())
            assert accepted_im['review'] == 'individually opened; isolated artist review accepted'
            p = O / im['file']
            data = p.read_bytes()
            assert data[:8] == b'\x89PNG\r\n\x1a\n'
            assert struct.unpack('>II', data[16:24]) == tuple(im['size']), p
            assert sha(p) == accepted_im['sha256'], p
            assert p not in pngs
            pngs.add(p)
        for suffix, size in (('1440', [1440, 900]), ('844', [844, 390])):
            deck = by_view['deck-' + suffix]
            rod = by_view['rod-' + suffix]
            assert deck['size'] == rod['size'] == size
            assert deck['horizontal_span_m'] == 10 and deck['down_degrees'] == 45
            assert rod['eye_height_m'] == 1.7 and rod['down_degrees'] == 30
        for view in ('three-quarter', 'front', 'right', 'back', 'top'):
            assert by_view[view]['size'] == [720, 600]
        for step, marker in (('build', 'SKERRIES BUILT'),
                             ('audit', 'SKERRIES AUDIT PASS'),
                             ('render', 'SKERRIES RENDERS')):
            log = D / f'{name}-{step}.log'
            text = log.read_text(errors='replace')
            assert marker in text and 'Traceback' not in text, log
            files.add(log)
        files.update((metric, manifest))
    assert len(pngs) == 81 and set((O / 'renders').rglob('*.png')) == pngs
    files.update(pngs)

    tris = {n: row['triangles'] for n, row in rows.items()}
    budgets = {
        'Seal': [tris['Seal'], 2000],
        'SealColony+SealSwimHead': [tris['SealColony'] + tris['SealSwimHead'], 4000],
        'ReefBreak_A+ReefBreak_B': [tris['ReefBreak_A'] + tris['ReefBreak_B'], 600],
        'CrabBuoySet+PotStack': [tris['CrabBuoySet'] + tris['PotStack'], 2500],
    }
    assert all(actual < limit for actual, limit in budgets.values())
    animation = rows['Seal']['round_trip']['animation']
    assert set(animation) == {'Bask', 'Look', 'Slide'}
    poses = []
    for name, end in (('Bask', 121), ('Look', 91), ('Slide', 37)):
        a = animation[name]
        assert a['result'] == 'PASS'
        for side in ('source', 'imported'):
            assert a[side]['frames'] == [1, end]
            assert a[side]['seconds'] == (end - 1) / 30
            assert a[side]['quarter_vertex_displacement_max_m'] > .003
            if name != 'Slide':
                assert a[side]['end_vertex_displacement_max_m'] < .00002
            else:
                assert a[side]['end_vertex_displacement_max_m'] > 1.8
        checks = a['deformed_surface_checks']
        assert len(checks) == 5 and all(c['result'] == 'PASS' for c in checks.values())
        poses.extend(c['max_vertex_error_metres'] for c in checks.values())
        assert 'action-' + name + '-0' in {i['view'] for i in rows['Seal']['visual_review']['images']}
        assert (O / 'renders/Seal' / (name + '-contact-strip.png')) in pngs
    assert len(poses) == 15 and max(poses) < .00002
    baseline = json.loads((D / 'baseline.json').read_text())
    for path, expected in baseline.items():
        assert sha(R / path) == expected, ('protected reference changed', path)
    assert rows['PotStack']['contract']['source_sha256'] == baseline['Art/Models/Fishing/CageKit/CrabCage.blend']

    report = O / 'REPORT.md'
    links = re.findall(r'\]\(([^)]+)\)', report.read_text())
    # The generated receipt is the single forward link and intentionally excludes itself.
    for link in links:
        if link != 'delivery-receipt.json':
            assert (O / link).is_file(), ('broken report link', link)
    files.add(report)
    files.update(D.glob('*.py'))
    files.add(D / 'baseline.json')
    for path in ('Art/Source/build_crab_coast_props.py', 'Art/Source/HarbourV2/audit.py'):
        files.add(R / path)
    assert not list(O.rglob('*.blend1')) and not (D / 'review-backup').exists()
    proof = {
        'task': 'SKERRIES-LIFE-1', 'owner': 'Codex 2 (WSL CLI)', 'date': '2026-10-25',
        'result': 'PASS: artist source/actual-FBX/individually reviewed evidence integrity',
        'acceptance_limit': 'Isolated Blender artist review; Unity/native integration remains external',
        'models': list(NAMES), 'source_fbx_pairs': 7,
        'triangles': tris, 'strict_combined_budgets_actual_less_than_limit': budgets,
        'reviewed_png_count': len(pngs), 'sampled_animation_poses': len(poses),
        'max_animated_surface_error_metres': max(poses),
        'protected_references_sha256_unchanged': baseline,
        'report_links_checked': len(links),
        'files_sha256': {p.relative_to(R).as_posix(): sha(p) for p in sorted(files)},
    }
    target = O / 'delivery-receipt.json'
    target.write_text(json.dumps(proof, indent=2) + '\n')
    assert all(sha(R / path) == value for path, value in proof['files_sha256'].items())
    print('SKERRIES DELIVERY PASS', len(NAMES), 'pairs;', len(pngs), 'reviewed PNGs;',
          len(poses), 'poses;', len(files), 'hash-bound files;', len(links), 'report links')


if __name__ == '__main__':
    run()
