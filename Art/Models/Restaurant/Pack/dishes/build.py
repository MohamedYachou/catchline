"""PACK-DISHES-1: additive source assemblies; run in standalone Blender."""
import bpy, sys, json, math, copy, shutil, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
O=Path(__file__).resolve().parent
R=O.parents[4]
K=R/'Art/Source/Restaurant/kenney'
sys.path.insert(0,str(K))
from inspect_pack import reset, load, bounds
from build_fit import RECIPES, instantiate, component, scene_setup, table

NAMES=['Dish_GrilledFish','Dish_FilletsLemon','Dish_FishSoup','Dish_CoffeeBiscuits','Dish_Lemonade','GrilledFishPlate']
NOTES={
 'Dish_GrilledFish':'Kenney plate + roasted whole fish + lemon-half + KayKit lettuce garnish. No grill-score texture in pack.',
 'Dish_FilletsLemon':'Kenney plate + two salmon toppings (rice removed) + loose fries (carton removed) + lemon-half. Salmon remains salmon coloured.',
 'Dish_FishSoup':'Kenney plate + bowl-soup + utensil-spoon + two small salmon topping pieces. Original vegetable broth retained with visible fish pieces.',
 'Dish_CoffeeBiscuits':'Kenney cup-saucer + cup-coffee + cookie. Shared runtime visual for coffee/tea/bread, per existing game mapping.',
 'Dish_Lemonade':'Kenney soda-glass + lemon-half with accepted lemonade atlas. Shared runtime visual for lemonade/beer, per existing game mapping.',
 'GrilledFishPlate':'Exact duplicate mesh/material/UV of Dish_GrilledFish, named for the carried two-handed prop.'}

def recipes(n):
 if n in ['Dish_GrilledFish','GrilledFishPlate']:
  p=copy.deepcopy(next(x[2] for x in RECIPES if x[0]=='GrilledFish'))
  factor=.22/.31
  for c in p:
   c['target_size_m']=[v*factor for v in c['target_size_m']]
   c['offset_bottom_center_blender_m']=[v*factor for v in c['offset_bottom_center_blender_m']]
  p.append(component('food_ingredient_lettuce',(.048,.041,.014),(-.048,.052,.019),pack='kaykit',role='lettuce garnish'))
 elif n=='Dish_FilletsLemon':
  p=copy.deepcopy(next(x[2] for x in RECIPES if x[0]=='PanFish'))
  factor=.22/.29
  for c in p:
   c['target_size_m']=[v*factor for v in c['target_size_m']]
   c['offset_bottom_center_blender_m']=[v*factor for v in c['offset_bottom_center_blender_m']]
  p.append(component('fries-loose',(.058,.095,.026),(.048,-.012,.025),(90,0,10),pack='derived',role='loose fries, carton removed'))
 elif n=='Dish_FishSoup':
  p=[component('plate',(.22,.22,.012),(0,0,0)),component('bowl-soup',(.16,.16,.067),(0,0,.010)),component('utensil-spoon',(.018,.153,.009),(.086,0,.014),(0,0,90)),component('salmon-fillet',(.029,.018,.009),(-.025,0,.068),pack='derived'),component('salmon-fillet',(.023,.016,.008),(.025,.008,.068),(0,0,25),pack='derived')]
 elif n=='Dish_CoffeeBiscuits':
  p=[component('cup-saucer',(.15,.15,.012),(0,0,0)),component('cup-coffee',(.082,.095,.075),(-.012,.012,.010)),component('cookie',(.041,.041,.009),(.036,-.035,.012))]
 elif n=='Dish_Lemonade':
  p=[component('soda-glass',(.067,.067,.15),(0,0,0),variant='lemonade'),component('lemon-half',(.031,.031,.018),(.029,0,.098))]
 return p

def assemble(n):
 reset();parts=recipes(n)
 for i,c in enumerate(parts):instantiate(c,f'{n} part{i}')
 meshes=[o for o in bpy.data.objects if o.type=='MESH']
 # Bake every evaluated parent/source matrix before detaching importer helpers.
 for ob in meshes:
  mat=ob.matrix_world.copy();ob.data=ob.data.copy();ob.parent=None;ob.matrix_world=Matrix.Identity(4);ob.data.transform(mat)
 for ob in list(bpy.data.objects):
  if ob.type!='MESH':bpy.data.objects.remove(ob,do_unlink=True)
 bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();ob=bpy.context.object
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 lo,hi=bounds([ob]);centre=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 for v in ob.data.vertices:v.co-=centre
 ob.name='Restaurant_'+n;ob.data.name=ob.name+'_Mesh'
 for m in ob.data.materials:
  if m and m.use_nodes:
   for node in m.node_tree.nodes:
    if node.type=='TEX_IMAGE' and node.image:
     name=Path(node.image.filepath).name
     assert (O/name).exists(), name
     node.image=bpy.data.images.load(str(O/name),check_existing=True)
 lo,hi=bounds([ob])
 return ob,dict(name=ob.name,components=parts,note=NOTES[n],bounds_blender=[list(lo),list(hi)],size_unity=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],triangles=sum(len(p.vertices)-2 for p in ob.data.polygons))

def build(start,end):
 (O/'renders').mkdir(exist_ok=True)
 for p in [K/'food-colormap-catchline.png',K/'food-colormap-roast.png',K/'food-colormap-lemonade.png',K.parent/'kaykit/restaurantbits_texture-catchline.png']:shutil.copy2(p,O/p.name)
 records=json.loads((O/'manifest.json').read_text())['items'] if (O/'manifest.json').exists() else []
 for n in NAMES[start:end]:
  ob,rec=assemble(n)
  bpy.ops.export_scene.fbx(filepath=str(O/(ob.name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=True,bake_anim=False,path_mode='COPY',embed_textures=True)
  bpy.ops.wm.save_as_mainfile(filepath=str(O/(ob.name+'.blend')))
  rec['fbx_sha256']=hashlib.sha256((O/(ob.name+'.fbx')).read_bytes()).hexdigest()
  records=[r for r in records if r['name']!=rec['name']]+[rec]
  (O/'manifest.json').write_text(json.dumps(dict(units='metres',coordinate_contract='Blender Z-up authoring; bottom centre pivot. FBX Y-up, metre units, baked axis conversion, identity local root. Unity handedness/native import remains lead verification.',items=records),indent=2))
  print('BUILT',n,rec['size_unity'],flush=True)

if __name__=='__main__':
 a,b=map(int,sys.argv[-1].split(':'));build(a,b)
