"""Additive stage-two kit derived from accepted V4. Never writes upstream."""
import bpy,bmesh,json,math,hashlib,shutil,sys,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;V=O.parent/'Stage1V4';R=O.parents[3];sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('geom',str(R/'Art/Source/build_crab_coast_props.py'));H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
bpy.ops.wm.open_mainfile(filepath=str(V/'Stage1V4.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
T=O/'textures';T.mkdir(exist_ok=True)
for n in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']:shutil.copyfile(V/'textures'/n,T/n)
cells={c['name']:c for c in json.loads((T/'atlas.json').read_text())['cells']}
sourcehash=hashlib.sha256((V/'Stage1V4.blend').read_bytes()).hexdigest()
def sx(x):return x if x<=-1 else -1+(x+1)*1.4
# Preserve accepted station shapes; widen only shell and evenly distribute dining furnishings.
for o in list(sc.objects):
 if o.type=='MESH' and (o.name.startswith(('TerraceFoundation','TerracePaving')) or o.name in ['TerraceTable','TerraceParasol','Candle_4','PlaceSetting_4','Glass_4','V4_Plate_4_0','V4_Glass_4_0','ExtraPlant0','ExtraPlant1','V4_WallPlant_7','V4_WallPlant_8']):bpy.data.objects.remove(o,do_unlink=True)
for o in sc.objects:
 if o.type=='MESH' and not o.name.startswith('REVIEW_'):
  o.data=o.data.copy()
  if o.name=='RoomShell':
   # Remove the former narrow jetty and disconnected front quay components, replaced by an extended terrace.
   bm=bmesh.new();bm.from_mesh(o.data);pending=set(bm.verts);remove=[]
   while pending:
    seed=pending.pop();component={seed};stack=[seed]
    while stack:
     for e in stack.pop().link_edges:
      for v in e.verts:
       if v in pending:pending.remove(v);component.add(v);stack.append(v)
    if max(v.co.y for v in component)<-2.66:remove.extend(component)
   bmesh.ops.delete(bm,geom=remove,context='VERTS');bm.to_mesh(o.data);bm.free()
   for v in o.data.vertices:v.co.x=sx(v.co.x)
  elif o.name.startswith(('RearMasonry','RearCoping','V4_RearMortar')):
   mw=o.matrix_world.copy();mi=mw.inverted()
   for v in o.data.vertices:
    p=mw@v.co;p.x=sx(p.x);v.co=mi@p
  else:o.location.x=sx(o.location.x)
 elif o.type=='LIGHT':o.location.x=sx(o.location.x)
# Whitewash the wall pigment only, leaving dark coping and navy shutters intact.
def recolour(ob,mapping):
 uv=ob.data.uv_layers.get('UV0') or ob.data.uv_layers[0]
 for p in ob.data.polygons:
  avg=sum((uv.data[i].uv for i in p.loop_indices),Vector((0,0)))/len(p.loop_indices);idx=min(3,max(0,int((1-avg.y)*4)))*8+min(7,max(0,int(avg.x*8)));old=next(c for c in cells.values() if c['index']==idx)
  if old['name'] not in mapping:continue
  dst=cells[mapping[old['name']]];ax,ay,aw,ah=old['pixel_cell'];bx,by,bw,bh=dst['pixel_cell']
  for i in p.loop_indices:
   u=uv.data[i].uv;u.x=(bx+(u.x*2048-ax)/aw*bw)/2048;u.y=1-(by+((1-u.y)*2048-ay)/ah*bh)/2048
for o in sc.objects:
 if o.type=='MESH' and not o.name.startswith('REVIEW_'):
  if o.name=='RoomShell':recolour(o,{'plaster':'ivory','stonecream':'ivory','stonecool':'ivory'})
  if o.name.startswith('RearMasonry'):recolour(o,{'stonecool':'plaster'})
# A single atlas shader for new structural pieces, with the identical V4 Surface packing.
mat=bpy.data.materials.new('Restaurant_Atlas_Bistro');mat.use_nodes=True;ns=mat.node_tree.nodes;lk=mat.node_tree.links;bs=ns.get('Principled BSDF');im=ns.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(T/'Restaurant_BaseColor.png'));im.image.pack();lk.new(im.outputs['Color'],bs.inputs['Base Color']);sf=ns.new('ShaderNodeTexImage');sf.image=bpy.data.images.load(str(T/'Restaurant_Surface.png'));sf.image.colorspace_settings.name='Non-Color';sf.image.pack();sep=ns.new('ShaderNodeSeparateColor');lk.new(sf.outputs['Color'],sep.inputs[0]);lk.new(sep.outputs['Red'],bs.inputs['Roughness']);lk.new(sep.outputs['Green'],bs.inputs['Metallic']);lk.new(im.outputs['Color'],bs.inputs['Emission Color']);mul=ns.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=2.5;lk.new(sep.outputs['Blue'],mul.inputs[0]);lk.new(mul.outputs[0],bs.inputs['Emission Strength'])
new=[]
def obj(name,g,bevel=0):
 me=bpy.data.meshes.new(name);me.from_pydata(g.vertices,[],g.faces);me.update();ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob);me.materials.append(mat);uv=me.uv_layers.new(name='UV0')
 for p,col in zip(me.polygons,g.colours):
  cell=cells[col];x,y,w,h=cell['pixel_cell'];axis=max(range(3),key=lambda k:abs(p.normal[k]));ax=[k for k in range(3) if k!=axis];points=[me.vertices[me.loops[i].vertex_index].co for i in p.loop_indices];lo=[min(v[k] for v in points) for k in ax];hi=[max(v[k] for v in points) for k in ax]
  for i,v in zip(p.loop_indices,points):
   a=[(v[k]-l)/max(r-l,1e-8) for k,l,r in zip(ax,lo,hi)];uv.data[i].uv=((x+24+a[0]*(w-48))/2048,1-(y+24+a[1]*(h-48))/2048)
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 if bevel:
  mod=ob.modifiers.new('SoftEdges','BEVEL');mod.width=bevel;mod.segments=1;bpy.ops.object.modifier_apply(modifier=mod.name)
  # Remap any bevel bridges to an inset point in their nearest source cell.
  uv=me.uv_layers[0]
  for p in me.polygons:
   ids={int(uv.data[i].uv.x*8)+8*int(uv.data[i].uv.y*4) for i in p.loop_indices}
   if len(ids)>1:
    av=sum((uv.data[i].uv for i in p.loop_indices),Vector((0,0)))/len(p.loop_indices);cx=min(7,int(av.x*8));cy=min(3,int(av.y*4))
    for i in p.loop_indices:uv.data[i].uv=((cx+.5)/8,(cy+.5)/4)
 me.uv_layers.new(name='LightmapUV');me.uv_layers.active_index=1;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT');me.uv_layers.active_index=0
 ao=me.color_attributes.new(name='LocalAO',type='BYTE_COLOR',domain='CORNER')
 for d in ao.data:d.color=(.9,.9,.9,1)
 new.append(ob);return ob

