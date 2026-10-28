"""Validate the SERVICE-PROPS-2 handoff without Unity or modifying assets."""
import hashlib, json, re, struct
from pathlib import Path

O = Path(__file__).resolve().parent
R = O.parents[2]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name): return json.loads((O / name).read_text())

keys = ['Cook_Pan', 'Cook_Grill', 'Cook_FryerBasket', 'Cook_OvenTray',
        'Cook_SteamPot', 'Cook_SoupLadle', 'Cook_BreadBoard', 'Cook_Burnt',
        'TipCoins_S', 'TipCoins_L', 'CatchBoard', 'Ferry']
names = ['Restaurant_' + k for k in keys]
records = load('cooking-manifest.json')
assert [r['name'] for r in records] == names
review = {r['name']: r for r in load('cooking-visual-review.json')}
assert set(review) == set(names)
delivery = set()
for rec in records:
    name = rec['name']
    asset = R / rec['file']
    assert rec['render_review'].startswith('PASS') and sha(asset) == rec['sha256']
    expected_folder = 'cooking' if name.startswith('Restaurant_Cook_') else 'service'
    assert asset.parent == R / 'Assets/Art/Models/Restaurant/Pack' / expected_folder
    assert rec['tris'] < (1200 if expected_folder == 'cooking' else 4000 if name == 'Restaurant_Ferry' else 3000)
    meta = Path(str(asset) + '.meta')
    source = O / 'blends' / (name + '.blend')
    assert meta.is_file() and source.is_file()
    delivery.update([asset, meta, source])
    v = review[name]
    assert v['opened'] is True and len(v['frames']) == 2
    assert set(rec['renders']) == {f['file'] for f in v['frames']}
    assert rec['service_camera_pitch_deg'] == 38 and rec['close_camera_pitch_deg'] == 55
    for frame in v['frames']:
        path = R / frame['file']
        data = path.read_bytes()
        assert data[:8] == b'\x89PNG\r\n\x1a\n' and struct.unpack('>II', data[16:24]) == (1440, 900)
        assert frame['size'] == [1440, 900] and sha(path) == frame['sha256']
        delivery.add(path)

assert {p.stem for p in (R / 'Assets/Art/Models/Restaurant/Pack/cooking').glob('*.fbx')} == set(names[:8])
folder_meta = R / 'Assets/Art/Models/Restaurant/Pack/cooking.meta'
delivery.add(folder_meta)
guids = {}
metas = list((R / 'Assets').rglob('*.meta'))
for path in metas:
    m = re.search(r'^guid: ([a-fA-F0-9]{32})\s*$', path.read_text(errors='replace'), re.M)
    if m: guids.setdefault(m[1], []).append(path)
for path in [p for p in delivery if p.suffix == '.meta']:
    guid = re.search(r'^guid: ([a-fA-F0-9]{32})\s*$', path.read_text(), re.M).group(1)
    assert guids[guid] == [path], (path, guids[guid])

baseline = load('cooking-preservation-baseline.json')
assert all(sha(R / p) == h for p, h in baseline.items())
old_count = 0
for line in (O / 'source-and-evidence.sha256').read_text().splitlines():
    h, name = line.split('  ', 1)
    data = (R / name).read_bytes()
    if name == str((O / 'REPORT.md').relative_to(R)):
        data = data.split(b'\n# SERVICE-PROPS-2\n')[0]
    assert hashlib.sha256(data).hexdigest() == h, name
    old_count += 1

report = (O / 'REPORT.md').read_text().split('\n# SERVICE-PROPS-2\n')[1]
links = re.findall(r'\]\(([^)]+)\)', report)
for link in links:
    if link not in ['cooking-artifact-check.json', 'cooking-source-and-evidence.sha256']:
        assert (O / link).exists(), link

for filename in ['cooking-audit.json', 'cooking-source-audit.json']:
    audit = load(filename)
    assert audit['status'] == 'PASS' and {i['name'] for i in audit['items']} == set(names)
for rec in load('cooking-source-audit.json')['items']:
    assert sha(O / rec['source']) == rec['sha256']

# Exclude the inventory itself, this result, and mutable build progress to avoid cycles.
for pattern in ['*cooking*.py', 'inspect_board*.py', 'inspect_service_contacts.py', 'station_preview.py',
                'cooking-*.json', 'cooking-*.log', 'service-contact*.json', 'service-contact*.log']:
    delivery.update(O.glob(pattern))
delivery.difference_update([O / 'cooking-artifact-check.json', O / 'cooking-build-progress.json'])
delivery.update([O / 'REPORT.md', O / 'renders/cooking-stations-inspection.png'])
inventory = O / 'cooking-source-and-evidence.sha256'
inventory.write_text(''.join(sha(p) + '  ' + str(p.relative_to(R)) + '\n' for p in sorted(delivery)))
result = dict(status='PASS', assets=12, production_blends=12, opened_frames=24,
              frame_size=[1440, 900], all_triangle_budgets_pass=True,
              unique_delivery_guids=13, scanned_assets_metas=len(metas),
              preserved_dependencies=len(baseline), preserved_service_props1_inventory_entries=old_count,
              old_report_prefix_preserved=True, resolved_report_links=len(links),
              sealed_files=len(delivery), inventory=str(inventory.relative_to(O)),
              native_Unity_acceptance='Not run; Claude integration scope',
              git_commands=False, subagents=False)
(O / 'cooking-artifact-check.json').write_text(json.dumps(result, indent=2) + '\n')
assert all((O / link).is_file() for link in links)
print(json.dumps(result, indent=2))
