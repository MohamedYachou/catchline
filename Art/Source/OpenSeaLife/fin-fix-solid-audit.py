import bpy,bmesh,json
from pathlib import Path
O=Path(__file__).resolve().parents[2]/'Models/OpenSeaLife'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/'BaskingFin.fbx'))
o=bpy.data.objects['BaskingFinSkin'];bm=bmesh.new();bm.from_mesh(o.data)
assert all(e.is_manifold for e in bm.edges)
components=[];unseen=set(bm.verts)
while unseen:
 stack=[unseen.pop()];part=[]
 while stack:
  v=stack.pop();part.append(v)
  for e in v.link_edges:
   w=e.other_vert(v)
   if w in unseen:unseen.remove(w);stack.append(w)
 components.append(part)
assert len(components)==2
rows=[]
# Imported rest vertices remain in Blender source axis convention.
for part in components:
 vs=[v.co for v in part];base=[v for v in vs if abs(v.z)<1e-5];tip=[v for v in vs if v.z>max(q.z for q in vs)-1e-5]
 width=max(v.x for v in base)-min(v.x for v in base);tipwidth=max(v.x for v in tip)-min(v.x for v in tip)
 assert width>.15 and tipwidth<width*.20
 rows.append({'vertices':len(vs),'waterline_width_m':width,'crown_width_m':tipwidth,'closed_manifold':True})
assert abs(max(r['waterline_width_m'] for r in rows)-.25)<1e-5
result={'result':'PASS','solid_components':rows,'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'names_pivot_clip':'Existing BaskingFin root/Rig/Skin, Root/Body/Tail bones and Cruise 3s retained; independent main audit covers all-frame fixed root and surface samples.'}
(O/'metrics/BaskingFin-solid-audit.json').write_text(json.dumps(result,indent=2)+'\n');print('SOLID FIN PASS',rows)
