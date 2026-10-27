"""Fresh FBX reimport and geometry/pivot/local-axis checks; no Unity writes."""
import sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build as B
sys.path.insert(0,str(B.R/'Art/Source/HarbourV2'))
import audit as A
def geometry():
    bpy.context.view_layer.update();rows={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH':continue
        o.data.calc_loop_triangles()
        rows[o.name]={'vertices':[tuple(o.matrix_world@v.co) for v in o.data.vertices],'triangles':[tuple(t.vertices) for t in o.data.loop_triangles],'faces':[tuple(p.vertices) for p in o.data.polygons]}
    return rows
def run(name):
    row=json.loads((B.O/'metrics'/(name+'.json')).read_text())
    bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));src=B.snapshot();geo=geometry()
    assert src['triangles']<1500 and abs(src['bounds'][0][2])<1e-6
    assert all(abs(c)<1e-6 for c in bpy.data.objects[name].location)
    canon=row['contract'].get('canonical')
    if canon:
        assert B.mesh_hash(bpy.data.objects['CrabBody'])==canon['geometry_sha256']
        with bpy.data.libraries.load(str(B.R/canon['path']),link=False) as (a,b):b.objects=['CrabBody']
        assert B.mesh_hash(b.objects[0])==canon['geometry_sha256'];bpy.data.objects.remove(b.objects[0],do_unlink=True)
        assert B.sha(B.R/canon['path'])==canon['sha256']
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(B.O/(name+'.fbx')))
    imp=B.snapshot();proof=A.same_geometry(geo,geometry())
    assert imp['triangles']==src['triangles'] and imp['parents']==src['parents']
    assert imp['materials']==src['materials']
    assert all(abs(v-1)<2e-5 for o in bpy.context.scene.objects for v in o.scale),imp['objects']
    axis={}
    for child in ('Lid','Bridle','Sheave','LegalMark'):
        if child not in row['contract']:continue
        o=bpy.data.objects[child];target=Vector(row['contract'][child]['pivot'])
        error=(o.matrix_world.translation-target).length;assert error<2e-5,(child,error)
        x=o.matrix_world.to_3x3()@Vector((1,0,0));assert (x-Vector((1,0,0))).length<2e-5,(child,list(x),imp['objects'])
        # Explicitly move the integration control, not merely inspect its rest pose.
        before=[o.matrix_world@v.co for v in o.data.vertices]
        if child=='Lid':o.rotation_euler.x=math.radians(-90)
        elif child=='Sheave':o.rotation_euler.x=math.pi/2
        elif child=='LegalMark':o.location.x=.05
        bpy.context.view_layer.update();after=[o.matrix_world@v.co for v in o.data.vertices]
        if child in ('Lid','Sheave'):
            assert max(abs(a.x-b.x) for a,b in zip(before,after))<2e-5
            assert max((a-b).length for a,b in zip(before,after))>.01
        if child=='Lid':assert max(p.z for p in after)>max(p.z for p in before)+.1
        if child=='LegalMark':assert max(abs(a.y-b.y)+abs(a.z-b.z) for a,b in zip(before,after))<2e-5
        axis[child]={'pivot_error_metres':error,'local_x_world':list(x),'control_test':'PASS'}
    for ext in ('blend','fbx'):assert B.sha(B.O/(name+'.'+ext))==row['sha256'][ext]
    row.update(round_trip={'result':'PASS','geometry':proof,'source':src,'imported':imp,'controls':axis},status='source/actualFBX PASS; visual review separate')
    (B.O/'metrics'/(name+'.json')).write_text(json.dumps(row,indent=2)+'\n');print('CAGE AUDIT PASS',name,imp['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
