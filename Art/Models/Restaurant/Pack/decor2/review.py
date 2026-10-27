"""Independent fresh-FBX audit and game-camera source proofs."""
import bpy,sys,json,math,hashlib
sys.dont_write_bytecode=True  # Keep imported source helper caches read-only.
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parent;R=O.parents[4]
sys.path.insert(0,str(R/'Art/Source/Restaurant/kenney'))
from inspect_pack import reset,load,bounds
from build_fit import material
from bpy_extras.object_utils import world_to_camera_view
M=json.loads((O/'manifest.json').read_text())['items'];(O/'renders').mkdir(exist_ok=True)

def import_piece(rec,display=False,at=(0,0,0)):
 obs=load(O/(rec['name']+'.fbx'));meshes=[o for o in obs if o.type=='MESH']
 for o in meshes:
  o.data=o.data.copy();o.data.transform(o.matrix_world);o.parent=None;o.matrix_world=Matrix.Identity(4)
  if display and (rec['mount']=='wall' or rec['stem'] in {'MenuBoard','WineRack'}):o.data.transform(Matrix.Rotation(math.pi,4,'Z'))
  for v in o.data.vertices:v.co+=Vector(at)
 # Fresh importer sometimes retains embedded image file names; force only exact adjacent atlas if file path exists.
 for o in meshes:
  for m in o.data.materials:
   if m and m.use_nodes:
    for n in m.node_tree.nodes:
     if n.type=='TEX_IMAGE' and n.image:
      basename=Path(n.image.filepath).name
      if (O/basename).exists():n.image=bpy.data.images.load(str(O/basename),check_existing=True);n.image.pack()
 return meshes

