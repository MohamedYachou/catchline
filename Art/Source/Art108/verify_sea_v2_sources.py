"""Read-only fresh source/FBX examination, independent of authoring functions.

Blender --background --python this-file. Writes only SeaV2-source-audit.json.
"""
import bpy, bmesh, json, hashlib, sys
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree

ROOT=Path(__file__).resolve().parents[3]
NAMES=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else ['GullHarbourMouth','GullKelpBank','GullSandbar','GullRockyPoint','GullDeepChannel']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def tris(objects):
    return sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects)
def distance(p,a,b):
    d=b-a;t=max(0,min(1,(p-a).dot(d)/d.length_squared))
    return (p-(a+d*t)).length

results=[]
for name in NAMES:
    folder=ROOT/'Art/Models/Maps'/name
    source=folder/(name+'SeaV2.blend');fbx=folder/(name+'SeaV2.fbx')
    nav=json.loads((folder/'navigation.json').read_text())
    receipt=json.loads((folder/'SeaV2-validation.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(source))
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    checks=[]
    def check(label,ok,detail=None):
        checks.append(dict(check=label,passed=bool(ok),detail=detail))
        assert ok,(name,label,detail)
    check('saved source and export hashes match current build receipt',
          sha(source)==receipt['sourceSha256'] and sha(fbx)==receipt['fbxSha256'])
    anchors=nav.get('sealColonyAnchors',[])+nav.get('lifeAnchors',[])
    check('source has only authoring meshes, one identity root and declared anchors',
          len(bpy.context.scene.objects)==len(objects)+1+len(anchors) and
          all(o.type in ('MESH','EMPTY') for o in bpy.context.scene.objects))
    root=bpy.data.objects['Catchline_'+name+'SeaV2']
    check('identity root and metre scale',root.location.length<1e-8 and all(abs(s-1)<1e-8 for s in root.scale) and
          all(abs(r)<1e-8 for r in root.rotation_euler) and bpy.context.scene.unit_settings.scale_length==1)
    check('source triangle and mesh counts match',tris(objects)==receipt['triangles'] and len(objects)==receipt['meshCount'])
    positions={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in objects}
    if name=='GullSkerries':
        import math
        check('FIX unchanged ground centres and radii',
              [(g['id'],g['centre']['x'],g['centre']['z'],g['radius']) for g in nav['grounds']]==
              [('seal-rocks',-84,-25,14),('kelp-gully',8,57,15),('outer-reef',99,-35,18)])
        colony=nav['sealColonyAnchors'];life=nav['lifeAnchors']
        check('FIX exactly nine unique life empties',len(anchors)==9 and len({a['id'] for a in anchors})==9)
        check('FIX colony anchors6-12m from seal ground',all(6<=math.hypot(a['position'][0]+84,a['position'][2]+25)<=12 for a in colony))
        check('ADDENDUM colony anchors6-9m from seal ground',all(6<=math.hypot(a['position'][0]+84,a['position'][2]+25)<=9 for a in colony))
        for i,a in enumerate(colony):
            rock=bpy.data.objects[f'Terrain_colony-slab-{i+1}'];ps=positions[rock.name]
            top=max(p.z for p in ps)
            check(f'ADDENDUM colony{i+1} flat top0.5-1.5m and anchor on top',
                  .5<=top<=1.5 and abs(a['position'][1]+.32-top)<.00001 and
                  sum(1 for p in ps if abs(p.z-top)<.00001)>=12,top)
        check('ADDENDUM no colony dome cap or baked reef breaker',not any(o.name.startswith(
              ('ColonySplitBoulder','GullySplitBoulder','OuterReefBreakingPatch','ReefBreak_A','ReefBreak_B')) for o in objects))
        hull_radius=math.hypot(8.5,4.2)/2
        for side in (-1,1):
            rock=bpy.data.objects[f'Terrain_gully-wall-{side}'];ps=positions[rock.name]
            length=max(p.x for p in ps)-min(p.x for p in ps)
            height=max(p.z for p in ps)
            water=next(p for p in nav['islands'] if p['sourceObject']==rock.name)['vertices']
            edge=min(distance(Vector((8,57)),Vector((a['x'],a['z'])),Vector((b['x'],b['z'])))
                     for a,b in zip(water,water[1:]+water[:1]))
            check(f'ADDENDUM gully{side}10-15m long1.5-3m high and5m hull gap',
                  10<=length<=15 and 1.5<=height<=3 and edge-hull_radius>=5,
                  dict(length=length,height=height,conservativeHullGap=edge-hull_radius))
        buoy=next(a for a in life if a['id']=='CrabBuoy_1')['position']
        check('FIX crab buoy8-12m from seal ground',8<=math.hypot(buoy[0]+84,buoy[2]+25)<=12)
        reef=[o for o in objects if o.name.startswith('Terrain_half-tide-reef-')]
        check('FIX six reef rocks8-15m from outer ground',len(reef)==6 and all(8<=math.hypot(sum(p.x for p in positions[o.name])/len(positions[o.name])-99,-sum(p.y for p in positions[o.name])/len(positions[o.name])+35)<=15 for o in reef))
        foam=[o for o in objects if o.name.startswith('SkerryContactFoam')]
        check('FIX thin contact foam above water and upward facing',len(foam)>80 and all(abs(p.z-.035)<.0001 for o in foam for p in positions[o.name]) and all(p.normal.z>.99 for o in foam for p in o.data.polygons),len(foam))
        stack=[p.z-.32 for o in objects if o.name.startswith('CairnStackGranite') for p in positions[o.name]]
        check('FIX granite stack6-8m plus separate cairn',6<=max(stack)<=8 and any(o.name.startswith('LandmarkCairn') for o in objects),max(stack))
    for anchor in anchors:
        o=bpy.data.objects[anchor['id']];x,y,z=anchor['position']
        check(anchor['id']+' source world anchor on rock',o.type=='EMPTY' and o.parent==root and
              (o.matrix_world.translation-Vector((x,-z,y+.32))).length<.0001)
    materials={o.name:sorted(m.name for m in o.data.materials) for o in objects}
    terrain=[o for o in objects if o.get('navigation_terrain')]
    check('all navigation source objects actually present',
          {o.name for o in terrain}=={p['sourceObject'] for p in nav['islands']+nav['shallows']})
    for o in terrain:
        bm=bmesh.new();bm.from_mesh(o.data)
        check(o.name+' closed positive-volume terrain',all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0)
        bm.free()
        vertices=positions[o.name]
        for field,level in [('islands',0),('shallows',-1)]:
            segments=[]
            for face in o.data.polygons:
                points=[vertices[i] for i in face.vertices];hits=[]
                for a,b in zip(points,points[1:]+points[:1]):
                    if min(a.z,b.z)<level<max(a.z,b.z):
                        q=a+(b-a)*((level-a.z)/(b.z-a.z));hits.append(Vector((q.x,-q.y)))
                if len(hits)==2:segments.append(hits)
            polys=[p for p in nav[field] if p['sourceObject']==o.name]
            outlines=[]
            for p in polys:
                points=[Vector((v['x'],v['z'])) for v in p['vertices']]
                outlines.extend(zip(points,points[1:]+points[:1]))
            check(o.name+f' {level}m fresh slice exists',bool(segments) and bool(outlines))
            error=max([min(distance(p,a,b) for a,b in outlines) for s in segments for p in s]+
                      [min(distance(p,a,b) for a,b in segments) for s in outlines for p in s])
            check(o.name+f' {level}m JSON matches saved mesh edges',error<.0003,error)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(fbx))
    imported=[o for o in bpy.context.scene.objects if o.type=='MESH']
    check('fresh actual FBX mesh names and triangle counts',set(positions)=={o.name for o in imported} and tris(imported)==receipt['triangles'])
    check('all actual FBX material names retained',all(sorted(m.name for m in o.data.materials)==materials[o.name] for o in imported))
    for anchor in anchors:
        o=bpy.data.objects[anchor['id']];x,y,z=anchor['position'];p=o.matrix_world.translation
        check(anchor['id']+' actual FBX compensated world anchor',o.type=='EMPTY' and
              (Vector((-p.x,p.y,p.z))-Vector((x,-z,y+.32))).length<.0001)
    error=0
    for o in imported:
        kd=KDTree(len(o.data.vertices))
        for i,v in enumerate(o.data.vertices):
            p=o.matrix_world@v.co;kd.insert(Vector((-p.x,p.y,p.z)),i)
        kd.balance()
        error=max(error,max(kd.find(p)[2] for p in positions[o.name]))
    check('fresh actual FBX all source vertices within0.1mm',error<.0001,error)
    results.append(dict(map=name,checks=checks,allPassed=True,maxFbxErrorMetres=error,
                        sourceSha256=sha(source),fbxSha256=sha(fbx),navigationSha256=sha(folder/'navigation.json')))
    print('FRESH SOURCE/FBX PASS',name,len(checks),flush=True)
out=dict(scope='Read-only source reopen, closed terrain, independently re-sliced mesh edges and actual FBX reimport; no Unity/native acceptance',
         allPassed=True,maps=results,totalChecks=sum(len(m['checks']) for m in results))
target=ROOT/'Art/Models/Maps'/NAMES[0]/'SeaV2-source-audit.json' if len(NAMES)==1 else ROOT/'Art/Models/Maps/SeaV2-source-audit.json'
target.write_text(json.dumps(out,indent=2))
print('FRESH SOURCE/FBX PASS',len(NAMES),'maps',out['totalChecks'],flush=True)
