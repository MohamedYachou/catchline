"""Clip only the connected bed's material borders; interpolate its exact triangle planes."""
from pathlib import Path
import json,math
import numpy as np
from shapely.geometry import Polygon,LineString,Point
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
S=Path(__file__).resolve().parent;s=json.loads((S/'accepted-snapshot.json').read_text());bed=s['objects']['ConnectedBathymetry'];verts=bed['vertices']
old=unary_union([Polygon([verts[i][:2] for i in f]) for f,m in zip(bed['faces'],bed['material_indices']) if m==0]);patches=[]
for p in sorted(old.geoms,key=lambda p:p.centroid.x):
 cx,cy=p.centroid.coords[0];angles=np.arange(96)*math.tau/96;r=[]
 for a in angles:
  hit=p.boundary.intersection(LineString([(cx,cy),(cx+100*math.cos(a),cy+100*math.sin(a))]));ps=[hit] if hit.geom_type=='Point' else list(hit.geoms);r.append(max(math.hypot(q.x-cx,q.y-cy) for q in ps))
 coeff=np.fft.rfft(r);coeff[5:]=0;smooth=np.fft.irfft(coeff,n=96);pts=[(cx+smooth[i]*math.cos(angles[i]),cy+smooth[i]*math.sin(angles[i])) for i in range(0,96,4)]
 q=Polygon(pts);a,b,c,d=q.bounds;A,B,C,D=p.bounds
 pts=[(A+(x-a)*(C-A)/(c-a),B+(y-b)*(D-B)/(d-b)) for x,y in pts];outer=Polygon(pts)
 shift=np.array(p.centroid.coords[0])-outer.centroid.coords[0]
 if np.linalg.norm(shift)>.48:
  shift*=.35/np.linalg.norm(shift);pts=[tuple(np.array(v)+shift) for v in pts];outer=Polygon(pts)
 assert outer.is_valid
 assert max(abs(a-b) for a,b in zip(p.bounds,outer.bounds))<=.5
 # Fade stays inside the exact accepted bounding footprint. 24 segments in each contour.
 pc=np.array(outer.centroid.coords[0]);outerpts=np.array(pts);length=np.linalg.norm(outerpts-pc,axis=1)
 rings=[Polygon(pc+(outerpts-pc)*((length-w)/length)[:,None]) for w in (.32,.64)]
 core=rings[1];middle=rings[0].difference(core);edge=outer.difference(rings[0]);
 patches.append({'old':p,'outer':outer,'core':core,'middle':middle,'edge':edge,'row':{'centre_before':list(p.centroid.coords[0]),'centre_after':list(outer.centroid.coords[0]),'bounds_before':list(p.bounds),'bounds_after':list(outer.bounds),'outline_segments':24,'transition_total_width_m':.64,'boundary_hausdorff_m':p.boundary.hausdorff_distance(outer.boundary),'area_before':p.area,'area_after':outer.area,'outer_xy':pts,'middle_xy':list(rings[0].exterior.coords)[:-1],'core_xy':list(core.exterior.coords)[:-1]}})
 assert math.dist(p.centroid.coords[0],outer.centroid.coords[0])<.5
regions=[(patch[k],i) for patch in patches for k,i in [('core',0),('middle',2),('edge',3)]]
union=unary_union([p['outer'] for p in patches]);newverts=[v[:] for v in verts];index={tuple(round(x,6) for x in v):i for i,v in enumerate(newverts)};faces=[];mats=[];changed=0;maxplane=0

def add(poly,tri,mat):
 global maxplane
 if poly.is_empty:return
 if poly.geom_type=='MultiPolygon' or poly.geom_type=='GeometryCollection':
  for p in poly.geoms:
   if p.geom_type in ('Polygon','MultiPolygon'):add(p,tri,mat)
  return
 if poly.area<1e-9:return
 a,b,c=[np.array(verts[j],dtype=float) for j in tri];cross=np.cross(b-a,c-a)
 if abs(cross[2])<1e-8:raise ValueError('cannot cut vertical bed')
 ts=constrained_delaunay_triangles(poly)
 for t in ts.geoms:
  f=[]
  for x,y in list(t.exterior.coords)[:3]:
   z=a[2]-(cross[0]*(x-a[0])+cross[1]*(y-a[1]))/cross[2];v=[x,y,float(z)];key=tuple(round(k,6) for k in v)
   if key not in index:index[key]=len(newverts);newverts.append(v)
   f.append(index[key])
  if len(set(f))<3:continue
  # Retain source winding.
  if np.cross(np.array(newverts[f[1]])-newverts[f[0]],np.array(newverts[f[2]])-newverts[f[0]])[2]*cross[2]<0:f.reverse()
  faces.append(f);mats.append(mat)

# Preserve authoritative original diagonals even in untouched nonplanar quads.
vfaces={i:set() for i in range(len(verts))}
for fi,f in enumerate(bed['faces']):
 for v in f:vfaces[v].add(fi)
trifaces={i:[] for i in range(len(bed['faces']))}
for tri in bed['loop_triangles']:
 match=set.intersection(*(vfaces[v] for v in tri));assert len(match)==1
 trifaces[next(iter(match))].append(tri)
for fi,(face,mi) in enumerate(zip(bed['faces'],bed['material_indices'])):
 poly=Polygon([verts[j][:2] for j in face]);touch=not poly.is_valid or poly.area<1e-8
 if touch or max(verts[j][2] for j in face)<-20 or not poly.intersects(union):
  for tri in trifaces[fi]:faces.append(tri);mats.append(1 if mi==0 else mi)
  continue
 changed+=1
 for tri in trifaces[fi]:
  t=Polygon([verts[j][:2] for j in tri]);add(t.difference(union),tri,1)
  for region,mi2 in regions:
   if t.intersects(region):add(t.intersection(region),tri,mi2)
# Remove unused vertices while retaining every used original coordinate exactly.
used=sorted({j for f in faces for j in f});lookup={v:i for i,v in enumerate(used)};out={'vertices':[newverts[j] for j in used],'faces':[[lookup[j] for j in f] for f in faces],'material_indices':mats,'patches':[p['row'] for p in patches],'changed_original_faces':changed,'old_triangles':bed['triangles'],'new_triangles':sum(len(f)-2 for f in faces)}
(S/'sand-edges-plan.json').write_text(json.dumps(out,indent=2)+'\n');print('PLAN PASS',out['old_triangles'],out['new_triangles'],'changed faces',changed)
for p in patches:print({k:v for k,v in p['row'].items() if not k.endswith('_xy')})
