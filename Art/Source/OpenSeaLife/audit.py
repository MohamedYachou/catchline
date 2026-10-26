"""Independent FBX roundtrip, topology/palette/skin and all-frame motion tests."""
import bpy,sys,math,json,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
sp=importlib.util.spec_from_file_location('independent_surface',str(B.R/'Art/Source/HarbourV2/audit.py'));A=importlib.util.module_from_spec(sp);sp.loader.exec_module(A)
def geometry(evaluated=False):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg) if evaluated else o;e.data.calc_loop_triangles();rows[o.name]={'vertices':[tuple(e.matrix_world@v.co) for v in e.data.vertices],'triangles':[tuple(t.vertices) for t in e.data.loop_triangles],'faces':[tuple(p.vertices) for p in e.data.polygons]}
 return rows
def activate(rig,clip):
 acts=[a for a in bpy.data.actions if a.name.split('|')[-1]==clip and ('|' not in a.name or a.name.split('|')[0]==rig.name)]
 assert len(acts)==1,(rig.name,clip,[a.name for a in bpy.data.actions]);rig.animation_data.action=acts[0];rig.animation_data.action_slot=acts[0].slots[0];return acts[0]
def poses(name):
 rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE'];sc=bpy.context.scene;res={};info={};expected=3 if name=='DolphinPod' else 1;assert len(rigs)==expected
 for clip,(end,loop) in B.CLIPS[name].items():
  for rig in rigs:
   a=activate(rig,clip);assert abs(a.frame_range[0]-1)<.001 and abs(a.frame_range[1]-end)<.001,(a.name,list(a.frame_range),end)
  res[clip]={};frames=[1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end]
  for f in range(1,end+1):
   sc.frame_set(f)
   for rig in rigs:
    root=rig.pose.bones['Root'];assert root.location.length<2e-6 and max(abs(c) for c in root.rotation_euler)<2e-6
    assert rig.location.length<2e-6
   if f in frames:res[clip][f]=geometry(True)
  def displacement(f):return max((Vector(v)-Vector(w)).length for n,d in res[clip][1].items() for v,w in zip(d['vertices'],res[clip][f][n]['vertices']))
  motion=max(displacement(f) for f in frames);closure=displacement(end);assert motion>.005,(clip,motion)
  if loop:assert closure<2e-5,(clip,closure)
  verts=lambda f:[v for d in res[clip][f].values() for v in d['vertices']]
  if clip=='Leap':
   assert min(v[2] for v in verts(frames[2]))>1.0,'leap must fully clear surface';assert closure<2e-5,'leap must return to waterline start'
  if clip=='Dive':assert max(v[2] for v in verts(end))<0,'gannet must fully enter water'
  info[clip]={'seconds':(end-1)/30,'loop':loop,'sample_frames':frames,'max_vertex_motion_m':motion,'end_vs_start_m':closure,'fixed_root_all_frames':True,'sample_z_ranges':{str(f):[min(v[2] for v in verts(f)),max(v[2] for v in verts(f))] for f in frames}}
 return res,info

def run(name):
 from io_scene_fbx import parse_fbx
 raw,_=parse_fbx.parse(str(B.O/(name+'.fbx')));settings=next(e for e in raw.elems if e.id==b'GlobalSettings');props=next(e for e in settings.elems if e.id==b'Properties70');unit=next(e.props[-1] for e in props.elems if e.props[0]==b'UnitScaleFactor');assert unit==100
 bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));src=B.snapshot();g=geometry();colors={m.name:list(m.diffuse_color) for m in bpy.data.materials};assert src['triangles']<=B.LIMITS[name];assert set(src['materials'])<=set(B.P);assert not list(bpy.data.images)
 assert bpy.data.objects[name].parent is None and bpy.data.objects[name].location.length<1e-7
 for o in bpy.context.scene.objects:
  assert o.type in ('EMPTY','MESH','ARMATURE') and max(abs(c-1) for c in o.scale)<1e-7
  if o.type!='MESH':continue
  assert not o.data.validate(verbose=True,clean_customdata=False);assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert len({i for p in o.data.polygons for i in p.vertices})==len(o.data.vertices);assert all(p.area>1e-12 for p in o.data.polygons),(o.name,'zero area')
  if name in B.CLIPS:assert all(abs(sum(w.weight for w in v.groups)-1)<1e-6 for v in o.data.vertices)
 dims=[src['bounds_unity'][1][i]-src['bounds_unity'][0][i] for i in range(3)];assert max(dims)<5 and min(dims)>.04,(name,dims)
 if name=='DolphinPod':
  for i in range(1,4):assert bpy.data.objects['Dolphin_'+str(i)].parent.name=='DolphinPod' and bpy.data.objects['Dolphin_'+str(i)].location.z==0
 if name=='DriftLog':assert bpy.data.objects['GullSeat'].parent.name=='DriftLog' and abs(dims[2]-1.835)<.04
 ps,ai=poses(name) if name in B.CLIPS else ({},{})
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30;bpy.ops.import_scene.fbx(filepath=str(B.O/(name+'.fbx')));imp=B.snapshot();ig=geometry()
 assert imp['parents']==src['parents'],(imp['parents'],src['parents']);assert imp['triangles']==src['triangles'] and imp['materials']==src['materials'];surface=A.same_geometry(g,ig)
 for o in bpy.context.scene.objects:assert max(abs(c-1) for c in o.scale)<2e-5
 for m in bpy.data.materials:assert max(abs(a-b) for a,b in zip(m.diffuse_color,colors[m.name]))<1e-5
 pi,ii=poses(name) if name in B.CLIPS else ({},{})
 animation={n:{'source':ai[n],'imported':ii[n],'surface_samples':{str(f):A.same_geometry(ps[n][f],pi[n][f]) for f in ps[n]}} for n in ps}
 build=json.loads((B.O/'metrics'/(name+'-build.json')).read_text())
 for e in ('blend','fbx'):assert B.sha(B.O/(name+'.'+e))==build['sha256'][e]
 row={'result':'PASS','name':name,'raw_fbx_unit_scale_factor':unit,'source':src,'imported':imp,'surface':surface,'animation':animation,'dimensions_unity_xyz_m':dims,'materials_linear_rgba':colors,'sha256':build['sha256'],'legacy_import_required':name in B.CLIPS}
 (B.O/'metrics'/(name+'-audit.json')).write_text(json.dumps(row,indent=2)+'\n');print('OPEN SEA AUDIT PASS',name,src['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
