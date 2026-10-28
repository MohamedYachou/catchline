"""SERVICE-PROPS-2 additive Blender authoring. One item per invocation; no Unity/git.
Updated Blender imports and authoring are Z-up; FBX delivery is Y-up.
"""
import sys,importlib.util,bpy,bmesh,math,json,hashlib,uuid
from pathlib import Path
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;R=O.parents[2]
spec=importlib.util.spec_from_file_location('service_base',O/'build_service.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
PI=math.pi
box=b.box;ell=b.ell;rod=b.rod;cyl=b.cyl;lathe=b.lathe;torus=b.torus;mesh=b.mesh
COOK={'Pan':('Stove',.8),'Grill':('Grill',.825),'FryerBasket':('Fryer',.91),'OvenTray':('Oven',1.2),'SteamPot':('Steamer',.92),'SoupLadle':('SoupKettle',.660388),'BreadBoard':('PrepCounter',.825),'Burnt':('Grill',.825)}

def steam(at=(0,0,.12),dark=False):
 x,y,z=at
 # Solid pale wisps read under opaque game shader; no particle/material dependency.
 for j in range(2):
  p=[(x+(j-.5)*.12,y,z),(x+(j-.5)*.12-.014,y,z+.045),(x+(j-.5)*.12+.017,y,z+.09),(x+(j-.5)*.12+.008,y,z+.125)]
  for i in range(3):rod('Smoke' if dark else 'Steam',p[i],p[i+1],.008 if dark else .004,'iron' if dark else 'ice',5)

def pan(burnt=False):
 lathe('Heavy iron skillet',[(0,0),(.13,0),(.155,.015),(.16,.055),(.149,.059),(.138,.023),(0,.023)],'iron',16)
 rod('Steel tang',(.145,0,.036),(.24,0,.045),.018,'steel',6)
 box('Navy pan handle',(.275,0,.045),(.105,.038,.032),'navy',.005)
 lathe('Hot butter sheen',[(0,.025),(.125,.025),(.126,.028),(0,.028)],'ochre' if burnt else 'gold',16)
 body=ell('Charred fillet' if burnt else 'Pink raw-to-golden fillet',(-.015,0,.054),(.145,.21,.054),'ink' if burnt else 'salmon',2,rot=-.17)
 if burnt:
  bpy.context.view_layer.update()
  for j in range(4):
   verts=[];y=-.06+j*.04
   for k in range(5):
    x=-.045+k*.016
    for edge in [-1,1]:
     yy=y-x*.2+edge*.0025;local=body.matrix_world.inverted()@Vector((x,yy,1));hit,co,n,fi=body.ray_cast(local,Vector((0,0,-1)));assert hit
     z=(body.matrix_world@co).z;verts.append((x,yy,z+.001))
   b.orient_sheet(mesh('Toasted crack in char',verts,[(k*2,k*2+2,k*2+3,k*2+1) for k in range(4)],'ochre'),True)
  for x,z,s in [(-.065,.22,.045),(.045,.28,.055),(-.05,.32,.04)]:ell('Faceted dark smoke puff',(x,.012,z),(s,s*.8,s*1.15),'iron')
 else:
  for j in range(4):box('Pale fillet flake',(-.023,-.065+j*.044,.078),(.10,.009,.006),'crumb',.001,-.20)
 if not burnt:
  for x,y in [(-.095,-.063),(.09,.06),(.09,-.06)]:ell('Sizzling golden butter',(x,y,.034),(.025,.02,.01),'yellow')
  b.herbs((-.065,.055,.078),.8)
 steam((-.015,.01,.105),burnt)

def grill():
 body=ell('Golden whole fish body',(0,-.015,.044),(.19,.34,.088),'batter',2)
 ell('Silver gold fish head',(0,-.163,.04),(.115,.12,.075),'fish',1)
 tail=mesh('Spread whole fish tail',[(-.018,.12,.033),(-.082,.245,.006),(.0,.22,.024),(.082,.245,.006),(.018,.12,.033)],[(0,1,2),(0,2,4),(2,3,4)],'ochre');b.orient_sheet(tail,True)
 fin=mesh('Golden dorsal fin',[(.005,-.075,.082),(.018,.07,.081),(.042,.06,.12),(.033,-.035,.125)],[(0,1,2,3)],'yellow');b.orient_sheet(fin,True)
 ell('Eye pale rim',(.035,-.185,.071),(.03,.026,.012),'cream');ell('Black fish eye',(.035,-.186,.078),(.016,.015,.005),'ink')
 bpy.context.view_layer.update()
 for j in range(4):
  verts=[];faces=[];y=-.09+j*.054
  for k in range(6):
   x=-.063+k*.0252
   for edge in [-1,1]:
    yy=y-x*.27+edge*.005
    hit,co,n,fi=body.ray_cast(Vector((x,yy+.015,1)),Vector((0,0,-1)))
    assert hit
    verts.append((x,yy,co.z+body.location.z+.0015))
  for k in range(5):faces.append((k*2,k*2+2,k*2+3,k*2+1))
  b.orient_sheet(mesh('Conforming dark char score',verts,faces,'ink'),True)
 rod('Head gill mark',(-.045,-.13,.065),(.055,-.116,.067),.004,'ochre',4)
 b.lemon((.11,-.08,.015),.7);steam((-.04,.025,.105))

def fryer():
 # Bottom wire rests on original basket rim, with a full new basket raised over oil.
 for x in [-.19,-.095,0,.095,.19]:rod('Basket bottom wire',(x,-.14,.008),(x,.14,.008),.006,'steel',4)
 for y in [-.14,-.07,0,.07,.14]:rod('Basket cross wire',(-.19,y,.008),(.19,y,.008),.006,'steel',4)
 for z in [.012,.095]:
  rod('Basket front rim',(-.2,-.15,z),(.2,-.15,z),.008,'steel',4)
  rod('Basket back rim',(-.2,.15,z),(.2,.15,z),.008,'steel',4)
  for x in [-.2,.2]:rod('Basket side rim',(x,-.15,z),(x,.15,z),.008,'steel',4)
 for x in [-.2,-.1,0,.1,.2]:
  for y in [-.15,.15]:rod('Basket vertical mesh',(x,y,.012),(x,y,.095),.005,'steel',4)
 for x in [-.2,.2]:rod('Basket side mesh',(x,0,.012),(x,0,.095),.005,'steel',4)
 for x in [-.09,.09]:rod('Handle arms',(x,-.15,.07),(x,-.325,.13),.009,'steel',4)
 rod('Navy lift grip',(-.105,-.325,.13),(.105,-.325,.13),.019,'navy',6)
 for i,(x,y) in enumerate([(-.12,-.065),(.02,-.055),(.135,-.04),(-.08,.06),(.075,.065)]):
  ell('Golden battered fish piece',(x,y,.049),(.12,.095,.07),'yellow' if i%3==0 else 'batter',2,rot=i*.47)
  box('Pale crispy ridge',(x,y-.006,.082),(.055,.009,.006),'crumb',0,i*.47)
 steam((0,.015,.12))

def oven_tray():
 box('Heavy oven tray',(0,0,.012),(.51,.34,.024),'iron',.008)
 for x in [-.276,.276]:
  box('Tray gold handle',(x,0,.028),(.045,.14,.023),'steel',.004)
 lathe('Cream sharing platter',[(0,.026),(.16,.026),(.20,.042),(.20,.052),(.176,.048),(0,.036)],'cream',20,sx=1.18,sy=.68)
 for i,(x,y) in enumerate([(-.073,.015),(.065,-.01)]):
  ell('Golden baked fish portion',(x,y,.072),(.12,.19,.067),'batter' if i else 'yellow',2,rot=.18-i*.32)
  for j in range(3):box('Baked pale flake',(x,y-.047+j*.042,.104),(.075,.008,.005),'crumb',0,.14-i*.28)
 for x,y in [(-.165,.018),(.155,.008),(-.09,.1),(.075,.1)]:
  ell('Green roast garnish',(x,y,.062),(.04,.055,.035),'leaf',1)
 b.lemon((-.12,-.085,.045),.7);b.lemon((.115,-.085,.045),.65)
 steam((0,.015,.13))

def steam_pot():
 # Recess leaves the original station's 0.10m-high lid knob untouched underneath.
 lathe('Hollow raised pot',[(.125,0),(.19,0),(.215,.06),(.218,.21),(.205,.22),(.191,.208),(.189,.118),(.125,.118)],'steel',16)
 lathe('Navy pot band',[(.213,.055),(.219,.06),(.221,.082),(.215,.088)],'navy',16)
 lathe('Pale bubbling pot surface',[(0,.155),(.18,.155),(.18,.16),(0,.16)],'cream',12)
 for x in [-.25,.25]:
  torus('Pot side grip',(x,0,.14),.045,.013,'navy',10,4,rotate=Matrix.Rotation(PI/2,3,'X'))
 # Bold two-pronged claw stands above the near rim.
 rod('Crab claw wrist',(-.045,-.08,.17),(-.045,-.15,.24),.036,'orange',6)
 ell('Crab claw palm',(-.045,-.165,.25),(.108,.09,.105),'orange',2)
 rod('Crab claw left prong',(-.075,-.17,.28),(-.096,-.175,.335),.025,'orange',5)
 rod('Crab claw left tip',(-.096,-.175,.335),(-.055,-.178,.36),.013,'yellow',5)
 rod('Crab claw right prong',(-.018,-.17,.28),(.014,-.176,.32),.023,'orange',5)
 rod('Crab claw right tip',(.014,-.176,.32),(-.018,-.178,.343),.012,'yellow',5)
 start=len(b.PARTS)
 lathe('Tilted steel lid',[(0,0),(.208,0),(.213,.012),(.16,.045),(0,.059)],'steel',16)
 cyl('Lid navy knob',(0,0,.078),.032,.04,'navy',8)
 rot=Matrix.Rotation(math.radians(-33),4,'X');at=Vector((0,.04,.34))
 for o in b.PARTS[start:]:o.matrix_world=Matrix.Translation(at)@rot@o.matrix_world
 steam((.07,-.12,.24))

def soup_ladle():
 lathe('Pale hot soup overlay',[(0,0),(.128,0),(.128,.004),(0,.004)],'cream',20,sx=1,sy=1.34)
 lathe('Deep steel soup ladle',[(0,.006),(.035,.006),(.057,.027),(.062,.055),(.054,.060),(.046,.034),(0,.026)],'steel',12,at=(-.035,-.025,0))
 lathe('Soup in ladle',[(0,.029),(.043,.029),(.043,.032),(0,.032)],'yellow',12,at=(-.035,-.025,0))
 rod('Ladle long steel handle',(.016,-.025,.055),(.185,-.065,.175),.009,'steel',6)
 rod('Ladle navy grip',(.16,-.059,.158),(.226,-.075,.206),.017,'navy',6)
 for x,y in [(-.075,.078),(.068,.07),(.07,-.09)]:
  box('Orange soup vegetable',(x,y,.010),(.022,.028,.012),'orange',.002,.3)
  ell('Floating green herb',(x+.025,y-.012,.009),(.025,.018,.009),'leaf')
 steam((-.015,.035,.065))

def bread_board():
 box('Thick honey cutting board',(0,0,.011),(.35,.20,.022),'wood',.006)
 box('Board end grip',(-.188,0,.011),(.045,.07,.019),'darkwood',.004)
 loaf=ell('Golden loaf being sliced',(-.015,.019,.061),(.195,.105,.086),'bread',2)
 bpy.context.view_layer.update()
 for x in [-.075,-.03,.015,.06]:
  verts=[]
  for i in range(5):
   y=-.018+i*.009
   for edge in [-1,1]:
    xx=x+edge*.004-y*.15;hit,co,n,fi=loaf.ray_cast(Vector((xx+.015,y,1)),Vector((0,0,-1)));assert hit
    verts.append((xx,y+.019,co.z+.062))
  b.orient_sheet(mesh('Conforming pale bread score',verts,[(i*2,i*2+2,i*2+3,i*2+1) for i in range(4)],'crumb'),True)
 for i,x in enumerate([.111,.146]):
  ell('Golden crust slice',(x,.02,.05),(.025,.105,.075),'crust',2,rot=-i*.12)
  ell('Soft bread slice face',(x+.012,.02,.051),(.004,.085,.055),'crumb',1,rot=-i*.12)
 box('Broad steel bread knife',(-.022,-.068,.032),(.21,.028,.012),'steel',.002,-.11)
 box('Navy bread knife grip',(.112,-.083,.035),(.085,.035,.021),'navy',.003,-.11)
 for x,y in [(.085,-.022),(.13,-.035),(.16,.07),(-.10,.065)]:ell('Fresh bread crumb',(x,y,.027),(.012,.011,.009),'crumb')

def tip_coins(big=False):
 layout=[(.005,-.015,0),(.005,-.015,.008),(.005,-.015,.016),(-.04,-.025,0),(.04,.005,0)]
 if big:layout=[(-.02,-.025,z) for z in [0,.009,.018,.027]]+[(.035,.005,z) for z in [0,.009,.018]]+[(-.065,-.02,0),(.075,-.035,0),(.01,-.065,0)]
 r=.025 if big else .0195
 for i,(x,y,z) in enumerate(layout):
  lathe('Chunky gold coin',[(0,0),(r*.85,0),(r,.002),(r,.006),(r*.85,.008),(0,.008)],'gold',12,at=(x,y,z))
  box('Raised coin stamp',(x,y,z+.0087),(r*.62,r*.19,.0014),'honey',0,rot=i*.65)
 # A creased, folded banknote with solid thickness and a simple teal stripe.
 s=1.35 if big else 1;x=-.023 if big else -.018;y=.037 if big else .031
 v=[(x-.03*s,y-.026*s,.002),(x+.03*s,y-.026*s,.002),(x-.03*s,y,.023*s),(x+.03*s,y,.023*s),(x-.03*s,y+.026*s,.006),(x+.03*s,y+.026*s,.006)]
 note=mesh('Folded ivory tip note',v,[(0,1,3,2),(2,3,5,4)],'cream');b.orient_sheet(note,True)
 mod=note.modifiers.new('Paper edge thickness','SOLIDIFY');mod.thickness=.0012;bpy.context.view_layer.objects.active=note;bpy.ops.object.modifier_apply(modifier=mod.name)
 for yy,zz in [(y-.014*s,.013*s),(y+.014*s,.014*s)]:
  stripe=box('Teal folded note band',(x,yy,zz+.0015),(.009*s,.017*s,.0013),'teal',0)
  stripe.rotation_euler.x=math.atan2(.021 if yy<y else -.017,.026)

def catch_board():
 k=.170/.89
 def yf(z):return -.205+k*z
 def slab(name,width,z0,z1,depth,color,front=True):
  v=[]
  for dy in [0,depth]:
   for x,z in [(-width/2,z0),(width/2,z0),(width/2,z1),(-width/2,z1)]:
    y=yf(z) if front else -yf(z);v.append((x,y+dy if front else y-dy,z))
  return mesh(name,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],color)
 for side in [-1,1]:
  for front in [True,False]:
   o=slab('Honey timber A-frame leg',.048,0,.89,.038,'wood',front)
   for v in o.data.vertices:v.co.x+=side*.26
 slab('Front dark slate',.47,.24,.84,.023,'ink');slab('Back dark slate',.47,.24,.84,.023,'ink',False)
 for z in [.235,.855]:
  for front in [True,False]:
   o=slab('Broad timber frame rail',.565,z-.019,z+.019,.040,'wood',front)
 for side in [-1,1]:
  rod('Brass fold hinge',(side*.276,-.045,.88),(side*.276,.045,.88),.020,'gold',8)
  rod('Side spreader chain',(side*.265,-.148,.30),(side*.265,.148,.30),.008,'iron',5)
 # A permanent modelled header; the lower slate remains genuinely blank for runtime fish.
 font=bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
 for text,z,width in [('CATCH',.755,.355),('of the day',.689,.355)]:
  cu=bpy.data.curves.new('Fixed chalk header','FONT');cu.body=text;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=.07;cu.resolution_u=1;cu.extrude=0;cu.font=font
  o=bpy.data.objects.new('Chalk '+text,cu);bpy.context.collection.objects.link(o);o.rotation_euler.x=math.atan2(1,k);o.location=(0,yf(z)-.003,z)
  bpy.context.view_layer.update();cu.size*=width/o.dimensions.x
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH');o=bpy.context.object
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<1e-8],context='FACES_ONLY');bmesh.ops.delete(bm,geom=[e for e in bm.edges if not e.link_faces],context='EDGES');bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS');bm.to_mesh(o.data);bm.free();o.data.update();b.uv_assign(o,'cream');b.PARTS.append(o)
 rod('Chalk header rule',(-.20,yf(.64)-.003,.64),(.20,yf(.64)-.003,.64),.002,'cream',4)
 box('Chalk stub on ledge',(.135,yf(.253)-.025,.259),(.042,.009,.009),'cream',0,rot=.08)

