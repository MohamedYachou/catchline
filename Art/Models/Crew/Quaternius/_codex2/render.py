import bpy,json,sys,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[5];O=R/'Art/Models/Crew/Quaternius';W=O/'_codex2'
rows=json.loads((W/'roster.json').read_text())
def plain(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=.85;return m
def stage():
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.max_bounces=4;s.world=s.world or bpy.data.worlds.new('PROOF_World');s.world.color=(.7,.7,.7);s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.72,.77,.83,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
 s.view_settings.view_transform='Standard';s.view_settings.look='Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
 for n,loc,power,size in [('Key',(-3,4,6),200,4),('Fill',(4,1,4),60,5),('Rim',(0,-3,4),90,3)]:
  bpy.ops.object.light_add(type='AREA',location=loc);l=bpy.context.object;l.name='PROOF_'+n;l.data.energy=power;l.data.size=size;l.rotation_euler=(Vector((0,0,1))-l.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();s.camera=bpy.context.object;s.camera.data.type='ORTHO';s.camera.data.lens=50
 return s
def camera(s,target,pitch,scale,w,h):
 t=Vector(target);p=math.radians(pitch);y=math.radians(2);d=Vector((math.sin(y)*math.cos(p),math.cos(y)*math.cos(p),math.sin(p)));s.camera.location=t+d*10;s.camera.rotation_euler=(-d).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=scale;s.render.resolution_x=w;s.render.resolution_y=h;s.render.resolution_percentage=100;bpy.context.view_layer.update()
mode=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['details']
if mode[0]=='details':
 names=mode[1:] or [r['name'] for r in rows]
 for name in names:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/f'{name}.fbx'),ignore_leaf_bones=False,automatic_bone_orientation=False);s=stage();camera(s,(0,.0,1.7),12,.52,600,660);s.render.filepath=str(W/f'{name}-head.png');bpy.ops.render.render(write_still=True);print('HEAD_RENDERED',name,flush=True)
elif mode[0]=='individual':
 for row in rows:
  name=row['name'];bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(O/f'{name}.fbx'),ignore_leaf_bones=False,automatic_bone_orientation=False);s=stage()
  floor=plain('PROOF_floor',(.72,.76,.73));line=plain('PROOF_grid',(.35,.47,.48))
  bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.007));bpy.context.object.data.materials.append(floor)
  for k in range(-3,4):
   for axis in [0,1]:
    bpy.ops.mesh.primitive_cube_add(size=1,location=(k if axis==0 else 0,k if axis else 0,-.002));o=bpy.context.object;o.dimensions=(.012,6,.003) if axis==0 else (6,.012,.003);o.data.materials.append(line)
  camera(s,(0,0,.85),38,2.6,900,900);s.render.filepath=str(W/f'{name}-proof.png');bpy.ops.render.render(write_still=True);print('BODY_RENDERED',name,flush=True)
else:
 bpy.ops.wm.read_factory_settings(use_empty=True);model_groups=[]
 for i,row in enumerate(rows):
  before=set(bpy.context.scene.objects);bpy.ops.import_scene.fbx(filepath=str(O/f'{row["name"]}.fbx'),ignore_leaf_bones=False,automatic_bone_orientation=False);added=set(bpy.context.scene.objects)-before;arm=next(o for o in added if o.type=='ARMATURE');arm.location.x=(i%3-1)*2.6;arm.location.y=1.65 if i<3 else -1.65;model_groups.append((row['name'],[o for o in added if o.type=='MESH']))
 s=stage()
 # One metre floor tiles and thin grid lines, proof-only geometry.
 m=plain('PROOF_floor',(.72,.76,.73));line=plain('PROOF_grid',(.35,.47,.48))
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.007));bpy.context.object.data.materials.append(m)
 for k in range(-6,7):
  for axis in [0,1]:
   bpy.ops.mesh.primitive_cube_add(size=1,location=(k if axis==0 else 0,k if axis else 0,-.002));o=bpy.context.object;o.dimensions=(.012,12,.003) if axis==0 else (12,.012,.003);o.data.materials.append(line)
 camera(s,(0,0,.86),38,8.9,2880,2000);s.render.filepath=str(W/'crew-grid.png')
 # Record exact pixel anchors and camera pose for contact-sheet lettering.
 from bpy_extras.object_utils import world_to_camera_view
 anchors=[];bounds={}
 for name,meshes in model_groups:
  points=[world_to_camera_view(s,s.camera,o.matrix_world@v.co) for o in meshes for v in o.data.vertices];box=[min(p.x for p in points),min(p.y for p in points),max(p.x for p in points),max(p.y for p in points)];assert min(box)>=0 and max(box)<=1,(name,box);bounds[name]=box
 (W/'grid-bounds.json').write_text(json.dumps(bounds,indent=2)+'\n')
 for i,row in enumerate(rows):
  a=world_to_camera_view(s,s.camera,Vector(((i%3-1)*2.6,1.65 if i<3 else -1.65,-.22)));anchors.append(dict(name=row['name'],x=a.x*2880,y=(1-a.y)*2000))
 (W/'render-layout.json').write_text(json.dumps(dict(pitch=38,yaw=2,gridMetres=1,resolution=[2880,2000],anchors=anchors),indent=2)+'\n');bpy.ops.render.render(write_still=True)
 print('GRID_RENDERED',flush=True)
