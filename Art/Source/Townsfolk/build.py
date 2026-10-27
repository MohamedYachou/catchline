"""Five additive townsfolk on the unchanged original CrewRig skeleton/actions.
Never executes the old crew builder or writes Assets. Coordinates: -Y face, Z up.
"""
import bpy,sys,math,json,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector,Matrix
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/Townsfolk';D=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('town_geo',str(R/'Art/Source/build_crab_coast_props.py'));H=importlib.util.module_from_spec(sp);sp.loader.exec_module(H)
NAMES=['Town_OldWoman','Town_Kid','Town_Fisherman','Town_Shopkeeper','Town_Walker']
SOURCE=R/'Art/Models/CrewRig/CrewRig.blend';FBX=R/'Assets/Art/Models/Crew/CrewRig.fbx'
P={**H.PALETTE,'M_Skin':'#B9784B','M_OilskinYellow':'#E6AD38','M_HairChestnut':'#50392E','M_HairSilver':'#ADB6AF','M_Oilskin':'#E8B43A','M_Basket':'#B98F5E'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bind(rig,name):
 a=next(a for a in bpy.data.actions if a.name.split('|')[-1]==name);rig.animation_data_create();rig.animation_data.action=a
 if a.slots:rig.animation_data.action_slot=a.slots[0]
 return a
def init():
 bpy.ops.wm.open_mainfile(filepath=str(SOURCE));bpy.context.preferences.filepaths.save_version=0
 rig=bpy.data.objects['CrewRig'];rig.animation_data_clear();rig.data.pose_position='REST'
 for o in list(bpy.data.objects):
  if o!=rig:bpy.data.objects.remove(o,do_unlink=True)
 for m in list(bpy.data.materials):bpy.data.materials.remove(m)
 H.PALETTE.update(P)
 for n,c in P.items():H.MATERIALS[n]=H.material(n,c)
 bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1;bpy.context.scene.render.fps=24
 return rig
class Skin:
 def __init__(self,rig):self.g=H.Geometry();self.weights=[];self.rig=rig;self.bone='Hips';self.smooth=[]
 def part(self,method,*args,bone=None,smooth=False,weights=None,posed=None):
  n=len(self.g.vertices);f=len(self.g.faces);getattr(self.g,method)(*args)
  for i in range(n,len(self.g.vertices)):
   p=Vector(self.g.vertices[i]);w=weights(p) if weights else {bone or self.bone:1}
   if posed:
    b=self.rig.data.bones[posed];pb=self.rig.pose.bones[posed];p=(pb.matrix@b.matrix_local.inverted()).inverted()@p;self.g.vertices[i]=tuple(p)
   self.weights.append(w)
  self.smooth.extend([smooth]*(len(self.g.faces)-f))
 def ell(self,c,r,col,bone=None,seg=10,rings=3,smooth=True):self.part('ellipsoid',c,r,seg,rings,col,bone=bone,smooth=smooth)
 def tube(self,p,r,col,bone=None,sides=8,weights=None):self.part('tube',p,r,sides,col,bone=bone,weights=weights)
 def box(self,c,s,col,bone=None):self.part('box',c,s,col,bone=bone)
 def lathe(self,rings,col,bone=None,segments=12,cap=True):
  # rings are (z,rx,ry,cy), seam closed; no textures or paper-thin layers.
  vs=[(rx*math.cos(a*math.tau/segments),cy+ry*math.sin(a*math.tau/segments),z) for z,rx,ry,cy in rings for a in range(segments)]
  fs=[(j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i) for j in range(len(rings)-1) for i in range(segments)]
  if cap:fs+=[tuple(reversed(range(segments))),tuple(range((len(rings)-1)*segments,len(rings)*segments))]
  self.part('add',vs,fs,col,bone=bone)
 def finish(self,name,scale=1):
  if scale!=1:
   # Fit the scaled child's actual Walk-neutral silhouette back into the fixed
   # adult bind skeleton; a raw uniform rest shrink detaches animated sleeves.
   self.rig.data.pose_position='POSE';bind(self.rig,'Walk');bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
   ms={b.name:self.rig.pose.bones[b.name].matrix@b.matrix_local.inverted() for b in self.rig.data.bones}
   fitted=[]
   for p,w in zip(self.g.vertices,self.weights):
    m=Matrix(tuple(tuple(sum(ms[n][a][b]*v for n,v in w.items()) for b in range(4)) for a in range(4)))
    fitted.append(tuple(m.inverted()@((m@Vector(p))*scale)))
   self.g.vertices=fitted;self.rig.animation_data_clear();self.rig.data.pose_position='REST'
  else:self.g.vertices=[tuple(v) for v in self.g.vertices]
  o=self.g.object(name,self.rig,bpy.context.scene.collection)
  # Delete unused material slots without changing face assignments.
  used=sorted(set(p.material_index for p in o.data.polygons));ms=[o.data.materials[i] for i in used];indices=[used.index(p.material_index) for p in o.data.polygons];o.data.materials.clear()
  for m in ms:o.data.materials.append(m)
  for p,i,sm in zip(o.data.polygons,indices,self.smooth):p.material_index=i;p.use_smooth=sm
  for b in self.rig.data.bones:o.vertex_groups.new(name=b.name)
  for i,w in enumerate(self.weights):
   for n,v in w.items():
    if v>0:o.vertex_groups[n].add([i],v,'REPLACE')
  m=o.modifiers.new('CrewSkin','ARMATURE');m.object=self.rig;m.use_deform_preserve_volume=False
  o['mesh_scale_only']=scale;o['animation_contract']='Original CrewRig skeleton and actions; sibling mesh, no per-person rig'
  return o

def blend(a,b,t):t=max(0,min(1,t));return {a:1-t,b:t}
def armweights(side,p):
 if abs(p.x)<.20:return blend('Spine1',side+'Arm',(abs(p.x)-.10)/.10)
 return blend(side+'Arm',side+'ForeArm',(abs(p.x)-.245)/.07)
def legweights(side,p):return blend(side+'Leg',side+'UpLeg',(p.z-.155)/.05)
def torso(s,col):
 s.ell((0,0,.427),(.142,.098,.145),col,'Spine',seg=12,rings=4,smooth=False)
 s.ell((0,0,.31),(.132,.092,.070),col,'Hips',seg=10,rings=3,smooth=False)
def limbs(s,sleeve='M_HullNavy',pants='M_HullNavy',rolled=False,boots=True,stripes=False):
 for sign,side in [(1,'Left'),(-1,'Right')]:
  if stripes:
   xs=[.04,.10,.14,.17,.20,.225,.25,.275,.30,.325,.35,.37,.39];profile=[(.04,.045),(.10,.052),(.17,.060),(.24,.053),(.28,.050),(.35,.044),(.39,.037)]
   def radius(x):
    for (a,ra),(b,rb) in zip(profile,profile[1:]):
     if a<=x<=b:return ra+(rb-ra)*(x-a)/(b-a)
   first=len(s.g.faces);s.tube([(sign*x,0,.49+min(1,(x-.04)/.13)*.02) for x in xs],[radius(x) for x in xs],sleeve,weights=lambda p,k=side:armweights(k,p))
   for j in range(len(xs)-1):
    if j%2:
     for k in range(8):s.g.colours[first+2+j*8+k]='M_HullNavy'
  else:
   xs=[.04,.10,.17,.24,.28,.33] if rolled else [.04,.10,.17,.24,.28,.35,.39]
   radii=[.045,.052,.060,.053,.050,.046] if rolled else [.045,.052,.060,.053,.050,.044,.037]
   s.tube([(sign*x,0,.49+min(1,(x-.04)/.13)*.02) for x in xs],radii,sleeve,weights=lambda p,k=side:armweights(k,p))
  if rolled:
   s.tube([(sign*.31,0,.51),(sign*.35,0,.51)],[.050,.050],'M_RailIvory',side+'ForeArm')
   s.tube([(sign*.35,0,.51),(sign*.397,0,.51)],[.038,.033],'M_Skin',side+'ForeArm')
  s.ell((sign*.421,-.003,.507),(.045,.041,.040),'M_Skin',side+'Hand',seg=8,rings=3)
  s.ell((sign*.407,-.033,.487),(.021,.025,.021),'M_Skin',side+'Hand',seg=6,rings=2)
  s.tube([(sign*.085,0,.316),(sign*.085,0,.24),(sign*.085,0,.18),(sign*.085,0,.10)],[.065,.058,.050,.044],pants,weights=lambda p,k=side:legweights(k,p))
  if boots:s.tube([(sign*.085,0,.09),(sign*.085,0,.155)],[.052,.053],'M_Rubber',side+'Leg')
  s.ell((sign*.085,-.03,.052),(.064,.102,.052),'M_Rubber',side+'Foot',seg=8,rings=3,smooth=False)
def face(s,old=False):
 s.ell((0,0,.76),(.173,.151,.19),'M_Skin','Head',seg=16,rings=7)
 s.ell((0,0,.567),(.054,.051,.068),'M_Skin','Neck',seg=8,rings=3)
 for sign in [-1,1]:
  if not old:s.ell((sign*.164,0,.744),(.027,.026,.041),'M_Skin','Head',seg=8,rings=3)
  s.ell((sign*.061,-.141,.774),(.013,.010,.021),'M_Rubber','Head',seg=8,rings=3)
  s.ell((sign*.065,-.151,.781),(.0038,.0028,.0042),'M_RailIvory','Head',seg=6,rings=2)
  # Hair-colour brows softened for civilian women; no drawn outline.
  s.ell((sign*.064,-.136,.809),(.021,.008,.006),'M_HairSilver' if old else 'M_HairChestnut','Head',seg=6,rings=2)
 s.ell((0,-.151,.745),(.022,.029,.025),'M_Skin','Head',seg=8,rings=3)
 s.tube([(-.025,-.149,.712),(0,-.159,.703),(.025,-.149,.712)],[.0038,.0038,.0038],'M_Rubber','Head',sides=5)
 if old:
  for sign in [-1,1]:s.tube([(sign*.076,-.140,.742),(sign*.092,-.133,.736)],[.0023,.0023],'M_HairSilver','Head',sides=4)
def cap(s,col,style='beanie'):
 if style=='sou':
  # Crown, rolled brim with lower rear skirt; back is +Y.
  s.lathe([(.895,.174,.153,0),(.96,.16,.14,0),(1.002,.112,.10,0),(1.014,.045,.044,0)],col,'Head',segments=12)
  n=16;vs=[]
  for rad in [0,1]:
   for i in range(n):
    a=i*math.tau/n;rear=max(0,math.sin(a));vs.append(((.16+rad*.063)*math.cos(a),(.14+rad*.067)*math.sin(a),.909-rad*(.012+.044*rear)))
  s.part('add',vs,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],col,bone='Head')
  s.lathe([(.907,.174,.153,0),(.923,.170,.150,0)],'M_OilskinYellow','Head',segments=12)
 elif style=='cap':
  s.lathe([(.886,.17,.15,.002),(.935,.151,.138,.002),(.963,.09,.085,.002),(.973,.025,.025,.002)],col,'Head')
  s.ell((0,-.148,.893),(.139,.094,.014),col,'Head',seg=10,rings=2,smooth=False)
  s.lathe([(.885,.172,.151,.002),(.903,.169,.149,.002)],'M_RailIvory','Head')
 else:
  s.lathe([(.864,.179,.158,0),(.898,.181,.159,0),(.951,.151,.135,0),(.989,.088,.082,0),(1.001,.025,.025,0)],col,'Head')
  s.lathe([(.86,.183,.162,0),(.898,.183,.162,0)],col,'Head')
  # Broad seam/rib geometry on the roll reads as knitted, no separate material.
  for i in range(12):
   a=i*math.tau/12;s.tube([(.185*math.cos(a),.164*math.sin(a),.864),(.185*math.cos(a),.164*math.sin(a),.892)],[.003,.003],col,'Head',sides=4)
