"""Independent final-export geometry checks and incumbent scale reference."""
import bpy,sys,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[4]
sys.path.insert(0,str(R/'Art/Source/Restaurant/kenney'))
from inspect_pack import reset,load,bounds

def inspect(p):
 reset();obs=load(p);meshes=[o for o in obs if o.type=='MESH'];lo,hi=bounds(meshes)
 geometry=[]
 for ob in meshes:
  geometry.append(dict(vertices=[[round(v,7) for v in ob.matrix_world@x.co] for x in ob.data.vertices],polygons=[list(p.vertices) for p in ob.data.polygons],uv=[[round(v,7) for v in x.uv] for x in ob.data.uv_layers.active.data]))
 return dict(size_unity=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],bottom=lo.z,centre_xy=[(lo.x+hi.x)/2,(lo.y+hi.y)/2],geometry_sha256=hashlib.sha256(json.dumps(geometry,sort_keys=True).encode()).hexdigest())

m=json.loads((O/'manifest.json').read_text());rows={r['name']:inspect(O/(r['name']+'.fbx')) for r in m['items']}
reference={}
for stem in ['GrilledFishPlate','SoupBowl','CoffeeCup','Glass']:
 p=R/'Art/Models/Restaurant/Stage1V2/items'/(stem+'.fbx')
 if p.exists():reference[stem]=inspect(p)
checks=dict(exact_six=len(rows)==6,bottom_center=all(abs(v['bottom'])<1e-6 and max(map(abs,v['centre_xy']))<1e-6 for v in rows.values()),carried_equals_served=rows['Restaurant_Dish_GrilledFish']['geometry_sha256']==rows['Restaurant_GrilledFishPlate']['geometry_sha256'],plate_widths=all(abs(rows['Restaurant_'+n]['size_unity'][0]-.22)<1e-5 for n in ['Dish_GrilledFish','Dish_FilletsLemon','Dish_FishSoup','GrilledFishPlate']),glass_height=abs(rows['Restaurant_Dish_Lemonade']['size_unity'][1]-.15)<1e-5)
(O/'geometry-audit.json').write_text(json.dumps(dict(pass_all=all(checks.values()),checks=checks,items=rows,incumbents=reference,proof_table=dict(diameter_m=.54,height_m=.69,dish_bottom_m=.692,clearance_m=.002)),indent=2))
print('GEOMETRY',checks)
assert all(checks.values())
