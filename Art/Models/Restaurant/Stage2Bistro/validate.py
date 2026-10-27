"""Independent full-FBX geometry/UV/bounds/material audit, no scene presentation mesh allowed."""
import bpy,json,math,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[3];M=json.loads((O/'build-metrics.json').read_text());expected={r['name']:r for r in M['production_meshes']}
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/'Stage2Bistro.fbx'),colors_type='LINEAR');bpy.context.view_layer.update();rows=[];total=0
for ob in bpy.context.scene.objects:
 if ob.type!='MESH':continue
 name=ob.name.removeprefix('EXPORT_');r=expected.pop(name);ob.data.calc_loop_triangles();tri=len(ob.data.loop_triangles);assert tri==r['triangles'],(name,tri,r['triangles']);total+=tri
 pts=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(v[k] for v in pts) for k in range(3)];hi=[max(v[k] for v in pts) for k in range(3)];assert all(math.isfinite(v) for p in pts for v in p)
 delta=max(abs(v-w) for a,b in [(lo,r['world_min_m']),(hi,r['world_max_m'])] for v,w in zip(a,b));assert delta<1e-5,(name,delta)
 assert len(ob.data.uv_layers)>=2,(name,len(ob.data.uv_layers));assert len(ob.data.materials)==1,(name,len(ob.data.materials));assert all(p.material_index==0 for p in ob.data.polygons)
 # Every exported triangle has a positive-area UV1; no lightmap chart lost in the exporter.
 uv=ob.data.uv_layers[1].data;areas=[]
 for t in ob.data.loop_triangles:
  a,b,c=[uv[i].uv.copy() for i in t.loops];areas.append(abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))/2)
 assert min(areas)>0,(name,min(areas))
 rows.append({'name':name,'triangles':tri,'bounds_min_m':lo,'bounds_max_m':hi,'bounds_max_delta_m':delta,'UV_layers':[u.name for u in ob.data.uv_layers],'UV1_min_triangle_area':min(areas),'material':ob.data.materials[0].name,'material_indices_valid':True,'linked_V2_source':r['linked_V2']})
assert not expected,expected.keys();assert total==M['room_triangles'] and total<=200000
(O/'validation.json').write_text(json.dumps({'pass':True,'triangles':total,'self_imposed_budget':200000,'mesh_count':len(rows),'FBX_sha256':hashlib.sha256((O/'Stage2Bistro.fbx').read_bytes()).hexdigest(),'historical_dependency_hashes_are_provenance_only':True,'meshes':rows,'presentation_objects_excluded':True,'unit_scale_m':bpy.context.scene.unit_settings.scale_length,'native_unity_import_unverified':True},indent=2));print('BISTRO FBX VALIDATION PASS',total,len(rows),flush=True)
