"""Larger hull refinement, additive art authoring only. Windows Blender --python build2.py -- Name."""
import bpy,bmesh,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[3];sys.path.insert(0,str(Path(__file__).parent));import geometry2 as G
NAME=sys.argv[sys.argv.index('--')+1];OUT=R/'Art/Models/BoatsV2'/NAME;OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True);src=R/f'Assets/Art/Models/Boats/{NAME}.fbx';bpy.ops.import_scene.fbx(filepath=str(src));bpy.context.view_layer.update();oldobs=list(bpy.context.scene.objects);before=G.stats(oldobs);G.ROOT=bpy.data.objects.get('Catchline_'+NAME);Geo=G.Geo;ring=G.ring
isday=NAME=='DayBoat';wood=NAME in ['DayBoat','CompactFisherV1','PrepFisherV1'];half,bow,stern,bottom,base,lift= {'DayBoat':(2.9,6.5,5.5,-1.1,.60,.32),'CompactFisherV1':(1.4,2.8,2.6,-.57,.445,.22),'PrepFisherV1':(1.75,3.4,3.4,-.57,.445,.26),'Tier5FisherV1':(2.1,4.25,4.25,-.57,.445,.30)}[NAME]
# Retain source plan and add intermediate side stations for a smooth sheer sweep.
if isday:plan=[(-2.9,5.5),(2.9,5.5),(2.9,3),(2.9,0),(2.9,-2.5),(2.9,-5),(1.8,-6.05),(0,-6.5),(-1.8,-6.05),(-2.9,-5),(-2.9,-2.5),(-2.9,0),(-2.9,3)]
else:
 raw=[(-1.1,2.6),(1.1,2.6),(1.34,2.34),(1.4,1.55),(1.4,0),(1.4,-1.45),(1.38,-1.92),(1.34,-2.13),(.94,-2.3),(.48,-2.65),(0,-2.8),(-.48,-2.65),(-.94,-2.3),(-1.34,-2.13),(-1.38,-1.92),(-1.4,-1.45),(-1.4,0),(-1.4,1.55),(-1.34,2.34)]
 plan=[(x*half/1.4,(y+2.8)*(bow+stern)/5.4-bow) for x,y in raw]
def sheer(y):return base+lift*(max(0,-y)/bow)**2+.10*(max(0,y)/stern)**2
# Underwater rake remains outside existing deck footprint at deck level.
def level(t,proud=0):
 f=.72+.28*min(1,t/.42);fy=.85+.15*min(1,t/.42)
 return [(x*f+proud*x/half,y*fy,bottom+(sheer(y)-bottom)*t) for x,y in plan]
g=Geo();last=level(0);n=len(plan)
courses=3 if NAME in ['CompactFisherV1','PrepFisherV1'] else 4
for k in range(1,courses+1):
 t=k/courses
 if k==1:
  a,b=level(.19),level(.26);ring(g,last,a,'M_HullNavy');last=b
 if k==2:
  shoulder=level(.42);ring(g,last,shoulder,'M_HullNavy');last=shoulder
 up=level(t);ring(g,last,up,'M_HullNavy')
 if k<courses:
  lip=level(t,.020 if wood else .005);ring(g,up,lip,'M_ClinkerRecess' if wood else 'M_HullBlue')
  rev=[(x,y,z+(.018 if wood else .008)) for x,y,z in lip];ring(g,lip,rev,'M_ClinkerRecess' if wood else 'M_HullBlue');last=rev
 else:last=up
# Interior painted lining offset from actual outer shell.
outer=level(1);inner=[(x*.955,y*.98,z) for x,y,z in outer];ring(g,outer,inner,'M_WoodHighlight' if wood else 'M_RailIvory');low=[(x*.82,y*.94,-.13) for x,y in plan];ring(g,inner,low,'M_DeckWood' if wood else 'M_RailIvory');g.add(level(0),[tuple(reversed(range(n)))],'M_HullNavy');g.mesh('Hull',bpy.data.objects['Hull'])
# Original guardrail/hardware retains node transform; only its upper rail follows new sheer.
railname='Rails' if isday else 'GunwaleHardware';rail=bpy.data.objects[railname];inv=rail.matrix_world.inverted()
for v in rail.data.vertices:
 p=rail.matrix_world@v.co
 if isday:
  dz=lift*(max(0,-p.y)/bow)**2+.10*(max(0,p.y)/stern)**2
 else:
  # source sheer .43 + .055*(y / 2.8)^2, rescaled on larger hulls
  sourcey=(p.y+bow)*5.4/(bow+stern)-2.8;dz=sheer(p.y)-(.43+.055*(sourcey/2.8)**2)
 p.z+=dz*min(1,max(0,(p.z-.02)/.25));v.co=inv@p