def shell(s,col,front=.85,back=.67,rx=.184,ry=.164,rz=.211):
 n=16;vs=[(0,0,.76+rz)];fs=[]
 for j in range(1,5):
  for i in range(n):
   a=i*math.tau/n;f=max(0,-math.sin(a));edge=back+(front-back)*f**3;angle=math.acos((edge-.76)/rz)*j/4
   vs.append((rx*math.sin(angle)*math.cos(a),ry*math.sin(angle)*math.sin(a),.76+rz*math.cos(angle)))
 fs.extend((0,1+i,1+(i+1)%n) for i in range(n))
 for j in range(3):fs.extend((1+j*n+i,1+j*n+(i+1)%n,1+(j+1)*n+(i+1)%n,1+(j+1)*n+i) for i in range(n))
 s.part('add',vs,fs,col,bone='Head');return vs,n

def hair(s,col='M_HairChestnut',long=False):
 shell(s,col,front=.846,back=.661 if long else .749,rx=.190,ry=.174,rz=.212)
 s.ell((-.062,-.119,.853),(.09,.035,.028),col,'Head',seg=8,rings=2,smooth=False)
def scarf(s):
 vs,n=shell(s,'M_SeaTeal',front=.852,back=.660)
 # Ivory edging uses the exact opening curve, including front hairline and cheeks.
 path=[tuple(Vector(v)*1.004) for v in vs[1+3*n:]];path.append(path[0]);s.tube(path,[.005]*len(path),'M_RailIvory','Head',sides=4)
 s.ell((0,-.105,.603),(.028,.024,.026),'M_SeaTeal','Head',seg=8,rings=2,smooth=False)
 for sign in [-1,1]:s.tube([(0,-.10,.602),(sign*.045,-.09,.575)],[.014,.007],'M_SeaTeal','Head',sides=5)
