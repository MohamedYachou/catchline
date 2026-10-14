"""Blender 5.2: stage existing assets for UI comps, never save changes to models.
Run in background mode; writes only two UI background PNGs. No Unity access.
"""
from pathlib import Path
import bpy, math, random, sys
from mathutils import Vector
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
import build_gull_harbour as K
OUT=ROOT/'Art/Source/UI'

def append(name,where=(0,0,0),yaw=0,scale=1):
    group=K.ASSETS[name][0]
    p=K.OUT/group/(name+'.blend')
    with bpy.data.libraries.load(str(p),link=False) as (src,dst):
        dst.collections=['ASSET_EXPORT']
    coll=dst.collections[0]; bpy.context.scene.collection.children.link(coll)
    root=next(o for o in coll.objects if o.type=='EMPTY')
    root.location=where; root.rotation_euler.z=yaw; root.scale=(scale,)*3
    return root,coll

def material(name,col): return K.B.material(name,col)
def geom(g,name): return g.object(name,None,bpy.context.scene.collection)
def scene(harbour=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene; sc.unit_settings.system='METRIC'
    K.B.MATERIALS.clear(); K.B.MATERIALS.update({n:material(n,c) for n,c in K.B.PALETTE.items()})
    append('Rowboat')
    append('Cooler',(.55,-.85,.02)); append('BaitBucket',(-.57,-.44,.02)); append('LunchTin',(.57,.53,.02))
    cap_pos=(-.35,-.28,0)
    # Pose a temporary copy for presentation only; never write CrewBody.blend.
    crew,coll=append('CrewBody',cap_pos,yaw=-.25)
    body=next(o for o in coll.objects if o.type=='MESH' and 'CrewBody' in o.name)
    for v in body.data.vertices:
        if abs(v.co.x)>.16 and .39<v.co.z<.68:
            side=1 if v.co.x>0 else -1
            shoulder=Vector((side*.165,0,.57)); p=v.co-shoulder
            a=side*math.radians(58)
            v.co=shoulder+Vector((math.cos(a)*p.x+math.sin(a)*p.z,p.y,-math.sin(a)*p.x+math.cos(a)*p.z))
    append('CaptainCap',(cap_pos[0],cap_pos[1],.91),yaw=-.25)
    append('FishingRod',(-1.115,-1,.50),yaw=.2)
    rod,_=append('FishingRod',(-1.115,1,.50),yaw=.2)
    rod.rotation_euler.y=-.55
    append('Mackerel',(.05,-.88,.018),yaw=1.1)
    sea=K.G(); sea.box((0,0,-.31),(200,200,.04),'M_SeaTeal'); geom(sea,'Sea')
    rng=random.Random(25)
    # Broad short wave strokes, restrained and physically in the plane.
    for i in range(80):
        x=rng.uniform(-12,12); y=rng.uniform(-12,12)
        if abs(x)<2.7 and abs(y)<2.7: continue
        g=K.G(); g.tube([(x,y,-.281),(x+.3,y+.02,-.281),(x+.68,y,-.281)],[.012]*3,4,'M_RailIvory' if i%5==0 else 'M_HullBlue'); geom(g,'WaterAccent')
    kelp_positions=[(-6,3.4),(-4.3,5.6),(-2.6,7),(0,5.3),(2,6.8),(4,4.8),(6,3.2),(7.6,6.8)]
    for i,(x,y) in enumerate(kelp_positions):
        append('KelpPatch',(x,y,-.27),yaw=i*.7)
    if harbour:
        for x in (-6,-2,2,6): append('Quay4m',(x,3.8,.1))
        append('HouseA',(-3,6,.1),yaw=.05); append('HouseB',(1,6,.1))
        append('Lighthouse',(-7,6,.1),scale=.7)
        for x in (-5,-1,3): append('Bollard',(x,3.2,.1)); append('LampPost',(x-1,4.2,.1))
        for i in range(9): append('BreakwaterRock'+chr(65+i%3),(-7+i*1.8,7.8,-.32),yaw=rng.random()*6)
    else:
        for i in range(4): append('BreakwaterRock'+chr(65+i%3),(5+i*1.15,5+i*.2,-.3),yaw=i)
    world=bpy.data.worlds.new('Soft sea ambience'); world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=K.B.linear_colour('#C2DDD9')
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6; sc.world=world
    for name,loc,power,size in [('Warm upper left',(-6,-4,10),1700,7),('Cool fill',(7,3,8),650,9)]:
        data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.shape='DISK'; data.size=size
        o=bpy.data.objects.new(name,data); sc.collection.objects.link(o); o.location=loc
        o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    data=bpy.data.cameras.new('Fixed gameplay orthographic'); data.type='ORTHO'; data.ortho_scale=13.5
    cam=bpy.data.objects.new('Camera',data); sc.collection.objects.link(cam)
    yaw=math.radians(35); elev=math.radians(45)
    target=Vector((0,.9,-.5)) if not harbour else Vector((.7,1.8,-.4))
    cam.location=target+Vector((math.sin(yaw)*math.cos(elev),-math.cos(yaw)*math.cos(elev),math.sin(elev)))*18
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
    if harbour: data.ortho_scale=17
    sc.render.engine='CYCLES'; sc.cycles.samples=32; sc.cycles.use_denoising=True
    sc.render.resolution_x=1920; sc.render.resolution_y=1080; sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG'; sc.render.image_settings.color_mode='RGB'
    sc.view_settings.view_transform='Standard'; sc.view_settings.look='None'
    sc.render.filepath=str(OUT/('harbour-background.png' if harbour else 'fishing-background.png'))
    bpy.ops.render.render(write_still=True)

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    scene(False); scene(True)