def audit():
 rows=[]
 for rec in M:
  reset();obs=import_piece(rec);lo,hi=bounds(obs);expected=rec['bounds_blender'];err=max(abs(lo[i]-expected[0][i]) for i in range(3));err=max(err,max(abs(hi[i]-expected[1][i]) for i in range(3)))
  images=[];badm=[]
  for o in obs:
   for m in o.data.materials:
    im=[n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m and m.use_nodes else []
    if not im:badm.append(m.name if m else 'None')
    images.extend([dict(name=i.name,size=list(i.size),path=i.filepath) for i in im])
  wall=rec['mount']=='wall'
  checks=dict(one_mesh=len(obs)==1,finite=all(math.isfinite(c) for v in [lo,hi] for c in v),bounds_match=err<1e-5,origin=(abs(lo.y)<1e-5 and abs(lo.z+hi.z)<1e-5) if wall else (abs(lo.z)<1e-5 and abs(lo.y+hi.y)<1e-5),centred_x=abs(lo.x+hi.x)<1e-5,valid_uv=all(o.data.uv_layers.active and all(math.isfinite(c) and -.0001<=c<=1.0001 for v in o.data.uv_layers.active.data for c in v.uv) for o in obs),atlas_only=not badm and bool(images),decoded_images=all(i['size'][0]>0 and i['size'][1]>0 for i in images),triangles_match=sum(len(p.vertices)-2 for o in obs for p in o.data.polygons)==rec['triangles'],fbx_hash=hashlib.sha256((O/(rec['name']+'.fbx')).read_bytes()).hexdigest()==rec['fbx_sha256'])
  rows.append(dict(name=rec['name'],checks=checks,error_m=err,images=images,bounds=[list(lo),list(hi)]))
 (O/'mesh-audit.json').write_text(json.dumps(dict(pass_all=all(all(r['checks'].values()) for r in rows),items=rows),indent=2));print('FRESH_AUDIT',len(rows),all(all(r['checks'].values()) for r in rows),flush=True)

def scene(target,span,width,height):
 s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=12;s.cycles.use_denoising=True
 try:
  p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
  for d in p.devices:d.use=d.type=='OPTIX'
  s.cycles.device='GPU'
 except Exception:pass
 s.render.resolution_x=width;s.render.resolution_y=height;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='Standard'
 s.world=bpy.data.worlds.new('Coastal fill');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.61,.72,.79,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
 bpy.ops.mesh.primitive_plane_add(size=70,location=(0,0,-.015));bpy.context.object.data.materials.append(material('Quay','#DFD6C3'))
 bpy.ops.object.light_add(type='AREA',location=(-4,-6,12));bpy.context.object.data.energy=2000;bpy.context.object.data.size=8
 bpy.ops.object.camera_add();c=bpy.context.object;c.data.type='ORTHO';c.data.ortho_scale=span;t=Vector(target);pitch=math.radians(38);yaw=math.radians(2)
 c.location=t+Vector((math.sin(yaw)*math.cos(pitch),-math.cos(yaw)*math.cos(pitch),math.sin(pitch)))*35;c.rotation_euler=(t-c.location).to_track_quat('-Z','Y').to_euler();s.camera=c
 return s

def individual(walls_only=False,stems=None):
 for rec in M:
  if walls_only and rec['mount']!='wall':continue
  if stems and rec['stem'] not in stems:continue
  reset();obs=import_piece(rec,True,(0,0,1.6 if rec['mount']=='wall' else 0));lo,hi=bounds(obs)
  s=scene((0,0,(hi.z+lo.z)/2),max(1.25,(hi.x-lo.x)*1.35,(hi.z-lo.z)*1.8),640,540)
  if rec['mount']=='wall':
   bpy.ops.mesh.primitive_cube_add(size=1,location=(0,.045,1.6));o=bpy.context.object;o.scale=(1.15,.06,1.05);o.data.materials.append(material('Wall cream','#D1C9B5'))
  s.render.filepath=str(O/'renders'/(rec['stem']+'.png'));bpy.ops.render.render(write_still=True);print('PROOF',rec['stem'],flush=True)

def grid():
 reset();anchors=[]
 for i,rec in enumerate(M):
  x=(i%4-1.5)*3;y=(i//4-.5)*4.3;z=1.6 if rec['mount']=='wall' else 0
  obs=import_piece(rec,True,(x,y,z));lo,hi=bounds(obs)
  if rec['mount']=='wall':
   bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y+.047,1.58));o=bpy.context.object;o.scale=(1.12,.06,1.08);o.data.materials.append(material('Wall swatch','#D1C9B5'))
  anchors.append(dict(stem=rec['stem'],bounds=[list(lo),list(hi)],at=[x,y,z],display_yaw=180 if rec['mount']=='wall' or rec['stem'] in {'MenuBoard','WineRack'} else 0))
 s=scene((0,0,.35),12.8,3200,2000);line=material('Metre line','#B7B4A6')
 for k in range(-10,11):
  for axis in [0,1]:
   bpy.ops.mesh.primitive_cube_add(size=1,location=(k if axis==0 else 0,k if axis==1 else 0,-.008));o=bpy.context.object;o.scale=(.009,21,.003) if axis==0 else (21,.009,.003);o.data.materials.append(line)
 bpy.context.view_layer.update()
 for a in anchors:
  pts=[world_to_camera_view(s,s.camera,Vector((x,y,z))) for x in [a['bounds'][0][0],a['bounds'][1][0]] for y in [a['bounds'][0][1],a['bounds'][1][1]] for z in [a['bounds'][0][2],a['bounds'][1][2]]]
  a['pixel_bounds']=[min(p.x for p in pts)*3200,min(1-p.y for p in pts)*2000,max(p.x for p in pts)*3200,max(1-p.y for p in pts)*2000]
 (O/'grid-layout.json').write_text(json.dumps(anchors,indent=2));s.render.filepath=str(O/'renders/grid.png');bpy.ops.render.render(write_still=True);print('GRID_DONE',flush=True)
if __name__=='__main__':
 mode=sys.argv[-1]
 if mode=='audit':audit()
 elif mode=='grid':grid()
 elif mode=='individual-walls':individual(True)
 elif mode=='wine':individual(stems={'WineRack'})
 else:individual()
