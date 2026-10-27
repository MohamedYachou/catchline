"""Independent reference/source/actual-FBX checks, including unchanged legacy paths."""
import bpy,sys,json,math,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
sp=importlib.util.spec_from_file_location('town_surface',str(B.R/'Art/Source/HarbourV2/audit.py'));A=importlib.util.module_from_spec(sp);sp.loader.exec_module(A)
def rig():return bpy.data.objects['CrewRig']
def skeleton():
 r=rig();return {'name':r.name,'parent':r.parent.name if r.parent else None,'world':[list(x) for x in r.matrix_world],'bones':{b.name:{'parent':b.parent.name if b.parent else None,'matrix':[list(x) for x in b.matrix_local],'head':list(b.head_local),'tail':list(b.tail_local),'deform':b.use_deform} for b in r.data.bones}}
def signature(a):
 curves=[]
 for layer in a.layers:
  for strip in layer.strips:
   for bag in strip.channelbags:
    for f in bag.fcurves:curves.append([f.data_path,f.array_index,[[*k.co,k.interpolation,*k.handle_left,*k.handle_right,k.handle_left_type,k.handle_right_type] for k in f.keyframe_points]])
 return hashlib.sha256(json.dumps(sorted(curves),sort_keys=True).encode()).hexdigest()
def actions():return {a.name.split('|')[-1]:{'range':list(a.frame_range),'curve_sha256':signature(a)} for a in bpy.data.actions}
def samples():
 r=rig();r.data.pose_position='POSE';out={}
 for a in list(bpy.data.actions):
  n=a.name.split('|')[-1];B.bind(r,n);out[n]={}
  for f in range(round(a.frame_range[0]),round(a.frame_range[1])+1):
   bpy.context.scene.frame_set(f);bpy.context.view_layer.update();out[n][f]={b.name:[list(row) for row in r.matrix_world@b.matrix] for b in r.pose.bones}
 return out
def near(a,b,eps=1e-5,path=''):
 if isinstance(a,dict):
  assert a.keys()==b.keys(),(path,a.keys(),b.keys());return max([near(a[k],b[k],eps,path+'/'+str(k)) for k in a]+[0])
 if isinstance(a,(tuple,list)):
  assert len(a)==len(b),path;return max([near(x,y,eps,path) for x,y in zip(a,b)]+[0])
 if isinstance(a,(float,int)) and not isinstance(a,bool):d=abs(a-b);assert d<=eps,(path,a,b,d);return d
 assert a==b,(path,a,b);return 0

def geo(evaluated=False):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg) if evaluated else o;e.data.calc_loop_triangles();rows[o.name]={'vertices':[tuple(e.matrix_world@v.co) for v in e.data.vertices],'triangles':[tuple(t.vertices) for t in e.data.loop_triangles],'faces':[tuple(p.vertices) for p in e.data.polygons]}
 return rows

def walk():
 r=rig();r.data.pose_position='POSE';B.bind(r,'Walk');out={}
 for f in [1,7,13,19,25]:bpy.context.scene.frame_set(f);out[f]=geo(True)
 return out

