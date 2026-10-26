"""Exact-model references for painterly item illustrations, not final sprites."""
import bpy,sys,json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(R/'Art/Source/HarbourLife'));import render as V
name=sys.argv[sys.argv.index('--')+1]
paths={'hull0':'Art/Models/BoatsV2/Rowboat/Rowboat.fbx','hull1':'Art/Models/BoatsV2/Skiff/Skiff.fbx','hull3':'Art/Models/BoatsV2/PrepFisherV1/PrepFisherV1.fbx','hull4':'Assets/Art/Models/Boats/Tier5DeepLines103.fbx'}
source=R/paths[name];out=R/'Art/Source/BoatsV2/ui/reference';out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.import_scene.fbx(filepath=str(source),use_anim=False)
def ancestry(o):
 names=[]
 while o:names.append(o.name);o=o.parent
 return names
visible=[];hidden=[]
for o in bpy.context.scene.objects:
 o.hide_render=any(n in ('RawBuckets','NetModule2','OptionalRodModule') for n in ancestry(o))
 if o.type=='MESH':(hidden if o.hide_render else visible).append(o.name)
for m in bpy.data.materials:
 col=tuple(m.diffuse_color);m.use_nodes=True;nd=m.node_tree.nodes.get('Principled BSDF');nd.inputs['Base Color'].default_value=col;nd.inputs['Roughness'].default_value=.8;nd.inputs['Metallic'].default_value=0
sc,cam=V.V.stage();sc.cycles.samples=24;sc.render.threads_mode='FIXED';sc.render.threads=6;sc.world.node_tree.nodes['Background'].inputs[1].default_value=.28;sc.render.film_transparent=True;sc.render.image_settings.color_mode='RGBA';sc.render.use_freestyle=False
for o in sc.objects:
 if o.type=='LIGHT':o.location*=4;o.data.energy*=16
sc.render.resolution_x=960;sc.render.resolution_y=720
bpy.context.view_layer.update();p=[o.matrix_world@v.co for o in sc.objects if o.type=='MESH' and not o.hide_render for v in o.data.vertices]
V.fitted(sc,cam,p,(-1,1.3,.78));sc.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
(out/(name+'.json')).write_text(json.dumps({'source':paths[name],'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'visible':visible,'hidden':hidden,'camera_direction':[-1,1.3,.78],'role':'geometry reference only; final illustration generated in existing painted item style'},indent=2));print('CARD REFERENCE PASS',name,flush=True)
