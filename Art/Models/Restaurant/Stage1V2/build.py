"""Stage1V2: authored metric restaurant. Execute via run.py build (Windows Blender).
All reusable items are exported individually at floor/base0, with a complete dressed assembly.
Library-only future items never leak into the room export. Presentation people/lights never export.
"""
from pathlib import Path
exec((Path(__file__).resolve().parent/'geometry.py').read_text())
from mathutils import Matrix
# Additional surfaces use the same shared atlas after geometry is joined.
stone=mat('Stone','B0A48E',.9);stonecool=mat('StoneCool','8F928D',.9);stonecream=mat('StoneCream','C7B79A',.9)
rope=mat('Rope','D1AF76',.85);terracotta=mat('Terracotta','AD6948',.85);fishmat=mat('Fish','BAC9C6',.4);food=mat('Food','C47A3B',.65);soup=mat('Soup','D98936',.45);lettuce=mat('Lettuce','539651',.85);linen=mat('Linen','F3E5CB',.8);glass=mat('GlassOpaque','486B78',.27);coffeecol=mat('CoffeeLiquid','573B2C',.45);char=mat('Char','67462E',.8)
footprints={};library=set();prop_sizes={}
def register(fn,fp,name=None):
 rt=fn()
 if name:
  old=rt.name;roots.pop(old);rt.name=name;roots[name]=rt
 footprints[rt.name]=fp;return rt
# reusable V1 silhouettes upgraded in-place in V2 only.
register(prep,(1,1));register(stove,(1,1));register(kettle,(1,1));register(fridge,(1,1),'FridgeV2');register(sink,(2,1));register(coffee,(1,1),'CoffeeBar');register(table,(1,1));register(reception,(1,1));register(passcounter,(2,1));register(trash,(1,1))
# Steel fridge upgrade: brushed shell and two handles, bevelled doors.
cur=roots['FridgeV2']
for o in cur.children:
 if o.type=='MESH':
  if any(k in o.name for k in ['FridgeBody','EnamelDoor']):o.data.materials.clear();o.data.materials.append(steel)
box('UpperSeam',(0,-.459,.82),(.7,.006,.014),dark,.002);box('Badge',(.2,-.461,1.03),(.15,.008,.06),brass,.004)
# Anchor panel on the desk faces the service camera; actual geometry, no decal transparency.
cur=roots['ReceptionDesk'];box('AnchorPanel',(0,-.414,.33),(.39,.028,.34),blue,.015)
rod('AnchorShank',(0,-.435,.21),(0,-.435,.43),.015,brass,8);rod('AnchorCross',(-.09,-.435,.37),(.09,-.435,.37),.012,brass,8)
path('AnchorCrown',[(-.12,-.435,.27),(-.1,-.435,.22),(0,-.435,.19),(.1,-.435,.22),(.12,-.435,.27)],.014,brass)
bpy.ops.mesh.primitive_torus_add(major_radius=.035,minor_radius=.009,major_segments=12,minor_segments=6,location=(0,-.435,.445),rotation=(math.pi/2,0,0));setup(bpy.context.object,'AnchorRing',brass)
# Two new cooking silhouettes: oven vertical with glowing cavities; fryer twin baskets.
def oven():
 rt=group('Oven');box('Feet',(0,0,.04),(.78,.72,.08),navy,.015);box('EnamelTower',(0,0,.63),(.84,.76,1.18),steel,.055)
 box('Control',(0,-.396,1.11),(.74,.035,.16),navy,.015)
 for x in [-.23,0,.23]:cyl('Dial',(x,-.425,1.11),.035,.025,brass,12,(math.pi/2,0,0))
 box('DoorFrame',(0,-.395,.64),(.74,.045,.66),navy,.025);box('DarkGlass',(0,-.423,.64),(.63,.012,.53),dark,.025)
 for z in [.47,.61,.75]:
  box('WarmRack',(0,-.433,z),(.53,.008,.018),glow,.004)
  for x in [-.18,0,.18]:box('Roast',(x,-.445,z+.034),(.115,.02,.04),food,.012)
 handle(0,.94,.53,y=-.455)
 for z in [.12,.16,.2]:box('Vent',(0,-.389,z),(.65,.02,.014),dark,.002)
 return rt
register(oven,(1,1))
def fryer():
 rt=group('Fryer');cabinet(top=False);box('SteelTop',(0,0,.63),(.93,.83,.07),steel,.025);box('Splash',(0,.35,.78),(.93,.055,.31),steel,.02)
 for x in [-.23,.23]:
  box('OilWell',(x,-.02,.674),(.35,.49,.025),dark,.025);box('Oil',(x,-.02,.69),(.29,.41,.012),brass,.016)
  for xx in [x-.16,x+.16]:rod('BasketRim',(xx,-.23,.73),(xx,.2,.73),.014,steel,8)
  for y in [-.23,.2]:rod('BasketRim',(x-.16,y,.73),(x+.16,y,.73),.014,steel,8)
  for xx in range(6):rod('BasketWire',(x-.135+xx*.054,-.21,.71),(x-.135+xx*.054,.18,.71),.005,steel,6)
  rod('BasketHandle',(x,-.23,.73),(x,-.42,.82),.016,steel,8);rod('Grip',(x-.07,-.42,.82),(x+.07,-.42,.82),.023,dark,10)
  cyl('FrontDial',(x,-.443,.56),.035,.025,orange,12,(math.pi/2,0,0))
 return rt
