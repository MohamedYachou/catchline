"""TIER5-103 production export from approved Tier5 hull and approved two-rig design."""
import bpy, math, json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[2]; O=R/'Art/Models/Tier5DeepLines103';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'Art/Models/Tier5Production071/Tier5FisherV1.blend'))
scene=bpy.context.scene
original_meshes={o.name for o in bpy.data.objects if o.type=='MESH'}
original_hashes={}
import hashlib
for rel in ['Art/Models/Tier5Production071/Tier5FisherV1.blend','Assets/Art/Models/Boats/Tier5FisherV1.fbx','Art/Source/export_tier5_071.py','Art/Models/Tier5DeepLines102/Tier5DeepLines102-preview.blend']:
 original_hashes[rel]=hashlib.sha256((R/rel).read_bytes()).hexdigest()
# Existing source contains both storage variants; show one, without changing source.
for ob in bpy.data.objects:
 if ob.parent and ob.parent.name=='RawBuckets':ob.hide_render=True
 if 'Engineer service' in ob.name or 'Service status' in ob.name:ob.hide_render=True
mats={n:bpy.data.materials.get(n) for n in ['M_HullNavy','M_RailIvory','M_DeckWood','M_Rubber','M_SeaTeal','M_Steel','M_SafetyOrange','M_Rope']}
def mat(n,color):
 if mats.get(n):return mats[n]
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);mats[n]=m;return m
mat('M_Rope',tuple(((v/255+.055)/1.055)**2.4 for v in [209,175,118]))
opt=[]
def cyl(name,a,b,r,material, optional=False):
 a,b=Vector(a),Vector(b);d=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(a+b)/2)
 ob=bpy.context.object;ob.name=name;ob.rotation_euler=d.to_track_quat('Z','Y').to_euler();ob.data.materials.append(mats[material])
 if optional:opt.append(ob)
 return ob
def box(n,p,s,m,optional=False):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);ob=bpy.context.object;ob.name=n;ob.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(mats[m]);bev=ob.modifiers.new('Soft manufactured edges','BEVEL');bev.width=.035;bev.segments=2;ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 if optional:opt.append(ob)
 return ob
reference_start=set(bpy.data.objects)
# Four normal rods remain visibly shorter than the new heavy fishing poles.
for i,(x,y) in enumerate([(-1.9,-.35),(1.9,-.35),(1.9,1.1),(1.9,2.55)]):
 s=1 if x>0 else -1;optional=i>1
 cyl('Normal rod '+str(i+1),(x,y,.46),(x+s*.9,y-.12,1.35),.026,'M_DeckWood',optional)
 cyl('Normal rod tip '+str(i+1),(x+s*.9,y-.12,1.35),(x+s*1.28,y-.20,1.57),.014,'M_Rubber',optional)
 cyl('Normal reel '+str(i+1),(x-.07,y,.69),(x+.07,y,.69),.09,'M_Steel',optional)
normal_proxies=set(bpy.data.objects)-reference_start
# Deep rods: compact edge clamps, strong upright butt, arched outward taper,
# visible manual reel/handle and hanging fishing line. No robotic/control cabinet.
for j,y in enumerate([.40,1.82],1):
 box(f'Deep {j} rail clamp',(1.86,y,.44),(.22,.30,.30),'M_HullNavy',True)
 pts=[(1.87,y,.46),(1.98,y,1.48),(2.25,y,2.49),(2.75,y,3.05),(3.34,y,3.14)]
 for k in range(4):cyl(f'Deep {j} tapered pole {k}',pts[k],pts[k+1],[.063,.05,.035,.020][k],'M_RailIvory' if k<2 else 'M_HullNavy',True)
 cyl(f'Deep {j} orange grip',(1.91,y,.78),(1.96,y,1.20),.076,'M_SafetyOrange',True)
 cyl(f'Deep {j} hand reel',(1.94,y-.15,.74),(1.94,y+.15,.74),.18,'M_HullNavy',True)
 for yy in [y-.16,y+.16]:cyl(f'Deep {j} reel flange',(1.94,yy-.015,.74),(1.94,yy+.015,.74),.205,'M_Steel',True)
 cyl(f'Deep {j} crank',(1.94,y-.20,.74),(1.69,y-.20,.86),.028,'M_SafetyOrange',True)
 cyl(f'Deep {j} handle',(1.69,y-.20,.86),(1.69,y-.33,.86),.043,'M_Rubber',True)
 for p in pts[1:]:cyl(f'Deep {j} line guide',p,(p[0],p[1],p[2]+.07),.035,'M_Steel',True)
 cyl(f'Deep {j} hanging fishing line',(3.34,y,3.14),(3.34,y,-.28),.009,'M_Rope',True)