def basket(s):
 # Design hanging in original Walk frame1; inverse-skin into unchanged bind pose.
 rig=s.rig;rig.data.pose_position='POSE';bind(rig,'Walk');bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
 kw={'bone':'RightForeArm','posed':'RightForeArm'}
 # Basket body is an octagonal closed woven pail with open top and actual inner wall.
 x,y,z=-.285,-.027,.265;n=10;vs=[]
 for h,rx,ry in [(0,.065,.049),(.105,.08,.059),(.105,.068,.048),(.018,.055,.039)]:
  vs.extend((x+rx*math.cos(i*math.tau/n),y+ry*math.sin(i*math.tau/n),z+h) for i in range(n))
 fs=[]
 for k in range(3):fs.extend((k*n+i,k*n+(i+1)%n,(k+1)*n+(i+1)%n,(k+1)*n+i) for i in range(n))
 fs.extend([tuple(reversed(range(n))),tuple(range(3*n,4*n))]);s.part('add',vs,fs,'M_Basket',**kw)
 for h in [.026,.065,.105]:
  path=[(x+(.065+.015*h/.105+.002)*math.cos(i*math.tau/n),y+(.049+.010*h/.105+.002)*math.sin(i*math.tau/n),z+h) for i in range(n+1)];s.part('tube',path,[.0035]*(n+1),4,'M_Rope',**kw)
 # Side-to-side arch passes over the forearm and descends to both basket rims.
 path=[(x+.077*math.cos(math.pi*i/8),y,z+.101+.107*math.sin(math.pi*i/8)) for i in range(9)];s.part('tube',path,[.007]*9,6,'M_Basket',**kw)
 rig.animation_data_clear();rig.data.pose_position='REST'
