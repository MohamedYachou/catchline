"""Seal technical delivery and reviewed image evidence. Run with project Pillow venv."""
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/KelpLife';S=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
names=('SeaOtter','OtterRaft','KelpMat');audits={n:read(O/'metrics'/f'{n}-audit.json') for n in names}
rows=[]
for n in names:
    a=audits[n];assert a['result']=='PASS'
    for ext in ('blend','fbx'):assert sha(O/f'{n}.{ext}')==a['sha256'][ext]
    manifest=read(O/'renders'/f'{n}.json');assert len(manifest)==(20 if n=='SeaOtter' else 5)
    for v in manifest:
        p=O/v['file']
        with Image.open(p) as im:assert list(im.size)==v['size'];im.verify()
        rows.append({'file':v['file'],'size':v['size'],'sha256':sha(p),'opened_and_reviewed':True})
assembly=read(O/'renders/Assembly.json')
for v in assembly['views']:
    p=O/v['file']
    with Image.open(p) as im:assert list(im.size)==v['size'];im.verify()
    rows.append({'file':v['file'],'size':v['size'],'sha256':sha(p),'opened_and_reviewed':True})
assert len(rows)==32
text='''# KelpLife — KELP-LIFE-ART-1

Codex 2 (WSL CLI). Source-art technical delivery; Unity import and production-water acceptance belong to the integrating lead. No Assets, meta, C#, Unity or git changes.

## Integration contract

One FBX and authoring blend per item. Metres, scale 1, fixed root at water contact, Unity Y up, adult head toward Unity +Z (Blender -Y). Raw FBX UnitScaleFactor=100 verified independently for all three files. Transforms are baked; no presentation floor, camera, light, hidden oversized mesh or texture in any FBX. Every mesh world bound is recorded below and in metrics.

| Item | Triangles | Unity XYZ dimensions, m | Use |
|---|---:|---|---|
'''
for n in names:
    a=audits[n];text+=f"| [{n}]({n}.fbx) | {a['source']['triangles']} | "+' × '.join(f'{x:.3f}' for x in a['dimensions_unity_xyz_m'])+' | '+{'SeaOtter':'Single animated adult, cap 700','OtterRaft':'Static group: two adults and one 47% pup on adult chest','KelpMat':'Static fallback / extra dressing; no animals'}[n]+' |\n'
text+='''
Place root at the visible water surface. The otter torso crosses the waterline; do not ground its belly on the surface. Raft footprint is 3 × 2 m, standalone mat 2.5 × 1.6 m, each with 15 narrow olive-to-green softly curved ribbons and exactly two bulbs. OtterRaft contains three animals total. Its meshes AdultA, AdultB and Pup are baked static; gently bob the whole root if desired. Individual animated behaviour uses SeaOtter, not the static raft.

### Legacy animation setup

Import SeaOtter as Legacy, 30 fps. Name the runtime clips Float, Groom and Dive, selecting the matching FBX action suffix if the importer exposes rig prefixes. Actual round-trip action names are recorded in the audit. No root motion: object root, rig and Root bone remain stationary every frame. Body bone supplies local movement.

| Runtime clip | Source frames | Duration | Wrap | Behaviour |
|---|---|---|---|---|
| Float | 1–121 | 4 s | Loop | Paws to chest, 12 mm bob, gentle 5° roll |
| Groom | 1–61 | 2 s | Loop | Short paws lift and rub face, small head motion |
| Dive | 1–37 | 1.2 s | Once | 180° roll, Body sinks 1.05 m below fixed root |

Both loop endpoints close within audit tolerance. Dive finishes wholly below the waterline; hide/despawn or reset before returning to Float. No animated water or wake is included. Runtime blending and timing require native acceptance.

### Materials

Opaque matte flat house colours; no texture dependencies. Use **two-sided rendering for the thin kelp ribbons**. Animal geometry is closed faceted mesh. Reuse incumbent MAP11-compatible shading/material bindings as appropriate, preserving these base colours.

| Material | sRGB hex |
|---|---|
| M_OtterBrown | #705040 |
| M_OtterCream | #C8C3AF |
| M_OtterPaw | #50392E |
| M_Rubber | #28343B |
| M_KelpGreen | #3D573B |
| M_KelpGold | #536D3D |
| M_KelpBulb | #8C7949 |

## Evidence and checks

All **32 individual images were opened**, including five orthographic views per item, five sampled poses per clip and the assembly pair. Warm brown body, cream-grey face/chest, round ears, dark eyes/nose and short chest paws checked. Three animals/pup placement, fifteen loose ribbons/two bulbs, no rectangular mat slab, silhouette and full framing checked. Front/side mat views are intentionally thin at water level. Action samples share framing wide enough to retain the entire dive.

- [SeaOtter five views and 15 clip samples](renders/SeaOtter/three-quarter.png); [pose manifest](renders/SeaOtter.json).
- [OtterRaft five views](renders/OtterRaft/three-quarter.png); [manifest](renders/OtterRaft.json).
- [KelpMat five views](renders/KelpMat/three-quarter.png); [manifest](renders/KelpMat.json).
- [Deck assembly 1440×900](renders/Assembly/deck-1440.png), [844×390](renders/Assembly/deck-844.png), [assembly provenance](renders/Assembly.json).

Assembly is a source-only 45° deck-camera fixture on simple teal water, with six original connected MAP11 fronds copied from RootedForestPatch_KelpSway_1, translated as one local cluster beside the raft. No peer terrain was modified. Initial fixture used an obsolete mesh name, then an entire overly broad cluster and submerged its visible tips; corrected by selecting six original fronds and preserving their original geometry/materials. Final pair opened again. This is composition evidence, not production water/HUD/native acceptance. Review blend is a separate non-delivery fixture.

Independent source→actual-FBX checks passed: triangle caps, finite nonzero faces, used vertices, rigid unit scales, root/hierarchy parity, full every-polygon topology/vertex parity (20 μm tolerance), palette round-trip, normalized skin weights, all three action frame ranges/durations, five deformed samples each, loop closure, stationary root every integer frame and submerged Dive endpoint. Export source hashes verified. Raw FBX metre convention checked. Audits include actual imported names, motion distances and every-mesh bounds; no claim of Unity or player acceptance.

## Every exported mesh bound

Unity XYZ metres, rest pose, min / max. Source and imported bounds agree within audited tolerance.

| Item / mesh | Minimum | Maximum |
|---|---|---|
'''
for n in names:
    for mesh,b in audits[n]['source']['mesh_bounds_unity'].items():
        text+=f'| {n} / {mesh} | '+ ' | '.join('('+', '.join(f'{v:.5f}' for v in side)+')' for side in b)+' |\n'
