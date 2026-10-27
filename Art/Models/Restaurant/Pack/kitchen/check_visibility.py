"""Game-camera visibility rays against fresh exported FBXs and proof supports."""
import sys
sys.dont_write_bytecode=True
import bpy,json,math,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('kitchen_review',O/'review.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
rows=[];pitch=math.radians(38);yaw=math.radians(2);toward=Vector((math.sin(yaw)*math.cos(pitch),-math.cos(yaw)*math.cos(pitch),math.sin(pitch)))
for r in v.M:
 v.v.reset();obs=v.v.import_piece(r,True,(0,0,v.height(r)));v.support(r);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();counts={}
 for ob in obs:
  count=0
  for p in ob.data.polygons:
   pt=ob.matrix_world@p.center;hit,loc,norm,face,obj,mat=bpy.context.scene.ray_cast(dg,pt+toward*20,-toward,distance=21)
   if hit and obj.original==ob:count+=1
  counts[ob.name]=count
 checks=dict(body_visible=counts.get(r['name'],0)>0,hood_task_light_visible=counts.get(r['glow_mesh'],0)>0 if r['glow_mesh'] else True)
 rows.append(dict(stem=r['stem'],visible_polygon_samples=counts,checks=checks))
result=dict(pass_all=all(all(r['checks'].values()) for r in rows),camera_pitch=38,camera_yaw=2,source_only=True,items=rows)
(O/'visibility-audit.json').write_text(json.dumps(result,indent=2));print('VISIBILITY',result,flush=True)