def run():
 O=B.O
 # Independent read-only baselines, using actual source and shipped FBX.
 bpy.ops.wm.open_mainfile(filepath=str(B.SOURCE));ref=skeleton();acts=actions();source_poses=samples()
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=24;bpy.ops.import_scene.fbx(filepath=str(B.FBX));reference_fbx=skeleton();fbxacts=actions();fbxposes=samples()
 bpy.ops.wm.open_mainfile(filepath=str(O/'Townsfolk.blend'));r=rig();source_skeleton_error=near(ref,skeleton(),0);assert acts==actions(),'Original source curves changed';source_pose_error=near(source_poses,samples(),0)
 assert sorted(o.name for o in bpy.context.scene.objects)==sorted(['CrewRig']+B.NAMES)
 assert len(r.data.bones)==20 and r.parent is None and not list(bpy.data.images)
 summary=B.snap();colors={m.name:list(m.diffuse_color) for m in bpy.data.materials if m.users};r.data.pose_position='REST';sourcegeo=geo();weightinfo={}
 for n in B.NAMES:
  o=bpy.data.objects[n];assert o.parent==r and o.parent_type=='OBJECT' and o.matrix_parent_inverse==r.matrix_world.inverted();assert all(abs(v-1)<1e-8 for v in o.scale);assert o.location.length<1e-8 and o.rotation_euler.to_matrix().is_identity
  assert summary[n]['triangles']<=2500;assert not o.data.validate(verbose=True,clean_customdata=False);assert all(p.area>1e-12 for p in o.data.polygons),(n,'zero area');assert all(math.isfinite(c) for v in o.data.vertices for c in v.co)
  assert len(o.modifiers)==1 and o.modifiers[0].type=='ARMATURE' and o.modifiers[0].object==r
  assert {v.name for v in o.vertex_groups}=={b.name for b in r.data.bones}
  assert all(m.name in B.P for m in o.data.materials)
  err=max(abs(sum(w.weight for w in v.groups)-1) for v in o.data.vertices);assert err<1e-6
  weightinfo[n]={'all_vertices_weighted':True,'normalization_error':err,'group_names_match':True}
 assert bpy.data.objects['Town_Kid']['mesh_scale_only']==.75
 assert .70<summary['Town_Kid']['bounds'][1][2]/summary['Town_Fisherman']['bounds'][1][2]<.80 # hats differ; unadorned scalp=.95*.75
 srwalk=walk();motion={}
 for n in B.NAMES:
  vs=lambda f:srwalk[f][n]['vertices'];motion[n]=max((Vector(x)-Vector(y)).length for x,y in zip(vs(1),vs(7)));assert motion[n]>.04
  assert max((Vector(x)-Vector(y)).length for x,y in zip(vs(1),vs(25)))<1e-5
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=24;bpy.ops.import_scene.fbx(filepath=str(O/'Townsfolk.fbx'));r=rig();import_skeleton_error=near(reference_fbx,skeleton(),1e-6);assert {n:a['range'] for n,a in fbxacts.items()}=={n:a['range'] for n,a in actions().items()};import_pose_error=near(fbxposes,samples(),2e-6)
 assert sorted(o.name for o in bpy.context.scene.objects)==sorted(['CrewRig']+B.NAMES)
 r.data.pose_position='REST';surface=A.same_geometry(sourcegeo,geo());assert B.snap().keys()==summary.keys()
 for m in bpy.data.materials:assert m.name in colors;near(colors[m.name],list(m.diffuse_color),1e-5)
 iw=walk();deformed={str(f):A.same_geometry(srwalk[f],iw[f]) for f in srwalk}
 row=json.loads((O/'metrics/build.json').read_text());assert all(row['sha256'][e]==B.sha(O/('Townsfolk.'+e)) for e in ['blend','fbx'])
 out={'result':'PASS','people':summary,'weights':weightinfo,'skeleton_source_max_error':source_skeleton_error,'skeleton_actual_fbx_reference_max_error':import_skeleton_error,'all_original_source_action_curves_identical':True,'original_actual_fbx_pose_parity':True,'fbx_raw_curve_hashes_identical':fbxacts==actions(),'original_source_pose_max_error':source_pose_error,'original_fbx_pose_max_error':import_pose_error,'actions':acts,'action_frame_count':sum(len(v) for v in source_poses.values()),'bones':20,'source_skeleton':ref,'fbx_skeleton':reference_fbx,'rest_surface':surface,'walk_samples':[1,7,13,19,25],'walk_seconds':1,'walk_deformed_surface':deformed,'walk_motion_metres':motion,'sha256':row['sha256'],'material_rgba_linear':colors}
 (O/'metrics/audit.json').write_text(json.dumps(out,indent=2)+'\n');print('TOWNSFOLK AUDIT PASS',summary,flush=True)
if __name__=='__main__':run()
