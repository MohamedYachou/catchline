"""JIG-LIGHTS-ART-1: material-only boat edit and metre-scale vertex-alpha FX."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
S=Path(__file__).resolve().parent;O=S.parents[3]/'Art/Models/BoatsV2/JigBoatV1'
def rgba(h):
 c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
 return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c)+(1,)
def material(n,h,glow=False):
 m=bpy.data.materials.get(n) or bpy.data.materials.new(n);m.diffuse_color=rgba(h);m.use_nodes=True
 if not glow:
  bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.8
 else:
  nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');mix=nt.nodes.new('ShaderNodeMixShader');attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='GlowAlpha';tr=nt.nodes.new('ShaderNodeBsdfTransparent');em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=m.diffuse_color;em.inputs['Strength'].default_value=1.8
  nt.links.new(attr.outputs['Alpha'],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
 m.use_backface_culling=False
 return m
def export(p):
 bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.fbx(filepath=str(p),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False,path_mode='AUTO',colors_type='SRGB')
def geom():
 bpy.context.view_layer.update()
 return {o.name:{'parent':o.parent.name if o.parent else None,'matrix':[list(r) for r in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons]} for o in bpy.context.scene.objects if o.type=='MESH'}
base=S/'lights-backup/JigBoatV1.blend'
bpy.ops.wm.open_mainfile(filepath=str(base if base.exists() else O/'JigBoatV1.blend'));before=geom();bulb=material('M_JigBulb','F3DEA1');centres=[];facecounts=[]
for i in range(1,9):
 o=bpy.data.objects['SquidLamp_%02d'%i];old=next(j for j,m in enumerate(o.data.materials) if m.name=='M_BandIvory');new=next((j for j,m in enumerate(o.data.materials) if m==bulb),len(o.data.materials))
 if new==len(o.data.materials):o.data.materials.append(bulb)
 vs=[];count=0
 for p in o.data.polygons:
  if p.material_index in (old,new):
   p.material_index=new;vs.extend(o.matrix_world@o.data.vertices[v].co for v in p.vertices);count+=1
 centre=[(min(v[a] for v in vs)+max(v[a] for v in vs))/2 for a in range(3)];centres.append(centre);facecounts.append(count)
assert geom()==before,'geometry or hierarchy changed'
bpy.context.preferences.filepaths.save_version=0
export(O/'JigBoatV1.fbx');bpy.ops.wm.save_as_mainfile(filepath=str(O/'JigBoatV1.blend'))
(S/'lights-baseline.json').write_text(json.dumps({'geometry_sha256':hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),'lamp_centres_authoring_m':centres,'bulb_faces_per_lamp':facecounts,'geometry_names_parents_matrices_unchanged':True},indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
root=bpy.data.objects.new('JigLampGlow',None);sc.collection.objects.link(root)
glow=material('M_LampGlow','FFE7A3',True);poolmat=material('M_JigWaterLight','CFEFC0',True)
def mesh(n,vs,fs,alphas,m,position):
 me=bpy.data.meshes.new(n);me.from_pydata(vs,[],fs);me.materials.append(m);o=bpy.data.objects.new(n,me);sc.collection.objects.link(o);o.parent=root;o.location=position
 ca=me.color_attributes.new(name='GlowAlpha',type='BYTE_COLOR',domain='POINT')
 for d,a in zip(ca.data,alphas):d.color=(1,1,1,a)
 o['shader_contract']='Unlit additive, tint material RGB, multiply vertex COLOR.a; double-sided, ZWrite Off, ZTest LEqual; no texture/collider/shadow.'
 return o
for i,c in enumerate(centres,1):
 vs=[];fs=[];alphas=[]
 # Two perpendicular vertical quad grids with continuous feather to zero at perimeter.
 for plane in (0,1):
  start=len(vs)
  for j in range(7):
   for k in range(7):
    u=(k-3)*.10;v=(j-3)*.10;vs.append((u,0,v) if plane==0 else (0,u,v));r=math.sqrt(u*u+v*v)/.30;alphas.append(.38*math.exp(-3*r*r)*max(0,1-r*r)**2)
  fs.extend((start+j*7+k,start+j*7+k+1,start+(j+1)*7+k+1,start+(j+1)*7+k) for j in range(6) for k in range(6))
 mesh('LampGlow_%02d'%i,vs,fs,alphas,glow,c)
# Radial rings, exactly6m long Y by3.5m wide X, central fade free of any opaque plane.
vs=[(0,0,0)];alphas=[.22];N=48
for r,a in [(.25,.19),(.50,.12),(.75,.045),(1,0)]:
 for j in range(N):
  t=j*math.tau/N;vs.append((1.75*r*math.cos(t),3*r*math.sin(t),0));alphas.append(a)
fs=[(0,1+j,1+(j+1)%N) for j in range(N)]
for k in range(3):
 a=1+k*N;b=a+N
 fs.extend((a+j,b+j,b+(j+1)%N,a+(j+1)%N) for j in range(N))
mesh('WaterLightPool',vs,fs,alphas,poolmat,(3.20,.96,-.395))
bpy.context.view_layer.update();export(O/'JigLampGlow.fbx');bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(O/'JigLampGlow.blend'))
print('LIGHTS BUILD PASS: unchanged hull + 8 bulb-only material regions, 8 soft crosses and oval pool',flush=True)
