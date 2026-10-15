"""Measured asset inventories and part pivot handoff for world/day-boat batches."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[2]
for batch in sys.argv[1:] or ['WorldPolish','DayBoatKit']:
 out=ROOT/'Art/Models'/batch;data=json.loads((out/'build-metrics.json').read_text());rows=[]
 revision='Six existing models polished in ART-009; see `../VisualPass09/REPORT.md` for compatibility and visual evidence.' if batch=='DayBoatKit' else 'Initial additive batch; no existing asset overwritten.'
 text=f'# Catchline / {batch}\n\n{len(data["assets"])} editable Blender sources, binary FBX exports and orthographic game-angle previews. Runtime groups are under `Assets/Art/Models/`; sources and previews stay in this batch directory. {revision} No Unity, Scripts or Scenes edits. New material names: **none** (NPCs reuse the Task06 hair palette).\n\n'
 text+='Build with Windows Blender5.2 and `Art/Source/'+('build_world_polish.py' if batch=='WorldPolish' else 'build_day_boat.py')+'`; optional arguments after `--` select assets. Run `validate_world_batches.py -- '+batch+'` in Blender; create review sheets with Python/Pillow `world_contact_sheets.py '+batch+'`. Validation checks source topology, materials, roots, finite bounds and zero-area faces; reimports every FBX and compares part names, pivots and bounds. Open surfaces are recorded in validation.json and intentional where noted.\n\n'
 if batch=='WorldPolish':
  text+='The31 assets cover9 upgrade props,11 harbour modules,3 static crew poses and8 sea modules. BigCooler/BigIceBox are exactly1.0x0.6x0.5m and share body geometry,with HingedLid. Rod variants preserve FishingRod part names/proportions/pivots. Boat repaints preserve their full original part/pivot sets. Outboard_Small root is its transom clamp,not an underside prop root; Propeller remains separate. The40m stepped backdrop repeats along X and belongs behind the shop row. Shed shell is8x6m plus its forward slipway. NPCs are static evaluated Task06 rig poses,not new skeletons; NPC_Sitting adapts Row with horizontal thighs/vertical shins. For Bench, place its root at Unity offset(0,0.2235,+0.15) from the bench root: local outfit seat contact0.239m meets seat top0.4625m; short legs dangle. NPC_Sitting-on-Bench.png is a source-only mounting review; no bench is included in the NPC FBX. WhaleTail has a separate Tail mesh with waterline/base pivot for consumer-driven rising/sinking; no animation clips are claimed. Buoy red/green topmark geometry communicates the type in addition to colour. KelpForest is exactly4x4m and planar; use a two-sided material. Shore/water modules deliberately extend below their waterline roots.\n\n'
 else:
  text+='DayBoat deck is exactly X[-2.5,+2.5],Unity Z[-5,+5],Y=0:50tiles total. Wheelhouse body is X[-1.5,+1.5],Z[+3,+5],height1.65m:columns1/2/3,rows8/9,6tiles inside the deck,44 remaining. Bow +Z; hull12x5.8m. Door faces aft. Roof overhang is separate from the authoritative body footprint. Port stern-quarter hauler gap is Unity Z[-4,-2.5]. Six named rod sockets expose attachment pivots. Mast/radar are static details. Station footprint/access/parts table is in `Stations/REPORT.md`. No baked station animation; consumer drives named moving parts. FishHold extends below deck and requires an actual opening in the boat deck at placement. The boat is supplied empty for free equipment layout.\n\n'
 text+='Source coordinates X right,-Y forward,Z up. FBX converts to Unity X right,+Y up,+Z forward. Root is ground/deck/waterline centre unless explicitly documented. Part pivot table below uses **Unity local metres** `(x,z,-y)` converted from source offsets. Part rotations zero/scales one; animate each part relative to its listed pivot. Materials are original canonical M_* flat colours,no external textures or embedded preview lights. Texture pack has a separate TEXTURES.md.\n\n| Asset | Group | Width x depth x height m | Triangles |\n| --- | --- | --- | ---: |\n'
 for a in data['assets']:text+='| ['+a['asset']+']('+a['group']+'/'+a['asset']+'.blend) | '+a['group']+' | '+' x '.join(f'{v:.3f}' for v in a['dimensions_width_depth_height_m'])+' | '+str(a['triangles'])+' |\n'
 text+='\n## Parts and pivots\n\n'
 for a in data['assets']:
  text+='### '+a['asset']+'\n\n'
  for p,v in a['pivots_blender'].items():text+='- `'+p+'`: ('+', '.join(f'{z:.4f}' for z in (v[0],v[2],-v[1]))+')\n'
  if a['notes']:text+='\n'+' '.join(a['notes'])+'\n'
  text+='\n'
 text+='Rendered contact sheets and individual previews were inspected. Validation files document mechanical checks; runtime placement, material remapping and animation integration remain for the game branch.\n'
 (out/'REPORT.md').write_text(text)
print('Reports generated')
