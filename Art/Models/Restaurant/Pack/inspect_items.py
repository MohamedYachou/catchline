import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent; R=O.parents[3]
sys.path.insert(0,str(R/'Art/Source/Restaurant/kenney'))
from inspect_pack import reset,load,bounds
NAMES='Stove SoupKettle PrepCounter FridgeV2 CoffeeBar TableFor2 TableFor4 Booth TerraceTable ReceptionDesk SinkDishRack Fryer Oven Grill Steamer PassCounter PlantPot1 LampPost Trophy Net Chart Jukebox DrinksFridge TableCandle BigFridge ReliableStove'.split()
def reference(n):
 p=R/'Art/Models/Restaurant/Stage1V2/items'/(n+'.fbx')
 if not p.exists():p=R/'Art/Models/Restaurant/KitchenKit2'/('Restaurant_'+n+'.fbx')
 if n=='TableCandle':p=R/'Art/Models/Restaurant/Stage1V2/items/TableLantern.fbx'
 return p
if __name__=='__main__':
 rec=[]
 for n in NAMES:
  reset();p=reference(n);obs=load(p);lo,hi=bounds(obs)
  rec.append(dict(name=n,source=p.relative_to(R).as_posix(),min=list(lo),max=list(hi),size=list(hi-lo),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),roots=[dict(name=o.name,rotation=list(o.rotation_euler),scale=list(o.scale)) for o in obs if o.parent is None]))
 (O/'reference-inventory.json').write_text(json.dumps(rec,indent=2))
 print('REFERENCE_DONE',len(rec))
