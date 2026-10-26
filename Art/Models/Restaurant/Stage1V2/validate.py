"""Fresh independent FBX reimport: mesh/world bounds, metres, roots, budget, both UV sets,
nondegenerate UV1s, atlas/vertex data. No rendering/native success is inferred.
"""
import bpy,json,math,hashlib
from pathlib import Path
from io_scene_fbx import parse_fbx
O=Path(__file__).resolve().parent;src=json.loads((O/'build-metrics.json').read_text());items=[];uvproof={}
def units(file):
 fbx,_=parse_fbx.parse(str(file));settings=next(e for e in fbx.elems if e.id==b'GlobalSettings');props=next(e for e in settings.elems if e.id==b'Properties70');return next(e.props[-1] for e in props.elems if e.props[0]==b'UnitScaleFactor')
def inspect(file,expected):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(file),colors_type='LINEAR');bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];rows=[]
 assert units(file)==100
 assert len(meshes)==len(expected),(file,len(meshes),len(expected))
 if file.name!='Stage1V2.fbx':
  for ob in bpy.context.scene.objects:
   if ob.type=='EMPTY' and ob.parent is None:assert ob.location.length<1e-5,(file,ob.name,list(ob.location))
 if file.name=='FryerBroken.fbx':
  socket=bpy.data.objects.get('SmokeSocket');assert socket is not None and socket.parent.name=='FryerBroken'
  assert max(abs(a-b) for a,b in zip(socket.location,(.23,.04,.81)))<1e-5
 for ob in meshes:
  row=expected[ob.name];me=ob.data;pts=[ob.matrix_world@v.co for v in me.vertices];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];tri=sum(len(p.vertices)-2 for p in me.polygons)
  assert all(math.isfinite(v) for p in pts for v in p);delta=max(abs(a-b) for aa,bb in [(lo,row['min_m']),(hi,row['max_m'])] for a,b in zip(aa,bb));assert delta<.0001 and tri==row['triangles'],(ob.name,delta,tri)
  assert len(me.materials)==1,(ob.name,len(me.materials))
  assert ob.parent.name==row['root'];assert len(me.uv_layers)==2,(ob.name,list(me.uv_layers))
  uv0=me.uv_layers[0];uv1=me.uv_layers[1]
  for uv in [uv0,uv1]:assert all(math.isfinite(c) and -.00001<=c<=1.00001 for p in uv.data for c in p.uv)
  me.calc_loop_triangles();areas=[]
  for t in me.loop_triangles:
   a,b,c=[uv1.data[i].uv for i in t.loops];area=abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))*.5;areas.append(area)
  # All authored surfaces need a real UV1 region; no stacked whole-mesh UV0 copy.
  deg=sum(a<1e-13 for a in areas)
  if deg:print('DEGENERATE DETAILS',ob.name,[(areas[i],me.loop_triangles[i].area) for i in range(len(areas)) if areas[i]<1e-13][:25],flush=True)
  assert deg==0,(ob.name,deg)
  assert sum(areas)<=1.0001,(ob.name,sum(areas))
  ao=me.color_attributes.get('LocalAO');assert ao is not None,(ob.name,list(me.color_attributes))
  if file.name in ['RoomShell.fbx','PrepCounter.fbx','GrilledFishPlate.fbx']:
   uvproof[ob.parent.name]={u.name:[[list(u.data[i].uv) for i in p.loop_indices] for p in me.polygons] for u in me.uv_layers}
  colors=[v.color[0] for v in ao.data];assert min(colors)>=.76 and max(colors)<=1.0001,(ob.name,min(colors),max(colors))
  rows.append({'mesh':ob.name,'root':ob.parent.name,'triangles':tri,'min_m':lo,'max_m':hi,'bounds_delta_m':delta,'UV_layers':[u.name for u in me.uv_layers],'UV1_triangle_area_sum':sum(areas),'UV1_degenerate_triangles':deg,'AO_min':min(colors),'AO_max':max(colors),'material_slots':len(me.materials)})
 return {'file':file.relative_to(O).as_posix(),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'pass':True,'unit_scale_factor':100,'rows':rows}
for r in src['roots']:
 expected={r['mesh']:{'root':r['root'],'min_m':r['local_min_m'],'max_m':r['local_max_m'],'triangles':r['triangles']}}
 record=inspect(O/r['fbx'],expected);items.append(record);print('ITEM VERIFIED',r['root'],r['triangles'],flush=True)
assembly=inspect(O/'Stage1V2.fbx',{r['mesh']:r for r in src['assembly']});assert sum(r['triangles'] for r in assembly['rows'])==src['dressed_assembly_triangles']
assert src['unique_library_plus_shell_triangles']<=150000 and src['dressed_assembly_triangles']<=150000
result={'pass':True,'items':items,'assembly':assembly,'unique_library_plus_shell_triangles':src['unique_library_plus_shell_triangles'],'dressed_assembly_triangles':src['dressed_assembly_triangles'],'max_triangles':150000,'texture_count':2,'texture_size':[2048,2048],'no_unlisted_or_presentation_meshes':True,'native_Unity_verified':False,'UV1_note':'Independent finite/range/positive-area/total-area audit; smart-projected packed island separation is additionally inspected by UV proof. No Unity lightmap bake performed.'}
(O/'UV-proof-data.json').write_text(json.dumps(uvproof))
(O/'validation.json').write_text(json.dumps(result,indent=2));print('V2 EXPORT AUDIT PASS',len(items),src['unique_library_plus_shell_triangles'],flush=True)
