"""Catchline stage-1 V2 painted kit. Run with Blender 5.2; all outputs beside this file.
No third-party/generated bitmap used: native meshes, constant PBR materials, original crew.
Blender X right, Y rear, Z up; 1 unit = 1 metre. Presentation never exported.
"""
import bpy, math, json, random, sys, hashlib
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent; R=O.parents[3]; (O/'renders').mkdir(exist_ok=True)
random.seed(76); bpy.ops.wm.read_factory_settings(use_empty=True)
sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
COL={};cur=None;roots={}
def linear(x):return x/12.92 if x<.04045 else ((x+.055)/1.055)**2.4
def mat(name,h,rough=.6,metal=0):
 m=bpy.data.materials.new(name);rgb=[linear(int(h[i:i+2],16)/255) for i in (0,2,4)];m.diffuse_color=(*rgb,1);m.use_nodes=True;b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=m.diffuse_color;b.inputs['Roughness'].default_value=rough;b.inputs['Metallic'].default_value=metal;COL[name]=m;return m
navy=mat('Enamel_Navy_173F57','173F57',.32);blue=mat('Enamel_Lit_2A6685','2A6685',.34);ivory=mat('Ivory_F3F0DC','F3F0DC',.4);cream=mat('Plaster_F0DFC2','F0DFC2',.9);wood=mat('Honey_C58B50','C58B50',.45);goldwood=mat('Wood_DFB77A','DFB77A',.52);darkwood=mat('Recess_8C5A36','8C5A36',.65);steel=mat('Steel_8FA6AC','8FA6AC',.28,.55);dark=mat('Rubber_28343B','28343B',.67);brass=mat('Brass_C99B4A','C99B4A',.3,.6);orange=mat('Orange_E36A35','E36A35',.4);teal=mat('Cushion_168F9F','168F9F',.75);leaf=mat('Leaf_657745','657745',.85);tilem=[mat('Tile_'+str(i),c,.75) for i,c in enumerate(['E8DEC6','E5D5B7','EFE6D1','D6CDBB'])];planks=[mat('Plank_'+str(i),c,.6) for i,c in enumerate(['C58B50','C68C51','CE9559','BC8147','D49B5C'])];ginger=mat('Cat_Ginger','CA823B',.85);catgrey=mat('Cat_Slate','666C71',.85)
glow=mat('Lantern_IvoryGlow','FFE7A3',.5);gb=glow.node_tree.nodes.get('Principled BSDF');gb.inputs['Emission Color'].default_value=glow.diffuse_color;gb.inputs['Emission Strength'].default_value=1.2
def group(name):
 global cur
 cur=bpy.data.objects.new(name,None);sc.collection.objects.link(cur);cur['units']='metres';roots[name]=cur;return cur
def finish(root,loc=(0,0,0),rz=0):root.location=loc;root.rotation_euler.z=math.radians(rz)
def setup(o,name,m):
 o.name=cur.name+'__'+name;o.parent=cur;o.data.materials.append(m);return o
def box(name,p,d,m,b=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.dimensions=d;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);setup(o,name,m)
 if b:
  mod=o.modifiers.new('Authored bevel','BEVEL');mod.width=b;mod.segments=2 if b>=.035 else 1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def cyl(name,p,r,depth,m,n=16,rot=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=depth,location=p);o=bpy.context.object
 if rot:o.rotation_euler=rot
 setup(o,name,m)
 bevel=o.modifiers.new('Soft rims','BEVEL');bevel.width=min(.012,r*.15);bevel.segments=1;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name)
 for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
 return o
def ell(name,p,s,m,sub=2):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=p);o=bpy.context.object;o.scale=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);setup(o,name,m)
 for f in o.data.polygons:f.use_smooth=True
 return o
def rod(name,a,b,r,m,n=10):
 a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,m,n);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def path(name,pts,r,m):
 # low-sided tubing as an actual mesh, no curve dependency in FBX
 for j,(a,b) in enumerate(zip(pts,pts[1:])):rod(name+str(j),a,b,r,m)
def handle(x,z,w=.18,y=-.451):
 rod('Handle',(x-w/2,y,z),(x+w/2,y,z),.014,brass)
 for xx in [x-w/2,x+w/2]:rod('HandleMount',(xx,y+.035,z),(xx,y,z),.012,steel)
def cabinet(width= .9,depth=.8,top=True):
 for x in [-width/2+.09,width/2-.09]:
  for y in [-depth/2+.08,depth/2-.08]:box('Foot',(x,y,.07),(.075,.075,.14),navy,.008)
 box('Carcass',(0,0,.32),(width,depth,.53),navy,.035)
 for x in [-width/4,width/4]:
  box('Door',(x,-depth/2-.012,.33),(width/2-.035,.035,.42),blue,.012);handle(x,.48,y=-depth/2-.053)
 if top:box('IvoryTop',(0,0,.62),(width+.055,depth+.055,.085),ivory,.035)
