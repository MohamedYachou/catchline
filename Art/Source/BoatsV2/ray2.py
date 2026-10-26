from pathlib import Path
p=Path(__file__).with_name('review2.py');s=p.read_text();s=s.replace("if '--audit-only' in sys.argv:sys.exit(0)","")
s=s.replace("views={k:views[k] for k in ['front-three-quarter','side','game-exact-45']}","views={k:views[k] for k in ['front-three-quarter','side']}")
s=s.replace('bpy.ops.render.render(write_still=True)', '''\n  for px,py in ([(500,463),(463,470)] if label=='front-three-quarter' else [(605,350)]):
   start=cam.matrix_world@Vector(((px/800-.5)*cam.data.ortho_scale,(.5-py/600)*cam.data.ortho_scale*.75,0));direction=cam.rotation_euler.to_matrix()@Vector((0,0,-1));hit,loc,normal,idx,obj,mat=sc.ray_cast(bpy.context.evaluated_depsgraph_get(),start,direction);print('RAY',label,px,py,obj.name if hit else None,list(loc),flush=True)
 ''')
s=s.replace(";print('RENDER PASS'","  print('RENDER PASS'")
exec(compile(s,str(p),'exec'))
