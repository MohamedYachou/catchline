"""CAGE-ART-1, deterministic metre-scale assets. No Unity/Assets writes.
Blender Z-up; board operator/gauge edge +Y maps to Unity -Z. FBX Y-up. Run -- <name>.
"""
import sys, math, json, hashlib
from pathlib import Path
sys.dont_write_bytecode = True
import bpy
from mathutils import Vector
R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R/'Art/Source'))
import build_crab_coast_props as H
O = R/'Art/Models/Fishing/CageKit'
P = {'M_HullNavy':'#173F57','M_SeaTeal':'#168F9F','M_Steel':'#8FA6AC',
     'M_Rubber':'#28343B','M_Rope':'#D1AF76','M_RailIvory':'#F3F0DC',
     'M_DeckWood':'#C58B50','M_WoodHighlight':'#DFB77A','M_WoodRecess':'#8C5A36',
     'M_Brass':'#E6AD38','M_LegalRed':'#CF4232','M_SafetyOrange':'#E36A35',
     'M_EggOrange':'#FF9B24','M_BandIvory':'#F3DEA1'}
G = H.Geometry
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def init(name):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1
    H.PALETTE=P;H.MATERIALS={k:H.material(k,v,.73) for k,v in P.items()}
    for k in ('M_Steel','M_Brass'):
        sh=H.MATERIALS[k].node_tree.nodes.get('Principled BSDF');sh.inputs['Metallic'].default_value=.28;sh.inputs['Roughness'].default_value=.42
    for k in ('M_DeckWood','M_WoodHighlight'):
        H.MATERIALS[k].node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.48
    root=bpy.data.objects.new(name,None);sc.collection.objects.link(root)
    root['contract']='Metres; base centre; Blender Z-up -> Unity Y-up. Board gauge at Unity -Z working edge.'
    return root
def part(g,name,root,pivot=(0,0,0)):
    g.vertices=[tuple(Vector(v)-Vector(pivot)) for v in g.vertices]
    o=g.object(name,root,bpy.context.scene.collection);o.location=pivot
    used=sorted({p.material_index for p in o.data.polygons});mats=[o.data.materials[i] for i in used];indices=[used.index(p.material_index) for p in o.data.polygons]
    o.data.materials.clear()
    for m in mats:o.data.materials.append(m)
    for p,i in zip(o.data.polygons,indices):p.material_index=i
    return o
def beam(g,a,b,w,c,d=None):g.beam(a,b,w,d or w,c)
def tube(g,path,r,c,sides=4):g.tube(path,[r]*len(path),sides,c)
def polyline(g,pts,w,c):
    for a,b in zip(pts,pts[1:]):beam(g,a,b,w,c)
