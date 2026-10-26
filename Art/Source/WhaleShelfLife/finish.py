"""Build review sheets, report and hash receipt after individual manual image review."""
from pathlib import Path
import ast,hashlib,json
from PIL import Image,ImageDraw,ImageFont
S=Path(__file__).resolve().parent;R=S.parents[2];O=R/'Art/Models/WhaleShelfLife'
N=['Humpback','BlowSpout','KittiwakeFlock','BaitBall']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
A={n:json.loads((O/'metrics'/(n+'-audit.json')).read_text()) for n in N}
C=json.loads((O/'metrics/contract-audit.json').read_text());assert C['result']=='PASS'
for n,a in A.items():
 assert a['result']=='PASS'
 for ext in ('blend','fbx'):assert a['sha256'][ext]==C['items'][n]['sha256'][ext]==sha(O/(n+'.'+ext))
images=sorted(p for p in (O/'renders').rglob('*.png') if p.name not in ('review-sheet.png','clip-sheet.png','fix-water-sheet.png'));assert len(images)==57
review=json.loads((S/'opened-images.json').read_text());assert set(review['opened'])=={p.relative_to(O).as_posix() for p in images}
for p in images:
 assert review['opened_sha256'][p.relative_to(O).as_posix()]==sha(p),('image changed since opened',p)
 Image.open(p).verify()
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
def sheet(rows,path,height):
 im=Image.new('RGB',(1500,len(rows)*height),'#E9E3D8');d=ImageDraw.Draw(im)
 for i,(name,labels) in enumerate(rows):
  for j,label in enumerate(labels):
   p=O/'renders'/name/(label+'.png');tile=Image.open(p).convert('RGB');tile.thumbnail((296,height-30));x=j*300;y=i*height;im.paste(tile,(x+(300-tile.width)//2,y+28));d.text((x+4,y+5),name+' '+label.replace('action-',''),font=font,fill='#173F57')
 im.save(path)
sheet([(n,['three-quarter','front','right','back','top']) for n in N],O/'renders/review-sheet.png',270)
sheet([(n,['action-'+c+'-'+str(i) for i in range(5)]) for n in N for c in A[n]['animation']],O/'renders/clip-sheet.png',250)
sheet([('FixWater',[c+'-'+str(i) for i in range(5)]) for c in ('Surface','Fluke')],O/'renders/fix-water-sheet.png',270)
t='''# WHALE-SHELF-LIFE-ART-1

Codex 2 (WSL CLI), 2026-10-26. Four independent FBXs and editable metre-scale blends for Whale shelf. Source-art delivery: no Unity, Assets, meta, C# or git operations. All 37 affected evidence images reopened individually for this fix; the 20 accepted flock/bait images retain their previous individual review with unchanged hashes. Three final review sheets also reopened. Integration and native acceptance remain the lead's work.

## Import and fixed waterline contract

Blender X right, -Y forward, Z up; Unity X right, Y up, +Z forward. Scene scale 1 metre; FBX UnitScaleFactor 100. Object scales are one. Place the named top-level root at the water surface; do not bottom-align the mesh. Roots, armatures and Root bones remain fixed at every frame. Body/wing/fish bones animate within that frame. Each FBX contains one mesh, its named root, and an armature only where animated. No presentation floor, water, light, camera, oversized helper or shadow catcher is exported. Opaque flat palette materials, faceted normals, no external textures. Production material/shader binding is lead-owned.

Set animated importers to Legacy, enable animation, disable root motion. Public names are the final suffix of FBX take names, which may include an armature prefix and pipe. Explicitly assign the clip frame ranges and Loop/Once wrap modes below; custom FBX legacy/loop properties are hints, not importer configuration. Use the imported rig's Animation component. BlowSpout is static and needs no animation importer.

| Asset | Triangles / cap | Rest size Unity XYZ, metres | 30 fps clips (inclusive frames) |
|---|---:|---|---|
'''
for n,a in A.items():
 b=json.loads((O/'metrics'/(n+'-build.json')).read_text());clips='; '.join(f"{c}: 1–{v['source']['sample_frames'][-1]}, {v['source']['seconds']:g}s, "+('Loop' if v['source']['loop'] else 'Once') for c,v in a['animation'].items()) or 'static'
 t+=f"| {n} | {a['source']['triangles']} / {b['limit']} | "+' × '.join(f'{x:.3f}' for x in a['dimensions_unity_xyz_m'])+' | '+clips+' |\n'
t+='''
KittiwakeFlock's cap is 300 per bird: each is 192 triangles, three together 576 / 900. The flock's reported rest size includes its three different positions and heights, rather than an individual bird's size.

## Items and event transitions

**Humpback**: root `Humpback`, `HumpbackRig`, `HumpbackSkin`; bones Root, Body, Tail, Pectoral.L and Pectoral.R. A broad blunt head, dark slate faceted back, lighter throat facets, long pale pectorals with three knobbles each, a small swept dorsal and broad notched solid flukes. Full length 8.65m, pectoral span 6.36m. No flat fin cards.

Surface is a complete roll-up/roll-down event: starts and ends below water, exposing the back/dorsal to 0.904m and knobbly head to 0.743m. A forward pitch rolls through the crest and the left pectoral breaks the surface exactly once. Root and rig remain fixed. Blow holds the surface pose with gentle breath motion; trigger the separate plume in code. Fluke begins at that surface pose, lowers the head/front while bending the tail stock upward independently, holds the raised vertical flukes from 0.9 to 1.5s, then slips straight down and ends wholly underwater. These are individual Once events: Surface's submerged endpoint and Blow's surface start differ. To show an extended breath, blend from Surface near its exposed midpoint into Blow, then into Fluke; alternatively show Surface as its own complete event. Do not concatenate the full Surface then Blow without a transition. The longest clip is three seconds; no world travel is baked. The Fluke end pose remains under water on Clamp; deactivate below water before resetting a new event.

Revised actual FBX Fluke geometry rises to +3.033m and finishes wholly submerged (highest vertex -1.367m). Whole-clip lowest geometry is -7.276m relative to the fixed waterline root. The front arches down while the tail stock bends upward separately: the front body stays fully below water during the 0.6s tail hold, and the fluke plane is within 4.1 degrees of vertical. From 1.5s onward its horizontal position stays constant within 0.000001m as the tail descends. Pale underside faces make the goodbye silhouette readable from the deck camera. Keep the full animated envelope in mind for skinned-mesh bounds/culling, not only the rest bounds. This anchor-depth comparison is a placement guide, not a full seabed collision audit.

**BlowSpout**: root `BlowSpout`, mesh `RoundedVapour`. 3.077m high, a tapered narrow base and four rounded decimated-icosphere lobes forming a bushy split V/heart crown. 180 triangles; ivory with a cool shadow lobe. Alpha is exactly one on all exported materials; no transparency. Static, opaque authored material. Parent to the whale with local Blender (0,-2.6,+0.17)m, corresponding to Unity (0,+0.17,+2.6)m, as a starting blowhole offset. The Blow body moves only gently; fine adjustment or a body-bone attachment can follow the imported breath pose. Scale from the base and fade using the production shader/property block in code; runtime fading is not baked or supplied. Do not leave it visible through Fluke.

**KittiwakeFlock**: root `KittiwakeFlock`, `KittiwakeFlockRig`, `KittiwakeFlockSkin`; Root and Bird_1/2/3 with left/right wing bones. Three ivory gulls, mantle-grey backs, black wingtips and yellow bills, each 1.68m wingspan. Circle makes one full orbit in four seconds at a measured 3m radius; 120-degree spacing, different base heights, small height/wing motion. Each bird's head stays 2.280–3.511m above water. The full animated XY radius is wider than 3m because of wings. Leave about 4m horizontal clearance from the flock centre and more than 3.7m air clearance. The root stays at waterline centre, not bird altitude.

**BaitBall**: root `BaitBall`, `BaitBallRig`, `BaitBallSkin`; Root and FishRing_0/1/2. Twenty-four small solid diamond-bodied fish tiles, dark teal with muted silver facets, spread across a shallow approximately 3.3m patch. Swirl is a slow ±0.16rad (18.3-degree total arc) reversing swirl with asynchronous small ripples, exactly closing in two seconds. Fish remain 0.040–0.265m below the root at every frame. Native water transparency/occlusion controls the shimmer; do not lift the root to the fish mesh surface or the tiles will break above water. No continuous fast two-second revolution.

## Suggested Whale shelf placement

Read-only references: `Art/Models/Maps/GullWhaleShelf/REPORT.md`, its SeaV2 wide/top images, Whale road day capture and WhaleSpout_1 anchor capture. The shelf is 360 × 280m; Whale road is the deeper eastern area, away from the pale crown and shallow herring shelf. The orange cylinder in the anchor image is a marker, not an accepted wildlife silhouette. Terrain, map roots, navigation and anchors remain untouched.

Use existing Unity anchor positions:

| Anchor | Unity XYZ, m | Suggested use |
|---|---|---|
| WhaleSpout_1 | (107, -0.32, -48) | One whale event, facing +Z initially |
| WhaleSpout_2 | (118, -0.32, -44) | Alternate whale event position |
| GannetDive_1 | (-89, -0.32, -41) | Optional sparse feeding patch/flock, subject to existing gannet dressing |
| GannetDive_2 | (-79, -0.32, -38) | Alternate patch rather than doubling the nearby flock |

Whale anchors are only 11.7m apart: alternate them rather than putting both full whales there simultaneously. At WhaleSpout_1, the review composition offsets suggest BaitBall (103.5,-0.32,-46.7) and flock centre (102.2,-0.32,-50.3), all with identity rotation; these are local offsets converted to Unity axes. The flock can instead share the bait-ball centre for direct feeding. Check the actual boat sightline and cast area before choosing the final composition. Keep wildlife out of movement lanes, destination approach and hook/cast paths. These spots are composition proposals, not tested navigation placements.

The map report measures terrain under the whale anchors at approximately Y=-8.513 and -8.404, versus waterline Y=-0.32: about 8.19/8.08m depth. The revised 7.276m dive gives approximately 0.92/0.81m point-depth allowance. The whale spans several metres, so the integrating lead must still confirm clearance over its whole footprint and chosen heading. Do not move this full dive onto the 3.03m-deep GannetDive shelf. Bait and airborne flock can use that shallow area. WreckGulls_1 is above-water crown rock; it is not the waterline pivot for this flock. Use one calm wildlife family near the camera, with the whale as the large focal gesture.

## Render review and audits

Five true orthographic studio views per item (20), five frames for each of five clips (25), and house-water deck45 assembly at 1440×900 and 844×390 (2): the original 47 images plus ten new opaque-water Surface/Fluke samples (57 total). Changed 37 images reopened individually for this fix; accepted flock/bait evidence inherited unchanged from the previous review. The two assemblies share a horizontal world span; no viewport approximation or Unity acceptance claimed. Review plane #1C6E7E has partial transmission to expose the shallow fish patch; production water is not reproduced. Studio floors sit below geometry; action frames omit the floor so complete submerged poses can be inspected. Action frames share one camera across all clips per asset. The dense assembly demonstrates the set together, rather than prescribing spawn density. Contact sheets are additional evidence; full-size images remain beside them.

Actual exported FBXs independently reimported in Blender 5.2: triangle caps, finite used vertices/nonzero faces, exact hierarchy, palette, every-mesh physical bounds, unit scale, source/import polygon-surface parity and normalized skin weights PASS. Every integer frame checks fixed root/rig/Root bone and world root. Five sample deformations per clip match within 20 micrometres; both loops close within 20 micrometres. Separate all-frame semantic checks cover 3m bird orbit, per-bird triangles, underwater fish envelope, humpback envelope and opaque rounded 3.077m vapour size plus revised Surface/Fluke semantic assertions. See metrics/*-audit.json and contract-audit.json, which include final source/FBX hashes. No presentation geometry is exported.

visual-validation.json records actual opened-image inventory and observations. delivery-receipt.json seals source, assets, logs and evidence with SHA-256. Native Legacy import, production material binding/water, animation culling bounds, bird speed/whale scale in context, full-footprint seabed clearance, HUD, casting and navigation acceptance remain for Claude/Mo. No native check is claimed.

## Every actual exported mesh bound (Blender XYZ, metres)

| Asset / mesh | Minimum | Maximum | Triangles |
|---|---|---|---:|
'''
for n,a in A.items():
 for mn,row in a['imported']['mesh_bounds'].items():t+=f"| {n} / {mn} | {tuple(round(x,5) for x in row['world_min_m'])} | {tuple(round(x,5) for x in row['world_max_m'])} | {row['triangles']} |\n"
t+='\n## Full animated envelopes (Blender XYZ, metres)\n\n| Asset / clip | Minimum | Maximum |\n|---|---|---|\n'
for n in N:
 for clip,row in C['items'][n]['actual_fbx'].items():
  if isinstance(row,dict) and 'bounds_xyz_m' in row:t+=f"| {n} / {clip} | {tuple(round(x,5) for x in row['bounds_xyz_m'][0])} | {tuple(round(x,5) for x in row['bounds_xyz_m'][1])} |\n"
t+='\n## Authored sRGB palette\n\n| Material | Hex |\n|---|---|\n'
for n,col in json.loads((O/'metrics/Humpback-build.json').read_text())['palette'].items():t+=f'| {n} | {col} |\n'
t+='''
## Reproduce and ownership

`python3 Art/Source/WhaleShelfLife/run.py build <asset...>`, then `audit <asset...>`, then `render <asset...> Assembly`. Windows Blender5.2 installed locally. Run contract.py with the same Blender for all-frame semantics. finish.py uses `/home/mo/.venvs/catchline-ui/bin/python` after opened-images.json truthfully records the individual review. Accepted helper modules are read-only: OpenSeaLife/build.py, HarbourV2/audit.py, Skerries/render.py and their existing dependencies. No UI/browser/Lighthouse test applies to these offline 3D models. Design-stack/house-style guidance was read; no formal UI audit or native runtime acceptance claimed. No subagents, commit, player-save change, watchdog file, remaining temporary backup or abandoned Blender worker. Source and Models WhaleShelfLife directories are the entire implementation scope; canonical comms.md records checkpoints and handoff.
'''
(O/'REPORT.md').write_text(t)
visual={'task':'WHALE-SHELF-LIFE-ART-1','result':'PASS source-art manual visual review','required_images':57,'opened_images':review['opened'],'observations':review['observations'],'additional_opened':review.get('additional_opened',[]),'native_acceptance':False,'limits':['Isolated Blender evidence; no production water, HUD, cast or navigation acceptance.','Explicit Legacy importer and wrap binding required.','Whale anchor depth comparison is point-based, not whole-footprint collision acceptance.'],'review_sheets':['renders/review-sheet.png','renders/clip-sheet.png','renders/fix-water-sheet.png']}
(O/'visual-validation.json').write_text(json.dumps(visual,indent=2)+'\n')
for p in S.glob('*.py'):ast.parse(p.read_text())
paths=sorted([p for p in O.rglob('*') if p.is_file() and p.name!='delivery-receipt.json']+[p for p in S.rglob('*') if p.is_file() and '__pycache__' not in str(p) and '_fix-backup' not in str(p)])
receipt={'task':'WHALE-SHELF-LIFE-ART-1','owner':'Codex 2 (WSL CLI)','result':'PASS source art; native acceptance false','audit_results':{n:a['result'] for n,a in A.items()},'required_images':57,'sha256':{p.relative_to(R).as_posix():sha(p) for p in paths}}
(O/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert all(sha(R/n)==h for n,h in receipt['sha256'].items());print('WHALE SHELF SEALED',len(paths),'hashes',len(images),'required images')
