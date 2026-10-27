"""Recheck current PropsV2 receipts and compose the delivery overview. Needs Pillow.

Run from any directory: uv run --with pillow python <this-file>.
This verifies saved Blender evidence; it does not run Unity or rerender assets.
"""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
NAMES = [
    'JigRig', 'SpareRig', 'LanternOilCan', 'DeckLightPool',
    'JellyfishClump', 'FlyingFishEvent', 'GullSwoop', 'SealHead',
    'DolphinFin', 'InspectorLaunch', 'RivalBoat', 'SquallOverlay',
    'OffalPile', 'TableEel',
]
comparisons = 0
images = set()
checked_files = {}


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(path, expected):
    global comparisons
    actual = sha(path)
    assert actual == expected, str(path)
    comparisons += 1
    checked_files[path.relative_to(ROOT).as_posix()] = actual


def decode(path):
    with Image.open(path) as im:
        im.load()
        assert im.width > 0 and im.height > 0
    images.add(path.relative_to(ROOT).as_posix())


records = []
for i, name in enumerate(NAMES):
    folder = OUT / name
    m = read(folder / 'build-manifest.json')
    v = read(folder / 'validation.json')
    iteration = folder / 'iterations' / m['revision']
    s = read(iteration / 'delivery-snapshot.json')
    assert v['pass'] and m['revision'] == v['revision'] == s['revision']
    assert m['delivery_sha256'] == v['delivery_sha256'] == s['delivery_sha256']
    for file, digest in m['delivery_sha256'].items():
        check(folder / file, digest)
        if file.endswith('.png'):
            decode(folder / file)
    runtime = ROOT / m['runtime_file']
    ext = '.fbx' if m['kind'] == 'mesh' else '.png'
    assert v['runtime_sha256'] == m['delivery_sha256'][name + ext]
    check(runtime, v['runtime_sha256'])
    for source in m['provenance']:
        check(ROOT / source['file'], source['sha256'])
    for file, digest in s['source_sha256'].items():
        check(iteration / 'source' / file, digest)
        check(ROOT / 'Art/Source' / file, digest)
    for file, field in [('validation.json', 'validation_sha256'),
                        ('build-manifest.json', 'manifest_sha256'),
                        ('review-sheet.png', 'review_sha256')]:
        check(folder / file, s[field])
        check(iteration / file, s[field])
    check(iteration / 'REPORT.md', sha(folder / 'REPORT.md'))
    assert 'PROPSV2 AUDIT PASS ' + name + ' ' + m['revision'] in (iteration / 'audit.log').read_text()
    assert (iteration / 'build.log').is_file()
    assert set(v['render_sha256']) == set(m.get('render_files', []))
    for file, digest in v['render_sha256'].items():
        check(ROOT / file, digest)
        decode(ROOT / file)
    decode(folder / 'review-sheet.png')
    decode(iteration / 'review-sheet.png')
    record = {
        'name': name, 'plan': 'A5' if i < 4 else 'A6',
        'revision': m['revision'], 'kind': m['kind'],
        'runtime_file': m['runtime_file'], 'runtime_sha256': v['runtime_sha256'],
        'pivot': m['pivot'], 'placement': m.get('pivot_use', m.get('use')),
        'origin': m.get('origin', 'Named effect design derivative; PNG plus editable SVG.'),
        'checks': len(v['checks']), 'provenance': m['provenance'],
        'review_sheet': (folder / 'review-sheet.png').relative_to(ROOT).as_posix(),
        'render_files': m.get('render_files', []),
    }
    if m['kind'] == 'mesh':
        assert v['triangles'] == m['triangles'] == sum(m['mesh_parts'].values())
        assert v['mesh_count'] == len(m['mesh_parts'])
        assert v['max_vertex_error_m'] < .0001 and v['max_part_pivot_error_m'] < .0001
        record.update(triangles=v['triangles'], parts=v['mesh_count'],
                      bounds_source_m=m['bounds_source_m'],
                      max_vertex_error_m=v['max_vertex_error_m'],
                      max_part_pivot_error_m=v['max_part_pivot_error_m'])
    else:
        record.update(logical_size=m['logical_size'], alpha_max=v['alpha_max'])
    records.append(record)

