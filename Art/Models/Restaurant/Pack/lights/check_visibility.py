"""Cast orthographic game-camera rays against fresh FBXs, count visible glow components."""
import sys
sys.dont_write_bytecode=True
import bpy,json,math,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('light_review',O/'review.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
rows=[];pitch=math.radians(38);yaw=math.radians(2);toward=Vector((math.sin(yaw)*math.cos(pitch),-math.cos(yaw)*math.cos(pitch),math.sin(pitch)))
for r in v.M:
 v.v.reset();obs=v.v.import_piece(r,True,(0,0,v.height(r)));v.support(r);g=next(o for o in obs if o.name==r['glow_mesh'])
 parent=list(range(len(g.data.vertices)))
 def root(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 for edge in g.data.edges:
  a,b=edge.vertices;parent[root(a)]=root(b)
 groups={root(x) for x in range(len(parent))};visible=set();samples=0;dg=bpy.context.evaluated_depsgraph_get()
 for p in g.data.polygons:
  pt=g.matrix_world@p.center;hit,loc,norm,face,obj,mat=bpy.context.scene.ray_cast(dg,pt+toward*20,-toward,distance=21)
  if hit and obj.original==g and face>=0:
   visible.add(root(g.data.polygons[face].vertices[0]));samples+=1
 checks=dict(glow_visible=bool(visible),all10bulbs_visible=len(visible)==10 if r['stem']=='StringLightsLong' else True)
 rows.append(dict(stem=r['stem'],glow_components=len(groups),visible_components=len(visible),visible_hit_samples=samples,checks=checks))
result=dict(pass_all=all(all(r['checks'].values()) for r in rows),camera_pitch=38,camera_yaw=2,source_only=True,items=rows)
(O/'visibility-audit.json').write_text(json.dumps(result,indent=2));print('VISIBILITY',result,flush=True)
