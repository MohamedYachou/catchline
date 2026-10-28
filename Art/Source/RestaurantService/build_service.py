"""SERVICE-PROPS-1 additive authored low-poly meshes. Blender 5.x, no Unity execution.
Blender authoring is Z-up; FBX axis conversion bakes Y-up, metres, bottom-centred.
Only the explicitly named new FBXs/metas and this source folder are written.
"""
import bpy, bmesh, math, json, random, hashlib, sys, uuid
from pathlib import Path
from mathutils import Vector, Matrix
from bpy_extras.io_utils import axis_conversion
from io_scene_fbx import import_fbx, export_fbx_bin
R=Path(__file__).resolve().parents[3]; O=Path(__file__).resolve().parent
PACK=R/'Assets/Art/Models/Restaurant/Pack'; REND=O/'renders'
for p in [REND,O/'blends',PACK/'service']:p.mkdir(parents=True,exist_ok=True)
class Reporter:
 def report(self,*args):print(*args,flush=True)
OP=Reporter(); PI=math.pi
# Top-origin atlas cells, 8 columns x 4 rows. UVs stay safely inside each tile.
CELLS={'navy':(0,0),'blue':(1,0),'cream':(2,0),'fish':(2,2),'steel':(7,0),
       'honey':(5,0),'wood':(4,0),'darkwood':(6,0),'ink':(0,1),'gold':(1,1),
       'orange':(2,1),'teal':(3,1),'leaf':(4,1),'ice':(5,1),'water':(6,1),
       'white':(7,1),'yellow':(3,2),'batter':(4,2),'iron':(5,2),'glass':(6,2),
       'crust':(7,2),'ochre':(0,3),'green':(1,3),'crumb':(2,3),'bread':(3,3),
       'salmon':(4,3),'puddle':(5,3),'tea':(6,3),'brown':(7,3)}
PARTS=[]; MAT=None

def load_fbx(p):
 before=set(bpy.context.scene.objects);import_fbx.load(OP,bpy.context,filepath=str(p),use_anim=False)
 return [o for o in bpy.context.scene.objects if o not in before]

def atlas_material():
 m=bpy.data.materials.new('RestaurantAtlas');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
 out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');l.new(bs.outputs['BSDF'],out.inputs[0])
 tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(R/'Assets/Resources/RestaurantAtlas/Restaurant_BaseColor.png'));tex.interpolation='Linear';tex.image.pack();l.new(tex.outputs['Color'],bs.inputs['Base Color'])
 sur=n.new('ShaderNodeTexImage');sur.image=bpy.data.images.load(str(R/'Assets/Resources/RestaurantAtlas/Restaurant_Surface.png'));sur.image.colorspace_settings.name='Non-Color';sur.image.pack()
 split=n.new('ShaderNodeSeparateColor');l.new(sur.outputs['Color'],split.inputs[0]);l.new(split.outputs['Red'],bs.inputs['Roughness']);l.new(split.outputs['Green'],bs.inputs['Metallic'])
 bs.inputs['Specular IOR Level'].default_value=.28
 m['UnityMaterial']='Assets/Art/Models/Restaurant/RestaurantAtlas.mat';return m

def uv_assign(o,color):
 col,row=CELLS[color]
 for old in list(o.data.uv_layers):o.data.uv_layers.remove(old)
 uv=o.data.uv_layers.new(name='UVMap')
 # planar mapping within the broad swatch interior. Food shades sampled from existing atlas.
 for poly in o.data.polygons:
  n=poly.normal;axis=max(range(3),key=lambda a:abs(n[a]));axes=[a for a in range(3) if a!=axis]
  for li in poly.loop_indices:
   v=o.data.vertices[o.data.loops[li].vertex_index].co
   a=.5+max(-.3,min(.3,v[axes[0]]*1.5));b=.5+max(-.3,min(.3,v[axes[1]]*1.5))
   uv.data[li].uv=((col+.16+.68*a)/8,1-(row+.16+.68*b)/4)
 o.data.materials.append(MAT)

def mesh(name,verts,faces,color):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);uv_assign(ob,color);PARTS.append(ob);return ob

def orient_sheet(ob,up=True):
 # Recalculate normals can choose either direction on an open sheet; enforce its intended side.
 if sum(p.normal.z*p.area for p in ob.data.polygons)*(1 if up else -1)<0:
  bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(ob.data);bm.free();ob.data.update()
 return ob