font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
title = ImageFont.truetype(font_path, 30)
body = ImageFont.truetype(font_path, 19)
small = ImageFont.truetype(font_path, 15)
overview = Image.new('RGB', (1600, 2220), '#F4EFE3')
d = ImageDraw.Draw(overview)
d.text((24, 18), 'Catchline / PropsV2 / A5 + A6', font=title, fill='#173F57')
d.text((24, 65), '12 mesh pieces + 2 RGBA effects / actual delivery previews', font=body, fill='#173F57')
for i, r in enumerate(records):
    x, y = (i % 4) * 400, 108 + (i // 4) * 510
    folder = OUT / r['name']
    if r['kind'] == 'mesh':
        im = Image.open(folder / 'iterations' / r['revision'] / 'three-quarter.png').convert('RGB')
        im.thumbnail((400, 400))
        overview.paste(im, (x + (400 - im.width) // 2, y))
        metric = f"{r['triangles']:,} tri / {r['parts']} parts"
    else:
        im = Image.open(folder / (r['name'] + '.png')).convert('RGBA')
        im.thumbnail((360, 360))
        bg = Image.new('RGBA', (400, 400), '#173F57')
        bg.alpha_composite(im, ((400 - im.width) // 2, (400 - im.height) // 2))
        overview.paste(bg.convert('RGB'), (x, y))
        metric = ' × '.join(map(str, r['logical_size'])) + ' RGBA'
    d.text((x + 16, y + 409), f"{r['plan']} / {r['name']}", font=body, fill='#173F57')
    d.text((x + 16, y + 438), r['revision'] + ' / ' + metric, font=small, fill='#52636A')
    d.text((x + 16, y + 464), f"{r['checks']} saved audit checks PASS", font=small, fill='#52636A')
d.text((24, 2171), 'Art evidence only. Native import, materials, placement and event behaviour remain integration work.', font=small, fill='#173F57')
overview.save(OUT / 'overview.png')
decode(OUT / 'overview.png')

index = {'schema': 'catchline.propsv2.delivery.v1', 'items': records,
         'source_axes': '+X right / -Y front / +Z up',
         'fbx_axes': '-Z forward / Y up', 'units': 'metres',
         'native_acceptance': 'Not tested; art only, no Unity/code writes.'}
(OUT / 'delivery-index.json').write_text(json.dumps(index, indent=2) + '\n')
totals = {
    'items': len(records), 'mesh_items': 12, 'rgba_items': 2,
    'triangles': sum(r.get('triangles', 0) for r in records),
    'mesh_parts': sum(r.get('parts', 0) for r in records),
    'blender_checks': sum(r['checks'] for r in records),
    'sha256_comparisons': comparisons,
    'unique_png_decodes': len(images),
    'individual_render_images': sum(len(r['render_files']) for r in records),
    'max_vertex_error_m': max(r.get('max_vertex_error_m', 0) for r in records),
    'max_part_pivot_error_m': max(r.get('max_part_pivot_error_m', 0) for r in records),
}
audit = {'pass': True, 'totals': totals, 'checked_sha256': checked_files,
         'decoded_png_files': sorted(images),
         'index_sha256': sha(OUT / 'delivery-index.json'),
         'overview_sha256': sha(OUT / 'overview.png'),
         'reproducer_sha256': sha(Path(__file__))}
(OUT / 'delivery-audit.json').write_text(json.dumps(audit, indent=2) + '\n')
rows = '\n'.join(f"| {r['plan']} | [{r['name']}]({r['name']}/REPORT.md) | {r['revision']} | "
                 + (f"{r['triangles']:,} / {r['parts']}" if r['kind'] == 'mesh' else ' × '.join(map(str,r['logical_size'])) + ' RGBA')
                 + f" | {r['checks']} |" for r in records)
report = f'''# PropsV2 — A5 gear and A6 events art

All 14 named items delivered: 12 clean mesh sources/FBXs and 2 editable SVG/RGBA effects.
Preview: [overview.png](overview.png). Exact runtime paths, pivots, bounds and
read-only provenance: [delivery-index.json](delivery-index.json).

| Plan | Item | Revision | Triangles / parts, or pixels | Audit checks |
|---|---|---|---|---|
{rows}

Total: {totals['triangles']:,} triangles / {totals['mesh_parts']} mesh parts;
{totals['blender_checks']} Blender validation checks passed. Final integrity pass:
{comparisons} SHA256 comparisons and {len(images)} unique PNG decodes, including
{totals['individual_render_images']} individual angle/context renders, 28 current/revision sheets,
2 source effects and this overview. Per-item reports distinguish new work and
existing-kit derivatives. Original StationsV1/Art108 sources are read-only and hash checked.

Mesh validation opens the saved clean source and independently imports the actual
runtime FBX. Every world-space vertex is matched in both directions; every mesh
part origin, count, material assignment/colour, bounds and metre scale is checked.
Maximum vertex error: {totals['max_vertex_error_m']:.9g} m; maximum part-origin error:
{totals['max_part_pivot_error_m']:.9g} m (tolerance 0.0001 m).
Effect checks cover PNG/SVG hashes, runtime equality, dimensions, finite RGBA,
transparent corners and restrained opacity; pool monotonic fade / rain sparsity.
Final image openings are recorded per item in canonical `comms.md`; a numerical
pass is not a visual or native acceptance claim.

## Placement and integration

Sources use Z up and -Y front; FBXs export Y up and -Z forward, in metres.
JigRig origin is the rail-clamp contact. SpareRig, LanternOilCan, JellyfishClump,
OffalPile and TableEel use centred floor/contact origins. FlyingFishEvent and
GullSwoop retain airborne pose origins. SealHead, DolphinFin and InspectorLaunch
use local waterline zero. RivalBoat preserves its inherited deck-centre root and
all part pivots; suggested water plane is source Z=-0.32 m. Consult each manifest
before positioning; do not apply blanket floor recentering.

DeckLightPool is a 256-square warm transparent pool, suggested diameter 1 m.
SquallOverlay is a 1024×512 sparse rain sprite. Bind alpha/emission and lamp
behaviour in native integration. Review lights, cameras, floors and teal water
surfaces are excluded from delivered mesh sources/exports. Assets contain static
poses; event travel/animation is runtime work.

Native Unity import, lighting/material binding, live placement and event behaviour
remain untested. No Unity scenes, game C#, git operations, or Mo acceptance claim.
Runtime copies are new files under `Assets/Art/Models/PropsV2/`; existing kit files
and GUIDs were not replaced. Claude owns commits and integration.

Recheck receipts and regenerate this index/overview with:
`uv run --with pillow python Art/Models/PropsV2/audit_delivery.py`.
Independent Blender reproducer: `Art/Source/validate_props_v2.py -- --name <Item>`
via Blender background mode. Source/tool snapshots and audit/build logs live in
each item's current `iterations/<revision>/` folder. Older drafts remain history.
'''
(OUT / 'REPORT.md').write_text(report)
print('PROPSV2 DELIVERY PASS', json.dumps(totals), flush=True)
