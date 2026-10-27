"""Table-contact pivots, one V4 atlas material, export only the named dish."""
import bpy,math,json,sys,shutil,hashlib,importlib.util,bmesh
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[3];sys.dont_write_bytecode=True
sp=importlib.util.spec_from_file_location('geometry',str(R/'Art/Source/build_crab_coast_props.py'));H=importlib.util.module_from_spec(sp);sp.loader.exec_module(H)
bpy.ops.wm.read_factory_settings(use_empty=True);sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
T=O/'textures';T.mkdir(exist_ok=True)
for n in ['Restaurant_BaseColor.png','Restaurant_Surface.png','atlas.json']:shutil.copyfile(O.parent/'Stage1V4/textures'/n,T/n)
cells={c['name']:c for c in json.loads((T/'atlas.json').read_text())['cells']}
mat=bpy.data.materials.new('Restaurant_Atlas_Dishes');mat.use_nodes=True;nt=mat.node_tree;bs=nt.nodes.get('Principled BSDF');im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(T/'Restaurant_BaseColor.png'));im.image.pack();nt.links.new(im.outputs['Color'],bs.inputs['Base Color']);surf=nt.nodes.new('ShaderNodeTexImage');surf.image=bpy.data.images.load(str(T/'Restaurant_Surface.png'));surf.image.colorspace_settings.name='Non-Color';surf.image.pack();sep=nt.nodes.new('ShaderNodeSeparateColor');nt.links.new(surf.outputs['Color'],sep.inputs[0]);nt.links.new(sep.outputs['Red'],bs.inputs['Roughness']);nt.links.new(sep.outputs['Green'],bs.inputs['Metallic'])
def lathe(g,profile,col,offset=(0,0,0),n=24):
 vs=[(offset[0]+r*math.cos(i*math.tau/n),offset[1]+r*math.sin(i*math.tau/n),offset[2]+z) for r,z in profile for i in range(n)];fs=[]
 for j in range(len(profile)-1):
  fs.extend([(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for i in range(n)])
 g.add(vs,fs,col)
def ring(g,r,z,col,c=(0,0),thick=.002):g.tube([(c[0]+r*math.cos(i*math.tau/32),c[1]+r*math.sin(i*math.tau/32),z) for i in range(33)],[thick]*33,6,col)
def plate(g):
 lathe(g,[(0,0),(.07,0),(.108,.009),(.138,.026),(.142,.034),(.138,.039),(.109,.02),(.07,.014),(0,.014)],'ivory');ring(g,.133,.038,'blue',thick=.0015)
def lemon(g,c,r=.024):
 # Flat upright quarter-round wedge: warm rind, pale pith, gold pulp sections.
 x,y,z=c;N=8
 def wedge(rad,depth,colour,zz):
  outline=[(x,y)]+[(x+rad*math.cos(a*math.pi/2/N),y+rad*math.sin(a*math.pi/2/N)) for a in range(N+1)]
  g.extrude_polygon(outline,zz,zz+depth,colour)
 wedge(r,.014,'brass',z);wedge(r*.88,.001,'white',z+.014);wedge(r*.76,.001,'glow',z+.015)
 for a in [math.pi/6,math.pi/3]:g.tube([(x,y,z+.017),(x+r*.76*math.cos(a),y+r*.76*math.sin(a),z+.017)],[.0007]*2,4,'white')
def herbs(g,x,y,z):
 for a in [0,2.1,4.2]:g.ellipsoid((x+.009*math.cos(a),y+.009*math.sin(a),z),(.013,.005,.002),8,3,'lettuce')
def ell(g,c,r,col):g.ellipsoid(c,r,12,5,col)
objects=[]
g=H.Geometry();lathe(g,[(0,0),(.049,0),(.068,.007),(.103,.073),(.107,.095),(.100,.101),(.093,.092),(.081,.029),(.04,.017),(0,.017)],'ivory');ring(g,.103,.1018,'blue',thick=.0014);lathe(g,[(0,.082),(.092,.082)],'soup');
for x,y in [(-.028,.027),(.035,.014),(.004,-.035)]:ell(g,(x,y,.085),(.022,.012,.008),'fish');herbs(g,x+.012,y+.008,.094)
objects.append(('Dish_FishSoup',g))
g=H.Geometry();plate(g)
for y in [-.027,.030]:
 ell(g,(-.014,y,.030),(.078,.024,.016),'food');ell(g,(-.014,y,.039),(.069,.020,.010),'white')
 for x in [-.047,-.016,.015]:g.tube([(x-.007,y-.014,.049),(x+.006,y+.014,.049)],[.0017]*2,5,'char')
lemon(g,(.064,-.023,.026),.035);herbs(g,-.077,-.064,.030);objects.append(('Dish_FilletsLemon',g))
g=H.Geometry();plate(g);ell(g,(-.013,0,.035),(.073,.035,.018),'food');ell(g,(-.075,0,.035),(.025,.023,.016),'fish');ell(g,(-.087,-.013,.049),(.003,.003,.002),'dark');g.extrude_polygon([(.04,-.009),(.101,-.033),(.091,0),(.101,.033),(.04,.009)],.026,.044,'food')
for x in [-.044,-.015,.014]:g.tube([(x-.006,-.025,.052),(x+.009,.025,.052)],[.002]*2,5,'char')
lemon(g,(-.025,.065,.026),.034);herbs(g,.045,-.065,.031);objects.append(('Dish_GrilledFish',g))
g=H.Geometry();lathe(g,[(0,0),(.049,0),(.084,.01),(.091,.015),(.087,.021),(.051,.014),(0,.013)],'ivory');ring(g,.084,.019,'blue',thick=.0013);lathe(g,[(0,.014),(.031,.014),(.045,.030),(.048,.094),(.044,.099),(.040,.094),(.036,.033),(0,.026)],'ivory');lathe(g,[(0,.089),(.041,.089)],'coffee');ring(g,.045,.098,'brass',thick=.0012)
g.tube([(.041+.025*math.sin(a),0,.056+.029*math.cos(a)) for a in [i*math.pi/16 for i in range(17)]],[.006]*17,8,'ivory')
for x in [-.041,.041]:
 ell(g,(x,-.066,.029),(.024,.014,.007),'food')
 for dx in [-.010,0,.010]:ell(g,(x+dx,-.067,.036),(.002,.002,.001),'char')
objects.append(('Dish_CoffeeBiscuits',g))
g=H.Geometry();lathe(g,[(0,0),(.034,0),(.037,.007),(.041,.133),(.040,.138),(.036,.139),(.035,.013),(0,.013)],'glass');lathe(g,[(0,.125),(.0365,.125)],'glow');ring(g,.039,.138,'white',thick=.0016);lemon(g,(.011,-.013,.132),.029);g.tube([(-.012,.010,.012),(-.012,.010,.154),(-.028,.010,.176)],[.0028]*3,6,'ivory');objects.append(('Dish_Lemonade',g))
rows=[]
for name,g in objects:
 me=bpy.data.meshes.new(name);me.from_pydata(g.vertices,[],g.faces);me.update();ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob);me.materials.append(mat)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free();uv=me.uv_layers.new(name='UVMap')
 for p,col in zip(me.polygons,g.colours):
  cell=cells[col];x,y,w,h=cell['pixel_cell'];coords=[me.vertices[me.loops[li].vertex_index].co for li in p.loop_indices];normal=p.normal;axis=max(range(3),key=lambda k:abs(normal[k]));axes=[k for k in range(3) if k!=axis];lo=[min(c[k] for c in coords) for k in axes];hi=[max(c[k] for c in coords) for k in axes]
  for li,c in zip(p.loop_indices,coords):
   u=(c[axes[0]]-lo[0])/max(hi[0]-lo[0],1e-7);v=(c[axes[1]]-lo[1])/max(hi[1]-lo[1],1e-7);uv.data[li].uv=((x+24+u*(w-48))/2048,1-(y+24+v*(h-48))/2048)
 me.calc_loop_triangles();vs=[v.co for v in me.vertices];lo=[min(v[k] for v in vs) for k in range(3)];hi=[max(v[k] for v in vs) for k in range(3)];assert abs(lo[2])<1e-6 and max(hi[k]-lo[k] for k in range(3))<.35
 bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
 bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,path_mode='COPY',embed_textures=True)
 rows.append({'name':name,'bounds_blender_m':[lo,hi],'triangles':len(me.loop_triangles),'atlas_cells':sorted(set(g.colours)),'fbx_sha256':hashlib.sha256((O/(name+'.fbx')).read_bytes()).hexdigest()})
bpy.ops.wm.save_as_mainfile(filepath=str(O/'RestaurantDishes.blend'));(O/'build-metrics.json').write_text(json.dumps({'dishes':rows,'units':'metres','origin':'table contact, z=0','material':'Restaurant_Atlas_Dishes','textures':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in T.glob('*.png')}},indent=2));print('DISH BUILD PASS',flush=True)