def oldwoman(rig):
 s=Skin(rig);torso(s,'M_HullNavy');limbs(s,'M_HullNavy');face(s,True);s.ell((-.055,-.120,.849),(.08,.027,.022),'M_HairSilver','Head',seg=8,rings=2,smooth=False);scarf(s)
 coat=[(.225,.185,.122,0),(.32,.16,.108,0),(.43,.148,.104,0),(.53,.123,.091,0),(.555,.05,.044,0)]
 s.lathe(coat,'M_HullNavy','Spine',segments=12)
 def front(x,z):
  for (za,xa,ya,_),(zb,xb,yb,_) in zip(coat,coat[1:]):
   if za<=z<=zb:
    t=(z-za)/(zb-za);rx=xa+(xb-xa)*t;ry=ya+(yb-ya)*t
    ring=[(rx*math.cos(i*math.tau/12),ry*math.sin(i*math.tau/12)) for i in range(6,13)]
    for (ax,ay),(bx,by) in zip(ring,ring[1:]):
     if ax<=x<=bx:return ay+(by-ay)*(x-ax)/(bx-ax)
  raise ValueError((x,z))
 for z in [.30,.37,.44,.51]:s.ell((0,front(0,z)-.002,z),(.008,.006,.008),'M_BandIvory','Spine',seg=6,rings=2)
 # Broad turned lapels and two coat pockets.
 for sign in [-1,1]:
  path=[(sign*x,front(sign*x,z)-.002,z) for x,z in [(.035,.54),(.06,.49),(.023,.45)]]
  s.tube(path,[.012,.015,.008],'M_SeaTeal','Spine',sides=4)
  outline=[(sign*.105-.0245,.308),(sign*.105+.0245,.308),(sign*.105+.0245,.352),(sign*.105-.0245,.352)]
  vs=[(x,front(x,z)+offset,z) for offset in [.002,-.006] for x,z in outline]
  s.part('add',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'M_SeaTeal',bone='Spine')
 basket(s);return s.finish('Town_OldWoman')
