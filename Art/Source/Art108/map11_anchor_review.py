import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from map11_kelp_forest import *
def anchors():
    import bpy
    from mathutils import Vector
    import build_sea_v2 as B
    folder=ROOT/'Art/Models/Maps'/NAME
    bpy.ops.wm.open_mainfile(filepath=str(folder/(NAME+'SeaV2.blend')))
    root=bpy.data.objects['Catchline_'+NAME+'SeaV2'];root.scale=(1,-1,1);root.location.z=-.32
    bpy.context.view_layer.update();sc=bpy.context.scene
    results=[]
    for a in L['lifeAnchors']:
        x,y,z=a['position'];hits=[]
        for ob in sc.objects:
            if ob.type!='MESH':continue
            inv=ob.matrix_world.inverted();origin=inv@Vector((x,z,100));direction=inv.to_3x3()@Vector((0,0,-1))
            hit,p,normal,face=ob.ray_cast(origin,direction)
            if hit:hits.append((float((ob.matrix_world@p).z),ob.name))
        top=max(hits,default=(-100,''))
        is_water=not a['id'].startswith('PostGulls')
        passed=top[0]<y+.09 if is_water else abs(top[0]-y)<.015
        results.append(dict(anchor=a['id'],position=a['position'],surface=top,passed=passed))
    (folder/'SeaV2-anchor-audit.json').write_text(json.dumps(dict(allPassed=all(r['passed'] for r in results),anchors=results),indent=2))
    assert all(r['passed'] for r in results),results
    B.setup_render(sc)
    d=bpy.data.lights.new('Anchor sun','SUN');o=bpy.data.objects.new('Anchor sun',d);sc.collection.objects.link(o);d.energy=2;o.rotation_euler=(.4,-.3,-.5)
    d=bpy.data.cameras.new('Anchor camera');d.type='ORTHO';cam=bpy.data.objects.new('Anchor camera',d);sc.collection.objects.link(cam);sc.camera=cam
    B.K.box('REVIEW water',(0,0,-.38),(800,800,.12),'M_SeaTeal',0)
    for a in L['lifeAnchors']:
        x,y,z=a['position'];target=Vector((x,z,y));marker=B.K.cyl('REVIEW marker',(x,z,y+.25),.12,.5,'M_SafetyOrange',8)
        cam.location=target+Vector((8,-12,9));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();d.ortho_scale=6 if not a['id'].startswith('PostGulls') else 3
        sc.render.filepath=str(folder/('SeaV2-anchor-'+a['id']+'.png'));bpy.ops.render.render(write_still=True);bpy.data.objects.remove(marker,do_unlink=True)
    print('MAP11 ANCHORS PASS',flush=True)


anchors()
