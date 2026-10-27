"""HARBOUR-LIFE-2. Chunky faceted harbour animals, metres, Blender -Y forward."""
import bpy,sys,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Euler
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[3];O=R/'Art/Models/HarbourLife'
sys.path.insert(0,str(R/'Art/Source'));import build_crab_coast_props as H
G=H.Geometry
P={'M_Rubber':'#28343B','M_GullWhite':'#F1F0EA','M_HairChestnut':'#50392E','M_Ginger':'#C58B50','M_GingerShade':'#9C6036','M_WoodHighlight':'#DFB77A','M_NoseRose':'#B97566','M_Teal':'#168F9F'}
LIMITS={'Dog':1200,'Cat':900}
CLIPS={'Dog':{'Trot':19,'Sit':91,'Sniff':61},'Cat':{'Sleep':121,'Look':91}}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def empty(n):
 o=bpy.data.objects.new(n,None);bpy.context.scene.collection.objects.link(o);return o

def mesh(g,n,parent):
 o=g.object(n,parent,bpy.context.scene.collection)
 used=sorted({p.material_index for p in o.data.polygons});mats=[o.data.materials[i] for i in used];ix=[used.index(p.material_index) for p in o.data.polygons];o.data.materials.clear()
 for m in mats:o.data.materials.append(m)
 for p,i in zip(o.data.polygons,ix):p.material_index=i
 return o

def loft(g,rows,col):
 n=len(rows[0]);faces=[tuple(reversed(range(n))),tuple(range((len(rows)-1)*n,len(rows)*n))]
 faces += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(rows)-1) for i in range(n)]
 g.add(sum(rows,[]),faces,col)

def wedge(g,poly,thick,col):
 # Profile polygon in XZ, front and back Y thickness.
 loft(g,[[(x,y+off,z) for x,y,z in poly] for off in (-thick/2,thick/2)],col)

