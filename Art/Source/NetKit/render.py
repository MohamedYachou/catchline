"""Five separately rendered angles for each model and both Bunt states."""
import sys,json,math
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build as B
def stage():
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True
    try:
        pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='OPTIX';pref.get_devices()
        for d in pref.devices:d.use=d.type=='OPTIX'
        sc.cycles.device='GPU'
    except Exception:sc.cycles.device='CPU'
    sc.render.threads_mode='FIXED';sc.render.threads=6
    sc.world=bpy.data.worlds.new('ReviewWorld');sc.world.use_nodes=True
    sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.28,.36,.40,1)
    sc.world.node_tree.nodes['Background'].inputs[1].default_value=.7
    sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
    sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
    for n,p,e,size,col in [('ReviewKey',(-3,2,5),450,4,(1,.89,.75)),('ReviewFill',(3,-2,3),240,3,(.75,.87,1))]:
        d=bpy.data.lights.new(n,'AREA');d.energy=e;d.shape='DISK';d.size=size;d.color=col
        o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=p
        o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',d);sc.collection.objects.link(cam);sc.camera=cam
    return sc,cam
def plane(z,colour='#D7DDD3'):
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,z));o=bpy.context.object;o.name='ReviewGround'
    o.data.materials.append(B.H.material('ReviewGroundMat',colour,.85));return o
def points():
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    return [o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith('Review') for v in o.evaluated_get(dg).data.vertices]
def look(cam,point,where):
    cam.location=Vector(point)+Vector(where).normalized()*6
    cam.rotation_euler=(Vector(point)-cam.location).to_track_quat('-Z','Y').to_euler()
def fitted(sc,cam,pts,d):
    centre=Vector(tuple((min(p[i] for p in pts)+max(p[i] for p in pts))*.5 for i in range(3)))
    look(cam,centre,d);cam.data.type='ORTHO'
    basis=cam.rotation_euler.to_matrix();u=basis@Vector((1,0,0));v=basis@Vector((0,1,0))
    w=max(p.dot(u) for p in pts)-min(p.dot(u) for p in pts);h=max(p.dot(v) for p in pts)-min(p.dot(v) for p in pts)
    # Re-centre in camera space: asymmetric oblique bags need this, otherwise
    # a world-AABB centre can clip a float despite an adequate frame width.
    shift=u*((max(p.dot(u) for p in pts)+min(p.dot(u) for p in pts))*.5-centre.dot(u))
    shift+=v*((max(p.dot(v) for p in pts)+min(p.dot(v) for p in pts))*.5-centre.dot(v))
    look(cam,centre+shift,d)
    cam.data.ortho_scale=max(w,h*sc.render.resolution_x/sc.render.resolution_y)*1.25
def render(sc,path):
    path.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
def run(name):
    bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));sc,cam=stage()
    sc.render.resolution_x=1000;sc.render.resolution_y=800
    rows=[]
    if name=='NetBunt':subjects=[('NetBunt-Slack',0),('NetBunt-Taut',1)]
    else:subjects=[('NetPanel',None),('NetHeap',None)]
    # Camera directions are Blender-space. Front is Unity -Z / Blender +Y.
    angles=[('three-quarter',(1,1,1)),('front',(0,1,.04)),('right',(1,0,.08)),('back',(0,-1,.04)),('top',(0,0,1))]
    for label,state in subjects:
        if name=='NetBunt':bpy.data.objects['Bunt'].data.shape_keys.key_blocks['Taut'].value=state
        else:
            for k in ('NetPanel','NetHeap'):
                bpy.data.objects[k].hide_render=k!=label
        pts=points();ground=plane(min(p.z for p in pts)-.012)
        for view,d in angles:
            fitted(sc,cam,pts,d);p=B.O/'renders'/label/(view+'.png')
            selected=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--only-view=')),None)
            if selected is None or view==selected:render(sc,p)
            rows.append({'file':p.relative_to(B.O).as_posix(),'subject':label,'view':view,'size':[1000,800]})
        bpy.data.objects.remove(ground,do_unlink=True)
    (B.O/'renders'/(name+'.json')).write_text(json.dumps(rows,indent=2)+'\n')
    print('NET RENDERS',name,len(rows),flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
