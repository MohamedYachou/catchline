import bpy,sys,json
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[4]
sys.path.insert(0,str(R/'Art/Source/Restaurant/kenney'))
from inspect_pack import reset,source,load,bounds
reset();obs=load(source('food','utensil-spoon'));lo,hi=bounds(obs)
print('SPOON_SOURCE',list(lo),list(hi),list(hi-lo))
for ob in obs:
 if ob.type=='MESH':
  vs=[ob.matrix_world@v.co for v in ob.data.vertices]
  print('SPOON_POINTS',[list(v) for v in vs[:20]])