text+='''
## Reproduction

From project root: `python3 Art/Source/KelpLife/run.py build,audit,render SeaOtter OtterRaft KelpMat`, then `python3 Art/Source/KelpLife/run.py render Assembly`. Runner invokes installed Windows Blender 5.2 with explicit success markers/logs, never Unity. Source depends on existing read-only crab-coast geometry helper and Harbour/Skerries audit/render helpers. Assembly additionally reads current MAP11 blend; its SHA is sealed in the manifest, so future terrain edits may change fixture appearance without changing delivered FBXs.

`/home/mo/.venvs/catchline-ui/bin/python Art/Source/KelpLife/finish.py` seals dimensions, image readability, export hashes and receipt. Visual review is manual and recorded in the receipt; image decoding alone is not visual acceptance. No backups remain, no subagents, no commit.
'''
text+='''
## KELP-RIBBON-FIX — 2026-10-26

Only OtterRaft and KelpMat were revised: fifteen narrow, nine-segment ribbons with soft compound waves, tapered tips and darker olive-to-green colours. All ten revised item views and both assembly views opened individually. The six broad MAP11 fronds on the assembly right remain an unchanged read-only reference. SeaOtter and its twenty previously accepted images were not redelivered. Exact AdultA/AdultB/Pup local vertices, faces, material slots and face-material indices match the retained pre-fix canonical SHA256 baselines; see metrics/ribbon-fix-otters.json. Both revised FBXs independently passed the full geometry/unit/footprint audits. Temporary replacement backups removed after verification.
'''
(O/'REPORT.md').write_text(text)
receipt={'task':'KELP-LIFE-ART-1','owner':'Codex 2 (WSL CLI)','technical_result':'PASS','native_acceptance':'Not run / integrating lead','images':rows,'visual_review':'All32 opened individually. Otter shape/palette/paws/loop samples/dive checked; raft has2adults+1pup; mat loose15ribbons+2bulbs; final assembly pair shows actual6MAP11fronds beside raft.','files':{p.relative_to(R).as_posix():sha(p) for p in sorted([*(O.glob('*.fbx')),*(O.glob('*.blend')),*(O/'metrics').glob('*.json'),*(S.glob('*.py')),O/'REPORT.md',*(O/'renders').glob('*.json')])}}
(O/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('KELP DELIVERY PASS',len(rows),'opened image records, export hashes and dimensions')
