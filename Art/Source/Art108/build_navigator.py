"""Navigator V1, additive shared-rig character and three in-place clips."""
import bpy, math, sys, json, hashlib, shutil
from pathlib import Path
from mathutils import Vector, Quaternion
sys.path.insert(0,str(Path(__file__).parent));import build_stations as K
ROOT=K.ROOT;OUT=ROOT/'Art/Models/NavigatorV1';OUT.mkdir(exist_ok=True)
GAME=ROOT/'Assets/Art/Models/Crew/NavigatorV1.fbx'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/Models/CrewRig/CrewRig.blend'))
arm=bpy.data.objects['CrewRig'];body=bpy.data.objects['Body'];outfit=bpy.data.objects['Outfit_Captain'];hat=bpy.data.objects['Hat_CaptainCap']
keep={arm,body,outfit,hat}
for o in list(bpy.data.objects):
    if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
arm.animation_data_clear()
for a in list(bpy.data.actions):bpy.data.actions.remove(a)
outfit.name='Outfit_Navigator';hat.name='Hat_NavigatorCap';hat.data=hat.data.copy()
for slot in hat.material_slots:
    if slot.material and slot.material.name=='M_RailIvory':slot.material=K.material('M_HullNavy')
for o in keep:o.hide_render=False;o.hide_viewport=False;o.hide_set(False)
bpy.context.scene.camera=None
def rigid(ob,bone):
    world=ob.matrix_world.copy();ob.parent=arm;ob.matrix_world=world
    vg=ob.vertex_groups.new(name=bone);vg.add(list(range(len(ob.data.vertices))),1,'REPLACE')
    mod=ob.modifiers.new('SharedRig','ARMATURE');mod.object=arm
    return ob
extras=[]
for x in (-.055,.055):
    ob=K.cyl('BinocularBarrel',(x,-.175,.43),.037,.13,'M_HullNavy',12);ob.rotation_euler.x=math.pi/2
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    extras.append(rigid(ob,'Spine1'))
    ob=K.cyl('BinocularLens',(x,-.244,.43),.027,.012,'M_SeaTeal',12);ob.rotation_euler.x=math.pi/2
    bpy.context.view_layer.objects.active=ob;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    extras.append(rigid(ob,'Spine1'))
extras.append(rigid(K.beam('BinocularBridge',(-.055,-.175,.43),(.055,-.175,.43),.013,'M_Steel'),'Spine1'))
for sign in (-1,1):extras.append(rigid(K.beam('BinocularStrap',(sign*.067,-.09,.54),(sign*.055,-.17,.45),.009,'M_Rope'),'Spine1'))
extras.append(rigid(K.box('CompassBadge',(0,-.157,.955),(.045,.013,.045),'M_RailIvory',.011),'Head'))
# Broad short bob locks; retain original body and scalp height, no new skeleton.
for sign in (-1,1):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=(sign*.15,.015,.70))
    ob=bpy.context.object;ob.name='NavigatorBob';ob.scale=(.048,.10,.085)
    ob.data.materials.append(bpy.data.materials['M_HairChestnut']);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    extras.append(rigid(ob,'Head'))
def orient(name,d):
    p=arm.pose.bones[name];desired=Vector(d).to_track_quat('Y','Z')
    parent=p.parent.matrix.to_quaternion() if p.parent else Quaternion()
    rest=(p.parent.bone.matrix_local.inverted()@p.bone.matrix_local).to_quaternion() if p.parent else p.bone.matrix_local.to_quaternion()
    p.rotation_quaternion=rest.inverted()@parent.inverted()@desired;bpy.context.view_layer.update()
def pose(name,t):
    for p in arm.pose.bones:p.rotation_mode='QUATERNION';p.rotation_quaternion=Quaternion();p.location=(0,0,0);p.scale=(1,1,1)
    wave=math.sin(t*math.tau);pulse=math.sin(t*math.pi)**2
    arm.pose.bones['Hips'].location.z=.003*wave
    arm.pose.bones['Head'].rotation_quaternion=Quaternion((0,0,1),.10*wave if name=='Idle' else -.16*pulse)
    bpy.context.view_layer.update()
    for sign,side in [(1,'Left'),(-1,'Right')]:
        upper=(sign*.08,-.015,-.18);lower=(-sign*.025,-.05,-.10)
        if name=='Point' and side=='Right':
            upper=(sign*.06,-.03-.11*pulse,-.16+.19*pulse);lower=(sign*.01,-.08-.09*pulse,-.08+.10*pulse)
        if name=='Warn':
            upper=(sign*(.08+.03*pulse),-.03,-.17+.30*pulse)
            lower=(sign*.025,-.055,-.10+.20*pulse+.025*math.sin(t*math.tau*3)*pulse)
        orient(side+'Arm',upper);orient(side+'ForeArm',lower);orient(side+'Hand',lower)
    bpy.context.view_layer.update()
