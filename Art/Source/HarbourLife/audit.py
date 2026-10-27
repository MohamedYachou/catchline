"""Source and actual FBX metres, topology, weights, action/root and surface audits."""
import bpy,sys,math,json,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
spec=importlib.util.spec_from_file_location('harbour_surface_reference',str(B.R/'Art/Source/HarbourV2/audit.py'));A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
def geometry(evaluated=False):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg) if evaluated else o;e.data.calc_loop_triangles()
  rows[o.name]={'vertices':[tuple(e.matrix_world@v.co) for v in e.data.vertices],'triangles':[tuple(t.vertices) for t in e.data.loop_triangles],'faces':[tuple(p.vertices) for p in e.data.polygons]}
 return rows

def poses(name):
 rig=bpy.data.objects[name+'Rig'];sc=bpy.context.scene;res={};info={}
 assert len(rig.data.bones)<=14
 for clip,end in B.CLIPS[name].items():
  acts=[a for a in bpy.data.actions if a.name.split('|')[-1]==clip];assert len(acts)==1,(clip,[a.name for a in bpy.data.actions])
  a=acts[0];assert abs(a.frame_range[0]-1)<.001 and abs(a.frame_range[1]-end)<.001
  rig.animation_data.action=a;res[clip]={};frames=[1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end];low=1e9;high=-1e9
  for f in range(1,end+1):
   sc.frame_set(f);bpy.context.view_layer.update()
   assert rig.location.length<2e-5 and rig.parent.location.length<2e-5
   root=rig.pose.bones['Root'];assert root.location.length<2e-5 and max(abs(c) for c in root.rotation_euler)<2e-5 and max(abs(c-1) for c in root.scale)<2e-5
   gg=geometry(True);vs=gg[name+'Skin']['vertices'];zmin=min(v[2] for v in vs);low=min(low,zmin);high=max(high,max(v[2] for v in vs))
   assert zmin>=-.004,(name,clip,f,'ground penetration',zmin)
   if f in frames:res[clip][f]=gg
  verts=lambda f:res[clip][f][name+'Skin']['vertices']
  delta=lambda f:max((Vector(p)-Vector(q)).length for p,q in zip(verts(1),verts(f)))
  motion=max(delta(f) for f in frames);closure=delta(end)
  assert motion>(.0008 if clip=='Sleep' else .005),(name,clip,motion)
  assert closure<3e-5,(name,clip,'loop',closure)
  info[clip]={'action_name':a.name,'frames':[1,end],'seconds':(end-1)/30,'loop':True,'samples':frames,'max_vertex_motion_m':motion,'end_vs_start_m':closure,'root_stationary_all_frames':True,'allframe_min_z_m':low,'allframe_max_z_m':high}
 rig.animation_data.action=None
 for pb in rig.pose.bones:pb.matrix_basis.identity()
 bpy.context.view_layer.update()
 return res,info

def run(name):
 bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));src=B.snapshot();g=geometry();colors={m.name:list(m.diffuse_color) for m in bpy.data.materials}
 assert src['triangles']<=B.LIMITS[name]
 assert set(src['materials'])<=set(B.P)
 assert bpy.data.objects[name].parent is None and bpy.data.objects[name].location.length<1e-7
 assert not list(bpy.data.images)
 for o in bpy.context.scene.objects:
  assert max(abs(c-1) for c in o.scale)<1e-7 and o.location.length<1e-7
  if o.type!='MESH':continue
  assert not o.data.validate(verbose=True,clean_customdata=False)
  assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert len({i for p in o.data.polygons for i in p.vertices})==len(o.data.vertices)
  assert all(p.area>1e-12 for p in o.data.polygons),(name,'zero-area face')
  assert all(abs(sum(w.weight for w in v.groups)-1)<1e-6 for v in o.data.vertices)
 bounds=src['bounds_unity'];size=[bounds[1][i]-bounds[0][i] for i in range(3)]
 assert abs(size[1]-({'Dog':.55,'Cat':.3}[name]))<1e-6,(name,size)
 assert abs(bounds[0][1])<1e-6
 assert bounds[1][2]>.10,'forward muzzle must point +UnityZ'
 ps,ai=poses(name)
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30;bpy.ops.import_scene.fbx(filepath=str(B.O/(name+'.fbx')))
 rig=bpy.data.objects[name+'Rig'];rig.animation_data.action=None
 for pb in rig.pose.bones:pb.matrix_basis.identity()
 bpy.context.view_layer.update();imp=B.snapshot();ig=geometry();assert imp['parents']==src['parents']
 assert imp['triangles']==src['triangles'] and imp['materials']==src['materials'];surface=A.same_geometry(g,ig)
 for o in bpy.context.scene.objects:
  assert max(abs(c-1) for c in o.scale)<2e-5
  if o.parent is None:assert o.location.length<2e-5
 for m in bpy.data.materials:assert max(abs(a-b) for a,b in zip(m.diffuse_color,colors[m.name]))<1e-5
 pi,ii=poses(name)
 animation={n:{'source':ai[n],'imported':ii[n],'samples':{str(f):A.same_geometry(ps[n][f],pi[n][f]) for f in ps[n]}} for n in ps}
 build=json.loads((B.O/'metrics'/(name+'-build.json')).read_text())
 for e in ('blend','fbx'):assert B.sha(B.O/(name+'.'+e))==build['sha256'][e]
 row={'result':'PASS','name':name,'source':src,'imported':imp,'surface':surface,'animation':animation,'dimensions_unity_xyz_m':size,'materials':colors,'sha256':build['sha256'],'bone_count':len(rig.data.bones)}
 (B.O/'metrics'/(name+'-audit.json')).write_text(json.dumps(row,indent=2)+'\n');print('HARBOUR AUDIT PASS',name,src['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
