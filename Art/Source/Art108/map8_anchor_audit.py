"""Independent surface/overhead test for Claude's MAP8 buried-anchor fix."""
import bpy, json, math, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[3]
ART=ROOT/'Art/Models/Maps/GullLighthouseRock'
nav=json.loads((ART/'navigation.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ART/'GullLighthouseRockSeaV2.blend'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
vertices=[];faces=[]
for o in meshes:
    offset=len(vertices);vertices += [o.matrix_world@v.co for v in o.data.vertices]
    faces += [[offset+i for i in p.vertices] for p in o.data.polygons]
tree=BVHTree.FromPolygons(vertices,faces)
checks=[]
for a in nav['lifeAnchors'][:3]:
    x,y,z=a['position'];top=y+.32
    # Group's rotated 2.64 x 1.43m envelope, plus the separate 0.66m bird
    # at runtime offset (1.65,-.77). All samples must reach the shelf top
    # from the sky, with no intervening body rock, and never float.
    samples=[(0,0),(1.65,-.77),(1.95,-.77),(1.65,-1.07)]
    samples += [(1.52*math.cos(t*math.pi/12),1.52*math.sin(t*math.pi/12)) for t in range(24)]
    heights=[]
    for dx,dz in samples:
        hit=tree.ray_cast(Vector((x+dx,-z-dz,50)),Vector((0,0,-1)))
        assert hit[0] is not None,(a['id'],'no visible surface',dx,dz)
        height=hit[0].z;heights.append(height)
        assert abs(height-top)<.0001,(a['id'],'buried or floating footprint',dx,dz,height,top)
    checks.append(dict(anchor=a['id'],worldPosition=a['position'],sourceTop=top,samples=len(samples),maxSurfaceError=max(abs(h-top) for h in heights),passed=True))
# The fix moves only elevated shelves/empties; all real waterline and -1m
# obstructions, grounds, camera/border data must remain identical.
before=ROOT/'docs/screens/map8-lighthouse-rock-1/safety-source/Assets/Art/Models/Environment/GullLighthouseRock/navigation.json'
old=json.loads(before.read_text())
assert {k:v for k,v in nav.items() if k!='lifeAnchors'}=={k:v for k,v in old.items() if k!='lifeAnchors'},'navigation geometry changed'
assert nav['lifeAnchors'][3:6]==old['lifeAnchors'][3:6],'tide-race/lamp anchors changed'
bx,_,bz=nav['lifeAnchors'][6]['position']; distances=[]
for island in nav['islands']:
    pts=[(v['x'],v['z']) for v in island['vertices']];inside=False
    for (ax,az),(cx,cz) in zip(pts,pts[1:]+pts[:1]):
        if (az>bz)!=(cz>bz) and bx<(cx-ax)*(bz-az)/(cz-az)+ax:inside=not inside
        dx,dz=cx-ax,cz-az;t=max(0,min(1,((bx-ax)*dx+(bz-az)*dz)/(dx*dx+dz*dz)))
        distances.append(math.hypot(bx-ax-t*dx,bz-az-t*dz))
    assert not inside,'buoy inside waterline rock'
assert min(distances)>1.3,'buoy too close to rock'
out=dict(allPassed=True,checks=checks,unchangedNavigationExceptLifeAnchors=True,buoyWorldPosition=nav['lifeAnchors'][6]['position'],buoyRockClearance=min(distances),sourceSha256=hashlib.sha256((ART/'GullLighthouseRockSeaV2.blend').read_bytes()).hexdigest(),limits='Source vertical surface and buoy-waterline checks; actual dressed native perch renders required separately.')
(ART/'SeaV2-anchor-fix-audit.json').write_text(json.dumps(out,indent=2))
print('MAP8 ANCHOR SURFACES PASS',len(checks),'anchors',sum(c['samples'] for c in checks),'samples; navigation geometry unchanged')