def kid(rig):
 s=Skin(rig)
 rings=[(.285,.160,.109,0),(.335,.150,.106,0),(.36,.147,.104,0),(.385,.144,.103,0),(.41,.145,.103,0),(.435,.143,.102,0),(.46,.138,.098,0),(.485,.128,.091,0),(.51,.112,.080,0),(.535,.080,.060,0),(.555,.05,.044,0)]
 first=len(s.g.faces);s.lathe(rings,'M_RailIvory','Spine',segments=12)
 for j in range(len(rings)-1):
  if j%2:
   for k in range(12):s.g.colours[first+j*12+k]='M_HullNavy'
 s.ell((0,0,.31),(.132,.092,.070),'M_HullNavy','Hips',seg=10,rings=3,smooth=False)
 limbs(s,'M_RailIvory',stripes=True);face(s);hair(s,long=True);cap(s,'M_SeaTeal','cap')
 return s.finish('Town_Kid',.75)
def fisherman(rig):
 s=Skin(rig);torso(s,'M_Oilskin');limbs(s,'M_Oilskin','M_Oilskin');face(s);hair(s);cap(s,'M_Oilskin','sou')
 coat=[(.29,.134,.096,0),(.36,.145,.105,0),(.46,.145,.103,0),(.535,.11,.082,0)]
 s.lathe(coat,'M_Oilskin','Spine')
 def front(x,z):
  for (za,xa,ya,_),(zb,xb,yb,_) in zip(coat,coat[1:]):
   if za<=z<=zb:
    t=(z-za)/(zb-za);rx=xa+(xb-xa)*t;ry=ya+(yb-ya)*t
    ring=[(rx*math.cos(i*math.tau/12),ry*math.sin(i*math.tau/12)) for i in range(6,13)]
    for (ax,ay),(bx,by) in zip(ring,ring[1:]):
     if ax<=x<=bx:return ay+(by-ay)*(x-ax)/(bx-ax)
  raise ValueError((x,z))
 # Zipper and pocket relief follow the jacket, rather than floating flat boxes.
 for za,zb in zip([.31,.36,.46],[.36,.46,.512]):
  outline=[(-.0055,za),(.0055,za),(.0055,zb),(-.0055,zb)]
  vs=[(x,front(x,z)+offset,z) for offset in [.002,-.004] for x,z in outline]
  s.part('add',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'M_HullNavy',bone='Spine')
 for sign in [-1,1]:
  outline=[(sign*.08-.0315,.345),(sign*.08+.0315,.345),(sign*.08+.0315,.385),(sign*.08-.0315,.385)]
  vs=[(x,front(x,z)+offset,z) for offset in [.002,-.006] for x,z in outline]
  s.part('add',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'M_OilskinYellow',bone='Spine')
 # Small chestnut moustache; friendly bead eyes remain crew-sized.
 for sign in [-1,1]:s.ell((sign*.016,-.157,.723),(.023,.008,.010),'M_HairChestnut','Head',seg=6,rings=2,smooth=False)
 return s.finish('Town_Fisherman')
