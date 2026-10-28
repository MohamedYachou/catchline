from io_scene_fbx import parse_fbx
from pathlib import Path
p=Path(__file__).resolve().parents[3]/'Assets/Art/Models/Restaurant/Pack/service/Restaurant_CatchBoard.fbx'
r,v=parse_fbx.parse(str(p))
def show(e,depth=0):
 if e.id in [b'Objects',b'Geometry'] or depth:
  print(' '*depth,e.id,[(len(x),str(type(x))) if hasattr(x,'__len__') else x for x in e.props])
  for c in e.elems:show(c,depth+1)
 else:
  for c in e.elems:show(c,0)
show(r)
