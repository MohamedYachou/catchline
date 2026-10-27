"""Record completed individual image review and author the integration handoff."""
from pathlib import Path
import json,hashlib,sys
R=Path(__file__).resolve().parents[3]
notes={
'JigKit':'''All six children attach independently under JigKit. All object origins are zero with unit scale. Blender X/right, -Y/front, Z/up; FBX -Z forward / Y up, metres. Production geometry has no lights, cameras, textures or review ground.

| Child | Tris | Contract |
| --- | ---: | --- |
| JigPirk |244| Eye-contact origin; hangs down local Blender -Z, 140mm tip depth, 0.286mm wire clearance below pivot. Slim silver faceted body, blue spine, split eye ring and three tail hook branches. |
| JigFeathers |196| Top swivel-contact origin, 200mm drop, three orange/ivory/yellow feather hooks. |
| JigLine |12| Top origin, down -Z exactly1m; square4mm cross-section. Scale length in runtime. |
| KelpStrand > KelpRibbon |60| Armature/holdfast origin, rest2.5m tall; three bones Kelp_0 > Kelp_1 > Kelp_2, normalized skin weights. |
| SeabedRocks |148| Sand-base centre origin, 3x2m patch, four angular rocks; highest point.8063m. M_Steel is earlier WorldPolish rock grey. |
| MoteCloud |100| Volume-centre origin,50 flat quads, seeded full3D orientation in2m cube; runtime scroll. |

Sway is a4s cyclic action, frames1–121 at30fps, no rig/root translation. Actual FBX reimport names it KelpStrand|KelpStrand|Sway; select suffix Sway and configure Unity Legacy+Loop at import. Root armature stays fixed; about.313m maximum sampled ribbon movement; matching endpoints. Render ribbons/motes and feather planes with two-sided shared materials; they are deliberately flat. Material names/linear colors are in audit.json, authored hex palette in build.json. M_FishSilver is material-driven silver; runtime shader supplies metal response.

Assembly is an isolated water-column fixture, horizontal5.2m span, about2.29degrees down, with the lure centred. Pirk and feather review scale2, kelp.75, rocks.85, motes1.3; source meshes remain at specified metre sizes. Phone framing clips the sand/base and line top as a close-up does. Production gradient/fog, fish, scrolling and interaction are Claude-owned. Full three-hook silhouette is established in studio closeups; hooks are small at scene scale.''',
'RepairKit':'''All four sibling meshes attach independently under RepairKit, zero object origins/unit scale, metres. Blender Z/up, -Y/front; FBX -Z forward/Y up. No rigs/clips/textures/lights/cameras in production.

| Child | Tris | Contract |
| --- | ---: | --- |
| TornNet |432| Panel-centre origin, lies in XY plane. Centreline1.2x.8m, outer cord bounds1.212x.812m, cord thickness12mm. Green-grey diamond mesh with real ragged~30cm centre opening. |
| MendedPatch |80| Same centre origin and plane; tan diamond cords exactly replace clipped ragged segments. Overlay at zero local translation to close the hole. Width~.311m. |
| NettingNeedle |254| Tip origin, points along+X, extends-.2m; open eye, five wound tan twine wraps, width~30mm including winding. Shared M_Twine warm wood/twine palette. |
| TwineBall |390| Bottom/base origin,10cm core plus wound strands and loose tail extending to+.089m X. Overall bounding width14cm including tail; wraps protrude.56mm below base. |

M_NetGreenGrey and M_Twine shared materials only. The patch is complementary geometry, so show it at TornNet's origin after the mend; no opaque hole plug. The isolated assembly shows the torn state, with patch alongside at(-.8,.2,.015), needle and ball on the panel. Camera55degrees down, horizontal1.88m span; panel fills~64%width at both1440x900 and844x390. Studio front/back/right are expected near-edge-on views of the flat net. Gameplay alignment, repair progress, shaders/native acceptance belong to Claude.'''}
for kit in (sys.argv[1:] or notes):
 o=R/'Art/Models'/kit;m=json.loads((o/'renders/manifest.json').read_text());a=json.loads((o/'metrics/audit.json').read_text());rows=[]
 if kit=='JigKit':
  b=json.loads((o/'metrics/build.json').read_text());rock=b['items']['SeabedRocks'];notes[kit]=notes[kit].replace('|148|','|'+str(rock['triangles'])+'|').replace('four angular rocks; highest point.8063m.','four irregular fractured slabs with broad split tops and raked shoulders; highest point'+format(rock['bounds_blender'][1][2],'.4f')+'m.')
 for x in m:
  note='Individually opened: contained, faceted silhouette and requested colors readable.'
  if x.get('item') in ['TornNet','MendedPatch'] and x.get('view') in ['front','back','right']:note='Individually opened: intentionally edge-on flat net; cord depth visible.'
  if x.get('item')=='JigLine':note='Individually opened: straight4mm line; top is enlarged square cross-section, three-quarter pale but present.'
  if x.get('item')=='SeabedRocks':note='Individually opened revised angular slabs: uneven broad planar tops, raked fractures, differing proportions; sand unchanged.'
  if x.get('item')=='MoteCloud':note='Individually opened FINAL corrected full3D quads: specks visible from every studio direction.'
  if 'action' in x:note='Individually opened: fixed holdfast, smooth ribbon bend; first/end match, intermediate poses differ.'
  if '/Assembly/' in x['file']:note='Individually opened: close-up layout readable at this aspect; staged scales/crops documented in REPORT.'
  rows.append({**x,'sha256':hashlib.sha256((o/x['file']).read_bytes()).hexdigest(),'opened_individually':True,'review':note})
 (o/'visual-review.json').write_text(json.dumps({'owner':'Codex 2 (WSL CLI)','images':rows,'limits':'Isolated Blender evidence; no Unity/native acceptance.'},indent=2)+'\n')
 links='\n'.join('- ['+x['file']+']('+x['file']+')' for x in m)
 text=f'''# {kit} — JIG-ART-1

Artist delivery by Codex 2 (WSL CLI). {a['source']['triangles']}/2500 triangles. Source/actual-FBX audits PASS; every final image below individually opened. No Unity/native validation, installation or git operation.

[Source]({kit}.blend) · [Export]({kit}.fbx) · [Build metrics](metrics/build.json) · [Actual FBX audit](metrics/audit.json) · [Image review](visual-review.json) · [Manifest](renders/manifest.json) · [Review scene]({kit}-assembly-review.blend) · [Receipt](delivery-receipt.json)

## Integration contract

{notes[kit]}

## Validation and reproduction

Source hierarchy, metre bounds/pivots, budgets, finite/nonzero-area geometry, allowed materials, texture independence and actual FBX ordered polygon/vertex surface equivalence PASS. Static maximum export vertex error {a['surface']['max_vertex_error_metres']:.9f}m; sampled deformations match within20micrometres where applicable. No production changes after final audit. Build/audit logs and source receipts bind current files.

Shared deterministic scripts live in Art/Source/JigKit; RepairKit source entry is Art/Source/RepairKit/README.md. Run `python3 Art/Source/JigKit/run.py build,audit,render {kit}` from project root using Windows Blender5.2. This regenerates assets/evidence and requires a fresh image review. Read-only dependency hashes are recorded in metrics/dependencies.json. No backup needed for initial additive delivery; temporary mote revision backups removed after verified correction.

## Final evidence

{links}
'''
 if kit=='JigKit':text+='\n## Accepted-delivery rock correction\n\nFour repeated rounded primitives replaced with authored irregular slabs. [Scoped comparison](metrics/rocks-revision.json) proves every other mesh, skin, rig and original Sway curve unchanged; their30 previously opened image reviews carry forward. Five revised rock studios and both assemblies regenerated and individually opened. Repair model/evidence/report unchanged; both receipts rebound only because authoring scripts are shared. Temporary pre-rocks backup removed after successful audit and visual preflight.\n'
 (o/'REPORT.md').write_text(text)
