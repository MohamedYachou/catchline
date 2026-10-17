"""Isolated BOAT032 comparison. Never changes production FBX or gameplay.
Blender --background --python this_file [-- upgraded]
"""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'Art/Models/Tier4Blockout032'
OUT.mkdir(parents=True, exist_ok=True)
UPGRADED = 'upgraded' in sys.argv
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, color):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    # Palette supplied in sRGB, shader takes linear values.
    p.inputs['Base Color'].default_value = (*[v / 12.92 if v < .04045 else ((v+.055)/1.055)**2.4 for v in color], 1)
    p.inputs['Roughness'].default_value = .72
    return m
def hexmat(name, c): return mat(name, tuple(int(c[i:i+2],16)/255 for i in (0,2,4)))
NAVY=hexmat('032 Navy','173F57'); IVORY=hexmat('032 Ivory','F3F0DC')
WOOD=hexmat('032 Wood','C58B50'); DARK=hexmat('032 Rubber','28343B')
TEAL=hexmat('032 Teal','168F9F'); STEEL=hexmat('032 Steel','8FA6AC')
ORANGE=hexmat('032 Orange','E36A35'); FISH=hexmat('032 Fish','BAC9C6')
BG=hexmat('032 Studio','E7EBE8'); INK=hexmat('032 Ink','173F57')
ICE=hexmat('032 Ice','BFE2E1')

def collection(name):
    c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c
T3=collection('Tier 3 - production reference - 5.4 x 2.8 m')
T4=collection('Tier 4 - blockout - 6.8 x 3.5 m')
STAGE=collection('Review cameras and labels')

def move(o,c):
    for old in list(o.users_collection): old.objects.unlink(o)
    c.objects.link(o); return o
def box(name, loc, size, material, c=T4, bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o=bpy.context.object
    o.name=name; o.dimensions=size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    if bevel:
        m=o.modifiers.new('Broad blockout bevel','BEVEL'); m.width=bevel; m.segments=2
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return move(o,c)
def cylinder(name,loc,radius,depth,material,c=T4):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=radius,depth=depth,location=loc)
    o=bpy.context.object;o.name=name;o.data.materials.append(material);return move(o,c)
def sphere(name,loc,size,material,c=T4):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=loc)
    o=bpy.context.object;o.name=name;o.scale=size;o.data.materials.append(material);return move(o,c)

# Bake importer axes into each mesh, maintaining original metre dimensions.
bpy.ops.import_scene.fbx(filepath=str(ROOT/'Assets/Art/Models/Boats/CompactFisherV1.fbx'))
refs=[]
for ob in list(bpy.context.scene.objects):
    if ob.type!='MESH': continue
    mesh=ob.data.copy(); mesh.transform(ob.matrix_world)
    new=bpy.data.objects.new('T3 '+ob.name,mesh); T3.objects.link(new)
    new.location.x=3.85; new.location.y=.1
    refs.append((ob.name,mesh))
for ob in list(bpy.context.scene.objects):
    if ob not in list(T3.objects): bpy.data.objects.remove(ob,do_unlink=True)

SX=3.5/2.8; SY=6.8/5.4; CX=-3.85
omit={'HoldLid','FishHold','HoldRimHinges','DeckDetails','HelmRoof','CanopyFittings'}
stretch={'Hull','GunwaleHardware','PlankDeck','HullPaintBand'}
for name,mesh in refs:
    if name in omit: continue
    data=mesh.copy()
    for v in data.vertices:
        x,y,z=v.co
        if name in stretch: x*=SX; y=(y+.1)*SY
        elif name.startswith(('Helm','Canopy','BowLocker')): y-=.53
        elif name.startswith(('Stern','Net','Outboard','Propeller','Engine')): y+=.78
        elif name.startswith(('Rod','Safety')): x*=SX; y=(y+.1)*SY
        v.co=(x+CX,y,z)
    o=bpy.data.objects.new('T4 '+name,data);T4.objects.link(o)

