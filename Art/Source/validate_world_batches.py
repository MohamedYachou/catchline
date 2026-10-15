"""Blender5.2: source/FBX roundtrip, original-pivot variants, grid envelope checks."""
import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
def near(a,b,tol=2e-5):assert len(a)==len(b) and all(abs(x-y)<tol for x,y in zip(a,b)),(list(a),list(b))
def bounds(meshes):
 pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 return [min(v[i] for v in pts) for i in range(3)],[max(v[i] for v in pts) for i in range(3)]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['WorldPolish','DayBoatKit']
old={a['asset']:a for a in json.loads((ROOT/'Art/Models/GullHarbour/build-metrics.json').read_text())['assets']}
for batch in args:
 out=ROOT/'Art/Models'/batch;data=json.loads((out/'build-metrics.json').read_text());results=[]
 for a in data['assets']:
  n=a['asset'];bpy.ops.wm.open_mainfile(filepath=str(ROOT/a['source']));col=bpy.data.collections['ASSET_EXPORT'];meshes=[o for o in col.objects if o.type=='MESH'];root=bpy.data.objects['Catchline_'+n]
  assert root.location.length<1e-6 and all(o.parent==root for o in meshes)
  assert not any(o.type=='ARMATURE' for o in col.objects)
  lo,hi=bounds(meshes);near(lo,a['bounds_min_blender']);near(hi,a['bounds_max_blender'])
  names={o.name for o in meshes};source_pivots={o.name:list(o.location) for o in meshes};top=[]
  for ob in meshes:
   near(ob.scale,[1,1,1]);near(ob.rotation_euler,[0,0,0]);near(ob.location,a['pivots_blender'][ob.name]);assert not ob.modifiers
   assert all(m.name in data['palette_srgb'] for m in ob.data.materials),(n,ob.name,[m.name for m in ob.data.materials if m.name not in data['palette_srgb']])
   assert all(math.isfinite(x) for v in ob.data.vertices for x in v.co)
   assert all(p.area>1e-11 for p in ob.data.polygons),(n,ob.name,'degenerate polygon')
   bm=bmesh.new();bm.from_mesh(ob.data);assert all(v.link_faces for v in bm.verts)
   top.append({'part':ob.name,'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges)});bm.free()
  if n.startswith('Rowboat_Variant') or n=='Skiff_VariantBlue' or n.startswith('FishingRod_'):
   base='Rowboat' if n.startswith('Rowboat') else 'Skiff' if n.startswith('Skiff') else 'FishingRod'
   assert names==set(old[base]['pivots_blender'])
   for k in names:near(source_pivots[k],old[base]['pivots_blender'][k])
   near(lo,old[base]['bounds_min_blender']);near(hi,old[base]['bounds_max_blender'])
  if n in ('BigCooler','BigIceBox'):near([hi[i]-lo[i] for i in range(3)],[1,.6,.5]);assert 'HingedLid' in names
  if n=='HillBackdrop':near([hi[0]-lo[0]],[40])
  if n=='KelpForest':near([hi[0]-lo[0],hi[1]-lo[1],lo[2],hi[2]],[4,4,0,0])
  if n=='DayBoat':
   l,h=bounds([bpy.data.objects['PlankDeck']]);near(l,[-2.5,-5,-.05]);near(h,[2.5,5,0])
   l,h=bounds([bpy.data.objects['WheelhouseBody']]);near(l,[-1.5,-5,0]);near(h,[1.5,-3,1.65])
   assert {f'RodSocket_{i}' for i in range(1,7)}<=names
   rail=bpy.data.objects['Rails'];pts=[rail.matrix_world@v.co for v in rail.data.vertices]
   assert not any(v.x< -2.7 and 2.56<v.y<3.94 and v.z>.10 for v in pts)
  foot={'NetDrum':(2,1),'PowerHauler':(1,1),'Conveyor_Straight':(1,1),'Conveyor_Corner':(1,1),'SortingChute':(2,1),'FishHold':(2,2),'IceMachine':(1,1),'GuttingTable':(2,1),'Crane':(1,1)}
  if n in foot:
   assert all(lo[i]>=-foot[n][i]/2-1e-5 and hi[i]<=foot[n][i]/2+1e-5 for i in (0,1)),(n,lo,hi)
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(ROOT/a['fbx']))
  imported=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert {o.name for o in imported}==names
  l,h=bounds(imported);near(l,lo);near(h,hi)
  for o in imported:near(o.matrix_world.translation,source_pivots[o.name])
  results.append({'asset':n,'source_and_fbx_passed':True,'parts':len(names),'topology':top})
 (out/'validation.json').write_text(json.dumps({'all_passed':True,'asset_count':len(results),'assets':results},indent=2)+'\n');print('PASS',batch,len(results),'sources and FBXs',flush=True)
