"""Fresh FBX checks and isolated game-camera proofs; no Unity/runtime claim."""
import sys
sys.dont_write_bytecode=True
import bpy,json,math,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('decor_review',O.parent/'decor/review.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v);v.O=O
M=json.loads((O/'manifest.json').read_text())['items'];(O/'renders').mkdir(exist_ok=True)
def audit():
 rows=[]
 for r in M:
  v.reset();obs=v.import_piece(r);lo,hi=v.bounds(obs);err=max(abs(c[i]-r['bounds_blender'][j][i]) for j,c in enumerate([lo,hi]) for i in range(3))
  g=[o for o in obs if o.name==r['glow_mesh']];body=[o for o in obs if o.name==r['name']];images=[];bad=[]
  for o in body:
   for m in o.data.materials:
    ims=[n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] if m and m.use_nodes else []
    if not ims:bad.append(m.name if m else 'None')
    for im in ims:images.append(dict(name=im.name,size=list(im.size),path=im.filepath))
  gm=list(g[0].data.materials) if len(g)==1 else [];bs=gm[0].node_tree.nodes.get('Principled BSDF') if len(gm)==1 else None
  rgba=list(bs.inputs['Base Color'].default_value) if bs else []
  pivot=(abs(lo.y)<1e-5 and abs(lo.z+hi.z)<1e-5) if r['mount']=='wall' else (abs(hi.z)<1e-5 and abs(lo.y+hi.y)<1e-5) if r['mount']=='ceiling' else (abs(lo.z)<1e-5 and abs(lo.y+hi.y)<1e-5)
  checks=dict(exact_two_meshes=len(obs)==2,exact_mesh_names=len(g)==len(body)==1,glow_one_own_material=len(gm)==1 and gm[0].name==r['glow_material'] and all(gm[0] not in list(o.data.materials) for o in body),bright_opaque_glow=bool(rgba) and rgba[0]>.95 and rgba[1]>.65 and rgba[2]>.30 and rgba[3]==1,glow_no_emission_authored=bool(bs) and bs.inputs['Emission Strength'].default_value==0,body_atlas_only=not bad and bool(images),decoded_images=all(im['size'][0]>0 and im['size'][1]>0 for im in images),bounds_match=err<1e-5,pivot=pivot,centred_x=abs(lo.x+hi.x)<1e-5,finite=all(math.isfinite(c) for ob in obs for vert in ob.data.vertices for c in vert.co),valid_uv=all(ob.data.uv_layers.active and all(math.isfinite(c) and 0<=c<=1 for x in ob.data.uv_layers.active.data for c in x.uv) for ob in obs),triangles_match=sum(len(p.vertices)-2 for ob in obs for p in ob.data.polygons)==r['triangles'],only_mesh_objects=all(ob.type=='MESH' for ob in bpy.context.scene.objects),fbx_hash=hashlib.sha256((O/(r['name']+'.fbx')).read_bytes()).hexdigest()==r['fbx_sha256'])
  rows.append(dict(name=r['name'],checks=checks,bounds=[list(lo),list(hi)],error_m=err,glow_linear_rgba=rgba,images=images))
 (O/'mesh-audit.json').write_text(json.dumps(dict(pass_all=all(all(x['checks'].values()) for x in rows),items=rows),indent=2));print('FRESH_AUDIT',len(rows),all(all(x['checks'].values()) for x in rows),flush=True)
def height(r):return r['mount_height_m']
def support(r,x=0,y=0):
 if r['mount']=='wall':
  bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y+.055,1.6));o=bpy.context.object;o.scale=(3.10 if r['stem']=='StringLightsLong' else .8,.065,.85);o.data.materials.append(v.material('Navy proof wall','#26495B'))
 elif r['mount']=='floor/table':
  bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,.36));o=bpy.context.object;o.scale=(.70,.70,.72);o.data.materials.append(v.material('Proof table','#96764E'))
def individual():
 for r in M:
  v.reset();obs=v.import_piece(r,True,(0,0,height(r)));lo,hi=v.bounds(obs);support(r)
  s=v.scene((0,0,(lo.z+hi.z)/2),max(1.3,(hi.x-lo.x)*1.27,(hi.z-lo.z)*1.8),800,650)
  s.render.filepath=str(O/'renders'/(r['stem']+'.png'));bpy.ops.render.render(write_still=True);print('PROOF',r['stem'],flush=True)
def grid():
 v.reset();anchors=[]
 for i,r in enumerate(M):
  x=(i%3-1)*3.6;y=(i//3-.5)*3.7
  obs=v.import_piece(r,True,(x,y,height(r)));lo,hi=v.bounds(obs);support(r,x,y)
  anchors.append(dict(stem=r['stem'],bounds=[list(lo),list(hi)],display_position=[x,y,height(r)],display_yaw=180 if r['mount']=='wall' else 0))
 s=v.scene((0,0,1.2),11.6,2400,1600);line=v.material('Metre line','#B1ADA0')
 for k in range(-9,10):
  for axis in [0,1]:
   bpy.ops.mesh.primitive_cube_add(size=1,location=(k if axis==0 else 0,k if axis==1 else 0,-.008));ob=bpy.context.object;ob.scale=(.012,20,.004) if axis==0 else (20,.012,.004);ob.data.materials.append(line)
 bpy.context.view_layer.update()
 for a in anchors:
  pts=[v.world_to_camera_view(s,s.camera,Vector((x,y,z))) for x in [a['bounds'][0][0],a['bounds'][1][0]] for y in [a['bounds'][0][1],a['bounds'][1][1]] for z in [a['bounds'][0][2],a['bounds'][1][2]]]
  a['pixel_bounds']=[min(p.x for p in pts)*2400,min(1-p.y for p in pts)*1600,max(p.x for p in pts)*2400,max(1-p.y for p in pts)*1600]
 (O/'grid-layout.json').write_text(json.dumps(anchors,indent=2));s.render.filepath=str(O/'renders/grid.png');bpy.ops.render.render(write_still=True);print('GRID_DONE',flush=True)
if __name__=='__main__':
 {'audit':audit,'individual':individual,'grid':grid}[sys.argv[-1]]()