def box(g,c,d,col):g.box(c,d,col)
def tube(g,a,b,r,col,n=8):g.tube([a,b],[r,r],n,col)
# Full-width water terrace, supported by piles: walkable top matches V4 quay z=-.03m.
g=H.Geometry();box(g,(1,-3.78,-.23),(10.7,2.5,.36),'wooddark')
for j in range(9):
 y=-2.62-j*.277;box(g,(1,y,-.055),(10.66,.26,.05),'wood' if j%3 else 'woodlight')
for x in [-4.24,-1.65,1,3.65,6.24]:
 for y in [-2.65,-4.91]:tube(g,(x,y,-1.1),(x,y,-.08),.11,'wooddark',10)
box(g,(1,-4.99,-.12),(10.85,.12,.24),'navy');obj('BistroTerraceDeck',g,.007)
# Navy rail only along outer edge, entry gap at right and fine rope rather than solid visual barrier.
g=H.Geometry()
for x in [-4.3,-2.65,-1,.65,2.3,3.95,6.3]:
 tube(g,(x,-4.99,-.04),(x,-4.99,.69),.038,'navy');g.ellipsoid((x,-4.99,.72),(.058,.058,.045),10,4,'brass')
for a,b in zip([-4.3,-2.65,-1,.65,2.3],[-2.65,-1,.65,2.3,3.95]):
 for z in [.27,.55]:g.tube([(a,-4.99,z),((a+b)/2,-5.0,z-.055),(b,-4.99,z)],[.013]*3,6,'rope')
