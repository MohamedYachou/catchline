raise RuntimeError('REJECTED recovery draft; never finalize these models. Original builders own corrections.')
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2]
for n in ['Pim','Dirk','Mira','Lise']:
    O=R/'Art/Models/CrewV2'/('Mira-sol' if n=='Mira' else n)
    m=json.loads((O/'build-manifest.json').read_text());v=json.loads((O/'validation.json').read_text());p=json.loads((O/'hairfix-preservation.json').read_text())
    assert m['revision']=='hair-strands-01' and v['revision']=='hair-strands-01' and v['all_passed'] and p['all_passed']
    for name,value in v['delivery_sha256'].items():assert hashlib.sha256((O/name).read_bytes()).hexdigest()==value,(n,name)
    (O/'REPORT.md').write_text(f'''# {n} — corrected hair coverage

Codex 1 (Windows app), 24 October 2026. Current delivery: **hair-strands-01**.
This supersedes the previous model revision for Mo's requested hair corrections.

Thin overlapping tapered strands now cover the temple gaps beneath the hat.
The original builder's Catmull-Rom curve construction is reused. Each added
lock has its own closed flattened cross-section and tip. No flat coverage patch
or new scalp shell is used. Mo rejected the earlier flat-patch draft; that draft
is not a delivery.
'''+('Lise also has 22 overlapping wavy strands behind and between the original curls, keeping the individual fine-strand appearance. Hair-only topology is reduced where needed to stay within the original budget.\n' if n=='Lise' else '\n')+f'''
Delivered: `{n}.blend`, `{n}.fbx`, existing unchanged textures, `{n}-review.png`.
Current geometry: **{m['triangles']:,} triangles**, below the 20,000 limit.
The correction is real Head-weighted geometry joined to the existing hair mesh.
No face, expression, hat, outfit, accessory or non-hair vertex/weight was changed.
Mira's earlier front-hair preservation statement applies to the archived r16;
the current revision intentionally adds temple hair as requested by Mo.

`hairfix-preservation.json` independently verifies exact unchanged non-hair
geometry, topology, material indices and weights, plus byte-identical textures.
`validation.json` and `hairfix-audit.log` verify the saved source and actual
FBX import: original 20-bone skeleton, all 11 original source actions, normalized
weights, 0.95m scalp, scale/pivot, texture resolution and 44 sampled poses.
Delivery hashes were rechecked after export.

Visual evidence is in `iterations/hair-strands-01/`: face, both temple close-ups,
rear hair, front, side, back, three-quarter, Idle and Walk.
`{n}-review.png` includes before/after and both-side/rear/pose evidence.
Selected renders do not establish every-frame collision clearance, Unity
integration, device performance or Mo's final visual acceptance.
Hair is rigidly attached to Head and has no secondary simulation.

Rebuild from project root using Blender 5.2:

```
blender -b --factory-startup --python-exit-code 1 --python Art/Source/fix_crew_hair_strands.py -- --name {n}
blender -b --factory-startup --python-exit-code 1 --python Art/Source/audit_crew_hair_coverage.py -- --name {n}
```

`iterations/hairfix-before/` is the immutable input source for this overlay,
and contains the previous report/receipts for provenance. It is a required
rebuild dependency. Earlier shared builders alone reproduce the earlier model;
run this overlay to reproduce the corrected delivery. Active roster builders,
shared rig and game Assets were not edited. No commit or native integration.
''')
    print(n,m['triangles'],'validated current delivery')
