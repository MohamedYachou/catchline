"""Saved-source scalp coverage, complete 10-degree angular hit list.
Natural exposed forehead/face and ears are not scalp: audit the largest connected
head component only, and record the anatomical hairline exclusion explicitly.
"""
import math,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def audit(bpy,name,out,revision,style,hair_name=None,hat_name=None):
    face=bpy.data.objects[name+'_Face']; data=face.data
    adjacency=[set() for _ in data.vertices]
    for edge in data.edges:
        a,b=edge.vertices;adjacency[a].add(b);adjacency[b].add(a)
    unseen=set(range(len(data.vertices)));components=[]
    while unseen:
        stack=[unseen.pop()];ids=set(stack)
        while stack:
            for neighbor in adjacency[stack.pop()]:
                if neighbor in unseen:unseen.remove(neighbor);ids.add(neighbor);stack.append(neighbor)
        components.append(ids)
    head=max(components,key=len)
    trees={'Scalp':BVHTree.FromPolygons([v.co for v in data.vertices],
             [tuple(p.vertices) for p in data.polygons if all(v in head for v in p.vertices)])}
    for suffix in ('Hair','Hat'):
        ob=bpy.data.objects[(hair_name if suffix=='Hair' else hat_name) or name+'_'+suffix]
        trees[suffix]=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[tuple(p.vertices) for p in ob.data.polygons])
    hits=[];gaps=[];tested=0
    for z in (.705,.725,.745,.765,.785,.805,.825,.845,.865,.885,.905):
        for degrees in range(0,360,10):
            angle=math.radians(degrees);direction=Vector((math.cos(angle),math.sin(angle),0))
            # atan convention: -Y is the open face. A swept front hairline is
            # higher than the nape. Exclusions are listed rather than hidden.
            front=max(0,-math.sin(angle))
            hairline=(.697 if style in ('pixie','short','highbun','lowbun','twinbraid') else .677)+.215*front**2
            excluded=z<hairline or (front>.82 and z<.890)
            distances={key:tree.ray_cast(direction*.5+Vector((0,0,z)),-direction,.6)[3] for key,tree in trees.items()}
            skin=distances['Scalp'];cover=[d for key,d in distances.items() if key!='Scalp' and d is not None]
            gap=not excluded and skin is not None and (not cover or min(cover)>skin+.0002)
            row={'z_m':z,'angle_degrees':degrees,'outside_in_distance_m':distances,
                 'excluded_exposed_face_below_hairline':excluded,'scalp_first':gap}
            hits.append(row)
            if not excluded and skin is not None:tested+=1
            if gap:gaps.append(row)
    result={'name':name,'revision':revision,'rays':len(hits),'scalp_samples':tested,
            'skin_first_hits':len(gaps),'gaps':gaps,'scope':'11 heights .705-.905m, every10degrees all360; anatomical exposed face/hairline exclusions listed; ears/nose/neck separated from scalp by connected mesh',
            'hits':hits}
    (out/'hair-coverage-hits.json').write_text(json.dumps(result,indent=2)+'\n')
    print('FEMALE SCALP COVERAGE',tested,'samples',len(gaps),'gaps',[(g['z_m'],g['angle_degrees']) for g in gaps[:16]],flush=True)
    assert not gaps,'Bare scalp before hair: see hair-coverage-hits.json'
    return {key:value for key,value in result.items() if key not in ('hits','gaps')}
