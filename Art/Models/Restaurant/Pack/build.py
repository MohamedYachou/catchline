"""Source-only pack assemblies. Blender Z-up, front -Y matches incumbents."""
import bpy,sys,json,math,shutil,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;R=O.parents[3]
sys.path.insert(0,str(O));from inspect_items import NAMES,reference
sys.path.insert(0,str(R/'Art/Source/Restaurant/kenney'))
from inspect_pack import load,bounds,reset,source
from build_fit import apply_palette,material,scene_setup
KR=next((R/'Art/Downloads/kaykit/restaurant').rglob('fbx(unity)'))
KF=next((R/'Art/Downloads/kaykit/furniture').rglob('fbx(unity)'))
for d in ['renders','comparisons']:(O/d).mkdir(exist_ok=True)
REF={x['name']:x for x in json.loads((O/'reference-inventory.json').read_text())}
PARTS=[]
def component(model,size,pos=(0,0,0),pack='restaurant',rot=180):
 p=(KR if pack=='restaurant' else KF)/(model+'.fbx') if pack in ['restaurant','furniture'] else source(pack.split(':')[-1],model)
 obs=load(p);meshes=[]
 # Bake importer hierarchy before normalisation; shared pack files remain read-only.
 for ob in obs:
  if ob.type=='MESH':
   ob.data=ob.data.copy();ob.data.transform(ob.matrix_world);ob.parent=None;ob.matrix_world=Matrix.Identity(4);meshes.append(ob)
 for ob in obs:
  if ob.type!='MESH':bpy.data.objects.remove(ob,do_unlink=True)
 apply_palette(meshes,pack={'restaurant':'kaykit','furniture':'kaykit-furniture','kenney:furniture':'furniture','kenney:food':'food'}[pack])
 M=Matrix.Rotation(math.radians(rot),4,'Z')
 for ob in meshes:ob.data.transform(M)
 lo,hi=bounds(meshes);s=Vector([size[i]/max(hi[i]-lo[i],1e-7) for i in range(3)])
 centre=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 for ob in meshes:
  for v in ob.data.vertices:v.co=Vector([(v.co[i]-centre[i])*s[i]+pos[i] for i in range(3)])
 PARTS.append(dict(model=model,source=p.relative_to(R).as_posix(),size_blender=list(size),bottom_centre_blender=list(pos),rotation_z_deg=rot,pack=pack))
 return meshes
