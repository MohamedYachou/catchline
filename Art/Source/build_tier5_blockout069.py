"""Isolated six-hired-crew size study; never exports production assets."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/Tier5Blockout069'; OUT.mkdir(parents=True,exist_ok=True)
# Reuse existing authored tier4 geometry, materials and frozen same-scale crew.
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/Models/Tier4Blockout032/tier4-ice-coolers.blend'))
scene=bpy.context.scene
base=next(c for c in bpy.data.collections if c.name.startswith('Tier 4 - blockout'))
for ob in list(bpy.data.objects):
 if ob.name not in base.objects: bpy.data.objects.remove(ob,do_unlink=True)
ref=bpy.data.collections.new('Tier 4 reference');scene.collection.children.link(ref)
cand=bpy.data.collections.new('Tier 5 provisional 8.5 x 4.2');scene.collection.children.link(cand)
# Reference centre -3.9, candidate centre +3.9. Original T4 centre -3.85.
for ob in list(base.objects):
 oldx=ob.location.x
 # Some authored hull meshes have offset baked in vertices, unlike the boxes/crew.
 coords=[ob.matrix_world@v.co for v in ob.data.vertices] if ob.type=='MESH' else []
 centre=sum((v for v in coords),Vector())/len(coords) if coords else ob.location.copy()
 localcentre=Vector((centre.x+3.85,centre.y,centre.z))
 cp=ob.copy();cp.data=ob.data.copy();cand.objects.link(cp);cp.name='T5 '+ob.name
 if ob.name.startswith(('T4 Hull','T4 GunwaleHardware','T4 PlankDeck','T4 HullPaintBand','T4 patched')):
  # Stretch structural shell only; fittings, machines and people retain actual dimensions.
  for v in cp.data.vertices:
   w=ob.matrix_world@v.co;v.co=((w.x+3.85)*1.2+3.9,w.y*1.25,w.z)
  cp.matrix_world.identity()
 else:
  delta=Vector((3.9+localcentre.x*1.2-centre.x,localcentre.y*1.25-centre.y,0))
  cp.location+=delta
 ob.location.x-=.05
 ref.objects.link(ob);base.objects.unlink(ob)
# Helpers for new blockout equipment.
def material(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1)
 m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.7
 return m
navy=material('069 navy',(.018,.050,.085));teal=material('069 teal',(.02,.28,.31));orange=material('069 safety orange',(.72,.18,.045));steel=material('069 steel',(.35,.45,.48));ivory=material('069 ivory',(.85,.84,.73));wood=material('069 wood',(.5,.28,.12));yellow=material('069 engineer yellow',(.8,.48,.04))
def box(name,loc,size,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 mod=o.modifiers.new('Soft edges','BEVEL');mod.width=.025;mod.segments=2
 for c in list(o.users_collection):c.objects.unlink(o)
 cand.objects.link(o);return o
def bar(name,a,b,r,mat):
 d=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(Vector(a)+Vector(b))/2)
 o=bpy.context.object;o.name=name;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat)
 for c in list(o.users_collection):c.objects.unlink(o)
 cand.objects.link(o);return o
# Service hatch and compact engineer console near wheel; clear central walkway.
box('Engineer service hatch',(4.98,-1.8,.035),(.65,.72,.06),steel)
box('Engineer service controls',(5.48,-1.8,.36),(.25,.62,.64),navy)
for dy in (-.18,0,.18):box('Service status lamps',(5.345,-1.8+dy,.50),(.02,.075,.075),orange)
# Copy delivered actor exactly; outfit is remapped yellow to identify engineer in this study.
def clone_actor(prefix,target,yaw,engineer=False):
 src=[o for o in cand.objects if o.name.startswith('T5 T4 port fisher')]
 assert len(src)>=2
 origin=src[0].location.copy()
 for o in src:
  n=o.copy();n.data=o.data.copy();cand.objects.link(n);n.name=prefix+' '+o.name.split()[-1]
  n.location=Vector(target)+(o.location-origin);n.rotation_euler.z=yaw
  if engineer and 'Outfit' in o.name:
   n.data.materials.clear();n.data.materials.append(yellow)
clone_actor('T5 engineer',(4.98,-.95,0),math.pi,True)
clone_actor('T5 sixth hired crew - example fisher',(2.55,1.30,0),math.pi/2)
# Exact Mo equipment:2fixed rods+2buoys+1fixed net; bay2rods OR1net.
for o in list(cand.objects):
 if 'RodVisual' in o.name or 'RodSocket' in o.name:bpy.data.objects.remove(o,do_unlink=True)
# One processor; second former prep figure is now a collecting deckhand.
for o in cand.objects:
 if 'prep hand 2' in o.name:o.location+=Vector((.3,1.0,0))
rodmodule=[];netmodule=[]
for i,(x,y) in enumerate([(2.0,-.35),(5.80,-.35),(5.80,1.1),(5.80,2.55)]):
 sign=-1 if x<3.9 else 1
 parts=[bar(('Fixed' if i<2 else 'Convertible')+' rod '+str(i+1),(x,y,.48),(x+sign*.68,y-.40,1.75),.018,navy),
 box('Rod holder '+str(i+1),(x,y,.45),(.12,.16,.26),steel)]
 if i>=2:rodmodule+=parts
# Buoys and crab-box traps are offshore; each gets its own rail service point.
for i,sign in enumerate([-1,1]):
 x=3.9+sign*2.8;y=-2.05
 box('Fixed buoy service '+str(i+1),(3.9+sign*1.78,y,.36),(.28,.40,.60),teal)
 bar('Buoy mooring rope '+str(i+1),(3.9+sign*2.0,y,.4),(x,y,-.08),.012,wood)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=(x,y,.02));o=bpy.context.object;o.name='Fixed buoy '+str(i+1);o.scale=(.15,.15,.23);o.data.materials.append(orange)
 bar('Buoy trap line',(x,y,-.12),(x,y,-.46),.012,wood)
 for xx in (x-.35,x+.35):
  for yy in (y-.275,y+.275):bar('Crab box corner',(xx,yy,-.66),(xx,yy,-.31),.018,navy)
 for z in (-.66,-.31):
  for yy in (y-.275,y+.275):bar('Crab box frame',(x-.35,yy,z),(x+.35,yy,z),.018,navy)
  for xx in (x-.35,x+.35):bar('Crab box frame',(xx,y-.275,z),(xx,y+.275,z),.018,navy)
# Secondnet is an alternative in the same stern-quarter working bay.
for original in list(cand.objects):
 if any(k in original.name for k in ['NetCrank','NetDrum','NetMountFittings','SternNet_Stowed','SternNetRoller']):
  o=original.copy();o.data=original.data.copy();cand.objects.link(o);o.name='Convertible second net '+original.name
  for v in o.data.vertices:
   w=original.matrix_world@v.co;v.co=(7.8-w.x,w.y,w.z)
  o.matrix_world.identity();o.hide_render=True;netmodule.append(o)
# Studio, camera, lights.
world=scene.world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.73,.8,1);world.node_tree.nodes['Background'].inputs[1].default_value=.7
floor=box('Studio floor',(0,0,-.83),(200,200,.10),ivory)
for name,loc,power in [('Key',(-3,-5,12),1800),('Fill',(7,5,10),1100)]:
 bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=8;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add();cam=bpy.context.object;scene.camera=cam;cam.data.type='ORTHO'
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
labels=[]
def label(txt,x,y,size=.25):
 cu=bpy.data.curves.new('Review caption','FONT');cu.body=txt;cu.size=size;cu.align_x='CENTER';cu.materials.append(navy)
 o=bpy.data.objects.new(txt,cu);scene.collection.objects.link(o);o.parent=cam;o.location=(x,y,-1);labels.append(o)
def view(name,loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 labels[1].location.x=3.9 if name=='comparison' else -3.9
 labels[2].location.x=-3.9 if name=='comparison' else 3.9
 scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
label('TIER 5 / SIX HIRED CREW + CAPTAIN',0,4.4,.34)
label('TIER 4 / 6.8 x 3.5 m / 4 hired + captain',-3.9,-4.25,.23)
label('TIER 5 / 8.5 x 4.2 m / 6 hired + captain',3.9,-4.25,.23)
label('A: 4 rods + 1 net + 2 buoys / engineer + processor + 4 flexible crew',0,-4.70,.18)
view('comparison',(0,12,17),(0,0,.3),16)
view('top',(0,0,25),(0,0,0),16)
for o in labels:o.hide_render=True
for o in ref.objects:o.hide_render=True
view('tier5-detail',(12,10,13),(3.9,0,.35),10.8)
for o in rodmodule:o.hide_render=True
for o in netmodule:o.hide_render=False
view('tier5-net-layout',(12,10,13),(3.9,0,.35),10.8)
view('tier5-net-top',(3.9,0,25),(3.9,0,0),16)
for o in rodmodule:o.hide_render=False
for o in netmodule:o.hide_render=True
# Save scene in comparison state, not the isolated detail view.
for o in ref.objects:o.hide_render=False
for o in labels:o.hide_render=False
cam.location=(0,12,17);cam.rotation_euler=(Vector((0,0,.3))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=16
labels[1].location.x=3.9;labels[2].location.x=-3.9
scene.render.filepath=str(OUT/'comparison.png');bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'tier5-size-study.blend'))
assert all(math.isfinite(v) for o in cand.objects for v in o.location)
assert len([o for o in cand.objects if o.name.endswith('Body')])==7
hull=next(o for o in cand.objects if o.name=='T5 T4 Hull')
bounds=[hull.matrix_world@v.co for v in hull.data.vertices]
actual=[max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in (1,0)]
assert all(abs(a-b)<.02 for a,b in zip(actual,[8.5,4.2])),actual
report={'hull_m':[8.5,4.2],'reference_m':[6.8,3.5],'hired_crew':6,'captain':1,'crew_scale_changed':False,'equipment_counts':'CONFIRMED:2fixed rods,2buoys,1fixednet,1processingtable; bay2rods OR1net','route_check':'not runtime validated','crab_boxes':'2buoy-served offshore trap placeholders; no fixed four-pot rack','production_changes':False}
(OUT/'manifest.json').write_text(json.dumps(report,indent=2))
print('BOAT069 SIZE STUDY COMPLETE',flush=True)
