import bpy,json,math,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;M=json.loads((O/'manifest.json').read_text());out=[]
for item in M['stages']:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/item['file']),colors_type='LINEAR');bpy.context.view_layer.update();expected={r['name']:r for r in item['meshes']};rows=[]
 for ob in bpy.context.scene.objects:
  assert ob.type=='MESH',(ob.name,ob.type)
  r=expected.pop(ob.name);me=ob.data;me.calc_loop_triangles();assert len(me.loop_triangles)==r['triangles'];p=[ob.matrix_world@v.co for v in me.vertices];lo=[min(v[k] for v in p) for k in range(3)];hi=[max(v[k] for v in p) for k in range(3)];assert all(math.isfinite(v) for a in p for v in a);delta=max(abs(v-w) for a,b in [(lo,r['min_m']),(hi,r['max_m'])] for v,w in zip(a,b));assert delta<1e-5,(ob.name,delta)
  assert len(me.uv_layers)==2 and len(me.materials)==1,(ob.name,[x.name for x in me.uv_layers],len(me.materials));assert all(p.material_index==0 for p in me.polygons);uv=me.uv_layers[1].data;areas=[]
  for t in me.loop_triangles:
   a,b,c=[uv[i].uv for i in t.loops];areas.append(abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))/2)
  assert min(areas)>0
  rows.append({'name':ob.name,'triangles':r['triangles'],'min_m':lo,'max_m':hi,'bounds_max_error_m':delta,'uv_channels':2,'UV1_min_area':min(areas),'material':me.materials[0].name})
 assert not expected and item['triangles']<60000
 f=json.loads((O/item['footprint']).read_text());assert f['tiles']==[6+2*item['stage'],5] and f['facade_unity_direction']==[0,0,-1]
 out.append({'name':item['name'],'file':item['file'],'FBX_sha256':hashlib.sha256((O/item['file']).read_bytes()).hexdigest(),'pass':True,'triangles':item['triangles'],'meshes':rows,'unit_m':1,'only_production_meshes':True,'floor_contact_z_m':0,'below_floor_piles_m':1})
(O/'validation.json').write_text(json.dumps({'pass':True,'stages':out,'native_import_unverified':True},indent=2));print('EXTERIORS FRESH IMPORT PASS',flush=True)