def atlas_material():
 if bpy.data.materials.get('Pack_detail_atlas'):return bpy.data.materials['Pack_detail_atlas']
 m=bpy.data.materials.new('Pack_detail_atlas');m.use_nodes=True
 n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(O/'restaurantbits_texture-catchline.png'),check_existing=True)
 m.node_tree.links.new(n.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
 return m
def uv_detail(ob,cell=0):
 ob.data.materials.append(atlas_material());uv=ob.data.uv_layers.new(name='UVMap')
 for x in uv.data:x.uv=((cell%8+.5)/8,1-(cell//8+.5)/4)
 return ob
def box(name,pos,size,cell=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);ob=bpy.context.object;ob.name=name;ob.scale=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);uv_detail(ob,cell);return ob
def rod(name,a,b,r=.012,cell=0):
 a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=r,depth=(b-a).length,location=(a+b)*.5)
 ob=bpy.context.object;ob.name=name;ob.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();uv_detail(ob,cell);return ob
def orb(name,pos,r,cell):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=r,location=pos);ob=bpy.context.object;ob.name=name;uv_detail(ob,cell)
def chair(x,y,angle=0):component('chair_A',(.30,.30,.76),(x,y,0),rot=angle+180)
def worktop(width=.88,depth=.76,height=.78):component('kitchencounter_straight_A',(width,depth,height))
def assemble(n):
 global PARTS
 PARTS=[];reset()
 if n in ['Stove','ReliableStove']:
  w= .92 if n=='Stove' else 1.56
  component('stove_multi',(w,.82,.80 if n=='Stove' else .87))
  if n=='ReliableStove':component('pan_A',(.36,.35,.13),(-.35,0,.87))
 elif n=='SoupKettle':
  component('stove_single',(.72,.63,.43));component('pot_B_stew',(.52,.50,.31),(0,0,.43))
 elif n=='PrepCounter':
  component('kitchentable_A',(.94,.85,.79));component('cuttingboard',(.43,.27,.035),(-.16,.03,.79));component('knife',(.26,.04,.055),(-.16,.04,.83),rot=30)
  component('jar_A_medium',(.12,.12,.20),(.30,-.24,.79))
 elif n in ['FridgeV2','BigFridge','DrinksFridge']:
  component('fridge_A' if n!='DrinksFridge' else 'fridge_B',(.76,.85,1.15) if n=='FridgeV2' else (1.46,.84,1.62) if n=='BigFridge' else (.73,.72,1.18))
 elif n=='CoffeeBar':
  worktop();component('kitchenCoffeeMachine',(.43,.38,.48),(-.17,-.10,.78),pack='kenney:furniture');component('cup-coffee',(.15,.15,.15),(.28,.12,.78),pack='kenney:food');component('menu',(.19,.10,.25),(.28,-.25,.78))
 elif n in ['TableFor2','TableFor4','TerraceTable','Booth']:
  if n=='TableFor2':
   component('table_round_A',(.54,.54,.69));chair(0,.33,180);chair(0,-.33,0)
  elif n=='TableFor4':
   component('table_medium_long',(1.10,.48,.68),pack='furniture')
   for x in [-.36,.36]:chair(x,.33,180);chair(x,-.33,0)
  elif n=='Booth':
   component('table_medium_long',(1.66,.42,.68),pack='furniture')
   # Three stations per side, six places within the two-tile width.
   for x in [-.61,0,.61]:
    component('benchCushionLow',(.58,.29,.76),(x,-.32,0),pack='kenney:furniture',rot=180)
    chair(x,.33,180)
  else:
   component('table_round_A',(.54,.54,.69));chair(-.33,0,-90);chair(.33,0,90)
   rod('Parasol pole',(0,0,0),(0,0,1.79),.019,5)
   vs=[(0,0,1.86)]+[(.49*math.cos(i*math.pi/4),.49*math.sin(i*math.pi/4),1.60) for i in range(8)]
   me=bpy.data.meshes.new('Canopy');me.from_pydata(vs,[],[(0,i+1,(i+1)%8+1) for i in range(8)]);ob=bpy.data.objects.new('Parasol canopy',me);bpy.context.scene.collection.objects.link(ob);uv_detail(ob,0)
 elif n=='ReceptionDesk':
  worktop(.92,.86,.78);component('menu',(.29,.18,.25),(.20,0,.78))
 elif n=='SinkDishRack':
  component('kitchentable_sink_large',(1.84,.82,.83));component('dishrack_plates',(.65,.41,.18),(.48,-.02,.57));component('papertowel',(.13,.13,.19),(-.73,-.28,.57))
 elif n=='Fryer':
  worktop(.90,.80,.78);component('pan_B',(.61,.60,.10),(0,0,.78));component('dishrack',(.50,.42,.11),(0,.02,.80));rod('Fryer basket handle',(0,.23,.88),(0,.42,.91),.024,7)
 elif n=='Oven':component('oven',(.82,.81,1.20))
 elif n=='Grill':
  component('stove_multi',(.81,.70,.78));
  for x in [-.27,-.18,-.09,0,.09,.18,.27]:rod('Grill grate',(x,-.26,.81),(x,.26,.81),.015,7)
 elif n=='Steamer':
  component('stove_single',(.66,.65,.45));component('pot_A',(.53,.50,.25),(0,0,.45));component('pot_A',(.53,.50,.25),(0,0,.67));component('lid_A',(.54,.51,.10),(0,0,.92))
 elif n=='PassCounter':
  component('kitchenBar',(1.87,.38,1.05),(0,-.10,0),pack='kenney:furniture')
  for x in [-.50,.50]:component('chair_stool',(.31,.29,.70),(x,.24,0))
 elif n=='PlantPot1':component('pottedPlant',(.38,.40,.72),pack='kenney:furniture')
 elif n=='LampPost':component('lamp_standing',(.47,.32,1.74),pack='furniture')
 elif n in ['Trophy','Chart','Net']:
  size=(.87,.11,.38) if n=='Trophy' else (.88,.08,.62 if n=='Net' else .68)
  component('pictureframe_medium',size,pack='furniture')
  if n=='Trophy':component('fish',(.66,.12,.23),(0,.07,.08),pack='kenney:food',rot=90)
  elif n=='Net':
   for i in range(9):
    x=-.37+i*.0925;rod('Net warp',(x,.061,.055),(x,.061,.565),.006,5)
   for i in range(7):
    z=.055+i*.085;rod('Net weft',(-.37,.065,z),(.37,.065,z),.006,5)
   for x in [-.32,-.16,0,.16,.32]:orb('Net cork float',(x,.085,.55),.028,5)
  else:
   # Minimal coastal navigation insert, no text at game distance.
   pts=[(-.33,.07,.12),(-.22,.07,.22),(-.29,.07,.34),(-.12,.07,.41),(-.07,.07,.57)]
   for a,b in zip(pts,pts[1:]):rod('Chart coastline',a,b,.014,26)
   for x,z in [(.12,.20),(.26,.35),(.07,.48)]:orb('Chart waypoint',(x,.071,z),.023,26)
 elif n=='Jukebox':
  component('cabinet_small',(.64,.43,.64),pack='furniture');component('radio',(.60,.39,.38),(0,0,.64),pack='kenney:furniture')
 elif n=='TableCandle':
  component('cup-saucer',(.12,.12,.014),pack='kenney:food')
  rod('Candle cream wax',(0,0,.02),(0,0,.13),.029,0);orb('Candle flame',(0,0,.147),.014,5)
 else:raise ValueError(n)
 meshes=[o for o in bpy.data.objects if o.type=='MESH']
 # Bake into a single, floor-centred identity mesh; no importer helper hierarchy.
 bpy.ops.object.select_all(action='DESELECT')
 for ob in meshes:ob.select_set(True)
 bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();ob=bpy.context.object
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 # Match incumbent Stage1V2 door/control side, with rotation baked into vertices.
 ob.data.transform(Matrix.Rotation(math.pi,4,'Z'))
 ob.name='Restaurant_'+n;ob.data.name=ob.name+'_Mesh'
 lo,hi=bounds([ob]);z=lo.z
 for v in ob.data.vertices:v.co.z-=z
 # Source imported materials point to the colocated accepted atlas variants.
 for mat in ob.data.materials:
  if mat and mat.use_nodes:
   for node in mat.node_tree.nodes:
    if node.type=='TEX_IMAGE' and node.image:
     name=Path(node.image.filepath).name
     if (O/name).exists():node.image=bpy.data.images.load(str(O/name),check_existing=True)
 lo,hi=bounds([ob]);return ob,dict(name=ob.name,assembly_rotation_baked_z_deg=180,components=PARTS,bounds_blender=[list(lo),list(hi)],size_unity=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],triangles=sum(len(p.vertices)-2 for p in ob.data.polygons),reference=REF[n],notes=NOTES.get(n,''))