clips=[('Idle',49,True),('Point',37,False),('Warn',37,False)]
arm.animation_data_create()
for name,end,loop in clips:
    action=bpy.data.actions.new(name);arm.animation_data.action=action;action.use_fake_user=True;action['loop']=loop;action['fps']=24
    for f in range(1,end+1):
        pose(name,(f-1)/(end-1))
        for p in arm.pose.bones:
            for attr in ('rotation_quaternion','location','scale'):p.keyframe_insert(attr,frame=f,group=p.name)
    action.use_frame_range=True;action.frame_start=1;action.frame_end=end
arm.animation_data.action=None;pose('Idle',0)
sc=bpy.context.scene;sc.render.fps=24;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
obs=[arm,body,outfit,hat]+extras
bpy.ops.object.select_all(action='DESELECT')
for o in obs:o.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(OUT/'NavigatorV1.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',
 apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=True,bake_space_transform=False,add_leaf_bones=False,
 bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,use_custom_props=True)
shutil.copyfile(OUT/'NavigatorV1.fbx',GAME)
record={'sourceRig':'Art/Models/CrewRig/CrewRig.blend','bones':[b.name for b in arm.data.bones],'boneCount':len(arm.data.bones),
 'heightBareScalp':.95,'clips':[dict(id=n,frames=[1,e],fps=24,loop=l) for n,e,l in clips],
 'triangles':K.tris(obs),'boundsSource':K.bounds(obs),'sourceRigSha256':hashlib.sha256((ROOT/'Art/Models/CrewRig/CrewRig.blend').read_bytes()).hexdigest(),
 'nativeAcceptance':'Pending code-owner Unity import and clip selection; match suffix after last pipe.'}
assert len(arm.data.bones)==20
# Render source with an independent quiet studio, no user application touched.
sc.render.engine='CYCLES';sc.cycles.samples=20;sc.render.resolution_x=480;sc.render.resolution_y=480;sc.render.resolution_percentage=100
sc.world.use_nodes=True
bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.58,.73,.82,1);bg.inputs[1].default_value=.65
for name,p,power,size in [('Key',(-2,-3,4),500,3),('Fill',(2,1,3),350,3)]:
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.size=size;o=bpy.data.objects.new(name,data);sc.collection.objects.link(o);o.location=p;o.rotation_euler=(Vector((0,0,.5))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Preview');o=bpy.data.objects.new('Preview',cam);sc.collection.objects.link(o);sc.camera=o;cam.type='ORTHO';cam.ortho_scale=1.35
o.location=(1.4,-2.8,1.6);o.rotation_euler=(Vector((0,0,.52))-o.location).to_track_quat('-Z','Y').to_euler()
sc.render.film_transparent=True;sc.view_settings.view_transform='AgX'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'NavigatorV1.blend'))
for name,end,loop in clips:
    arm.animation_data.action=bpy.data.actions[name]
    for phase,frame in [('start',1),('middle',(end+1)//2),('end',end)]:
        sc.frame_set(frame);sc.render.filepath=str(OUT/f'{name}-{phase}.png');bpy.ops.render.render(write_still=True)
# Independent FBX readback of rig, mesh totals and clip coverage.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(GAME))
rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
assert set(record['bones'])==set(b.name for b in rig.data.bones)
assert K.tris(list(bpy.context.scene.objects))==record['triangles']
actions=[a.name.split('|')[-1] for a in bpy.data.actions]
assert all(n in actions for n,_,_ in clips),(actions,clips)
record['roundTrip']={'boneNamesMatch':True,'trianglesMatch':True,'clips':actions}
(OUT/'validation.json').write_text(json.dumps(record,indent=2))
print('ART108 NAVIGATOR ROUNDTRIP PASSED',record['boneCount'],actions)