register(fryer,(1,1))
# Variant retains the exact footprint, with an explicitly named emission socket only, no opaque smoke blob.
source=roots['Fryer'];rt=group('FryerBroken')
for o in list(source.children):n=o.copy();n.data=o.data.copy();sc.collection.objects.link(n);n.parent=rt
cur=rt;box('RepairStripe',(0,-.447,.36),(.32,.012,.065),orange,.009)
socket=bpy.data.objects.new('SmokeSocket',None);sc.collection.objects.link(socket);socket.parent=rt;socket.location=(.23,.04,.81);footprints[rt.name]=(1,1);library.add(rt.name)
# Remove portable kettle pedestal lift: kettle+stand remain two reusable items.
rt=group('KettleStand');cabinet();footprints[rt.name]=(1,1)
# Constrain accepted Pass geometry to2x1 in its own local axes.
for o in roots['PassCounter'].children:
 if o.type=='MESH':
  for v in o.data.vertices:
   p=o.matrix_basis@v.co;p.x*=.633333333333;v.co=p
  o.matrix_basis=Matrix.Identity(4)
# Flat supports and textiles, generous bevels; chairs fit the declared tile envelope.
def chair(x,y,angle=0):
 parts=set(sc.objects)
 for dx in [-.12,.12]:
  for yy in [-.115,.115]:rod('ChairLeg',(x+dx*1.1,y+yy*1.1,.018),(x+dx,y+yy,.34),.023,wood,8)
 box('Seat',(x,y,.36),(.32,.31,.065),wood,.025);box('Cushion',(x,y,.405),(.285,.28,.04),teal,.025)
 for dx in [-.125,.125]:rod('BackPost',(x+dx,y+.13,.35),(x+dx,y+.14,.77),.023,navy,8)
 box('Backrest',(x,y+.145,.69),(.31,.05,.19),wood,.025)
 if angle:
  for o in set(sc.objects)-parts:o.location=Vector((x,y,0))+Matrix.Rotation(math.radians(angle),4,'Z')@(o.location-Vector((x,y,0)));o.rotation_euler.rotate_axis('Z',math.radians(angle))
def table4():
 rt=group('TableFor4');box('TableTop',(0,0,.64),(1.05,.49,.085),wood,.045)
 for x in [-.4,.4]:
  cyl('Base',(x,0,.04),.16,.08,navy,16);rod('Pedestal',(x,0,.04),(x,0,.6),.045,navy,12)
 for x in [-.36,.36]:chair(x,-.32,180);chair(x,.32)
 return rt
register(table4,(2,1));library.add('TableFor4')
def booth():
 rt=group('Booth');box('Base',(0,.19,.15),(1.88,.5,.3),navy,.045);box('Cushion',(0,.13,.36),(1.84,.49,.12),teal,.055);box('Back',(0,.39,.61),(1.9,.16,.65),teal,.055)
 for x in [-.9,.9]:box('End',(x,.15,.4),(.12,.56,.53),wood,.035)
 for x in [-.6,0,.6]:box('BackSeam',(x,.302,.62),(.012,.008,.47),blue,.002)
 box('TableTop',(0,-.23,.64),(1.36,.4,.08),wood,.035)
 for x in [-.48,.48]:rod('TableFoot',(x,-.23,.01),(x,-.23,.6),.05,navy,10)
 return rt
register(booth,(2,1));library.add('Booth')
def terrace():
 rt=group('TerraceTable');cyl('Base',(0,0,.03),.21,.06,navy);cyl('Stem',(0,0,.35),.04,.64,navy);cyl('Top',(0,0,.63),.28,.075,wood,24)
 chair(-.33,0,90);chair(.33,0,-90)
 return rt
register(terrace,(1,1));library.add('TerraceTable')
def parasol():
 rt=group('Parasol');cyl('Pole',(0,0,.84),.022,1.68,wood,12);cyl('Foot',(0,0,.03),.17,.06,stone,12)
 # compact1m diameter, low enough not to become a huge lid over the floor.
 verts=[(0,0,1.8)]+[(.49*math.cos(i*math.pi/4),.49*math.sin(i*math.pi/4),1.52) for i in range(8)]
 mesh=bpy.data.meshes.new('Canopy');mesh.from_pydata(verts,[],[(0,1+i,1+(i+1)%8) for i in range(8)]);ob=bpy.data.objects.new('Canopy',mesh);sc.collection.objects.link(ob);setup(ob,'IvoryCanopy',ivory)
 for i in range(8):a=i*math.pi/4;rod('CanopyRib',(0,0,1.79),(.49*math.cos(a),.49*math.sin(a),1.515),.008,wood,6)
 ell('Finial',(0,0,1.82),(.035,.035,.045),brass,1);return rt
