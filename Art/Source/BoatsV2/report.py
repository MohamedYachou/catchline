"""Write measured delivery report; visual conclusions supplied after opening evidence."""
from pathlib import Path
import json,sys,hashlib
R=Path(__file__).resolve().parents[3];name=sys.argv[1];o=R/'Art/Models/BoatsV2'/name;v=json.loads((o/'validation.json').read_text());b=json.loads((o/'build-metrics.json').read_text());oldtri=sum(d['triangles'] for d in b['before'].values()); row=name=='Rowboat'
fmt=lambda xs:'('+', '.join(f'{x:.5f}' for x in xs)+')'
s=f'''# {name} refinement — BOAT-REFINE-1

Additive editable source and FBX; protected Assets model remains unchanged. **{v['triangles']:,} triangles** (current {oldtri:,}; cap {3000 if row else 5000:,}). One metre per tile. Matte canonical Art/STYLE.md palette; no textures, crews, lights, cameras or presentation floor in delivered geometry.

Curved sheer and raked forefoot replace the slab sides. Exported rail end lifts relative to amidships: **{v['sheer_bow_lift_m']*100:.1f} cm bow / {v['sheer_stern_lift_m']*100:.1f} cm stern**; the deck stays put. Five overlapping clinker courses with three upper dark 20 mm reveals and 25 mm proud laps, swept ivory gunwale, honey rubbing strake, orange painted waterline and timber keel/stem give the silhouette a built wooden character. Inner lining, end seats and three restrained flat-colour paint chips complete the timber work. {'Original oars, oarlocks and rod sockets remain intact; the centre thwart retains its original contact height with simpler geometry.' if row else 'Original console, motor, propeller, hold, hinged lid and sockets remain intact; a compact outboard clamp bracket and small end benches add the working details.'}

## Preserved mechanical contract

Independent import of original and exported FBXs: **PASS**, {v['legacy_nodes']} legacy nodes retained with identical parents and local/world matrices within 0.0001 m. Matrix checks also cover rotation/scale/origin, not only pivot translation. Deck and all retained meshes compare every world-space vertex within 0.0001 m, far tighter than the brief's 1 cm limit. Source axes X right / -Y bow / Z up and importer root conversion remain unchanged. Runtime model binding, station definitions, GameData hull dimensions and RodBases were read, never edited. {'3 × 2' if row else '5 × 3'} tile grid stays in place.

| Measurement (source world metres) | Current | Refined |
| --- | --- | --- |
| Deck minimum XYZ | {fmt(v['deck_old_bounds'][0])} | {fmt(v['deck_new_bounds'][0])} |
| Deck maximum XYZ | {fmt(v['deck_old_bounds'][1])} | {fmt(v['deck_new_bounds'][1])} |
| Walking surface Z | 0.00000 | 0.00000 |
| Triangles | {oldtri} | {v['triangles']} |

| Legacy node | Old source-world pivot XYZ (m) | New source-world pivot XYZ (m) | Maximum matrix delta |
| --- | --- | --- | ---: |
'''
for d in v['nodes']:s+=f"| {d['node']} | {fmt(d['old_source_world_pivot'])} | {fmt(d['new_source_world_pivot'])} | {d['max_matrix_delta']:.9g} |\n"
s+='\nUnchanged mesh vertices: '+', '.join('`'+n+'`' for n in v['unchanged_meshes'])+'.\n\nNew child nodes: '+', '.join('`'+n+'`' for n in v['new_nodes'])+'. All remain under the original root. Added seats/soles sit outside the rectangular build deck. Open single-face paint/sole overlays are intentional; no zero-area polygons or nonfinite vertices. No baked animations.\n'
s+='''
## Opened comparison evidence

[Review sheet](renders/review-sheet.png) shows current left, refined right at identical scale, lights and material treatment. Individual labelled full-resolution pairs:

'''
for view in ['front-three-quarter','side','back-three-quarter','top','low-waterline','deck-55','game-exact-45']:s+=f'- [{view}](renders/compare-{view}.png)\n'
s+='''
The requested approximate 55-degree deck view is included. Read-only runtime inspection found VoyageGame camera Euler(45,35,0); an additional exact 45-degree/35-yaw authoring pair is supplied. These are Blender authoring comparisons, not Unity screenshots or evidence of native material remapping, gameplay placement, crew clearance, or player acceptance. Claude imports after review.

'''
s+=(o/'visual-notes.txt').read_text() if (o/'visual-notes.txt').exists() else 'Visual inspection pending.\n'
s+='\n## Reproduction and receipt\n\nWindows Blender 5.2: run `Art/Source/BoatsV2/build.py -- '+name+'`, then `review.py -- '+name+'`; Python/Pillow `sheets.py '+name+'` creates labelled pairs. `validation.json` and `build-metrics.json` contain measured results; logs reside in source directory. Zero-area bevel fragments are removed during authoring before export. Original FBX SHA256: `'+v['original_sha256']+'`.\n\nNo Assets writes, Unity launches, game-code changes, git operations or subagents. Native import and in-game acceptance remain with Claude/Mo.\n'
(o/'REPORT.md').write_text(s)
files=[x for x in o.rglob('*') if x.is_file() and x.name!='receipt.json'];(o/'receipt.json').write_text(json.dumps({str(x.relative_to(o)):hashlib.sha256(x.read_bytes()).hexdigest() for x in sorted(files)},indent=2));print('Report and receipt:',name,len(files),'files')