obj('BistroTerraceRail',g)
# More generous right-hand entry, without a presentation floor.
g=H.Geometry();box(g,(5.16,-5.7,-.23),(1.85,1.4,.36),'wooddark')
for i in range(7):box(g,(5.16,-5.1-i*.20,-.055),(1.83,.185,.05),'wood')
for x in [4.3,6.03]:tube(g,(x,-6.25,-1.1),(x,-6.25,.65),.05,'navy')
obj('BistroEntryJetty',g,.006)
# Raised whitewashed dining facade physically anchors the awning; kitchen stays cutaway.
g=H.Geometry();box(g,(2.91,2.68,1.995),(6.22,.20,.61),'ivory');box(g,(2.91,2.68,2.32),(6.30,.24,.07),'navy');obj('BistroAwningFacade',g,.012)
# Blue/ivory awning projects toward the game camera from the raised facade.
g=H.Geometry();segments=24;x0=-.15;w=6.12
for i in range(segments):
 x=x0+(i+.5)*w/segments;col='blue' if i%2==0 else 'ivory';x1=x-w/segments/2;x2=x+w/segments/2
 g.add([(x1,2.58,2.30),(x2,2.58,2.30),(x2,1.79,2.03),(x1,1.79,2.03),(x1,2.58,2.275),(x2,2.58,2.275),(x2,1.79,2.005),(x1,1.79,2.005)],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)],col)
 # scalloped hanging valance facing camera, narrow so the blue remains the dominant shape.
 box(g,(x,1.79,1.965),(w/segments-.004,.035,.12),col);g.ellipsoid((x,1.79,1.91),(w/segments*.49,.024,.07),8,3,col)
for x in [x0,x0+w]:tube(g,(x,2.58,1.1),(x,1.79,2.02),.024,'navy')
obj('BistroBlueAwning',g)
# Terrace strings placed at the far edge, rising above front wall rather than concealing diners.
g=H.Geometry();points=[]
for i in range(31):
 x=-4.3+i*10.6/30;z=2.15-.30*math.sin(math.pi*i/30);points.append((x,-2.85,z))
g.tube(points,[.013]*len(points),6,'dark')
for i in range(21):
 x=-4.3+(i+.5)*10.6/21;z=2.15-.30*math.sin(math.pi*(i+.5)/21);tube(g,(x,-2.85,z),(x,-2.85,z-.09),.012,'brass');g.ellipsoid((x,-2.85,z-.125),(.041,.041,.060),10,4,'glow')
for x in [-4.3,6.3]:tube(g,(x,-2.85,-.03),(x,-2.85,2.23),.035,'navy')
obj('BistroStringLights',g)
# Reuse accepted tier-two tables/chairs with a placeable component per table.
with bpy.data.libraries.load(str(O.parent/'Upgrades/RestaurantUpgrades.blend'),link=False) as (a,b):b.objects=['Dining4_Tier2','Dining2_Tier2','PlantPotLeafy','PlantPotFlowers'] if 'PlantPotLeafy' in a.objects else ['Dining4_Tier2','Dining2_Tier2']
loaded={o.name:o for o in b.objects if o}
# Explicit source names for plant props vary; use existing V4 flowers copied below.
tables=[]
for i,x in enumerate([-2.65,.20,3.05]):
 src=loaded['Dining4_Tier2' if i!=1 else 'Dining2_Tier2'];o=src.copy();o.data=src.data.copy();o.name=f'BistroTerraceTable_{i+1}';sc.collection.objects.link(o);o.location=(x,-3.75,-.03);tables.append({'name':o.name,'seats':4 if i!=1 else 2,'position_blender_m':list(o.location),'tabletop_z_m':.706})
for i,(src,loc) in enumerate([('PlantPot1',(-4.04,-4.55,-.03)),('PlantPot2',(-1.2,-4.58,-.03)),('PlantPot3',(1.63,-4.58,-.03)),('PlantPot1',(4.2,-4.50,-.03)),('PlantPot2',(6.0,-2.8,-.03))]):
 o=bpy.data.objects[src].copy();o.data=o.data.copy();o.name=f'BistroTerracePlant_{i}';sc.collection.objects.link(o);o.location=loc
# Existing source terrace props that now conflict are kept as movable quay cargo but moved out of seats/entry.
for n,loc in {'JettyLamp':(6.18,-4.6,-.03),'JettyBarrel':(6.18,-1.8,-.03),'JettyCrate':(6.18,-1.3,-.03),'V4_QuayCargo0':(-4.45,-1.5,-.03),'V4_QuayCargo1':(-4.42,-1.5,.43),'V4_QuayCargo2':(-4.45,-.9,-.03)}.items():
 if n in bpy.data.objects:bpy.data.objects[n].location=loc
# Move former cargo rope coils onto their barrel.
for i in range(3):bpy.data.objects[f'V4_RopeCoil{i}'].location=(-4.45,-.9,.91+i*.025)
# All accepted source/material images packed, then relative paths repaired for local atlas binding.
for im in bpy.data.images:
 if im.source=='FILE':
  try:im.filepath=bpy.path.abspath(im.filepath);im.pack()
  except Exception:pass
# Add terrace point-light recipe; retain V4 night grading/world/fixture powers.
recipe=json.loads((V/'lighting.json').read_text())
for row in recipe['lights']:
 row['position_blender_m'][0]=sx(row['position_blender_m'][0]);x,y,z=row['position_blender_m'];row['position_unity_m']=[x,z,-y]