# A continuous cap tied exactly to the new shell, plus rubbing strake.
g=Geo()
for zoff,height,width,m in [(.012,.055,.07,'M_RailIvory'),(-.085,.045,.038,'M_WoodHighlight' if wood else 'M_HullBlue')]:
 a=[(x*(1+width/half),y*1.005,sheer(y)+zoff) for x,y in plan];b=[(x,y,z+height) for x,y,z in a];c=[(x*.975,y*.99,z) for x,y,z in b];d=[(x,y,z-height) for x,y,z in c]
 for aa,bb in [(a,b),(b,c),(c,d),(d,a)]:ring(g,aa,bb,m)
g.mesh('SweptCapAndRubber')
# Continuous boot-top lies flush on the actual faceted shell between course boundaries.
g=Geo();ring(g,level(.19),level(.26),'M_SafetyOrange');g.mesh('WaterlineStripe' if isday else 'HullPaintBand',bpy.data.objects['WaterlineStripe' if isday else 'HullPaintBand'])
g=Geo();g.beam((0,stern*.94,bottom-.025),(0,-bow*.94,bottom-.025),.11,.14,'M_WoodRecess' if wood else 'M_HullNavy');g.beam((0,-bow*.94,bottom-.025),(0,-bow*1.008,sheer(-bow)+.01),.10,.09,'M_WoodRecess' if wood else 'M_HullNavy');g.mesh('KeelAndRakedStem')
# A single purposeful canopy drip lip, entirely within the existing roof overhang.
if NAME in ['CompactFisherV1','PrepFisherV1']:
 roof=bpy.data.objects['HelmRoof' if NAME=='CompactFisherV1' else 'squared helm canopy']
 vs=[roof.matrix_world@v.co for v in roof.data.vertices];xmin=min(v.x for v in vs);xmax=max(v.x for v in vs);ymin=min(v.y for v in vs);ymax=max(v.y for v in vs);z=min(v.z for v in vs)+.035
 g=Geo();corners=[(xmin+.015,ymin+.015,z),(xmax-.015,ymin+.015,z),(xmax-.015,ymax-.015,z),(xmin+.015,ymax-.015,z)]
 for i in range(4):g.beam(corners[i],corners[(i+1)%4],.055,.055,'M_RailIvory')
 g.mesh('CanopyDripLip',bevel=.009)
 if NAME=='PrepFisherV1':
  # Four triangular timber brackets stay against canopy uprights, above the working floor.
  g=Geo()
  for side in [-1,1]:
   for y in [ymin+.15,ymax-.15]:
    x=side*.81;z0=1.01;verts=[(x+dx,y+dy,z0+dz) for dx in [-.035,.035] for dy,dz in [(0,0),(0,.30),(-.25 if y>(ymin+ymax)/2 else .25,.30)]]
    g.add(verts,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],'M_WoodHighlight')
  g.mesh('CanopyTimberKnees',bevel=.012)
bpy.context.view_layer.update();obs=list(bpy.context.scene.objects);after=G.stats(obs);oldtri=sum(d['triangles'] for d in before.values());tri=sum(d['triangles'] for d in after.values());assert tri<=int(oldtri*1.4),(NAME,oldtri,tri)
for n,d in before.items():
 assert n in after and after[n]['parent']==d['parent'],n
 assert max(abs(d[k][i][j]-after[n][k][i][j]) for k in ['local','world'] for i in range(4) for j in range(4))<1e-6,n
# Existing shaders retain house palette; new additions are matte and texture free.
for m in list(bpy.data.materials):
 if m.name in G.PALETTE:G.mat(m.name)
bpy.ops.object.select_all(action='DESELECT')
for o in obs:o.select_set(True)
bpy.ops.export_scene.fbx(filepath=str(OUT/(NAME+'.fbx')),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',add_leaf_bones=False,bake_anim=False,path_mode='AUTO')
bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(NAME+'.blend')))
(OUT/'build-metrics.json').write_text(json.dumps({'name':NAME,'triangles':tri,'original_triangles':oldtri,'triangle_cap':int(oldtri*1.4),'before':before,'after':after,'modified_legacy_meshes':['Hull',railname,'WaterlineStripe' if isday else 'HullPaintBand'],'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'construction':'clinker timber' if wood else 'welded steel plates'},indent=2));print('BUILD PASS',NAME,oldtri,tri,flush=True)
