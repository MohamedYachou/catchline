"""Authored Catchline fish and matching transparent portraits. Background Blender 3.1+.
No dependencies, downloaded models or textures. Exports are staged, never installed here.
Run: blender --background --factory-startup --python Art/Source/build_fish_polish16.py
Optional -- <model> for one species. Nose -Y in source; FBX nose +Z, Y up.
"""
import bpy, bmesh, math, json, sys, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.kdtree import KDTree
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'Art/Models/FishPolish16'; OUT.mkdir(parents=True,exist_ok=True)
# name, length, half-height/length, half-width/length, dorsal palette, fin palette, type
FISH=[('Herring',.26,.115,.075,'M_Steel','M_FishSilver','school'),
 ('Mackerel',.34,.135,.08,'M_SeaTeal','M_SeaTeal','striped'),
 ('Pollock',.48,.135,.10,'M_KelpGreen','M_KelpGreen','long'),
 ('SeaBass',.50,.18,.105,'M_HullBlue','M_Steel','spiny'),
 ('CongerEel',.80,.045,.045,'M_HullNavy','M_HullBlue','eel'),
 ('Plaice',.36,.26,.045,'M_WoodRecess','M_Rope','flat'),
 ('Cod',.70,.19,.13,'M_KelpGreen','M_KelpGreen','cod'),
 ('Whiting',.38,.12,.075,'M_Steel','M_BandIvory','whiting'),
 ('RedMullet',.34,.175,.09,'M_Skin','M_SafetyOrange','mullet'),
 ('Turbot',.58,.33,.055,'M_CoastWet','M_CoastStone','diamond')]
COLORS={'M_Steel':'8FA6AC','M_FishSilver':'BAC9C6','M_RailIvory':'F3F0DC','M_Rubber':'28343B','M_SeaTeal':'168F9F','M_HullNavy':'173F57','M_HullBlue':'2A6685','M_KelpGreen':'477A56','M_WoodRecess':'8C5A36','M_Rope':'D1AF76','M_SafetyOrange':'E36A35','M_Skin':'B9784B','M_BandIvory':'F3DEA1','M_CoastWet':'696F64','M_CoastStone':'A99A7C'}
MATS={}; GROUP=None

def mat(name):
 if name in MATS:return MATS[name]
 c=COLORS[name];rgb=[int(c[i:i+2],16)/255 for i in (0,2,4)]
 rgba=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb)+(1,)
 m=bpy.data.materials.new(name);m.diffuse_color=rgba;m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=rgba;p.inputs['Roughness'].default_value=.52
 MATS[name]=m;return m

def mesh(name,vs,fs,colors):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.parent=GROUP
 names=list(dict.fromkeys(colors))
 for n in names:me.materials.append(mat(n))
 for p,c in zip(me.polygons,colors):p.material_index=names.index(c)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
 return ob

def ball(name,pos,size,color):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=pos)
 o=bpy.context.object;o.name=name;o.scale=size;o.parent=GROUP;o.data.materials.append(mat(color))
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for p in o.data.polygons:p.use_smooth=True
 return o

def fin(name,poly,color,thick):
 # Closed fin in YZ with a real edge, rather than one-sided triangle sheets.
 vs=[(x,y,z) for x in (-thick,thick) for y,z in poly];n=len(poly)
 fs=[tuple(reversed(range(n))),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 return mesh(name,vs,fs,[color]*len(fs))

def line(name,pts,r,color):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.bevel_depth=r;cu.bevel_resolution=0;cu.resolution_u=2
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,v in zip(sp.points,pts):p.co=(*v,1)
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);ob.parent=GROUP;cu.materials.append(mat(color))
 bpy.context.view_layer.objects.active=ob;ob.select_set(True);bpy.ops.object.convert(target='MESH');ob.select_set(False)
 return ob

