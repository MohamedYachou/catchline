"""Early TIER5-102 review only. Read approved geometry; never export to Assets."""
import bpy, math, json
from mathutils import Vector
from pathlib import Path
R=Path(__file__).resolve().parents[2]; O=R/'Art/Models/Tier5DeepLines102';O.mkdir(exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'Art/Models/Tier5Production071/Tier5FisherV1.blend'))
scene=bpy.context.scene
# Existing source contains both storage variants; show one, without changing source.
for ob in bpy.data.objects:
 if ob.parent and ob.parent.name=='RawBuckets':ob.hide_render=True
 if 'Engineer service' in ob.name or 'Service status' in ob.name:ob.hide_render=True
mats={n:bpy.data.materials.get(n) for n in ['M_HullNavy','M_RailIvory','M_DeckWood','M_Rubber','M_SeaTeal','M_Steel','M_SafetyOrange','M_Rope']}
def mat(n,color):
 if mats.get(n):return mats[n]
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);mats[n]=m;return m
mat('M_Rope',(.61,.44,.23))
opt=[]
def cyl(name,a,b,r,material, optional=False):
 a,b=Vector(a),Vector(b);d=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=10,radius=r,depth=d.length,location=(a+b)/2)
 ob=bpy.context.object;ob.name=name;ob.rotation_euler=d.to_track_quat('Z','Y').to_euler();ob.data.materials.append(mats[material])
 if optional:opt.append(ob)
 return ob
def box(n,p,s,m,optional=False):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);ob=bpy.context.object;ob.name=n;ob.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(mats[m]);bev=ob.modifiers.new('Soft manufactured edges','BEVEL');bev.width=.035;bev.segments=2;ob.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL')
 if optional:opt.append(ob)
 return ob
# Four normal rods remain visibly shorter than the new heavy fishing poles.
for i,(x,y) in enumerate([(-1.9,-.35),(1.9,-.35),(1.9,1.1),(1.9,2.55)]):
 s=1 if x>0 else -1;optional=i>1
 cyl('Normal rod '+str(i+1),(x,y,.46),(x+s*.9,y-.12,1.35),.026,'M_DeckWood',optional)
 cyl('Normal rod tip '+str(i+1),(x+s*.9,y-.12,1.35),(x+s*1.28,y-.20,1.57),.014,'M_Rubber',optional)
 cyl('Normal reel '+str(i+1),(x-.07,y,.69),(x+.07,y,.69),.09,'M_Steel',optional)
# Deep rods: compact edge clamps, strong upright butt, arched outward taper,
# visible manual reel/handle and hanging fishing line. No robotic/control cabinet.
for j,y in enumerate([.40,1.82],1):
 box(f'Deep {j} rail clamp',(1.86,y,.44),(.22,.30,.30),'M_HullNavy',True)
 pts=[(1.87,y,.46),(1.98,y,1.48),(2.25,y,2.49),(2.75,y,3.05),(3.34,y,3.14)]
 for k in range(4):cyl(f'Deep {j} tapered pole {k}',pts[k],pts[k+1],[.063,.05,.035,.020][k],'M_RailIvory' if k<2 else 'M_HullNavy',True)
 cyl(f'Deep {j} orange grip',(1.91,y,.78),(1.96,y,1.20),.076,'M_SafetyOrange',True)
 cyl(f'Deep {j} hand reel',(1.94,y-.15,.74),(1.94,y+.15,.74),.18,'M_HullNavy',True)
 for yy in [y-.16,y+.16]:cyl(f'Deep {j} reel flange',(1.94,yy-.015,.74),(1.94,yy+.015,.74),.205,'M_Steel',True)
 cyl(f'Deep {j} crank',(1.94,y-.20,.74),(1.69,y-.20,.86),.028,'M_SafetyOrange',True)
 cyl(f'Deep {j} handle',(1.69,y-.20,.86),(1.69,y-.33,.86),.043,'M_Rubber',True)
 for p in pts[1:]:cyl(f'Deep {j} line guide',p,(p[0],p[1],p[2]+.07),.035,'M_Steel',True)
 cyl(f'Deep {j} hanging fishing line',(3.34,y,3.14),(3.34,y,-.28),.009,'M_Rope',True)
# Preview trap/buoy positions follow fixed approved anchors; no baked crew.
for x in [-2.8,2.8]:
 y=-2.05
 cyl('Fixed trap buoy',(x,y,-.33),(x,y,-.05),.16,'M_SafetyOrange')
 cyl('Buoy neck',(x,y,-.07),(x,y,.14),.045,'M_RailIvory')
 cyl('Fixed buoy rope',(1.9 if x>0 else -1.9,y,.37),(x,y,-.16),.014,'M_Rope')
 box('Crab cage frame',(x,y,-.77),(.64,.5,.40),'M_HullNavy')
 for z in [-.98,-.56]:
  for dy in [-.25,.25]:cyl('Cage bar',(x-.32,y+dy,z),(x+.32,y+dy,z),.022,'M_Steel')
 for xx in [-.32,-.16,0,.16,.32]:
  for dy in [-.25,.25]:cyl('Cage upright',(x+xx,y+dy,-.98),(x+xx,y+dy,-.56),.014,'M_Steel')
# Rotate second net group about its existing geometry centre to the optional side.
net=bpy.data.objects['NetModule2'];net.location=(-2.22,1.0,0);net.rotation_euler.z=-math.pi/2
for ob in net.children:ob.hide_render=True
# Render studio, no image-generation stand-in.
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-1.04));floor=bpy.context.object;floor.name='REVIEW ONLY neutral sea stage';floor.data.materials.append(mat('Review sea',(.085,.32,.36)))
world=bpy.data.worlds.new('Review soft coastal sky');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.56,.70,.76,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;scene.world=world
for loc,energy,size in [((2,-5,10),1400,7),((-5,2,6),900,6)]:
 bpy.ops.object.light_add(type='AREA',location=loc);lamp=bpy.context.object;lamp.data.energy=energy;lamp.data.shape='DISK';lamp.data.size=size;lamp.rotation_euler=(Vector((0,0,0))-lamp.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(11,13,13));cam=bpy.context.object;cam.data.type='ORTHO';scene.camera=cam
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True;scene.render.resolution_x=1440;scene.render.resolution_y=1100;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
def render(name,loc,target,scale):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 if 'plan' in name:cam.rotation_euler.z=-math.pi/2
 scene.render.filepath=str(O/name);bpy.ops.render.render(write_still=True)
render('01-rod-deepline-beauty.png',(11,13,13),(.35,.1,.6),12.8)
render('02-rod-deepline-plan.png',(0,0,18),(0,0,0),12.0)
# Save review scene in primary variant. Variant comparison is render-only state.
bpy.ops.wm.save_as_mainfile(filepath=str(O/'Tier5DeepLines102-preview.blend'))
for ob in opt:ob.hide_render=True
for i in [3,4]:bpy.data.objects['RodHolder_'+str(i)].hide_render=True
for ob in net.children:ob.hide_render=False
render('03-side-net-beauty.png',(11,13,13),(.35,.1,.6),12.8)
render('04-side-net-plan.png',(0,0,18),(0,0,0),12.0)
print('TIER102 PREVIEW COMPLETE')