def cup(x,y,z):
 cyl('Cup',(x,y,z+.045),.048,.09,ivory);cyl('Coffee',(x,y,z+.092),.037,.004,dark);path('CupHandle',[(x+.04,y,z+.02),(x+.08,y,z+.03),(x+.08,y,z+.07),(x+.04,y,z+.08)],.009,ivory)
def plates(x,y,z,count=3):
 for i in range(count):cyl('Plate',(x,y,z+.012*i),.11,.018,ivory,20)
def prep():
 rt=group('PrepCounter');cabinet();box('CuttingBoard',(.02,-.02,.687),(.48,.34,.045),wood,.025)
 box('KnifeBlade',(.02,-.01,.716),(.22,.037,.009),steel,.002);box('KnifeHandle',(.18,-.01,.717),(.12,.042,.025),navy,.008)
 cyl('UtensilPot',(-.32,.23,.72),.06,.15,teal);rod('Spoon',(-.34,.23,.75),(-.36,.23,.96),.012,wood);ell('SpoonBowl',(-.36,.23,.965),(.025,.018,.045),wood,1)
 box('Towel',(.24,-.444,.42),(.14,.028,.28),ivory,.012);return rt
def stove():
 rt=group('Stove');cabinet(top=False);box('SteelRange',(0,0,.615),(.94,.84,.09),steel,.025);box('Backsplash',(0,.38,.7),(.92,.04,.22),steel,.012)
 for x in [-.23,.23]:
  for y in [-.18,.18]:
   cyl('Burner',(x,y,.67),.13,.025,dark,16)
   for a in range(4):
    aa=a*math.pi/2;rod('Grate',(x+math.cos(aa)*.05,y+math.sin(aa)*.05,.697),(x+math.cos(aa)*.18,y+math.sin(aa)*.18,.697),.019,dark)
 box('OvenGlass',(0,-.432,.3),(.68,.025,.3),dark,.025);box('OvenInner',(0,-.45,.29),(.55,.012,.18),navy,.012);handle(0,.48,.53)
 for x in [-.3,-.1,.1,.3]:cyl('Knob',(x,-.451,.59),.034,.035,orange,12,(math.pi/2,0,0))
 return rt
def kettle():
 rt=group('SoupKettle');box('StoveBase',(0,0,.085),(.66,.64,.17),navy,.025);cyl('Dial',(0,-.33,.1),.04,.02,orange,12,(math.pi/2,0,0));ell('PotBody',(0,0,.39),(.33,.3,.29),dark);cyl('Rim',(0,0,.57),.285,.05,steel,24);ell('Lid',(0,0,.61),(.285,.285,.07),steel);cyl('LidKnob',(0,0,.7),.055,.09,navy)
 for x in [-.35,.35]:path('SideHandle',[(x*.8,0,.49),(x,-.04,.49),(x,.08,.49),(x*.8,.08,.49)],.025,dark)
 return rt
def fridge():
 rt=group('Fridge');box('FridgeBody',(0,0,.58),(.78,.78,1.16),navy,.065);box('EnamelDoor',(0,-.407,.66),(.72,.09,.98),ivory,.06);rod('Pull',(-.25,-.49,.48),(-.25,-.49,.85),.022,navy)
 box('VentFrame',(0,-.423,.105),(.64,.04,.12),steel,.008)
 for z in [.07,.11,.15]:box('Vent',(0,-.447,z),(.53,.015,.013),dark,.002)
 return rt
def sink():
 rt=group('SinkDishRack');cabinet(1.8,.8,False)
 # countertop frame and real recessed basin, not a steel patch covering the bowl
 box('TopBack',(0,.3,.62),(1.86,.23,.07),ivory,.02);box('TopFront',(0,-.32,.62),(1.86,.2,.07),ivory,.02);box('TopLeft',(-.84,0,.62),(.18,.42,.07),ivory,.02);box('Drainboard',(.45,0,.62),(.89,.48,.07),ivory,.02)
 box('BasinBottom',(-.39,-.02,.48),(.66,.43,.035),steel,.025)
 for x in [-.73,-.04]:box('BasinSide',(x,-.02,.55),(.025,.46,.15),steel,.012)
 for y in [-.24,.21]:box('BasinSide',(-.39,y,.55),(.7,.025,.15),steel,.012)
 cyl('Drain',(-.39,0,.504),.033,.006,dark)
 path('Tap',[(-.45,.3,.65),(-.45,.3,.93),(-.45,.25,.99),(-.45,.07,.99),(-.45,.02,.94)],.023,steel)
 box('RackTray',(.43,.02,.675),(.65,.45,.04),navy,.018)
 for i in range(5):cyl('UprightPlate',(.22+i*.10,.04,.80),.117,.018,ivory,20,(0,math.pi/2,0))
 for y in [-.16,.2]:rod('RackRail',(.1,y,.72),(.76,y,.72),.013,steel)
 return rt
