"""Audit actual FBX files, then render isolated game45 day/night fixtures (not Unity)."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import parse_fbx
sys.dont_write_bytecode=True
S=Path(__file__).resolve().parent;O=S.parents[3]/'Art/Models/BoatsV2/JigBoatV1';P=O/'renders/lights';P.mkdir(exist_ok=True,parents=True)
def load(p):
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(p));bpy.context.view_layer.update();return list(bpy.context.scene.objects)
def unit(p):
 root,_=parse_fbx.parse(str(p));s=next(e for e in root.elems if e.id==b'GlobalSettings');props=next(e for e in s.elems if e.id==b'Properties70');return next(e.props[-1] for e in props.elems if e.props[0]==b'UnitScaleFactor')
def snapshot(obs):
 return {o.name:{'vertices':[list(o.matrix_world@v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],'parent':o.parent.name if o.parent else None,'materials':[m.name for m in o.data.materials],'face_materials':[o.data.materials[p.material_index].name for p in o.data.polygons]} for o in obs if o.type=='MESH'}
original=S/'lights-original-mesh.json'
if original.exists():baseline=json.loads(original.read_text())
else:
 baseline=snapshot(load(S/'lights-backup/JigBoatV1.fbx'));original.write_text(json.dumps(baseline))
boat=snapshot(load(O/'JigBoatV1.fbx'));assert baseline.keys()==boat.keys();maxerr=0;bulbcentres=[]
for n,b in baseline.items():
 a=boat[n];assert b['faces']==a['faces'] and b['parent']==a['parent']
 assert len(b['vertices'])==len(a['vertices'])
 maxerr=max(maxerr,max((Vector(v)-Vector(w)).length for v,w in zip(b['vertices'],a['vertices'])))
 expected=['M_JigBulb' if n.startswith('SquidLamp_') and m=='M_BandIvory' else m for m in b['face_materials']];assert expected==a['face_materials'],n
 if n.startswith('SquidLamp_'):
  vs=[Vector(a['vertices'][i]) for f,m in zip(a['faces'],a['face_materials']) if m=='M_JigBulb' for i in f];bulbcentres.append([.5*(min(v[k] for v in vs)+max(v[k] for v in vs)) for k in range(3)])
assert maxerr<1e-6,maxerr
bpy.ops.wm.open_mainfile(filepath=str(O/'JigLampGlow.blend'));source=snapshot(list(bpy.context.scene.objects));obs=load(O/'JigLampGlow.fbx');fx=snapshot(obs);assert source.keys()==fx.keys()
rows=[]
for asset,data in [('JigBoatV1',boat),('JigLampGlow',fx)]:
 assert unit(O/(asset+'.fbx'))==100
 for n,a in data.items():
  vs=a['vertices'];lo=[min(v[i] for v in vs) for i in range(3)];hi=[max(v[i] for v in vs) for i in range(3)]
  assert all(math.isfinite(x) for v in vs for x in v)
  assert -2<lo[0] and hi[0]<5.1 and -4<lo[1] and hi[1]<4.1 and -1<lo[2] and hi[2]<2.2,(n,lo,hi)
  row={'asset':asset,'name':n,'parent':a['parent'],'min_m':lo,'max_m':hi,'triangles':sum(len(f)-2 for f in a['faces']),'materials':a['materials']};rows.append(row)
  if asset=='JigLampGlow':
   assert a['parent']=='JigLampGlow'
   assert max((Vector(v)-Vector(w)).length for v,w in zip(source[n]['vertices'],vs))<1e-5
   o=bpy.data.objects[n];ca=o.data.color_attributes.get('GlowAlpha');assert ca and ca.domain=='CORNER';aa=[d.color[3] for d in ca.data];assert min(aa)==0 and max(aa)>.1;row['vertex_alpha_minmax']=[min(aa),max(aa)]
   assert all(p.area>1e-10 for p in o.data.polygons)
   if n.startswith('LampGlow_'):
    i=int(n[-2:])-1;c=[.5*(lo[k]+hi[k]) for k in range(3)];assert (Vector(c)-Vector(bulbcentres[i])).length<1e-5
   else:assert abs(hi[0]-lo[0]-3.5)<1e-5 and abs(hi[1]-lo[1]-6)<1e-5 and abs(hi[2]-lo[2])<1e-6
assert len(fx)==9 and sum(r['triangles'] for r in rows if r['asset']=='JigBoatV1')==5635
record={'pass':True,'boat_old_new_max_vertex_delta_m':maxerr,'boat_geometry_names_hierarchy_unchanged':True,'only_bulb_surface_materials_changed':True,'units':{'JigBoatV1':100,'JigLampGlow':100},'bulb_centres_m':bulbcentres,'bounds':rows,'native_Unity_tested':False}
(O/'lights-audit.json').write_text(json.dumps(record,indent=2));print('LIGHTS AUDIT PASS',maxerr,len(rows),flush=True)
if '--audit-only' in sys.argv:sys.exit(0)
def colour(h):
 c=[int(h[i:i+2],16)/255 for i in (0,2,4)];return tuple(x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in c)+(1,)
def tint(m,h):
 m.diffuse_color=colour(h);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=m.diffuse_color;bs.inputs['Roughness'].default_value=.42
# Authoring .blend used only to restore explicit vertex-alpha shader, actual FBX geometry remains rendered.
def fxshader(m,h):
 m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');mix=nt.nodes.new('ShaderNodeMixShader');attr=nt.nodes.new('ShaderNodeVertexColor');attr.layer_name='GlowAlpha';tr=nt.nodes.new('ShaderNodeBsdfTransparent');em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=colour(h);em.inputs['Strength'].default_value=2
 nt.links.new(attr.outputs['Alpha'],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(em.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs[0])
for night in [False,True]:
 objs=load(O/'JigBoatV1.fbx');sc=bpy.context.scene
 bpy.ops.import_scene.fbx(filepath=str(O/'JigLampGlow.fbx'));bpy.context.view_layer.update();fxobs=[o for o in sc.objects if o.type=='MESH' and (o.name.startswith('LampGlow_') or o.name=='WaterLightPool')]
 for o in fxobs:o.hide_render=not night
 fxshader(bpy.data.materials['M_LampGlow'],'FFE7A3');fxshader(bpy.data.materials['M_JigWaterLight'],'CFEFC0')
 bulb=bpy.data.materials['M_JigBulb'];bs=bulb.node_tree.nodes.get('Principled BSDF');bs.inputs['Emission Color'].default_value=colour('FFE7A3');bs.inputs['Emission Strength'].default_value=3 if night else 0
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.40));sea=bpy.context.object;sea.name='REVIEW_ONLY_SEA';m=bpy.data.materials.new('REVIEW_ONLY_WATER');tint(m,'123643' if night else '287E93');sea.data.materials.append(m)
 # Calm broad small-amplitude shading; no foam, glitter or large displacement.
 nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=1.6;tex.inputs['Detail'].default_value=1;bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.025;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
 world=bpy.data.worlds.new('Review dusk' if night else 'Review day');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.32,.50,1) if night else (.65,.74,.80,1);world.node_tree.nodes['Background'].inputs[1].default_value=.38 if night else .6;sc.world=world
 for label,pos,power,size,col in [('Key',(-4,-5,8),150 if night else 1050,7,(.57,.70,1) if night else (1,.90,.77)),('Rim',(0,5,6),100 if night else 650,5,(.65,.75,1))]:
  d=bpy.data.lights.new(label,'AREA');d.energy=power;d.size=size;d.color=col;o=bpy.data.objects.new('REVIEW_ONLY_'+label,d);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
 if night:
  for i,c in enumerate(bulbcentres):
   d=bpy.data.lights.new('REVIEW_ONLY_lamp_%02d'%i,'POINT');d.energy=12;d.color=(1,.78,.39);d.shadow_soft_size=.18;o=bpy.data.objects.new(d.name,d);sc.collection.objects.link(o);o.location=c
 cam=bpy.data.objects.new('REVIEW_ONLY_camera',bpy.data.cameras.new('Camera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.sensor_fit='HORIZONTAL';target=Vector((.85,.05,.2));d=Vector((-math.cos(math.radians(35)),-math.sin(math.radians(35)),1)).normalized();cam.location=target+d*30;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=13.7
 sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True;sc.render.threads_mode='FIXED';sc.render.threads=6;sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.25;sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
 for w,h in [(1440,900),(844,390)]:
  sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.filepath=str(P/('%s-%dx%d.png'%('night' if night else 'day',w,h)));bpy.ops.render.render(write_still=True);print('LIGHTS RENDER PASS',sc.render.filepath,flush=True)
print('LIGHTS REVIEW COMPLETE',flush=True)
