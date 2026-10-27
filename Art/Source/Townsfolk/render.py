"""Original Walk-bound studio/sequence/lineup fixtures. Clean export untouched."""
import bpy,sys,math,json,importlib.util
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
sp=importlib.util.spec_from_file_location('town_stage',str(B.R/'Art/Source/Skerries/render.py'));V=importlib.util.module_from_spec(sp);sp.loader.exec_module(V)
def points(objects):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();return [e.matrix_world@v.co for o in objects for e in [o.evaluated_get(dg)] for v in e.data.vertices]
def fit(sc,cam,p,d,margin=1.23):
 cam.data.type='ORTHO';cam.data.sensor_fit='HORIZONTAL';c=Vector(tuple((min(v[i] for v in p)+max(v[i] for v in p))/2 for i in range(3)));V.look(cam,c,d);b=cam.rotation_euler.to_matrix();u=b@Vector((1,0,0));v=b@Vector((0,1,0));lo,hi=min(q.dot(u) for q in p),max(q.dot(u) for q in p);lv,hv=min(q.dot(v) for q in p),max(q.dot(v) for q in p);c+=u*((lo+hi)/2-c.dot(u))+v*((lv+hv)/2-c.dot(v));V.look(cam,c,d);cam.data.ortho_scale=max(hi-lo,(hv-lv)*sc.render.resolution_x/sc.render.resolution_y)*margin

def run(only=None):
 O=B.O;bpy.ops.wm.open_mainfile(filepath=str(O/'Townsfolk.blend'));bpy.context.preferences.filepaths.save_version=0;sc,cam=V.stage();ground=V.plane(-.009,'#D5D7CB');rig=bpy.data.objects['CrewRig'];rig.data.pose_position='POSE';B.bind(rig,'Walk');rows=[]
 if only and (O/'renders/manifest.json').exists():rows=[r for r in json.loads((O/'renders/manifest.json').read_text()) if r.get('person')!=only and r.get('view')!='line-up']
 def save(label,objects,extra=None,size=(640,600)):
  sc.render.resolution_x,sc.render.resolution_y=size;pp=points(objects);uv=[world_to_camera_view(sc,cam,p) for p in pp];crop=[min(p.x for p in uv),max(p.x for p in uv),min(p.y for p in uv),max(p.y for p in uv)];assert crop[0]>.025 and crop[1]<.975 and crop[2]>.025 and crop[3]<.975,(label,crop)
  path=O/'renders'/(label+'.png');V.render(sc,path);rows.append({'file':path.relative_to(O).as_posix(),'size':list(size),'projection':'orthographic','horizontal_span_m':cam.data.ortho_scale,'camera':list(cam.location),'image_bounds_normalized':crop,**(extra or {})})
 for n in ([only] if only else B.NAMES):
  objs=[bpy.data.objects[n]]
  for o in rig.children:o.hide_render=o.name!=n
  sc.frame_set(1);p=points(objs);sc.render.resolution_x=640;sc.render.resolution_y=600
  for name,d in [('front',(0,-1,0)),('back',(0,1,0)),('left',(-1,0,0)),('right',(1,0,0)),('three-quarter',(.8,-1,.5))]:
   fit(sc,cam,p,d);save(n+'/'+name,objs,{'person':n,'view':name,'action':'Walk','frame':1})
  allp=[]
  for f in [1,7,13,19,25]:sc.frame_set(f);allp+=points(objs)
  fit(sc,cam,allp,(.7,-1,.25))
  for i,f in enumerate([1,7,13,19,25]):sc.frame_set(f);save(n+'/Walk-'+str(i),objs,{'person':n,'action':'Walk','view':'Walk-'+str(i),'frame':f,'seconds':(f-1)/24})
 # Six copies at identical object/armature scale, child reduction is mesh only.
 for o in rig.children:o.hide_render=True
 lineup=[];names=B.NAMES
 for i,n in enumerate(names):
  nr=rig.copy();nr.data=rig.data.copy();sc.collection.objects.link(nr);nr.name='ReviewRig_'+n;nr.location.x=(i-2.5)*.68;nr.data.pose_position='POSE';B.bind(nr,'Walk')
  o=bpy.data.objects[n].copy();o.data=bpy.data.objects[n].data.copy();o.parent=nr;o.name='Review_'+n;sc.collection.objects.link(o);o.hide_render=False;o.modifiers[0].object=nr;lineup.append(o)
 with bpy.data.libraries.load(str(B.SOURCE),link=False) as (src,dst):dst.objects=['CrewRig','Body','Outfit_Captain','Hat_CaptainCap']
 loaded={o.name:o for o in dst.objects if o};ref=next(o for o in loaded.values() if o.type=='ARMATURE')
 for o in loaded.values():
  if not o.users_collection:sc.collection.objects.link(o)
 ref.location.x=2.5*.68;ref.data.pose_position='POSE';B.bind(ref,'Walk')
 reference_meshes=[o for o in loaded.values() if o.type=='MESH']
 for o in reference_meshes:o.hide_render=False
 lineup+=reference_meshes;sc.frame_set(1);bpy.context.view_layer.update();sc.render.resolution_x=1800;sc.render.resolution_y=660
 fit(sc,cam,points(lineup),(0,-1,.10),1.13);save('Lineup/all-five-with-crew',lineup,{'view':'line-up','left_to_right':names+['Original CrewRig Captain'],'all_object_armature_scales':[1,1,1],'child_mesh_scale':.75},size=(1800,660))
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'Townsfolk-lineup-review.blend'));(O/'renders/manifest.json').write_text(json.dumps(rows,indent=2)+'\n');print('TOWNSFOLK RENDER PASS',len(rows),flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else None)