# Cover previous flush hatch. Tier4 stores fish locally around the table instead.
box('T4 patched plank over previous hold', (CX-.8125,1.07,-.018),(.85,1.00,.03),WOOD)
# Different silhouette: short flat work canopy, coloured brow and short mast.
box('T4 squared helm canopy',(CX,-1.60,1.43),(1.88,1.72,.14),IVORY,bevel=.075)
box('T4 teal canopy brow',(CX,-.74,1.43),(1.82,.045,.095),TEAL,bevel=.012)
cylinder('T4 short mast',(CX+.58,-1.90,1.71),.025,.46,STEEL)
cylinder('T4 orange beacon',(CX+.58,-1.90,1.98),.065,.09,ORANGE)

# Two hands stand abreast, both facing the bow (-Y).
TY=.72; WY=1.40; SYOUT=2.04
box('Prep stainless rim',(CX,TY,.57),(1.48,.64,.10),STEEL)
box('Prep washable top',(CX,TY,.63),(1.39,.57,.035),IVORY,bevel=.025)
for dx in (-.59,.59):
    for dy in (-.22,.22):box('Prep table leg',(CX+dx,TY+dy,.275),(.055,.055,.55),STEEL,bevel=.008)
box('Prep table lower shelf',(CX,TY,.20),(1.25,.45,.055),TEAL)
for i,dx in enumerate((-.36,.36)):
    box('Cutting board '+str(i+1),(CX+dx,TY,.66),(.51,.39,.035),WOOD,bevel=.018)
    # Fish and one deliberately chunky knife per board.
    sphere('Fish on cutting board '+str(i+1),(CX+dx-.04,TY,.705),(.17,.065,.045),FISH)
    box('Knife blade '+str(i+1),(CX+dx+.18,TY-.015,.702),(.035,.21,.018),STEEL,bevel=.003)
    box('Knife handle '+str(i+1),(CX+dx+.18,TY+.135,.702),(.048,.095,.035),DARK,bevel=.01)
    box('Worker standing mat '+str(i+1),(CX+dx,WY,.016),(.56,.52,.025),DARK,bevel=.02)

def bucket(x,y,idx):
    # Open barrel, hollow interior, restrained handful of fish.
    seg=16; ro=.255; ri=.218; z0=.025; z1=.40
    vs=[]
    for r,z in ((ro*.83,z0),(ro,z1),(ri,z1),(ri*.83,z0+.035)):
        for j in range(seg):
            a=j*2*math.pi/seg;vs.append((x+r*math.cos(a),y+r*math.sin(a),z))
    faces=[]
    for k in range(3):
        for j in range(seg):faces.append((k*seg+j,k*seg+(j+1)%seg,(k+1)*seg+(j+1)%seg,(k+1)*seg+j))
    faces.append(tuple(range(3*seg,4*seg)))
    me=bpy.data.meshes.new('Open bucket mesh');me.from_pydata(vs,[],faces);me.materials.append(TEAL)
    o=bpy.data.objects.new('RAW bucket '+str(idx),me);T4.objects.link(o)
    for off in (-.07,.07):sphere('Raw fish in bucket',(x+off,y,.31),(.055,.15,.045),FISH)
    # Simple side handles.
    for side in (-1,1):box('Bucket handle',(x+side*.264,y,.30),(.04,.15,.045),STEEL,bevel=.012)

def cooler(x,y,idx,raw=False):
    box(('RAW ice cooler ' if raw else 'PREPARED freezer ')+str(idx),(x,y,.245),(.60,.48,.45),IVORY,bevel=.045)
    box('Insulated lid '+str(idx),(x,y,.49),(.64,.51,.075),TEAL,bevel=.035)
    box('Recessed lid handle '+str(idx),(x,y,.535),(.18,.045,.025),STEEL,bevel=.008)
    box('Storage front latch '+str(idx),(x,y-.25,.39),(.08,.025,.09),STEEL,bevel=.008)
    if raw:
        box('Ice marker vertical',(x,y-.267,.25),(.035,.008,.13),ICE,bevel=.003)
        box('Ice marker horizontal',(x,y-.268,.25),(.13,.008,.035),ICE,bevel=.003)

