"""Reopen editable files, then independently import actual FBX and compare surfaces/actions."""
import bpy,sys,math,json,importlib.util
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path(__file__).resolve().parent));import build as B
sp=importlib.util.spec_from_file_location('surface_check',str(B.R/'Art/Source/HarbourV2/audit.py'));A=importlib.util.module_from_spec(sp);sp.loader.exec_module(A)
def geometry(ev=False):
 bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();rows={}
 for o in bpy.context.scene.objects:
  if o.type!='MESH':continue
  e=o.evaluated_get(dg) if ev else o;e.data.calc_loop_triangles();rows[o.name]={'vertices':[tuple(e.matrix_world@v.co) for v in e.data.vertices],'triangles':[tuple(t.vertices) for t in e.data.loop_triangles],'faces':[tuple(p.vertices) for p in e.data.polygons]}
 return rows
def sway():
 rig=bpy.data.objects['KelpStrand'];assert len(rig.data.bones)==3
 act=next(a for a in bpy.data.actions if a.name.split('|')[-1]=='Sway');rig.animation_data.action=act;assert max(abs(x-y) for x,y in zip(act.frame_range,(1,121)))<.001
 out={}
 for f in [1,31,61,91,121]:bpy.context.scene.frame_set(f);out[f]=geometry(True)
 vs=lambda f:out[f]['KelpRibbon']['vertices'];delta=lambda f:max((Vector(x)-Vector(y)).length for x,y in zip(vs(1),vs(f)))
 assert delta(121)<.00002;assert max(delta(f) for f in out)>.10
 for f in range(1,122):
  bpy.context.scene.frame_set(f);assert rig.location.length<1e-6;assert rig.pose.bones['Kelp_0'].location.length<1e-6
 return out,{'name':act.name,'frames':[1,121],'seconds':4,'loop':True,'motion_m':max(delta(f) for f in out),'closure_m':delta(121),'samples':[1,31,61,91,121]}
def run(kit):
 O=B.R/'Art/Models'/kit;bpy.ops.wm.open_mainfile(filepath=str(O/(kit+'.blend')));src=B.snapshot();geo=geometry();colors={m.name:list(m.diffuse_color) for m in bpy.data.materials};assert src['triangles']<=2500
 assert sorted(o.name for o in bpy.data.objects[kit].children)==sorted(B.ITEMS[kit]);assert not list(bpy.data.images)
 for o in bpy.context.scene.objects:
  assert o.location.length<1e-7 and max(abs(x-1) for x in o.scale)<1e-7
  if o.type!='MESH':continue
  assert not o.data.validate(verbose=True,clean_customdata=False);assert all(p.area>1e-12 for p in o.data.polygons),(o.name,'degenerate');assert all(math.isfinite(x) for v in o.data.vertices for x in v.co)
  assert all(m.name in B.P for m in o.data.materials)
  if o.name=='KelpRibbon':assert all(abs(sum(w.weight for w in v.groups)-1)<1e-6 for v in o.data.vertices)
 def bounds(n):return src['items'][n]['bounds_blender']
 if kit=='JigKit':
  lo,hi=bounds('JigPirk');assert abs(lo[2]+.14)<1e-6 and abs(hi[2])<.0004
  lo,hi=bounds('JigLine');assert abs(lo[2]+1)<1e-6 and abs(hi[2])<1e-7;assert abs(hi[0]-lo[0]-.004)<1e-7
  lo,hi=bounds('KelpRibbon');assert abs(hi[2]-lo[2]-2.5)<1e-6
  assert len(bpy.data.objects['MoteCloud'].data.polygons)==50
  lo,hi=bounds('SeabedRocks');assert abs(hi[0]-lo[0]-3)<1e-6
 else:
  lo,hi=bounds('TornNet');assert abs(hi[0]-lo[0]-1.212)<1e-6 and abs(hi[1]-lo[1]-.812)<1e-6
  assert all(math.hypot(v.co.x,v.co.y)>.143 for v in bpy.data.objects['TornNet'].data.vertices)
  lo,hi=bounds('NettingNeedle');assert abs(hi[0]-lo[0]-.2)<1e-6
 poses,info=sway() if kit=='JigKit' else ({},{})
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=30;bpy.ops.import_scene.fbx(filepath=str(O/(kit+'.fbx')));imp=B.snapshot();assert imp['parents']==src['parents'];assert imp['triangles']==src['triangles'];surface=A.same_geometry(geo,geometry())
 assert set(colors)=={m.name for m in bpy.data.materials}
 for m in bpy.data.materials:assert max(abs(x-y) for x,y in zip(colors[m.name],m.diffuse_color))<1e-5
 ps,inf=sway() if kit=='JigKit' else ({},{})
 animation={str(f):A.same_geometry(poses[f],ps[f]) for f in poses}
 row=json.loads((O/'metrics/build.json').read_text());assert all(row['sha256'][e]==B.sha(O/(kit+'.'+e)) for e in ['blend','fbx'])
 out={'result':'PASS','source':src,'imported':imp,'surface':surface,'sway_source':info,'sway_imported':inf,'animation':animation,'material_rgba_linear':colors,'sha256':row['sha256']};(O/'metrics/audit.json').write_text(json.dumps(out,indent=2)+'\n');print('KIT AUDIT PASS',kit,src['triangles'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
