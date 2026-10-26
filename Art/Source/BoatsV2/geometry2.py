import bpy,bmesh,math
from mathutils import Vector,Matrix
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
