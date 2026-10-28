"""Independent SERVICE-PROPS-4 FBX/readback checks. Read-only assets."""
import bpy,sys,json,hashlib,re
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import import_fbx,parse_fbx
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
class Op:
 def report(self,*a):print(*a)
rows=json.loads((O/'props4-manifest.json').read_text());out=[]
for rec in rows:
 if rec.get('rig'):continue
 bpy.ops.wm.read_factory_settings(use_empty=True);path=R/rec['file'];import_fbx.load(Op(),bpy.context,filepath=str(path),use_anim=False);bpy.context.view_layer.update()
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];raw=[o.matrix_world@v.co for o in obs for v in o.data.vertices];vs=[Vector((-v.x,v.z,-v.y)) for v in raw]
 lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];size=[hi[i]-lo[i] for i in range(3)]
 assert max(abs(size[i]-rec['size_xyz_unity_m'][i]) for i in range(3))<.00002,(rec['name'],size,rec['size_xyz_unity_m'])
 if 'Wall_' in rec['name']:
  assert abs(lo[2])<.0001,(rec['name'],'wall contact',lo,hi)
 elif 'PaperLanterns' in rec['name']:
  assert abs(lo[0])<.0001 and abs(hi[0]-6)<.0001,(rec['name'],lo,hi)
  glows=[o for o in obs if o.name.split('.')[0]=='Glow']
  assert len(glows)==6 and len({o.parent.name for o in glows if o.parent})==6
  assert all(o.parent.name.startswith('Lantern_') for o in glows)
  assert all(all(abs(d.uv.x-.4375)<1e-5 and abs(d.uv.y-.375)<1e-5 for d in o.data.uv_layers.active.data) for o in glows),'Glow must use canonical emitting yellow cell'
 else:assert abs(lo[0]+hi[0])<.00002 and abs(lo[2]+hi[2])<.00002 and abs(lo[1])<.00002,(rec['name'],lo,hi)
 tris=0
 for ob in obs:
  me=ob.data;me.calc_loop_triangles();tris+=len(me.loop_triangles)
  assert len(me.materials)==1 and me.materials[0].name=='RestaurantAtlas'
  assert len(me.uv_layers)==1 and all(0<=d.uv.x<=1 and 0<=d.uv.y<=1 for d in me.uv_layers.active.data)
  assert me.color_attributes.active_color and all(all(0<=c<=2 for c in d.color) for d in me.color_attributes.active_color.data)
  assert not any(t.area<1e-12 for t in me.loop_triangles),(rec['name'],'degenerate')
 assert tris==rec['tris'] and tris<rec['triangle_limit_exclusive']
 for child in rec.get('children',[]):assert any(o.name==child and o.parent for o in obs),(rec['name'],child)
 meta=Path(str(path)+'.meta').read_text();assert 'name: RestaurantAtlas' in meta and 'guid: 93ede68a78343aa4bbc6d4deed7baeec' in meta
 assert hashlib.sha256(path.read_bytes()).hexdigest()==rec['sha256']
 tree,ver=parse_fbx.parse(str(path));objects=next(e for e in tree.elems if e.id==b'Objects')
 if 'PaperLanterns' in rec['name']:
  models={e.props[0]:e.props[1].split(b'\x00\x01')[0] for e in objects.elems if e.id==b'Model'}
  glow_ids=[k for k,v in models.items() if v==b'Glow'];assert len(glow_ids)==6,models
  connections=next(e for e in tree.elems if e.id==b'Connections')
  parents={e.props[1]:e.props[2] for e in connections.elems if e.props[0]==b'OO' and e.props[1] in glow_ids}
  assert len(parents)==6 and len(set(parents.values()))==6
  assert all(models.get(par,b'').startswith(b'Lantern_') for par in parents.values())
 for geometry in [e for e in objects.elems if e.id==b'Geometry']:
  indices=next(e for e in geometry.elems if e.id==b'PolygonVertexIndex').props[0]
  assert len(indices)%3==0
  for layer_id,index_id in [(b'LayerElementNormal',b'NormalsIndex'),(b'LayerElementColor',b'ColorIndex'),(b'LayerElementUV',b'UVIndex')]:
   layer=next(e for e in geometry.elems if e.id==layer_id);assert len(next(e for e in layer.elems if e.id==index_id).props[0])==len(indices),(rec['name'],'incomplete corner layer',layer_id)
 props=next(e for e in next(e for e in tree.elems if e.id==b'GlobalSettings').elems if e.id==b'Properties70');vals={p.props[0].decode():p.props[-1] for p in props.elems};assert vals['UpAxis']==1 and vals['UpAxisSign']==1 and vals['UnitScaleFactor']==100.
 out.append(dict(name=rec['name'],tris=tris,size_unity_m=size,zero_degenerate=True,complete_corner_layers=True,canonical_atlas=True,children=rec.get('children',[]),Y_up_metres=True));print('PASS',rec['name'],tris,flush=True)
base=json.loads((O/'props4-preservation.json').read_text());changed=[p for p,h in base.items() if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h];
external=json.loads((O/'props4-external-dependency-changes.json').read_text())['items']
assert set(changed)=={e['file'] for e in external},changed
for e in external:
 assert base[e['file']]==e['before_sha256']
 assert hashlib.sha256((R/e['file']).read_bytes()).hexdigest()==e['current_sha256'],e['file']
(O/'props4-audit.json').write_text(json.dumps(dict(status='PASS',items=out,preserved_dependency_count=len(base)-len(changed),external_dependency_changes=changed),indent=2)+'\n');print('PROPS4_AUDIT_PASS',len(out),len(base))
