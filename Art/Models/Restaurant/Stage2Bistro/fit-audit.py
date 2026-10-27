import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from io_scene_fbx import parse_fbx
O=Path(__file__).resolve().parent
for name,W,K in [('Stage2Bistro',10,4),('Stage3Restaurant',12,4),('Stage4Seafood',14,5)]:
 D=O.parent/name;f=D/(name+'.fbx');tree,version=parse_fbx.parse(str(f));settings=next(e for e in tree.elems if e.id==b'GlobalSettings');props=next(e for e in settings.elems if e.id==b'Properties70');units={e.props[0].decode():e.props[-1] for e in props.elems if e.props[0] in [b'UnitScaleFactor',b'OriginalUnitScaleFactor']};assert units['UnitScaleFactor']==100,units
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(f),colors_type='LINEAR');sc=bpy.context.scene;bpy.context.view_layer.update();floor=bpy.data.objects['EXPORT_GridFloor'];tops=[]
 for p in floor.data.polygons:
  pts=[floor.matrix_world@floor.data.vertices[i].co for i in p.vertices]
  if all(abs(v.z-.04)<1e-5 for v in pts):tops.append(pts)
 def contains(p,a,b,c):
  v0=c-a;v1=b-a;v2=p-a;dot00=v0.dot(v0);dot01=v0.dot(v1);dot02=v0.dot(v2);dot11=v1.dot(v1);dot12=v1.dot(v2);inv=1/(dot00*dot11-dot01*dot01);u=(dot11*dot02-dot01*dot12)*inv;v=(dot00*dot12-dot01*dot02)*inv;return u>=-1e-5 and v>=-1e-5 and u+v<=1.00001
 tested=[]
 for x in range(W+3):
  for y in range(5):
   p=Vector((-3.5+x,2-y,.04));assert any(contains(p,*tri) for tri in tops),(name,x,y);tested.append([x,y])
 # Door clear at standing head and waist along right wall opening (exclude frame threshold).
 wall=bpy.data.objects['EXPORT_GridSideWall'];pts=[wall.matrix_world@v.co for v in wall.data.vertices];assert max(v.y for v in pts)<1.51
 forbidden=['EXPORT_DiningFour','EXPORT_DiningTwo_','EXPORT_TerraceTable','EXPORT_SeafoodBooth','EXPORT_RestaurantDiningTable','EXPORT_SeafoodDiningTable']
 assert not [o.name for o in sc.objects if o.name.startswith(tuple(forbidden))]
 l=json.loads((D/'layout.json').read_text());assert l['door_tile']==[W-1,0] and l['room_tiles']==[W,5] and l['kitchen_tiles']==[K,5] and l['terrace_tiles']==[3,5]
 assert hashlib.sha256((D/'textures/Restaurant_BaseColor.png').read_bytes()).hexdigest()==hashlib.sha256((O.parent/'Stage1V4/textures/Restaurant_BaseColor.png').read_bytes()).hexdigest()
 (D/'fit-audit.json').write_text(json.dumps({'pass':True,'grid_centres_checked':tested,'room_tiles':[W,5],'kitchen_tiles':[K,5],'terrace_tiles':[3,5],'door_tile':[W-1,0],'right_wall_stops_at_y':max(v.y for v in pts),'FBX_units':units,'V4_atlas_unchanged':True,'FBX_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'no_fixed_usable_seating':True,'native_import_unverified':True},indent=2));print(name,'GRID+UNITS AUDIT PASS',flush=True)
