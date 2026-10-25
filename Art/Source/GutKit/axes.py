"""Independent raw FBX world-space axes/unit/pivot checks, including root conversion."""
import bpy,json,sys,math
from pathlib import Path
from mathutils import Matrix,Vector,Euler
from io_scene_fbx import parse_fbx
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
root,ver=parse_fbx.parse(str(B.O/'GutKit.fbx'))
def props(e):
 p=next((c for c in e.elems if c.id==b'Properties70'),None)
 return {c.props[0].decode():[v.decode() if isinstance(v,bytes) else v for v in c.props[4:]] for c in p.elems} if p else {}
settings=props(next(e for e in root.elems if e.id==b'GlobalSettings'))
for k,v in dict(UpAxis=1,UpAxisSign=1,CoordAxis=0,CoordAxisSign=1,FrontAxis=2,FrontAxisSign=1,UnitScaleFactor=100).items():assert settings[k]==[v],(k,settings[k])
objs=next(e for e in root.elems if e.id==b'Objects');cons=next(e for e in root.elems if e.id==b'Connections')
models={e.props[0]:e for e in objs.elems if e.id==b'Model'}
parents={c.props[1]:c.props[2] for c in cons.elems if c.props[0]==b'OO'}
def world(i):
 if i not in models:return Matrix.Identity(4)
 p=props(models[i]);r=[math.radians(v) for v in p.get('Lcl Rotation',[0,0,0])];pre=[math.radians(v) for v in p.get('PreRotation',[0,0,0])]
 m=Matrix.Translation(p.get('Lcl Translation',[0,0,0]))@Euler(pre,'XYZ').to_matrix().to_4x4()@Euler(r,'XYZ').to_matrix().to_4x4()@Matrix.Diagonal(Vector(p.get('Lcl Scaling',[1,1,1])+[1]))
 return world(parents.get(i,0))@m
bpy.ops.wm.open_mainfile(filepath=str(B.O/'GutKit.blend'));build=json.loads((B.O/'metrics/build.json').read_text());rows={}
for e in objs.elems:
 if e.id!=b'Geometry' or e.props[-1]!=b'Mesh':continue
 n=e.props[1].split(b'\x00')[0].decode().removesuffix('_Mesh');raw=next(c for c in e.elems if c.id==b'Vertices').props[0]
 w=world(parents[e.props[0]]);pts=[w@Vector(raw[j:j+3]) for j in range(0,len(raw),3)]
 expected=[Vector(B.u(bpy.data.objects[n].matrix_world@v.co)) for v in bpy.data.objects[n].data.vertices]
 assert len(expected)==len(pts)
 err=max((p-q).length for p,q in zip(pts,expected));assert err<2e-5,(n,err)
 pivot=w.translation;assert pivot.length<1e-6,(n,list(pivot))
 rows[n]={'raw_world_unity_max_error_m':err,'pivot':list(pivot)}
assert set(rows)==set(B.LIMITS)
takes=[e.props[1].split(b'\x00')[0].decode() for e in objs.elems if e.id==b'AnimationStack']
assert set(takes)=={'GullRig|Idle','GullRig|Lunge'},takes
(B.O/'metrics/fbx-axes.json').write_text(json.dumps({'result':'PASS','settings':settings,'animation_stacks':takes,'meshes':rows},indent=2)+'\n')
print('GUT AXES PASS',flush=True)
