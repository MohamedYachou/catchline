"""NET-ART-1. Deterministic cord geometry in metres; no Assets/runtime writes.

Geometry inputs use Unity coordinates. Convert exactly once to Blender X,-Z,Y.
Run Windows Blender 5.2: -b -t 6 -P <this script> -- NetBunt|NetPanelSet
"""
import sys, math, json, hashlib
from pathlib import Path
sys.dont_write_bytecode=True
import bpy
from mathutils import Vector
R=Path(__file__).resolve().parents[3]
O=R/'Art/Models/NetKit'
sys.path.insert(0,str(R/'Art/Source'))
import build_crab_coast_props as H
G=H.Geometry
P={'M_NetGreenGrey':'#50766C','M_Rope':'#D1AF76',
   'M_SafetyOrange':'#E36A35','M_RailIvory':'#F3F0DC',
   'M_Steel':'#8FA6AC','M_Rubber':'#28343B'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def to_b(p):return (p[0],-p[2],p[1])
def to_u(p):return (p[0],p[2],-p[1])
def tube(g,pts,r,col,sides=3):g.tube(pts,[r]*len(pts),sides,col)
def empty(name,parent=None,location=(0,0,0)):
    o=bpy.data.objects.new(name,None);bpy.context.scene.collection.objects.link(o)
    o.parent=parent;o.location=to_b(location);o.empty_display_type='PLAIN_AXES';o.empty_display_size=.08
    return o
def init(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    H.PALETTE=P;H.MATERIALS={k:H.material(k,v,.76) for k,v in P.items()}
    root=empty(name);root['axes']='Metres. Blender X,Y,Z -> Unity X,Z,-Y.'
    return root
def mesh(g,name,parent,pivot=(0,0,0)):
    g.vertices=[to_b(Vector(p)-Vector(pivot)) for p in g.vertices]
    o=g.object(name,parent,bpy.context.scene.collection);o.location=to_b(pivot)
    used=sorted({p.material_index for p in o.data.polygons})
    mats=[o.data.materials[i] for i in used];inds=[used.index(p.material_index) for p in o.data.polygons]
    o.data.materials.clear()
    for m in mats:o.data.materials.append(m)
    for p,i in zip(o.data.polygons,inds):p.material_index=i
    return o
def barrel(g,centre,direction,length=.12,radius=.044,sides=8):
    """One sealed barrel, broad ivory centre band; shared GillNet float language."""
    t=Vector(direction).normalized();helper=Vector((0,1,0))
    if abs(t.dot(helper))>.9:helper=Vector((0,0,1))
    u=t.cross(helper).normalized();v=t.cross(u).normalized();c=Vector(centre)
    vs=[]
    for a,r in [(-.5,.68),(-.26,1),(-.11,1),(.11,1),(.26,1),(.5,.68)]:
        for k in range(sides):
            th=k*math.tau/sides;vs.append(c+t*(a*length)+radius*r*(u*math.cos(th)+v*math.sin(th)))
    fs=[tuple(reversed(range(sides)))];cols=['M_SafetyOrange']
    for j in range(5):
        for k in range(sides):
            fs.append((j*sides+k,j*sides+(k+1)%sides,(j+1)*sides+(k+1)%sides,(j+1)*sides+k))
            cols.append('M_RailIvory' if j==2 else 'M_SafetyOrange')
    fs.append(tuple(range(5*sides,6*sides)));cols.append('M_SafetyOrange')
    off=len(g.vertices);g.vertices.extend(tuple(p) for p in vs)
    g.faces.extend(tuple(i+off for i in f) for f in fs);g.colours.extend(cols)
def stretch(p):
    x,y,z=p;t=max(0,min(1,(z-.045)/.155));s=t*t*(3-2*t)
    return (x*(1-.28*s),y*(1-.22*s),z+.38*max(0,z-.045))
def bunt(root):
    g=G()
    # Seven contours carry two continuous bias families: real diamond holes.
    profile=[(0,.44,.29,0),(.10,.53,.36,-.05),(.23,.55,.38,-.075),
             (.37,.49,.35,-.105),(.51,.36,.28,-.12),(.63,.19,.15,-.14),(.70,.030,.025,-.16)]
    for direction in (-1,1):
        for i in range(16):
            pts=[]
            for k,(z,rx,ry,cy) in enumerate(profile):
                a=(i+direction*k)*math.tau/16
                pts.append((rx*math.cos(a),cy+ry*math.sin(a),z))
            tube(g,pts,.0057,'M_NetGreenGrey',3)
    # Slightly heavier selected seams soften the silhouette without hiding the catch.
    for i in range(4):
        a=(i+.5)*math.tau/4
        tube(g,[(rx*math.cos(a),cy+ry*math.sin(a),z) for z,rx,ry,cy in profile],.0075,'M_NetGreenGrey',3)
    rim=[(.44*math.cos(i*math.tau/24),.29*math.sin(i*math.tau/24),0) for i in range(25)]
    tube(g,rim,.012,'M_Rope',4)
    for i in range(6):
        a=(i+.5)*math.tau/6
        barrel(g,(.44*math.cos(a),.29*math.sin(a),0),(-.44*math.sin(a),.29*math.cos(a),0),.116,.042,6)
    # Bound cod end: compact closure, rather than an open hole at the back.
    for z,r in [(.675,.08),(.707,.034)]:
        tube(g,[(r*math.cos(i*math.tau/8),-.16+r*.7*math.sin(i*math.tau/8),z) for i in range(9)],.008,'M_Rope',3)
    tube(g,[(0,-.16,.705),(.022,-.165,.735),(.048,-.172,.726)],.008,'M_Rope',3)
    o=mesh(g,'Bunt',root)
    o.shape_key_add(name='Basis')
    o.shape_key_add(name='Slack')
    taut=o.shape_key_add(name='Taut')
    for a,b in zip(o.data.vertices,taut.data):b.co=to_b(stretch(to_u(a.co)))
    o['rest_state']='Slack=0 and Taut=0; explicit Slack channel duplicates rest. Drive only Taut 0..1.'
    root['pivot']='Mouth centre; mouth normal Unity -Z; bag extends Unity +Z.'
    fill=empty('Fill',root,(0,-.09,.31))
    fill['purpose']='Catch parent. Fits six 0.28..0.34m fish. Does not automatically follow blendshape.'
    return {'pivot_unity':[0,0,0],'mouth_normal_unity':[0,0,-1],
      'Fill':{'position_unity':[0,-.09,.31],'taut_position_unity':list(stretch((0,-.09,.31)))},
      'shape_keys':{'mesh':'Bunt','names':['Slack','Taut'],'slack':'Basis geometry',
        'drive':'Unity Bunt blendshape Taut from0 to100; Slack stays0. No skeleton or clips.',
        'function':'Rear narrows28%, vertical body narrows22%; depth beyond the fixed45mm mouth band lengthens38%.'}}
def panel_set(root):
    # Both contents have their own zero local pivot for independent instantiation.
    g=G()
    # Economical coarse grid: continuous paths have fewer caps than short cells.
    for i in range(13):
        x=-1.19+i*(2.38/12)
        tube(g,[(x,.0,-.49),(x,-.035,0),(x,.0,.49)],.0053,'M_NetGreenGrey',3)
    for j in range(7):
        z=-.49+j*.98/6
        tube(g,[(-1.19,-.035*math.sin(j*math.pi/6),z),(1.19,-.035*math.sin(j*math.pi/6),z)],.0053,'M_NetGreenGrey',3)
    tube(g,[(-1.19,0,.49),(1.19,0,.49)],.011,'M_Rope',4)
    tube(g,[(-1.19,0,-.49),(1.19,0,-.49)],.009,'M_Rubber',4)
    for x in (-1.12,-.56,0,.56,1.12):barrel(g,(x,.025,.49),(1,0,0),.115,.038,6)
    # Distinct lead weights on the opposite long edge, no separate floating spheres.
    for x in (-.95,-.48,0,.48,.95):
        g.ellipsoid((x,-.012,-.49),(.032,.018,.024),6,1,'M_Steel')
    panel=mesh(g,'NetPanel',root)
    panel['pivot']='Waterline centre. X2.4m, Z1m. Corks +Z, lead line -Z.'
    # A folded strip with real openings, not solid overlapping balls.
    g=G();n=9
    folds=[(-.30,.028,-.14),(.28,.055,-.18),(.16,.13,.03),
           (-.28,.075,.16),(-.11,.045,-.02),(.27,.16,.17),
           (.11,.10,-.05),(-.21,.035,-.16),(.03,.09,.07)]
    def section(i,s):
        c=Vector(folds[i]);before=Vector(folds[max(0,i-1)]);after=Vector(folds[min(8,i+1)])
        d=after-before;across=Vector((-d.z,0,d.x)).normalized()
        return c+across*(s*.105)+Vector((0,s*.018*math.sin(i*1.7),0))
    def hp(t,s):
        q=max(0,min(8,t*8));i=min(7,int(q));f=q-i
        return section(i,s).lerp(section(i+1,s),f)
    for s in (-1,-.5,0,.5,1):tube(g,[hp(i/(n-1),s) for i in range(n)],.0065,'M_NetGreenGrey',3)
    for i in range(n):tube(g,[hp(i/(n-1),s) for s in (-1,0,1)],.0065,'M_NetGreenGrey',3)
    tube(g,[hp(i/(n-1),1.06) for i in range(n)],.010,'M_Rope',3)
    tube(g,[hp(i/(n-1),-1.06) for i in range(n)],.008,'M_Rubber',3)
    for t in (.12,.5,.87):
        c=hp(t,1.06);nxt=hp(t+.01,1.06)
        barrel(g,c,Vector(nxt)-Vector(c),.105,.034,6)
    heap=mesh(g,'NetHeap',root)
    heap['pivot']='Waterline/base centre; separate from NetPanel, toggle one child.'
    return {'pivot_unity':[0,0,0],'children':['NetPanel','NetHeap'],
      'NetPanel':{'pivot_unity':[0,0,0],'cork_edge':'Unity +Z','lead_edge':'Unity -Z','nominal_span_m':[2.4,1]},
      'NetHeap':{'pivot_unity':[0,0,0],'use':'Toggle off NetPanel and on NetHeap for a missed cast; both exported visible.'}}
def snapshot():
    bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    return {'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),
      'bounds_blender':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],
      'dimensions_unity':[max(p[i] for p in pts)-min(p[i] for p in pts) for i in (0,2,1)],
      'parents':{o.name:o.parent.name if o.parent else None for o in bpy.context.scene.objects},
      'materials':sorted({o.data.materials[p.material_index].name for o in meshes for p in o.data.polygons}),
      'objects':{o.name:{'location_unity':list(to_u(o.location)),'scale':list(o.scale),
                         'triangles':sum(len(p.vertices)-2 for p in o.data.polygons) if o.type=='MESH' else 0} for o in bpy.context.scene.objects}}
def run(name):
    O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True)
    root=init(name);contract={'NetBunt':bunt,'NetPanelSet':panel_set}[name](root)
    row=snapshot();limit=2500 if name=='NetBunt' else 1600
    assert row['triangles']<limit,(name,row['triangles'])
    if name=='NetPanelSet':assert all(v['triangles']<800 for v in row['objects'].values())
    for m in list(bpy.data.materials):
        if m.users==0:bpy.data.materials.remove(m)
    bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'EMPTY','MESH'},
      axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',
      bake_space_transform=True,use_mesh_modifiers=False,mesh_smooth_type='FACE',use_triangles=False,
      add_leaf_bones=False,bake_anim=False,path_mode='AUTO',use_custom_props=True)
    row.update(name=name,contract=contract,limit=limit,palette_srgb=P,
               sha256={ext:sha(O/(name+'.'+ext)) for ext in ('blend','fbx')},status='built; exported geometry/visual audit pending')
    (O/'metrics'/(name+'.json')).write_text(json.dumps(row,indent=2)+'\n')
    print('NET BUILT',name,row['triangles'],row['dimensions_unity'],flush=True)
if __name__=='__main__':run(sys.argv[sys.argv.index('--')+1])