def animal(name):
 g=G();tags=[];spec=[]
 def bone(n,p,par):spec.append((n,tuple(p),par))
 def part(n,fn):
  st=len(g.vertices);fn();tags.append((st,len(g.vertices),n))
 def ell(c,r,col,n=8,k=2):g.ellipsoid(c,r,n,k,col)
 bone('Root',(0,0,0),None)
 if name=='Dog':
  bone('Body',(0,0,.31),'Root');bone('Neck',(0,-.10,.325),'Body');bone('Head',(0,-.205,.405),'Body')
  bone('TailA',(0,.245,.34),'Body');bone('TailB',(0,.37,.39),'TailA')
  def body():
   ell((0,.01,.325),(.105,.255,.108),'M_Rubber',10,3)
   ell((0,.185,.317),(.093,.09,.091),'M_Rubber',8,2)
  part('Body',body)
  def neck():
   ell((0,-.155,.347),(.108,.107,.087),'M_GullWhite',8,2)
   # Broad angular neck ruff: silhouette tufts, no noise texture.
   for s in (-1,1):
    wedge(g,[(s*.062,-.137,.389),(s*.145,-.138,.325),(s*.071,-.137,.331)],.055,'M_GullWhite')
    wedge(g,[(s*.066,-.123,.339),(s*.121,-.102,.284),(s*.043,-.117,.306)],.055,'M_GullWhite')
  part('Neck',neck)
  def head():
   ell((0,-.245,.463),(.085,.083,.073),'M_Rubber',10,3)
   # Central white blaze lies on front plane and joins a tapered canine muzzle.
   loft(g,[[(-.014,-.322,.469),(.014,-.322,.469),(.018,-.301,.516),(-.018,-.301,.516)], [(-.014,-.326,.468),(.014,-.326,.468),(.018,-.305,.516),(-.018,-.305,.516)]],'M_GullWhite')
   ell((0,-.315,.431),(.057,.085,.041),'M_GullWhite',8,2)
   ell((0,-.390,.444),(.026,.018,.019),'M_Rubber',8,2)
   # Left pricked, right flopped; asymmetry is geometry, not rig dependence.
   wedge(g,[(-.074,-.245,.483),(-.073,-.232,.550),(-.020,-.246,.498)],.037,'M_Rubber')
   wedge(g,[(.023,-.247,.501),(.074,-.232,.535),(.096,-.278,.469),(.055,-.284,.475)],.029,'M_Rubber')
   for s in (-1,1):
    ell((s*.063,-.298,.479),(.011,.007,.011),'M_HairChestnut',6,1)
    ell((s*.063,-.304,.479),(.006,.0035,.0065),'M_Rubber',6,1)
    wedge(g,[(s*.050,-.258,.431),(s*.103,-.233,.405),(s*.076,-.278,.451)],.045,'M_Rubber')
  part('Head',head)
  part('TailA',lambda:g.tube([(0,.232,.34),(0,.32,.374),(0,.382,.403)],[.033,.033,.024],6,'M_Rubber'))
  part('TailB',lambda:g.tube([(0,.365,.397),(0,.445,.447),(0,.49,.466)],[.027,.026,.009],6,'M_GullWhite'))
  for side,s in [('L',-1),('R',1)]:
   for label,y in [('Fore',-.16),('Hind',.16)]:
    x=s*.082;hip=Vector((x,y,.32));knee=Vector((x,y+(.055 if label=='Hind' else .012),.17));ankle=Vector((x,y,.055))
    upper=label+'.'+side;lower=label+'Paw.'+side
    bone(upper,hip,'Body');bone(lower,knee,upper)
    def up(hip=hip,knee=knee,label=label):
     g.tube([hip,knee],[.042 if label=='Hind' else .028,.026],6,'M_Rubber')
    part(upper,up)
    def low(knee=knee,ankle=ankle):
     g.tube([knee,ankle-Vector((0,0,.012))],[.026,.022],6,'M_GullWhite')
     ell((ankle.x,ankle.y-.018,.024),(.030,.048,.024),'M_GullWhite',8,2)
    part(lower,low)
 else:
  bone('Body',(0,.025,.12),'Root');bone('Head',(0,-.045,.225),'Body')
  bone('TailA',(0,.095,.065),'Body');bone('TailB',(.095,.09,.035),'TailA');bone('TailC',(.125,-.025,.025),'TailB')
  def body():
   ell((0,.025,.123),(.069,.078,.098),'M_Ginger',10,3)
   ell((0,-.034,.166),(.052,.048,.069),'M_WoodHighlight',8,2)
   for s in (-1,1):
    ell((s*.053,.044,.065),(.043,.058,.061),'M_Ginger',8,2)
   # Broad tabby shoulders, no floating stripes.
   for i,f in enumerate(g.faces):
    c=sum((Vector(g.vertices[v]) for v in f),Vector())/len(f)
    if c.y>.04 and .14<c.z<.182:g.colours[i]='M_GingerShade'
  part('Body',body)
  def head():
   ell((0,-.045,.253),(.060,.054,.047),'M_Ginger',10,3)
   for s in (-1,1):
    wedge(g,[(s*.019,-.047,.280),(s*.049,-.032,.326),(s*.059,-.043,.278)],.031,'M_Ginger')
    wedge(g,[(s*.030,-.064,.285),(s*.048,-.051,.312),(s*.052,-.059,.282)],.002,'M_NoseRose')
    ell((s*.019,-.088,.235),(.023,.019,.015),'M_WoodHighlight',8,1)
   ell((0,-.107,.244),(.009,.006,.006),'M_NoseRose',6,1)
   # Tabby forehead crown as inset planar faces.
   for x in [-.021,0,.021]:
    wedge(g,[(x-.006,-.091,.269),(x+.004,-.091,.269),(x+.006,-.070,.293)],.001,'M_GingerShade')
  part('Head',head)
  for s,label in [(-1,'L'),(1,'R')]:
   bone('Eye.'+label,(s*.032,-.086,.261),'Head')
   part('Eye.'+label,lambda s=s:ell((s*.032,-.091,.261),(.008,.005,.009),'M_Rubber',6,1))
   bone('Fore.'+label,(s*.030,-.046,.15),'Body')
   def fore(s=s):
    g.tube([(s*.030,-.046,.16),(s*.031,-.065,.026)],[.017,.014],6,'M_Ginger')
    ell((s*.031,-.075,.016),(.020,.031,.016),'M_WoodHighlight',8,2)
   part('Fore.'+label,fore)
   bone('Hind.'+label,(s*.063,.045,.04),'Body')
   part('Hind.'+label,lambda s=s:ell((s*.060,.004,.018),(.026,.041,.018),'M_Ginger',8,2))
  part('TailA',lambda:g.tube([(0,.095,.067),(.057,.123,.041),(.101,.087,.028)],[.018,.019,.017],6,'M_Ginger'))
  part('TailB',lambda:g.tube([(.093,.093,.03),(.132,.040,.024),(.124,-.027,.022)],[.019,.018,.015],6,'M_GingerShade'))
  part('TailC',lambda:g.tube([(.126,-.018,.024),(.101,-.080,.022),(.053,-.093,.022)],[.016,.014,.009],6,'M_Ginger'))
  # Full sitting silhouette is exactly .30m tall including ears.
  factor=.3/max(v[2] for v in g.vertices)
  g.vertices=[tuple(c*factor for c in v) for v in g.vertices];spec=[(n,tuple(c*factor for c in p),par) for n,p,par in spec]
 skin=mesh(g,name+'Skin',None);root=empty(name)
 ar=bpy.data.armatures.new(name+'Skeleton');rig=bpy.data.objects.new(name+'Rig',ar);bpy.context.scene.collection.objects.link(rig);rig.parent=root
 bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
 for n,p,par in spec:
  b=ar.edit_bones.new(n);b.head=p;b.tail=Vector(p)+Vector((0,.035,0))
  if par:b.parent=ar.edit_bones[par]
 bpy.ops.object.mode_set(mode='OBJECT');skin.parent=rig;mod=skin.modifiers.new(name+'Skinning','ARMATURE');mod.object=rig
 for n,_,_ in spec:skin.vertex_groups.new(name=n);rig.pose.bones[n].rotation_mode='XYZ'
 for a,b,n in tags:skin.vertex_groups[n].add(list(range(a,b)),1,'REPLACE')
 return rig,skin,{n:Vector(p) for n,p,_ in spec}

