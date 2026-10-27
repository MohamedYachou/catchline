"""Per-item studio, five Sway samples, close-up scene fixtures; no export stage pollution."""
import bpy,sys,math,json,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
sp=importlib.util.spec_from_file_location('render_stage',str(B.R/'Art/Source/Skerries/render.py'));V=importlib.util.module_from_spec(sp);sp.loader.exec_module(V)
def points():
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
 return [o.evaluated_get(dg).matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith('Review') for v in o.evaluated_get(dg).data.vertices]
def fit(sc,cam,p,d):
 cam.data.type='ORTHO';cam.data.sensor_fit='HORIZONTAL';c=Vector(tuple((min(v[i] for v in p)+max(v[i] for v in p))/2 for i in range(3)));V.look(cam,c,d);b=cam.rotation_euler.to_matrix();u=b@Vector((1,0,0));v=b@Vector((0,1,0));lo,hi=min(q.dot(u) for q in p),max(q.dot(u) for q in p);lv,hv=min(q.dot(v) for q in p),max(q.dot(v) for q in p);c+=u*((lo+hi)/2-c.dot(u))+v*((lv+hv)/2-c.dot(v));V.look(cam,c,d);cam.data.ortho_scale=max(hi-lo,(hv-lv)*sc.render.resolution_x/sc.render.resolution_y)*1.27
def run(kit,only=None):
 O=B.R/'Art/Models'/kit;bpy.ops.wm.open_mainfile(filepath=str(O/(kit+'.blend')));bpy.context.preferences.filepaths.save_version=0;sc,cam=V.stage();sc.cycles.samples=24;rows=([r for r in json.loads((O/'renders/manifest.json').read_text()) if r.get('item')!=only and not r['file'].startswith('renders/Assembly/')] if only else []);ground=V.plane(-.01,'#C9D1CC')
 def visible(item):
  for o in sc.objects:
   if o.type=='MESH' and not o.name.startswith('Review'):o.hide_render=(o.name!=item and (not o.parent or o.parent.name!=item))
 def save(label,size,extra=None):
  sc.render.resolution_x,sc.render.resolution_y=size;path=O/'renders'/(label+'.png');V.render(sc,path);rows.append({'file':path.relative_to(O).as_posix(),'size':list(size),**(extra or {})})
 for item in ([only] if only else B.ITEMS[kit]):
  visible(item);p=points();ground.location.z=min(x.z for x in p)-.008
  if item in ['MoteCloud','KelpStrand']:ground.hide_render=True
  else:ground.hide_render=False
  sc.render.resolution_x=640;sc.render.resolution_y=540
  for label,d in [('front',(0,-1,0)),('back',(0,1,0)),('right',(1,0,0)),('top',(0,0,1)),('three-quarter',(1,-1,1))]:
   fit(sc,cam,p,d);save(item+'/'+label,(640,540),{'item':item,'view':label,'projection':'orthographic'})
  if item=='KelpStrand':
   rig=bpy.data.objects[item];allp=[]
   for f in [1,31,61,91,121]:sc.frame_set(f);allp+=points()
   fit(sc,cam,allp,(.25,-1,.2))
   for i,f in enumerate([1,31,61,91,121]):sc.frame_set(f);save(item+'/Sway-'+str(i),(640,540),{'action':'Sway','frame':f,'seconds':(f-1)/30})
   sc.frame_set(1)
 # Staging is outside the clean production source and FBX.
 ground.hide_render=False
 for o in sc.objects:
  if o.type=='MESH':o.hide_render=False
 placements={}
 if kit=='JigKit':
  placements={'JigPirk':((0,0,-.21),2),'JigFeathers':((.30,.02,-.11),2),'JigLine':((0,0,.79),1),'KelpStrand':((-.83,.55,-1.60),.75),'SeabedRocks':((0,.72,-1.65),.85),'MoteCloud':((0,.15,-.35),1.3)}
  for n,(loc,s) in placements.items():bpy.data.objects[n].location=loc;bpy.data.objects[n].scale=(s,s,s)
  ground.location.z=-1.65;ground.data.materials[0]=V.mat('ReviewSand','#D8C79A');sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.015,.065,.075,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.55
  # Dark teal rear wall suggests a water column without replacing runtime fog.
  bpy.ops.mesh.primitive_plane_add(size=200,location=(0,3,0),rotation=(math.pi/2,0,0));wall=bpy.context.object;wall.name='ReviewWaterBackdrop';wall.data.materials.append(V.mat('ReviewTeal','#163E49'))
  V.look(cam,(0,0,-.35),(0,-1,.04));cam.data.type='ORTHO';cam.data.sensor_fit='HORIZONTAL';cam.data.ortho_scale=5.2
 else:
  placements={'TornNet':((0,0,.014),1),'MendedPatch':((0,0,.015),1),'NettingNeedle':((.44,-.25,.05),1),'TwineBall':((.49,.23,.018),1)}
  for n,(loc,s) in placements.items():bpy.data.objects[n].location=loc
  # Primary assembly shows the torn state; inset separate patch lies alongside the hole.
  bpy.data.objects['MendedPatch'].location=(-.80,.20,.015);placements['MendedPatch']=((-.8,.2,.015),1)
  ground.location.z=0;ground.data.materials[0]=V.mat('ReviewQuay','#C2B199');V.look(cam,(-.09,0,.01),(0,-math.cos(math.radians(55)),math.sin(math.radians(55))));cam.data.type='ORTHO';cam.data.sensor_fit='HORIZONTAL';cam.data.ortho_scale=1.88
 for label,size in [('assembly-1440',(1440,900)),('assembly-844',(844,390))]:save('Assembly/'+label,size,{'projection':'orthographic','camera_blender':list(cam.location),'target':'lure centre' if kit=='JigKit' else 'net panel centre','down_degrees':math.degrees(math.atan(.04)) if kit=='JigKit' else 55,'horizontal_span_m':cam.data.ortho_scale,'placements':placements})
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(kit+'-assembly-review.blend')));(O/'renders/manifest.json').write_text(json.dumps(rows,indent=2)+'\n');print('KIT RENDERS',kit,len(rows),flush=True)
if __name__=='__main__':
 a=sys.argv[sys.argv.index('--')+1:];run(a[0],a[1] if len(a)>1 else None)