def arch(y):return .08+.255*math.sqrt(max(0,1-(y/.211)**2))
def crab_cage(root):
    g=G();g.rectangle_ring(.60,.45,.016,0,.024,.034,'M_HullNavy')
    # Four structural arched hoops; coarse longitudinal net with an actual hatch opening.
    angles=[i*math.pi/8 for i in range(9)]
    for x in (-.282,-.158,.158,.282):
        path=[(x,-.211,.017)]+[(x,-.211*math.cos(a),.08+.255*math.sin(a)) for a in angles]+[(x,.211,.017)]
        tube(g,path,.010,'M_HullNavy')
    for a in angles:
        y=-.211*math.cos(a);z=.08+.255*math.sin(a)
        spans=[(-.282,-.158),(.158,.282)] if abs(y)<.14 else [(-.282,.282)]
        for l,r in spans:beam(g,(l,y,z),(r,y,z),.006,'M_Steel')
    # Floor mesh is sparse and strong enough to see through the water.
    for x in (-.20,-.10,0,.10,.20):beam(g,(x,-.211,.018),(x,.211,.018),.006,'M_Steel')
    for y in (-.14,0,.14):beam(g,(-.282,y,.018),(.282,y,.018),.006,'M_Steel')
    for x in (-.282,.282):
        for y in (-.14,0,.14):
            spans=[(.022,.075),(.225,arch(y))] if x>0 and y==0 else [(.022,arch(y))]
            for lo,hi in spans:beam(g,(x,y,lo),(x,y,hi),.006,'M_Steel')
        for z in (.12,.22):
            w=.211*math.sqrt(1-((z-.08)/.255)**2)
            gap=.075*math.sqrt(max(0,1-((z-.15)/.075)**2)) if x>0 else 0
            spans=[(-w,-gap),(gap,w)] if gap>0 else [(-w,w)]
            for lo,hi in spans:beam(g,(x,lo,z),(x,hi,z),.006,'M_Steel')
    # One coarse inward funnel is a real open entrance, not a painted circle.
    for x,ry,rz in [(.284,.075,.075),(.193,.042,.042)]:
        path=[(x,ry*math.cos(i*math.tau/8),.15+rz*math.sin(i*math.tau/8)) for i in range(9)]
        tube(g,path,.005,'M_Rope')
    for i in range(4):
        a=i*math.tau/4;beam(g,(.284,.075*math.cos(a),.15+.075*math.sin(a)),(.193,.042*math.cos(a),.15+.042*math.sin(a)),.0045,'M_Steel')
    # Teal low-profile bait box and orange hatch latch.
    g.box((0,.075,.047),(.11,.07,.042),'M_SeaTeal')
    g.box((0,.039,.054),(.060,.005,.012),'M_RailIvory')
    for x in (-.22,.22):
        g.box((x,0,.008),(.065,.30,.016),'M_Rubber')
    body=part(g,'CreelFrame',root)
    lid=G();ys=[-.13,-.065,0,.065,.13]
    for x in (-.145,.145):tube(lid,[(x,y,arch(y)+.003) for y in ys],.008,'M_SeaTeal')
    for y in (-.13,.13):beam(lid,(-.145,y,arch(y)+.003),(.145,y,arch(y)+.003),.016,'M_SeaTeal')
    tube(lid,[(0,y,arch(y)+.003) for y in ys],.0045,'M_Steel')
    for y in (-.065,0,.065):beam(lid,(-.145,y,arch(y)+.003),(.145,y,arch(y)+.003),.005,'M_Steel')
    lid.box((0,-.137,arch(-.13)+.007),(.040,.026,.018),'M_SafetyOrange')
    for x in (-.105,.105):
        tube(lid,[(x-.018,.13,arch(.13)+.003),(x+.018,.13,arch(.13)+.003)],.012,'M_Rope',6)
    hinge=(0,.13,arch(.13)+.003);o=part(lid,'Lid',root,hinge)
    o['animation']='Local X hinge; negative angle opens upward; recommended 0 to -90 degrees'
    b=G();pivot=(0,.219,.355)
    for x in (-.275,.275):tube(b,[(x,.219,.085),(x*.45,.219,.26),pivot],.006,'M_Rope')
    b.torus(pivot,.020,.005,'M_Steel');o=part(b,'Bridle',root,pivot)
    o['attachment']='Rope tie at this origin; ring in local XZ / Unity XY plane'
    return {'Lid':{'pivot':hinge,'axis':[1,0,0],'open_degrees':-90},'Bridle':{'pivot':pivot,'attachment':True}}
