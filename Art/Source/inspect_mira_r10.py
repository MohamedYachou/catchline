"""Read-only r09 component audit; Blender headless."""
import bpy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'Art/Models/CrewV2/Mira-sol/iterations/r09/Mira.blend'))
ob=bpy.data.objects['Mira_HairSculpt']; me=ob.data
adj=[set() for v in me.vertices]
for e in me.edges:
 a,b=e.vertices; adj[a].add(b); adj[b].add(a)
left=set(range(len(adj))); comps=[]
while left:
 seed=min(left); comp={seed}; stack=[seed];left.remove(seed)
 while stack:
  for i in adj[stack.pop()]:
   if i in left: left.remove(i);comp.add(i);stack.append(i)
 vv=[me.vertices[i].co for i in comp]
 pp=[p for p in me.polygons if p.vertices[0] in comp]
 comps.append(dict(id=len(comps), seed=seed, vertices=len(comp), triangles=sum(len(p.vertices)-2 for p in pp),
   bounds=[[round(f(v[d] for v in vv),6) for d in range(3)] for f in (min,max)]))
print('HAIR_COMPONENTS',json.dumps(comps,indent=2),flush=True)
print('MESHSIZES',[(o.name,len(o.data.vertices),len(o.data.polygons)) for o in bpy.data.objects if o.type=='MESH'],flush=True)