register(parasol,(1,1));library.add('Parasol')
# Decor, all independently copyable and base pivoted.
def plant_prop(name,r=.18,h=.32,style=0):
 rt=group(name);cyl('Pot',(0,0,h/2),r,h,terracotta if style==1 else ivory,14);cyl('Lip',(0,0,h),r*1.1,.05,wood if style==1 else ivory,14);cyl('Soil',(0,0,h+.012),r*.9,.012,darkwood,14)
 for i in range(9):
  a=i*2*math.pi/9;length=.2+random.uniform(0,.11);p=(math.cos(a)*r*.7,math.sin(a)*r*.7,h+length*.7)
  o=ell('Leaf',p,(.065,.045,length),leaf if i%2 else lettuce,1);o.rotation_euler=(math.cos(a)*.5,math.sin(a)*.5,a)
 return rt
for i,(r,h) in enumerate([(.14,.24),(.18,.3),(.22,.39)]):register(lambda i=i,r=r,h=h:plant_prop('PlantPot'+str(i+1),r,h,i%2),(1,1))
def barrel():
 rt=group('Barrel');ell('Staves',(0,0,.29),(.26,.26,.3),wood,2)
 for z,r in [(.09,.222),(.28,.259),(.49,.228)]:cyl('NavyHoop',(0,0,z),r,.055,navy,16)
 cyl('Top',(0,0,.555),.21,.035,woodlight if 'woodlight' in globals() else goldwood,16)
 for y in [-.1,0,.1]:box('LidJoin',(0,y,.575),(.36,.007,.004),darkwood,.001)
 return rt
register(barrel,(1,1))
def crate():
 rt=group('Crate')
 for z in [.09,.23,.37]:
  for y in [-.22,.22]:box('Slat',(0,y,z),(.48,.04,.115),wood,.012)
  for x in [-.22,.22]:box('Slat',(x,0,z),(.04,.42,.115),goldwood,.012)
 for x in [-.21,.21]:
  for y in [-.21,.21]:box('Corner',(x,y,.21),(.055,.055,.42),darkwood,.012)
 box('Bottom',(0,0,.025),(.45,.45,.05),wood,.008);return rt
register(crate,(1,1))
def lantern_geometry(x=0,y=0,z=0,scale=1):
 cyl('Base',(x,y,z+.025),.09*scale,.05*scale,navy,12);cyl('GoldenGlass',(x,y,z+.13*scale),.062*scale,.18*scale,glow,10);cyl('Cap',(x,y,z+.24*scale),.1*scale,.045*scale,navy,12)
 for i in range(4):a=i*math.pi/2;rod('Cage',(x+math.cos(a)*.07*scale,y+math.sin(a)*.07*scale,z+.035*scale),(x+math.cos(a)*.07*scale,y+math.sin(a)*.07*scale,z+.23*scale),.007*scale,navy,6)
 rod('Handle',(x-.04*scale,y,z+.25*scale),(x+.04*scale,y,z+.25*scale),.008*scale,brass,8)
def lamp_post():
 rt=group('LampPost');cyl('Foot',(0,0,.04),.16,.08,navy,16);cyl('BaseCollar',(0,0,.13),.09,.18,navy,12);rod('Post',(0,0,.1),(0,0,1.75),.045,navy,12);rod('Arm',(0,0,1.69),(.28,0,1.69),.035,navy,10);lantern_geometry(.28,0,1.39);return rt
register(lamp_post,(1,1))
def fence_post():
 rt=group('RopeFencePost');cyl('Post',(0,0,.3),.09,.6,wood,12);cyl('Cap',(0,0,.6),.11,.045,goldwood,12)
 for z in [.15,.46]:cyl('Collar',(0,0,z),.098,.045,navy,12)
 return rt
register(fence_post,(1,1))
# Service props: their own roots/FBXs, no baked table attachment.
def lathe(name,profile,m,n=20):
 verts=[(r*math.cos(j*2*math.pi/n),r*math.sin(j*2*math.pi/n),z) for r,z in profile for j in range(n)];faces=[]
 for k in range(len(profile)-1):
  for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob);setup(ob,name,m)
 for p in me.polygons:p.use_smooth=True
 return ob
def plate_shape():lathe('Porcelain',[(0,.008),(.07,.008),(.105,.018),(.135,.033),(.14,.042),(.135,.049),(.105,.028),(.07,.02),(0,.02)],ivory,24)
def plate_clean():rt=group('PlateClean');plate_shape();return rt
def plate_dirty():
 rt=group('PlateDirty');plate_shape()
 for x,y,r in [(-.05,.02,.021),(.035,.025,.018),(.02,-.04,.014)]:ell('Sauce',(x,y,.025),(r,r*.7,.004),food,1)
 rod('Bone',(-.04,-.03,.03),(.03,.02,.03),.005,ivory,6);return rt
def fish_plate():
 rt=group('GrilledFishPlate');plate_shape();ell('Fish',(-.01,0,.045),(.09,.032,.025),food,2)
 for x in [-.045,-.015,.015,.045]:
  points=[]
  for j in range(7):
   y=-.021+j*.007;xx=x+(y+.021)*.28
   z=.045+.025*math.sqrt(max(.02,1-((xx+.01)/.09)**2-(y/.032)**2))+.001
   points.append((xx,y,z))
  path('GrillMark',points,.0014,char)
 for i in range(3):ell('Salad',(.06,(-1+i)*.026,.037),(.027,.019,.014),lettuce,1)
 cyl('Lemon',(-.075,.05,.034),.025,.012,goldwood,12);return rt
