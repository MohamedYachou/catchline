"""Five true orthographic views, matched deck/rod camera pairs, action samples.
All stage geometry/lights excluded from the individual exports.
"""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B

def mat(n,c,r=.75):return B.H.material(n,c,r)
def stage():
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True
    try:
        p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
        for d in p.devices:d.use=d.type=='OPTIX'
        sc.cycles.device='GPU'
    except Exception:sc.cycles.device='CPU'
    sc.render.threads_mode='FIXED';sc.render.threads=6
    sc.world=bpy.data.worlds.new('ReviewWorld');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.26,.34,.40,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.7
    sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.render.image_settings.file_format='PNG';sc.render.resolution_percentage=100
    # Distant soft sources light wide reef and small seal consistently.
    for n,loc,power,size,col in [('WarmKey',(-4,-5,7),1350,5,(1,.88,.72)),('CoolFill',(5,1,6),750,5,(.72,.86,1))]:
        d=bpy.data.lights.new(n,'AREA');d.energy=power;d.shape='DISK';d.size=size;d.color=col;o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('ReviewCamera');cam=bpy.data.objects.new('ReviewCamera',d);sc.collection.objects.link(cam);sc.camera=cam
    return sc,cam

def plane(z,col):
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,z));o=bpy.context.object;o.name='ReviewGround';o.data.materials.append(mat('ReviewGroundMat',col));return o

def look(cam,point,direction):
    cam.location=Vector(point)+Vector(direction).normalized()*8;cam.rotation_euler=(Vector(point)-cam.location).to_track_quat('-Z','Y').to_euler()

def fitted(sc,cam,pts,d,scale=None):
    c=Vector(tuple((min(p[i] for p in pts)+max(p[i] for p in pts))*.5 for i in range(3)));look(cam,c,d);cam.data.type='ORTHO'
    b=cam.rotation_euler.to_matrix();u=b@Vector((1,0,0));v=b@Vector((0,1,0));w=max(p.dot(u) for p in pts)-min(p.dot(u) for p in pts);h=max(p.dot(v) for p in pts)-min(p.dot(v) for p in pts)
    cam.data.ortho_scale=scale or max(w,h*sc.render.resolution_x/sc.render.resolution_y)*1.25

def render(sc,path):path.parent.mkdir(parents=True,exist_ok=True);sc.render.filepath=str(path);bpy.ops.render.render(write_still=True)
def pts():
    bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
    return [o.evaluated_get(dg).matrix_world@v.co for o in bpy.context.scene.objects if o.type=='MESH' and not o.name.startswith('Review') for v in o.evaluated_get(dg).data.vertices]

def run(name,mode='all'):
    bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));sc,cam=stage();water=name.startswith('Reef') or name in ('SealSwimHead','CrabBuoySet')
    ground=plane(-.012,'#1C6E7E' if water else '#D7DDD3');points=pts();rows=[];out=B.O/'renders'/name
    def save(label,size,extra=None):
        sc.render.resolution_x,sc.render.resolution_y=size;p=out/(label+'.png');render(sc,p);rows.append({'file':p.relative_to(B.O).as_posix(),'view':label,'size':size,**(extra or {})})
    if mode in ('all','studio'):
        sc.render.resolution_x=720;sc.render.resolution_y=600
        for vn,d in [('three-quarter',(1,-1,1)),('front',(0,-1,.05)),('right',(1,0,.05)),('back',(0,1,.05)),('top',(0,0,1))]:
            fitted(sc,cam,points,d);save(vn,(720,600))
    if mode in ('all','cameras'):
        # Honest10m horizontal span at both aspects,45deg down; camera centre at asset centre.
        ground.data.materials[0]=mat('ReviewSea','#1C6E7E')
        centre=Vector(tuple((min(p[i] for p in points)+max(p[i] for p in points))*.5 for i in range(3)))
        cam.data.type='ORTHO';look(cam,centre,(.574,-.819,1));cam.data.ortho_scale=10
        for label,size in [('deck-1440',(1440,900)),('deck-844',(844,390))]:save(label,size,{'projection':'orthographic','down_degrees':45,'horizontal_span_m':10})
        #1.7m eye with52deg vertical FOV, looking30deg downward. Subject at sightline intersection.
        cam.data.type='PERSP';cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=24;cam.data.lens=24/(2*math.tan(math.radians(26)))
        eye=1.7;targetz=centre.z;distance=(eye-targetz)/math.tan(math.radians(30))
        # Wide rock/reef pieces need a longer viewing distance, while eye and pitch stay exact.
        halfwidth=max(abs(p.x-centre.x) for p in points);halfdepth=max(abs(p.y-centre.y) for p in points)
        distance=max(distance,halfwidth/(math.tan(math.radians(26))*1.6*.82)+halfdepth)
        cam.location=(centre.x,centre.y-distance,eye)
        direction=Vector((0,math.cos(math.radians(30)),-math.sin(math.radians(30))));cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
        for label,size in [('rod-1440',(1440,900)),('rod-844',(844,390))]:save(label,size,{'projection':'perspective','eye_height_m':1.7,'down_degrees':30,'vertical_fov_degrees':52,'horizontal_distance_m':distance})
    if name=='Seal' and mode in ('all','actions'):
        rig=bpy.data.objects['SealRig'];cam.data.type='ORTHO';look(cam,(0,-.7,.15),(1,-1,1));cam.data.ortho_scale=3.9
        for action,end in [('Bask',121),('Look',91),('Slide',37)]:
            rig.animation_data.action=bpy.data.actions[action]
            for i,f in enumerate([1,1+(end-1)//4,1+(end-1)//2,1+3*(end-1)//4,end]):
                sc.frame_set(f);save('action-'+action+'-'+str(i),(480,360),{'action':action,'frame':f,'seconds':(f-1)/30})
        # Reset stage: show the slide above dark review water at final frame for intended visibility.
    manifest=B.O/'renders'/(name+'.json')
    if manifest.exists() and mode!='all':
        old=json.loads(manifest.read_text());labels={a['view'] for a in rows};rows=[a for a in old if a['view'] not in labels]+rows
    manifest.write_text(json.dumps(rows,indent=2)+'\n');print('SKERRIES RENDERS',name,len(rows),flush=True)
if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:];run(args[0],args[1] if len(args)>1 else 'all')
