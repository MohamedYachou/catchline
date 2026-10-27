"""JIG-ART-1: metre-scale jig and repair kit authoring. No game writes."""
import bpy,sys,math,json,random,hashlib,importlib.util
from pathlib import Path
from mathutils import Vector, Euler
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(R/'Art/Source'));import build_crab_coast_props as H
G=H.Geometry
P={'M_FishSilver':'#BAC9C6','M_Rubber':'#28343B','M_NetGreenGrey':'#50766C','M_RailIvory':'#F3F0DC','M_JigBlue':'#3D7FB8','M_FeatherOrange':'#E36A35','M_FeatherYellow':'#F2C14E','M_Kelp':'#5E7A3A','M_Twine':'#C9A66B','M_Sand':'#D8C79A','M_Steel':'#8FA6AC'}
ITEMS={'JigKit':['JigPirk','JigFeathers','JigLine','KelpStrand','SeabedRocks','MoteCloud'],'RepairKit':['TornNet','MendedPatch','NettingNeedle','TwineBall']}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def empty(n,par=None):
 o=bpy.data.objects.new(n,None);bpy.context.scene.collection.objects.link(o);o.parent=par;return o

def mesh(g,n,par):
 o=g.object(n,par,bpy.context.scene.collection)
 used=sorted({p.material_index for p in o.data.polygons});ms=[o.data.materials[i] for i in used];ix=[used.index(p.material_index) for p in o.data.polygons];o.data.materials.clear()
 for m in ms:o.data.materials.append(m)
 for p,i in zip(o.data.polygons,ix):p.material_index=i
 return o

def tube(g,p,r,col,s=3):g.tube(p,[r]*len(p),s,col)
def loft(g,rows,col):
 n=len(rows[0]);fs=[tuple(reversed(range(n)))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(rows)-1) for i in range(n)]+[tuple(range((len(rows)-1)*n,len(rows)*n))];g.add(sum(rows,[]),fs,col)
def ring(g,centre,r,wire,col,n=8):
 x,y,z=centre;tube(g,[(x+r*math.sin(i*math.tau/n),y,z+r*math.cos(i*math.tau/n)) for i in range(n+1)],wire,col,3)
def hook(g,c,r=.010):
 x,y,z=c;tube(g,[(x,y,z),(x,y,z-.018),(x+r*.3,y,z-.025),(x+r,y,z-.025),(x+r*1.25,y,z-.018),(x+r*.9,y,z-.014)],.0012,'M_Rubber')
def pirk(root):
 g=G();ring(g,(0,0,-.005),.004,.0009,'M_FishSilver');rows=[]
 for z,w,d in [(-.01,.003,.002),(-.035,.011,.005),(-.075,.009,.004),(-.106,.004,.003)]:rows.append([(w*math.cos(i*math.tau/6),d*math.sin(i*math.tau/6),z) for i in range(6)])
 loft(g,rows,'M_FishSilver')
 # A broad blue spine panel remains geometry/material driven, with clean silver flank.
 g.add([(-.005,-.0044,-.028),(.005,-.0044,-.028),(.007,-.0044,-.068),(.003,-.0032,-.103),(-.003,-.0032,-.103),(-.007,-.0044,-.068)],[(0,1,2,3,4,5)],'M_JigBlue');ring(g,(0,0,-.109),.003,.0008,'M_FishSilver')
 for k in range(3):
  h=G();hook(h,(0,0,-.111),.009)
  a=k*math.tau/3;h.vertices=[(x*math.cos(a)-y*math.sin(a),x*math.sin(a)+y*math.cos(a),z) for x,y,z in h.vertices];g.merge(h)
 # Exact140mm eye-to-lowest-hook envelope, without stretching the eye pivot.
 mn=min(v[2] for v in g.vertices);g.vertices=[(x,y,z*.14/-mn) for x,y,z in g.vertices]
 return mesh(g,'JigPirk',root)
def feathers(root):
 g=G();ring(g,(0,0,-.004),.003,.0008,'M_FishSilver');tube(g,[(0,0,-.008),(0,0,-.198)],.0009,'M_RailIvory')
 for i,col in enumerate(['M_FeatherOrange','M_RailIvory','M_FeatherYellow']):
  z=-.039-i*.057;s=-1 if i%2 else 1;x=s*.026;tube(g,[(0,0,z),(x,0,z-.011)],.0009,'M_RailIvory');hook(g,(x,0,z-.011),.007)
  # Three tapered fins per tuft, visible from side/back as well as front.
  for j in range(3):
   a=j*math.tau/3;u=Vector((math.cos(a)*.007,math.sin(a)*.007,0));c=Vector((x,0,z-.014));g.add([tuple(c),tuple(c+u+Vector((0,0,-.014))),tuple(c+Vector((s*.003,0,-.033))),tuple(c-u+Vector((0,0,-.014)))],[(0,1,2,3)],col)
 return mesh(g,'JigFeathers',root)
