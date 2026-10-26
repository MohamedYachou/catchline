"""Independently reimport exported FBX, inspect units/bounds/geometry then render it."""
import bpy,sys,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
from io_scene_fbx import parse_fbx
HERE=Path(__file__).resolve().parent;R=HERE.parents[3];O=R/'Art/Models/BoatsV2/JigBoatV1';P=O/'renders';FBX=O/'JigBoatV1.fbx'
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(FBX));bpy.context.view_layer.update()
obs=list(bpy.context.scene.objects);rows=[];points=[];metrics=json.loads((O/'build-metrics.json').read_text());node_errors=[]
for o in obs:
 if o.type!='MESH':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];assert all(math.isfinite(x) for v in vs for x in v),o.name
 assert all(p.area>1e-10 for p in o.data.polygons),o.name
 lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)];span=[hi[i]-lo[i] for i in range(3)];points+=vs
 assert -2<lo[0]<2 and -4<lo[1]<4 and -1<lo[2]<2.1,(o.name,lo)
 assert hi[0]<2 and hi[1]<4 and hi[2]<2.1,(o.name,hi)
 assert 'REVIEW' not in o.name.upper()
 assert o.parent.name=='Catchline_JigBoatV1',o.name
 b=metrics['objects'][o.name];delta=max(abs(b['world'][i][j]-o.matrix_world[i][j]) for i in range(4) for j in range(4));assert delta<1e-5,(o.name,delta)
 rows.append({'name':o.name,'parent':o.parent.name,'world_min_m':lo,'world_max_m':hi,'span_m':span,'local_scale':list(o.scale),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons),'max_authoring_world_matrix_delta':delta,'materials':[m.name for m in o.data.materials]})
root,_=parse_fbx.parse(str(FBX));settings=next(e for e in root.elems if e.id==b'GlobalSettings');props=next(e for e in settings.elems if e.id==b'Properties70');unit=next(e.props[-1] for e in props.elems if e.props[0]==b'UnitScaleFactor');assert unit==100,unit
tri=sum(r['triangles'] for r in rows);assert tri==metrics['triangles'] and tri<=13000
lo=[min(v[i] for v in points) for i in range(3)];hi=[max(v[i] for v in points) for i in range(3)]
# Physically empty crew rectangle above the deck, cabin forward, tray/reels outboard.
def clip_face(poly,axis,value,greater):
 result=[]
 for a,b in zip(poly,poly[1:]+poly[:1]):
  ia=a[axis]>=value if greater else a[axis]<=value;ib=b[axis]>=value if greater else b[axis]<=value
  if ia:result.append(a)
  if ia!=ib:
   t=(value-a[axis])/(b[axis]-a[axis]);result.append(a+(b-a)*t)
 return result
obstacles=[]
for o in obs:
 if o.type!='MESH':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices]
 for face in o.data.polygons:
  poly=[vs[i] for i in face.vertices]
  for axis,low,high in [(0,-.8,.65),(1,-.95,2.65),(2,.035,1.7)]:
   poly=clip_face(poly,axis,low,True)
   if poly:poly=clip_face(poly,axis,high,False)
   if not poly:break
  if poly:obstacles.append(o.name);break
assert not obstacles,obstacles
record={'pass':True,'triangles':tri,'triangle_cap':13000,'mesh_count':len(rows),'node_count':len(obs),'unit_scale_factor':unit,'source_axis':'X right, -Y bow, Z up','world_min_m':lo,'world_max_m':hi,'fbx_sha256':hashlib.sha256(FBX.read_bytes()).hexdigest(),'no_review_or_oversized_mesh':True,'clear_walkway_box_m':[[-.8,-.95,.035],[.65,2.65,1.7]],'walkway_obstacles':obstacles,'lamp_count':len([r for r in rows if r['name'].startswith('SquidLamp_')]),'reel_count':len([r for r in rows if r['name'].startswith('JigReel_')]),'native_Unity_tested':False}
assert record['lamp_count']==8 and record['reel_count']==3
(O/'bounds-audit.json').write_text(json.dumps({'pass':True,'unit_scale_factor':unit,'fbx_sha256':record['fbx_sha256'],'rows':rows,'world_min_m':lo,'world_max_m':hi},indent=2));(O/'validation.json').write_text(json.dumps(record,indent=2));print('JIG AUDIT PASS',tri,len(rows),'UNIT',unit,flush=True)
# Verify blend/FBX vertex positions, not just matrices or counts.
sourcepts={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in obs if o.type=='MESH'}
bpy.ops.wm.open_mainfile(filepath=str(O/'JigBoatV1.blend'));bpy.context.view_layer.update();maxerr=0
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 vs=[o.matrix_world@v.co for v in o.data.vertices];target=sourcepts[o.name];assert len(vs)==len(target)
 tree=KDTree(len(target))
 for i,v in enumerate(target):tree.insert(v,i)
 tree.balance();maxerr=max(maxerr,max(tree.find(v)[2] for v in vs))
