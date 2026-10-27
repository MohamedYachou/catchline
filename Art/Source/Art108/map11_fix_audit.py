"""Independent before/after sand-bed and unchanged-terrain audit in Blender."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'Art/Models/Maps/GullKelpForest'
before=ROOT.parent/'Catchline-sim/Backups/map11-fix-before/GullKelpForest'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def geometry():
    return {o.name:([list(o.matrix_world@v.co) for v in o.data.vertices],
                    [list(p.vertices) for p in o.data.polygons])
            for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith('Terrain_')}
bpy.ops.wm.open_mainfile(filepath=str(before/'GullKelpForestSeaV2.blend'))
old=geometry()
bpy.ops.wm.open_mainfile(filepath=str(folder/'GullKelpForestSeaV2.blend'))
checks=[]
def check(label,ok,detail=None):
    checks.append(dict(check=label,passed=bool(ok),detail=detail))
    assert ok,(label,detail)
check('all accepted terrain/post meshes unchanged',old==geometry())
check('navigation bytes unchanged',sha(before/'navigation.json')==sha(folder/'navigation.json'))
bed=bpy.data.objects['ConnectedBathymetry']
nav=json.loads((folder/'navigation.json').read_text())
check('all connected bed vertices below true shallow slice',max(v.co.z for v in bed.data.vertices)<-1.05)
for g in nav['grounds']:
    x,z=g['centre']['x'],g['centre']['z']
    for r in (0,6,10):
        xx=x+math.cos(math.radians(35))*r;zz=z-math.sin(math.radians(35))*r
        hit,p,normal,face=bed.ray_cast(Vector((xx,-zz,10)),Vector((0,0,-1)))
        check(g['id']+' bed ray '+str(r)+'m',hit,float(-p.z))
        if r==0:check(g['id']+' actual anchor pocket depth retained',abs(-p.z-g['nominalDepth'])<.2,float(-p.z))
        else:check(g['id']+' raised shelf visible beside hull',1.05<-p.z<1.5,float(-p.z))
for i in range(1,5):
    check('localized cluster KelpSway_'+str(i),bpy.data.objects.get('RootedForestPatch_KelpSway_'+str(i)) is not None)
result=dict(allPassed=True,checks=checks,sourceSha256=sha(folder/'GullKelpForestSeaV2.blend'),
            limits='Source geometry and vertical ray audit; production-water visibility requires native frames.')
(folder/'sand-fix-audit.json').write_text(json.dumps(result,indent=2))
print('MAP11 FIX GEOMETRY PASS',len(checks))
