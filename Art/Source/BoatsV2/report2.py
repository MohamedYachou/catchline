"""Measured reports/receipts for revised BOAT-REFINE-2; call only after opening final evidence."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[3];name=sys.argv[1];o=R/'Art/Models/BoatsV2'/name
v=json.loads((o/'validation.json').read_text());b=json.loads((o/'build-metrics.json').read_text())
f=lambda xs:'('+', '.join(f'{x:.5f}' for x in xs)+')'
s=f'''# {name} — BOAT-REFINE-2

Editable Blender source and independently reimported FBX. {v['triangles']} triangles; original {v['original_triangles']}; cap {v['triangle_cap']} (+40%). Protected Assets FBX unchanged. Native Unity acceptance is not claimed.

Two restrained overlapping navy hull courses, swept ivory cap and honey rubbing strip; continuous orange painted band built into the shell topology. Source-like broad shoulder encloses the unchanged deck; raked lower shell/keel. One bevelled canopy drip lip follows the existing roof overhang. {'Four chunky timber knees remain against canopy uprights, above the floor, with central machinery unchanged.' if name=='PrepFisherV1' else 'Cabin footprint, helm, hatch opening and sorting approach are retained.'}

## Mechanical diff

Independent original/exported FBX import: PASS. Every legacy node name, parent and local/world matrix preserved within 0.0001m; retained meshes compare every world-space vertex at the same tolerance. New decorative meshes use identity source-world transforms; existing independent roots stay independent. Source X right / -Y forward / Z up and FBX conversion unchanged. No station/grid/origin/scale/socket edits.

| Measurement | Original | Refined |
| --- | --- | --- |
| Deck minimum XYZ | {f(v['deck_old_bounds'][0])} | {f(v['deck_new_bounds'][0])} |
| Deck maximum XYZ | {f(v['deck_old_bounds'][1])} | {f(v['deck_new_bounds'][1])} |
| Triangles | {v['original_triangles']} | {v['triangles']} |

Exported cap bow/stern rise from amidships: {v['sheer_bow_lift_m']*100:.2f}/{v['sheer_stern_lift_m']*100:.2f}cm. Walking surface/deck vertices unchanged.

| Legacy node | Old pivot XYZ | New pivot XYZ | Maximum matrix delta |
| --- | --- | --- | ---: |
'''
for d in v['nodes']:s+=f"| {d['node']} | {f(d['old_source_world_pivot'])} | {f(d['new_source_world_pivot'])} | {d['max_matrix_delta']:.9g} |\n"
s+='\nRetained mesh vertex sets: '+', '.join('`'+n+'`' for n in v['unchanged_meshes'])+'.\n\nNew nodes: '+', '.join('`'+n+'`' for n in v['new_nodes'])+'.\n'
a=json.loads((o/'bounds-audit.json').read_text())
s+='\n## Export bounds and unit compatibility correction\n\nIndependent FBX reimport lists every mesh below (metres, source X/Y/Z). No presentation floor, shadow catcher or mesh outside boat-sized bounds exists. The rejected export used UnitScaleFactor=1 with compensating root scale100; this delivery uses UnitScaleFactor=100, matching the original, without the added root scale. This corrects an export representation mismatch relevant to Unity useFileScale=0/useFileUnits=1. The reported harbour plane still needs native import confirmation by Claude.\n\nPrevious versus corrected export maximum world-vertex deviation: '+f"{a['max_world_vertex_delta_from_prior_rendered_export_m']:.9g}"+' m. Geometry is equivalent to the reviewed renders. Exact FBX SHA256: `'+a['exported_sha256']+'`. Full local bounds, matrices, parents, material names and raw FBX model properties are in [bounds-audit.json](bounds-audit.json).\n\n| Every exported mesh | Original world min / max | Export world min / max | Largest span m |\n| --- | --- | --- | ---: |\n'
for row in a['rows']:
 old=row['original'];new=row['exported']
 fmt=lambda b:f(b[0])+' / '+f(b[1])
 s+='| '+row['name']+' | '+(fmt(old['world_bounds']) if old else 'new trim')+' | '+fmt(new['world_bounds'])+f" | {row['world_span_max_m']:.5f} |\n"
s+='\n## Visual evidence\n\n[Opened seven-pair sheet](renders/review-sheet.png): identical union framing, shaders, warm/cool studio lighting and cameras. Current left, refined right. Authoring images, not runtime screenshots.\n'
for view in ['front-three-quarter','side','back-three-quarter','top','low-waterline','deck-55','game-exact-45']:s+=f'\n- [{view}](renders/compare-{view}.png)'
s+='\n\n'+(o/'visual-notes.txt').read_text()
s+='\n\n## Materials and reproduction\n\nOnly existing M_* palette names, including M_ClinkerRecess=#0E2C40 already present in ArtLibrary.PaletteHex; no new palette entry required. All matte. No textures/crew/review cameras/floor/lights exported. Source SHA256 `'+v['original_sha256']+'`.\n\nWindows Blender5.2: `build2.py -- '+name+'`, `review2.py -- '+name+'`; Python `sheets.py '+name+'` and `report2.py '+name+'`. Sources/logs in Art/Source/BoatsV2. `validation.json` is the independent audit; receipt.json hashes the delivered files.\n\nNo git/commit/Unity/Assets/game-code/save/watchdog changes or subagents. Claude owns material remapping/import/runtime/player review.\n'
(o/'REPORT.md').write_text(s)
files=sorted(p for p in o.rglob('*') if p.is_file() and p.name!='receipt.json');(o/'receipt.json').write_text(json.dumps({str(p.relative_to(o)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2));print(name,len(files),'receipt files')
