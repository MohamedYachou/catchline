"""Blender 5.2: source-only ART-010 reference. -- before|after|targets.

Matches Unity camera and placement maths. Also accepts -- refined for POLISH-002's updated target.
Never modifies runtime textures,
materials, rig sources or scenes. Reference effects are illustrative geometry.
"""
import bpy, math, json, sys, importlib.util, random
from pathlib import Path
from mathutils import Vector

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/FirstVoyage10'
spec=importlib.util.spec_from_file_location('gull10',Path(__file__).with_name('build_gull_harbour.py'))
K=importlib.util.module_from_spec(spec);spec.loader.exec_module(K)
B=K.B
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'after'
assets={a['asset']:a for a in json.loads((ROOT/'Art/Models/GullHarbour/build-metrics.json').read_text())['assets']}
scene=None

def unity(v):return Vector((v[0],v[2],v[1]))

def append_asset(name,position,yaw=0,scale=1,baseline=False):
    a=assets[name]
    source=OUT/'Rowboat-before.blend' if baseline else ROOT/a['source']
    names={'Catchline_'+name}|set(a['pivots_blender'])
    with bpy.data.libraries.load(str(source),link=False) as (src,dst):
        dst.objects=[n for n in src.objects if n in names]
    for ob in dst.objects:scene.collection.objects.link(ob)
    root=next(o for o in dst.objects if o.type=='EMPTY')
    # Unity's left-handed world requires a reflection, not just a Z-up rotation.
    root.location=unity(position);root.rotation_euler.z=math.radians(-yaw);root.scale=(scale,-scale,scale)
    return root

def reference_mat(name,hexcode,roughness=.8):
    return B.material('REF_ONLY_'+name,hexcode,roughness)

def mesh_obj(name,verts,faces,mat):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);scene.collection.objects.link(ob);mesh.materials.append(mat)
    return ob

def boat_point(x,y,z):return (1+y,.5+x,z)

def foam(contact=True,wake=False):
    """Broken narrow waterline ribbons; no full bright outline."""
    mat=reference_mat('Foam','#CBE4DB')
    outline=[(-.95,2.1),(.95,2.1),(1.15,1.8),(1.2,1.3),(1.2,0),
             (1.2,-1.5),(1,-1.65),(.45,-1.95),(0,-2.1),(-.45,-1.95),
             (-1,-1.65),(-1.2,-1.5),(-1.2,0),(-1.2,1.3),(-1.15,1.8)]
    if contact:
        for i,(p,q) in enumerate(zip(outline,outline[1:]+outline[:1])):
            if i in (0,3,7,10,13):continue
            for j,(start,end) in enumerate(((.10,.38),(.52,.84))):
                a=Vector(p).lerp(Vector(q),start);b=Vector(p).lerp(Vector(q),end)
                # Hull section at Z=-.32 interpolates existing lower shell loops.
                verts=[boat_point(v.x*.684+v.normalized().x*d,
                                  v.y*.910+v.normalized().y*d,-.312)
                       for d in (.025,.065) for v in (a,b)]
                mesh_obj(f'REF_Contact_{i}_{j}',verts,[(0,1,3,2)],mat)
    if wake:
        for side in (-1,1):
            path=[(side*.67,1.94),(side*.84,2.35),(side*1.06,2.83),(side*1.20,3.35)]
            verts=[boat_point(x+d*side,y,-.310) for d in (0,.045) for x,y in path]
            mesh_obj('REF_RowingWake',verts,[(i,i+1,i+5,i+4) for i in range(3)],mat)

def water(broad):
    mat=reference_mat('Water','#168F9F',.88)
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    shader.inputs['Specular IOR Level'].default_value=.12
    if broad:
        nodes=mat.node_tree.nodes;links=mat.node_tree.links
        tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1.7
        tex.inputs['Detail'].default_value=0;tex.inputs['Roughness'].default_value=.25
        coord=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='ADD'
        links.new(coord.outputs['Object'],mapping.inputs[0])
        # Deliberately slow lateral drift; two numeric phases are documented.
        mapping.inputs[1].default_value=(0,0,0);mapping.inputs[1].keyframe_insert('default_value',frame=1)
        mapping.inputs[1].default_value=(.36,.18,0);mapping.inputs[1].keyframe_insert('default_value',frame=145)
        links.new(mapping.outputs['Vector'],tex.inputs['Vector'])
        ramp=nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].position=.22;ramp.color_ramp.elements[0].color=B.linear_colour('#168F9F')
        ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=B.linear_colour('#279DA8')
        links.new(tex.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],shader.inputs['Base Color'])
    mesh_obj('REF_Water_NotRuntime',[(-100,-100,-.32),(100,-100,-.32),(100,100,-.32),(-100,100,-.32)],[(0,1,2,3)],mat)