def coffee():
 rt=group('CoffeeMachine');cabinet();box('MachineBack',(0,.15,.95),(.7,.27,.53),navy,.04);box('MachineRoof',(0,.04,1.21),(.77,.65,.055),blue,.025);box('ControlBar',(0,-.19,1.09),(.74,.13,.18),steel,.018)
 for x in [-.24,0,.24]:cyl('Button',(x,-.263,1.1),.034,.023,orange if x==.24 else ivory,12,(math.pi/2,0,0))
 for x in [-.19,.19]:
  cyl('GroupHead',(x,-.12,.96),.058,.1,steel);rod('Portafilter',(x,-.12,.92),(x,-.34,.92),.025,dark)
 box('DripTray',(0,-.12,.71),(.71,.53,.045),steel,.015)
 for x in [-.27,-.18,-.09,0,.09,.18,.27]:box('TraySlots',(x,-.12,.736),(.012,.35,.005),dark,.001)
 cup(-.16,-.13,.746);cup(.17,.04,1.24);return rt
def table():
 rt=group('TableFor2');cyl('PedestalBase',(0,0,.035),.24,.07,navy,24);cyl('Pedestal',(0,0,.31),.062,.55,navy);cyl('RoundTop',(0,0,.62),.28,.09,wood,32)
 # restrained seams on the solid wooden tabletop
 for y in [-.14,0,.14]:
  w=math.sqrt(.275**2-y*y);box('BoardSeam',(0,y,.666),(2*w,.006,.003),darkwood,.001)
 for side in [-1,1]:
  x=side*.33
  for dx in [-.11,.11]:
   for yy in [-.11,.11]:rod('ChairLeg',(x+dx*1.15,yy*1.2,.02),(x+dx,yy,.34),.025,wood)
  box('ChairSeat',(x,0,.35),(.30,.30,.065),wood,.03);box('Cushion',(x,0,.398),(.27,.27,.045),teal,.03)
  for yy in [-.12,.12]:rod('ChairBackPost',(x+side*.12,yy,.35),(x+side*.13,yy,.79),.026,navy)
  box('ChairBack',(x+side*.13,0,.72),(.05,.30,.17),wood,.025)
 cyl('Vase',(0,.08,.72),.04,.1,ivory);rod('Stem',(0,.08,.76),(0,.08,.87),.006,leaf);ell('Flower',(0,.08,.88),(.04,.04,.035),ivory,1);return rt
def reception():
 rt=group('ReceptionDesk');cyl('DeskBase',(0,0,.05),.44,.1,wood,24);cyl('RoundNavyBody',(0,0,.34),.415,.48,navy,24);cyl('IvoryTop',(0,0,.62),.47,.1,ivory,32)
 for i in range(16):
  a=i*2*math.pi/16;rod('PanelJoin',(.416*math.cos(a),.416*math.sin(a),.16),(.416*math.cos(a),.416*math.sin(a),.52),.006,blue,6)
 box('TillBase',(-.05,0,.705),(.31,.24,.08),wood,.018);o=box('TillScreen',(-.05,.04,.82),(.26,.04,.18),navy,.012);o.rotation_euler.x=math.radians(-15);box('Ledger',(.23,-.04,.683),(.16,.24,.014),ivory,.004);cyl('Bell',(-.28,-.12,.73),.054,.08,brass);return rt
def passcounter():
 rt=group('PassCounter');box('Base',(0,0,.07),(2.85,.48,.12),ivory,.02);box('Body',(0,0,.36),(2.8,.43,.5),navy,.025)
 for x in [-1.16,-.77,-.38,0,.38,.77,1.16]:box('Panel',(x,-.223,.36),(.018,.01,.43),blue,.002)
 box('HoneyTop',(0,0,.65),(3,.62,.11),wood,.035)
 # open shelf kept low so cooks and counter tops remain visible at52deg
 for x in [-1.28,1.28]:box('ShelfPost',(x,.13,.86),(.06,.06,.47),wood,.012)
 box('OpenShelf',(0,.13,1.09),(2.78,.28,.065),wood,.02);plates(-.88,0,.72);plates(.94,0,.72,2);return rt
def trash():
 rt=group('TrashCan');cyl('BinFoot',(0,0,.025),.235,.05,navy,20);cyl('NavyBin',(0,0,.28),.235,.5,navy,20);cyl('IvoryLid',(0,0,.55),.25,.055,ivory,20);box('LidHandle',(0,0,.6),(.13,.05,.04),brass,.012);box('Pedal',(0,-.24,.065),(.13,.14,.045),steel,.01)
 for x in [-.245,.245]:rod('SidePull',(x,-.07,.44),(x,.07,.44),.016,brass)
 return rt
