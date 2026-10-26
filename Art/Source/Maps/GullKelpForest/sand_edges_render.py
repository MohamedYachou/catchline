import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent;O=R/'Art/Models/Maps/GullKelpForest';B=R.parent/'Catchline-sim/Backups/codex2-sand-edges-before'
state=sys.argv[sys.argv.index('--')+1];src=B if state=='old' else O
bpy.ops.wm.open_mainfile(filepath=str(src/'GullKelpForestSeaV2.blend'))
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.cycles.max_bounces=4
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for d in prefs.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in prefs.devices):sc.cycles.device='GPU'
except Exception:pass
sc.view_settings.view_transform='AgX';sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.film_transparent=False
sc.world=bpy.data.worlds.new('SandEdgeReviewWorld');sc.world.use_nodes=True;bg=sc.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.55,.73,.80,1);bg.inputs[1].default_value=.65
ld=bpy.data.lights.new('SandEdgeReviewSun','SUN');lo=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(lo);lo.rotation_euler=(.35,-.45,-.5);ld.energy=2;ld.angle=.15;ld.color=(1,.92,.80)
cd=bpy.data.cameras.new('SandEdgeReviewCamera');co=bpy.data.objects.new(cd.name,cd);sc.collection.objects.link(co);sc.camera=co;cd.type='ORTHO';cd.clip_end=1000
patches=json.loads((S/'sand-edges-plan.json').read_text())['patches']
for i,p in enumerate(patches,1):
 x,y=p['centre_before'];target=Vector((x,y,-1.5))
 for view in ['top','deck-45']:
  direction=Vector((0,0,-1)) if view=='top' else Vector((.574,-.819,-1)).normalized()
  co.location=target-direction*90;co.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
  for w,h in [(1440,900),(844,390)]:
   sc.render.resolution_x=w;sc.render.resolution_y=h;cd.ortho_scale=34 if w==1440 else 48
   sc.render.filepath=str(O/f'SeaV2-sand-edges-ground{i}-{view}-{w}x{h}-{state}.png');bpy.ops.render.render(write_still=True)
   print('RENDERED',Path(sc.render.filepath).name,flush=True)
print('SAND EDGE RENDER COMPLETE',state,flush=True)
