from pathlib import Path
import json,hashlib,ast
from PIL import Image,ImageDraw,ImageFont
S=Path(__file__).resolve().parent;R=S.parents[3];O=R/'Art/Models/BoatsV2/Tier6V1';P=O/'renders'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
v=read(O/'validation.json');b=read(O/'bounds-audit.json');m=read(O/'build-metrics.json');c=read(S/'card-validation.json')
assert v['pass'] and v['full_surface_audit']['result']=='PASS' and not v['walkway_obstacles'];assert v['fbx_sha256']==sha(O/'Tier6V1.fbx')==b['fbx_sha256'];assert c['sha256']==sha(R/c['asset'])
# Check connected access graph, including side passages and every required work location.
walk=v['walkways'];adj=lambda a,b:all(a['min'][i]<=b['max'][i]+1e-5 and b['min'][i]<=a['max'][i]+1e-5 for i in range(2));seen={0}
while True:
 nxt={j for i in seen for j,w in enumerate(walk) if adj(walk[i],w)}|seen
 if nxt==seen:break
 seen=nxt
assert len(seen)==len(walk),(len(seen),len(walk))
for n,d in m['objects'].items():
 if 'Worker' not in n and 'Access_' not in n and not n.startswith('CrewStand_'):continue
 p=[d['world'][i][3] for i in range(3)];assert any(all(w['min'][i]<=p[i]<=w['max'][i] for i in range(2)) for w in walk),(n,p)
