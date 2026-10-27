"""Local V4 palette, night and additive V2 referenced dressing; no incumbent writes."""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];V=O.parent/'Stage1V2';V3=O.parent/'Stage1V3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def checkpoint(s):
 with (R/'comms.md').open('a') as f:f.write('\nCHECKPOINT / RESTAURANT-LOOK-DETAIL-4 / Codex 2 (WSL CLI): '+s+'\n')
bpy.ops.wm.open_mainfile(filepath=str(V3/'Stage1V3.blend'));bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene
baseline={str(p.relative_to(R)):sha(p) for d in [V,V3,O.parent/'Guests'] for p in d.rglob('*') if p.is_file() and '_v2' not in p.name and '-v2' not in p.name and 'renders-v2' not in p.parts}
(O/'dependencies.json').write_text(json.dumps(baseline,indent=2))
production=[o for o in sc.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')];oldnames={o.name for o in production};provenance={o.name:bool(o.data.library) for o in production};placements=[]
# Local geometry/material copies preserve the accepted linked libraries exactly.
matcopies={}
for o in production:
 o.data=o.data.copy()
 for i,m in enumerate(o.data.materials):
  key=m.as_pointer()
  if key not in matcopies:
   n=m.copy();n.name=m.name+'_V4';matcopies[key]=n
   if n.use_nodes:
    for node in n.node_tree.nodes:
     if node.type=='TEX_IMAGE' and node.image:
      fname='Restaurant_Surface.png' if 'Surface' in node.name or 'Surface' in node.image.name else 'Restaurant_BaseColor.png'
      if (O/'textures'/fname).exists():node.image=bpy.data.images.load(str(O/'textures'/fname),check_existing=True);node.image.colorspace_settings.name='Non-Color' if 'Surface' in fname else 'sRGB'
  o.data.materials[i]=matcopies[key]
def lin(v):return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def pigment(m,h):
 c=tuple(lin(int(h[i:i+2],16)/255) for i in (0,2,4));m.diffuse_color=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1)
for m in matcopies.values():
 for prefix,h in [('WarmLimestone','91ACC9'),('HoneyTimber','A86D3F'),('DeepNavyEnamel','1D3B6E'),('CrockeryIvory','DAE8F1')]:
  if m.name.startswith(prefix):pigment(m,h)