def atlas_emission(mat):
 n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED');sep=next(x for x in n if x.type=='SEPARATE_COLOR')
 base=bs.inputs['Base Color'].links[0].from_socket;l.new(base,bs.inputs['Emission Color'])
 e=n.new('ShaderNodeMath');e.operation='MULTIPLY';e.inputs[1].default_value=2.8;l.new(sep.outputs['Blue'],e.inputs[0]);l.new(e.outputs[0],bs.inputs['Emission Strength']);mat['ReviewMatchesCanonicalEmission']=True

def harbour_context(rm,scene):
 atlas_emission(rm)
 pier=b.load_fbx(R/'Assets/Resources/Restaurant/RestaurantPier.fbx');bpy.context.view_layer.update()
 for o in pier:
  ancestors=[];parent=o
  while parent:ancestors.append(parent.name);parent=parent.parent
  if any(x.startswith(('Pier_S2','Pier_S3','Pier_S4')) for x in ancestors):o.hide_render=True
  if o.type=='MESH':o.data.materials.clear();o.data.materials.append(rm)
 # Actual AddSea level and existing water texture, review context only.
 bpy.ops.mesh.primitive_plane_add(size=90,location=(0,0,-.57));sea=bpy.context.object;sea.name='REVIEW_AddSea'
 m=bpy.data.materials.new('REVIEW_NightWater');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;bs=n['Principled BSDF']
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(R/'Assets/Resources/Restaurant/NightWater.png'));uv=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=8;l.new(uv.outputs['UV'],scale.inputs[0]);l.new(scale.outputs[0],t.inputs[0]);mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(.32,.32,.32,1);l.new(t.outputs[0],mul.inputs[1]);l.new(mul.outputs[0],bs.inputs['Base Color']);l.new(mul.outputs[0],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.45;bs.inputs['Roughness'].default_value=.35;bs.inputs['Metallic'].default_value=.15;sea.data.materials.append(m)
 for r in json.loads((R/'Assets/Resources/Restaurant/RestaurantPier-lighting.json').read_text())['lights']:
  d=bpy.data.lights.new('REVIEW_'+r['name'],'POINT');d.energy=r['blender_power'];d.color=r['linear_rgb'];d.shadow_soft_size=max(.12,r.get('radius_m',.2));o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=r['position_blender_m']
 d=bpy.data.lights.new('REVIEW_BlueHarbourFill','SUN');d.energy=.6;d.color=(.39,.60,1);o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.rotation_euler=(math.radians(30),math.radians(-20),math.radians(-25))


def ferry():
 # Nine-metre harbour passenger ferry: chunky single-deck cabin and higher forward wheelhouse.
 outline=[(-4.5,-.83),(-3.7,-1.30),(2.70,-1.30),(4.05,-.76),(4.50,0),(4.05,.76),(2.70,1.30),(-3.70,1.30),(-4.50,.83)]
 n=len(outline)
 def hull_strip(name,levels,color,cap=False):
  v=[(x*sx,y*sy,z) for z,sx,sy in levels for x,y in outline]
  fs=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(levels)-1) for i in range(n)]
  if cap:fs+=[tuple(reversed(range(n))),tuple(range((len(levels)-1)*n,len(levels)*n))]
  return mesh(name,v,fs,color)
 hull_strip('Broad faceted navy hull',[(-.62,.91,.60),(-.18,.985,.90),(.0,1,1),(.62,1,1)],'navy',True)
 hull_strip('Gold waterline ribbon',[(.035,1.0002,1.0002),(.125,1.0002,1.0002)],'gold')
 hull_strip('Cream deck gunwale',[(.57,1.0004,1.0004),(.72,1.0004,1.0004)],'cream')
 # Deck top in the same outline, slightly inset below the cream cap.
 hull_strip('Honey passenger deck',[(.625,.985,.965),(.705,.985,.965)],'wood',True)
 box('Cream passenger cabin',(-.85,0,1.415),(4.35,2.12,1.29),'cream',.045)
 box('Navy cabin skirt',(-.85,0,.875),(4.40,2.15,.18),'navy',.02)
 box('Navy passenger roof',(-.85,0,2.10),(4.65,2.31,.16),'navy',.055)
 box('Honey roof edge',(-.85,0,2.035),(4.53,2.24,.055),'honey',.01)
 # Windows sample yellow's existing Surface.B=1 emission, using the one canonical material.
 for side in [-1,1]:
  for x in [-2.34,-1.39,-.44,.51]:
   box('Passenger window navy surround',(x,side*1.073,1.65),(.74,.045,.59),'navy',.018)
   box('Warm lit passenger window',(x,side*1.099,1.65),(.61,.017,.46),'yellow',.008)
   box('Cream window mullion',(x,side*1.115,1.65),(.035,.015,.47),'cream',0)
  # Four two-tone life rings with white rope bands.
  for x in [-2.05,.2]:
   ob=torus('Orange and white life ring',(x,side*1.16,1.055),.205,.043,'orange',16,4,rotate=Matrix.Rotation(PI/2,3,'X'))
   uv=ob.data.uv_layers.active
   for poly in ob.data.polygons:
    if (poly.index//4)%4==0:
     for li in poly.loop_indices:uv.data[li].uv=(.3125,.875)
   rod('Life-ring hanging strap',(x,side*1.12,1.29),(x,side*1.13,1.36),.014,'steel',4)
 # Raised forward wheelhouse, with a broad glowing windshield and side panes.
 box('Cream raised wheelhouse',(2.0,0,1.585),(1.52,1.82,1.75),'cream',.06)
 for side in [-1,1]:
  box('Wheelhouse side frame',(2.02,side*.925,2.02),(1.10,.045,.72),'navy',.025)
  box('Lit wheelhouse side window',(2.02,side*.951,2.02),(.94,.018,.55),'yellow',.012)
  box('Side windshield mullion',(2.02,side*.968,2.02),(.045,.018,.57),'cream',0)
 box('Front windshield frame',(2.78,0,2.02),(.035,1.58,.74),'navy',.025)
 box('Broad lit front windshield',(2.801,0,2.02),(.018,1.40,.56),'yellow',.01)
 for yy in [-.36,.36]:box('Windshield upright',(2.818,yy,2.02),(.018,.045,.58),'cream',0)
 box('Wheelhouse navy sunshade',(2.03,0,2.51),(1.92,2.12,.16),'navy',.045)
 # Aft door and open boarding deck make this a people carrier.
 box('Navy aft passenger door',(-3.039,0,1.285),(.03,.70,1.04),'navy',.012)
 box('Lit aft door pane',(-3.059,0,1.52),(.014,.50,.38),'yellow',.005)
 rod('Brass door pull',(-3.076,-.23,1.03),(-3.076,-.23,1.25),.018,'gold',5)
 for y in [-.87,.87]:
  box('Aft passenger bench',(-3.67,y,.91),(.80,.34,.12),'wood',.018)
  box('Aft bench back',(-3.67,y*1.15,1.16),(.80,.065,.40),'navy',.012)
  for x in [-3.95,-3.4]:rod('Bench leg',(x,y,.72),(x,y,.88),.035,'iron',4)
 # Rails around fore and aft decks; cabin sides have no redundant rail clutter.
 for side in [-1,1]:
  for x in [-4.20,-3.47,3.04,3.73]:
   y=side*(1.12 if x<3.2 else .85)
   rod('Steel safety stanchion',(x,y,.72),(x,y,1.37),.025,'cream',5)
  rod('Aft upper rail',(-4.22,side*1.12,1.37),(-3.38,side*1.12,1.37),.026,'cream',5)
  rod('Aft middle rail',(-4.22,side*1.12,1.04),(-3.38,side*1.12,1.04),.018,'steel',5)
  for z,r in [(1.37,.026),(1.04,.018)]:
   rod('Bow curved safety rail',(2.90,side*1.16,z),(3.76,side*.85,z),r,'cream',5)
   rod('Bow pointed safety rail',(3.76,side*.85,z),(4.37,0,z),r,'cream',5)
 rod('Bow tip stanchion',(4.37,0,.72),(4.37,0,1.37),.025,'cream',5)
 for z in [1.04,1.37]:rod('Stern cross rail',(-4.22,-1.12,z),(-4.22,1.12,z),.024,'cream',5)
 # Rounded black fenders and two mooring cleats.
 for side in [-1,1]:
  for x in [-2.6,2.7]:ell('Navy hanging fender',(x,side*1.31,.37),(.18,.18,.49),'iron')
 for x in [-3.85,3.35]:
  rod('Deck mooring cleat',(x,-.10,.765),(x,.10,.765),.035,'steel',5)
 box('Navy short funnel',(-.75,0,2.43),(.42,.46,.55),'navy',.045)
 box('Gold funnel band',(-.75,0,2.53),(.44,.48,.12),'gold',.016)
 box('Funnel top',(-.75,0,2.735),(.52,.57,.09),'iron',.025)
 rod('Navigation light pole',(2.02,0,2.57),(2.02,0,3.03),.026,'steel',6)
 cyl('Glowing top lantern',(2.02,0,3.07),.071,.12,'yellow',8)
 cyl('Lantern cap',(2.02,0,3.15),.093,.035,'navy',8)


def make(key):
 if key=='Pan':pan()
 elif key=='Grill':grill()
 elif key=='FryerBasket':fryer()
 elif key=='OvenTray':oven_tray()
 elif key=='SteamPot':steam_pot()
 elif key=='SoupLadle':soup_ladle()
 elif key=='BreadBoard':bread_board()
 elif key=='Burnt':pan(True)
 elif key=='TipCoins_S':tip_coins()
 elif key=='TipCoins_L':tip_coins(True)
 elif key=='CatchBoard':catch_board()
 elif key=='Ferry':ferry()
 else:raise ValueError(key)

def room_material():
 m=b.atlas_material();n=m.node_tree.nodes;l=m.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED');tex=next(x for x in n if x.type=='TEX_IMAGE' and x.image.name.startswith('Restaurant_BaseColor'))
 col=n.new('ShaderNodeVertexColor');col.layer_name='Color';mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;l.new(tex.outputs['Color'],mul.inputs[1]);l.new(col.outputs[0],mul.inputs[2]);l.new(mul.outputs[0],bs.inputs['Base Color'])
 return m

def load_station(name):
 obs=b.load_fbx(b.PACK/('Restaurant_'+name+'.fbx'));bpy.context.view_layer.update()
 for o in obs:
  if o.type=='MESH':
   # Preserve original station texture appearance; new props alone use canonical atlas.
   for i,mat in enumerate(o.data.materials):
    if mat and mat.name.startswith('Pack_detail_atlas'):
     o.data.materials[i]=b.MAT;continue
    if mat and mat.use_nodes:
     for node in mat.node_tree.nodes:
      if node.type=='TEX_IMAGE' and node.image:
       p=b.PACK/'restaurantbits_texture-catchline.png';node.image=bpy.data.images.load(str(p),check_existing=True);node.image.pack()
 return obs

def scene_setup(ob,rec,key):
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.view_layers[0].cycles.use_denoising=True
 try:
  pref=bpy.context.preferences.addons['cycles'].preferences;pref.compute_device_type='CUDA';pref.get_devices()
  for dev in pref.devices:dev.use=dev.type=='CUDA'
  if any(d.type=='CUDA' for d in pref.devices):scene.cycles.device='GPU'
 except Exception:pass
 scene.world=bpy.data.worlds.new('Harbour blue dusk');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.10,.16,.28,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.32
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.1
 scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
 room=b.load_fbx(R/'Assets/Resources/Restaurant/Stage1V4.fbx');rm=room_material()
 for o in room:
  if o.type=='MESH':
   o.data.materials.clear();o.data.materials.append(rm)
   source=o.data.color_attributes.active_color
   if not o.data.color_attributes.get('Color'):
    vals=[tuple(c.color) for c in source.data] if source else [];col=o.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
    for i,c in enumerate(col.data):c.color=vals[i] if vals else (1,1,1,1)
 # Evidence-only station substitution in the existing prep slot, never written back to room.
 offset=Vector(rec['origin_offset_authored'])
 if key in COOK:
  station,top=COOK[key];at=Vector((-2.48,-.05,.04))
  for o in room:
   if o.name=='EXPORT_PrepCounter':o.hide_render=True
  station_obs=load_station(station)
  for o in station_obs:
   if not o.parent:o.location+=at
  delta=Vector((-.23,-.138,0)) if key=='Pan' else Vector((.16,-.03,0)) if key=='BreadBoard' else Vector((0,0,0))
  ob.location=at+Vector((offset.x,offset.y,top))+delta
  rec['station']=station;rec['station_top_y_m']=top;rec['station_local_unity_pivot_m']=[-offset.x-delta.x,top,-offset.y-delta.y]
  rec['review_station_world_blender_m']=list(at)
  service_target=at+Vector((0,0,.66));service_scale=3.0
 elif key.startswith('TipCoins'):
  top=.812;at=Vector((1.35,.28,0));ob.location=at+Vector((0,0,top))
  rec['station']='Stage1V4 EXPORT_DiningTwo_Cloth_Four upper cloth';rec['station_top_y_m']=top;rec['station_local_unity_pivot_m']=[-1.35,top,-.28];rec['placement_note']='Room-local Unity (-1.35,0.812,-0.28), identity rotation, scale1; ray-measured cloth surface.'
  service_target=Vector((1.35,.45,.48));service_scale=1.7
 elif key=='CatchBoard':
  harbour_context(rm,scene);ob.location=Vector((-5.60,3.65,0))
  rec['station']='RestaurantPier Pier_S1 quay approach';rec['station_top_y_m']=0;rec['station_local_unity_pivot_m']=[5.60,0,-3.65]
  rec['blank_slate_panel_unity']={'centre_m':[0,.445,.205-(.170/.89)*.445+.004],'normal':[0,.170/.89,1],'width_m':.40,'height_m':.31,'up':[0,1,-.170/.89],'note':'Normal/up vectors normalise before use; fish patch lies below fixed chalk heading. Front faces local Unity +Z.'}
  service_target=Vector((-5.05,3.35,.45));service_scale=3.7
 elif key=='Ferry':
  harbour_context(rm,scene);ob.location=Vector((10.5,2.65,-.57))
  rec['station']='RestaurantPier quay / AddSea';rec['station_top_y_m']=-.57;rec['station_local_unity_pivot_m']=[-10.5,-.57,-2.65];rec['waterline_local_unity_y_m']=0;rec['draught_m']=.62;rec['heading_unity']=[-1,0,0];rec['placement_note']='Room/pier-local Unity (-10.5,-0.57,-2.65), identity rotation, scale1; local forward -X, waterlineY0, actual AddSea surfaceY-0.57.'
  rec['window_emission']='Existing yellow atlas cell(3,2), Surface.B=1, canonical shader emission factor2.8; no new material/texture.'
  service_target=Vector((5.25,1.6,.55));service_scale=23
  d=bpy.data.lights.new('REVIEW_FerryWarmQuayBounce','AREA');d.energy=650;d.color=(1,.77,.5);d.size=7;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=(10.5,2,6)
 else:raise ValueError(key)
 lights=json.loads((R/'Assets/Resources/Restaurant/Stage1V4-lighting.json').read_text())['lights']
 for r in lights:
  if r['type']!='POINT':continue
  d=bpy.data.lights.new('REVIEW_'+r['name'],'POINT');d.energy=r['blender_power'];d.color=r['linear_rgb'];d.shadow_soft_size=max(.12,r.get('radius_m',.2));o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=r['position_blender_m']
 for name,loc,energy,color,size in [('RoomBounce',(0,-.5,6),1500,(1,.77,.5),8),('Worklight',(-3,-2,3.8),110,(1,.79,.52),2)]:
  d=bpy.data.lights.new('REVIEW_'+name,'AREA');d.energy=energy;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((-2.48,0,.8))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.clip_end=120;scene.camera=cam
 b.place_camera(cam,service_target,service_scale,38)
 if key in ['CatchBoard','Ferry']:cam.location=service_target+(cam.location-service_target).normalized()*25
 scene.render.filepath=str(O/'renders'/(rec['name']+'-service.png'));bpy.ops.render.render(write_still=True)
 target=ob.location+Vector((-offset.x,-offset.y,rec['size_xyz_unity_m'][1]*.4))
 scale=max(rec['size_xyz_unity_m'][0]*1.55,rec['size_xyz_unity_m'][2]*2,rec['size_xyz_unity_m'][1]*1.7,.25 if key.startswith('TipCoins') else .55)
 b.place_camera(cam,target,scale,55)
 if key=='Ferry':cam.location=target+(cam.location-target).normalized()*25
 scene.render.filepath=str(O/'renders'/(rec['name']+'-close.png'));bpy.ops.render.render(write_still=True)
 rec['renders']=[str((O/'renders'/(rec['name']+'-'+s+'.png')).relative_to(R)) for s in ['service','close']]
 rec['service_camera_pitch_deg']=38;rec['close_camera_pitch_deg']=55

def main():
 key=sys.argv[sys.argv.index('--')+1];bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 b.PARTS=[];b.MAT=b.atlas_material()
 if key in ['CatchBoard','Ferry']:atlas_emission(b.MAT)
 make(key)
 name=('Restaurant_Cook_' if key in COOK else 'Restaurant_')+key;ob,rec=b.join_asset(name);ob['service_props_task']='SERVICE-PROPS-2'

 if key=='Ferry':
  for v in ob.data.vertices:v.co.z+=rec['origin_offset_authored'][2]
  ob.data.update();ob['pivot']='waterline centre Y0';rec['waterline_local_unity_y_m']=0
 limit=1200 if key in COOK else 4000 if key=='Ferry' else 3000;assert rec['tris']<limit,(name,rec['tris'])
 folder=b.PACK/('cooking' if key in COOK else 'service');folder.mkdir(exist_ok=True)
 if not folder.with_suffix('.meta').exists():folder.with_suffix('.meta').write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')
 path=folder/(name+'.fbx');b.export(ob,path)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'blends'/(name+'.blend')),check_existing=False)
 rec.update(file=str(path.relative_to(R)),triangle_limit_exclusive=limit,material='RestaurantAtlas',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),render_review='PENDING')
 (O/'cooking-build-progress.json').write_text(json.dumps(dict(state='EXPORTED; RENDERS AND REVIEW UNVERIFIED',item=rec),indent=2)+'\n')
 scene_setup(ob,rec,key)
 manifest=O/'cooking-manifest.json';records=json.loads(manifest.read_text()) if manifest.exists() else [];records=[a for a in records if a['name']!=name]+[rec];manifest.write_text(json.dumps(records,indent=2)+'\n')
 (O/'cooking-build-progress.json').write_text(json.dumps(dict(state='RENDERED; REVIEW UNVERIFIED',item=rec),indent=2)+'\n')
 print('ITEM_RENDERED',name,rec['tris'],rec['size_xyz_unity_m'],rec.get('station_local_unity_pivot_m'),flush=True)
if __name__=='__main__':main()