deep_meshes=set(bpy.data.objects)-reference_start-normal_proxies
trap_start=set(bpy.data.objects)
# Preview trap/buoy positions follow fixed approved anchors; no baked crew.
for x in [-2.8,2.8]:
 y=-2.05
 cyl('Fixed trap buoy',(x,y,-.33),(x,y,-.05),.16,'M_SafetyOrange')
 cyl('Buoy neck',(x,y,-.07),(x,y,.14),.045,'M_RailIvory')
 cyl('Fixed buoy rope',(1.9 if x>0 else -1.9,y,.37),(x,y,-.16),.014,'M_Rope')
 box('Crab cage frame',(x,y,-.77),(.64,.5,.40),'M_HullNavy')
 for z in [-.98,-.56]:
  for dy in [-.25,.25]:cyl('Cage bar',(x-.32,y+dy,z),(x+.32,y+dy,z),.022,'M_Steel')
 for xx in [-.32,-.16,0,.16,.32]:
  for dy in [-.25,.25]:cyl('Cage upright',(x+xx,y+dy,-.98),(x+xx,y+dy,-.56),.014,'M_Steel')
trap_proxies=set(bpy.data.objects)-trap_start
# Rotate second net group about its existing geometry centre to the optional side.
net=bpy.data.objects['NetModule2'];net.location=(-2.22,1.0,0);net.rotation_euler.z=-math.pi/2
for ob in net.children:ob.hide_render=True

# Group without changing world geometry. Reference meshes live outside export set.
def empty(n,p=(0,0,0)):
 ob=bpy.data.objects.new(n,None);scene.collection.objects.link(ob);ob.location=p;bpy.context.view_layer.update();return ob
def adopt(ob,parent):
 bpy.context.view_layer.update();world=ob.matrix_world.copy();ob.parent=parent;ob.matrix_world=world;bpy.context.view_layer.update()
refcol=bpy.data.collections.new('RENDER ONLY runtime equipment references - EXCLUDED FBX');scene.collection.children.link(refcol)
for ob in normal_proxies|trap_proxies:
 for col in list(ob.users_collection):col.objects.unlink(ob)
 refcol.objects.link(ob)
for ob in list(bpy.data.objects):
 if 'Engineer service' in ob.name or 'Service status' in ob.name:bpy.data.objects.remove(ob,do_unlink=True)
module=empty('DeepLineModule');optional_group=empty('OptionalRodModule');fixed_net=empty('NetModule1')
for i in [3,4]:
 for n in ['RodHolder_','RodSocket_']:adopt(bpy.data.objects[n+str(i)],optional_group)
for n in ['NetCrank','NetDrum','NetMountFittings','SternNet_Stowed','SternNetRoller']:adopt(bpy.data.objects[n],fixed_net)
for j,y in enumerate([.40,1.82],1):
 rig=empty('DeepLineRig_'+str(j),(1.87,y,.46));adopt(rig,module)
 reel=empty('DeepLineReelPivot_'+str(j),(1.94,y,.74));adopt(reel,rig)
 for ob in deep_meshes:
  if ob.name.startswith(f'Deep {j} '):adopt(ob,reel if any(k in ob.name for k in ['hand reel','reel flange','crank','handle']) else rig)
 for n,p in [('DeepLineWorker_', (1.25,y,0)),('DeepLineTip_', (3.34,y,3.14)),('DeepLineBase_', (1.87,y,.46))]:adopt(empty(n+str(j),p),module)
# Current source workers refer to the former two-aft-net arrangement.
bpy.data.objects['NetWorker_1'].location=(.95,3.10,0)
bpy.data.objects['NetWorker_2'].location=(1.25,1.80,0)
bpy.context.view_layer.update()
# Flatten transformed optional-net group into child geometry before export.
# Named group root stays at hull origin; no hidden importer double transform.
for ob in list(net.children):
 world=ob.matrix_world.copy();ob.parent=None;ob.matrix_world=world
 ob.select_set(True)
 bpy.context.view_layer.objects.active=ob
 bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
 ob.select_set(False)
