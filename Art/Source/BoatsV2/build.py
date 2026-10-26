"""Additive boat refinement. Run Windows Blender --background --python build.py -- Rowboat|Skiff.
Never writes Assets, Unity, original models or gameplay code. Geometry in source world X/right,-Y/bow,Z/up.
"""
import bpy,bmesh,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[3]; NAME=sys.argv[sys.argv.index('--')+1]; OUT=R/'Art/Models/BoatsV2'/NAME;OUT.mkdir(parents=True,exist_ok=True)
PALETTE={'M_HullNavy':'173F57','M_HullBlue':'2A6685','M_ClinkerRecess':'0E2C40','M_DeckWood':'C58B50','M_WoodHighlight':'DFB77A','M_WoodRecess':'8C5A36','M_RailIvory':'F3F0DC','M_SafetyOrange':'E36A35','M_Steel':'8FA6AC','M_Rope':'D1AF76','M_Rubber':'28343B'}
def lin(x):return x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4
def mat(n):
 m=bpy.data.materials.get(n)
 if m is None:m=bpy.data.materials.new(n)
 c=tuple(lin(int(PALETTE[n][i:i+2],16)/255) for i in (0,2,4))+(1,);m.diffuse_color=c;m.use_nodes=True;bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=c;bs.inputs['Roughness'].default_value=.8;bs.inputs['Metallic'].default_value=0
 return m