def crew():
    source=ROOT/'Art/Models/CrewRig/CrewRig.blend'
    wanted={'CrewRig','Body','Outfit_Captain','Hat_CaptainCap'}
    with bpy.data.libraries.load(str(source),link=False) as (src,dst):
        dst.objects=[n for n in src.objects if n in wanted]
        dst.actions=[n for n in src.actions if n=='Wait']
    for ob in dst.objects:scene.collection.objects.link(ob);ob.hide_render=False;ob.hide_viewport=False
    arm=next(o for o in dst.objects if o.type=='ARMATURE')
    arm.animation_data_clear()
    if dst.actions:
        action=dst.actions[0];arm.animation_data_create();arm.animation_data.action=action
        if hasattr(action,'slots') and len(action.slots):arm.animation_data.action_slot=action.slots[0]
    arm.location=unity((1,0,-.05))
    arm.scale=(1,-1,1)
    scene.frame_set(12)
    arm.animation_data_clear()  # Freeze this existing Wait pose for water-only phase comparisons.
    return arm

def make_scene(baseline=False,broad=True,contact=True,wake=False):
    global scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    append_asset('Rowboat',(1,0,.5),-90,baseline=baseline)
    append_asset('Cooler',(1,0,1),180)
    append_asset('BaitBucket',(.25,0,1.25))
    append_asset('LunchTin',(1.75,0,1.3),20)
    for name,pos,yaw,scale in [('RopeCoil',(-.38,.01,.45),30,.8),('SmallAnchor',(-.42,.02,.95),90,.6),
                              ('TackleBox',(2.32,0,1.32),90,.8),('Lantern',(2.4,0,.55),0,.8)]:
        append_asset(name,pos,yaw,scale)
    rod=append_asset('FishingRod',(0,.44,-.615))
    direction=unity((.05,1.6,-.6)).normalized()
    rod.rotation_mode='QUATERNION';rod.rotation_quaternion=Vector((0,0,1)).rotation_difference(direction)
    rod.scale=(1.25,-1.25,1.25)  # 1.6m source to 2m; preserve Unity handedness.
    crew()
    water(broad);foam(contact,wake)
    world=bpy.data.worlds.new('REF_CoolAmbient');world.use_nodes=True
    bg=world.node_tree.nodes.get('Background');bg.inputs[0].default_value=B.linear_colour('#BCD6DF');bg.inputs[1].default_value=.45
    scene.world=world
    for name,pos,power,size,color in [('WarmKey',(-4,0,7),1100,4.5,'#FFF2DC'),('CoolFill',(5,4,6),260,6,'#C6E0EB')]:
        data=bpy.data.lights.new('REF_'+name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=B.linear_colour(color)[:3]
        ob=bpy.data.objects.new(data.name,data);scene.collection.objects.link(ob);ob.location=pos
        ob.rotation_euler=(Vector((1,.5,0))-ob.location).to_track_quat('-Z','Y').to_euler()
    data=bpy.data.cameras.new('REF_ExactGameplayCamera');data.type='ORTHO'
    cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam);scene.camera=cam
    yaw=math.radians(35);pitch=math.radians(45)
    forward=Vector((math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),-math.sin(pitch)))
    center=(1.35,0,.20) if MODE=='refined' else (1,0,-.7)
    target=unity(center);cam.location=target-forward*40
    cam.rotation_euler=forward.to_track_quat('-Z','Y').to_euler()
    cam.data.clip_start=.1;cam.data.clip_end=120
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    scene.render.resolution_percentage=100
    scene['reference_only']='ART-010 target; no Unity integration; effects are illustrative geometry/nodes'
    scene['unity_camera']=f'Euler(45,35,0), orthoSize3.2, center{center}, distance40, no bob at review snapshot'
    scene.frame_set(1)  # Water begins at its exact zero-offset phase; crew pose is already frozen.

def render(name,x,y,save=False):
    scene.render.resolution_x=x;scene.render.resolution_y=y
    # Blender ortho_scale is horizontal span for landscape; Unity size is half vertical span.
    scene.camera.data.ortho_scale=6.4*x/y
    scene.render.filepath=str(OUT/(name+'.png'))
    if save:bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    bpy.ops.render.render(write_still=True)

if MODE in ('before','after','refined'):
    make_scene(baseline=MODE=='before')
    render(MODE+'-desktop',1440,900,True)
    render(MODE+'-phone',844,390)
elif MODE=='targets':
    for variant,broad,contact,wake in [('flat',False,False,False),('contact',True,True,False),('rowing',True,True,True)]:
        make_scene(broad=broad,contact=contact,wake=wake)
        render('target-'+variant,960,600,True)
    # Reuse exactly the same contact scene at second water phase.
    make_scene(broad=True,contact=True);scene.frame_set(145)
    render('target-drift-6s',960,600)
else:raise ValueError(MODE)
print('ART-010 reference renders complete:',MODE,flush=True)
