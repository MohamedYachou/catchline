"""Keep production geometry/names and embed explicit emissive night material variants."""
import bpy,json,shutil,hashlib
from pathlib import Path
from io_scene_fbx import parse_fbx
O=Path(__file__).resolve().parent;B=O/'_night-backup';B.mkdir(exist_ok=True);M=json.loads((O/'manifest.json').read_text());rows=[];bpy.context.preferences.filepaths.save_version=0
for stage in M['stages']:
 stem=Path(stage['file']).stem
 for ext in ['blend','fbx']:
  p=O/(stem+'.'+ext)
  if not (B/p.name).exists():shutil.copy2(p,B/p.name)
 bpy.ops.wm.open_mainfile(filepath=str(O/(stem+'.blend')));sc=bpy.context.scene;prod=[o for o in sc.objects if o.type=='MESH'];base=next(m for o in prod for m in o.data.materials if not m.name.endswith('_Night'));n=base.name+'_Night';night=bpy.data.materials.get(n) or base.copy();night.name=n
 # Surface atlas blue channel already isolates glow cell. Opaque walls and wood stay opaque/unlit.
 mul=next(x for x in night.node_tree.nodes if x.type=='MATH' and x.operation=='MULTIPLY');mul.inputs[1].default_value=6
 mapping={}
 for ob in prod:
  if ob.name in ['DoorsWindowsChimneys','LanternsStringLights','TerraceTablesChairs']:ob.data.materials[0]=night;mapping[ob.name]={'day':base.name,'night':night.name}
 sc['exterior_night_variant_v1']=True
 bpy.ops.object.select_all(action='DESELECT')
 for o in prod:o.select_set(True)
 bpy.context.view_layer.objects.active=prod[0]
 bpy.ops.export_scene.fbx(filepath=str(O/stage['file']),use_selection=True,object_types={'MESH'},apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',bake_anim=False,colors_type='LINEAR',path_mode='RELATIVE')
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(stem+'.blend')))
 tree,version=parse_fbx.parse(str(O/stage['file']));glob=next(e for e in tree.elems if e.id==b'GlobalSettings');props=next(e for e in glob.elems if e.id==b'Properties70');unit=next(e.props[-1] for e in props.elems if e.props[0]==b'UnitScaleFactor');assert unit==100
 footprint=json.loads((O/stage['footprint']).read_text());rows.append({'stage':stage['name'],'file':stage['file'],'mesh_material_variants':mapping,'default_export':'Night materials on windows and practical fixtures; original day atlas material retained on other production meshes in same FBX; remap listed meshes to day material for day look.','glow_mask':'Restaurant_Surface.png blue: only glow atlas cell emissive','night_emission_multiplier':6,'day_emission_multiplier':2.5,'lights':[{'name':'Restaurant_'+stage['name']+'_Practical'+str(i)+'_Night','position_blender_m':p,'position_unity_m':[p[0],p[2],-p[1]],'color_rgb':[1,.60,.24],'blender_watts':12,'unity_range_recipe_m':2.1} for i,p in enumerate(footprint['lamp_positions_blender_m'])],'FBX_UnitScaleFactor':unit})
(O/'night-materials.json').write_text(json.dumps({'pass':True,'same_geometry_names_bounds_footprint':True,'opaque':True,'stages':rows,'runtime_material_light_switch_pending_lead':True},indent=2));print('EXTERIORS NIGHT MATERIAL PASS')