class Geo:
 def __init__(self):self.v=[];self.f=[];self.m=[]
 def add(self,v,f,m):
  k=len(self.v);self.v+=list(v);self.f += [tuple(k+i for i in p) for p in f];self.m += [m]*len(f)
 def box(self,c,s,m):
  x,y,z=c;a,b,d=[v/2 for v in s];self.add([(x+sx*a,y+sy*b,z+sz*d) for sx,sy,sz in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
 def beam(self,a,b,w,h,m):
  a,b=Vector(a),Vector(b);u=(b-a).normalized();v=u.cross(Vector((0,0,1))).normalized();v=Vector((1,0,0)) if v.length<.1 else v;t=u.cross(v).normalized();self.add([tuple(p+v*sv*w/2+t*st*h/2) for p in (a,b) for sv,st in [(-1,-1),(1,-1),(1,1),(-1,1)]],[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],m)
 def mesh(self,name,obj=None,bevel=0):
  if obj is None:
   obj=bpy.data.objects.new(name,bpy.data.meshes.new(name));bpy.context.scene.collection.objects.link(obj);obj.parent=ROOT;obj.matrix_world=Matrix.Identity(4)
  me=bpy.data.meshes.new(name+'_Refined');inv=obj.matrix_world.inverted();me.from_pydata([inv@Vector(v) for v in self.v],[],self.f);me.update();obj.data=me
  names=list(dict.fromkeys(self.m))
  for n in names:me.materials.append(mat(n))
  for p,m in zip(me.polygons,self.m):p.material_index=names.index(m)
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
  if bevel:
   bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Small working edge bevel','BEVEL');mod.width=bevel;mod.segments=1;mod.affect='EDGES';bpy.ops.object.modifier_apply(modifier=mod.name)
  bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY');bm.to_mesh(obj.data);bm.free()
  return obj

def ring(g,a,b,m):
 n=len(a);g.add(a+b,[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],m)
def stats(obs):
 return {o.name:{'type':o.type,'parent':o.parent.name if o.parent else None,'world':[list(r) for r in o.matrix_world],'local':[list(r) for r in o.matrix_local],'triangles':sum(len(p.vertices)-2 for p in o.data.polygons) if o.type=='MESH' else 0} for o in obs}
bpy.ops.wm.read_factory_settings(use_empty=True);src=R/f'Assets/Art/Models/Boats/{NAME}.fbx';bpy.ops.import_scene.fbx(filepath=str(src));bpy.context.view_layer.update();ROOT=bpy.data.objects.get('Catchline_'+NAME);oldobs=list(bpy.context.scene.objects);before=stats(oldobs)
# Preserve world and local matrices of all imported nodes. Working deck, sockets and moving parts untouched.
isrow=NAME=='Rowboat';half=1.2 if isrow else 1.75;stern=2.1 if isrow else 3.;bow=2.1 if isrow else 3.5;bottom=-.45 if isrow else -.65
# More stations down the long sides: a quiet round-bilged silhouette while retaining the build rectangle.
if isrow:
 plan=[(-.90,2.1),(.90,2.1),(1.10,1.85),(1.20,1.45),(1.23,.75),(1.24,0),(1.23,-.75),(1.21,-1.48),(1.04,-1.72),(.69,-1.96),(.30,-2.10),(0,-2.14),(-.30,-2.10),(-.69,-1.96),(-1.04,-1.72),(-1.21,-1.48),(-1.23,-.75),(-1.24,0),(-1.23,.75),(-1.20,1.45),(-1.10,1.85)]
else:
 plan=[(-1.48,3),(1.48,3),(1.68,2.76),(1.78,2.5),(1.81,1.5),(1.82,0),(1.81,-1.5),(1.78,-2.5),(1.52,-2.82),(1.11,-3.14),(.61,-3.40),(.23,-3.51),(0,-3.54),(-.23,-3.51),(-.61,-3.40),(-1.11,-3.14),(-1.52,-2.82),(-1.78,-2.5),(-1.81,-1.5),(-1.82,0),(-1.81,1.5),(-1.78,2.5),(-1.68,2.76)]
n=len(plan)
def sheer(y):
 return (.43 if isrow else .44)+(.15 if isrow else .18)*(max(0,-y)/bow)**2+.08*(max(0,y)/stern)**2
# Five clinker courses; three upper laps have a dark 20mm vertical reveal and 25mm proud edge.
def level(t,proud=0):
 sx=.65+.35*t**.62;sy=.70+.30*t
 deckhalf=1.5 if isrow else 2.5
 return [(x*sx+(proud*x/half),(y if abs(y)<=deckhalf else math.copysign(deckhalf+(abs(y)-deckhalf)*sy,y)),bottom+(sheer(y)-bottom)*t) for x,y in plan]
g=Geo();last=level(0)
for k in range(1,6):
 t=k/5;upper=level(t);ring(g,last,upper,'M_HullNavy')
 if k<5:
  proud=.014 if k==1 else .025
  lip=level(t,proud);ring(g,upper,lip,'M_ClinkerRecess')
  if k>=2:
   reveal=[(x,y,z+.020) for x,y,z in lip];ring(g,lip,reveal,'M_ClinkerRecess');last=reveal
  else:last=lip
 else:last=upper
# Inner lining follows the same exterior surface with a real inward offset.
outer=level(1)
def lining(t):return [(x*.942,y*.976,z-.012) for x,y,z in level(t)]
inner=lining(1);ring(g,outer,inner,'M_WoodHighlight');prev=inner
for k in range(1,5):
 t=1-.58*k/4;innerlow=lining(t);ring(g,prev,innerlow,'M_DeckWood')
 if k<4:
  seam=lining(t-.007);ring(g,innerlow,seam,'M_WoodRecess');prev=seam
 else:prev=innerlow
# bottom shell closed on underside; inner floor hidden below unchanged build deck.
g.add(level(0),[tuple(reversed(range(n)))],'M_HullNavy');g.add(prev,[tuple(range(n))],'M_DeckWood');g.mesh('Hull',bpy.data.objects['Hull'])
# Solid swept rails use a compact rectangular cross section, no degenerate bevel joins.
g=Geo(); railA=[];railB=[];railC=[];railD=[]
for x,y in plan:
 z=sheer(y)+.025;railA.append((x*1.012,y*1.006,z-.018));railB.append((x*1.012,y*1.006,z+.048));railC.append((x*.90,y*.965,z+.048));railD.append((x*.90,y*.965,z-.018))
for a,b,m in [(railA,railB,'M_RailIvory'),(railB,railC,'M_RailIvory'),(railC,railD,'M_DeckWood'),(railD,railA,'M_RailIvory')]:ring(g,a,b,m)
# A timber rubbing strake beneath the ivory rail, fore/aft sweep.
a=[(x*1.015,y*1.008,sheer(y)-.075) for x,y in plan];b=[(x*1.015,y*1.008,sheer(y)-.032) for x,y in plan];ring(g,a,b,'M_WoodHighlight');g.mesh('IvoryGunwale',bpy.data.objects['IvoryGunwale'])
# Painted waterline follows actual hull surface interpolation, rather than floating above it.
def paintlevel(t):
 a,b=level(.2,.014),level(.4);u=(t-.2)/.2
 return [(p[0]*(1-u)+q[0]*u+x*.006/half,p[1]*(1-u)+q[1]*u+y*.006/(bow+stern),p[2]*(1-u)+q[2]*u) for p,q,(x,y) in zip(a,b,plan)]
g=Geo();ring(g,paintlevel(.225),paintlevel(.315),'M_SafetyOrange');g.mesh('WaterlineBand')
g=Geo();tip=-min(y for x,y in plan);dh=1.5 if isrow else 2.5;forefoot=dh+(tip-dh)*.70+.035
g.beam((0,stern*.87,bottom-.035),(0,-forefoot,bottom-.035),.085,.13,'M_WoodRecess');g.beam((0,-forefoot,bottom-.035),(0,-tip*1.012,sheer(-tip)-.005),.085,.075,'M_WoodRecess');g.mesh('KeelAndStem')
# Three broad worn paint edges, shaped flat-colour chips, never texture noise.
g=Geo()
for idx in ([3,7,17] if isrow else [3,7,19]):
 x,y=plan[idx];s=1 if x>0 else -1;z=sheer(y)-.052
 g.add([(x*1.017,y-.08,z),(x*1.018,y+.10,z+.005),(x*1.019,y+.14,z-.017),(x*1.019,y-.04,z-.026)],[(0,1,2,3)],'M_WoodRecess')
g.mesh('PaintWear')
if isrow:
 # Same centre thwart contact/height plus small end seats beyond the usable grid.
 g=Geo();g.box((0,0,.32),(2.05,.28,.09),'M_DeckWood');g.box((0,0,.367),(1.98,.025,.006),'M_WoodHighlight')
 for x in [-.82,.82]:g.box((x,0,.16),(.09,.20,.30),'M_WoodRecess')
 for y,w in [(1.76,1.58),(-1.76,1.30)]:
  g.box((0,y,.21),(w,.32,.10),'M_DeckWood');g.box((0,y-.01,.263),(w-.06,.025,.006),'M_WoodHighlight')
 # Flat end soles outside unmodified walking rectangle.
 for p in [[(-.99,1.5),(.99,1.5),(.82,1.94),(-.82,1.94)],[(-.90,-1.5),(.90,-1.5),(.42,-1.80),(0,-1.95),(-.42,-1.80)]]:
  g.add([(x,y,0) for x,y in p],[tuple(range(len(p)))],'M_DeckWood')
 g.mesh('CentreThwart',bpy.data.objects['CentreThwart'],.008)
else:
 g=Geo()
 # Stern bench remains clear of the existing console and grid, bow bench outside build rectangle.
 for x,w in [(-.93,1.05)]:g.box((x,2.74,.22),(w,.27,.10),'M_DeckWood')
 g.box((0,-2.82,.24),(2.55,.32,.10),'M_DeckWood')
 for x in [-1.08,1.08]:g.box((x,-2.82,.10),(.09,.24,.23),'M_WoodRecess')
 g.mesh('EndBenches',bevel=.012)
 # Compact small-outboard clamp bracket outside original transom, original motor untouched.
 g=Geo()
 for x in [-.25,.25]:
  g.box((x,3.04,.29),(.075,.24,.34),'M_Steel');g.box((x,2.94,.46),(.10,.26,.065),'M_Steel');g.beam((x,3.0,.36),(x,3.20,.18),.055,.055,'M_Rubber')
 g.box((0,3.16,.30),(.60,.075,.13),'M_WoodRecess');g.mesh('OutboardBracket',bevel=.008)
 # End soles close the original bare triangular voids outside the deck grid.
 g=Geo()
 for p in [[(-1.49,2.5),(1.49,2.5),(1.36,2.88),(-1.36,2.88)],[(-1.49,-2.5),(1.49,-2.5),(.88,-3.0),(.2,-3.28),(0,-3.35),(-.2,-3.28),(-.88,-3.0)]]:
  g.add([(x,y,0) for x,y in p],[tuple(range(len(p)))],'M_DeckWood')
 g.mesh('EndSoles')
bpy.context.view_layer.update();obs=list(bpy.context.scene.objects);after=stats(obs)
for n,d in before.items():
 assert n in after and after[n]['parent']==d['parent']
 assert max(abs(d[k][i][j]-after[n][k][i][j]) for k in ['local','world'] for i in range(4) for j in range(4))<1e-6,n
tri=sum(d['triangles'] for d in after.values());assert tri <= (3000 if isrow else 5000),(NAME,tri)
# Give each original material its canonical shader for Blender review (no textures).
for m in list(bpy.data.materials):
 if m.name in PALETTE:mat(m.name)
bpy.ops.object.select_all(action='DESELECT')
for o in obs:o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(OUT/(NAME+'.fbx')),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,add_leaf_bones=False,bake_anim=False,path_mode='AUTO')
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(NAME+'.blend')))
(OUT/'build-metrics.json').write_text(json.dumps({'name':NAME,'triangles':tri,'before':before,'after':after,'source':str(src.relative_to(R)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()},indent=2))
print('BUILD PASS',NAME,tri,flush=True)