def soup_bowl():
 rt=group('SoupBowl');lathe('Bowl',[(0,.005),(.055,.005),(.105,.085),(.106,.1),(.093,.1),(.05,.02),(0,.02)],ivory,24);cyl('Soup',(0,0,.082),.096,.008,soup,24)
 for x,y in [(-.02,.025),(.04,0),(-.035,-.03)]:ell('Herb',(x,y,.089),(.012,.009,.003),lettuce,1)
 return rt
def coffee_prop():rt=group('CoffeeCup');cup(0,0,0);return rt
def glass_prop():
 rt=group('Glass');lathe('OpaqueGlass',[(0,0),(.033,0),(.04,.11),(.037,.118),(.031,.118),(.028,.017),(0,.017)],glass,16);cyl('Water',(0,0,.095),.033,.003,blue,16);return rt
def candle():rt=group('TableLantern');lantern_geometry(scale=.65);return rt
def cloche():
 rt=group('Cloche');cyl('Tray',(0,0,.012),.15,.024,steel,24);lathe('Dome',[(.145,.024),(.14,.065),(.115,.11),(.07,.145),(0,.157)],steel,24);cyl('Knob',(0,0,.176),.025,.04,brass,12);return rt
for fn in [plate_clean,plate_dirty,fish_plate,soup_bowl,coffee_prop,glass_prop,candle,cloche]:
 rt=fn();prop_sizes[rt.name]=True
# Room shell masonry / floor / quay; intentionally no water/presentation floor.
cur=group('RoomShell');room=cur
# Cream ceramic in left3x5, grout actual gaps over a cream foundation.
box('Foundation',(0,0,-.14),(8.26,5.26,.28),stonecream,.06)
box('KitchenGrout',(-2.5,0,.003),(3,5,.025),stonecream,.012)
for ix in range(6):
 for iy in range(10):box('Ceramic',(-3.75+ix*.5,-2.25+iy*.5,.025),(.482,.482,.045),random.choice(tilem[:3]),.013)
# Rich honey floor: broad tone breaks and narrow recessed seams.
for iy in range(16):
 y=-2.5+(iy+.5)*5/16;ends=[-1]+sorted([random.uniform(-.4,.3),random.uniform(.8,1.6),random.uniform(2.3,3.1)])+[4]
 for a,b in zip(ends,ends[1:]):box('FloorPlank',((a+b)/2,y,.027),(b-a-.01,5/16-.01,.05),random.choice(planks),.008)
def wall_run(label,start,end,height=.88):
 a,b=Vector(start),Vector(end);delta=b-a;length=delta.length;direction=delta.normalized();normal=Vector((-direction.y,direction.x,0));num=round(length/.52)
 for row in range(3):
  cuts=[0]+[max(0,min(length,i*length/num+(row%2)*length/num*.48)) for i in range(1,num)]+[length]
  for j,(u,v) in enumerate(zip(cuts,cuts[1:])):
   p=a+direction*(u+v)/2;p.z=.146+row*.285
   o=box(label+'Stone',p,(v-u-.015,.205,.27),cream if (j+row)%4 else ivory,.035);o.rotation_euler.z=math.atan2(delta.y,delta.x)
 caps=math.ceil(length/.64)
 for i in range(caps):
  p=a+direction*(i+.5)*length/caps;p.z=.91
  o=box(label+'RoundedCap',p,(length/caps-.009,.29,.13),ivory,.035);o.rotation_euler.z=math.atan2(delta.y,delta.x)
wall_run('Rear',(-4.12,2.59,0),(4.12,2.59,0));wall_run('Right',(4.09,-2.5,0),(4.09,2.5,0));wall_run('LeftRear',(-4.09,1.35,0),(-4.09,2.5,0));wall_run('LeftFront',(-4.09,-2.5,0),(-4.09,.25,0))
# Front cutaway wall under1m, windows and blue shutters as in service mockup.
wall_run('Front',(-4.08,-2.59,0),(2.25,-2.59,0));wall_run('EntryPier',(3.6,-2.59,0),(4.08,-2.59,0))
def front_window(x,y,z=.52):
 box('WindowRecess',(x,y,z),(.8,.035,.52),navy,.025);box('WarmWindow',(x,y-.025,z),(.67,.016,.41),glow,.015)
 for xx in [x-.225,x,x+.225]:box('Mullion',(xx,y-.045,z),(.035,.025,.45),wood,.008)
 box('Crossbar',(x,y-.05,z),(.68,.03,.035),wood,.006)
 box('Sill',(x,y-.08,z-.27),(.87,.16,.09),ivory,.022)
 for sign in [-1,1]:
  for i in range(4):box('Shutter',(x+sign*.54+(i-1.5)*.055,y-.015,z),(.052,.065,.54),blue,.009)
  for zz in [z-.18,z+.18]:box('ShutterRail',(x+sign*.54,y-.057,zz),(.24,.026,.045),navy,.006)
