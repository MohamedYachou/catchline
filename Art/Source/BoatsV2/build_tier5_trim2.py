"""Trim only on the live tier5 hull; never rewrite its shell or optional groups."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(Path(__file__).parent));import geometry2 as G
NAME='Tier5DeepLines103';O=R/'Art/Models/BoatsV2'/NAME;O.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
src=R/f'Assets/Art/Models/Boats/{NAME}.fbx';bpy.ops.import_scene.fbx(filepath=str(src));bpy.context.view_layer.update()
G.ROOT=None;before=G.stats(list(bpy.context.scene.objects));h=bpy.data.objects['Hull'];vs=[h.matrix_world@v.co for v in h.data.vertices]
def unique(points):
 out=[]
 for p in points:
  if not any((p-q).length<1e-5 for q in out):out.append(p.copy())
 return out
upper=unique([p for p in vs if .43<p.z<.49]);upper.sort(key=lambda p:math.atan2(p.y,p.x))
lower=unique([p for p in vs if abs(p.z+.05)<1e-4])
assert len(upper)==len(lower)==15,(len(upper),len(lower))
low=[min(lower,key=lambda p:(Vector((p.x,p.y))-Vector((u.x*.94,u.y*.985))).length) for u in upper]
assert len({tuple(p) for p in low})==len(low)
def surface(t,proud=0,zoff=0):
 out=[]
 for a,b in zip(low,upper):
  p=a.lerp(b,t);normal=Vector((p.x/2.1,p.y/4.25,0)).normalized();p+=normal*proud;p.z+=zoff;out.append(tuple(p))
 return out
# The cap follows the existing sheer. No shell, rail, deck or footprint reshaping.
g=G.Geo();a=surface(1,.035,.012);b=[(x,y,z+.055) for x,y,z in a];c=surface(1,-.055,.067);d=surface(1,-.055,.012)
for aa,bb in [(a,b),(b,c),(c,d),(d,a)]:G.ring(g,aa,bb,'M_RailIvory')
g.mesh('FleetIvoryCap')
g=G.Geo()
for t,width,proud,material in [(.77,.032,.018,'M_HullBlue'),(.32,.016,.009,'M_ClinkerRecess'),(.57,.016,.009,'M_ClinkerRecess')]:
 a=surface(t,proud);b=[(x,y,z+width) for x,y,z in a];c=surface(t,.002,width);d=surface(t,.002)
 for aa,bb in [(a,b),(b,c),(c,d),(d,a)]:G.ring(g,aa,bb,material)
g.mesh('FleetRubbingAndQuietCourses')
modified=[]
for j in [1,2]:
 ob=bpy.data.objects[f'Deep {j} rail clamp'];center=ob.matrix_world.translation.copy();g=G.Geo()
 # One faceted saddle and narrow steel retaining strap, below the original rail envelope.
 g.box(tuple(center),(.205,.28,.265),'M_HullNavy');g.mesh(ob.name,ob,bevel=.018)
 # The steel collar is integrated in the same named mesh without a new optional root.
 me=ob.data;world=[ob.matrix_world@v.co for v in me.vertices];faces=[tuple(p.vertices) for p in me.polygons]
 g=G.Geo();g.add([tuple(v) for v in world],faces,'M_HullNavy');g.box(tuple(center+Vector((0,0,.090))),(.215,.11,.045),'M_Steel');g.mesh(ob.name,ob)
 modified.append(ob.name)
bpy.context.view_layer.update();after=G.stats(list(bpy.context.scene.objects));tri=sum(d['triangles'] for d in after.values());oldtri=sum(d['triangles'] for d in before.values())
assert tri<=int(oldtri*1.4)
for n,d in before.items():
 assert n in after and d['parent']==after[n]['parent'],n
 assert max(abs(d[k][i][j]-after[n][k][i][j]) for k in ['local','world'] for i in range(4) for j in range(4))<1e-6,n
for m in list(bpy.data.materials):
 if m.name in G.PALETTE:G.mat(m.name)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(O/(NAME+'.fbx')),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False,use_custom_props=True)
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(O/(NAME+'.blend')))
(O/'build-metrics.json').write_text(json.dumps({'name':NAME,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'original_triangles':oldtri,'triangles':tri,'triangle_cap':int(oldtri*1.4),'modified_legacy_meshes':modified,'before':before,'after':after,'construction':'original hull/deck preserved; additive trim only; simplified two rig saddles'},indent=2))
print('BUILD PASS',NAME,oldtri,tri,flush=True)
