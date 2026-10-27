"""Idempotent in-place approved-grid migration of the authored room sources.
Run instead of historical build.py to re-export the corrected source blends.
"""
import bpy,bmesh,json,math,hashlib,sys,importlib.util
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('geom',str(R/'Art/Source/build_crab_coast_props.py'));H=importlib.util.module_from_spec(spec);spec.loader.exec_module(H)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for stage,name,W,K in [(2,'Stage2Bistro',10,4),(3,'Stage3Restaurant',12,4),(4,'Stage4Seafood',14,5)]:
 D=O.parent/name;bpy.ops.wm.open_mainfile(filepath=str(D/(name+'.blend')));sc=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0;right=W-4
 cells={c['name']:c for c in json.loads((D/'textures/atlas.json').read_text())['cells']};mat=next(m for m in bpy.data.materials if m.name.startswith('Restaurant_Atlas_'))
 def obj(n,g):
  me=bpy.data.meshes.new(n);me.from_pydata(g.vertices,[],g.faces);me.update();ob=bpy.data.objects.new(n,me);sc.collection.objects.link(ob);me.materials.append(mat);uv=me.uv_layers.new(name='UV0')
  for p,col in zip(me.polygons,g.colours):
   x,y,w,h=cells[col]['pixel_cell'];ax=[k for k in range(3) if k!=max(range(3),key=lambda k:abs(p.normal[k]))];pts=[me.vertices[me.loops[i].vertex_index].co for i in p.loop_indices];lo=[min(v[k] for v in pts) for k in ax];hi=[max(v[k] for v in pts) for k in ax]
   for i,v in zip(p.loop_indices,pts):
    a=[(v[k]-l)/max(r-l,1e-8) for k,l,r in zip(ax,lo,hi)];uv.data[i].uv=((x+24+a[0]*(w-48))/2048,1-(y+24+a[1]*(h-48))/2048)
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='LightmapUV');grid=math.ceil(math.sqrt(len(me.polygons)))
  for j,p in enumerate(me.polygons):
   for i,(u,v) in zip(p.loop_indices,[(.12,.12),(.88,.12),(.12,.88)]):uv.data[i].uv=((j%grid+u)/grid,(j//grid+v)/grid)
  me.uv_layers.active_index=0;ao=me.color_attributes.new(name='LocalAO',type='BYTE_COLOR',domain='CORNER')
  for d in ao.data:d.color=(.9,.9,.9,1)
  return ob
 if not sc.get('approved_grid_fit_v1'):
  removed=[]
  # Runtime owns all usable seats/tables. Omit previous hard-coded seating and its loose settings.
  prefixes=('BistroTerrace','BistroEntry','BistroString','RestaurantTerrace','RestaurantDiningTable','RestaurantOuterFestoon','SeafoodTerrace','SeafoodEntry','SeafoodDiningTable','SeafoodBooth','SeafoodFestoon','DiningTwo_','DiningFour','TerraceTable','Candle_','PlaceSetting_','Glass_','V4_Plate_','V4_Glass_','V4_PillarLantern','PlateDirty','CoffeeCup','DinnerSoup','DinnerPlate')
  exact={'Booth','JettyLamp','JettyBarrel','JettyCrate','RopeFencePost','V4_WallPlant_9','TerraceParasol','SeafoodBarStools','RestaurantBarStools'}
  for ob in list(sc.objects):
   if ob.type=='MESH' and (ob.name.startswith(prefixes) or ob.name in exact):removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
  # Keep the old shell's detailed rear/left walls/cabinet dressing, replace floors and right/front wall.
  ob=bpy.data.objects['RoomShell'];ob.data=ob.data.copy();bm=bmesh.new();bm.from_mesh(ob.data);pending=set(bm.verts);delete=[]
  while pending:
   seed=pending.pop();comp={seed};stack=[seed]
   while stack:
    for e in stack.pop().link_edges:
     for v in e.verts:
      if v in pending:pending.remove(v);comp.add(v);stack.append(v)
   pts=[ob.matrix_world@v.co for v in comp];lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
   if hi[2]<=.091 or lo[0]>=right-.10 or hi[1]<-2.38 or lo[1]<-2.78:delete.extend(comp)
  bmesh.ops.delete(bm,geom=delete,context='VERTS');bm.to_mesh(ob.data);bm.free()
  # Compress stage3's mistakenly sixth row; structural surfaces move coherently to north Y2.5.
  if stage==3:
   def sy(y):return y if y<=0 else y*5/7
   structural=('RoomShell','RearMasonry','RearCoping','V4_RearMortar','RestaurantDiningWall','RestaurantArchedWindows','RestaurantWallPanels','BistroAwningFacade','BistroBlueAwning','RestaurantBackBar')
   for ob in sc.objects:
    if ob.type=='MESH' and not ob.name.startswith('REVIEW_'):
     if ob.name.startswith(structural):
      ob.data=ob.data.copy();mw=ob.matrix_world.copy();mi=mw.inverted()
      for v in ob.data.vertices:p=mw@v.co;p.y=sy(p.y);v.co=mi@p
     else:
      pts=[ob.matrix_world@Vector(v) for v in ob.bound_box];cy=(min(v.y for v in pts)+max(v.y for v in pts))/2;ob.location.y+=sy(cy)-cy
    elif ob.type=='LIGHT':ob.location.y=sy(ob.location.y)
  # Shift pass cluster to the widened kitchen boundary; retain all station silhouettes.
  if stage in [2,3]:
   for ob in sc.objects:
    if ob.name.startswith(('PassCounter','PassStack','PassFish','PassCloche')):ob.location.x+=.55 if stage==2 else .4
  # Remove obsolete forward-terrace practicals, keep interior lights.
  for ob in list(sc.objects):
   if ob.type=='LIGHT' and ob.location.y< -2.5:bpy.data.objects.remove(ob,do_unlink=True)
  # Exact one-metre squares; no interpolation of the gameplay footprint.
  g=H.Geometry();g.box(((-4+right+3)/2,0,-.11),(W+3,5,.22),'wooddark')
  for x in range(W+3):
   for y in range(5):
    col=('tilecream' if (x+y)%2==0 else 'tileblue') if x<K else ('woodlight' if (x+2*y)%7==0 else 'wood')
    # atlas uses tile names depending on accepted version
    if col not in cells:col=('ivory' if (x+y)%2==0 else 'stonecool') if x<K else 'wood'
    g.box((-3.5+x,2-y,.015),(.988,.988,.05),col)
  obj('GridFloor',g)
  # Right cutaway wall ends before doorway at y1.5..2.5. Door tile=(Width-1,0).
  g=H.Geometry();g.box((right+.10,-.5,.47),(.20,4,.94),'plaster');g.box((right+.10,-.5,.98),(.25,4,.08),'navy');obj('GridSideWall',g)
  g=H.Geometry()
  for y in [1.48,2.52]:g.box((right+.08,y,1.10),(.22,.075,2.2),'wooddark')
  g.box((right+.08,2,2.21),(.24,1.12,.10),'navy');g.box((right+.08,2,.025),(.30,.98,.05),'stonecream');obj('GridEntranceFrame',g)
  # Narrow forward quay has no seats; side terrace is open to sky on all outer sides.
  g=H.Geometry();g.box(((right-4)/2,-2.87,-.12),(W+.4,.70,.24),'wooddark')
  for j in range(3):g.box(((right-4)/2,-2.62-j*.22,.015),(W+.35,.21,.05),'wood')
  for x in [-4,right,right+3]:
   for y in [-2.5,2.5]:g.tube([(x,y,-1.05),(x,y,-.05)],[.09,.09],8,'wooddark')
  obj('GridQuayPiles',g)
  g=H.Geometry();points=[(right+2.9,-2.4+4.8*i/24,2.20-.25*math.sin(math.pi*i/24)) for i in range(25)];g.tube(points,[.012]*25,6,'dark')
  for y in [-2.4,2.4]:g.tube([(right+2.9,y,0),(right+2.9,y,2.25)],[.026,.026],8,'navy')
  for i in range(10):
   y=-2.3+i*4.6/9;z=2.20-.25*math.sin(math.pi*(y+2.4)/4.8);g.ellipsoid((right+2.9,y,z-.06),(.04,.04,.055),8,3,'glow')
  obj('GridTerraceStringLights',g)
  # Small off-grid plant accents; no chairs, tables or service blockers in terrace tiles.
  for i,y in enumerate([-2.65,2.70]):
   src=bpy.data.objects.get('PlantPot1')
   if src:
    q=src.copy();q.data=src.data.copy();q.name='GridEdgePlant'+str(i);sc.collection.objects.link(q);q.location=(right+1.5,y,.04)
  for i,y in enumerate([-1.5,1.5]):
   d=bpy.data.lights.new('GridTerraceWarm'+str(i),'POINT');d.energy=16;d.color=(1,.603827,.204902);d.shadow_soft_size=.24;q=bpy.data.objects.new(d.name,d);sc.collection.objects.link(q);q.location=(right+2.65,y,1.85)
  sc['approved_grid_fit_v1']=True
  (D/'fit-changes.json').write_text(json.dumps({'removed_nodes':removed,'stage':stage,'new_components':['GridFloor','GridSideWall','GridEntranceFrame','GridQuayPiles','GridTerraceStringLights'],'rule':'no fixed usable seating exported; runtime supplies all seats'},indent=2))
 # Remove orphaned front/right wall lantern fragments left in the merged historical shell.
 if not sc.get('approved_grid_fit_cleanup_v1'):
  ob=bpy.data.objects['RoomShell'];bm=bmesh.new();bm.from_mesh(ob.data);pending=set(bm.verts);delete=[]
  while pending:
   v=pending.pop();comp={v};stack=[v]
   while stack:
    for e in stack.pop().link_edges:
     for v in e.verts:
      if v in pending:pending.remove(v);comp.add(v);stack.append(v)
   pts=[ob.matrix_world@v.co for v in comp];lo=[min(p[k] for p in pts) for k in range(3)];hi=[max(p[k] for p in pts) for k in range(3)]
   if lo[2]>1 and hi[2]<1.4 and ((lo[1]<-2.3 and hi[1]<-2.2) or (lo[0]>right-.6 and hi[0]<right and hi[1]<1.5)):delete.extend(comp)
  bmesh.ops.delete(bm,geom=delete,context='VERTS');bm.to_mesh(ob.data);bm.free()
  old=bpy.data.objects.get('SeafoodStringLights')
  if old:bpy.data.objects.remove(old,do_unlink=True)
  sc['approved_grid_fit_cleanup_v1']=True
 # Refresh metadata from actual geometry, preserving the V4 origin and axis recipe.
 prod=[o for o in sc.objects if o.type=='MESH' and not o.name.startswith('REVIEW_')];bpy.context.view_layer.update();rows=[]
 for ob in prod:
  me=ob.data;me.calc_loop_triangles();pts=[ob.matrix_world@v.co for v in me.vertices];rows.append({'name':ob.name,'export_name':'EXPORT_'+ob.name,'triangles':len(me.loop_triangles),'world_min_m':[min(v[k] for v in pts) for k in range(3)],'world_max_m':[max(v[k] for v in pts) for k in range(3)],'linked_V2':ob.get('kit_source','')})
 metrics=json.loads((D/'build-metrics.json').read_text());metrics.update(production_meshes=rows,room_triangles=sum(r['triangles'] for r in rows),approved_grid_fit=True,room_tiles=[W,5],kitchen_tiles=[K,5],terrace_tiles=[3,5]);(D/'build-metrics.json').write_text(json.dumps(metrics,indent=2))
 layout={'stage':stage,'name':{2:'Bistro',3:'Restaurant',4:'Seafood house'}[stage],'room_tiles':[W,5],'kitchen_tiles':[K,5],'terrace_tiles':[3,5],'tile_m':1,'room_bounds_blender_m':[[-4,-2.5,0],[right,2.5,0]],'kitchen_bounds_blender_m':[[-4,-2.5,0],[K-4,2.5,0]],'terrace_bounds_blender_m':[[right,-2.5,0],[right+3,2.5,0]],'terrace_tile_x_range':[W,W+2],'door_tile':[W-1,0],'entry_centre_blender_m':[right,2,.04],'door_tile_centre_blender_m':[right-.5,2,.04],'floor_surface_z_m':.04,'terrace_surface_z_m':.04,'waterline_z_m':-.55,'origin':'unchanged V4','tile_to_blender':'[-4+x+.5,2.5-y-.5,.04]','convert_blender_to_unity':'[x,z,-y]','runtime_layout_convention':'all fixed dining tables/chairs/booths omitted; runtime places usable seats','front_quay':'narrow .70m strip along -Y, no seats','terrace_open_sky':True,'terrace_open_outer_sides':True};(D/'layout.json').write_text(json.dumps(layout,indent=2))
 recipe=json.loads((D/'lighting.json').read_text());recipe['lights']=[{'name':o.name,'type':o.data.type,'position_blender_m':list(o.location),'position_unity_m':[o.location.x,o.location.z,-o.location.y],'blender_power':o.data.energy,'linear_rgb':list(o.data.color),'range_recipe_m':5,'radius_m':o.data.shadow_soft_size} for o in sc.objects if o.type=='LIGHT'];recipe['approved_grid_fit']='room5deep, side terrace3x5, coordinates refreshed from scene';(D/'lighting.json').write_text(json.dumps(recipe,indent=2))
 bpy.ops.object.select_all(action='DESELECT');copies=[]
 for ob in prod:q=ob.copy();q.data=ob.data.copy();q.name='EXPORT_'+ob.name;sc.collection.objects.link(q);q.select_set(True);copies.append(q)
 bpy.ops.export_scene.fbx(filepath=str(D/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,colors_type='LINEAR',path_mode='RELATIVE')
 for q in copies:bpy.data.objects.remove(q,do_unlink=True)
 sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;bpy.ops.wm.save_as_mainfile(filepath=str(D/(name+'.blend')));print(name,'GRID FIT PASS',len(prod),metrics['room_triangles'],flush=True)