for x in [-2.65,-.6,1.45]:front_window(x,-2.707)
for x in [-2.4,.1,2.7]:front_window(x,2.466,.55)
# Kitchen backsplash as a low rear upstand, hood is unobstructed above appliances.
for ix in range(7):
 for iz in range(2):box('Backsplash',(-3.72+ix*.39,2.459,.32+iz*.25),(.376,.025,.235),tilem[(ix+iz)%3],.009)
# Extractor hood and tall back wall kept within kitchen rear strip; no slab over working floor.
box('HoodBack',(-2.5,2.48,1.06),(1.4,.10,.42),cream,.025)
box('HoodCanopy',(-2.5,2.16,1.38),(1.25,.61,.16),steel,.025);box('HoodFace',(-2.5,1.85,1.35),(1.21,.06,.23),steel,.022)
box('HoodFlue',(-2.5,2.36,1.6),(.43,.24,.37),steel,.028)
for x in [-2.83,-2.5,-2.17]:box('HoodFilter',(x,2.14,1.291),(.23,.43,.012),dark,.005)
# Shelf carries real cups and plate stacks, and a wall-mounted trophy fish.
box('PlateShelf',(-.72,2.38,1.22),(1.52,.34,.07),wood,.02)
for x in [-1.3,-.2]:rod('ShelfBracket',(x,2.45,.99),(x,2.2,1.18),.022,navy,8)
for x in [-1.25,-.91,-.57]:plates(x,2.33,1.27,3)
cyl('ShelfPot',(-.2,2.33,1.34),.09,.15,blue,12)
box('TrophyPlaque',(2.35,2.46,1.25),(1.3,.08,.44),wood,.07)
ell('TrophyFish',(2.35,2.39,1.26),(.46,.07,.14),fishmat,2);ell('FishBack',(2.36,2.375,1.32),(.38,.04,.06),blue,1);ell('FishEye',(2.01,2.313,1.29),(.022,.012,.022),dark,1)
# Fish tail/dorsal are low-facet solid forms.
ell('Tail',(2.85,2.38,1.26),(.15,.055,.17),blue,1)
# Alley door opens left, two cats below; no change to accepted crew art.
box('AlleyFrame',(-4.10,.79,.57),(.2,1.13,1.14),ivory,.035)
for i in range(6):box('AlleyPlank',(-4.035,.34+i*.16,.54),(.035,.15,1.04),blue,.01)
for z in [.22,.84]:box('AlleyBrace',(-4.0,.74,z),(.035,.98,.07),navy,.01)
box('AlleyThreshold',(-4.45,.79,-.015),(.82,1.2,.1),stonecream,.025)
for j,m in enumerate([ginger,catgrey]):
 x=-4.48;y=.47+j*.53;ell('CatBody',(x,y,.19),(.17,.16,.21),m);ell('CatHead',(x,y-.025,.4),(.15,.14,.14),m);ell('CatMuzzle',(x,y-.15,.37),(.09,.03,.055),ivory,1)
 for sign in [-1,1]:
  bpy.ops.mesh.primitive_cone_add(vertices=4,radius1=.06,depth=.13,location=(x+sign*.09,y,.54));setup(bpy.context.object,'CatEar',m)
  ell('CatEye',(x+sign*.05,y-.15,.425),(.014,.009,.02),dark,1);ell('CatPaw',(x+sign*.08,y-.1,.045),(.05,.07,.045),ivory,1)
 path('CatTail',[(x+.13,y+.04,.09),(x+.24,y+.1,.15),(x+.25,y+.1,.28)],.027,m)
# Architectural lanterns along caps. Their glass is opaque emissive, light rig later.
lantern_locs=[(-3.78,2.27,1.02),(.15,2.3,1.02),(3.7,2.27,1.02),(3.82,-1.1,1.02),(-3.83,-2.4,1.02),(2.15,-2.4,1.02)]
for x,y,z in lantern_locs:lantern_geometry(x,y,z,1.15)
# Stone quay base below waterline0.55m beneath restaurant floor, actual chunky cut blocks.
waterline=-.55
box('QuayCore',(0,-.1,-.45),(9.4,6.6,.58),stonecool,.1)
for row in range(2):
 for i in range(15):
  x=-4.5+i*.64+(row%2)*.16
  if x>4.6:continue
  o=box('QuayFace',(x,-3.39,-.66+row*.31),(.61,.31,.30),random.choice([stone,stonecool,stonecream]),.065);o.rotation_euler.y=random.uniform(-.03,.03)
for side in [-1,1]:
 for i in range(10):box('QuaySide',(side*4.66,-3.05+i*.66,-.45),(.29,.64,.59),random.choice([stone,stonecool,stonecream]),.06)
for i in range(15):box('QuayCoping',(-4.5+i*.64,-3.28,-.12),(.62,.5,.18),random.choice([stonecream,cream]),.04)
# Dock/steps at front-right entry, in the same room mesh (no water geometry).
for i in range(3):box('EntryStep',(2.93,-2.83-i*.24,-.04-i*.09),(1.25,.3,.15),stonecream,.025)
for i in range(9):box('JettyPlank',(2.96,-3.38-i*.16,-.29),(1.7,.15,.12),random.choice(planks),.018)
for x in [2.16,3.76]:
 for y in [-3.4,-4.63]:cyl('JettyPost',(x,y,-.48),.09,.85,wood,12);cyl('JettyCap',(x,y,-.05),.106,.05,goldwood,12)