def kelp(root):
 ar=bpy.data.armatures.new('KelpSkeleton');rig=bpy.data.objects.new('KelpStrand',ar);bpy.context.scene.collection.objects.link(rig);rig.parent=root;bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for i in range(3):
  b=ar.edit_bones.new('Kelp_'+str(i));b.head=(0,0,i*2.5/3);b.tail=(0,0,(i+1)*2.5/3)
  if i:b.parent=ar.edit_bones['Kelp_'+str(i-1)];b.use_connect=True
 bpy.ops.object.mode_set(mode='OBJECT');g=G();rows=[]
 for i in range(16):
  t=i/15;z=t*2.5;w=.018+.115*math.sin(math.pi*t)**.7;x=.08*math.sin(t*math.pi*3);y=.035*math.sin(t*math.pi*4)
  rows.append([(x-w,y-.014*math.cos(t*math.tau),z),(x,y+.014,z),(x+w,y+.014*math.cos(t*math.tau),z)])
 vs=sum(rows,[]);g.add(vs,[(j*3+i,j*3+i+1,(j+1)*3+i+1,(j+1)*3+i) for j in range(15) for i in range(2)],'M_Kelp');skin=mesh(g,'KelpRibbon',rig);mod=skin.modifiers.new('Skin','ARMATURE');mod.object=rig
 for i in range(3):skin.vertex_groups.new(name='Kelp_'+str(i))
 for v in skin.data.vertices:
  q=max(0,min(2,v.co.z/(2.5/3)-.5));a=int(q);b=min(2,a+1);t=q-a
  skin.vertex_groups[a].add([v.index],1-t,'REPLACE')
  if b!=a and t:skin.vertex_groups[b].add([v.index],t,'REPLACE')
 sc=bpy.context.scene;sc.render.fps=30;rig.animation_data_create();act=bpy.data.actions.new('Sway');act.use_fake_user=True;rig.animation_data.action=act
 for f in range(1,122,5):
  t=(f-1)/120
  for i,pb in enumerate(rig.pose.bones):
   pb.rotation_mode='XYZ';pb.rotation_euler=(math.radians(3)*math.sin(t*math.tau+i*.6),math.radians(7)*math.sin(t*math.tau+i*.65),0);pb.keyframe_insert('rotation_euler',frame=f)
 act['loop']=True;act['seconds']=4.;sc.frame_start=1;sc.frame_end=121;sc.frame_set(1);return rig

def rocks(root):
 g=G();# A single broad sand island, gently bevelled edge.
 rows=[]
 for rx,ry,z in [(1.42,.93,0),(1.5,1.,.035),(1.39,.91,.075)]:rows.append([(rx*math.cos(i*math.tau/12),ry*math.sin(i*math.tau/12),z) for i in range(12)])
 loft(g,rows,'M_Sand')
 # Fractured slabs: asymmetrical clipped outlines, raked shoulders, broad split tops.
 outline=[(-.95,-.65),(-.30,-1),(.72,-.78),(1,-.10),(.78,.77),(.12,1),(-.78,.63),(-1,.12)]
 for x,y,rx,ry,h,ang,lean in [(-.88,.05,.46,.31,.45,-.31,.12),(-.27,.29,.57,.40,.72,.17,-.16),(.48,.12,.49,.32,.48,-.22,.13),(1.02,-.20,.31,.24,.31,.43,-.09)]:
  rows=[]
  for level in range(3):
   row=[]
   for i,(u,v) in enumerate(outline):
    if level==0:xx,yy,zz=u*.94,v*.95,.06
    elif level==1:xx,yy,zz=u,v,.075+h*(.54+.055*(i%3))
    else:xx,yy,zz=u*(.67+.05*(i%2))+lean,v*.70-.10,.075+h*(.91+.09*u-.06*v)
    row.append((x+rx*xx*math.cos(ang)-ry*yy*math.sin(ang),y+rx*xx*math.sin(ang)+ry*yy*math.cos(ang),zz))
   rows.append(row)
  loft(g,rows,'M_Steel')
 return mesh(g,'SeabedRocks',root)
def motes(root):
 g=G();rng=random.Random(103)
 for i in range(50):
  c=Vector(tuple(rng.uniform(-.985,.985) for _ in range(3)));r=rng.uniform(.004,.009);rot=Euler(tuple(rng.random()*math.tau for _ in range(3))).to_matrix();u=rot@Vector((r,0,0));v=rot@Vector((0,0,r*.6));g.add([c-u-v,c+u-v,c+u+v,c-u+v],[(0,1,2,3)],'M_FishSilver')
 return mesh(g,'MoteCloud',root)

