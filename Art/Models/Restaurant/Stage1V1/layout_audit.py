"""Independent local-footprint and camera sample checks on the exported, rendered assets."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O/'LookProof.blend'));sc=bpy.context.scene;deps=bpy.context.evaluated_depsgraph_get();bpy.context.view_layer.update()
size={'PrepCounter':(1,1),'Stove':(1,1),'SoupKettle':(1,1),'Fridge':(1,1),'SinkDishRack':(2,1),'CoffeeMachine':(1,1),'TableFor2':(1,1),'TableFor2_B':(1,1),'ReceptionDesk':(1,1),'PassCounter':(2,1),'TrashCan':(1,1),'KettleStand':(1,1)}
rows=[]
for name,cap in size.items():
 root=bpy.data.objects[name];iv=root.matrix_world.inverted();pts=[iv@o.matrix_world@v.co for o in root.children if o.type=='MESH' for v in o.data.vertices];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];dims=[hi[i]-lo[i] for i in range(3)];ok=dims[0]<=cap[0]+1e-5 and dims[1]<=cap[1]+1e-5 and abs(lo[2])<.03
 # Kettle's portable base starts at0; the room's pedestal lift is the root position.
 rows.append({'root':name,'local_dimensions_m':dims,'local_min_m':lo,'local_max_m':hi,'footprint_tiles':cap,'within_footprint_and_floor_pivot':ok,'world_position_blender_m':list(root.location),'root_scale':list(root.scale)})
 assert ok,(name,dims,cap,lo)
# Samples are deliberate probes, not certification that entire tops or walkways are visible.
samples={'PrepCounter':(-3.48,.86,.71),'Stove':(-1.55,1.94,.69),'SoupKettle':(-2.47,1.98,1.35),'Fridge':(-3.45,1.97,1.16),'SinkDishRack':(-3.48,-.2,.92),'CoffeeMachine':(-1.55,-1.91,1.24),'TableFor2':(1.35,.98,.667),'ReceptionDesk':(3.13,-1.76,.674),'PassCounter':(-.68,0,1.123),'TrashCan':(-2.4,-2.07,.60)}
forward=sc.camera.matrix_world.to_quaternion()@Vector((0,0,-1));views=[]
for name,p in samples.items():
 target=Vector(p);origin=target-forward*30;hit,pos,normal,face,obj,mat=sc.ray_cast(deps,origin,forward,distance=30.05);hitroot=obj.parent.name if hit and obj.parent else None
 views.append({'station':name,'sample_blender_m':p,'first_hit_root':hitroot,'sample_unblocked_by_other_station':hitroot in [None,name]})
result={'pass':all(r['within_footprint_and_floor_pivot'] for r in rows),'footprint_rows':rows,'camera_probe_rows':views,'camera_probe_limit':'Only listedtop samples; does not certify floor visibility, all surfaces, grid-path feasibility or native camera projection.','native_Unity_tested':False}
(O/'layout-audit.json').write_text(json.dumps(result,indent=2));print('STAGE1 LAYOUT AUDIT PASS',len(rows),flush=True)