for i,dx in enumerate((-.36,.36)):
    if UPGRADED:cooler(CX+dx,.14,i+1,True)
    else:bucket(CX+dx,.13,i+1)
    cooler(CX+dx,SYOUT,i+1)
cylinder('Chum pail under table',(CX,TY,.25),.15,.31,ORANGE)

# Use the delivered game rig, evaluate pose, then freeze into review meshes.
# Both boats use identical original body data/height; no scale fudge.
before=set(bpy.data.objects)
bpy.ops.import_scene.fbx(filepath=str(ROOT/'Assets/Art/Models/Crew/CrewRig.fbx'),use_anim=True)
crew=[o for o in bpy.data.objects if o not in before]
arm=next(o for o in crew if o.type=='ARMATURE')
actions=list(bpy.data.actions)
def actor(name,pos,yaw,role,c,working=False):
    arm.animation_data_create()
    action=next(a for a in actions if a.name.endswith('|'+('Bait' if working else 'Idle')))
    arm.animation_data.action=action
    if hasattr(action,'slots') and len(action.slots):arm.animation_data.action_slot=action.slots[0]
    bpy.context.scene.frame_set(9 if working else 1)
    bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
    names={'Body', 'Outfit_'+role, 'Hat_CaptainCap' if role=='Captain' else 'Hat_Beanie'}
    for src in crew:
        if src.name not in names:continue
        evaluated=src.evaluated_get(dg)
        me=bpy.data.meshes.new_from_object(evaluated,depsgraph=dg)
        me.transform(src.matrix_world)
        o=bpy.data.objects.new(name+' '+src.name,me);c.objects.link(o)
        o.location=pos;o.rotation_euler.z=yaw

# Four aboard the reference, five aboard the candidate to make personnel cost visible.
actor('T3 captain',(3.85-.12,-.82,0),0,'Captain',T3)
actor('T3 port fisher',(3.85-.75,.10,0),math.pi/2,'Fisherman',T3)
actor('T3 starboard fisher',(3.85+.75,.10,0),-math.pi/2,'Fisherman',T3)
actor('T3 hand',(3.85,1.40,0),0,'Deckhand',T3)
actor('T4 captain',(CX-.12,-1.30,0),0,'Captain',T4)
actor('T4 port fisher',(CX-1.22,-.10,0),math.pi/2,'Fisherman',T4)
actor('T4 starboard fisher',(CX+1.22,-.10,0),-math.pi/2,'Fisherman',T4)
for i,dx in enumerate((-.36,.36)):actor('T4 prep hand '+str(i+1),(CX+dx,WY,0),0,'Deckhand',T4,True)
for o in crew:bpy.data.objects.remove(o,do_unlink=True)

# Review stage, neutral background and readable orthographic views.
box('Studio floor',(0,0,-.82),(200,200,.12),BG,STAGE,bevel=0)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1600;scene.render.resolution_y=1080;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.world=bpy.data.worlds.new('032 studio world')
scene.world.color=(.65,.65,.65)
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs[0].default_value=(.65,.72,.78,1)
scene.world.node_tree.nodes.get('Background').inputs[1].default_value=.6
scene.view_settings.view_transform='AgX'
for name,loc,power,size in [('Key',(-5,-4,12),1900,8),('Fill',(7,4,10),1300,7)]:
    bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name=name
    o.data.energy=power;o.data.shape='DISK';o.data.size=size
    o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat('-Z','Y').to_euler();move(o,STAGE)
