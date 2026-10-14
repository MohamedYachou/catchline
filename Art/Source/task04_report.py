"""Refresh measured handoff inventory after each Task 04 part."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/GullHarbour'
data=json.loads((OUT/'build-metrics.json').read_text())
report=OUT/'REPORT.md'
s=report.read_text().split('\n## Task 04 delivery')[0]
import re
s=re.sub(r'\*\*\d+ editable Blender assets, \d+ FBXs, \d+ (?:individual )?orthographic previews\*\*', f"**{len(data['assets'])} editable Blender assets, {len(data['assets'])} FBXs, {len(data['assets'])} individual orthographic previews**", s)
rows=[]
for a in data['assets']:
 rows.append('| ['+a['asset']+']('+a['group']+'/'+a['asset']+'.blend) | '+str(a['triangles'])+' | '+' × '.join(f'{x:.4f}' for x in a['dimensions_width_depth_height_m'])+' |')
s+='\n## Task 04 delivery\n\nCurrent measured inventory below supersedes the earlier tier 1 table. All assets include editable source, FBX and orthographic preview under the existing group directories. Existing asset names, complete part-name sets and pivots are checked against the saved Task 03 baseline, alongside source/FBX round-trip checks.\n\n'
s+='Part A: pointed rowboat bow, flat transom, rising sheer, rope fender and stripe; cooler handles/latch/rim/drain; framed house windows, steps, chimney and eave trim; quay rings/wear plus Quay4mLadder; lighthouse gallery and glazed lamp room. Cooler and IceBox still share the same body geometry.\n\n'
if any(a['asset']=='RopeCoil' for a in data['assets']):
 s+='Part B: six deck props; Plaice (0.36 m, flat) and Cod (0.70 m), each with a separate tail; seven harbour props including MarketStallAwning and 0.4 m perched Seagull with Wing_L/Wing_R; five ShopFront groups; five sea modules. Shop fronts use ground/door-centre roots, face Unity −Z, and leave the central doorway clear. Their previews are framed from the water-facing side to show papers, charts and rope displays. SandBank is exactly flat, 4 × 2 m; CliffSegment8m has matching end profiles at X ±4; DistantShip hull silhouette is 8 m fore-aft.\n\n'
if any(a['asset']=='Skiff' for a in data['assets']):
 s+='Part C: Skiff with 5 × 3 m deck at height zero, 6.5 × 3.5 m hull (motor excluded), Propeller, HoldLid and RodSocket_1..3. Console occupies starboard/stern tile c=2, r=0 (zero-based, columns port→starboard; rows stern→bow), Unity centre (1,0,−2); this overrides the earlier forward-console suggestion in STYLE.md. HandWinch fits 1 × 1 m with Crank. GillNetCoil, GillNetFloatLine and GillNetSection provide deck storage and 2 m water modules. SortTable fits 2 × 1 m with tray, chute and bin. FishHold is included in Skiff: HoldLid rotates local X at its rear hinge; no redundant standalone hatch is supplied. No animation clips are included. Front/side/top boat views and an open-hold render accompany the focused SkiffKit and BoatViews contact sheets.\n\n'
s+='New M_ names: **none**. All exports reuse the canonical palette. Open surfaces (nets and waterline sand) need two-sided material handling at integration. Unity was not opened; Assets/Scripts and Assets/Scenes were not touched. No requested modelling work remains unfinished in the delivered parts; Unity import/material and animation integration remain for the game branch.\n\n| Asset | Triangles | Width × depth × height (m) |\n| --- | ---: | --- |\n'+'\n'.join(rows)+'\n\nRebuild additions with `build_task04.py -- B` or `-- C`; Part A uses the existing builder. Then run `validate_gull_harbour.py`, `gull_contact_sheets.py` and `task04_report.py`. Additional boat views use `render_task04_boat_views.py` before composing contacts. Detailed part pivots and notes are in build-metrics.json.\n'
report.write_text(s)