def box(name,at,size,color,bevel=.003,rot=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=at);o=bpy.context.object;o.name=name;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:
  mod=o.modifiers.new('Broad single bevel','BEVEL');mod.width=min(bevel,min(size)*.22);mod.segments=1
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 o.rotation_euler.z=rot;uv_assign(o,color);PARTS.append(o);return o

def ell(name,at,size,color,sub=1,rot=0):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub,radius=1,location=at);o=bpy.context.object;o.name=name;o.scale=[v*.5 for v in size];o.rotation_euler.z=rot
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);uv_assign(o,color);PARTS.append(o);return o

def lathe(name,profile,color,n=16,at=(0,0,0),sx=1,sy=1):
 verts=[(at[0]+r*math.cos(2*PI*i/n)*sx,at[1]+r*math.sin(2*PI*i/n)*sy,at[2]+z) for r,z in profile for i in range(n)]
 faces=[]
 for j in range(len(profile)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;faces.append((a,b,b+n,a+n))
 return mesh(name,verts,faces,color)

def cyl(name,at,r,depth,color,n=10,r2=None):
 return lathe(name,[(0,-depth/2),(r,-depth/2),(r if r2 is None else r2,depth/2),(0,depth/2)],color,n,at)

def rod(name,a,b,r,color,n=6):
 mid=(Vector(a)+Vector(b))*.5;o=cyl(name,mid,r,(Vector(b)-Vector(a)).length,color,n)
 # cyl vertices created in world coordinates; rotate about its midpoint.
 mat=(Vector(b)-Vector(a)).to_track_quat('Z','Y').to_matrix().to_4x4()
 for v in o.data.vertices:v.co=mid+(mat.to_3x3()@(v.co-mid))
 return o

def torus(name,at,major,minor,color,n=12,m=4,scale=(1,1,1),rotate=None):
 verts=[]
 q=Matrix.Identity(3) if rotate is None else rotate
 for i in range(n):
  a=2*PI*i/n
  for j in range(m):
   b=2*PI*j/m;v=Vector(((major+minor*math.cos(b))*math.cos(a)*scale[0],(major+minor*math.cos(b))*math.sin(a)*scale[1],minor*math.sin(b)*scale[2]));verts.append(Vector(at)+q@v)
 faces=[(i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m) for i in range(n) for j in range(m)]
 return mesh(name,verts,faces,color)

def plate(at=(0,0,0),radius=.13,dirty=False,n=16):
 x,y,z=at
 lathe('Cream glazed plate',[(0,0),(.075,0),(radius,.013),(radius,.021),(radius-.016,.022),(.078,.009),(0,.009)],'cream',n,at)
 lathe('Teal rim stripe',[(radius-.004,.0215),(radius-.010,.023)],'teal',n,at)
 if dirty:
  ell('Sauce smear',(x-.025,y+.018,z+.011),(.071,.045,.003),'salmon')
  for i,(px,py) in enumerate([(.023,-.03),(-.04,-.025),(.015,.036)]):
   ell('Leftover crumb',(x+px,y+py,z+.016),(.016,.012,.009),'batter')
  rod('Fish bone',(x-.03,y-.007,z+.016),(x+.04,y+.018,z+.018),.002,'white',5)
  for j in range(3):
   px=x-.014+j*.018;py=y+j*.006
   rod('Bone rib',(px-.006,py-.013,z+.018),(px+.004,py+.012,z+.018),.0016,'white',4)

def lemon(at,scale=1):
 # Broad half-wheel with pale rind and four visible juicy wedges.
 x,y,z=at;r=.028*scale;n=8
 verts=[(x,y,z),(x,y,z+.013*scale)]
 for h in [0,.013*scale]:
  verts += [(x+r*math.cos(PI*i/n),y+r*math.sin(PI*i/n),z+h) for i in range(n+1)]
 faces=[]
 for i in range(n):faces.extend([(0,2+i,3+i),(1,12+i,11+i),(2+i,11+i,12+i,3+i)])
 faces.append((0,1,11,2));faces.append((0,10,19,1));mesh('Lemon rind',verts,faces,'cream')
 for i in range(4):
  a=.08+PI*i/4;b=PI*(i+1)/4-.08
  orient_sheet(mesh('Lemon flesh',[(x,y+.002,z+.0135*scale),(x+r*.82*math.cos(a),y+r*.82*math.sin(a),z+.0135*scale),(x+r*.82*math.cos(b),y+r*.82*math.sin(b),z+.0135*scale)],[(0,1,2)],'yellow'))

def herbs(at,scale=1):
 x,y,z=at
 for i in [-1,0,1]:ell('Parsley leaf',(x+i*.008*scale,y+abs(i)*.006*scale,z),(.023*scale,.011*scale,.006*scale),'green',rot=i*.6)

def fish(at=(0,0,.04),scale=1,iced=False):
 x,y,z=at
 ell('Silver catch' if iced else 'Roasted whole fish',(x,y,z),(.22*scale,.074*scale,.052*scale),'fish' if iced else 'batter',2)
 mesh('Tail fin',[(x-.08*scale,y,z),(x-.142*scale,y-.037*scale,z+.007*scale),(x-.125*scale,y,z+.005*scale),(x-.142*scale,y+.037*scale,z+.007*scale)],[(0,1,2),(0,2,3)],'steel' if iced else 'ochre')
 ell('Eye',(x+.078*scale,y-.022*scale,z+.018*scale),(.011*scale,.008*scale,.009*scale),'ink')
 if not iced:
  for i in range(3):box('Grill score',(x+(-.04+i*.035)*scale,y,z+.026*scale),(.007*scale,.048*scale,.002*scale),'crust',0,-.35)

def basket(at=(0,0,0),sx=.23,sy=.17):
 x,y,z=at
 box('Basket base',(x,y,z+.012),(sx*.85,sy*.82,.024),'bread',.006)
 # Slatted trapezoid sides, airy openings remain visible.
 for j in [-1,1]:
  for i in range(7):
   px=x+(i-3)*sx/7
   rod('Wicker rib',(px,y+j*sy*.36,z+.015),(px,y+j*sy*.5,z+.065),.004,'honey',5)
  rod('Basket long rim',(x-sx*.48,y+j*sy*.5,z+.065),(x+sx*.48,y+j*sy*.5,z+.065),.006,'crumb',6)
  rod('Basket lower weave',(x-sx*.45,y+j*sy*.44,z+.039),(x+sx*.45,y+j*sy*.44,z+.039),.0035,'bread',5)
 for j in [-1,1]:
  rod('Basket end rim',(x+j*sx*.48,y-sy*.5,z+.065),(x+j*sx*.48,y+sy*.5,z+.065),.006,'crumb',6)
 # Paper/linen lining readable above warm wood.
 box('Cream liner',(x,y,z+.036),(sx*.80,sy*.73,.005),'cream',.002,.06)

def glass(empty=False):
 # The shared game shader is opaque: show amber through the filled glass silhouette.
 lathe('Thick glass',[(0,0),(.034,0),(.038,.009),(.047,.138),(.044,.147),(.038,.147),(.031,.015),(0,.015)],'glass' if empty else 'gold',16)
 if not empty:lathe('Glass foot',[(0,0),(.034,0),(.037,.008),(.034,.012),(0,.012)],'glass',16)
 lathe('Pale glass rim',[(.038,.145),(.044,.147),(.046,.143)],'white',16)
 if empty:
  cyl('Last sip',(0,0,.017),.030,.002,'water',16)
  box('Glass highlight',(-.027,-.027,.075),(.005,.003,.09),'white',.001,-.3)
 else:
  lathe('Golden beer',[(0,.018),(.030,.018),(.040,.126),(0,.126)],'gold',16)
  lathe('Cream foam',[(0,.126),(.041,.126),(.042,.137),(.036,.142),(0,.142)],'cream',16)
  for x,y,r in [(-.016,.006,.01),(.016,-.009,.008),(.006,.02,.009)]:ell('Foam pillow',(x,y,.141),(r*2,r*2,.008),'white')
  box('Glass highlight',(-.029,-.027,.073),(.004,.003,.087),'white',.001,-.3)

def make_dish(key):
 if key=='FishAndChips':
  plate()
  ell('Battered cod',(-.043,.004,.044),(.086,.181,.054),'batter',2,rot=-.22)
  for i in range(4):ell('Batter ridge',(-.045+i*.006,-.06+i*.038,.064),(.060,.015,.011),'yellow',rot=.1)
  for i in range(8):
   x=.035+(i%3)*.018;y=-.062+(i//3)*.047
   box('Chunky chip',(x,y,.034+(i%2)*.008),(.014,.082,.015),'yellow',.003,-.3+(i%3)*.25)
  lemon((-.08,-.078,.023));herbs((.035,.073,.055))
 elif key=='Platter':
  box('Sharing board',(0,0,.014),(.43,.29,.028),'honey',.015)
  box('Board handle',(-.235,0,.014),(.065,.072,.028),'honey',.008)
  cyl('Handle inset',(-.247,0,.029),.011,.001,'darkwood',10)
  box('Cream serving paper',(.014,0,.030),(.36,.235,.004),'cream',.004)
  fish((-.045,.028,.064),.9)
  for x,y in [(.112,-.05),(.134,.037),(.055,-.084)]:
   ell('Mussel shell',(x,y,.046),(.057,.039,.025),'navy',rot=-.25)
   ell('Mussel meat',(x,y,.057),(.032,.019,.011),'orange',rot=-.25)
  lemon((.11,.083,.037),1.2);herbs((-.11,-.078,.037),1.3)
 elif key=='Crab':
  plate();ell('Cooked crab carapace',(0,.014,.056),(.13,.095,.057),'orange',2)
  for side in [-1,1]:
   for j in range(3):
    y=-.006+j*.026;rod('Crab leg',(side*.045,y,.048),(side*.085,y+.025,.031),.006,'orange',5);rod('Crab toe',(side*.085,y+.025,.031),(side*.099,y+.002,.026),.004,'batter',5)
   rod('Claw arm',(side*.043,-.016,.047),(side*.064,-.06,.049),.010,'orange',6)
   ell('Chunky crab claw',(side*.07,-.073,.055),(.045,.043,.03),'orange',rot=side*.25)
   # A dark cleft separates the two broad pincer tips.
   box('Claw cleft',(side*.07,-.09,.066),(.006,.02,.004),'crust',0,side*.25)
   rod('Eye stalk',(side*.024,-.025,.071),(side*.026,-.042,.079),.004,'orange',5)
   ell('Crab eye',(side*.026,-.044,.08),(.009,.009,.009),'ink')
  lemon((.07,.064,.023));herbs((-.06,.06,.025))
 elif key=='Calamari':
  plate()
  for i,(x,y,z) in enumerate([(-.047,-.04,.036),(.024,-.047,.037),(.056,.015,.037),(-.008,.029,.038),(-.06,.032,.039),(-.004,-.008,.056)]):
   torus('Golden calamari ring',(x,y,z),.023,.008,'batter',10,4,scale=(1, .82 if i%2 else 1.1,1))
  cyl('Teal aioli ramekin',(.061,.075,.037),.022,.036,'teal',10)
  cyl('Pale lemon aioli',(.061,.075,.057),.019,.002,'cream',10)
  lemon((-.058,.072,.025));herbs((.008,.002,.067))
 elif key=='Fries':
  basket(sx=.21,sy=.16)
  for i in range(13):
   x=(i%4-1.5)*.032;y=(i//4-1)*.037;z=.055+(i%3)*.009
   box('Golden chunky fry',(x,y,z),(.015,.098,.018),'yellow' if i%3 else 'batter',.003,(i%5-2)*.3)
  cyl('Sauce pot',(.076,.052,.071),.022,.031,'teal',10);cyl('Orange dipping sauce',(.076,.052,.088),.019,.002,'orange',10)
 elif key=='Bread':
  basket(sx=.24,sy=.18)
  for x,y,rot in [(-.040,.018,-.3),(.039,.025,.25)]:
   ell('Crusty bread roll',(x,y,.075),(.074,.14,.071),'crust',2,rot)
   for j in range(3):box('Pale bread score',(x,y+(j-1)*.03,.108),(.047,.007,.004),'crumb',.001,rot)
  ell('Bread slice',(.014,-.056,.07),(.10,.054,.022),'crumb',2,rot=.12)
  box('Butter pat',(-.063,-.057,.074),(.033,.027,.016),'yellow',.004)
 elif key=='Beer':glass(False)
 elif key=='Tea':
  # Compact tray makes both the cup and pot a single carryable serving.
  box('Tea tray',(0,0,.008),(.29,.19,.016),'teal',.012)
  cyl('Cream saucer',(-.074,-.026,.021),.060,.012,'cream',16)
  lathe('Teacup',[(0,0),(.024,0),(.034,.046),(.030,.049),(.026,.047),(.020,.009),(0,.009)],'cream',12,(-.074,-.026,.027))
  cyl('Tea surface',(-.074,-.026,.068),.027,.002,'tea',12)
  torus('Cup handle',(-.111,-.026,.052),.018,.0045,'cream',10,4,rotate=Matrix.Rotation(PI/2,3,'X'))
  lathe('Teapot',[(0,0),(.034,0),(.052,.024),(.050,.066),(.032,.091),(.025,.095),(0,.095)],'cream',12,(.052,.023,.016))
  cyl('Teal teapot lid',(.052,.023,.112),.033,.009,'teal',12);ell('Lid knob',(.052,.023,.122),(.018,.018,.016),'gold')
  torus('Teapot loop handle',(.112,.023,.069),.031,.007,'teal',12,4,scale=(.8,1,1),rotate=Matrix.Rotation(PI/2,3,'X'))
  # Stout tapered spout in profile.
  rod('Teapot spout',(.015,.023,.061),(-.014,.023,.082),.012,'cream',8)
  rod('Spout lip',(-.014,.023,.082),(-.022,.023,.104),.009,'cream',8)
  cyl('Spout opening',(-.022,.023,.106),.006,.002,'tea',8)


def basin():
 # Removable liner inside the measured .562 x .328m opening; max .48 x .28m.
 # Rectangular rounded-looking tray through two nested octagonal rings.
 rings=[(.215,.115,0),(.24,.14,.08),(.231,.131,.087),(.207,.107,.013)]
 verts=[]
 for x,y,z in rings:
  cut=.035
  verts.extend([(-x+cut,-y,z),(x-cut,-y,z),(x,-y+cut,z),(x,y-cut,z),(x-cut,y,z),(-x+cut,y,z),(-x,y-cut,z),(-x,-y+cut,z)])
 faces=[tuple(range(7,-1,-1))]
 for j in range(3):
  for i in range(8):faces.append((j*8+i,j*8+(i+1)%8,(j+1)*8+(i+1)%8,(j+1)*8+i))
 faces.append(tuple(range(24,32)));mesh('Sink basin insert',verts,faces,'steel')
 lathe('Drain strainer',[(0,0),(.022,0),(.022,.002),(0,.002)],'iron',12,(.125,.04,.014))
 for i in range(3):box('Drain slot',(.125+(i-1)*.009,.04,.017),(.003,.024,.001),'ink',0)

def make_service(key):
 if key.startswith('PlateStackDirty'):
  count=int(key[-1])
  for i in range(count):
   start=len(PARTS);plate(((-1)**i*.006,(-1)**(i//2)*.005,i*.018),dirty=i==count-1)
 elif key=='GlassEmpty':glass(True)
 elif key=='PlateStackClean':
  for i in range(6):plate((0,0,i*.018))
 elif key.startswith('SinkPile'):
  count=int(key[-1]);basin()
  # Three plates on the basin floor; second three form an uneven but stable upper pile.
  for i in range(count):
   x=[-.095,.095,-.01][i%3];y=[-.012,-.008,.012][i%3];z=.02+(i//3)*.052+i%3*.012
   start=len(PARTS);plate((0,0,0),.11,dirty=i>=max(0,count-3),n=12)
   transform=Matrix.Translation((x,y,z))@Matrix.Rotation([.12,-.14,.19][i%3],4,'Y')
   for ob in PARTS[start:]:ob.matrix_world=transform@ob.matrix_world
 elif key=='FishCrateOpen':
  box('Crate base',(0,0,.025),(.52,.36,.05),'wood',.008)
  for side in [-1,1]:
   for z in [.072,.137,.202]:
    box('Long slotted crate board',(0,side*.18,z),(.54,.024,.048),'honey',.004)
   for x in [-.25,.25]:box('Corner batten',(x,side*.17,.13),(.035,.035,.245),'wood',.004)
   for z in [.072,.137]:box('Crate end board',(side*.26,0,z),(.024,.34,.048),'honey',.004)
   # Split upper end board leaves an actual hand-grip slot.
   for y in [-.13,.13]:box('Hand-grip end',(side*.26,y,.202),(.024,.09,.048),'honey',.004)
   box('End grip rail',(side*.26,0,.232),(.024,.35,.014),'crumb',.003)
  box('Bed of ice',(0,0,.14),(.46,.29,.045),'ice',.012)
  rng=random.Random(62)
  for i in range(19):ell('Chunk of ice',(rng.uniform(-.22,.22),rng.uniform(-.13,.13),rng.uniform(.161,.185)),(.044,.034,.029),'white' if i%3 else 'water')
  for y,s in [(-.072,1.2),(.06,1.05)]:fish((.012,y,.192),s,True)
  # Teal fresh-catch panel, raised pale fish glyph (no tiny text).
  box('Crate label',(0,-.195,.121),(.15,.006,.072),'teal',.004)
  ell('Label fish',(0,-.200,.124),(.086,.006,.028),'cream')
  mesh('Label tail',[(-.033,-.204,.124),(-.061,-.204,.143),(-.061,-.204,.104)],[(0,1,2)],'cream')
 elif key.startswith('Gull_'):
  flap=key.endswith('Flap')
  for x in [-.043,.043]:
   rod('Orange gull shin',(x,0,.022),(x,.014,.122),.008,'ochre',6)
   # Webbed foot a solid broad orange triangle, planted on the floor.
   mesh('Webbed gull foot',[(x-.008,.019,.012),(x-.033,-.052,.002),(x+.025,-.05,.002),(x+.009,.019,.012),(x-.033,-.052,.009),(x+.025,-.05,.009)],[(0,1,2,3),(0,4,1),(1,4,5,2),(2,5,3),(0,3,5,4)],'ochre')
  ell('Gull pear body',(0,.012,.176),(.16,.245,.19),'cream',2)
  ell('White neck',(0,-.057,.257),(.098,.105,.12),'white',2)
  ell('Gull head',(0,-.084,.307),(.112,.119,.096),'white',2)
  # Bill points forward toward -Y and remains visible from service view.
  mesh('Yellow gull bill',[(-.026,-.126,.304),(.026,-.126,.304),(.019,-.19,.294),(-.019,-.19,.294),(-.023,-.126,.284),(.023,-.126,.284),(.012,-.187,.281),(-.012,-.187,.281)],[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],'yellow')
  box('Bill seam',(0,-.17,.289),(.036,.04,.002),'crust',0)
  for side in [-1,1]:
   ell('Black gull eye',(side*.051,-.11,.319),(.012,.012,.014),'ink')
   ell('Gull eye glint',(side*.055,-.113,.322),(.003,.003,.004),'cream')
   if flap:
    # Two bent soaring wings: thick shoulder, broad grey fan, black primaries.
    # Reverse winding on the mirrored side for the game's backface-culling shader.
    wingfaces=lambda fs:[tuple(reversed(f)) if side<0 else f for f in fs]
    verts=[(side*.05,.005,.225),(side*.18,-.02,.319),(side*.30,.006,.35),(side*.37,.12,.284),(side*.26,.113,.267),(side*.12,.10,.203)]
    orient_sheet(mesh('Raised grey wing',verts,wingfaces([(0,1,5),(1,2,4,5)]),'fish'))
    orient_sheet(mesh('Black primary fan',[verts[2],verts[3],(side*.405,.15,.254),(side*.344,.127,.245),(side*.314,.13,.235),verts[4]],wingfaces([(0,1,2,3,4,5)]),'ink'))
    # second layer provides thickness and readable reverse face.
    orient_sheet(mesh('Wing underside',[(x,y,z-.01) for x,y,z in verts],wingfaces([(5,1,0),(5,4,2,1),(4,3,2)]),'cream'),False)
    for j in range(2):rod('Wing feather shaft',(side*.23,.035+j*.03,.306),(side*.34,.105+j*.02,.27),.0027,'white',4)
   else:
    ell('Folded grey wing',(side*.066,.037,.198),(.046,.176,.087),'fish',2,rot=-side*.14)
    ell('Folded black wingtips',(side*.062,.111,.163),(.038,.075,.032),'ink',1)
    for j in range(2):rod('Folded white feather',(side*.086,.046+j*.025,.215),(side*.085,.071+j*.025,.198),.002,'white',4)
  orient_sheet(mesh('White tail fan',[(-.048,.092,.178),(.048,.092,.178),(.062167,.177,.149667),(-.062167,.177,.149667)],[(0,1,2,3)],'white'))
  orient_sheet(mesh('Tail black tips',[(-.062167,.177,.149667),(.062167,.177,.149667),(.065,.194,.144),(-.065,.194,.144)],[(0,1,2,3)],'ink'))
 elif key=='Spill':
  # Opaque atlas shader: flattened scalloped puddle, geometry highlights, no transparency dependency.
  rng=random.Random(18);n=20;verts=[(0,0,.004)]
  for i in range(n):
   a=i*2*PI/n;r=1+.13*math.sin(5*a)+.07*math.cos(3*a);verts.append((.26*r*math.cos(a),.18*r*math.sin(a),.004))
  mesh('Spilled drink puddle',verts,[(0,i+1,(i+1)%n+1) for i in range(n)],'puddle')
  for x,y,s in [(-.112,-.048,1),(.087,.092,.7)]:ell('Puddle reflection',(x,y,.005),(.067*s,.012*s,.0015),'glass')
  for i in range(4):ell('Floor food scrap',(-.10+i*.061,.025*math.sin(i*2),.009),(.025,.018,.014),'yellow' if i%2 else 'orange')
  for x,y in [(.29,.025),(-.25,-.13),(.16,-.18)]:ell('Stray droplet',(x,y,.003),(.025,.017,.002),'puddle')

DISHES=['FishAndChips','Platter','Crab','Calamari','Fries','Bread','Beer','Tea']
SERVICE=['PlateStackDirty2','PlateStackDirty4','GlassEmpty','PlateStackClean','SinkPile0','SinkPile3','SinkPile6','FishCrateOpen','Gull_Stand','Gull_Flap','Spill']

def clean_geometry(ob):
 # Lathe poles share a position: weld and discard zero-area faces, preserving UV seams.
 bm=bmesh.new();bm.from_mesh(ob.data)
 bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.0000001)
 bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.0000001)
 bm.to_mesh(ob.data);bm.free();ob.data.update()

def join_asset(name):
 bpy.ops.object.select_all(action='DESELECT')
 for o in PARTS:o.select_set(True)
 bpy.context.view_layer.objects.active=PARTS[0];bpy.ops.object.join();ob=bpy.context.object;ob.name=name;ob.data.name=name
 bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
 clean_geometry(ob)
 coords=[v.co for v in ob.data.vertices];lo=Vector([min(v[i] for v in coords) for i in range(3)]);hi=Vector([max(v[i] for v in coords) for i in range(3)])
 offset=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
 for v in ob.data.vertices:v.co-=offset
 ob.data.calc_loop_triangles()
 # Single material index, white vertex colour exactly matches atlas shader multiplication.
 for p in ob.data.polygons:p.material_index=0;p.use_smooth=False
 ob.data.materials.clear();ob.data.materials.append(MAT)
 c=ob.data.color_attributes.new(name='Color',type='BYTE_COLOR',domain='CORNER')
 for d in c.data:d.color=(1,1,1,1)
 ob['service_props_task']='SERVICE-PROPS-1';ob['Unity_up']='Y';ob['unit']='metre';ob['pivot']='bottom centre'
 return ob,dict(name=name,tris=len(ob.data.loop_triangles),size_xyz_blender_m=list(hi-lo),size_xyz_unity_m=[hi.x-lo.x,hi.z-lo.z,hi.y-lo.y],origin_offset_authored=list(offset),vertices=len(ob.data.vertices))

def export(ob,path):
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 export_fbx_bin.save(OP,bpy.context,filepath=str(path),use_selection=True,object_types={'MESH'},global_matrix=axis_conversion(to_forward='-Z',to_up='Y').to_4x4(),axis_up='Y',axis_forward='-Z',bake_space_transform=True,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,use_triangles=True,use_tspace=False,mesh_smooth_type='FACE',path_mode='STRIP',use_custom_props=True)
 # Explicit external object remap survives the project's material-import postprocessor.
 meta=Path(str(path)+'.meta')
 template=(PACK/'dishes/Restaurant_Dish_GrilledFish.fbx.meta').read_text()
 import re
 guid=re.search(r'^guid: (.+)$',meta.read_text(),re.M).group(1) if meta.exists() else uuid.uuid4().hex
 template=re.sub(r'^guid: .+$','guid: '+guid,template,flags=re.M)
 template=template.replace('  externalObjects: {}','''  externalObjects:
  - first:
      type: UnityEngine:Material
      assembly: UnityEngine.CoreModule
      name: RestaurantAtlas
    second: {fileID: 2100000, guid: 93ede68a78343aa4bbc6d4deed7baeec, type: 2}''')
 meta.write_text(template)

def flat_material(name,color,rough=.8):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return m

def reference():
 obs=load_fbx(PACK/'dishes/Restaurant_Dish_GrilledFish.fbx')
 # Legacy file is literally Y-up in Blender world coordinates. Rotate once into the Z-up review stage.
 mx=Matrix.Rotation(PI/2,4,'X')
 for o in obs:
  if not o.parent:o.matrix_world=mx@o.matrix_world
 for ob in obs:
  if ob.type!='MESH':continue
  for mat in ob.data.materials:
   if mat and mat.use_nodes:
    for node in mat.node_tree.nodes:
     if node.type=='TEX_IMAGE' and node.image:
      old=node.image.filepath.lower()
      path=PACK/'dishes/food-colormap-roast.png' if 'colormap' in old else PACK/'restaurantbits_texture-catchline.png'
      node.image=bpy.data.images.load(str(path),check_existing=True);node.image.pack()
  ob.name='REFERENCE_EXISTING_GrilledFish__022m'
 return obs

def setup_stage():
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=72;scene.cycles.use_denoising=True
 scene.render.resolution_x=900;scene.render.resolution_y=700;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
 scene.world=bpy.data.worlds.new('Cool harbour fill');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.25,.36,.43,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.38
 scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.35
 # Review-only honey timber floor. Colour is in linear space.
 ground=flat_material('REVIEW ONLY honey table',(.31,.16,.060))
 bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object;floor.name='REVIEW_ONLY_table';floor.location.z=-.001;floor.data.materials.append(ground)
 for name,loc,energy,color,size in [('Warm service practical',(-1.4,-1.0,2.5),170,(1,.74,.44),2),('Cool window fill',(1.5,.5,1.7),70,(.57,.79,1),2),('Soft rear rim',(0,1.8,2.1),90,(1,.91,.73),1.5)]:
  bpy.ops.object.light_add(type='AREA',location=loc);o=bpy.context.object;o.name='REVIEW_ONLY_'+name;o.data.energy=energy;o.data.color=color;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add();camera=bpy.context.object;camera.name='REVIEW_ONLY_Camera';camera.data.type='ORTHO';scene.camera=camera
 return camera

def place_camera(camera,target,scale,pitch):
 target=Vector(target);yaw=math.radians(12);p=math.radians(pitch)
 direction=Vector((math.sin(yaw)*math.cos(p),-math.cos(yaw)*math.cos(p),math.sin(p)))
 camera.location=target+direction*3;camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale

def render_item(ob,rec):
 refs=reference();camera=setup_stage()
 extent=rec['size_xyz_blender_m'];width=extent[0];height=extent[2];depth=extent[1]
 # Model and untouched reference are always at the same scale. Separate footprints avoid overlap.
 refx=width/2+.18
 for o in refs:
  if not o.parent:o.location.x+=refx
 target=((-.5*width+refx+.11)/2,0,height*.34)
 scale=max(width+.40,depth*1.35+height*.9,.57)*1.25
 place_camera(camera,target,scale,38)
 bpy.context.scene.render.filepath=str(REND/(rec['name']+'-service.png'));bpy.ops.render.render(write_still=True)
 # Close-up includes the same reference to make every plate/carry prop reviewable at equal scale.
 place_camera(camera,target,scale*.89,55)
 bpy.context.scene.render.filepath=str(REND/(rec['name']+'-close.png'));bpy.ops.render.render(write_still=True)
 rec['renders']=[str((REND/(rec['name']+'-'+s+'.png')).relative_to(R)) for s in ['service','close']]
 rec['service_camera_pitch_deg']=38;rec['close_camera_pitch_deg']=55
 bpy.context.scene['Review']='Left: new model. Right: existing 0.22m GrilledFish, unscaled. Honey table, warm practical and cool fill. NOT Unity runtime.'
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'blends'/(rec['name']+'.blend')),check_existing=False)


def main():
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 selected=args or DISHES+SERVICE
 records=json.loads((O/'manifest.json').read_text()) if (O/'manifest.json').exists() else []
 global MAT,PARTS
 for key in selected:
  bpy.ops.wm.read_factory_settings(use_empty=True);PARTS=[];MAT=atlas_material()
  dish=key in DISHES
  (make_dish if dish else make_service)(key)
  name='Restaurant_'+('Dish_' if dish else '')+key
  ob,rec=join_asset(name);limit=1500 if dish else 3000;assert rec['tris']<limit,(name,rec['tris'],limit)
  path=PACK/('dishes' if dish else 'service')/(name+'.fbx');export(ob,path)
  rec.update(file=str(path.relative_to(R)),triangle_limit_exclusive=limit,material='RestaurantAtlas',material_guid='93ede68a78343aa4bbc6d4deed7baeec',sha256=hashlib.sha256(path.read_bytes()).hexdigest(),render_review='pending human-visible image inspection by Codex 2')
  render_item(ob,rec)
  records=[x for x in records if x['name']!=name]+[rec];(O/'manifest.json').write_text(json.dumps(records,indent=2)+'\n')
  print('ITEM_RENDERED',name,rec['tris'],rec['size_xyz_unity_m'],flush=True)
 if not (PACK/'service.meta').exists():(PACK/'service.meta').write_text('fileFormatVersion: 2\nguid: '+uuid.uuid4().hex+'\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n')

if __name__=='__main__':main()
