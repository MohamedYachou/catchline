"""Independent actual-FBX surface, world bounds and sampled deformation audit."""
import bpy,sys,math,json,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
spec=importlib.util.spec_from_file_location('independent_surface',str(B.R/'Art/Source/HarbourV2/audit.py'));A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
def geometry(evaluated=False):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg) if evaluated else o;e.data.calc_loop_triangles();rows[o.name]={'vertices':[tuple(e.matrix_world@v.co) for v in e.data.vertices],'triangles':[tuple(t.vertices) for t in e.data.loop_triangles],'faces':[tuple(p.vertices) for p in e.data.polygons]}
 return rows

def poses(name):
 rig=bpy.data.objects[name+'Rig'];sc=bpy.context.scene;res={};info={};assert len(rig.data.bones)==7
 for action,(end,loop) in B.CLIPS[name].items():
  acts=[a for a in bpy.data.actions if a.name.split('|')[-1]==action];assert len(acts)==1,(action,[a.name for a in bpy.data.actions])
  a=acts[0];assert abs(a.frame_range[0]-1)<.001 and abs(a.frame_range[1]-end)<.001
  rig.animation_data.action=a;res[action]={};frames=[1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end]
  for f in range(1,end+1):
   sc.frame_set(f);assert rig.location.length<1e-6 and rig.parent.location.length<1e-6
   assert rig.pose.bones['Root'].location.length<1e-6 and max(abs(c) for c in rig.pose.bones['Root'].rotation_euler)<1e-6
   if f in frames:res[action][f]=geometry(True)
  verts=lambda f:res[action][f][name+'Skin']['vertices']
  delta=lambda f:max((Vector(p)-Vector(q)).length for p,q in zip(verts(1),verts(f)))
  motion=max(delta(f) for f in frames);closure=delta(end);assert motion>.004,(action,motion)
  if loop:assert closure<2e-5,(action,closure)
  else:assert max(v[2] for v in verts(end))<-.55
  info[action]={'action_name':a.name,'frames':[1,end],'seconds':(end-1)/30,'loop':loop,'samples':frames,'max_vertex_motion_m':motion,'end_vs_start_m':closure,'root_stationary_all_frames':True}
 return res,info

def run(name):
 from io_scene_fbx import parse_fbx
 raw,_=parse_fbx.parse(str(B.O/(name+'.fbx')));settings=next(e for e in raw.elems if e.id==b'GlobalSettings');props=next(e for e in settings.elems if e.id==b'Properties70');unit=next(e.props[-1] for e in props.elems if e.props[0]==b'UnitScaleFactor');assert unit==100
 bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));src=B.snapshot();g=geometry();colors={m.name:list(m.diffuse_color) for m in bpy.data.materials}
 assert src['triangles']<=B.LIMITS[name];assert set(src['materials'])<=set(B.P);assert not list(bpy.data.images)
 assert bpy.data.objects[name].parent is None and bpy.data.objects[name].location.length<1e-7
 for o in bpy.context.scene.objects:
  assert max(abs(c-1) for c in o.scale)<1e-7
  assert o.type in ('EMPTY','MESH','ARMATURE')
  if o.type!='MESH':continue
  assert not o.data.validate(verbose=True,clean_customdata=False);assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert len({i for p in o.data.polygons for i in p.vertices})==len(o.data.vertices);assert all(p.area>1e-12 for p in o.data.polygons)
  if name in B.CLIPS:assert all(abs(sum(w.weight for w in v.groups)-1)<1e-6 for v in o.data.vertices)
 bounds=src['bounds_unity'];size=[bounds[1][i]-bounds[0][i] for i in range(3)]
 assert max(size)<4 and min(size)>.08,(name,size,'oversized presentation object')
 if name=='ChannelMarkers':
  for n in ('RedCan','GreenCone'):
   ob=bpy.data.objects[n];vs=[ob.children[0].matrix_world@v.co for v in ob.children[0].data.vertices];assert abs(sum([min(p.x for p in vs),max(p.x for p in vs)])/2-ob.location.x)<1e-6
   assert ob.location.z==0 and ob.location.y==0
 if name=='PotBuoyLine':assert abs(size[0]-3.024)<.04
 ps,ai=poses(name) if name in B.CLIPS else ({},{})
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30;bpy.ops.import_scene.fbx(filepath=str(B.O/(name+'.fbx')))
 imp=B.snapshot();ig=geometry();assert imp['parents']==src['parents'];assert imp['triangles']==src['triangles'] and imp['materials']==src['materials'];surface=A.same_geometry(g,ig)
 for o in bpy.context.scene.objects:assert max(abs(c-1) for c in o.scale)<2e-5
 for m in bpy.data.materials:assert max(abs(a-b) for a,b in zip(m.diffuse_color,colors[m.name]))<1e-5
 pi,ii=poses(name) if name in B.CLIPS else ({},{})
 animation={n:{'source':ai[n],'imported':ii[n],'samples':{str(f):A.same_geometry(ps[n][f],pi[n][f]) for f in ps[n]}} for n in ps}
 build=json.loads((B.O/'metrics'/(name+'-build.json')).read_text())
 for e in ('blend','fbx'):assert B.sha(B.O/(name+'.'+e))==build['sha256'][e]
 row={'result':'PASS','name':name,'raw_fbx_unit_scale_factor':unit,'source':src,'imported':imp,'surface':surface,'animation':animation,'dimensions_unity_xyz_m':size,'materials':colors,'sha256':build['sha256']}
 (B.O/'metrics'/(name+'-audit.json')).write_text(json.dumps(row,indent=2)+'\n');print('GULL AUDIT PASS',name,src['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
