"""Targeted atlas-UV steel finish; no geometry/material/UV1 changes. Run in Windows Blender."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
def posix(p):return str(p).replace(chr(92),'/')
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V2';B=O/'_station-finish-backup'
components={'Stove':[154,190,394],'Oven':[14,262],'FridgeV2':[171],'Fryer':[178,214,418],'PrepCounter':[34,166,370,594],'SoupKettle':[62],'SinkDishRack':[154,190,394,598,622,646,670],'CoffeeBar':[698,734]}
opts=dict(use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE',colors_type='LINEAR')
def apply(me,indices):
 uv=me.uv_layers[0].data;changed=0;oldcells={}
 for i in indices:
  p=me.polygons[i];avg=sum((uv[k].uv for k in p.loop_indices),Vector((0.,0.)))/len(p.loop_indices);x=min(7,max(0,int(avg.x*8)));y=min(3,max(0,int((1-avg.y)*4)));old=y*8+x
  if old==7:continue
  delta=Vector(((7-x)/8,y/4))
  for k in p.loop_indices:uv[k].uv+=delta
  changed+=1;oldcells[str(old)]=oldcells.get(str(old),0)+1
 return {'changed_polygons':changed,'old_cells':oldcells,'destination_cell':7}
bpy.ops.wm.open_mainfile(filepath=posix(B/'Stage1V2/Stage1V2.blend'));bpy.context.preferences.filepaths.save_version=0
# Resolve the two known original atlas images explicitly (directory existence is insufficient).
for filename in ['Restaurant_BaseColor.png','Restaurant_Surface.png']:
 im=bpy.data.images[filename];target=V/'textures'/filename;assert target.is_file()
 im.filepath_raw=target.as_posix();im.reload();assert Path(bpy.path.abspath(im.filepath)).is_file(),(im.name,im.filepath)
changes={};indices={};topology={}
for name,selected in components.items():
 root=bpy.data.objects[name];ob=next(o for o in root.children if o.type=='MESH');me=ob.data;parent=list(range(len(me.vertices)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for e in me.edges:
  a,b=map(find,e.vertices);parent[b]=a
 chosen=[p.index for p in me.polygons if find(p.vertices[0]) in selected];assert chosen,name
 indices[name]=chosen;topology[name]=[list(p.vertices) for p in me.polygons];changes[name]={'kit':apply(me,chosen),'components':selected,'polygon_indices':chosen}
 matrix=root.matrix_basis.copy();root.matrix_basis=Matrix.Identity(4);bpy.context.view_layer.update();bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for o in root.children:o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=posix(V/'items'/f'{name}.fbx'),**opts)
 root.matrix_basis=matrix;bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=posix(V/'Stage1V2.blend'))
bpy.ops.wm.open_mainfile(filepath=posix(B/'Stage1V4/Stage1V4.blend'));bpy.context.preferences.filepaths.save_version=0
for name,chosen in indices.items():
 ob=bpy.data.objects[name];assert [list(p.vertices) for p in ob.data.polygons]==topology[name],name
 changes[name]['V4']=apply(ob.data,chosen)
# Same Stage1V4 exporter convention; temporary clones only, never review/floor/water props.
prod=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')];bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in prod:
 n=o.copy();n.data=o.data.copy();n.name='EXPORT_'+o.name;bpy.context.scene.collection.objects.link(n);n.select_set(True);copies.append(n)
bpy.ops.export_scene.fbx(filepath=posix(O/'Stage1V4.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,colors_type='LINEAR',path_mode='RELATIVE')
for n in copies:bpy.data.objects.remove(n,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=posix(O/'Stage1V4.blend'));(O/'station-finish-changes.json').write_text(json.dumps(changes,indent=2));print('STATION FINISH BUILD PASS',flush=True)