def setworld(rig,n,pos,rot=(0,0,0),scale=(1,1,1)):
 rig.pose.bones[n].matrix=Matrix.Translation(Vector(pos)) @ Euler(rot,'XYZ').to_matrix().to_4x4() @ Matrix.Diagonal((*scale,1))
 bpy.context.view_layer.update()
def transform(pos,pivot,rot,newpivot):return Vector(newpivot)+Euler(rot,'XYZ').to_matrix()@(Vector(pos)-Vector(pivot))
def legpose(rig,skin,rests,upper,lower,hip,foot):
 # Two-bone sagittal IK, with a backward hock. Keep the paw's bottom on the floor.
 p=rests[upper];k=rests[lower];a=Vector((p.x,p.y,.055))
 L1=(k-p).length;L2=(a-k).length;d=(foot-hip).length;d=min(d,L1+L2-.0001)
 along=(foot-hip).normalized();side=Vector((0,-along.z,along.y));m=(L1*L1-L2*L2+d*d)/(2*d);height=math.sqrt(max(0,L1*L1-m*m))
 knee=hip+along*m+side*height
 def ang(v,w):return math.atan2(v.y*w.z-v.z*w.y,v.y*w.y+v.z*w.z)
 r1=ang(k-p,knee-hip);r2=ang(a-k,foot-knee)
 setworld(rig,upper,hip,(r1,0,0));setworld(rig,lower,knee,(r2,0,0))
 # Avoid the rotated toe dipping through the quay, while keeping upper/lower join exact.
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();ev=skin.evaluated_get(dg);indices=[v.index for v in skin.data.vertices if any(skin.vertex_groups[w.group].name==lower for w in v.groups)]
 zmin=min((ev.matrix_world@ev.data.vertices[i].co).z for i in indices)
 if zmin<0:
  pb=rig.pose.bones[lower];mat=pb.matrix.copy();mat.translation.z-=zmin;pb.matrix=mat;bpy.context.view_layer.update()