def build(row):
 global GROUP,MATS
 name,L,H,W,back,fc,kind=row; MATS={}
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.context.preferences.filepaths.save_version=0
 sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
 GROUP=bpy.data.objects.new('Catchline_'+name,None);bpy.context.collection.objects.link(GROUP)
 GROUP['species']=name;GROUP['source_nose']='-Y';GROUP['units']='metres'
 flat=kind in ('flat','diamond'); eel=kind=='eel'
 if flat:
  profile=[(-.47,.10),(-.40,.50),(-.29,.8),(-.12,1),(0,1 if kind=='flat' else 1.08),(.15,.8),(.27,.4),(.35,.15)]
 elif eel:profile=[(-.48,.35),(-.43,.9),(-.32,1),(-.13,.95),(.08,.8),(.27,.55),(.42,.20),(.51,.02)]
 else:profile=[(-.48,.12),(-.44,.5),(-.36,.78),(-.24,.98),(-.08,1),(.08,.90),(.22,.58),(.33,.18)]
 sides=20;vs=[]
 for y,f in profile:
  cx=math.sin((y+.5)*math.tau)*L*.055 if eel else 0
  for i in range(sides):
   a=i*math.tau/sides;vs.append((cx+L*W*f*math.cos(a),y*L,L*H*f*math.sin(a)))
 fs=[tuple(reversed(range(sides)))];colors=[back]
 for j in range(len(profile)-1):
  for i in range(sides):
   fs.append((j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i))
   a=(i+.5)*math.tau/sides
   color=back if math.sin(a)>.28 else 'M_RailIvory' if math.sin(a)<-.55 else 'M_FishSilver'
   if flat:color=back if math.cos(a)>-.2 else 'M_RailIvory'
   colors.append(color)
 fs.append(tuple(range((len(profile)-1)*sides,len(profile)*sides)));colors.append(back)
 body=mesh('Body',vs,fs,colors)
 # Broad facets with smooth side normals and a deliberate colour boundary.
 for p in body.data.polygons:p.use_smooth=True
 eye_y=-.365*L;eye_z=(.012 if eel else .055)*L if not flat else .10*L
 eye_x=W*L*.82
 for side in ([1] if flat else [-1,1]):
  z_positions=[.06*L,.14*L] if flat else [eye_z]
  for z in z_positions:
   eye_scale=.60 if eel else 1
   ball('EyeRim',(side*eye_x,eye_y,z),(L*.019*eye_scale,L*.026*eye_scale,L*.026*eye_scale),'M_BandIvory')
   ball('Eye',(side*(eye_x+L*.011),eye_y-L*.005,z),(L*.012*eye_scale,L*.016*eye_scale,L*.017*eye_scale),'M_Rubber')
   ball('EyeGlint',(side*(eye_x+L*.020),eye_y-L*.008,z+L*.006*eye_scale),(L*.004*eye_scale,)*3,'M_RailIvory')
  # Gill arcs and a short mouth are legible without tiny engraved scales.
  gz=.02 if eel else .08
  line('Gill',[(side*W*L*.86,-.29*L,-gz*.65*L),(side*W*L*.99,-.265*L,0),(side*W*L*.85,-.28*L,gz*L)],L*.0025,'M_Rubber')
  line('Mouth',[(side*W*L*.3,-.465*L,-.015*L),(side*W*L*.62,-.415*L,-.025*L)],L*.002,'M_Rubber')
 if flat:
  fin('Dorsal',[(y*L,z*L) for y,z in [(-.38,.09),(-.22,H*1.08),(0,H*1.16),(.21,H*.68),(.31,.04)]],fc,L*.008)
  fin('Anal',[(y*L,-z*L) for y,z in [(-.38,.09),(-.22,H*1.08),(0,H*1.16),(.21,H*.68),(.31,.04)]],fc,L*.008)
 elif eel:
  fin('Dorsal',[(y*L,z*L) for y,z in [(-.15,.04),(-.06,.085),(.25,.055),(.5,0),(.25,.025)]],fc,L*.004)
 else:
  if kind in ('cod','whiting','long'):
   for j in range(3):
    y=-.22+j*.17;fin('Dorsal'+str(j),[(y*L,H*.83*L),((y+.045)*L,H*1.42*L),((y+.12)*L,H*.72*L)],fc,L*.007)
  elif kind=='mullet':
   for y,h,w in [(-.20,1.50,.16),(.08,1.20,.12)]:
    fin('Dorsal',[(y*L,H*.87*L),((y+.045)*L,H*h*L),((y+w)*L,H*.72*L)],fc,L*.007)
  elif kind=='striped':
   fin('Dorsal',[(-.24*L,H*.85*L),(-.16*L,H*1.60*L),(-.02*L,H*.90*L)],fc,L*.007)
   fin('RearDorsal',[(.08*L,H*.85*L),(.14*L,H*1.15*L),(.21*L,H*.55*L)],fc,L*.006)
  elif kind=='spiny':
   poly=[(-.28*L,H*.75*L)]+[((-.26+i*.045)*L,H*(1.52 if i%2==0 else 1.05)*L) for i in range(10)]+[(.19*L,H*.6*L)]
   fin('SpinyDorsal',poly,fc,L*.007)
  else:fin('Dorsal',[(-.24*L,H*.85*L),(-.12*L,H*1.55*L),(.02*L,H*1.2*L),(.12*L,H*.75*L)],fc,L*.007)
  fin('Anal',[(.02*L,-H*.77*L),(.13*L,-H*1.3*L),(.24*L,-H*.50*L)],fc,L*.006)
  for side in [-1,1]:
   o=fin('Pectoral',[(-.22*L,0),(-.08*L,-.13*L),(.02*L,-.06*L)],fc,L*.006);o.location.x=side*W*.8*L;o.rotation_euler.y=side*.55
 if not eel:
  poly=[(.32*L,.025*L),(.52*L,.16*L),((.45 if flat else .44)*L,0),(.52*L,-.16*L),(.32*L,-.025*L)]
  if kind in ('flat','diamond','cod'):
   # Fan tails: these species should not inherit a schooling fish's deep fork.
   poly=[(.32*L,.025*L),(.47*L,.12*L),(.52*L,.075*L),(.52*L,-.075*L),(.47*L,-.12*L),(.32*L,-.025*L)]
  elif kind in ('whiting','long','mullet'):
   poly=[(.32*L,.025*L),(.52*L,.12*L),(.485*L,0),(.52*L,-.12*L),(.32*L,-.025*L)]
  tail=fin('Tail',poly,fc,L*.009)
  # Tail pivot at attachment, preserving runtime tail animation.
  off=Vector((0,.32*L,0))
  for v in tail.data.vertices:v.co-=off
  tail.location=off
 if kind=='striped':
  for j in range(7):
   y=(-.20+j*.065)*L;factor=1-abs(y/L)*1.5
   pts=[]
   for i in range(9):
    a=.15+i*.35;pts.append((W*L*factor*math.cos(a),y+math.sin(a*3)*L*.012,H*L*factor*math.sin(a)+L*.002))
   line('MackerelBand',pts,L*.005,'M_HullNavy')
 if kind in ('flat','diamond'):
  for y,z in [(-.15,.12),(-.05,-.12),(.05,.16),(.15,-.04),(-.24,-.04),(.02,.02)]:
   ball('Spot',(W*L*.97,y*L,z*L),(L*.006,L*.023,L*.019),'M_SafetyOrange' if kind=='flat' else 'M_CoastStone')
 if kind in ('cod','mullet'):
  for side in ([-1,1] if kind=='mullet' else [0]):
   line('Barbel',[(side*.02*L,-.42*L,-.09*L),(side*.03*L,-.46*L,-.22*L)],L*.003,'M_BandIvory')
 if kind=='mullet':
  pts=[]
  for y in [-.31,-.24,-.12,0,.08,.15]:
   k=next(i for i in range(len(profile)-1) if profile[i][0]<=y<=profile[i+1][0])
   ya,fa=profile[k];yb,fb=profile[k+1];f=fa+(fb-fa)*(y-ya)/(yb-ya)
   x=W*L*f*math.sqrt(1-(.015/(H*f))**2)+L*.002
   pts.append((x,y*L,-.015*L))
  for side in [-1,1]:line('GoldLateralLine',[(side*x,y,z) for x,y,z in pts],L*.004,'M_BandIvory')
 # Eel details follow its curved centreline, including the camera-facing eye.
 if eel:
  for o in list(GROUP.children_recursive):
   if o==body or o.type!='MESH':continue
   if o.name.startswith('Eye'):
    o.location.x+=math.sin((o.location.y/L+.5)*math.tau)*L*.055
   else:
    for v in o.data.vertices:v.co.x+=math.sin((v.co.y/L+.5)*math.tau)*L*.055
 # Consolidate static detail; retain just the animated tail as a separate object.
 bpy.ops.object.select_all(action='DESELECT')
 static=[o for o in GROUP.children_recursive if o.type=='MESH' and o.name!='Tail']
 for o in static:o.select_set(True)
 bpy.context.view_layer.objects.active=body;bpy.ops.object.join();body.name='Body'
 for o in GROUP.children_recursive:
  if o.type=='MESH':
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
 bpy.context.view_layer.update()
 # Portrait uses exactly the authored model, warm diffuse light, transparent margins.
 sc.render.engine='CYCLES';sc.cycles.samples=24;sc.cycles.use_denoising=True
 sc.render.resolution_x=512;sc.render.resolution_y=256;sc.render.resolution_percentage=100
 sc.render.film_transparent=True;sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGBA'
 sc.view_settings.view_transform='Standard';sc.view_settings.look='Medium High Contrast';sc.view_settings.exposure=0;sc.view_settings.gamma=1
 world=bpy.data.worlds.new('Soft coastal fill');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.74,.80,1);world.node_tree.nodes['Background'].inputs[1].default_value=.65;sc.world=world
 for n,pos,power,size in [('Warm key',(L,-L,2*L),80*L*L,1.4*L),('Cool fill',(-L,-.3*L,L),35*L*L,1.2*L)]:
  d=bpy.data.lights.new(n,'AREA');d.energy=power;d.size=size;d.color=(1,.86,.68) if n=='Warm key' else (.70,.85,1)
  o=bpy.data.objects.new(n,d);sc.collection.objects.link(o);o.location=pos;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
 d=bpy.data.cameras.new('Portrait');cam=bpy.data.objects.new('Portrait',d);sc.collection.objects.link(cam)
 cam.location=(L*1.8,-L*.25,L*.8);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();d.type='ORTHO';d.ortho_scale=L*(1.50 if kind=='diamond' else 1.25);sc.camera=cam
 folder=OUT/name;folder.mkdir(exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(folder/(name+'.blend')))
 bpy.ops.object.select_all(action='DESELECT')
 obs=[GROUP]+list(GROUP.children_recursive)
 for o in obs:o.select_set(True)
 bpy.context.view_layer.objects.active=GROUP
 bpy.ops.export_scene.fbx(filepath=str(folder/(name+'.fbx')),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',bake_space_transform=True,add_leaf_bones=False,bake_anim=False,path_mode='AUTO')
 sc.render.filepath=str(folder/('fish-'+('conger' if name=='CongerEel' else name.lower())+'.png'))
 bpy.ops.render.render(write_still=True)
 meshes=[o for o in obs if o.type=='MESH'];tri=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
 source_verts=sorted(tuple(round(v,5) for v in o.matrix_world@ve.co) for o in meshes for ve in o.data.vertices)
 src_bounds=[[min(v[i] for v in source_verts) for i in range(3)],[max(v[i] for v in source_verts) for i in range(3)]]
 # Actual saved source reopened, then actual exported FBX independently imported.
 bpy.ops.wm.open_mainfile(filepath=str(folder/(name+'.blend')))
 saved=[o for o in bpy.data.objects if o.type=='MESH'];savedtri=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in saved)
 savedverts=sorted(tuple(round(v,5) for v in o.matrix_world@ve.co) for o in saved for ve in o.data.vertices)
 assert savedverts==source_verts,(name,'saved-source vertices')
 assert savedtri==tri and tri<4000,(name,tri)
 saved_materials=sorted({m.name for o in saved for m in o.data.materials})
 assert all(m in COLORS for m in saved_materials),(name,'palette')
 assert not list(bpy.data.images),(name,'external or embedded textures')
 saved_hierarchy={o.name:(o.parent.name if o.parent else None) for o in saved}
 saved_pivots={o.name:tuple(round(v,6) for v in o.location) for o in saved}
 assert all(p=='Catchline_'+name for p in saved_hierarchy.values()),(name,'mesh parents')
 assert all(abs(v-1)<1e-6 for o in saved for v in o.scale),(name,'scale')
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(folder/(name+'.fbx')))
 imported=[o for o in bpy.data.objects if o.type=='MESH'];rttri=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in imported)
 rtverts=sorted(tuple(round(v,5) for v in o.matrix_world@ve.co) for o in imported for ve in o.data.vertices)
 assert rttri==tri,(name,tri,rttri)
 assert sorted({m.name for o in imported for m in o.data.materials})==saved_materials,(name,'FBX materials')
 assert {o.name:(o.parent.name if o.parent else None) for o in imported}==saved_hierarchy,(name,'FBX hierarchy')
 assert not list(bpy.data.images),(name,'FBX textures')
 assert len(rtverts)==len(source_verts),(name,'vertex count')
 # FBX may reorder vertices with near-equal X coordinates: compare spatial sets both ways.
 def distance(a,b):
  kd=KDTree(len(a))
  for i,v in enumerate(a):kd.insert(v,i)
  kd.balance();return max(kd.find(v)[2] for v in b)
 max_error=max(distance(source_verts,rtverts),distance(rtverts,source_verts))
 assert max_error<.0001,(name,'roundtrip',max_error)
 report={'name':name,'triangles':tri,'meshes':len(imported),'source_bounds':src_bounds,'saved_source_triangles':savedtri,'saved_source_vertices_equal':True,'source_vertex_count':len(source_verts),'materials':saved_materials,'mesh_parents':saved_hierarchy,'source_mesh_pivots':saved_pivots,'fbx_triangles':rttri,'vertex_max_roundtrip_error_m':max_error,'nose':'source -Y; exported Unity +Z','tail_pivot':('none; continuous eel body' if eel else 'attachment .32 * length on source Y; runtime retains Tail suffix'),'texture_dependencies':[],'portrait':[512,256],'validation':'saved source and actual FBX checked; Unity native appearance pending'}
 report['file_sha256']={q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in [folder/(name+'.blend'),folder/(name+'.fbx'),folder/('fish-'+('conger' if name=='CongerEel' else name.lower())+'.png')]}
 (folder/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print('FISH_DELIVERY',json.dumps(report),flush=True)

if __name__=='__main__':
 args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
 for row in FISH:
  if not args or row[0] in args:build(row)