def shopkeeper(rig):
 s=Skin(rig);torso(s,'M_SeaTeal');limbs(s,'M_SeaTeal',rolled=True);face(s);hair(s,long=True)
 s.ell((0,.142,.84),(.075,.055,.067),'M_HairChestnut','Head',seg=10,rings=3,smooth=False)
 # Ivory apron is a continuous skirt/bib front, plus tied belt/back bow.
 verts=[(-.105,-.108,.31),(.105,-.108,.31),(-.077,-.102,.47),(.077,-.102,.47),(-.068,-.078,.527),(.068,-.078,.527)]
 s.part('add',verts,[(0,1,3,2),(2,3,5,4)],'M_RailIvory',bone='Spine')
 s.box((0,-.113,.375),(.084,.015,.046),'M_BandIvory','Spine')
 s.lathe([(.388,.146,.104,0),(.404,.146,.104,0)],'M_BandIvory','Spine')
 for sign in [-1,1]:s.tube([(sign*.068,-.077,.527),(sign*.073,0,.555),(sign*.065,.085,.515),(sign*.06,.104,.46),(sign*.06,.103,.398)],[.009]*5,'M_RailIvory','Spine',sides=4)
 s.ell((0,.104,.397),(.018,.015,.013),'M_BandIvory','Spine',seg=6,rings=2)
 for sign in [-1,1]:s.tube([(0,.104,.397),(sign*.04,.103,.37),(sign*.038,.095,.344)],[.009,.007,.004],'M_RailIvory','Spine',sides=4)
 return s.finish('Town_Shopkeeper')
