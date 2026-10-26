"""Independent FBX reimport audit and matched original/refined comparison renders."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];NAME=sys.argv[sys.argv.index('--')+1];O=R/'Art/Models/BoatsV2'/NAME;P=O/'renders';P.mkdir(exist_ok=True)
bpy.context.preferences.filepaths.save_version=0

def snapshot(path):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path));bpy.context.view_layer.update();d={}
 for o in bpy.context.scene.objects:
  v=[o.matrix_world@p.co for p in o.data.vertices] if o.type=='MESH' else []
  d[o.name]={'parent':o.parent.name if o.parent else None,'local':[list(r) for r in o.matrix_local],'world':[list(r) for r in o.matrix_world],'triangles':sum(len(p.vertices)-2 for p in o.data.polygons) if v else 0,'verts':sorted([list(p) for p in v]),'bounds':[[min(p[i] for p in v) for i in range(3)],[max(p[i] for p in v) for i in range(3)]] if v else []}
 return d
oldpath=R/f'Assets/Art/Models/Boats/{NAME}.fbx';newpath=O/(NAME+'.fbx');old=snapshot(oldpath);new=snapshot(newpath);diff=[]
for n,d in old.items():
 assert n in new,n
 e=new[n];delta=max(abs(d[k][i][j]-e[k][i][j]) for k in ['local','world'] for i in range(4) for j in range(4));assert delta<.0001,(n,delta)
 assert e['parent']==d['parent']
 diff.append({'node':n,'old_source_world_pivot':[d['world'][i][3] for i in range(3)],'new_source_world_pivot':[e['world'][i][3] for i in range(3)],'max_matrix_delta':delta})
# Preserve every legacy part except the intentionally refined shell, gunwale and rowboat thwart.
unchanged=[n for n in old if old[n]['verts'] and n not in ['Hull','IvoryGunwale']+(['CentreThwart'] if NAME=='Rowboat' else [])]
for n in unchanged:
 a,b=old[n]['verts'],new[n]['verts'];assert len(a)==len(b),(n,len(a),len(b));assert max(abs(x-y) for p,q in zip(a,b) for x,y in zip(p,q))<.0001,n
tris=sum(v['triangles'] for v in new.values());assert tris<=(3000 if NAME=='Rowboat' else 5000)
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  assert all(math.isfinite(c) for p in o.data.vertices for c in p.co)
  assert all(p.area>1e-10 for p in o.data.polygons),(o.name,'zero face')
base=json.load(open(R/'Art/Models/BoatsV2/baseline.json'));assert hashlib.sha256(oldpath.read_bytes()).hexdigest()==base[NAME]['sha256']
# Measure the requested end lift from exported rail vertices, independent of builder formulas.
rv=new['IvoryGunwale']['verts'];mid=max(p[2] for p in rv if abs(p[1])<.05);ymin=min(p[1] for p in rv);ymax=max(p[1] for p in rv)
bow_lift=max(p[2] for p in rv if p[1]<ymin*.96)-mid;stern_lift=max(p[2] for p in rv if p[1]>ymax*.96)-mid
assert abs(bow_lift-(.15 if NAME=='Rowboat' else .18))<.012,(NAME,'bow lift',bow_lift)
assert abs(stern_lift-.08)<.005,(NAME,'stern lift',stern_lift)
record={'sheer_bow_lift_m':bow_lift,'sheer_stern_lift_m':stern_lift,'sheer_mid_rail_top_z':mid,'pass':True,'triangles':tris,'legacy_nodes':len(old),'unchanged_meshes':unchanged,'deck_old_bounds':old['PlankDeck']['bounds'],'deck_new_bounds':new['PlankDeck']['bounds'],'nodes':diff,'new_nodes':sorted(set(new)-set(old)),'original_sha256':base[NAME]['sha256'],'source_fbx_preserved':True,'native_Unity_tested':False}
(O/'validation.json').write_text(json.dumps(record,indent=2));print('AUDIT PASS',NAME,tris,flush=True)
# All images are authoring renders, never runtime screenshots. Both sides receive same shaders, lights and camera.
views={'front-three-quarter':(-1,-1,.85),'side':(-1,0,.02),'back-three-quarter':(1,1,.85),'top':(0,-.00001,1),'low-waterline':(-1,-1,.14),'deck-55':(-math.cos(math.radians(35))*math.cos(math.radians(55)),-math.sin(math.radians(35))*math.cos(math.radians(55)),math.sin(math.radians(55))),'game-exact-45':(-math.cos(math.radians(35))*math.cos(math.radians(45)),-math.sin(math.radians(35))*math.cos(math.radians(45)),math.sin(math.radians(45)))}
if '--audit-only' in sys.argv:sys.exit(0)
variants=[('new',newpath),('old',oldpath)]
if '--preview-only' in sys.argv:variants=variants[:1];views={'front-three-quarter':views['front-three-quarter']}
for variant,path in variants:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path));sc=bpy.context.scene
 for m in bpy.data.materials:
  m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF')
  if bs:bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.8;bs.inputs['Metallic'].default_value=0
 sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=6
 sc.render.resolution_x=800;sc.render.resolution_y=600;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
 sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.25;sc.view_settings.gamma=1
 sc.world=bpy.data.worlds.new('Review soft cool fill');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.74,.80,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.6
 floorz=-.60 if NAME=='Rowboat' else -.83
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,floorz));floor=bpy.context.object;floor.name='REVIEW_ONLY_floor';m=bpy.data.materials.new('REVIEW_ONLY_cream');m.diffuse_color=(.78,.74,.64,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=m.diffuse_color;m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=1;floor.data.materials.append(m)
 for label,pos,power,size,col in [('Key',(-4,-5,8),1050,7,(1,.90,.77)),('Fill',(4,-1,5),350,6,(.72,.85,1)),('Rim',(0,5,6),650,5,(1,.95,.84))]:
  d=bpy.data.lights.new(label,'AREA');d.energy=power;d.size=size;d.color=col;o=bpy.data.objects.new('REVIEW_ONLY_'+label,d);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.objects.new('REVIEW_ONLY_camera',bpy.data.cameras.new('Review'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO'
 target=Vector((0,-.1,.1));points=[Vector(v) for d in [old,new] for ob in d.values() for v in ob['bounds']]
 # Bounding extrema for camera projection; fixed union frustum for each pair.
 corners=[]
 for d in [old,new]:
  for ob in d.values():
   if ob['bounds']:
    lo,hi=ob['bounds'];corners += [Vector((x,y,z)) for x in [lo[0],hi[0]] for y in [lo[1],hi[1]] for z in [lo[2],hi[2]]]
 for label,direction in views.items():
  cam.location=target+Vector(direction).normalized()*18;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update();ps=[cam.matrix_world.inverted()@v for v in corners];spanx=max(p.x for p in ps)-min(p.x for p in ps);spany=max(p.y for p in ps)-min(p.y for p in ps);cam.data.ortho_scale=max(spanx,spany*800/600)*1.20
  sc.render.filepath=str(P/(variant+'-'+label+'.png'));bpy.ops.render.render(write_still=True);print('RENDER PASS',NAME,variant,label,flush=True)
print('REVIEW COMPLETE',NAME,flush=True)
