"""Finalize tier5 evidence only after opening the paired views."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/BoatsV2/Tier5DeepLines103'
v=json.loads((O/'validation.json').read_text());b=json.loads((O/'build-metrics.json').read_text());a=json.loads((O/'bounds-audit.json').read_text())
fmt=lambda xs:'('+', '.join(f'{x:.5f}' for x in xs)+')'
s=f'''# Tier5DeepLines103 — BOAT-REFINE-2 D

Trim-only delivery for the live tier-5 hull. Original hull, existing gunwale, painted band, plank deck, cabin, machinery and optional equipment geometry are retained. A narrow ivory cap follows the existing sheer, with a blue rubbing strip and two quiet dark surface courses. Two rail clamps become simpler faceted saddles with a steel retaining strap; all detail stays below the existing rail envelope. No hull rebuild or deck-footprint change.

Editable Blender source and independently reimported FBX: **{v['triangles']} triangles**, original {v['original_triangles']}, cap {v['triangle_cap']} (+40%). Source FBX unchanged. No Unity or installed-player acceptance claimed.

## Node and deck diff

All {v['legacy_nodes']} original names, parents and local/world matrices pass an independent original/export comparison at 0.0001 m tolerance (0.1 mm). Every world vertex of the {len(v['unchanged_meshes'])} retained meshes passes a bidirectional nearest-vertex comparison at that tolerance. Only `Deep 1 rail clamp` and `Deep 2 rail clamp` are replaced. New trim nodes are independent, identity-transform meshes. The source X-right / -Y-forward / Z-up authoring coordinates and FBX conversion are preserved. All node transforms, including rod sockets, rig/reel pivots, workers and placement anchors, remain stable.

| Measurement | Original | Exported |
| --- | --- | --- |
| Deck min XYZ | {fmt(v['deck_old_bounds'][0])} | {fmt(v['deck_new_bounds'][0])} |
| Deck max XYZ | {fmt(v['deck_old_bounds'][1])} | {fmt(v['deck_new_bounds'][1])} |
| Triangles | {v['original_triangles']} | {v['triangles']} |

| Original node | Original pivot XYZ | Exported pivot XYZ | Max matrix delta |
| --- | --- | --- | ---: |
'''
for n in v['nodes']:s+=f"| {n['node']} | {fmt(n['old_source_world_pivot'])} | {fmt(n['new_source_world_pivot'])} | {n['max_matrix_delta']:.9g} |\n"
s+='\nRetained mesh vertex sets: '+', '.join('`'+n+'`' for n in v['unchanged_meshes'])+'.\n\nNew nodes: '+', '.join('`'+n+'`' for n in v['new_nodes'])+'.\n'
s+='''
## Every-mesh bounds

Independent original/exported FBX world bounds in metres. No presentation floor, water-cut, proxy, shadow catcher, light or camera is exported. The original UnitScaleFactor=100 convention is preserved, without a compensating root scale100. Full mesh-local bounds, transforms, parents, materials and raw FBX properties are in [bounds-audit.json](bounds-audit.json).

| Every exported mesh | Original world min / max | Exported world min / max | Max span m |
| --- | --- | --- | ---: |
'''
for row in a['rows']:
 old=row['original'];new=row['exported'];ff=lambda x:fmt(x[0])+' / '+fmt(x[1])
 s+=f"| {row['name']} | {ff(old['world_bounds']) if old else 'new trim'} | {ff(new['world_bounds'])} | {row['world_span_max_m']:.5f} |\n"
s+='''
## Optional groups and materials

`OptionalRodModule`, `NetModule1`, `NetModule2`, `RawBuckets`, `RawIceCoolers`, `PreparedHold`, `PrepStation` and the two deep-line rig hierarchies remain separate and unchanged. Nothing is baked into an always-on combined mesh. Both comparison variants hide RawBuckets, NetModule2 and OptionalRodModule identically, displaying the original chosen production arrangement; all alternatives remain in the FBX and in the full geometry audit. Render visibility does not select the runtime configuration.

Existing M_* names are retained, including original duplicated-material suffixes such as M_SeaTeal.003. Existing ArtLibrary remapping removes the suffix before PaletteHex lookup. New trim uses M_RailIvory, M_HullBlue and M_ClinkerRecess, all already in PaletteHex; saddles use M_HullNavy/M_Steel. No new palette entry required, no textures added.

## Opened evidence

[Seven matched pairs](renders/review-sheet.png): current left, refined right, same union framing, shaders, studio lights and camera. These are authoring views, not game screenshots.
'''
for view in ['front-three-quarter','side','back-three-quarter','top','low-waterline','deck-55','game-exact-45']:s+=f'\n- [{view}](renders/compare-{view}.png)'
s+='\n\n'+(O/'visual-notes.txt').read_text()
s+='\n\n## Reproduction and handoff\n\nWindows Blender5.2.1: `build_tier5_trim2.py`, `review_tier5_trim2.py -- Tier5DeepLines103`, `bounds2.py -- Tier5DeepLines103`; existing Python `sheets.py Tier5DeepLines103` and `report_tier5_trim2.py`. All scripts/logs in Art/Source/BoatsV2. Protected source SHA256 `'+v['original_sha256']+'`; delivered FBX SHA256 `'+v['exported_fbx_sha256']+'`. `validation.json` binds node/deck/triangle audit, `receipt.json` hashes delivery.\n\nNo git/commit, Unity, production Assets, game code, player-save or watchdog changes for D; no subagents. Claude owns import/runtime acceptance. Legacy DayBoat and Tier5FisherV1 remain untouched under the revised brief.\n'
(O/'REPORT.md').write_text(s)
files=sorted(p for p in O.rglob('*') if p.is_file() and p.name!='receipt.json');(O/'receipt.json').write_text(json.dumps({str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2));print('REPORT RECEIPT',len(files))
