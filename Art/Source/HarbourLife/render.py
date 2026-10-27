"""Five true animal studios and five poses per action; no runtime claim."""
import bpy,sys,math,json,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
sp=importlib.util.spec_from_file_location('life_render_reference',str(B.R/'Art/Source/Skerries/render.py'));V=importlib.util.module_from_spec(sp);sp.loader.exec_module(V)
def points():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 return [o.evaluated_get(dg).matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('Review') for v in o.evaluated_get(dg).data.vertices]
def fitted(sc,cam,p,direction):
 cam.data.type='ORTHO';cam.data.sensor_fit='HORIZONTAL';c=Vector(tuple((min(v[i] for v in p)+max(v[i] for v in p))*.5 for i in range(3)));V.look(cam,c,direction);bpy.context.view_layer.update()
 basis=cam.rotation_euler.to_matrix();u=basis@Vector((1,0,0));v=basis@Vector((0,1,0));lu,hu=min(q.dot(u) for q in p),max(q.dot(u) for q in p);lv,hv=min(q.dot(v) for q in p),max(q.dot(v) for q in p)
 c+=u*((lu+hu)/2-c.dot(u))+v*((lv+hv)/2-c.dot(v));V.look(cam,c,direction);cam.data.ortho_scale=max(hu-lu,(hv-lv)*sc.render.resolution_x/sc.render.resolution_y)*1.30;bpy.context.view_layer.update()
def run(name):
 bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));sc,cam=V.stage();sc.cycles.samples=24;V.plane(-.008,'#CED4CE');p=points();rows=[];out=B.O/'renders'/name
 def save(label,size,extra=None):
  sc.render.resolution_x,sc.render.resolution_y=size;path=out/(label+'.png')
  from bpy_extras.object_utils import world_to_camera_view
  bpy.context.view_layer.update();cs=[world_to_camera_view(sc,cam,p) for p in points()];margin=[min(v.x for v in cs),min(v.y for v in cs),max(v.x for v in cs),max(v.y for v in cs)]
  assert min(margin[:2])>.03 and max(margin[2:])<.97,('crop',name,label,margin)
  V.render(sc,path);rows.append({'file':path.relative_to(B.O).as_posix(),'view':label,'size':size,'source_sha256':B.sha(B.O/(name+'.blend')),'projected_bounds_01':margin,**(extra or {})})
 sc.render.resolution_x=720;sc.render.resolution_y=600
 for label,d in [('three-quarter',(1,-1,.7)),('front',(0,-1,0)),('right',(1,0,0)),('back',(0,1,0)),('left',(-1,0,0))]:
  fitted(sc,cam,p,d);save(label,(720,600),{'projection':'orthographic','pose':'rest'})
 rig=bpy.data.objects[name+'Rig'];sc.render.resolution_x=640;sc.render.resolution_y=480
 for clip,end in B.CLIPS[name].items():
  rig.animation_data.action=bpy.data.actions[clip];frames=[1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end];allpoints=[]
  for f in frames:sc.frame_set(f);allpoints+=points()
  fitted(sc,cam,allpoints,(1,-1,.65))
  for i,f in enumerate(frames):sc.frame_set(f);save('action-'+clip+'-'+str(i),(640,480),{'action':clip,'frame':f,'seconds':(f-1)/30,'projection':'orthographic','common_camera_within_action':True})
 (B.O/'renders'/(name+'.json')).write_text(json.dumps(rows,indent=2)+'\n');print('HARBOUR RENDERS',name,len(rows),flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