# Independently reconstruct the alpha-preserving card export.
master=Image.open(S/'card-master.png');card=Image.open(R/c['asset']);assert master.mode=='RGBA' and card.mode=='RGBA' and card.size==(480,360)
crop=master.crop(master.getchannel('A').point(lambda x:255 if x>8 else 0).getbbox());crop.thumbnail((432,312),Image.Resampling.LANCZOS);expected=Image.new('RGBA',(480,360));expected.alpha_composite(crop,((480-crop.width)//2,(360-crop.height)//2));assert expected.tobytes()==card.tobytes()
a=card.getchannel('A');assert a.getextrema()==(0,255) and all(a.getpixel(p)==0 for p in [(0,0),(479,0),(0,359),(479,359)])
views=['front-three-quarter','side','back-three-quarter','top','low-waterline','deck-55','game-exact-45','lineup-top','lineup-three-quarter'];images=[]
for n in views:
 p=P/(n+'.png');im=Image.open(p);assert im.size==((1600,1000) if n.startswith('lineup') else (1000,750));im.verify();images.append({'file':p.relative_to(O).as_posix(),'size':list(Image.open(p).size),'sha256':sha(p),'opened_and_reviewed':True})
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',21)
sheet=Image.new('RGB',(1500,1240),'#E9E3D8');draw=ImageDraw.Draw(sheet)
for i,n in enumerate(views):
 im=Image.open(P/(n+'.png')).convert('RGB');im.thumbnail((490,365));x=i%3*500;y=i//3*410;sheet.paste(im,(x+(500-im.width)//2,y+35));draw.text((x+12,y+8),n,font=font,fill='#173F57')
sheet.save(P/'review-sheet.png')
text='''# TIER6-BOAT-1 — Shelter Boat C

Codex 2 (WSL CLI). Source-art delivery only. Mo selected C, about10m, fitted with every earlier tier's fishing station. No Unity, Assets, metas, C# or git changes. Integrating lead owns game grid, placement/interaction coordinates, import palette bindings and native HUD/water/navigation acceptance.

## 0. Inventory and A. Fitted concept

Before modelling, every object from the four accepted authoring blends was inventoried: Tier5DeepLines103141nodes, PrepFisherV190, CompactFisherV133 and JigBoatV144. Full tables remain appended to ../Tier6/REPORT.md; bounds/hierarchy/source hashes are in Art/Source/BoatsV2/Tier6/station-inventory.json. All sources are read-only. The fitted painted concept Art/Source/BoatsV2/Tier6/concept-C-fitted.png has side/threequarter/top, fourteen equipment labels and crew routes. Prompt and reference retained. It is an illustrative schematic; the final audited coordinates and ten crew points below supersede its eight drawn circles.

## B. 3D and integration contract

Tier6V1.blend and Tier6V1.fbx. Hull nominal10m x5m: widened to retain the full inherited equipment kit with connected walkways. Navy clinker hull with swept sheer, three recessed laps, orange waterline band, ivory cap, warm planked deck; enclosed forward ivory wheelhouse and a long navy shelter roof over the preparation area. Two outboard buoy winch/booms, four rod holders, two articulated deep-line rigs, rear+side nets, full prep/raw/prepared storage, three jig reels, eight warm bulbs/cable and sorting tray. Ten crew stand nodes exceed Buoy fisher's eight berths. Runtime crew capacity is not changed by this art delivery.

Metres, scale1, source X right/-Y bow/Z up, fixed deck/root z0. Raw FBX UnitScaleFactor100, no space bake, FBX_SCALE_UNITS; same corrected Jig exporter contract. FBX Blender reimport restores original coordinates; Unity maps -Y to +Z. Every node remains beneath Catchline_Tier6V1. Every semantic equipment name is preserved, including rig/reel pivot parents. Rods for regular holders remain runtime equipment; no duplicate RodVisual meshes. Deep-line poles and jig reels are visible delivered geometry.

RawBuckets is a separate pair of actual stowed buckets rather than Tier5's coincident alternative cooler meshes; RawIceCoolers and PreparedHold retain their named source component hierarchies. Both variants can be toggled by their respective roots; lead should decide which runtime storage presentation to show. BuoyRig_1/2 are additional visible static winch/booms; BuoyAnchor_1/2 remain waterline hook positions for runtime buoy/pot visuals. Prepared hold and raw input aliases from Prep are retained with current storage coordinates. OptionalRodModule remains separate. No catch animation, runtime collision or navigation data is included.

'''
text+=f"**{v['triangles']:,}tri /18,000 cap; {v['mesh_count']}meshes, {v['node_count']}nodes.** Independent source/FBX every ordered polygon-cycle/multiplicity comparison PASS, max vertex error {v['full_surface_audit']['max_vertex_error_metres']:.9f}m; hierarchy/material palette/source scale/world matrices and all57required semantic names PASS. Every mesh bounded independently; no presentation plane, hidden giant mesh, camera, light or texture exported. Degenerate zero-area faces in carried source bevels removed in the new asset only.\n\n"
text+='''### Crew access

Actual exported polygons clipped against every human-clearance prism (z.045–1.65m). Main spine0.90m wide; cabin side passages0.72m; cabin cross passage0.70m; task access branches0.70m. Zero intersecting obstacle polygons. Connected prism graph checked; every Worker, Access and CrewStand node lies inside the network. The walkable deck is solid and flat atz0, centre hatch essentially flush. Roof underside1.70m clears tested crew height1.65m. Clearance is source geometry proof, not a Unity grid/pathfinding test: lead must adapt grid and crew routes to these coordinates, not reuse old hull grids blindly.

| Required semantic node | Source XYZ, m | Parent |
|---|---|---|
'''
for n in v['semantic_names_verified']+[f'CrewStand_{i}' for i in range(1,11)]:
 d=m['objects'][n];text+=f"| {n} | "+str(tuple(round(d['world'][i][3],4) for i in range(3)))+f" | {d['parent']} |\n"
text+='''
### Materials

All inherited station slots kept, including source suffixes when Blender distinguishes duplicate materials. Preserve actual FBX slot names when binding; do not assume a suffix indicates a new intended colour. M_JigBulb comes from accepted Jig lights and needs the same warm bulb runtime emission binding; separate JigLampGlow is not duplicated here. Boat is static; attach any future animated glows separately. Base palette follows the accepted navy/ivory/wood/teal/steel/orange family. No texture dependency.

### Opened visual evidence

Seven1000x750views: front-three-quarter,side,back-three-quarter,top,low-waterline,deck-55,game-exact-45. Two1600x1000equal-scale lineups: Prep left, Buoy fisher centre, Tier6 right. All nine opened individually, plus review-sheet.png. Checked swept sheer/clinker at side/waterline, cabin closure, shelter coverage, supported stations, lamp cable, both net modules, clear centre deck and larger working hull. Rendering uses actual exported FBXs with isolated source-only floor/lights. No export contains these presentation objects. Family lineup is equal world scale, not individually resized cards.

## C. Refit card

Art/Source/BoatsV2/ui/v2-item-hull-tier6.png,480x360RGBA. Generated from final model game45 plus accepted Prep card reference, prompt/master retained; exact alpha-bounds crop/Lanczos centred export independently reconstructed pixel-for-pixel. Alpha0–255, all corners transparent, visible bounds(33,24)–(447,336). Card and native-size comparison beside Skiff/Prep opened. Consistent thin outline, saturated navy, honey timber, ivory/teal surfaces and shaded volume. Camera follows model reference so poles/lamps stay separated; neighbouring cards show the other quarter. All silhouette margins clear. Tiny fittings simplified as in incumbent cards. Native UI acceptance not run.

## Every actual exported mesh bound

Source/rest XYZ metres, same convention as Blender authoring. These are actual FBX reimport bounds, including outboard poles/lines and engine; whole-model extent intentionally exceeds the nominal hull.

| Mesh | Minimum | Maximum | Triangles |
|---|---|---|---:|
'''
for row in b['rows']:text+='| '+row['name']+' | '+str(tuple(round(x,5) for x in row['world_min_m']))+' | '+str(tuple(round(x,5) for x in row['world_max_m']))+' | '+str(row['triangles'])+' |\n'
text+='\n### Exact used material colours\n\n| Material | sRGB hex |\n|---|---|\n'
used={n for row in b['rows'] for n in row['materials']}
for n,col in sorted(v['materials_linear_rgba'].items()):
 if n not in used:continue
 cv=lambda x:round(max(0,min(1,12.92*x if x<=.0031308 else 1.055*x**(1/2.4)-.055))*255)
 text+='| '+n+' | #'+''.join(f'{cv(x):02X}' for x in col[:3])+' |\n'
text+='''
## Reproduction / checks / limits

Source Art/Source/BoatsV2/Tier6/. Run Windows Blender5.2 background with build_tier6.py, review_tier6.py, then surface_audit.py; run export_card.py and finish_tier6.py with /home/mo/.venvs/catchline-ui/bin/python. inventory.py is read-only for four source blends and appends original inventory tables to the older concept report. Shared geometry2.py and HarbourV2/audit.py helpers read-only. build/review/final surface logs retained. Actual FBX audit precedes rendered review. No Unity project batchmode, import, saves or source/runtime edits performed. No subagents, no commit, no replacement backup required for new Tier6V1; accepted concept history preserved. Final receipt seals models, reports, all source scripts, input inventory, concept/card provenance, every image and audits. Source technical/visual review does not claim native integration acceptance.
'''
(O/'REPORT.md').write_text(text)
v.update(access_graph_connected=True,all_worker_access_crew_nodes_in_network=True,native_Unity_tested=False);(O/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
visual={'result':'PASS','images':images,'review_sheet':'renders/review-sheet.png','concept_opened':True,'card_opened':True,'card_comparison_opened':True,'native_acceptance':False};(O/'visual-validation.json').write_text(json.dumps(visual,indent=2)+'\n')
for p in S.glob('*.py'):ast.parse(p.read_text())
paths=[p for p in [*O.rglob('*'),*S.rglob('*'),R/c['asset'],R/'Art/Models/BoatsV2/Tier6/REPORT.md'] if p.is_file() and p.suffix in ('.py','.json','.txt','.md','.png','.blend','.fbx') and p.name not in ('delivery-receipt.json','bounds-in-progress.json','clearance-findings.json') and '__pycache__' not in str(p)]
receipt={'task':'TIER6-BOAT-1','owner':'Codex 2 (WSL CLI)','result':'PASS source technical and manual visual; not native acceptance','files':{p.relative_to(R).as_posix():sha(p) for p in paths}}
(O/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');assert all(sha(R/p)==h for p,h in receipt['files'].items())
print('TIER6 FINISH PASS',len(receipt['files']),'hashes,9views,connected access graph,all worker nodes,exact card reconstruction',flush=True)
