"""Reopen artist fixture; measure required camera and six-fish nominal bag fit."""
import sys,math,json
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build as B
O=B.O
bpy.ops.wm.open_mainfile(filepath=str(O/'NetKit-camera-fixture.blend'))
sc=bpy.context.scene;cam=sc.camera;root=bpy.data.objects['NetBunt'];fill=bpy.data.objects['Fill']
meta=json.loads((O/'assembly.json').read_text())
assert (cam.location-Vector((0,0,2))).length<1e-6
forward=cam.rotation_euler.to_quaternion()@Vector((0,0,-1))
pitch=math.degrees(math.asin(-forward.z));fov=math.degrees(2*math.atan(cam.data.sensor_height/(2*cam.data.lens)))
assert abs(pitch-34)<1e-5 and abs(fov-54)<1e-5 and cam.data.sensor_fit=='VERTICAL',(pitch,fov)
assert abs(B.to_u(root.location)[2]-2.5)<1e-6
assert len(meta['fish'])==6
profile=[(0,.44,.29,0),(.10,.53,.36,-.05),(.23,.55,.38,-.075),(.37,.49,.35,-.105),(.51,.36,.28,-.12),(.63,.19,.15,-.14),(.70,.030,.025,-.16)]
def envelope(p,taut):
    x,y,z=p
    if taut:
        z=z if z<=.045 else (z+.0171)/1.38
        t=max(0,min(1,(z-.045)/.155));s=t*t*(3-2*t);x/=(1-.28*s);y/=(1-.22*s)
    assert 0<=z<=.70,('fish outside bag depth',z)
    i=next(i for i in range(6) if profile[i][0]<=z<=profile[i+1][0])
    a,b=profile[i:i+2];t=(z-a[0])/(b[0]-a[0]);rx,ry,cy=[a[k]+t*(b[k]-a[k]) for k in (1,2,3)]
    return math.sqrt((x/rx)**2+((y-cy)/ry)**2)
rows=[]
for taut in (False,True):
    bpy.data.objects['Bunt'].data.shape_keys.key_blocks['Taut'].value=int(taut)
    fill.location=B.to_b(B.stretch((0,-.09,.31)) if taut else (0,-.09,.31))
    fish=[]
    for item in meta['fish']:
        f=bpy.data.objects[item['root']];p=item['fill_local_unity'];f.location=B.to_b((p[0]*(.72 if taut else 1),p[1]*(.78 if taut else 1),p[2]))
        k=.82*(.8 if taut else 1);f.scale=(k,k,k)
        bodies=[o for o in f.children_recursive if o.type=='MESH'];assert bodies
        fish.extend(bodies)
    bpy.context.view_layer.update()
    world=[o.matrix_world@v.co for o in fish for v in o.data.vertices]
    ratio=max(envelope(B.to_u(root.matrix_world.inverted()@p),taut) for p in world)
    assert ratio<1,('nominal bag envelope exceeded',taut,ratio)
    views=[]
    for width,height in ((1440,900),(844,390)):
        sc.render.resolution_x=width;sc.render.resolution_y=height;bpy.context.view_layer.update()
        pts=[world_to_camera_view(sc,cam,p) for p in world]
        assert all(0<p.x<1 and 0<p.y<1 and p.z>0 for p in pts)
        views.append({'size':[width,height],'fish_projected_bounds_pixels':[[min(p.x for p in pts)*width,min(p.y for p in pts)*height],[max(p.x for p in pts)*width,max(p.y for p in pts)*height]]})
    rows.append({'state':'Taut' if taut else 'Slack','fish_roots':6,'fish_meshes':len(fish),'maximum_nominal_envelope_radius_fraction':ratio,'views':views})
for rel,sha in meta['readonly_dependencies_sha256'].items():assert B.sha(B.R/rel)==sha,rel
result={'result':'PASS','camera_height_m':cam.location.z,'pitch_down_degrees':pitch,'vertical_fov_degrees':fov,'bunt_outward_m':B.to_u(root.location)[2],'states':rows,'limit':'Nominal interpolated elliptical bag envelope only; no physics/collision or native Unity acceptance.','readonly_dependencies_unchanged':True}
(O/'metrics/fixture-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('NET FIXTURE AUDIT PASS',json.dumps(result),flush=True)
