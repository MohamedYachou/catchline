"""Material-only follow-up: compare all geometry and nav to verified B."""
import bpy, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'Art/Models/Maps/GullKelpForest'
before=ROOT.parent/'Catchline-sim/Backups/map11-material-before'
def geometry():
    return {o.name:dict(matrix=[list(row) for row in o.matrix_world],
        vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons])
        for o in bpy.context.scene.objects if o.type=='MESH'}
def anchors():
    return {o.name:[list(row) for row in o.matrix_world] for o in bpy.context.scene.objects if o.type=='EMPTY'}
bpy.ops.wm.open_mainfile(filepath=str(before/'GullKelpForestSeaV2.blend'))
old,empties=geometry(),anchors()
bpy.ops.wm.open_mainfile(filepath=str(folder/'GullKelpForestSeaV2.blend'))
assert old==geometry(),'geometry drift'
assert empties==anchors(),'anchor drift'
assert (before/'navigation.json').read_bytes()==(folder/'navigation.json').read_bytes(),'nav drift'
bed=bpy.data.objects['ConnectedBathymetry']
counts={m.name:sum(p.material_index==i for p in bed.data.polygons) for i,m in enumerate(bed.data.materials)}
assert all(n>0 for n in counts.values()) and len(counts)==2,counts
result=dict(allPassed=True,allMeshGeometryAndTransformsUnchanged=True,allEmptyTransformsUnchanged=True,
    navigationBytesUnchanged=True,meshCount=len(old),bedMaterialFaces=counts,
    sourceSha256=hashlib.sha256((folder/'GullKelpForestSeaV2.blend').read_bytes()).hexdigest(),
    limits='Material-only delta from verified B geometry; native visual review is separate.')
(folder/'sand-material-audit.json').write_text(json.dumps(result,indent=2))
print('MAP11 MATERIAL-ONLY PARITY PASS',len(old),counts)