def animate(name,rig,skin,rests):
 sc=bpy.context.scene
 for clip,end in CLIPS[name].items():
  act=bpy.data.actions.new(clip);act.use_fake_user=True;rig.animation_data_create();rig.animation_data.action=act
  for f in range(1,end+1):
   t=(f-1)/(end-1);q=math.tau*t
   for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
   bpy.context.view_layer.update()
   if name=='Dog':
    if clip=='Trot':
     bp=rests['Body']+Vector((0,0,.007*(1-math.cos(2*q))));br=(.015*math.sin(2*q),0,0)
    elif clip=='Sit':bp=Vector((0,.02,.220+.002*math.sin(q)));br=(math.radians(-35),0,0)
    else:bp=rests['Body']+Vector((0,0,-.012));br=(math.radians(-6),0,0)
    setworld(rig,'Body',bp,br,scale=(1,1,1+.008*math.sin(q)))
    hp=transform(rests['Head'],rests['Body'],br,bp)
    if clip=='Sniff':hp=Vector((0,-.225,.255+.007*math.sin(2*q)));hr=(math.radians(53)+.05*math.sin(2*q),0,.045*math.sin(q))
    elif clip=='Sit':hp=Vector((0,-.15,.420+.002*math.sin(q)));hr=(-.10,0,.08*math.sin(q))
    else:hr=(.035*math.sin(2*q),0,.025*math.sin(q))
    setworld(rig,'Head',hp,hr)
    np=transform(rests['Neck'],rests['Body'],br,bp)
    nr=(rests['Head']-rests['Neck']).rotation_difference(hp-np).to_euler()
    setworld(rig,'Neck',np,nr)
    tp=transform(rests['TailA'],rests['Body'],br,bp);tr=(math.radians(18) if clip=='Sniff' else -.15,0,.32*math.sin(q*(2 if clip=='Sit' else 1)))
    setworld(rig,'TailA',tp,tr)
    tail=transform(rests['TailB'],rests['TailA'],tr,tp);setworld(rig,'TailB',tail,(tr[0],0,tr[2]+.2*math.sin(q)))
    for s,label in [(-1,'L'),(1,'R')]:
     for part,y in [('Fore',-.16),('Hind',.16)]:
      upper=part+'.'+label;lower=part+'Paw.'+label;hip=transform(rests[upper],rests['Body'],br,bp)
      phase=q+(0 if (s==-1)==(part=='Fore') else math.pi)
      if clip=='Trot':foot=Vector((s*.082,y+.045*math.cos(phase),.055+.045*max(0,math.sin(phase))))
      elif clip=='Sit':foot=Vector((s*.082,(hip.y-.015 if part=='Fore' else .17),.055))
      else:foot=Vector((s*.082,y,.055))
      legpose(rig,skin,rests,upper,lower,hip,foot)
   else:
    scale=.3/.326
    if clip=='Sleep':
     bp=Vector((0,.025,.078))*scale;br=(0,math.radians(90),math.radians(-20));bscale=(.75,.95,.90)
     setworld(rig,'Body',bp,br,bscale)
     hp=Vector((.040,-.081,.068))*scale;hr=(math.radians(18),math.radians(-12),math.radians(45))
     setworld(rig,'Head',hp,hr)
     # Forelegs tuck under the muzzle; hind feet lie inside the curled silhouette.
     for s,label in [(-1,'L'),(1,'R')]:
      setworld(rig,'Fore.'+label,Vector((s*.024,-.032,.065))*scale,(math.radians(90),0,s*.28))
      setworld(rig,'Hind.'+label,Vector((s*.051,.033,.043))*scale,(0,0,s*.2))
     for label in ['L','R']:
      ep=transform(rests['Eye.'+label],rests['Head'],hr,hp);setworld(rig,'Eye.'+label,ep,hr,(1,1,.16))
     # Small inhale stretches the torso without shifting the root or contact point.
     rig.pose.bones['Body'].scale*=1+.006*(1-math.cos(q))*.5
    else:
     bp=rests['Body']+Vector((0,0,.0012*math.sin(q)));setworld(rig,'Body',bp,scale=(1,1,1+.006*math.sin(q)))
     hp=rests['Head']+Vector((0,0,.0012*math.sin(q)));hr=(.02*math.sin(2*q),0,math.radians(30)*math.sin(q));setworld(rig,'Head',hp,hr)
     for label in ['L','R']:
      ep=transform(rests['Eye.'+label],rests['Head'],hr,hp);setworld(rig,'Eye.'+label,ep,hr)
     for n in ['Fore.L','Fore.R','Hind.L','Hind.R']:setworld(rig,n,rests[n])
    # Tail remains a curl; only the terminal tip flicks in Look.
    for n in ['TailA','TailB','TailC']:
     setworld(rig,n,rests[n],(0,0,(.16*math.sin(q*2) if n=='TailC' and clip=='Look' else 0)))
   bpy.context.view_layer.update()
   for pb in rig.pose.bones:
    for prop in ['location','rotation_euler','scale']:pb.keyframe_insert(prop,frame=f,group=pb.name)
  for fc in act.layers[0].strips[0].channelbag(rig.animation_data.action_slot).fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
   fc.modifiers.new('CYCLES')
  act['loop']=True;act['seconds']=(end-1)/30
 rig.animation_data.action=None
 for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
 sc.frame_start=1;sc.frame_end=max(CLIPS[name].values());sc.frame_set(1);bpy.context.view_layer.update()