net.location=(0,0,0);net.rotation_euler=(0,0,0)
for ob in [o for o in bpy.data.objects if o.name.startswith('Module2_')]:adopt(ob,net)
# Permanent service anchors retained for compatibility, not Engineer geometry.
export_objects=[o for o in bpy.data.objects if o.type in {'MESH','EMPTY'} and o not in normal_proxies|trap_proxies]
for ob in export_objects:
 ob.hide_set(False);ob.hide_viewport=False;ob.hide_render=False
# Apply authored mesh rotation/scale with hierarchy intact; world positions preserved.
for ob in export_objects:
 if ob.type=='MESH':
  bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
  bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
def export(path,objects):
 bpy.ops.object.select_all(action='DESELECT')
 for ob in objects:ob['Tier5SourceName']=ob.name;ob.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'EMPTY','MESH'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False,use_custom_props=True)
full=R/'Assets/Art/Models/Boats/Tier5DeepLines103.fbx';standalone=R/'Assets/Art/Models/Boats/Tier5DeepLineRig103.fbx'
export(full,export_objects)
def descendants(ob):return [ob]+[n for c in ob.children for n in descendants(c)]
export(standalone,descendants(module))
def bounds(ob):
 pts=[ob.matrix_world@v.co for v in ob.data.vertices];return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
def tris(ob):
 ob.data.calc_loop_triangles();return len(ob.data.loop_triangles)
for j,y in enumerate([.40,1.82],1):
 assert (bpy.data.objects['DeepLineTip_'+str(j)].matrix_world.translation-Vector((3.34,y,3.14))).length<.001
 assert (bpy.data.objects['DeepLineReelPivot_'+str(j)].matrix_world.translation-Vector((1.94,y,.74))).length<.001
assert bounds(bpy.data.objects['Module2_NetDrum'])[0][0]>1.8
receipt={'blender':bpy.app.version_string,'hull_source_bounds':bounds(bpy.data.objects['Hull']),'source_mesh_bounds':{o.name:bounds(o) for o in export_objects if o.type=='MESH'},'source_objects':len(export_objects),'source_triangles':sum(tris(o) for o in export_objects if o.type=='MESH'),'materials':sorted({slot.material.name for o in export_objects if o.type=='MESH' for slot in o.material_slots if slot.material}),'source_anchors':{o.name:list(o.matrix_world.translation) for o in export_objects if o.type=='EMPTY'},'original_sha256':original_hashes,'exports':{}}
# Store production-only scene before creating stage; proxy collection included but hidden.
for ob in normal_proxies|trap_proxies:ob.hide_render=True
for ob in net.children:ob.hide_render=True
for ob in bpy.data.objects['RawBuckets'].children:ob.hide_render=True
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Tier5DeepLines103.blend'))
# Roundtrip in a separate temporary scene then return to the production scene.
production_scene=scene
for path in [full,standalone]:
 check=bpy.data.scenes.new('FBX roundtrip verification');bpy.context.window.scene=check
 bpy.ops.import_scene.fbx(filepath=str(path));imported=list(check.objects)
 names={o.name.split('.00')[0] for o in imported}
 # Imports are suffixed because source remains loaded; use original_name property mapping via suffix trim.
 def find(n):return next((o for o in imported if o.get('Tier5SourceName')==n),None)
 if path==full:
  hull=find('Hull');assert hull
  bb=bounds(hull);dims=sorted(bb[1][i]-bb[0][i] for i in range(3));assert abs(dims[-1]-8.5)<.002 and abs(dims[-2]-4.2)<.002,dims
  required=['Hull','DeepLineModule','OptionalRodModule','NetModule1','NetModule2','RawBuckets','RawIceCoolers','PreparedHold','PrepStation']+[n for n in receipt['source_anchors']]
 else:required=['DeepLineModule','DeepLineRig_1','DeepLineRig_2','DeepLineWorker_1','DeepLineWorker_2','DeepLineTip_1','DeepLineTip_2','DeepLineReelPivot_1','DeepLineReelPivot_2']
 for n in required:assert find(n) is not None,(path,n)
 assert len([o for o in imported if o.name.startswith('DeepLineRig_')])==2
 for j in [1,2]:
  source_distance=(Vector(receipt['source_anchors']['DeepLineTip_'+str(j)])-Vector(receipt['source_anchors']['DeepLineWorker_'+str(j)])).length
  actual_distance=(find('DeepLineTip_'+str(j)).matrix_world.translation-find('DeepLineWorker_'+str(j)).matrix_world.translation).length
  assert abs(source_distance-actual_distance)<.002,(source_distance,actual_distance)
 assert not any(any(k in o.name for k in ['Normal rod','Normal reel','Crab cage','Fixed trap','Cage bar','Cage upright','Review','REVIEW','Body','Engineer service','Service status']) for o in imported)
 for ob in imported:
  assert min(ob.scale)>0,(ob.name,list(ob.scale))
  if ob.type=='MESH':assert len(ob.data.vertices)>0 and all(math.isfinite(v) for vertex in ob.data.vertices for v in vertex.co)
 for source_name,source_bounds in receipt['source_mesh_bounds'].items():
  original=bpy.data.objects[source_name]
  if path==standalone and original not in descendants(module):continue
  actual=find(source_name);assert actual is not None,source_name
  actual_bounds=bounds(actual)
  source_dims=sorted(source_bounds[1][i]-source_bounds[0][i] for i in range(3))
  actual_dims=sorted(actual_bounds[1][i]-actual_bounds[0][i] for i in range(3))
  assert max(abs(a-b) for a,b in zip(source_dims,actual_dims))<.003,(source_name,source_dims,actual_dims)
  assert abs(Vector(tuple((source_bounds[0][i]+source_bounds[1][i])/2 for i in range(3))).length-Vector(tuple((actual_bounds[0][i]+actual_bounds[1][i])/2 for i in range(3))).length)<.003,source_name
 receipt['exports'][path.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'objects':len(imported),'triangles':sum(tris(o) for o in imported if o.type=='MESH'),'hull_sorted_dimensions':dims if path==full else None,'required_names_passed':required,'rig_count':2,'every_mesh_world_dimensions_and_origin_distance_preserved':True,'positive_scales_finite_geometry':True,'no_stage_or_runtime_proxies':True,'roundtrip_anchors':{n:list(find(n).matrix_world.translation) for n in required if find(n).type=='EMPTY'}}
 for ob in imported:bpy.data.objects.remove(ob,do_unlink=True)
 bpy.context.window.scene=production_scene;bpy.data.scenes.remove(check)