# Rope fence along quay, open around entry/jetty.
for x in [-4.5,-3.3,-2.1,-.9,.3,1.5,4.5]:
 cyl('QuayPost',(x,-3.18,.13),.085,.57,wood,12);cyl('PostCap',(x,-3.18,.43),.105,.055,goldwood,12)
for a,b in [(-4.5,-3.3),(-3.3,-2.1),(-2.1,-.9),(-.9,.3),(.3,1.5)]:path('SaggingRope',[(a,-3.18,.35),((a+b)/2,-3.18,.22),(b,-3.18,.35)],.023,rope)
room['waterline_blender_z_m']=waterline
# Placement composition: LEFT kitchen, pass front-to-back, entrance right.8x5 contract.
placements={
'PrepCounter':((-2.48,-.05,.04),0),'Stove':((-3.44,1.92,.04),0),'SoupKettle':((-3.48,.65,.69),90),'KettleStand':((-3.48,.65,.04),90),
'FridgeV2':((-1.48,1.92,.04),0),'Oven':((-2.48,1.92,.04),0),'Fryer':((-3.48,-.35,.04),90),'SinkDishRack':((-3.48,-1.73,.04),90),
'CoffeeBar':((3.48,.02,.04),-90),'ReceptionDesk':((3.02,-1.84,.04),0),'PassCounter':((-.62,0,.04),90),'TrashCan':((-1.5,-1.97,.04),0),
'TableFor2':((1.25,.7,.04),0),'TableFor4':((1.2,-1.4,.04),0),'Booth':((2.15,1.89,.04),0),
'PlantPot1':((3.59,1.88,.04),0),'PlantPot2':((.17,2.06,.04),0),'PlantPot3':((3.69,-1.78,.04),0),
'Barrel':((-4.43,-1.79,-.04),0),'Crate':((-4.41,1.74,-.04),0),'LampPost':((-4.45,-2.87,-.03),0),'RopeFencePost':((4.45,-2.84,-.03),0)}
# Full kit includes higher-stage table/booth, placed only for art proof; no gameplay availability claim.
# Service props on pass and tables: real reusable meshes with base pivots.
placements.update({'PlateClean':((-.62,-.65,.76),0),'PlateDirty':((-3.3,-1.9,.71),0),'GrilledFishPlate':((1.23,.63,.72),0),'SoupBowl':((1.24,-1.35,.73),0),'CoffeeCup':((3.38,-.1,.80),0),'Glass':((1.05,-1.45,.73),0),'TableLantern':((1.32,.84,.72),0),'Cloche':((-.62,.5,.76),0)})
# Duplicate already-built objects, never regenerate a different model for room repetition.
def duplicate(name,newname,loc,rz=0):
 source=roots[name];rt=group(newname)
 for o in list(source.children):
  if o.type!='MESH':continue
  n=o.copy();n.data=o.data.copy();sc.collection.objects.link(n);n.parent=rt
 footprints[newname]=footprints.get(name,(1,1));placements[newname]=(loc,rz);return rt
# Two table2 types same source and extra warmth/decor; no overfilling aisles.
duplicate('TableLantern','TableLantern_B',(1.2,-1.4,.73));duplicate('PlantPot1','PlantPot1_B',(-4.42,-.43,-.03));duplicate('Crate','Crate_B',(-4.43,1.75,.39))
# UV0 and single atlas material. Assign swatches by source material, with per-face projection
# in material/object local coordinates so broad brush-grain follows actual planks.
atlas=json.loads((O/'textures/atlas.json').read_text());cells={r['name']:r for r in atlas['cells']}
def swatch(m):
 n=m.name
 if n.startswith('Enamel_Navy'):return 'navy'
 if n.startswith('Enamel_Lit'):return 'blue'
 if n.startswith('Ivory'):return 'ivory'
 if n.startswith('Plaster'):return 'plaster'
 if n.startswith('Honey') or n.startswith('Plank'):return 'wood'
 if n.startswith('Wood_D'):return 'woodlight'
 if n.startswith('Recess'):return 'wooddark'
 if n.startswith('Steel'):return 'steel'
 if n.startswith('Rubber'):return 'dark'
 if n.startswith('Brass'):return 'brass'
 if n.startswith('Orange'):return 'orange'
 if n.startswith('Cushion'):return 'teal'
 if n.startswith('Leaf'):return 'leaf'
 if n.startswith('Tile_'):return 'tile'+str(min(int(n.split('_')[1])+1,3))
 if n.startswith('Cat_Ginger'):return 'catginger'
 if n.startswith('Cat_Slate'):return 'catgrey'
 if n.startswith('Lantern'):return 'glow'
 return {'Stone':'stone','StoneCool':'stonecool','StoneCream':'stonecream','Rope':'rope','Terracotta':'terracotta','Fish':'fish','Food':'food','Soup':'soup','Lettuce':'lettuce','Linen':'white','GlassOpaque':'glass','CoffeeLiquid':'coffee','Char':'char'}[n]
