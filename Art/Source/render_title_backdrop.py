"""Task 05.2: existing model stage, golden-hour ortho. Never saves model files.
Blender 5.2 --background --factory-startup --python-exit-code 1 --python <this>.
"""
from pathlib import Path
import sys,math,random
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import render_ui_backgrounds as R
import build_task04 as A
A.register(); R.K.ASSETS.update(A.K.ASSETS)
K=R.K; ROOT=R.ROOT
bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene
K.B.MATERIALS.clear(); K.B.MATERIALS.update({n:R.material(n,c) for n,c in K.B.PALETTE.items()})
sea=K.G(); sea.box((0,0,-.38),(180,180,.08),'M_SeaTeal');R.geom(sea,'Sea')
# Town runs behind the quay; the broad lower-left bay remains empty for UI.
for x in (-8,-4,0,4,8): R.append('Quay4m',(x,4,.10))
shops=['FishMarket','HarbourMaster','CrewOffice','Chandlery','Supplies']
for i,(x,shop) in enumerate(zip((-8,-4,0,4,8),shops)):
    R.append('HouseA' if i%2==0 else 'HouseB',(x,7,.10))
    R.append('ShopFront_'+shop,(x,5.58,.10),yaw=math.pi)
    R.append('LampPost',(x-1.5,3.8,.10))
    R.append('Bollard',(x+.9,3.35,.10))
R.append('Lighthouse',(12,7,.10),scale=.85)
for i in range(9):R.append('BreakwaterRock'+chr(65+i%3),(10+i*.65,5+i*.65,-.35),yaw=i*.8)
# Source bow is -Y. At yaw zero its projection is toward 8 o'clock.
yaw=0
boat=(5,1,0)
R.append('Rowboat',boat,yaw=yaw)
R.append('Cooler',(5.25,1.35,.02),yaw=yaw)
R.append('CrewBody',(5,1,.02),yaw=yaw,scale=1)
R.append('CaptainCap',(5,1,.93),yaw=yaw)
R.append('FishingRod',(4.3,1,.5),yaw=-.3)
R.append('CrateStack',(8,3.9,.1)); R.append('Barrel',(-7,3.9,.1))
rng=random.Random(52)
for i in range(65):
    x=rng.uniform(-17,18);y=rng.uniform(-10,11)
    if -10<x<10 and 2<y<9:continue
    g=K.G();g.tube([(x,y,-.33),(x+.35,y+.04,-.33),(x+.8,y,-.33)],[.012]*3,4,'M_RailIvory' if i%5==0 else 'M_HullBlue');R.geom(g,'BroadWaterAccent')
world=bpy.data.worlds.new('Warm maritime fill');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=K.B.linear_colour('#D4DDD5')
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65;sc.world=world
for name,loc,power,size,color in [('Golden hour',(-10,-5,14),4200,10,'#FFE0AF'),('Sea fill',(9,-2,11),1800,12,'#C2DDD9')]:
    d=bpy.data.lights.new(name,'AREA');d.energy=power;d.size=size;d.color=K.B.linear_colour(color)[:3]
    o=bpy.data.objects.new(name,d);sc.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((1,4,0))-o.location).to_track_quat('-Z','Y').to_euler()
d=bpy.data.cameras.new('45 down 35 yaw');d.type='ORTHO';d.ortho_scale=33
cam=bpy.data.objects.new('Camera',d);sc.collection.objects.link(cam)
target=Vector((-.5,2,.7));a=math.radians(35);e=math.radians(45)
cam.location=target+Vector((math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))*40
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();sc.camera=cam
sc.render.engine='CYCLES';sc.cycles.samples=32;sc.cycles.use_denoising=True
sc.render.resolution_x=1920;sc.render.resolution_y=1080;sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA'
sc.view_settings.view_transform='Standard';sc.view_settings.look='None'
sc.render.filepath=str(ROOT/'Art/Source/UI/Pass2/title-backdrop-render.png')
bpy.ops.render.render(write_still=True)
