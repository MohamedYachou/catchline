import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent));import build_stations as K
OUT=K.OUT;PRE=OUT/'Previews';PRE.mkdir(exist_ok=True)
records=json.loads((OUT/'kit-manifest.json').read_text())['assets']
names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [r['id'] for r in records]
for name in names:
    bpy.ops.wm.open_mainfile(filepath=str(OUT/f'{name}.blend'))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];bb=K.bounds(meshes)
    center=Vector([(a+b)*.5 for a,b in zip(*bb)]);span=max(b-a for a,b in zip(*bb));span=max(span,.3)
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
        for dev in prefs.devices:dev.use=dev.type=='OPTIX'
        if any(dev.use for dev in prefs.devices):sc.cycles.device='GPU'
    except Exception:pass
    sc.world=bpy.data.worlds.new('Soft studio');sc.world.use_nodes=True
    bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.6,.74,.8,1);bg.inputs[1].default_value=.6
    for id,off,power in [('Key',(-2,-3,4),250),('Fill',(3,2,3),160)]:
        d=bpy.data.lights.new(id,'AREA');d.energy=power*span*span;d.size=2*span
        o=bpy.data.objects.new(id,d);sc.collection.objects.link(o);o.location=center+Vector(off)*span
        o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('Kit review');d.type='ORTHO';cam=bpy.data.objects.new('Kit review',d);sc.collection.objects.link(cam);sc.camera=cam
    cam.location=center+Vector((1.1,-1.8,1.3))*span;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();bpy.context.view_layer.update()
    projected=[cam.matrix_world.inverted()@(o.matrix_world@Vector(p)) for o in meshes for p in o.bound_box]
    d.ortho_scale=max(max(p[i] for p in projected)-min(p[i] for p in projected) for i in (0,1))*1.26
    sc.render.resolution_x=512;sc.render.resolution_y=512;sc.render.resolution_percentage=100
    sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA';sc.view_settings.view_transform='AgX'
    sc.render.filepath=str(PRE/f'{name}.png');bpy.ops.render.render(write_still=True)
    print('ART108 KIT PREVIEW',name,flush=True)
