"""Read-only independently imported critic versus delivered Ada FBX and settings."""
import bpy,sys,json,re,hashlib
from pathlib import Path
from io_scene_fbx import import_fbx,parse_fbx
from mathutils import Vector
O=Path(__file__).resolve().parent;R=O.parents[2]
class Op:
 def report(self,*a):print(*a)
def snapshot(path):
 bpy.ops.wm.read_factory_settings(use_empty=True);import_fbx.load(Op(),bpy.context,filepath=str(path),use_anim=True);bpy.context.view_layer.update()
 rig=next(o for o in bpy.data.objects if o.type=='ARMATURE');bones={b.name:dict(parent=b.parent.name if b.parent else None,matrix=[list(r) for r in b.matrix_local]) for b in rig.data.bones}
 clips={}
 for a in bpy.data.actions:
  key=a.name.split('|')[-1];rig.animation_data_create();rig.animation_data.action=a
  if a.slots:rig.animation_data.action_slot=a.slots[0]
  frames=sorted(set([int(a.frame_range[0]),int(a.frame_range[1]),int(sum(a.frame_range)/2),int(a.frame_range[0]+(a.frame_range[1]-a.frame_range[0])*.25)]));samples=[]
  for f in frames:
   bpy.context.scene.frame_set(f);bpy.context.view_layer.update();samples.append({b.name:[list(r) for r in b.matrix] for b in rig.pose.bones})
  clips[key]=dict(range=list(a.frame_range),frames=frames,samples=samples)
 return rig,bones,clips
def matrix_error(a,b):return max(abs(x-y) for ar,br in zip(a,b) for x,y in zip(ar,br))
path=R/'Assets/Art/Models/Restaurant/Guests/Restaurant_Guest_Critic.fbx';ada=path.with_name('Restaurant_Guest_Ada.fbx')
ar,ab,ac=snapshot(ada);an=ar.name;cr,cb,cc=snapshot(path)
assert cr.name==an=='CrewRig';assert set(ab)==set(cb)
restmax=0
for name in ab:
 assert ab[name]['parent']==cb[name]['parent'];err=matrix_error(ab[name]['matrix'],cb[name]['matrix']);restmax=max(restmax,err);assert err<.00001,(name,err)
assert set(ac)==set(cc),(set(ac),set(cc));maxerr=0
for key in ac:
 assert ac[key]['range']==cc[key]['range'] and ac[key]['frames']==cc[key]['frames'],key
 for sa,sc in zip(ac[key]['samples'],cc[key]['samples']):
  for bone in sa:
   err=matrix_error(sa[bone],sc[bone]);maxerr=max(maxerr,err);assert err<.00003,(key,bone,err)
obs=[o for o in bpy.data.objects if o.type=='MESH'];tris=0
for o in obs:
 assert o.parent==cr and any(m.type=='ARMATURE' and m.object==cr for m in o.modifiers)
 me=o.data;me.calc_loop_triangles();tris+=len(me.loop_triangles);assert not any(t.area<1e-12 for t in me.loop_triangles),(o.name,'degenerate')
 assert len(me.materials)==1 and me.materials[0].name=='RestaurantAtlas';assert len(me.uv_layers)==1 and me.color_attributes.active_color
 assert all(abs(d.uv.x-7.5/8)<1e-6 and abs(d.uv.y-.625)<1e-6 for d in me.uv_layers.active.data)
 assert all(abs(d.color[3]-1)<1e-6 for d in me.color_attributes.active_color.data)
 for v in me.vertices:
  assert abs(sum(g.weight for g in v.groups)-1)<.00001 and len(v.groups)<=4
  if o.name=='Critic_Notebook':assert all(o.vertex_groups[g.group].name=='LeftHand' and abs(g.weight-1)<1e-5 for g in v.groups)
assert any(o.name=='Critic_Notebook' for o in obs);assert tris<6000
meta=Path(str(path)+'.meta').read_text();am=Path(str(ada)+'.meta').read_text()
norm=lambda t:re.sub(r'^guid: .+$','guid: GUID',t,flags=re.M)
remap='  externalObjects:\n  - first:\n      type: UnityEngine:Material\n      assembly: UnityEngine.CoreModule\n      name: RestaurantAtlas\n    second: {fileID: 2100000, guid: 93ede68a78343aa4bbc6d4deed7baeec, type: 2}'
assert norm(meta.replace(remap,'  externalObjects: {}'))==norm(am)
rec=next(r for r in json.loads((O/'props3-manifest.json').read_text()) if r['name']=='Restaurant_Guest_Critic');assert rec['tris']==tris and rec['sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
tree,ver=parse_fbx.parse(str(path));objects=next(e for e in tree.elems if e.id==b'Objects')
for geometry in [e for e in objects.elems if e.id==b'Geometry']:
 indices=next(e for e in geometry.elems if e.id==b'PolygonVertexIndex').props[0];assert len(indices)%3==0
 for lid,iid in [(b'LayerElementNormal',b'NormalsIndex'),(b'LayerElementColor',b'ColorIndex'),(b'LayerElementUV',b'UVIndex')]:
  layer=next(e for e in geometry.elems if e.id==lid);assert len(next(e for e in layer.elems if e.id==iid).props[0])==len(indices)
base=json.loads((O/'props3-preservation.json').read_text());assert all(hashlib.sha256((R/p).read_bytes()).hexdigest()==h for p,h in base.items())
out=dict(status='PASS',tris=tris,bones=len(cb),bone_parent_and_rest_parity=True,max_rest_matrix_error=restmax,clips={k:dict(range=v['range'],sampled_frames=v['frames']) for k,v in cc.items()},max_animated_bone_matrix_error=maxerr,notebook_LeftHand_weight=1,normalized_weights=True,complete_corner_layers=True,zero_degenerate=True,Ada_importer_parity_except_GUID_and_material_remap=True,preserved_dependencies=len(base),runtime_Unity_acceptance='Not run; task prohibits Unity')
(O/'props3-critic-audit.json').write_text(json.dumps(out,indent=2)+'\n');print('CRITIC AUDIT PASS',tris,len(cb),len(cc),restmax,maxerr,flush=True)