for rel,digest in original_hashes.items():assert hashlib.sha256((R/rel).read_bytes()).hexdigest()==digest,rel
receipt['original_files_unchanged']=True
(O/'export.json').write_text(json.dumps(receipt,indent=2))
for ob in normal_proxies|trap_proxies:ob.hide_render=False
# Render studio, no image-generation stand-in.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.04));floor=bpy.context.object;floor.name='REVIEW ONLY neutral sea stage';floor.data.materials.append(mat('Review sea',(.085,.32,.36)))
world=bpy.data.worlds.new('Review soft coastal sky');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.56,.70,.76,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;scene.world=world
for loc,energy,size in [((2,-5,10),1400,7),((-5,2,6),900,6)]:
 bpy.ops.object.light_add(type='AREA',location=loc);lamp=bpy.context.object;lamp.data.energy=energy;lamp.data.shape='DISK';lamp.data.size=size;lamp.rotation_euler=(Vector((0,0,0))-lamp.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(11,13,13));cam=bpy.context.object;cam.data.type='ORTHO';scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.resolution_x=1800;scene.render.resolution_y=1375;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
def render(name,loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 if 'plan' in name:cam.rotation_euler.z=-math.pi/2
 scene.render.filepath=str(O/name)
 bpy.ops.render.render(write_still=True)
render('01-rod-deepline-beauty.png',(11,13,13),(.35,.1,.6),12.8)
# Approved102 plan remains the placement reference;103 receipt records exact mesh bounds.
# Save review scene in primary variant. Variant comparison is render-only state.
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Tier5DeepLines103-review.blend'))
for ob in opt:ob.hide_render=True
for i in [3,4]:bpy.data.objects['RodHolder_'+str(i)].hide_render=True
for ob in net.children:ob.hide_render=False
render('03-side-net-beauty.png',(11,13,13),(.35,.1,.6),12.8)
# Two final beauty views intentionally keep this production delivery lean.
print('TIER103 EXPORT ROUNDTRIP AND RENDER COMPLETE')
