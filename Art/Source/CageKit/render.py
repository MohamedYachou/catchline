"""Five consistent studio angles plus independently rendered integration states."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build as B
def material(name,hex,rough=.7):return B.H.material(name,hex,rough)
def stage():
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True
    try:
        p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
        for d in p.devices:d.use=d.type=='OPTIX'
        sc.cycles.device='GPU'
    except Exception:sc.cycles.device='CPU'
    sc.render.threads_mode='FIXED';sc.render.threads=6
    sc.world=bpy.data.worlds.new('ReviewWorld');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.35,.40,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.65
    sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
    for name,loc,energy,size,col in [('Key',(-2,1,4),350,3,(1,.88,.72)),('Fill',(2,-1,3),180,3,(.72,.86,1))]:
        d=bpy.data.lights.new(name,'AREA');d.energy=energy;d.shape='DISK';d.size=size;d.color=col
        o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',d);sc.collection.objects.link(cam);sc.camera=cam
    return sc,cam
def plane(z,size=200,hex='#D9DFD6'):
    bpy.ops.mesh.primitive_plane_add(size=size,location=(0,0,z));o=bpy.context.object;o.name='ReviewGround';o.data.materials.append(material('ReviewGroundMat',hex));return o
def look(cam,point,direction,scale=1):
    cam.location=Vector(point)+Vector(direction).normalized()*4;cam.rotation_euler=(Vector(point)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=scale
def fitted(sc,cam,pts,d):
    c=Vector(tuple((min(p[i] for p in pts)+max(p[i] for p in pts))*.5 for i in range(3)));look(cam,c,d)
    b=cam.rotation_euler.to_matrix();u=b@Vector((1,0,0));v=b@Vector((0,1,0));w=max(p.dot(u) for p in pts)-min(p.dot(u) for p in pts);h=max(p.dot(v) for p in pts)-min(p.dot(v) for p in pts)
    cam.data.ortho_scale=max(w,h*sc.render.resolution_x/sc.render.resolution_y)*1.22
def render(sc,path):
    path.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
def individual(name):
    bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' for v in o.data.vertices]
    sc,cam=stage();plane(-.001);sc.render.resolution_x=1000;sc.render.resolution_y=800;rows=[]
    for vn,d in [('three-quarter',(1,-1,1)),('front',(0,-1,.06)),('right',(1,0,.06)),('back',(0,1,.06)),('top',(0,0,1))]:
        fitted(sc,cam,pts,d);p=B.O/'renders'/name/(vn+'.png');render(sc,p);rows.append({'file':p.relative_to(B.O).as_posix(),'view':vn,'size':[1000,800]})
    if name=='CrabCage':
        bpy.data.objects['Lid'].rotation_euler.x=math.radians(-90);bpy.context.view_layer.update();pts=[o.matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('Review') for v in o.data.vertices];fitted(sc,cam,pts,(1,-1,1));p=B.O/'renders'/name/'lid-open.png';render(sc,p);rows.append({'file':p.relative_to(B.O).as_posix(),'view':'negative90degree local-X hinge open','size':[1000,800]})
    (B.O/'renders'/(name+'.json')).write_text(json.dumps(rows,indent=2)+'\n');print('CAGE RENDERS COMPLETE',name,len(rows),flush=True)
if __name__=='__main__':individual(sys.argv[sys.argv.index('--')+1])