for i,x in enumerate([-3.6,-1.5,.6,2.7,4.8]):
 d=bpy.data.lights.new('BistroStringWarm'+str(i),'POINT');d.energy=13;d.color=(1,.603827,.204902);d.shadow_soft_size=.20;o=bpy.data.objects.new(d.name,d);sc.collection.objects.link(o);o.location=(x,-2.9,1.8);recipe['lights'].append({'name':o.name,'type':'POINT','position_blender_m':list(o.location),'position_unity_m':[x,1.8,2.9],'blender_power':13,'linear_rgb':list(d.color),'range_recipe_m':3,'radius_m':.2})
for i,row in enumerate(tables):
 x,y,z=row['position_blender_m'];d=bpy.data.lights.new('BistroTableCandle'+str(i),'POINT');d.energy=8.05;d.color=(1,.603827,.204902);d.shadow_soft_size=.10;o=bpy.data.objects.new(d.name,d);sc.collection.objects.link(o);o.location=(x,y,.85);recipe['lights'].append({'name':o.name,'type':'POINT','position_blender_m':list(o.location),'position_unity_m':[x,.85,-y],'blender_power':8.05,'linear_rgb':list(d.color),'range_recipe_m':2,'radius_m':.1})
# Old terrace source candle light moved to first new table; remove duplicate in scene and recipe.
if 'TableCandle4' in bpy.data.objects:bpy.data.objects.remove(bpy.data.objects['TableCandle4'],do_unlink=True)
recipe['lights']=[r for r in recipe['lights'] if r['name']!='TableCandle4'];recipe['source_recipe']='Stage1V4/lighting.json';recipe['stage2_additions']='5 string practicals, 3 table candles';(O/'lighting.json').write_text(json.dumps(recipe,indent=2))
prod=[o for o in sc.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')]
# Appended table meshes receive explicit non-overlapping per-triangle lightmap charts.
for o in prod:
 if len(o.data.uv_layers)<2:
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();me=o.data;uv=me.uv_layers.new(name='LightmapUV');grid=math.ceil(math.sqrt(len(me.polygons)));pad=.12
  for j,p in enumerate(me.polygons):
   x=j%grid;y=j//grid
   for li,(u,v) in zip(p.loop_indices,[(pad,pad),(1-pad,pad),(pad,1-pad)]):uv.data[li].uv=((x+u)/grid,(y+v)/grid)
  me.uv_layers.active_index=0
sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
bpy.context.view_layer.update()
rows=[]
for o in prod:
 o.data.calc_loop_triangles();p=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'triangles':len(o.data.loop_triangles),'world_min_m':[min(v[k] for v in p) for k in range(3)],'world_max_m':[max(v[k] for v in p) for k in range(3)],'linked_V2':o.get('kit_source',''),'export_name':'EXPORT_'+o.name})
metrics={'source_V4_sha256':sourcehash,'room_triangles':sum(r['triangles'] for r in rows),'production_meshes':rows,'unit_scale_m':1,'layout_tile_m':1,'camera_note':'same V4 perspective orientation and lenses, reframed around expanded stage'};(O/'build-metrics.json').write_text(json.dumps(metrics,indent=2))
(O/'layout.json').write_text(json.dumps({'stage':2,'name':'Bistro','room_tiles':[10,5],'tile_m':1,'room_bounds_blender_m':[[-4,-2.5,0],[6,2.5,0]],'kitchen_tiles':[3,5],'floor_surface_z_m':.04,'terrace_surface_z_m':-.03,'terrace_bounds_blender_m':[[-4.35,-5.03,-.03],[6.35,-2.53,-.03]],'waterline_z_m':-.55,'origin':'V4 retained; dining extends positive X','convert_blender_to_unity':'[x,z,-y]','runtime_layout_convention':'EXPORT_<component>; hide original layout component when replacing it, same as Stage1V4','terrace_tables':tables,'entry_centre_blender_m':[5.16,-5.7,-.03]},indent=2))
# Export copies named exactly like V4; do not ship water/camera/lights with the kit.
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in prod:
 q=o.copy();q.data=o.data.copy();q.name='EXPORT_'+o.name;sc.collection.objects.link(q);q.select_set(True);copies.append(q)
bpy.context.view_layer.objects.active=copies[0]
bpy.ops.export_scene.fbx(filepath=str(O/'Stage2Bistro.fbx'),use_selection=True,object_types={'MESH'},apply_unit_scale=True,global_scale=1,axis_forward='-Z',axis_up='Y',use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True)
for q in copies:bpy.data.objects.remove(q,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Stage2Bistro.blend'));print('BISTRO BUILD PASS',len(prod),metrics['room_triangles'],flush=True)