def walker(rig):
 s=Skin(rig)
 rows=[(.285,.160,.109,0),(.313,.154,.108,0),(.333,.147,.104,0),(.385,.144,.103,0),(.43,.143,.102,0),(.46,.138,.098,0),(.49,.125,.089,0),(.512,.111,.079,0),(.538,.088,.065,0),(.552,.05,.044,0)]
 first=len(s.g.faces);s.lathe(rows,'M_SeaTeal','Spine')
 for j in [0,7]:
  for k in range(12):s.g.colours[first+j*12+k]='M_BandIvory'
 s.ell((0,0,.295),(.12,.084,.05),'M_HullNavy','Hips',seg=10,rings=3,smooth=False)
 limbs(s,'M_SeaTeal');face(s);hair(s,long=True);cap(s,'M_SafetyOrange')
 # Cuffs and small raised knit stitches fitted to the actual faceted surface.
 for sign,side in [(1,'Left'),(-1,'Right')]:s.tube([(sign*.37,0,.51),(sign*.39,0,.51)],[.044,.042],'M_BandIvory',side+'ForeArm')
 def front(x,z):
  for (za,xa,ya,_),(zb,xb,yb,_) in zip(rows,rows[1:]):
   if za<=z<=zb:
    t=(z-za)/(zb-za);rx=xa+(xb-xa)*t;ry=ya+(yb-ya)*t
    ring=[(rx*math.cos(i*math.tau/12),ry*math.sin(i*math.tau/12)) for i in range(6,13)]
    for (ax,ay),(bx,by) in zip(ring,ring[1:]):
     if ax<=x<=bx:return ay+(by-ay)*(x-ax)/(bx-ax)
  raise ValueError((x,z))
 for x in [-.092,-.046,0,.046,.092]:
  outline=[(x,.481),(x+.014,.465),(x,.449),(x-.014,.465)]
  vs=[(a,front(a,z)-.0006,z) for a,z in outline]+[(x,front(x,.465)-.0025,.465)]
  s.part('add',vs,[(0,1,4),(1,2,4),(2,3,4),(3,0,4),(3,2,1,0)],'M_BandIvory',bone='Spine')
 return s.finish('Town_Walker')
def snap():
 rig=bpy.data.objects['CrewRig'];out={}
 for o in rig.children:
  if o.type!='MESH':continue
  o.data.calc_loop_triangles();vs=[o.matrix_world@v.co for v in o.data.vertices];out[o.name]={'vertices':len(vs),'triangles':len(o.data.loop_triangles),'materials':sorted({m.name for m in o.data.materials}),'bounds':[[min(v[i] for v in vs) for i in range(3)],[max(v[i] for v in vs) for i in range(3)]],'parent':o.parent.name,'object_scale':list(o.scale),'mesh_scale_only':o.get('mesh_scale_only')}
 return out
def run():
 O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True);rig=init();[fn(rig) for fn in [oldwoman,kid,fisherman,shopkeeper,walker]]
 print('BUDGETS',[(n,v['triangles']) for n,v in snap().items()],flush=True)
 for n,v in snap().items():assert v['triangles']<=2500,(n,v['triangles'])
 bind(rig,'Walk');rig.data.pose_position='REST';bpy.context.scene.frame_set(1)
 rig['contract']='Unmodified original CrewRig bone rest matrices, hierarchy, armature object name and all eleven actions'
 bpy.ops.wm.save_as_mainfile(filepath=str(O/'Townsfolk.blend'))
 bpy.ops.object.select_all(action='DESELECT');rig.select_set(True)
 for o in rig.children:o.select_set(True)
 bpy.context.view_layer.objects.active=rig
 rig.data.pose_position='POSE'
 bpy.ops.export_scene.fbx(filepath=str(O/'Townsfolk.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=True,bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,use_custom_props=True,mesh_smooth_type='FACE')
 row={'people':snap(),'sha256':{e:sha(O/('Townsfolk.'+e)) for e in ['blend','fbx']},'palette':P,'fps':24,'female_characters':['Town_OldWoman','Town_Kid','Town_Shopkeeper','Town_Walker'],'male_characters':['Town_Fisherman']};(O/'metrics/build.json').write_text(json.dumps(row,indent=2)+'\n')
 deps=[SOURCE,FBX,R/'Art/Source/build_crab_coast_props.py',R/'Art/Source/Skerries/render.py',R/'Art/Source/HarbourV2/audit.py'];(O/'metrics/dependencies.json').write_text(json.dumps({p.relative_to(R).as_posix():sha(p) for p in deps},indent=2)+'\n')
 print('TOWNSFOLK BUILD PASS',[(n,v['triangles']) for n,v in row['people'].items()],flush=True)
if __name__=='__main__':run()