def snapshot():
 bpy.context.view_layer.update();objects=list(bpy.context.scene.objects);meshes=[o for o in objects if o.type=='MESH'];p=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
 return {'triangles':sum(len(f.vertices)-2 for o in meshes for f in o.data.polygons),'vertices':sum(len(o.data.vertices) for o in meshes),'bounds_unity':[[min((v.x,v.z,-v.y)[i] for v in p) for i in range(3)],[max((v.x,v.z,-v.y)[i] for v in p) for i in range(3)]],'meshes':[o.name for o in meshes],'materials':sorted({m.name for o in meshes for m in o.data.materials}),'parents':{o.name:o.parent.name if o.parent else None for o in objects}}
def run(name):
 O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True);bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=30
 H.PALETTE=P;H.MATERIALS={n:H.material(n,c,.8) for n,c in P.items()}
 rig,skin,rests=animal(name);animate(name,rig,skin,rests);root=bpy.data.objects[name];root['axes']='Blender X,-Y,Z -> Unity X,Z,-Y; +Z forward in Unity; metres, fixed feet-centre root.'
 row=snapshot();assert row['triangles']<=LIMITS[name],(name,row['triangles'])
 for m in list(bpy.data.materials):
  if m.users==0:bpy.data.materials.remove(m)
 bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
 bpy.ops.object.select_all(action='SELECT');bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'EMPTY','MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',bake_space_transform=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_step=1,bake_anim_simplify_factor=0,use_custom_props=True,colors_type='LINEAR')
 row.update(name=name,limit=LIMITS[name],bones=[b.name for b in rig.data.bones],clips={n:{'frames':[1,e],'seconds':(e-1)/30,'loop':True} for n,e in CLIPS[name].items()},sha256={e:sha(O/(name+'.'+e)) for e in ['blend','fbx']},palette=P)
 (O/'metrics'/(name+'-build.json')).write_text(json.dumps(row,indent=2)+'\n');print('HARBOUR BUILT',name,row['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
