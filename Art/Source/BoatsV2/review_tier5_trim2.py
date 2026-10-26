"""Independent FBX reimport audit and matched original/refined comparison renders."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
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
# Preserve all cabin, deck, machinery, attachments and variants exactly.
b=json.load(open(O/'build-metrics.json'));unchanged=[n for n in old if old[n]['verts'] and n not in b['modified_legacy_meshes']]
for n in unchanged:
 a,c=old[n]['verts'],new[n]['verts'];assert len(a)==len(c),(n,len(a),len(c))
 # FBX rounds coordinates/reorders ties; compare bidirectional vertex positions.
 for source,target in [(a,c),(c,a)]:
  tree=KDTree(len(target))
  for i,p in enumerate(target):tree.insert(Vector(p),i)
  tree.balance();assert max(tree.find(Vector(p))[2] for p in source)<.0001,n
tris=sum(v['triangles'] for v in new.values());assert tris<=b['triangle_cap']
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  assert all(math.isfinite(c) for p in o.data.vertices for c in p.co)
  # Historical meshes may contain degenerate original faces: new/modified parts must not.
  if o.name not in unchanged:assert all(p.area>1e-10 for p in o.data.polygons),(o.name,'zero face')
assert hashlib.sha256(oldpath.read_bytes()).hexdigest()==b['source_sha256']
record={'pass':True,'triangles':tris,'original_triangles':b['original_triangles'],'triangle_cap':b['triangle_cap'],'legacy_nodes':len(old),'unchanged_meshes':unchanged,'deck_old_bounds':old['PlankDeck']['bounds'],'deck_new_bounds':new['PlankDeck']['bounds'],'nodes':diff,'new_nodes':sorted(set(new)-set(old)),'original_sha256':b['source_sha256'],'source_fbx_preserved':True,'native_Unity_tested':False}
record['exported_fbx_sha256']=hashlib.sha256(newpath.read_bytes()).hexdigest()
record['material_names']=sorted({m.name for m in bpy.data.materials})
palette_text=(R/'Assets/Scripts/Game/ArtLibrary.cs').read_text()
record['unknown_material_names']=[n for n in record['material_names'] if chr(34)+n.split('.')[0]+chr(34) not in palette_text]
assert not record['unknown_material_names'],record['unknown_material_names']
(O/'validation.json').write_text(json.dumps(record,indent=2));print('AUDIT PASS',NAME,tris,flush=True)
# All images are authoring renders, never runtime screenshots. Both sides receive same shaders, lights and camera.
views={'front-three-quarter':(-1,-1,.85),'side':(-1,0,.02),'back-three-quarter':(1,1,.85),'top':(0,-.00001,1),'low-waterline':(-1,-1,.14),'deck-55':(-math.cos(math.radians(35))*math.cos(math.radians(55)),-math.sin(math.radians(35))*math.cos(math.radians(55)),math.sin(math.radians(55))),'game-exact-45':(-math.cos(math.radians(35))*math.cos(math.radians(45)),-math.sin(math.radians(35))*math.cos(math.radians(45)),math.sin(math.radians(45)))}
if '--audit-only' in sys.argv:sys.exit(0)
variants=[('new',newpath),('old',oldpath)]
if '--new-only' in sys.argv:variants=variants[:1]
if '--old-only' in sys.argv:variants=variants[1:]
if '--preview-only' in sys.argv:variants=variants[:1];views={k:views[k] for k in ['front-three-quarter','side','game-exact-45']}
for variant,path in variants:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(path));sc=bpy.context.scene
 for o in sc.objects:
  p=o
  while p:
   if p.name in ['RawBuckets','NetModule2','OptionalRodModule']:o.hide_render=True;break
   p=p.parent
 for m in bpy.data.materials:
  m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF')
  if bs:bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.8;bs.inputs['Metallic'].default_value=0
 sc.render.engine='CYCLES';sc.cycles.device='CPU';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=6
 sc.render.resolution_x=800;sc.render.resolution_y=600;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=False
 sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.25;sc.view_settings.gamma=1
 sc.world=bpy.data.worlds.new('Review soft cool fill');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.74,.80,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.6
 floorz=min(ob['bounds'][0][2] for ob in new.values() if ob['bounds'])-.13
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,floorz));floor=bpy.context.object;floor.name='REVIEW_ONLY_floor';m=bpy.data.materials.new('REVIEW_ONLY_cream');m.diffuse_color=(.78,.74,.64,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=m.diffuse_color;m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=1;floor.data.materials.append(m)
 for label,pos,power,size,col in [('Key',(-4,-5,8),1050,7,(1,.90,.77)),('Fill',(4,-1,5),350,6,(.72,.85,1)),('Rim',(0,5,6),650,5,(1,.95,.84))]:
  d=bpy.data.lights.new(label,'AREA');d.energy=power;d.size=size;d.color=col;o=bpy.data.objects.new('REVIEW_ONLY_'+label,d);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
 cam=bpy.data.objects.new('REVIEW_ONLY_camera',bpy.data.cameras.new('Review'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO'
 target=Vector((0,-.1,.4));points=[Vector(v) for d in [old,new] for ob in d.values() for v in ob['bounds']]
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