def net_segments():
 # Coarse105mm diamonds clipped exactly to1.2x.8 panel; ragged hole with cut ends.
 seg=[]
 for slope in (-1,1):
  for k in range(-11,12):
   b=k*.105;pts=[]
   for x in (-.6,.6):
    y=slope*x+b
    if -.4<=y<=.4:pts.append(Vector((x,y,0)))
   for y in (-.4,.4):
    x=(y-b)/slope
    if -.6<x<.6:pts.append(Vector((x,y,0)))
   if len(pts)!=2:continue
   a,c=pts;d=c-a;A=d.dot(d);B=2*a.dot(d);C=a.dot(a)-.15**2;disc=B*B-4*A*C
   if disc>0:
    t0=(-B-math.sqrt(disc))/(2*A);t1=(-B+math.sqrt(disc))/(2*A)
    if 0<t0<t1<1:
     # Alternating cutback makes the hole recognisably torn without making an orderly disc.
     extra=.012 if k%2 else .002;t0=max(0,t0-extra/d.length);t1=min(1,t1+extra/d.length)
     seg.append((tuple(a),tuple(a+d*t0),'old'));seg.append((tuple(a+d*t0),tuple(a+d*t1),'new'));seg.append((tuple(a+d*t1),tuple(c),'old'));continue
   seg.append((tuple(a),tuple(c),'old'))
 return seg

def repair(root):
 a,b=G(),G()
 for x,y,kind in net_segments():tube(a if kind=='old' else b,[x,y],.0028 if kind=='old' else .0032,'M_NetGreenGrey' if kind=='old' else 'M_Twine')
 for p,q in [((-.6,-.4,0),(.6,-.4,0)),((.6,-.4,0),(.6,.4,0)),((.6,.4,0),(-.6,.4,0)),((-.6,.4,0),(-.6,-.4,0))]:tube(a,[p,q],.006,'M_NetGreenGrey',4)
 mesh(a,'TornNet',root);mesh(b,'MendedPatch',root)
 g=G();# Flat wooden shuttle points from its tip pivot down-X, eye is real open geometry.
 poly=[(0,0),(-.038,-.012),(-.18,-.012),(-.2,-.007),(-.2,.007),(-.18,.012),(-.038,.012)]
 g.extrude_polygon(poly,-.002,.002,'M_Twine')
 # The long slot is built as a frame perched above the solid tapered nose.
 # Open rear eye: replace the rear solid section with four broad rails.
 g=G();g.extrude_polygon([(0,0),(-.039,-.012),(-.05,-.012),(-.05,.012),(-.039,.012)],-.002,.002,'M_Twine')
 for y in (-.009,.009):g.box((-.122,y,0),(.144,.006,.004),'M_Twine')
 g.box((-.197,0,0),(.006,.024,.004),'M_Twine');g.box((-.058,0,.001),(.006,.02,.006),'M_Twine')
 # Four quiet raised wraps of the same tan twine, routed around the rails.
 for i in range(5):
  x=-.078-i*.014;tube(g,[(x,-.014,0),(x,-.011,.005),(x,.011,.005),(x,.014,0),(x,.011,-.005),(x,-.011,-.005),(x,-.014,0)],.0012,'M_Twine')
 mesh(g,'NettingNeedle',root);g=G();g.ellipsoid((0,0,.05),(.05,.05,.05),10,4,'M_Twine')
 for k in range(4):
  a=k*.72;p=[]
  for j in range(13):
   t=j*math.tau/12;p.append((.049*math.cos(t)*math.cos(a),.049*math.cos(t)*math.sin(a),.05+.049*math.sin(t)))
  tube(g,p,.0018,'M_Twine')
 tube(g,[(.03,-.036,.026),(.058,-.049,.003),(.089,-.048,.002)],.0018,'M_Twine');mesh(g,'TwineBall',root)

def snapshot():
 rows={};bpy.context.view_layer.update()
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  p=[o.matrix_world@v.co for v in o.data.vertices];o.data.calc_loop_triangles();rows[o.name]={'triangles':len(o.data.loop_triangles),'bounds_blender':[[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]],'pivot_blender':list(o.location),'materials':sorted({o.data.materials[p.material_index].name for p in o.data.polygons})}
 return {'triangles':sum(x['triangles'] for x in rows.values()),'items':rows,'parents':{o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects}}
def run(kit):
 O=R/'Art/Models'/kit;O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True)
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;H.PALETTE=P;H.MATERIALS={k:H.material(k,v,.72) for k,v in P.items()};root=empty(kit)
 if kit=='JigKit':
  pirk(root);feathers(root);g=G();g.beam((0,0,0),(0,0,-1),.004,.004,'M_RailIvory');mesh(g,'JigLine',root);kelp(root);rocks(root);motes(root)
 else:repair(root)
 for m in list(bpy.data.materials):
  if m.users==0:bpy.data.materials.remove(m)
 row=snapshot();assert row['triangles']<=2500,(kit,row['triangles']);bpy.ops.wm.save_as_mainfile(filepath=str(O/(kit+'.blend')));bpy.ops.object.select_all(action='SELECT')
 bpy.ops.export_scene.fbx(filepath=str(O/(kit+'.fbx')),use_selection=True,object_types={'EMPTY','MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_space_transform=kit!='JigKit',use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=kit=='JigKit',bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0,use_custom_props=True)
 row.update(palette=P,sha256={e:sha(O/(kit+'.'+e)) for e in ['blend','fbx']});(O/'metrics/build.json').write_text(json.dumps(row,indent=2)+'\n');print('KIT BUILT',kit,row['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