def pot_hauler(root):
    g=G()
    # Base saddle and two hooked cheeks fit a horizontal 50 mm rail.
    g.box((0,0,.016),(.18,.13,.032),'M_HullNavy')
    for x in (-.062,.062):
        for y in (-.046,.046):
            g.box((x,y,.064),(.026,.028,.064),'M_Steel')
            g.box((x,y*.66,.065),(.026,.004,.044),'M_Rubber')
        g.box((x,0,.110),(.026,.12,.028),'M_Steel')
        tube(g,[(x,-.078,.065),(x,-.049,.065)],.008,'M_Brass',6)
        g.box((x,-.080,.065),(.045,.012,.016),'M_Brass')
    for x in (-.075,.075):
        beam(g,(x,.015,.119),(x,0,.247),.032,'M_HullNavy',.043)
        tube(g,[(x-.012,0,.247),(x+.012,0,.247)],.026,'M_Steel',8)
    g.box((.100,.012,.168),(.055,.078,.085),'M_SeaTeal')
    g.box((.130,-.017,.187),(.007,.022,.028),'M_SafetyOrange')
    tube(g,[(-.106,0,.247),(.135,0,.247)],.015,'M_Steel',8)
    part(g,'HaulerMount',root)
    # Twelve-sided grooved tyre, axle along X. Profile radii reach exactly .15m.
    w=G();v=[];f=[]
    profile=[(-.041,.118),(-.037,.145),(-.029,.15),(-.017,.137),(0,.128),(.017,.137),(.029,.15),(.037,.145),(.041,.118)]
    n=16
    for x,r in profile:
        v += [(x,r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n)) for i in range(n)]
    for j in range(len(profile)-1):
        f += [(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for i in range(n)]
    f += [((len(profile)-1)*n+i,(len(profile)-1)*n+(i+1)%n,(i+1)%n,i) for i in range(n)]
    w.add(v,f,'M_Rubber')
    for x in (-.038,.038):
        # Gold spoke plates and bearing hubs, exposed between both side cheeks.
        for i in range(5):
            a=i*math.tau/5;beam(w,(x,0,0),(x,.12*math.cos(a),.12*math.sin(a)),.018,'M_Brass',.014)
    tube(w,[(-.045,0,0),(.045,0,0)],.032,'M_Brass',10)
    # Geometry above was local to axle; move into source world before part subtracts pivot.
    pivot=(0,0,.247);w.vertices=[tuple(Vector(v)+Vector(pivot)) for v in w.vertices]
    o=part(w,'Sheave',root,pivot);o['animation']='Spin local X; tyre outer diameter exactly 0.300m'
    return {'Sheave':{'pivot':pivot,'axis':[1,0,0],'diameter_metres':.3},'rail_saddle':{'rail_diameter_metres':.05,'channel_centre_source':[0,0,.065],'clear_width_metres':.05672,'clear_height_metres':.064}}
def sorting_board(root):
    g=G()
    # Broad tightly fitted wet planks, with a bevel highlight rather than noisy grain.
    for i in range(5):
        y=-.12+i*.06
        beam(g,(-.31,y,.025),(.31,y,.025),.058,'M_DeckWood' if i%2==0 else 'M_WoodHighlight',.032)
    g.box((0,0,.011),(.62,.30,.022),'M_WoodRecess')
    # Subtle raised back lip keeps a flicked crab on the working surface.
    beam(g,(-.31,.137,.057),(.31,.137,.057),.026,'M_DeckWood',.064)
    for x in (-.245,.245):
        g.box((x,0,.006),(.036,.30,.012),'M_HullNavy')
        for y in (-.11,.11):tube(g,[(x,y,.04),(x,y,.043)],.005,'M_Steel',6)
    # Gauge zero is the left end at x=-.26, ticks extend 0.52m to the right.
    g.box((0,-.121,.047),(.54,.036,.008),'M_Brass')
    for i in range(27):
        x=-.26+i*.02;length=.024 if i%5==0 else (.018 if i%2==0 else .011)
        g.box((x,-.137+length*.5,.052),(.0025,length,.002),'M_Rubber')
    # Physical zero stop, pale small end cap so both endpoints survive phone downscale.
    g.box((-.26,-.121,.060),(.009,.037,.022),'M_RailIvory')
    for x in (-.25,.25):g.box((x,.137,.067),(.025,.029,.040),'M_HullNavy')
    g.vertices=[(x,-y,z) for x,y,z in g.vertices]
    part(g,'BoardAndGauge',root)
    m=G();pivot=(-.26+.115,-.121,.052)
    # Red U-notch wraps the near gauge edge, leaving its zero and ticks visible.
    m.box((pivot[0],-.143,.060),(.016,.014,.016),'M_LegalRed')
    for x in (pivot[0]-.007,pivot[0]+.007):m.box((x,-.122,.056),(.003,.034,.008),'M_LegalRed')
    m.box((pivot[0],-.105,.056),(.017,.004,.008),'M_LegalRed')
    m.vertices=[(x,-y,z) for x,y,z in m.vertices];pivot=(pivot[0],-pivot[1],pivot[2])
    o=part(m,'LegalMark',root,pivot);o['animation']='Slide local X; desired x = -0.26 + legal length in metres. Initial 0.115m.'
    return {'LegalMark':{'pivot':pivot,'slide_axis':[1,0,0],'zero_x':-.26,'initial_legal_length_metres':.115},'gauge':{'zero_x':-.26,'max_x':.26,'minor_tick_metres':.02}}
def crab_berried(root):
    src=R/'Art/Models/Props/Crab.blend';before=sha(src)
    with bpy.data.libraries.load(str(src),link=False) as (a,b):b.objects=['CrabBody']
    o=b.objects[0];bpy.context.scene.collection.objects.link(o);o.parent=root
    o.name='CrabBody';o['preserved']='Exact existing plain-crab mesh, scale and pivot; no vertex edits'
    for i,m in enumerate(o.data.materials):o.data.materials[i]=H.MATERIALS[m.name.split('.')[0]]
    g=G()
    # Eggs sit beneath the rear abdominal flap and project at its sides for phone recognition.
    g.ellipsoid((0,.063,.027),(.055,.047,.021),10,3,'M_EggOrange')
    for x,y,z,r in [(-.042,.078,.025,.018),(0,.092,.024,.018),(.042,.078,.025,.018),(-.023,.100,.024,.016),(.023,.100,.024,.016),(-.051,.052,.023,.015),(.051,.052,.023,.015)]:
        g.ico((x,y,z),r,'M_EggOrange')
    # The flap is a small dark-gold wedge above the underside clutch, not a second shell.
    g.extrude_polygon([(-.027,.055),(.027,.055),(.022,.088),(0,.100),(-.022,.088)],.040,.046,'M_SafetyOrange')
    part(g,'EggMass',root)
    assert sha(src)==before
    return {'canonical':{'path':src.relative_to(R).as_posix(),'sha256':before,'object':'CrabBody','geometry_sha256':mesh_hash(o)},'eggs':'Bright orange clutch under rear tail flap; existing shell/legs/claws untouched'}
def mesh_hash(o):
    row={'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons]}
    return hashlib.sha256(json.dumps(row,separators=(',',':')).encode()).hexdigest()
BUILD={'CrabCage':crab_cage,'PotHauler':pot_hauler,'SortingBoard':sorting_board,'CrabBerried':crab_berried}
def snapshot():
    bpy.context.view_layer.update();objs=list(bpy.context.scene.objects);meshes=[o for o in objs if o.type=='MESH'];pts=[o.matrix_world@v.co for o in meshes for v in o.data.vertices]
    return {'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes),
      'bounds':[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],
      'dimensions_blender':[max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)],
      'parents':{o.name:o.parent.name if o.parent else None for o in objs},
      'materials':sorted({o.data.materials[p.material_index].name for o in meshes for p in o.data.polygons}),
      'objects':{o.name:{'location':list(o.location),'rotation':list(o.rotation_euler),'scale':list(o.scale),'tris':sum(len(p.vertices)-2 for p in o.data.polygons) if o.type=='MESH' else 0} for o in objs}}
def build(name):
    O.mkdir(parents=True,exist_ok=True);(O/'metrics').mkdir(exist_ok=True)
    root=init(name);contract=BUILD[name](root);bpy.context.view_layer.update()
    row=snapshot();assert row['triangles']<1500,(name,row['triangles'])
    # Remove unused data; embedded shared palette only, no loose material folders.
    for m in list(bpy.data.materials):
        if m.users==0:bpy.data.materials.remove(m)
    bpy.ops.wm.save_as_mainfile(filepath=str(O/(name+'.blend')))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(O/(name+'.fbx')),use_selection=True,object_types={'EMPTY','MESH'},
        axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=True,use_mesh_modifiers=True,mesh_smooth_type='FACE',use_triangles=False,
        add_leaf_bones=False,bake_anim=False,path_mode='AUTO',use_custom_props=True)
    row.update(name=name,contract=contract,axes='Blender (X,Y,Z) maps to Unity (X,Z,-Y); board operator/gauge edge source +Y / Unity -Z',
        sha256={ext:sha(O/(name+'.'+ext)) for ext in ('blend','fbx')},status='built; actualFBX/visual review pending')
    (O/'metrics'/(name+'.json')).write_text(json.dumps(row,indent=2)+'\n');print('CAGE BUILD',name,row['triangles'],flush=True)
if __name__=='__main__':build(sys.argv[sys.argv.index('--')+1])
