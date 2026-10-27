"""Build the current delivery report from audited files and actual review hashes."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/GullHarbour/HarbourV2'
groups={
'A':['Slipway','PontoonSegment','PontoonGangway','FuelDock','QuayCrane','BreakwaterWall','BreakwaterEnd','OuterWharf','WharfLight','MouthBeacon'],
'B':['HarbourMasterHut','NoticeBoard','SuppliesShed','IceHouse','NetLoft','BoatyardShed','BoatCradle'],
'C':['CompactFisherV1_VariantRed','PrepFisherV1_VariantGreen','Tier5DeepLines103_VariantBlue','Skiff_VariantYellow'],
'D':['ChannelMarkerRed','ChannelMarkerGreen','BellBuoy','Wreck','SealRocks','FloatingCrate','Dolphin','SeagullDive','HandCart']}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reviews=json.loads((O/'reviewed-images.json').read_text()) if (O/'reviewed-images.json').exists() else []
reviewmap={r['path']:r for r in reviews}
rows=[];lines=['# HARBOUR-ART-1 — growing harbour kit','',
'Codex 2 (WSL CLI). A–D individual art complete. E supplies five reviewed occupied clearance proposals; the adopted runtime layout still needs the corrections below.', '',
'Editable sources and FBXs are in this directory. Authoring script: `Art/Source/HarbourV2/build.py`; independent round-trip audit: `audit.py`. Blender 5.2.1 LTS. Metres, shared STYLE.md palette material names, matte broad bevels. No textures or external material folders. Preview cameras, lights and floor are excluded from FBX.', '',
'## Import and placement','',
'New models face Unity local **-Z**. Old HouseA/B face +Z; the plan’s yaw180 for old houses must not be copied to new front-facing buildings. Use yaw0 for new doors/windows facing the water. Jib is an exact direct child of QuayCrane, pivot on the slew axis at local Y3.16. Gangway child pivot is at its quay end, local Y.35.', '',
'Absolute harbour-datum assets (root Y0): Slipway deck .35 to -.9; PontoonSegment/FuelDock deck0; PontoonGangway .35 to0; BreakwaterWall/End cap .6; OuterWharf deck .35; MouthBeacon rock sole -.8. Place other ground-contact buildings/props on the surface they stand on. Submerged construction is intentional.', '',
'## Individual asset checks','',
'Each accepted row has a source+FBX triangle/material/mesh/bounds round-trip PASS and five individually opened 600px renders. Image hashes are in `reviewed-images.json`; full metrics and part details in `metrics/<name>.json`.', '',
'| Group | Model | Tris / limit | W × D × H (m) | State |','| --- | --- | ---: | --- | --- |']
for group,names in groups.items():
 for name in names:
    p=O/'metrics'/(name+'.json')
    if not p.exists():lines.append(f'| {group} | {name} | — | — | Pending |');continue
    row=json.loads(p.read_text());assert row.get('round_trip',{}).get('result')=='PASS',name
    for k in ['blend','fbx']:assert sha(O/(name+'.'+k))==row['sha256'][k],(name,k)
    opened=0
    for rp in row['renders']:
      rp=rp.replace('\\','/');im=R/rp
      if rp in reviewmap and sha(im)==reviewmap[rp]['sha256']:opened+=1
    state='Individual PASS' if opened==5 else f'Visual review pending ({opened}/5)'
    row['actual_reviewed_images']=opened;rows.append(row)
    dims=' × '.join(f'{d:.2f}' for d in row['dimensions_width_depth_height'])
    budget=f"{row['triangles']} / {row['limit']}"
    if row.get('canonical_source'):
      assert row.get('canonical_geometry_identity',{}).get('result')=='PASS',name
      assert row.get('geometry_round_trip',{}).get('result')=='PASS',name
      budget=f"{row['triangles']} (inherited boat exception)"
    lines.append(f"| {group} | {name} | {budget} | {dims} | {state} |")
lines+=['', 'Paint variants retain the exact released production hull geometry. Their inherited triangle counts exceed the generic 1500-triangle prop budget; this explicit exception follows the brief’s same-mesh requirement. Every variant has independent canonical-source and FBX triangle-surface identity checks. Newly authored buildings and props retain strict limits.']
assembly=[]
for tier in range(5):
 p=O/'assembly/clearance'/f'tier{tier}.json'
 if not p.exists():continue
 row=json.loads(p.read_text());assert not row['boat_surface_intersections'],tier
 for source,digest in row['sources'].items():assert sha(R/source)==digest,source
 for render in row['renders']:
  assert sha(R/render['path'])==render['sha256'],render['path']
  assert render['review']=='opened',render['path']
 assembly.append(row)
lines+=['','## Occupied assemblies — E','',
'Five editable scenes and ten final renders are in `assembly/clearance/`: tier0–tier4, whole harbour1440×900 and landscape phone844×390. All final images were individually opened. Orthographic pitch45°, yaw35°. All five actual-mesh audits report zero boat/boat or boat/solid triangle-surface intersections. Canonical and variant meshes are unchanged. The initial portrait crops were superseded because they excluded berth edges.', '',
'At phone size the hut/notice board/stall, boatyard/pontoon/fuel station, net loft/crane, and ice house/shopfront groups read as distinct silhouettes. Small paper and shop symbols are decoration rather than readable text. The whole views show the increasing building set, older moored boats, the lighthouse exit and every berth. Water covers intentionally submerged foundations; buildings and landing supports meet their authored datums.', '',
'### Required placement handoff to Claude','',
'This is a **clearance proposal**, not proof that the current runtime layout fits. `assembly/updated/tier4-audit.json` preserves four actual-mesh surface collisions in the latest rowboat/outer-slot coordinates, even after presentation datum/front corrections. Both rowboats at Z−1.8 intersect the slipway (196/200 triangle pairs); outer slot1 at X24.2 intersects two east-wall sections (453/1229 pairs), reaching X28.719. Earlier plan diagnostics remain in `assembly/plan/`.', '',
'| Item | Reviewed proposal (Unity metres) | Reason |',
'| --- | --- | --- |',
'| Rowboats | X−27.35/−22.65, Y0, **Z−4.8**, level | Z−3.7 still intersects ramp rails; Z−4.8 clears without pitching |',
'| Slipway | (−25,−.05,2.4) | Sunk ramp, unchanged mesh |',
'| Outer boats | X**11.9/21.4**, Y0; Z=−10.6+.9+.3+actual beam/2, bow−X | Full hulls clear each other, wharf and east wall |',
'| Breakwater/outer wharf | wall rootsY0, Z−12; wharf rootsY0, Z−10.6 | Authored local cap .6 and deck .35 already include heights |',
'| Quay4m | rootY.217 | Existing mesh top reaches .35 at this root |',
'| Gangway | (−13,0,3.5) | Local .35→0 ramp meets quay and pontoon without added height |',
'| Supplies shed | (−28,.35,6), yaw0 | Separate roof from boatyard, front toward water |',
'| Boatyard/cradle | both X−35,Z6.5; shedY.35, cradleY.35 | Cradle is inside shed, clear of adjacent roof |',
'| New buildings | yaw0, ground-contactY.35 | New fronts−Z; old HouseA/B keep yaw180 |',
'| Beach | Cut ramp opening, shore landing at (−25,−.12,3.65), 8×.94×2.5 | Excludes ramp/boat overlap and supports head of ramp |',
'| Crane | (16.5,.35,4.2) | Keeps quay service area clear |', '',
'Exact per-tier boat/asset transforms, occupied bounds, source hashes and camera settings are in each `tierN.json`; `assembly.py` reproduces them. Surface intersection tests do not establish containment-free solid clearance. Visual review supplements the test; it does not replace native runtime verification. This correction proposal is the remaining runtime dependency, assigned to Claude/Codex1.', '',
'## Delivery boundary','',
'Individual exports, editable sources, 150 studio review hashes and ten final assembly review hashes are complete. Unity imports, actual runtime placement, lighting and native captures belong to Codex1/Claude. No Unity/gameplay/save/scene/build/install acceptance is claimed. No Assets or existing baseline sources were edited. No git operations. FISH-ARMS-2 follows this art handoff.', '']
baseline=json.loads((O/'baseline.json').read_text())
for name,row in baseline.items():
 assert sha(R/row['path'].replace('\\','/'))==row['sha256'],('existing baseline changed',name)
(O/'REPORT.md').write_text('\n'.join(lines))
receipt={'task':'HARBOUR-ART-1','owner':'Codex 2 (WSL CLI)','status':'art complete; runtime placement corrections/native acceptance pending',
 'individual_pass':[r['name'] for r in rows if r['actual_reviewed_images']==5],
 'reviewed_image_count':sum(r['actual_reviewed_images'] for r in rows),'baseline_sources_unchanged':True,
 'assembly_tiers_reviewed':[r['tier'] for r in assembly],
 'assembly_reviewed_image_count':sum(len(r['renders']) for r in assembly),
 'assembly_layout':'clearance proposal; not runtime adoption',
 'runtime_dependencies':['Adopt or resolve documented placement corrections','Native Unity verification by Claude/Codex1'],
 'remaining':[n for ns in groups.values() for n in ns if n not in [r['name'] for r in rows if r['actual_reviewed_images']==5]],
 'group_individual_complete':{g:all(n in [r['name'] for r in rows if r['actual_reviewed_images']==5] for n in ns) for g,ns in groups.items()}}
(O/'delivery-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