assert maxerr<.0001,maxerr
record['blend_fbx_max_vertex_delta_m']=maxerr;(O/'validation.json').write_text(json.dumps(record,indent=2));print('BLEND PARITY',maxerr,flush=True)
if '--audit-only' in sys.argv:sys.exit(0)
views={'front-three-quarter':(-1,-1,.85),'side':(-1,0,.02),'back-three-quarter':(1,1,.85),'top':(0,-.00001,1),'low-waterline':(-1,-1,.14),'deck-55':(-math.cos(math.radians(35))*math.cos(math.radians(55)),-math.sin(math.radians(35))*math.cos(math.radians(55)),math.sin(math.radians(55))),'game-exact-45':(-math.cos(math.radians(35))*math.cos(math.radians(45)),-math.sin(math.radians(35))*math.cos(math.radians(45)),math.sin(math.radians(45)))}
def imported(path,offset=(0,0,0),tag=''):
 prev=set(bpy.context.scene.objects);bpy.ops.import_scene.fbx(filepath=str(path));new=list(set(bpy.context.scene.objects)-prev);bpy.context.view_layer.update()
 for o in new:
  if not o.parent:o.location+=Vector(offset)
 bpy.context.view_layer.update()
 for o in new:
  if tag:o.name=tag+'_'+o.name
 return new

def stage(res=(1000,750)):
 sc=bpy.context.scene
 for m in bpy.data.materials:
  m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF')
  if bs:bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.8;bs.inputs['Metallic'].default_value=0
 sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=6
 sc.render.resolution_x,sc.render.resolution_y=res;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
 sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.25
 sc.world=bpy.data.worlds.new('Review cool fill');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.74,.80,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.6
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.85));f=bpy.context.object;f.name='REVIEW_ONLY_floor';m=bpy.data.materials.new('REVIEW_ONLY_cream');m.diffuse_color=(.78,.74,.64,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=m.diffuse_color;m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=1;f.data.materials.append(m)
 for label,pos,power,size,col in [('Key',(-4,-5,8),1050,7,(1,.90,.77)),('Fill',(4,-1,5),350,6,(.72,.85,1)),('Rim',(0,5,6),650,5,(1,.95,.84))]:
  d=bpy.data.lights.new(label,'AREA');d.energy=power;d.size=size;d.color=col;o=bpy.data.objects.new('REVIEW_ONLY_'+label,d);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.objects.new('REVIEW_ONLY_camera',bpy.data.cameras.new('Review'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';return sc,cam

def render(sc,cam,objs,label,direction,target=None):
 pts=[o.matrix_world@v.co for o in objs if o.type=='MESH' for v in o.data.vertices];lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)));hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)));target=(lo+hi)/2 if target is None else Vector(target)
 cam.location=target+Vector(direction).normalized()*30;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();iv=cam.matrix_world.inverted();ps=[iv@v for v in pts];spanx=max(p.x for p in ps)-min(p.x for p in ps);spany=max(p.y for p in ps)-min(p.y for p in ps);cam.data.ortho_scale=max(spanx,spany*sc.render.resolution_x/sc.render.resolution_y)*1.17
 # Centre projected geometry, preserving orthographic direction.
 dx=(max(p.x for p in ps)+min(p.x for p in ps))/2;dy=(max(p.y for p in ps)+min(p.y for p in ps))/2;cam.location+=cam.rotation_euler.to_matrix()@Vector((dx,dy,0))
 sc.render.filepath=str(P/(label+'.png'));bpy.ops.render.render(write_still=True);print('JIG RENDER PASS',label,flush=True)
if '--lineup-only' not in sys.argv:
 bpy.ops.wm.read_factory_settings(use_empty=True);objs=imported(FBX);sc,cam=stage()
 useviews=views if '--preview-only' not in sys.argv else {k:views[k] for k in ['side','game-exact-45']}
 for label,d in useviews.items():
  if '--remaining-only' in sys.argv and label in ['side','game-exact-45'] and (P/(label+'.png')).exists():continue
  render(sc,cam,objs,label,d)
if '--preview-only' not in sys.argv:
 bpy.ops.wm.read_factory_settings(use_empty=True);allobs=[]
 for label,name,x in [('COMPACT','CompactFisherV1',-4.65),('JIG','JigBoatV1',0),('PREP','PrepFisherV1',4.65)]:allobs+=imported(R/'Art/Models/BoatsV2'/name/(name+'.fbx'),(x,0,0),label)
 sc,cam=stage((1600,1000));render(sc,cam,allobs,'lineup-top',(0,-.00001,1));render(sc,cam,allobs,'lineup-three-quarter',(0,-1,1))
print('JIG REVIEW COMPLETE',flush=True)