# Before merging each part gets swatch-mapped UVs using projected face coordinates.
for root in roots.values():
 for ob in root.children:
  if ob.type!='MESH':continue
  me=ob.data
  # Drop primitive UVMap so Unity channel 0/1 are exactly the authored UV0/UV1.
  for old in list(me.uv_layers):me.uv_layers.remove(old)
  uv=me.uv_layers.new(name='UV0');me.uv_layers.active=uv
  for poly in me.polygons:
   cell=cells[swatch(me.materials[poly.material_index])];axis=max(range(3),key=lambda i:abs(poly.normal[i]));axes=[i for i in range(3) if i!=axis]
   vals=[me.vertices[me.loops[li].vertex_index].co for li in poly.loop_indices];lo=[min(v[i] for v in vals) for i in axes];hi=[max(v[i] for v in vals) for i in axes]
   for li in poly.loop_indices:
    v=me.vertices[me.loops[li].vertex_index].co;t=[(v[ax]-lo[k])/(hi[k]-lo[k]) if hi[k]-lo[k]>.000001 else .5 for k,ax in enumerate(axes)]
    # longer stroke direction follows longest projected face extent, including floor planks.
    if hi[0]-lo[0]>hi[1]-lo[1]:t=t[::-1]
    x,y,w,h=cell['pixel_cell'];uv.data[li].uv=((x+16+t[0]*(w-32))/2048,1-(y+16+(1-t[1])*(h-32))/2048)
# Join mesh per item/root, applying world-preserving transforms; per-item UV1 packed separately.
for root in roots.values():
 children=[o for o in root.children if o.type=='MESH']
 if not children:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in children:o.select_set(True)
 bpy.context.view_layer.objects.active=children[0];bpy.ops.object.join();ob=bpy.context.object;ob.name=root.name+'_Mesh'
 # Root identity before placement. Bake piece offsets into mesh, origin exactly at root.
 M=ob.matrix_basis.copy();ob.data.transform(M);ob.matrix_basis=Matrix.Identity(4)
 # Exact floor/base plane, including lathed prop lips and curved barrel bottom.
 if root.name!='RoomShell':
  zbase=min(v.co.z for v in ob.data.vertices)
  for vert in ob.data.vertices:vert.co.z-=zbase
  for child in root.children:
   if child.type=='EMPTY':child.location.z-=zbase
 # Explicit production triangulation discards zero-area cap/bevel tessellation, including lathe poles.
 import bmesh
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
 dead=[f for f in bm.faces if f.calc_area()<1e-8]
 if dead:bmesh.ops.delete(bm,geom=dead,context='FACES_ONLY')
 loose=[v for v in bm.verts if not v.link_faces]
 if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
 bm.to_mesh(ob.data);bm.free();ob.data.update()
 uv0=ob.data.uv_layers.get('UV0');uv0.name='UV0';ob.data.uv_layers.active=uv0
 uv1=ob.data.uv_layers.new(name='UV1');ob.data.uv_layers.active=uv1
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.018,correct_aspect=True);bpy.ops.object.mode_set(mode='OBJECT')
 ob.data.uv_layers.active=uv0;uv0.active_render=True
# One shared material with both textures; local AO is a genuine object-local ray bake.
M=bpy.data.materials.new('Restaurant_Atlas_URP');M.use_nodes=True;ns=M.node_tree.nodes;ls=M.node_tree.links;b=ns.get('Principled BSDF')
base=ns.new('ShaderNodeTexImage');base.name='BaseColor_sRGB';base.image=bpy.data.images.load(str(O/'textures/Restaurant_BaseColor.png'));base.interpolation='Linear'
surface=ns.new('ShaderNodeTexImage');surface.name='Surface_LINEAR_RoughMetalEmit';surface.image=bpy.data.images.load(str(O/'textures/Restaurant_Surface.png'));surface.image.colorspace_settings.name='Non-Color';surface.interpolation='Linear'
uvnode=ns.new('ShaderNodeUVMap');uvnode.uv_map='UV0';ls.new(uvnode.outputs['UV'],base.inputs['Vector']);ls.new(uvnode.outputs['UV'],surface.inputs['Vector'])
sep=ns.new('ShaderNodeSeparateColor');ls.new(surface.outputs['Color'],sep.inputs['Color']);ls.new(sep.outputs['Red'],b.inputs['Roughness']);ls.new(sep.outputs['Green'],b.inputs['Metallic'])
vc=ns.new('ShaderNodeVertexColor');vc.layer_name='LocalAO';mult=ns.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=1;ls.new(base.outputs['Color'],mult.inputs[1]);ls.new(vc.outputs['Color'],mult.inputs[2]);ls.new(mult.outputs[0],b.inputs['Base Color'])
ls.new(base.outputs['Color'],b.inputs['Emission Color']);power=ns.new('ShaderNodeMath');power.operation='MULTIPLY';power.inputs[1].default_value=2.8;ls.new(sep.outputs['Blue'],power.inputs[0]);ls.new(power.outputs[0],b.inputs['Emission Strength'])
from mathutils.bvhtree import BVHTree
# Deterministic low-frequency AO with12 cosine-distributed rays,0.22m range and floor-independent.
from mathutils.geometry import tessellate_polygon
AOrows=[]
for root in roots.values():
 ob=next((o for o in root.children if o.type=='MESH'),None)
 if not ob:continue
 me=ob.data;me.update();verts=[v.co.copy() for v in me.vertices];polys=[list(p.vertices) for p in me.polygons];tree=BVHTree.FromPolygons(verts,polys,all_triangles=False,epsilon=.00001)
 ao=[]
 for v in me.vertices:
  n=v.normal.normalized()
  if n.length<.5:n=Vector((0,0,1))
  tangent=n.cross(Vector((0,0,1)) if abs(n.z)<.9 else Vector((0,1,0))).normalized();bit=n.cross(tangent);hits=0
  for j in range(12):
   a=j*2.3999632297;r=math.sqrt((j+.5)/12);d=tangent*(math.cos(a)*r)+bit*(math.sin(a)*r)+n*math.sqrt(1-r*r)
   loc,normal,idx,dist=tree.ray_cast(v.co+n*.004,d,.22)
   if loc is not None:hits+=1-(dist/.22)*.5
  ao.append(1-.23*hits/12)
 color=me.color_attributes.get('LocalAO') or me.color_attributes.new(name='LocalAO',type='FLOAT_COLOR',domain='CORNER')
 for loop in me.loops:a=ao[loop.vertex_index];color.data[loop.index].color=(a,a,a,1)
 me.color_attributes.active_color=color;me.materials.clear();me.materials.append(M)
 for p in me.polygons:p.material_index=0
 AOrows.append({'root':root.name,'vertices':len(ao),'min':min(ao),'max':max(ao),'ray_count_per_vertex':12,'radius_m':.22,'world_floor_excluded':True})
 print('UV+AO',root.name,len(me.polygons),flush=True)
