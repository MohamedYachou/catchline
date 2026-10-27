"""Actual shipped FBXs, reconstructed item-art camera/light/ink recipe. No Assets writes."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
import render as V
FILES={'hull3':'PrepFisherV1.fbx','hull4':'Tier5DeepLines103.fbx'}
def ancestry(o):
 out=[]
 while o:out.append(o.name);o=o.parent
 return out

def run(name):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 source=B.R/'Assets/Art/Models/Boats'/FILES[name];bpy.ops.import_scene.fbx(filepath=str(source),use_anim=False)
 hidden=[];visible=[]
 for o in bpy.context.scene.objects:
  o.hide_render=any(n in ('RawBuckets','NetModule2','OptionalRodModule') for n in ancestry(o))
  if o.type=='MESH':(hidden if o.hide_render else visible).append(o.name)
 # Import diffuse materials as matte Principled, preserving the actual source palette.
 for m in bpy.data.materials:
  col=tuple(m.diffuse_color);m.use_nodes=True;nd=m.node_tree.nodes.get('Principled BSDF');nd.inputs['Base Color'].default_value=col;nd.inputs['Roughness'].default_value=.80;nd.inputs['Metallic'].default_value=0
 sc,cam=V.V.stage();sc.cycles.samples=48;sc.world.node_tree.nodes['Background'].inputs[1].default_value=.28;sc.render.film_transparent=True;sc.render.image_settings.color_mode='RGBA'
 for o in sc.objects:
  if o.type=='LIGHT':o.location*=4;o.data.energy*=16
 sc.render.resolution_x=960;sc.render.resolution_y=720;sc.render.use_freestyle=True;sc.render.line_thickness=1.0
 fs=sc.view_layers[0].freestyle_settings;fs.crease_angle=math.radians(120)
 ls=fs.linesets[0];ls.select_silhouette=True;ls.select_border=True;ls.select_crease=True;ls.select_external_contour=True;ls.select_material_boundary=False
 if ls.linestyle is None:ls.linestyle=bpy.data.linestyles.new('ItemNavyInk')
 ls.linestyle.color=(.055,.095,.115);ls.linestyle.thickness=2.2
 bpy.context.view_layer.update();p=[o.matrix_world@v.co for o in sc.objects if o.type=='MESH' and not o.hide_render for v in o.data.vertices]
 V.fitted(sc,cam,p,(-1,1.3,.78));out=B.R/'Art/Source/HarbourLife/ui';out.mkdir(exist_ok=True)
 path=out/(name+'-raw.png');sc.render.filepath=str(path);bpy.ops.wm.save_as_mainfile(filepath=str(out/(name+'-review.blend')));bpy.ops.render.render(write_still=True)
 receipt={'source':source.relative_to(B.R).as_posix(),'source_sha256':B.sha(source),'raw':path.name,'raw_sha256':B.sha(path),'visible_meshes':visible,'hidden_meshes':hidden,'variant':'RawIceCoolers; single net; optional rods hidden; DeepLineModule visible','camera_direction':[-1,1.3,.78],'camera_projection':'orthographic','camera_matrix':[list(r) for r in cam.matrix_world],'ortho_scale':cam.data.ortho_scale,'raw_size':[960,720],'outline':'Freestyle navy 2.2px at 2x; crease120deg, silhouette/border; outer2px at final','light_recipe':'Skerries warm key/cool fill, positions4x energy16x for boat scale','recipe_limitation':'Original item sheet was generated; exact historic Blender camera/lighting does not exist. This is a reconstruction using the supplied two current PNG references.'}
 (out/(name+'-render.json')).write_text(json.dumps(receipt,indent=2)+'\n');print('HARBOUR BOAT RENDER',name,flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