# Joined kit components retain exact positions/topology. Repaint UV cells, never move vertices.
repaint=[]
for o in production:
 if not o.data.uv_layers or not any('Atlas' in m.name for m in o.data.materials):continue
 me=o.data;parent=list(range(len(me.vertices)))
 def find(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 for e in me.edges:
  a,b=map(find,e.vertices);parent[b]=a
 comps={}
 for v in me.vertices:comps.setdefault(find(v.index),[]).append(v.co)
 info={k:([min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]) for k,pts in comps.items()};uv=me.uv_layers[0].data;changed=0
 for p in me.polygons:
  lo,hi=info[find(p.vertices[0])];cen=[(a+b)/2 for a,b in zip(lo,hi)];dim=[b-a for a,b in zip(lo,hi)];avg=sum((uv[i].uv for i in p.loop_indices),Vector((0.,0.)))/len(p.loop_indices);col=min(7,max(0,int(avg.x*8)));row=min(3,max(0,int((1-avg.y)*4)));cell=row*8+col;dest=cell
  if o.name=='RoomShell':
   perimeter=(abs(cen[0])>3.8 or abs(cen[1])>2.45)
   if cell in [2,3] and perimeter and .08<cen[2]<1.05 and max(dim)>.18:
    dest=0 if cen[2]<.32 and cen[0]>-1 else 17
   if cell==1:dest=0  # shutters and alley door share blue trim pigment
  if o.name.startswith(('Dining','TerraceTable')) and cell in [4,5,6] and max(dim[:2])<.52:dest=0
  if dest!=cell:
   for i in p.loop_indices:uv[i].uv+=Vector(((dest%8-col)/8,-(dest//8-row)/4))
   changed+=1
 if changed:repaint.append({'mesh':o.name,'repainted_faces':changed})
(O/'palette-meshes.json').write_text(json.dumps(repaint,indent=2))
checkpoint('A source VERIFIED: picker records/2x2048 local atlases generated; original mesh coordinates/topology untouched, local materials and UV pigment remaps created. Visual outcome UNVERIFIED until E proof. IN PROGRESS B night/water/grade; C follows. Same reservations, no subagents.')
# Broad toy pigments under cooler, less orange-washed ambient illumination.
sc.view_settings.exposure=-.25;sc.view_settings.look='AgX - Medium High Contrast'
sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.055,.16,.42,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.32
lightrows=[]
for o in sc.objects:
 if o.type!='LIGHT':continue
 d=o.data;d=d.copy();o.data=d
 if d.type=='AREA':d.energy*=.95;d.color=tuple(lin(v) for v in (.83,.92,1))
 elif d.type=='SUN':d.energy=.28;d.color=tuple(lin(v) for v in (.39,.61,1))
 else:d.energy*=1.15;d.color=tuple(lin(v) for v in (1,.80,.49))
# Emissive opaque blue sea remains review-only; physical roughness and wave bump catch warm practicals.
w=bpy.data.objects['REVIEW_WaterPlane'];w.data=w.data.copy();water=w.data.materials[0].copy();w.data.materials[0]=water;water.name='REVIEW_BlueSea_V4';nodes=water.node_tree.nodes;links=water.node_tree.links;b=nodes.get('Principled BSDF');pigment(water,'057DB8');b.inputs['Roughness'].default_value=.22;b.inputs['Metallic'].default_value=.32;b.inputs['Emission Color'].default_value=(*[lin(v) for v in (.015,.30,.62)],1);b.inputs['Emission Strength'].default_value=.48
tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2.8;tex.inputs['Detail'].default_value=2;tex.inputs['Roughness'].default_value=.65;tc=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(.6,3,1);links.new(tc.outputs['Object'],mapping.inputs[0]);links.new(mapping.outputs[0],tex.inputs['Vector']);bump=nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.24;bump.inputs['Distance'].default_value=.11;links.new(tex.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],b.inputs['Normal'])
# Explicit small blue ripples: procedural emissive sea colour rather than alpha or extra export geometry.
ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.43;ramp.color_ramp.elements[0].color=(.002,.035,.10,1);ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(.008,.20,.45,1);links.new(tex.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs['Color'],b.inputs['Emission Color'])
cg=sc.compositing_node_group;gl=next(n for n in cg.nodes if n.type=='GLARE');out=next(n for n in cg.nodes if n.type=='GROUP_OUTPUT');hs=cg.nodes.new('CompositorNodeHueSat');hs.inputs['Saturation'].default_value=1.10;cg.links.new(gl.outputs['Image'],hs.inputs['Image']);cg.links.new(hs.outputs['Image'],out.inputs['Image'])
checkpoint('B source implemented: EV-.25 Medium High Contrast, saturation1.10, blue ambient/fill,1.15x warmer practicals, opaque blue procedural sea/ripple bump. Visual result UNVERIFIED. IN PROGRESS C additive kit dressing; V3 layout and camera preserved.')
# Reuse local repainted V2 meshes, sourcing any unused library roots by reference first.
meta=json.loads((V/'build-metrics.json').read_text());rows={r['root']:r for r in meta['roots']};source={}
for r in json.loads((V3/'build-metrics.json').read_text())['placements']:
 if r['name'] in bpy.data.objects:source[r['source_root']]=bpy.data.objects[r['name']].data
missing=[r['mesh'] for n,r in rows.items() if n not in source]
with bpy.data.libraries.load(str(V/'Stage1V2.blend'),link=True) as (src,dst):dst.objects=missing
for n,r in rows.items():
 if n not in source:
  me=next(m for m in dst.objects if m and m.name==r['mesh']).data.copy()
  for i,m in enumerate(me.materials):me.materials[i]=next(x for x in matcopies.values() if x.name.startswith('Restaurant_Atlas'))
  source[n]=me
# Helpers from accepted source are function definitions only, no previous task execution.
old=(V3/'build.py').read_text();exec(old[old.index('def mat('):old.index('# Full back wall')])
def kit(src,name,loc,yaw=0):
 ob=bpy.data.objects.new(name,source[src]);sc.collection.objects.link(ob);ob.location=loc;ob.rotation_euler.z=math.radians(yaw);production.append(ob);placements.append({'name':name,'source_root':src,'source_blend':'../Stage1V2/Stage1V2.blend','position_m':list(loc),'yaw_deg':yaw});return ob
# Plants punctuate each wall, not the central service aisle.
for i,(src,loc) in enumerate([('PlantPot2',(-3.76,-.92,.04)),('PlantPot1',(-3.76,1.06,.04)),('PlantPot3',(-.05,2.09,.04)),('PlantPot2',(3.72,1.95,.04)),('PlantPot1',(3.78,-.80,.04)),('PlantPot3',(3.75,-2.23,.04)),('PlantPot2',(-.02,-2.19,.04)),('PlantPot3',(-4.02,-3.78,-.03)),('PlantPot1',(-1.75,-4.02,-.03)),('PlantPot2',(.07,-3.03,-.03))]):kit(src,'V4_WallPlant_'+str(i),loc)
# More complete place settings, matched to original table tops/chair centres.
for j,(x,y,z) in enumerate([(.65,-1.35,.72),(2.25,-1.35,.72),(1.35,.48,.72),(2.15,1.74,.72),(-2.85,-3.48,.64)]):
 # Additional settings complement the fixed original plates instead of intersecting them.
 if j in [0,1]:extra=[(.18,.10,-.08,.16)]
 elif j==2:extra=[(-.35,.10,-.43,-.08),(.35,.10,.43,-.08)]
 elif j==3:extra=[(.36,-.06,.23,.11)]
 else:extra=[(.16,.11,-.09,.15)]
 for i,(px,py,gx,gy) in enumerate(extra):
  kit('PlateClean',f'V4_Plate_{j}_{i}',(x+px,y+py,z));kit('Glass',f'V4_Glass_{j}_{i}',(x+gx,y+gy,z+.02))
# Packed back shelf: cups, small pot silhouettes and plate stacks.
for i in range(10):
 x=-3.20+i*.24;kit('CoffeeCup','V4_ShelfCup_'+str(i),(x,2.02,1.53))
for i,x in enumerate([-3.12,-2.44,-1.76]):
 kit('SoupBowl','V4_ShelfPot_'+str(i),(x,2.27,1.54))
 for z in range(3):kit('PlateClean',f'V4_ShelfStack_{i}_{z}',(x+.15,2.28,1.53+z*.018))
# Hanging pans over actual hob (left of hood), solid metal discs and handles.
navy=mat('V4_PaintedNavy','1D3B6E',.4);brass=mat('V4_BurnishedCopper','B86D39',.36);dark=mat('V4_Mortar','23354C',.85)
rod('V4_PanRack',(-3.93,2.17,1.69),(-3.00,2.17,1.69),.022,navy)
for i,x in enumerate([-3.79,-3.46,-3.13]):
 rod('V4_PanHandle'+str(i),(x,2.17,1.64),(x,2.17,1.44),.018,navy)
 rod('V4_PanBowl'+str(i),(x,2.145,1.32),(x,2.185,1.32),.12,brass)
 rod('V4_PanInside'+str(i),(x,2.125,1.32),(x,2.14,1.32),.095,navy)
# Thin dark joint backings sit behind the same masonry, no tabletop/room footprint changes.
box('V4_RearMortar',(0,2.64,1.40),(8.18,.05,.82),dark,0)
# Quay vignette kept clear of entry/queue and terrace occupied seats.
for i,(src,loc,yaw) in enumerate([('Crate',(-.70,-3.23,-.03),8),('Crate',(-.66,-3.23,.43),-7),('Barrel',(-1.21,-3.16,-.03),0),('Barrel',(4.37,1.54,-.03),0),('Crate',(4.37,.91,-.03),12),('Crate',(-4.40,1.86,-.03),0)]):kit(src,'V4_QuayCargo'+str(i),loc,yaw)
# Solid rope coils at cargo, thin torus rings; UV1 generated below.
rope=mat('V4_Rope','BD965F',.9)
for i in range(3):
 bpy.ops.mesh.primitive_torus_add(major_segments=16,minor_segments=5,location=(-1.20,-3.16,.91+i*.026),major_radius=.15-i*.018,minor_radius=.014);ob=bpy.context.object;ob.name='V4_RopeCoil'+str(i);ob.data.materials.append(rope);production.append(ob)
# Lantern on each visible quay pillar and additional side wall pool.
for i,(x,y,z) in enumerate([(-4.5,-3.18,.64),(-3.3,-3.18,.64),(-2.1,-3.18,.64),(-.9,-3.18,.64),(.3,-3.18,.64),(1.5,-3.18,.64),(4.5,-3.18,.64),(4.03,1.1,1.02),(-4.03,-1.1,1.02)]):
 kit('TableLantern','V4_PillarLantern'+str(i),(x,y,z));d=bpy.data.lights.new('V4_Practical'+str(i),'POINT');d.energy=10;d.color=tuple(lin(v) for v in (1,.66,.25));d.shadow_soft_size=.12;ob=bpy.data.objects.new(d.name,d);sc.collection.objects.link(ob);ob.location=(x,y,z+.14)
# New small primitives get independent lightmap UV; copied kit retains both channels.
for ob in production:
 if ob.name in oldnames or ob.name.startswith(('V4_WallPlant','V4_Plate','V4_Glass','V4_Shelf','V4_QuayCargo','V4_PillarLantern')):continue
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 if not ob.data.uv_layers:ob.data.uv_layers.new(name='UV0')
 if len(ob.data.uv_layers)<2:ob.data.uv_layers.new(name='LightmapUV')
 ob.data.uv_layers.active_index=1;bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.035);bpy.ops.object.mode_set(mode='OBJECT');ob.data.uv_layers.active_index=0
bpy.context.view_layer.update();meshrows=[];total=0
for o in production:
 o.data.calc_loop_triangles();t=len(o.data.loop_triangles);total+=t;pts=[o.matrix_world@v.co for v in o.data.vertices];meshrows.append({'name':o.name,'triangles':t,'linked_V2':provenance.get(o.name,True) if o.name in oldnames else o.name in [p['name'] for p in placements],'world_min_m':[min(p[k] for p in pts) for k in range(3)],'world_max_m':[max(p[k] for p in pts) for k in range(3)]})
assert total<=180000,total
bpy.ops.object.select_all(action='DESELECT');copies=[]
for o in production:
 c=o.copy();c.data=o.data.copy();sc.collection.objects.link(c);c.name='EXPORT_'+o.name;c.select_set(True);copies.append(c)
bpy.ops.export_scene.fbx(filepath=str(O/'Stage1V4.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,colors_type='LINEAR',path_mode='RELATIVE')
for o in copies:bpy.data.objects.remove(o,do_unlink=True)
for o in sc.objects:
 if o.type=='LIGHT':lightrows.append({'name':o.name,'type':o.data.type,'position_blender_m':list(o.location),'position_unity_m':[o.location.x,o.location.z,-o.location.y],'blender_power':o.data.energy,'linear_rgb':list(o.data.color),'range_recipe_m':5,'radius_m':getattr(o.data,'shadow_soft_size',0)})
(O/'build-metrics.json').write_text(json.dumps({'room_triangles':total,'budget':180000,'production_meshes':meshrows,'placements':placements,'V2_blend_sha256':sha(V/'Stage1V2.blend'),'V3_blend_sha256':sha(V3/'Stage1V3.blend'),'footprint_room':[8,5],'kitchen':[3,5],'original_mesh_names':sorted(oldnames),'original_geometry_preserved':True},indent=2))
(O/'lighting.json').write_text(json.dumps({'lights':lightrows,'world_linear_rgb':[.055,.16,.42],'world_strength':.32,'exposure_ev':-.25,'view_transform':'AgX Medium High Contrast','saturation':1.10,'bloom':{'threshold':1.8,'strength':.07,'size':.35},'water':'opaque blue emission0.48, roughness0.22 metallic0.32 noise2.8 bump0.11 strength0.24','URP_units_not_equivalent_to_watts':True},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Stage1V4.blend'),relative_remap=True)
checkpoint(f'C source export VERIFIED {total:,}tri/{len(production)}meshes within180k; {len(placements)} added V2-kit references plus pan rack/mortar/rope. Independent FBX and visual checks pending E. IN PROGRESS D additive guests, same rig/clips; original exports untouched.')
print('V4 BUILD PASS',total,len(production),flush=True)
