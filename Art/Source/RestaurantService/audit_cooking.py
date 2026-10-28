"""Independent FBX readback for SERVICE-PROPS-2; does not write any assets."""
import bpy,json,hashlib,re,sys
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import import_fbx,parse_fbx
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
class Op:
 def report(self,*a):print(*a)
records=json.loads((O/'cooking-manifest.json').read_text());out=[]
if '--pending' in sys.argv:
 pending=json.loads((O/'cooking-build-progress.json').read_text())['item'];records=[r for r in records if r['name']!=pending['name']]+[pending]
for rec in records:
 bpy.ops.wm.read_factory_settings(use_empty=True);path=R/rec['file'];import_fbx.load(Op(),bpy.context,filepath=str(path),use_anim=False);bpy.context.view_layer.update()
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==1
 ob=obs[0];me=ob.data;me.calc_loop_triangles();raw=[ob.matrix_world@v.co for v in me.vertices];vs=[Vector((-v.x,v.z,-v.y)) for v in raw];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];size=[hi[i]-lo[i] for i in range(3)]
 assert max(abs(size[i]-rec['size_xyz_unity_m'][i]) for i in range(3))<.00002,(rec['name'],size)
 assert abs(lo[0]+hi[0])<.00002 and abs(lo[2]+hi[2])<.00002,(lo,hi)
 if rec['name']!='Restaurant_Ferry':assert abs(lo[1])<.00002,(rec['name'],lo)
 else:assert lo[1]<0<hi[1] and abs(ob.location.z)<.00002
 assert len(me.loop_triangles)==rec['tris'] and rec['tris']<rec['triangle_limit_exclusive']
 assert len(me.materials)==1 and me.materials[0].name=='RestaurantAtlas'
 assert len(me.uv_layers)==1 and all(0<=d.uv.x<=1 and 0<=d.uv.y<=1 for d in me.uv_layers.active.data)
 assert all(max(abs(c-1) for c in d.color)<.00001 for d in me.color_attributes.active_color.data)
 assert not any(t.area<1e-12 for t in me.loop_triangles),(rec['name'],'degenerate')
 meta=Path(str(path)+'.meta').read_text();assert 'name: RestaurantAtlas' in meta and 'guid: 93ede68a78343aa4bbc6d4deed7baeec' in meta
 assert hashlib.sha256(path.read_bytes()).hexdigest()==rec['sha256']
 tree,ver=parse_fbx.parse(str(path))
 objects=next(e for e in tree.elems if e.id==b'Objects');geometry=next(e for e in objects.elems if e.id==b'Geometry');indices=next(e for e in geometry.elems if e.id==b'PolygonVertexIndex').props[0];assert len(indices)==rec['tris']*3,(rec['name'],'orphan edge/corner count',len(indices))
 for layer_id,index_id in [(b'LayerElementNormal',b'NormalsIndex'),(b'LayerElementColor',b'ColorIndex'),(b'LayerElementUV',b'UVIndex')]:
  layer=next(e for e in geometry.elems if e.id==layer_id);assert len(next(e for e in layer.elems if e.id==index_id).props[0])==len(indices),(rec['name'],'incomplete corner layer',layer_id)
 gs=next(e for e in tree.elems if e.id==b'GlobalSettings');props=next(e for e in gs.elems if e.id==b'Properties70');vals={p.props[0].decode():p.props[-1] for p in props.elems};assert vals['UpAxis']==1 and vals['UpAxisSign']==1 and vals['UnitScaleFactor']==100.
 out.append(dict(name=rec['name'],sha256=rec['sha256'],tris=rec['tris'],size_unity_m=size,bounds_unity_m=[lo,hi],root_location=list(ob.location),zero_degenerate=True,one_atlas_material=True,canonical_remap=True,complete_corner_layers=True,Y_up_metres=True));print('PASS',rec['name'],rec['tris'],flush=True)
base=json.loads((O/'cooking-preservation-baseline.json').read_text());changed=[p for p,h in base.items() if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h];assert not changed,changed
(O/'cooking-audit.json').write_text(json.dumps(dict(status='PASS',items=out,preserved_dependency_count=len(base)),indent=2)+'\n');print('AUDIT_ALL_PASS',len(out),'preserved',len(base))
