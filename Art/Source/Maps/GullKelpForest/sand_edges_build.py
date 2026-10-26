import bpy,bmesh,json
from pathlib import Path
R=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent;O=R/'Art/Models/Maps/GullKelpForest'
B=R.parent/'Catchline-sim/Backups/codex2-sand-edges-before'
p=json.loads((S/'sand-edges-plan.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(B/'GullKelpForestSeaV2.blend'))
o=bpy.data.objects['ConnectedBathymetry'];old=o.data;mesh=bpy.data.meshes.new(old.name+'_OrganicSand')
mesh.from_pydata(p['vertices'],[],p['faces']);mesh.update()
for m in old.materials:mesh.materials.append(m)
for name,t in [('M_SandEdgeInner',.67),('M_SandEdgeOuter',.33)]:
 m=old.materials[0].copy();m.name=name
 for field in ['diffuse_color']:
  a=getattr(old.materials[0],field);b=getattr(old.materials[1],field);setattr(m,field,tuple(a[i]*t+b[i]*(1-t) for i in range(4)))
 if m.use_nodes:
  node=m.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=m.diffuse_color
 mesh.materials.append(m)
for f,i in zip(mesh.polygons,p['material_indices']):f.material_index=i
for k in old.keys():mesh[k]=old[k]
o.data=mesh;bpy.data.meshes.remove(old);mesh.name='ConnectedBathymetry'
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(O/'GullKelpForestSeaV2.blend'))
for o in bpy.context.scene.objects:
 if o.type=='MESH':
  for v in o.data.vertices:x,y,z=v.co;v.co=(-x,z,-y)
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 elif o.type=='EMPTY' and o.parent:
  x,y,z=o.location;o.location=(-x,z,-y)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(O/'GullKelpForestSeaV2.fbx'),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=False,bake_space_transform=False,use_triangles=True,bake_anim=False,add_leaf_bones=False)
print('SAND EDGES BUILD EXPORTED',flush=True)
