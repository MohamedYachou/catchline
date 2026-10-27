"""Independent source and fresh-FBX preservation, UV-delta, bounds and units audit."""
import bpy,json,gzip,hashlib,math,sys
from pathlib import Path
from io_scene_fbx import parse_fbx
def posix(p):return str(p).replace(chr(92),'/')
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V2';B=O/'_station-finish-backup';R=O.parents[3]
names=['Stove','Oven','FridgeV2','Fryer','PrepCounter','SoupKettle','SinkDishRack','CoffeeBar']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(data):return hashlib.sha256(json.dumps(data,separators=(',',':')).encode()).hexdigest()
def vec(v,n=6):return [round(float(x),n) for x in v]
def snap(path,blend=False):
 if blend:bpy.ops.wm.open_mainfile(filepath=posix(path))
 else:bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=posix(path),colors_type='LINEAR')
 bpy.context.view_layer.update();out={}
 if blend and '_station-finish-backup' not in str(path):
  for im in bpy.data.images:
   if im.source=='FILE':assert im.packed_file or Path(bpy.path.abspath(im.filepath)).is_file(),(path,im.name,'missing image link')
 for ob in bpy.context.scene.objects:
  row={'type':ob.type,'parent':ob.parent.name if ob.parent else None,'matrix':vec([c for r in ob.matrix_world for c in r])}
  if ob.type=='MESH':
   me=ob.data;pts=[ob.matrix_world@v.co for v in me.vertices];me.calc_loop_triangles()
   row.update({'geometry':digest({'v':[vec(v.co) for v in me.vertices],'p':[list(p.vertices) for p in me.polygons],'normals':[vec(p.normal) for p in me.polygons]}),'triangles':len(me.loop_triangles),'materials':[m.name for m in me.materials],'material_indices':digest([p.material_index for p in me.polygons]),'attributes':{a.name:digest([vec(d.color) for d in a.data]) for a in me.color_attributes},'uv_names':[u.name for u in me.uv_layers],'UV1':digest([[vec(d.uv,7) for d in u.data] for u in list(me.uv_layers)[1:]]),'UV0':digest([vec(d.uv,7) for d in me.uv_layers[0].data]) if me.uv_layers else None,'min_m':[min(p[i] for p in pts) for i in range(3)],'max_m':[max(p[i] for p in pts) for i in range(3)]})
   canonical=ob.name.removeprefix('EXPORT_').removesuffix('_Mesh')
   if canonical in names:
    row['uv0_values']=[vec(d.uv,7) for d in me.uv_layers[0].data]
   for u in me.uv_layers:assert all(math.isfinite(c) for d in u.data for c in d.uv)
   if len(me.uv_layers)>1:
    uv=me.uv_layers[1].data;areas=[]
    for t in me.loop_triangles:
     a,b,c=[uv[i].uv for i in t.loops];areas.append(abs((b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x))/2)
    assert min(areas)>0,(path,ob.name,'UV1')
  out[ob.name]=row
 return out
files={f'kit/{n}':V/'items'/f'{n}.fbx' for n in names};files['V4']=O/'Stage1V4.fbx'
blends={'V2-source':V/'Stage1V2.blend','V4-source':O/'Stage1V4.blend'}
protected=[*[p for d in [V,O] for p in (d/'textures').glob('*') if p.is_file()],*[p for p in [O/'layout.json'] if p.exists()],O/'final-cameras.json',O/'lighting.json',V/'build-metrics.json',O/'build-metrics.json']
# All runtime import files remain read-only during this art delivery.
protected.extend(R/'Assets/Art/Models/Restaurant/Stage1V2'/f'Restaurant_{n}.fbx' for n in names)
basepath=O/'station-finish-baseline.json.gz'
if not basepath.exists():
 baseline={'protected':{str(p.relative_to(R)):sha(p) for p in protected},'snapshots':{}}
 for k,p in {**files,**blends}.items():
  old=B/('Stage1V2' if k.startswith('kit/') or k=='V2-source' else 'Stage1V4')/p.relative_to(V if k.startswith('kit/') or k=='V2-source' else O)
  baseline['snapshots'][k]=snap(old,k in blends)
 basepath.write_bytes(gzip.compress(json.dumps(baseline).encode()))
else:baseline=json.loads(gzip.decompress(basepath.read_bytes()))
assert all(sha(R/p)==h for p,h in baseline['protected'].items()),'protected files changed'
results={}
for key,path in {**files,**blends}.items():
 before=baseline['snapshots'][key];after=snap(path,key in blends);assert before.keys()==after.keys(),(key,'names');uvchanges={};rows=[]
 for name,b in before.items():
  a=after[name];canonical=name.removeprefix('EXPORT_').removesuffix('_Mesh');allowed=canonical in names
  for prop in b:
   if prop in ['min_m','max_m']:assert max(abs(x-y) for x,y in zip(b[prop],a[prop]))<1e-6,(key,name,prop)
   elif prop in ['UV0','uv0_values'] and allowed:continue
   else:assert b[prop]==a[prop],(key,name,prop)
  if 'uv0_values' in b:
   count=0
   for old,new in zip(b['uv0_values'],a['uv0_values']):
    dx,dy=[new[i]-old[i] for i in range(2)]
    assert abs(dx*8-round(dx*8))<2e-6 and abs(dy*4-round(dy*4))<2e-6,(key,name,'UV0 within-cell shape changed')
    if abs(dx)+abs(dy)>1e-6:
     assert 7/8-1e-6<=new[0]<=1+1e-6 and .75-1e-6<=new[1]<=1+1e-6,(key,name,'destination not steel')
     count+=1
   uvchanges[name]=count
  if a['type']=='MESH':rows.append({'name':name,'triangles':a['triangles'],'min_m':a['min_m'],'max_m':a['max_m'],'materials':a['materials'],'uv_names':a['uv_names']})
 if key not in blends:
  tree,_=parse_fbx.parse(str(path));settings=next(e for e in tree.elems if e.id==b'GlobalSettings');props=next(e for e in settings.elems if e.id==b'Properties70');unit=next(e.props[-1] for e in props.elems if e.props[0]==b'UnitScaleFactor');assert unit==100,(key,unit)
  if key.startswith('kit/'):
   root=after[key.split('/')[1]];assert max(abs(v-(1 if i in [0,5,10,15] else 0)) for i,v in enumerate(root['matrix']))<1e-6
   assert abs(rows[0]['min_m'][2])<1e-5
 results[key]={'pass':True,'sha256':sha(path),'object_count':len(after),'mesh_count':len(rows),'triangles':sum(r['triangles'] for r in rows),'UV0_changed_loops':uvchanges,'meshes':rows,'FBX_UnitScaleFactor':100 if key not in blends else None}
metrics=json.loads((V/'build-metrics.json').read_text());fps={r['root']:r for r in metrics['roots']}
for n in names:
 row=results['kit/'+n]['meshes'][0];old=fps[n];assert row['triangles']==old['triangles'];assert all(abs(a-b)<1e-5 for side in ['min','max'] for a,b in zip(row[side+'_m'],old['local_'+side+'_m']))
 results['kit/'+n]['footprint_tiles']=old['footprint_tiles']
result={'pass':True,'geometry_names_pivots_normals_materials_AO_UV1_preserved':True,'UV0_only_integer_atlas_cell_translations_to_steel7':True,'protected_hashes_unchanged':baseline['protected'],'files':results,'native_Unity_after_verified':False}
(O/'station-finish-validation.json').write_text(json.dumps(result,indent=2));print('STATION FINISH INDEPENDENT AUDIT PASS',flush=True)