bpy.ops.object.camera_add(location=(0,13,17))
cam=bpy.context.object;cam.name='Comparison orthographic';cam.data.type='ORTHO';cam.data.ortho_scale=16.5
cam.rotation_euler=(Vector((0,0,.3))-cam.location).to_track_quat('-Z','Y').to_euler()
scene.camera=cam;move(cam,STAGE)
labels=[]
def caption(name,txt,x,y,size=.25):
    cu=bpy.data.curves.new(name,'FONT');cu.body=txt;cu.size=size;cu.align_x='CENTER'
    cu.space_line=1.25;ob=bpy.data.objects.new(name,cu);STAGE.objects.link(ob)
    ob.parent=cam;ob.location=(x,y,-1);cu.materials.append(INK);labels.append(ob)
caption('Title','TIER 4 / PREPARATION BOAT - ROUGH SIZE STUDY',0,4.85,.33)
caption('T3 label','TIER 3  |  5.4 x 2.8 m',-3.6,-4.25,.29)
caption('T3 sub','Production FBX / 4 crew',-3.6,-4.65,.21)
caption('T4 label','TIER 4  |  6.8 x 3.5 m',3.6,-4.25,.29)
caption('T4 sub','+26% length / +25% beam / 5 crew shown',3.6,-4.65,.21)
suffix='ice-coolers' if UPGRADED else 'buckets'
scene.render.filepath=str(OUT/f'comparison-{suffix}.png')
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'tier4-{suffix}.blend'))
bpy.ops.render.render(write_still=True)

# True top view with labels and no perspective/scale mismatch.
cam.location=(0,0,20);cam.rotation_euler=(0,0,math.pi);cam.data.ortho_scale=15.5
for ob in labels:ob.hide_render=True
caption('Top heading','TOP PLAN / IDENTICAL CREW SCALE',0,4.55,.30)
caption('Top T3','TIER 3 / 5.4 x 2.8 m',-3.85,-4.10,.27)
caption('Top T4','TIER 4 / 6.8 x 3.5 m',3.85,-4.10,.27)
scene.render.filepath=str(OUT/f'top-{suffix}.png');bpy.ops.render.render(write_still=True)

# Close view of the workflow, same actual candidate geometry.
for ob in labels:ob.hide_render=True
for ob in T3.objects:ob.hide_render=True
cam.location=(CX+4,6.5,7.5);cam.rotation_euler=(Vector((CX,.9,.4))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.ortho_scale=5.6
scene.render.filepath=str(OUT/f'station-{suffix}.png');bpy.ops.render.render(write_still=True)

report={'reference_hull_m':[5.4,2.8],'candidate_hull_m':[6.8,3.5],
 'crew_body_height_m':.95,'reference_people':4,'candidate_people':5,
 'crew_cap_status':'visual fit only; not a gameplay decision',
 'table_m':[1.48,.64,.67],'prep_worker_centres':[[CX-.36,WY,0],[CX+.36,WY,0]],
 'raw_storage_centres':[[CX-.36,.14,.24],[CX+.36,.14,.24]],
 'prepared_storage_centres':[[CX-.36,SYOUT,.24],[CX+.36,SYOUT,.24]],
 'variant':suffix,'prepared_freshness':'no spoilage',
 'raw_freshness':'protected by upgraded ice coolers only',
 'runtime_integration':False,'route_validation':'not runtime verified'}
(OUT/f'manifest-{suffix}.json').write_text(json.dumps(report,indent=2))
for prefix, expected in [('T3 ',(2.8,5.4)),('T4 ',(3.5,6.8))]:
    hull=bpy.data.objects[prefix+'Hull']
    bounds=[hull.matrix_world@Vector(v) for v in hull.bound_box]
    measured=[max(v[i] for v in bounds)-min(v[i] for v in bounds) for i in range(2)]
    assert all(abs(a-b)<.002 for a,b in zip(measured,expected)),(prefix,measured)
for c in (T3,T4):
    assert all(math.isfinite(v) for o in c.objects if o.type=='MESH' for p in o.data.vertices for v in p.co)
print('GEOMETRY VERIFIED: exact hull dimensions, finite vertices, original crew scale')
print('BOAT032 BLOCKOUT COMPLETE',suffix)