NOTES={
 'TerraceTable':'Parasol added per current brief, so height 1.86m exceeds old table-only 0.785m. Seats at original side positions x=+/-0.33.',
 'TableFor2':'Chair centres use runtime Seat front/back +/-0.33, rather than old mesh side chairs. Runtime guest Seat z=+/-0.38.',
 'Booth':'Six visible seats, three per side; rear bench modules plus front chairs. Runtime seat formula can overlap the third pair; lead owns any seating logic correction.',
 'Fryer':'Pack counter, shallow pan and wire rack assembled as a fryer; rack is a visual basket proxy, not a bespoke fryer model.',
 'Jukebox':'Kenney radio on KayKit cabinet: compact music cabinet proxy; packs contain no dedicated jukebox.',
 'Trophy':'Kenney whole fish mounted over KayKit picture frame.',
 'Net':'KayKit wall board plus declared coarse rope/cork geometry; no downloaded fishing net exists.',
 'Chart':'KayKit frame plus coarse atlas-coloured coastline/waypoint insert, no baked text.',
 'BigFridge':'1.46m width preserves incumbent 1.485m width: upgrade spans two tiles despite general 1x1 default.',
 'ReliableStove':'1.56m width preserves incumbent 1.58m width: upgrade spans two tiles despite general 1x1 default.'}
def render(ob,path,span=None):
 lo,hi=bounds([ob]);s=scene_setup(target=(0,0,(hi.z+lo.z)*.48),span=span or max(1.35,hi.x*1.95,hi.z*2.35),width=480,height=420)
 s.cycles.samples=8;s.render.filepath=str(path)
 # Front -Y matches the incumbent game-azimuth inspection.
 # Same pitch/yaw as game; no game-runtime evidence is implied.
 bpy.ops.render.render(write_still=True)
def export(ob,n):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(O/('Restaurant_'+n+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_space_transform=True,bake_anim=False,path_mode='COPY',embed_textures=True)
def build(start,end):
 records=json.loads((O/'manifest.json').read_text()).get('items',[]) if (O/'manifest.json').exists() else []
 for n in NAMES[start:end]:
  ob,rec=assemble(n);export(ob,n);bpy.ops.wm.save_as_mainfile(filepath=str(O/('Restaurant_'+n+'.blend')))
  rec['fbx_sha256']=hashlib.sha256((O/(rec['name']+'.fbx')).read_bytes()).hexdigest()
  records=[x for x in records if x['name']!=rec['name']]+[rec]
  (O/'manifest.json').write_text(json.dumps(dict(units='metres',coordinate_contract='Blender Z-up, front -Y matches Stage1V2; assembly rotation180 baked; Y-up FBX identity local transform; Unity importer handedness checked by lead.',items=records),indent=2))
  if '--no-render' not in sys.argv:render(ob,O/'renders'/(n+'.png'))
  print('BUILT',n,flush=True)
if __name__=='__main__':
 for p in (R/'Art/Source/Restaurant/kaykit').glob('*texture-catchline.png'):shutil.copy2(p,O/p.name)
 shutil.copy2(R/'Art/Source/Restaurant/kenney/food-colormap-catchline.png',O/'food-colormap-catchline.png')
 
 if ',' in sys.argv[-1]:
  for i in map(int,sys.argv[-1].split(',')):build(i,i+1)
 else:
  a,b=map(int,sys.argv[-1].split(':'));build(a,b)