# Export per-item at origin; FBX includes only its root, mesh and named smoke socket if applicable.
export_opts=dict(use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False,path_mode='RELATIVE',colors_type='LINEAR')
rows=[]
def bounds(ob):
 pts=[ob.matrix_world@v.co for v in ob.data.vertices];lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)];return lo,hi
for name,root in roots.items():
 children=list(root.children);mesh=next(o for o in children if o.type=='MESH');lo,hi=bounds(mesh);tri=sum(len(p.vertices)-2 for p in mesh.data.polygons);dims=[hi[i]-lo[i] for i in range(3)]
 fp=footprints.get(name)
 if fp:assert dims[0]<=fp[0]+.0001 and dims[1]<=fp[1]+.0001,(name,dims,fp)
 # floor pivots: service props may start .008m above; kettle's body handles were designed at0.
 if name!='RoomShell':assert abs(lo[2])<1e-5,(name,lo)
 bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
 for o in children:o.select_set(True)
 file='items/'+name+'.fbx' if name!='RoomShell' else 'RoomShell.fbx'
 bpy.ops.export_scene.fbx(filepath=str(O/file),**export_opts)
 rows.append({'root':name,'mesh':mesh.name,'fbx':file,'local_min_m':lo,'local_max_m':hi,'local_dimensions_m':dims,'footprint_tiles':fp,'triangles':tri,'service_prop':name in prop_sizes,'in_dressed_room':name in placements or name=='RoomShell'})
# Place assembly. Library-only meshes hidden and excluded by explicit selection.
for name,root in roots.items():
 if name in placements:loc,rz=placements[name];finish(root,loc,rz)
 if name not in placements and name!='RoomShell':
  for o in root.children:o.hide_render=True;o.hide_viewport=True
bpy.context.view_layer.update();roommeshes=[]
bpy.ops.object.select_all(action='DESELECT')
for name,root in roots.items():
 if name in placements or name=='RoomShell':
  root.select_set(True)
  for ob in root.children:ob.select_set(True)
  roommeshes.extend(o for o in root.children if o.type=='MESH')
bpy.ops.export_scene.fbx(filepath=str(O/'Stage1V2.fbx'),**export_opts)
assembly=[]
for ob in roommeshes:
 lo,hi=bounds(ob);assembly.append({'mesh':ob.name,'root':ob.parent.name,'min_m':lo,'max_m':hi,'triangles':sum(len(p.vertices)-2 for p in ob.data.polygons)})
unique=sum(r['triangles'] for r in rows);placed=sum(r['triangles'] for r in assembly)
assert unique<=150000 and placed<=150000,(unique,placed)
metrics={'budget_triangles':150000,'unique_library_plus_shell_triangles':unique,'dressed_assembly_triangles':placed,'atlas_maps':2,'atlas_resolution':[2048,2048],'texture_channels':atlas['surface_channels'],'room_tiles':[8,5],'kitchen_tiles':[3,5],'waterline_blender_z_m':waterline,'roots':rows,'assembly':assembly,'placements':placements,'AO':AOrows,'architectural_lantern_positions_m':lantern_locs,'units':'1 Blender unit =1 metre; FBX UnitScaleFactor100; X right Y rear Z up'}
(O/'build-metrics.json').write_text(json.dumps(metrics,indent=2));bpy.ops.wm.save_as_mainfile(filepath=str(O/'Stage1V2.blend'));print('V2 BUILD COMPLETE',unique,placed,len(rows),flush=True)
