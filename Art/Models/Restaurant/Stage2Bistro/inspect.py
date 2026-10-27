import bpy,json
from pathlib import Path
O=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(O.parent/'Stage1V4/Stage1V4.blend'));sc=bpy.context.scene;rows=[]
for o in sc.objects:
 if o.type!='MESH' or o.name.startswith('REVIEW_'):continue
 p=[o.matrix_world@v.co for v in o.data.vertices];rows.append({'name':o.name,'loc':list(o.location),'lo':[min(v[k] for v in p) for k in range(3)],'hi':[max(v[k] for v in p) for k in range(3)]})
me=bpy.data.objects['RoomShell'].data;parent=list(range(len(me.vertices)))
def find(x):
 while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
 return x
for e in me.edges:a,b=map(find,e.vertices);parent[b]=a
comps={}
for v in me.vertices:comps.setdefault(find(v.index),[]).append(v.co)
cc=[{'id':k,'verts':len(p),'lo':[min(v[i] for v in p) for i in range(3)],'hi':[max(v[i] for v in p) for i in range(3)]} for k,p in comps.items()]
(O/'source-inventory.json').write_text(json.dumps({'meshes':rows,'shell_components':cc},indent=2));print('INSPECT',len(rows),len(cc),flush=True)
