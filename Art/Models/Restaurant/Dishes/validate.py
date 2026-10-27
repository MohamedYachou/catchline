import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;P=O/'renders';P.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cells=json.loads((O/'textures/atlas.json').read_text())['cells'];metrics=json.loads((O/'build-metrics.json').read_text())['dishes'];rows=[]
for row in metrics:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/(row['name']+'.fbx')));obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(obs)==1 and len(bpy.context.scene.objects)==1;ob=obs[0];assert ob.name==row['name'];assert len(ob.data.materials)==1;assert ob.data.materials[0].name=='Restaurant_Atlas_Dishes';assert len(ob.data.uv_layers)==1
 pts=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)];assert abs(lo[2])<1e-5;assert max(hi[k]-lo[k] for k in range(3))<.35
 delta=max(abs(x-y) for a,b in zip([lo,hi],row['bounds_blender_m']) for x,y in zip(a,b));assert delta<1e-5
 used=set()
 for poly in ob.data.polygons:
  uvs=[ob.data.uv_layers[0].data[i].uv for i in poly.loop_indices];valid=[]
  for c in cells:
   x,y,w,h=c['pixel_cell'];u0,u1=(x+16)/2048,(x+w-16)/2048;v0,v1=1-(y+h-16)/2048,1-(y+16)/2048
   if all(u0-1e-6<=uv.x<=u1+1e-6 and v0-1e-6<=uv.y<=v1+1e-6 for uv in uvs):valid.append(c['name'])
  assert len(valid)==1,(row['name'],poly.index,valid);used.add(valid[0])
 assert used==set(row['atlas_cells'])
 images=[n.image for n in ob.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image];assert images and all(i.has_data and min(i.size)>0 for i in images)
 ob.data.calc_loop_triangles();rows.append({'name':row['name'],'fbx_sha256':sha(O/(row['name']+'.fbx')),'world_bounds_m':[lo,hi],'roundtrip_bounds_max_delta_m':delta,'triangles':len(ob.data.loop_triangles),'one_mesh_only':True,'one_atlas_material':True,'uv_each_face_inside_single_inset_cell':True,'cells':sorted(used),'loaded_embedded_images':[{'name':i.name,'size':list(i.size)} for i in images]})
(O/'validation.json').write_text(json.dumps({'pass':True,'dishes':rows,'native_unity_unverified':True},indent=2));print('DISH IMPORT AUDIT PASS',flush=True)
# Presentation in a separate file; export sources have no lights/cameras/table.
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;props=[]
for i,row in enumerate(metrics):
 bpy.ops.import_scene.fbx(filepath=str(O/(row['name']+'.fbx')));ob=next(o for o in sc.objects if o.type=='MESH' and o.name==row['name']);ob.location=(0,0,0);props.append(ob)
sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True;sc.cycles.device='GPU';prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
for d in prefs.devices:d.use=d.type=='OPTIX'
sc.world=bpy.data.worlds.new('Night room');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.19,.27,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.5
for loc,power,size,col in [((-.6,-1.3,2),65,2,(1,.83,.65)),((1,-.2,1),25,1,(.65,.84,1))]:
 data=bpy.data.lights.new('Softbox','AREA');data.energy=power;data.color=col;data.shape='DISK';data.size=size;ob=bpy.data.objects.new('Softbox',data);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(-ob.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('V4-angle camera',bpy.data.cameras.new('V4-angle camera'));sc.collection.objects.link(cam);sc.camera=cam;cam.rotation_euler=json.loads((O.parent/'Stage1V4/final-cameras.json').read_text())[0]['rotation_blender_rad'];cam.data.lens=58;sc.render.resolution_x=600;sc.render.resolution_y=600;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG';sc.render.film_transparent=True;sc.view_settings.view_transform='AgX'
for ob in props:
 for other in props:other.hide_render=other!=ob
 cam.location=Vector((0,0,.052))+cam.rotation_euler.to_matrix()@Vector((0,0,.85));sc.render.filepath=str(P/(ob.name+'.png'));bpy.ops.render.render(write_still=True)
for i,ob in enumerate(props):ob.hide_render=False;ob.location=((i-2)*.35,0,.7)
# Simple warm table, photographic proof only; one-to-one dimensions, no prop scaling.
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.68));table=bpy.context.object;table.name='REVIEW_ONLY_Table';table.dimensions=(1.85,.50,.04);mat=bpy.data.materials.new('REVIEW_ONLY_WarmWood');mat.use_nodes=True;mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.22,.095,.038,1);mat.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.55;table.data.materials.append(mat)
sc.render.film_transparent=False;sc.render.resolution_x=1440;sc.render.resolution_y=600;cam.location=Vector((0,0,.73))+cam.rotation_euler.to_matrix()@Vector((0,0,3.4));sc.render.filepath=str(O/'table-lineup.png');bpy.ops.render.render(write_still=True);bpy.ops.wm.save_as_mainfile(filepath=str(O/'Dishes-V4-check.blend'));print('DISH RENDER PASS',flush=True)
