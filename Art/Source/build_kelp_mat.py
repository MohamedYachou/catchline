"""WSL preprocessing for exactly-flat kelp. Requires Shapely 2.1+.
Union overlapping leaf silhouettes, subtract bulb disks, triangulate each region.
Blender consumes the saved JSON; no Shapely dependency inside Blender.
"""
from pathlib import Path
import json, math
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import constrained_delaunay_triangles
leaves=[(-.30,-.16,.25,.54),(-.22,.05,-.15,.64),(-.02,-.20,.40,.59),(.10,.07,-.30,.52),(.23,-.11,.12,.56),(-.36,.18,-.48,.42)]
polys=[]
for j,(x,y,a,length) in enumerate(leaves):
    left=[];right=[]
    for i in range(13):
        t=i/12; u,v=math.cos(a),math.sin(a)
        cx=x+u*length*t-v*math.sin(t*5+j)*.025
        cy=y+v*length*t+u*math.sin(t*5+j)*.025
        w=.065*math.sin(math.pi*t)**.65+.003
        left.append((cx-v*w,cy+u*w));right.append((cx+v*w,cy-u*w))
    polys.append(Polygon(left+right[::-1]))
blades=unary_union(polys)
bulbs=unary_union([Polygon([(x+.036*math.cos(i*math.tau/16),y+.028*math.sin(i*math.tau/16)) for i in range(16)]) for x,y in [(-.26,.04),(-.12,-.15),(.12,.09),(.24,-.10)]])
regions=[('M_KelpGreen',blades.difference(bulbs)),('M_WoodRecess',bulbs)]
result=[]
for mat,shape in regions:
    for tri in constrained_delaunay_triangles(shape).geoms:
        points=list(tri.exterior.coords)[:3]
        area=(points[1][0]-points[0][0])*(points[2][1]-points[0][1])-(points[1][1]-points[0][1])*(points[2][0]-points[0][0])
        if area<0:points.reverse()
        result.append({'material':mat,'triangle':[[round(x,9),round(y,9),0] for x,y in points]})
Path(__file__).with_name('kelp-mat.json').write_text(json.dumps({'provenance':'build_kelp_mat.py / planar union, bulb cutouts, constrained Delaunay triangulation','faces':result},indent=2)+'\n')
print('Exactly-flat kelp:',len(result),'triangles; no overlapping faces')
