"""Targeted UV/pigment repair. Geometry and every export node remain unchanged."""
import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent
source=O/'_backwall-backup/Stage1V4.blend'
if not source.exists():source=O/'Stage1V4.blend'
bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
meshes=[o for o in sc.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')]
def sig(o):
 return hashlib.sha256(repr(([tuple(v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],list(map(tuple,o.matrix_world)),[[tuple(d.uv) for d in u.data] for u in list(o.data.uv_layers)[1:]])).encode()).hexdigest()
before={o.name:sig(o) for o in meshes};changes=[]
mat=next(m for m in bpy.data.materials if m.name.startswith('Restaurant_Atlas') and any(n.type=='TEX_IMAGE' and n.image and 'Stage1V4' in bpy.path.abspath(n.image.filepath) for n in m.node_tree.nodes))
cells={c['name']:c for c in json.loads((O/'textures/atlas.json').read_text())['cells']}
for ob in meshes:
 cell='stonecool' if ob.name.startswith('RearMasonry_') else 'navy' if ob.name=='RearCoping' else 'wooddark' if ob.name=='HighKitchenShelf' else None
 if cell is None:continue
 me=ob.data;me.materials.clear();me.materials.append(mat)
 attribute=next(n for n in mat.node_tree.nodes if n.type=='VERTEX_COLOR').layer_name
 ao=me.color_attributes.get(attribute) or me.color_attributes.new(name=attribute,type='FLOAT_COLOR',domain='CORNER')
 for d in ao.data:d.color=(.85,.85,.85,1)
 me.uv_layers[0].name='UV0'
 uv=me.uv_layers[0].data;x,y,w,h=cells[cell]['pixel_cell']
 for p in me.polygons:
  p.material_index=0;axes=[k for k in range(3) if k!=max(range(3),key=lambda k:abs(p.normal[k]))];vs=[me.vertices[me.loops[i].vertex_index].co for i in p.loop_indices];lo=[min(v[k] for v in vs) for k in axes];hi=[max(v[k] for v in vs) for k in axes]
  for i,v in zip(p.loop_indices,vs):
   a=(v[axes[0]]-lo[0])/max(hi[0]-lo[0],1e-8);b=(v[axes[1]]-lo[1])/max(hi[1]-lo[1],1e-8);uv[i].uv=((x+24+a*(w-48))/2048,1-(y+24+b*(h-48))/2048)
 changes.append({'node':'EXPORT_'+ob.name,'atlas_cell':cell,'faces':len(me.polygons)})
assert changes and all(sig(o)==before[o.name] for o in meshes)
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in meshes:
 c=o.copy();c.data=o.data.copy();sc.collection.objects.link(c);c.name='EXPORT_'+o.name;c.select_set(True);copies.append(c)
bpy.ops.export_scene.fbx(filepath=str(O/'Stage1V4.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,colors_type='LINEAR',path_mode='RELATIVE')
for o in copies:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Stage1V4.blend'),relative_remap=True)
(O/'backwall-changes.json').write_text(json.dumps({'changes':changes,'geometry_transform_UV1_unchanged':True,'source_signatures':before,'material':mat.name,'fbx_sha256':hashlib.sha256((O/'Stage1V4.fbx').read_bytes()).hexdigest()},indent=2));print('BACKWALL BUILD PASS',len(changes),flush=True)
