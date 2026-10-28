"""Read-only FBX/atlas/preservation validation. Never starts Unity."""
import bpy,json,math,hashlib,re
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import import_fbx,parse_fbx
R=Path(__file__).resolve().parents[3];O=Path(__file__).resolve().parent
class Reporter:
 def report(self,*a):print(*a)
records=json.loads((O/'manifest.json').read_text());out=[]
for rec in records:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 path=R/rec['file'];import_fbx.load(Reporter(),bpy.context,filepath=str(path),use_anim=False)
 obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==1,(path,len(obs))
 ob=obs[0];me=ob.data;me.calc_loop_triangles()
 vs=[ob.matrix_world@v.co for v in me.vertices];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];size=[hi[i]-lo[i] for i in range(3)]
 # Bundled importer retains the pack's Y-up world convention. Compare in Unity coordinates.
 assert max(abs(size[i]-rec['size_xyz_unity_m'][i]) for i in range(3))<.00001,(rec['name'],size,rec['size_xyz_blender_m'])
 assert abs(lo[1])<.00001 and abs(lo[0]+hi[0])<.00001 and abs(lo[2]+hi[2])<.00001,(rec['name'],lo,hi)
 tris=len(me.loop_triangles);assert tris==rec['tris'] and tris<rec['triangle_limit_exclusive'],(rec['name'],tris,rec['tris'])
 assert len(me.materials)==1 and me.materials[0].name=='RestaurantAtlas'
 assert len(me.uv_layers)==1 and all(0<=d.uv.x<=1 and 0<=d.uv.y<=1 for d in me.uv_layers.active.data)
 assert all(max(abs(c-1) for c in d.color)<.00001 for d in me.color_attributes.active_color.data)
 meta=Path(str(path)+'.meta').read_text();assert 'name: RestaurantAtlas' in meta and 'guid: 93ede68a78343aa4bbc6d4deed7baeec' in meta
 assert hashlib.sha256(path.read_bytes()).hexdigest()==rec['sha256']
 # Read FBX GlobalSettings directly, independently of importer axis correction.
 tree,version=parse_fbx.parse(str(path));gs=next(e for e in tree.elems if e.id==b'GlobalSettings');props=next(e for e in gs.elems if e.id==b'Properties70');vals={p.props[0].decode():(p.props[-1].decode() if isinstance(p.props[-1],bytes) else p.props[-1]) for p in props.elems}
 assert vals['UpAxis']==1 and vals['UpAxisSign']==1,(rec['name'],vals)
 assert vals['UnitScaleFactor']==100.0,(rec['name'],vals)
 assert not any(t.area<1e-12 for t in me.loop_triangles),(rec['name'],'degenerate triangles')
 out.append(dict(name=rec['name'],triangles=tris,roundtrip_size_unity_m=size,bottom_center_unity_m=[(lo[0]+hi[0])/2,lo[1],(lo[2]+hi[2])/2],imported_root_rotation=list(ob.rotation_euler),fbx_global_settings=vals,degenerate_triangles=sum(1 for t in me.loop_triangles if t.area<1e-12),one_atlas_material=True,explicit_unity_remap=True))
 print('AUDIT_PASS',rec['name'],tris,flush=True)
base=json.loads((O/'preservation-baseline.json').read_text());changed=[p for p,h in base.items() if hashlib.sha256((R/p).read_bytes()).hexdigest()!=h]
assert not changed,changed
(O/'export-audit.json').write_text(json.dumps(dict(status='PASS',items=out,untouched_dependency_count=len(base),preservation='PASS',limits='Blender FBX roundtrip and metadata/source validation only. No Unity import/runtime acceptance.'),indent=2)+'\n')
print('AUDIT_ALL_PASS',len(out),len(base),flush=True)
