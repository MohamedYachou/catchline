"""All-frame source/actual-FBX semantic and envelope checks, independent from authoring."""
import bpy,sys,json,math
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
import audit as A

def check(name,imported):
 root=bpy.data.objects[name];start=root.matrix_world.copy();sc=bpy.context.scene
 mesh=next(o for o in sc.objects if o.type=='MESH');assert all(abs(a-b)<1e-5 for m in bpy.data.materials for a,b in zip(m.diffuse_color,B.H.linear_colour(B.P[m.name])))
 rows={};rig=next((o for o in sc.objects if o.type=='ARMATURE'),None)
 if name=='KittiwakeFlock':
  counts={}
  for i in range(3):
   n='Bird_'+str(i+1);ids={v.index for v in mesh.data.vertices if any(mesh.vertex_groups[w.group].name.startswith(n) and w.weight>.99 for w in v.groups)}
   counts[n]=sum(len(p.vertices)-2 for p in mesh.data.polygons if set(p.vertices)<=ids);assert 0<counts[n]<=300
  rows['bird_triangles']=counts
 semantic={}
 for clip,(end,loop) in B.CLIPS.get(name,{}).items():
  traces=[]
  A.activate(rig,clip);envelope=[[],[],[]];radii=[];heights=[];max_water=-999;min_water=999;mid_tail=None
  for f in range(1,end+1):
   sc.frame_set(f);bpy.context.view_layer.update();assert max(abs(root.matrix_world[i][j]-start[i][j]) for i in range(4) for j in range(4))<2e-6
   pts=[Vector(v) for d in A.geometry(True).values() for v in d['vertices']]
   if name=='Humpback':
    evaluated=mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    def part(pred):
     return [evaluated.matrix_world@evaluated.data.vertices[v.index].co for v in mesh.data.vertices if pred(v)]
    def group(v,n):return any(mesh.vertex_groups[w.group].name==n and w.weight>.99 for w in v.groups)
    tailpts=part(lambda v:group(v,'Tail') and v.co.y>3.6)
    bodypts=part(lambda v:group(v,'Body') and v.co.y<2.28)
    headpts=part(lambda v:group(v,'Body') and v.co.y<-3)
    pecpts=part(lambda v:group(v,'Pectoral.L'))
    centre=sum(tailpts,Vector())/len(tailpts)
    normal=(rig.matrix_world@rig.pose.bones['Tail'].matrix).to_3x3()@Vector((0,0,1));normal.normalize()
    traces.append({'frame':f,'tail_max_z':max(p.z for p in tailpts),'tail_centre_xyz':list(centre),'tail_plane_normal_z':normal.z,'front_body_max_z':max(p.z for p in bodypts),'head_max_z':max(p.z for p in headpts),'pec_max_z':max(p.z for p in pecpts),'whole_max_z':max(p.z for p in pts)})
   for i in range(3):envelope[i].extend(p[i] for p in pts)
   max_water=max(max_water,max(p.z for p in pts));min_water=min(min_water,min(p.z for p in pts))
   if name=='KittiwakeFlock':
    for i in range(3):
     c=rig.matrix_world@rig.pose.bones['Bird_'+str(i+1)].head;r=math.hypot(c.x,c.y);radii.append(r);heights.append(c.z);assert abs(r-3)<2e-5
   if name=='BaitBall':assert max(p.z for p in pts)<-.035,'fish must remain below water'
   if name=='Humpback' and clip=='Fluke' and f==46:
    tail=rig.matrix_world@rig.pose.bones['Tail'].tail;mid_tail=list(tail);assert max(p.z for p in pts)>1
  if name=='Humpback':assert min_water>-8,'dive must fit measured Whale shelf anchor depth'
  row={'fixed_world_root_all_frames':True,'bounds_xyz_m':[[min(d) for d in envelope],[max(d) for d in envelope]],'water_z_min_max_m':[min_water,max_water]}
  if radii:row.update(orbit_radius_m=[min(radii),max(radii)],bird_head_altitude_m=[min(heights),max(heights)])
  if traces:
   row['fix_motion_samples']=traces
   if clip=='Surface':
    assert traces[0]['whole_max_z']<0 and traces[-1]['whole_max_z']<0
    crest=max(r['front_body_max_z'] for r in traces);assert .6<crest<1.05,crest
    assert max(r['head_max_z'] for r in traces)>.3
    assert max(r['pec_max_z'] for r in traces)>.15
    breaches=[r['pec_max_z']>0 for r in traces];assert sum(a!=b for a,b in zip(breaches,breaches[1:]))==2
    row['surface_fix']={'back_crest_m':crest,'head_crest_m':max(r['head_max_z'] for r in traces),'one_pectoral_breach':True,'submerged_endpoints':True}
   if clip=='Fluke':
    hold=[r for r in traces if 28<=r['frame']<=46]
    assert all(2.5<r['tail_max_z']<3.15 for r in hold),hold[0]
    assert all(abs(r['tail_plane_normal_z'])<.12 for r in hold)
    assert all(r['front_body_max_z']<0 for r in hold)
    delta=max((Vector(r['tail_centre_xyz'])-Vector(hold[0]['tail_centre_xyz'])).length for r in hold);assert delta<2e-5
    descent=[r for r in traces if r['frame']>=46]
    xy=max(math.hypot(r['tail_centre_xyz'][0]-descent[0]['tail_centre_xyz'][0],r['tail_centre_xyz'][1]-descent[0]['tail_centre_xyz'][1]) for r in descent);assert xy<2e-5,xy
    assert all(b['tail_max_z']<=a['tail_max_z']+1e-5 for a,b in zip(descent,descent[1:]))
    assert traces[-1]['whole_max_z']<0
    row['fluke_fix']={'hold_seconds':.6,'tail_peak_m':hold[0]['tail_max_z'],'vertical_plane_normal_z':hold[0]['tail_plane_normal_z'],'front_submerged_during_hold':True,'hold_max_drift_m':delta,'descent_horizontal_drift_m':xy,'final_whole_max_z':traces[-1]['whole_max_z']}
  if mid_tail:row['mid_tail_bone_end_xyz_m']=mid_tail
  rows[clip]=row
 if name=='BlowSpout':
  v=[mesh.matrix_world@v.co for v in mesh.data.vertices];height=max(p.z for p in v)-min(p.z for p in v);assert 2.8<height<3.2;rows['vapour_height_m']=height
  assert all(m.diffuse_color[3]==1 for m in bpy.data.materials)
  assert all(next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED').inputs['Alpha'].default_value==1 for m in bpy.data.materials)
  rows['opaque_materials']=True
 return rows
out=json.loads((B.O/'metrics/contract-audit.json').read_text()).get('items',{})
for name in (sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else B.LIMITS):
 bpy.ops.wm.open_mainfile(filepath=str(B.O/(name+'.blend')));source=check(name,False)
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30;bpy.ops.import_scene.fbx(filepath=str(B.O/(name+'.fbx')));actual=check(name,True)
 out[name]={'source':source,'actual_fbx':actual,'sha256':{e:B.sha(B.O/(name+'.'+e)) for e in ('blend','fbx')}};print('CONTRACT PASS',name,flush=True)
(B.O/'metrics/contract-audit.json').write_text(json.dumps({'result':'PASS','items':out},indent=2)+'\n')
