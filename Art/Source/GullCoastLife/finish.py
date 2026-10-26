"""Package already audited source art; run after opening every final image."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,ast
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/GullCoastLife';S=Path(__file__).parent
names=['Cormorant','CormorantRock','Oystercatcher','OystercatcherGroup','ChannelMarkers','PotBuoyLine']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
audits={n:json.loads((O/'metrics'/f'{n}-audit.json').read_text()) for n in names}
for n,a in audits.items():
 assert a['result']=='PASS'
 for ext in ('blend','fbx'):assert a['sha256'][ext]==sha(O/f'{n}.{ext}'),(n,ext)
for p in S.glob('*.py'):ast.parse(p.read_text(),str(p))
def sheet(paths,cols,w,h,title,out):
 rows=(len(paths)+cols-1)//cols;im=Image.new('RGB',(cols*w,rows*h+40),'#142C35');d=ImageDraw.Draw(im);d.text((12,12),title,fill='#F3F0DC')
 for i,p in enumerate(paths):
  tile=Image.open(p).convert('RGB');tile.thumbnail((w,h-28));x=(i%cols)*w;y=(i//cols)*h+40;im.paste(tile,(x+(w-tile.width)//2,y));d.text((x+8,y+h-23),p.parent.name+' / '+p.stem,fill='#F3F0DC')
 im.save(out)
sheet([O/'renders'/n/'three-quarter.png' for n in names],3,400,360,'GULL COAST LIFE | six source-art exports',O/'renders/review-sheet.png')
sheet([O/'renders'/f'Assembly-{g}'/'deck-844.png' for g in ['HarbourMouth','KelpBank','Sandbar','RockyPoint','DeepChannel']],2,500,260,'GULL COAST LIFE | deck45 isolated assemblies / phone',O/'renders/assembly-sheet.png')
rows=[]
for n,a in audits.items():
 dims=' x '.join(f'{v:.3f}' for v in a['dimensions_unity_xyz_m']);rows.append(f"| {n}.fbx | {a['source']['triangles']} | {dims} | PASS |")
report='''# Gull coast life — GULL-COAST-LIFE-ART-1

Codex 2 (WSL CLI), 2026-10-26. Six source-art exports delivered for integrating lead review. No Unity, Assets, meta, runtime or map edits; no commit.

## Delivered assets

All dimensions below are Unity world X × Y × Z metres, rest pose; contact origin Y=0. Counts include every exported mesh. Bird caps are 600 and 400 triangles respectively.

| Export | Triangles | Bounds size (m) | Independent FBX audit |
|---|---:|---|---|
'''+ '\n'.join(rows)+'''

Each item has a same-name editable `.blend`; only the same-name `.fbx` is an import asset. `review-*.blend` and `renders/` are evidence, never import them as scenery. No presentation floor, water, review kelp, light or camera exists in the six FBXs. `metrics/*-audit.json` records every exported mesh and its source/import world bounds, hierarchy, geometry correspondence, palette and file hashes.

## Integration contract

Metres; Unity +Y up, +Z bird forward. FBX global unit factor 100 is the standard Blender metre export; import at scale 1 with unit conversion enabled, never multiply scene placement by 100. Roots have unit scale and remain at their contact/waterline origins. Apply placement at the actual map waterline, which may differ from zero.

- **Cormorant**: `Cormorant` root, `CormorantRig`, `CormorantSkin`. Seven bones: Root, Body, Head, Wing.L, Wing.R, Leg.L, Leg.R. Dark teal-black faceted feathers with pale throat, hooked horn bill, teal eyes and webbed feet. Source feather roughness .32; preserve a subdued gloss in the runtime material binding. Generic/Legacy rig, not Humanoid. Import clips as Legacy: Idle frames1–91, 3s loop; DryWings1–61, 2s loop; Dive1–31, 1s once. All sampled at30fps. FBX takes may be rig-prefixed by the importer: expose the short clip names above. DryWings holds both wings open with small flicks. Dive tips and lowers the body beneath water; root remains fixed. Hide/reset or return to Idle after Dive, rather than looping the sinking endpoint. No code-driven translation is baked into Root.
- **CormorantRock**: static two-bird group on approximately1m irregular warm-grey rock, sunk below the waterline. `CormorantRockBase`, `PerchedCormorant_1`, `PerchedCormorant_2`. Birds are .78 scale geometry baked into metres. Use the independent Cormorant rig for animated individuals; the grouped habitat has no clips.
- **Oystercatcher**: root/rig/skin follow the same naming pattern and seven-bone layout. Ivory belly and wing bars, dark body, long orange bill, pink legs. Legacy Walk1–31, 1s loop; Probe1–46, 1.5s loop. Walk is in place; translate the instance along dry sand in code if needed. Probe bends the body and lowers the bill. Root stays fixed, loops close exactly. No collider supplied.
- **OystercatcherGroup**: four static individuals on an irregular2x1m wet-sand patch, shallow skirt below contact. `WetSandBar`, `Forager_1..4`. For moving birds, hide/replace a static bird with an independent rig at its placement. Do not animate the whole sand patch.
- **ChannelMarkers**: root `ChannelMarkers`; child empties `RedCan` and `GreenCone`, local positions(-1.15,0,0) and(+1.15,0,0) in Unity metres. Each child origin is its own waterline pivot and owns its coloured mesh. Detach/reposition these children with world transform preservation; the2.3m display spacing is an assembly layout, not a prescribed navigable channel width. Bases extend .22m below water and lamps reach1.56m above. Red can/green cone also distinguish shape. Static; bob each child mildly in code. Only the small top lens uses `M_LampGlow` (#FFE7A3); bind emission/bloom at runtime. No baked light, halo, shadow catcher or floor.
- **PotBuoyLine**: waterline-centred root; three orange/ivory floats and slack curved rope. Overall rope envelope3.024m (3m centreline span plus tube radius); floats at X=-1.25,0,+1.25. Static rigid assembly: a small whole-root bob is safe; independent float displacement requires rope deformation by runtime. Do not stretch the line to fill a map.

Materials are named flat house-palette slots with no texture dependency. Main colours: feathers #25383C/#344D4A, ivory #F3F0DC, orange #E36A35, pink #C9857F, rocks #8E8A80/#6F6A61, wet sand #A69775/#8F856F, marker red #BF4F3D, green #477A56, rope #D1AF76. Runtime URP material binding remains lead-owned. Keep flat normals and opaque surfaces; no need for two-sided bird skins.

## Suggested spot per ground

Based on the five existing `Art/Models/Maps/Gull*/renders/SeaV2-wide-day.png` views, opened together in `Art/Source/GullCoastLife/map-references.png`. These are composition suggestions, not navigation-tested coordinates.

| Ground | Piece and suggested relationship to the rendered terrain |
|---|---|
| Harbour mouth | PotBuoyLine along the outside shoulder of the breakwater, parallel to its outer edge; leave the central approach and harbour entrance clear. |
| Kelp bank | PotBuoyLine just beyond the visible kelp-bed edge, orange/ivory against green water; offset from the fishing anchor and crossing routes. |
| Sandbar | OystercatcherGroup on the exposed long-bar shoulder, long axis following the sand contour. Sink its skirt into the existing sand and keep its feet above tide level. |
| Rocky point | CormorantRock beside a smaller outer rock, away from the main point silhouette; sink its base so the warm-grey facets join the existing reef. Independent Cormorants may perch on the original higher rocks. |
| Deep channel | Separate red/green marker children to opposite channel shoulders, downstream of the drop-off anchor; orient them as a channel pair while keeping the full navigation lane and casting area open. |

Lead must select final coordinates against actual terrain, HUD, navigation lanes, casts and tide/water shader. No fixed map coordinates or native placement acceptance are claimed here.

## Evidence and checks

`renders/<item>/` contains five views each (front, right, back, top, three-quarter), plus five samples per bird clip:25 action frames total. `renders/Assembly-<ground>/` contains all five ground assemblies at deck45,1440x900 and844x390,10 images total. Shared horizontal framing within each pair; isolated house teal water with asset at metre scale, not the production terrain/HUD. KelpBank's sparse background kelp is a review prop only. `review-sheet.png` and `assembly-sheet.png` provide quick review contacts. Every final image was opened by Codex 2; see visual-validation.json for exact inventory and manual observations.

Independent Blender FBX reimport checks passed for all six: triangle caps; finite nonzero faces; used vertices; every mesh bounds; complete vertex/polygon surface correspondence; material palette; hierarchy; metre units; normalized skin weights; all clips and source/import deformed surfaces at five samples; fixed Root at every integer frame; exact loop closure; terminal Dive fully below water. Audit tolerances are20 micrometres surface correspondence and2e-5m loop closure. The nested marker export initially failed a52mm surface test; disabling axis-space baking for that nested static hierarchy corrected it, and the final independent audit passes. Historical diagnostic is retained only as debugging evidence, not a final pass receipt.

Reproduce with Windows Blender5.2 via `python3 Art/Source/GullCoastLife/run.py build <names>`, then `audit`, then `render`; use ground names for assembly renders. Do not batchmode the main Unity project. `finish.py` seals source/model/audit/render SHA256 values after actual image inspection. No browser/HTML detector applies to native 3D assets; visual checks use rendered geometry. No formal Impeccable critique, independent reviewer or native runtime acceptance is claimed. Questions skipped: standing instruction requests autonomous delivery, with no unresolved art decision.
'''
(O/'REPORT.md').write_text(report)
images=sorted((O/'renders').rglob('*.png'));assert len(images)==67,len(images)
for p in images:
 im=Image.open(p);im.verify()
visual={'method':'manual opened final images with view_image; geometry and palette read against house style','opened_images':[p.relative_to(O).as_posix() for p in images],'verdict':'PASS source-art visual review','observations':['Cormorant long neck, throat patch and hooked bill readable; open wings and headfirst dive sampled.','Oystercatcher orange bill/ivory belly/pink legs distinct; four sand birds separate at deck45.','Angular warm-grey rock partially submerged; marker can/cone distinct; all three floats and slack rope read at844x390.'],'limits':['Isolated Blender evidence; no native Unity/HUD/navigation/water shader acceptance.','Grouped habitats static; only independent birds animate.','Orthographic side views intentionally align repeated elements; three-quarter/top show separation.']}
(O/'visual-validation.json').write_text(json.dumps(visual,indent=2)+'\n')
files=sorted([p for p in O.rglob('*') if p.is_file() and p.name!='receipt.json']+[p for p in S.rglob('*') if p.is_file() and '__pycache__' not in str(p)])
receipt={'task':'GULL-COAST-LIFE-ART-1','owner':'Codex 2 (WSL CLI)','native_acceptance':False,'audit_results':{n:a['result'] for n,a in audits.items()},'images':len(images),'sha256':{p.relative_to(R).as_posix():sha(p) for p in files}}
(O/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('SEALED',len(files),'files',len(images),'images; all six current FBX audits PASS')
