"""ART108: additive station kit. Run in isolated Blender background process.

No existing mesh or metadata is written. Source Z-up, front -Y; exports Y-up.
Station positions are in the runtime Boat transform, NOT the FBX child root.
"""
import bpy, math, json, hashlib, shutil, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'Art/Models/StationsV1'
GAME=ROOT/'Assets/Art/Models/StationsV1'
for p in [OUT,GAME]: p.mkdir(parents=True,exist_ok=True)
PALETTE={'M_DeckWood':'C58B50','M_WoodHighlight':'DFB77A','M_WoodRecess':'8C5A36',
 'M_HullNavy':'173F57','M_RailIvory':'F3F0DC','M_SeaTeal':'168F9F',
 'M_Steel':'8FA6AC','M_Rubber':'28343B','M_Rope':'D1AF76',
 'M_SafetyOrange':'E36A35','M_FishSilver':'BAC9C6','M_OilskinYellow':'E6AD38','M_Skin':'B9784B'}
def material(name):
    m=bpy.data.materials.get(name)
    if m: return m
    m=bpy.data.materials.new(name); m.use_nodes=True
    rgb=[int(PALETTE[name][i:i+2],16)/255 for i in (0,2,4)]
    rgb=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb]
    bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Roughness'].default_value=.72
    m.diffuse_color=(*rgb,1)
    return m
def box(name,p,size,mat,bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p)
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material(mat))
    if bevel:
        mod=o.modifiers.new('Broad bevel','BEVEL');mod.width=bevel;mod.segments=2
        bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=o.modifiers.new('Face normals','WEIGHTED_NORMAL')
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return o
def cyl(name,p,r,depth,mat,vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=p)
    o=bpy.context.object;o.name=name;o.data.materials.append(material(mat));return o
def beam(name,a,b,r,mat):
    a,b=Vector(a),Vector(b);o=cyl(name,(a+b)/2,r,(b-a).length,mat)
    o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o
def torus(name,p,major,minor,mat):
    bpy.ops.mesh.primitive_torus_add(major_segments=16,minor_segments=6,location=p,major_radius=major,minor_radius=minor)
    o=bpy.context.object;o.name=name;o.data.materials.append(material(mat));return o
def fish(p,i):
    x,y,z=p
    bpy.ops.mesh.primitive_uv_sphere_add(segments=10,ring_count=6,location=p)
    o=bpy.context.object;o.name=f'FillFish_{i:02}';o.scale=(.035,.12,.025)
    o.rotation_euler.z=(i%3-1)*.22;o.data.materials.append(material('M_FishSilver'))
    o=box(f'FishTail_{i:02}',(x,y-.12,z),(.065,.05,.015),'M_SeaTeal',.008)
    cyl(f'FishEye_{i:02}',(x+.017,y+.075,z+.022),.008,.005,'M_Rubber',8)
def basket(large=False,fill=0):
    w,d=(.56,.42) if large else (.40,.30);h=.28 if large else .23
    box('Bottom',(0,0,.025),(w,d,.05),'M_WoodRecess',.012)
    for k in range(3):
        z=.075+k*(h-.06)/3
        for sign in (-1,1):
            box('LongSlat',(0,sign*(d/2-.018),z),(w,.035,.045),'M_DeckWood',.009)
            box('EndSlat',(sign*(w/2-.018),0,z),(.035,d,.045),'M_DeckWood',.009)
    for x in (-w/2+.022,w/2-.022):
        for y in (-d/2+.022,d/2-.022):
            box('Corner',(x,y,h/2),(.038,.038,h),'M_WoodHighlight',.009)
    for sign in (-1,1):
        box('IvoryRim',(0,sign*(d/2-.01),h),(w+.02,.035,.035),'M_RailIvory',.011)
        beam('RopeHandle',(sign*w/2,-.065,h-.01),(sign*w/2,.065,h-.01),.014,'M_Rope')
    for i in range((0,2,4,6)[fill]):
        level=(h-.05,h-.015,h+.025)[fill-1]
        fish(((i%3-1)*w*.23,(i//3-.5)*d*.35,level+(.035 if i>=3 else 0)),i)
def board():
    box('ClampedBoard',(0,0,.045),(.58,.30,.09),'M_DeckWood',.025)
    box('BoardInset',(0,0,.097),(.47,.23,.015),'M_WoodHighlight',.012)
    for x in (-.20,.20):
        box('RailClamp',(x,0,-.035),(.05,.12,.15),'M_HullNavy',.01)
        cyl('ClampCap',(x,-.045,-.10),.028,.025,'M_Steel')
    box('KnifeBlade',(.12,.03,.115),(.15,.025,.009),'M_Steel',.003)
    box('KnifeGrip',(.23,.03,.119),(.08,.035,.025),'M_HullNavy',.006)
def table(large=False):
    w,d=(1.05,.55) if large else (.72,.42)
    for x in (-w/2+.07,w/2-.07):
        for y in (-d/2+.06,d/2-.06):
            box('Leg',(x,y,.25),(.07,.07,.50),'M_HullNavy',.012)
            box('Foot',(x,y,.025),(.10,.10,.05),'M_Rubber',.012)
    box('LowerShelf',(0,0,.15),(w-.07,d-.04,.05),'M_DeckWood',.016)
    box('TimberApron',(0,0,.50),(w,d,.10),'M_DeckWood',.025)
    box('IvoryWorktop',(0,0,.56),(w+.03,d+.03,.035),'M_RailIvory',.014)
    box('TealSortTray',(-w*.18,0,.585),(w*.43,d*.74,.025),'M_SeaTeal',.015)
    box('KeepTray',(w*.27,0,.585),(w*.31,d*.74,.025),'M_WoodHighlight',.015)
    box('BackLip',(0,d/2,.61),(w,.035,.10),'M_HullNavy',.01)
def bait():
    box('Bin',(0,0,.19),(.46,.36,.38),'M_HullNavy',.035)
    box('Inset',(0,0,.39),(.39,.29,.03),'M_Rubber',.012)
    box('LidBack',(0,.10,.425),(.48,.16,.04),'M_RailIvory',.012)
    box('TealBand',(0,-.186,.21),(.27,.015,.09),'M_SeaTeal',.006)
    for x in (-.24,.24):box('Handle',(x,0,.28),(.03,.14,.04),'M_Rope',.008)
def nav(height=.65):
    cyl('Foot',(0,0,.035),.15,.07,'M_HullNavy')
    cyl('Post',(0,0,height/2),.035,max(.03,height-.05),'M_Steel')
    box('ChartDesk',(0,0,height),(.38,.24,.045),'M_DeckWood',.022)
    box('Chart',(0,0,height+.03),(.29,.17,.012),'M_RailIvory',.005)
    for x in (-.06,.06):
        o=cyl('BinocularTube',(x,-.04,height+.08),.039,.15,'M_HullNavy');o.rotation_euler.x=math.pi/2
    beam('BinocularBridge',(-.06,-.04,height+.08),(.06,-.04,height+.08),.013,'M_Steel')
def seat():
    for x in (-.19,.19):box('SeatLeg',(x,0,.17),(.055,.18,.34),'M_HullNavy')
    box('Seat',(0,0,.35),(.52,.29,.07),'M_DeckWood',.025)
    box('Cushion',(0,0,.402),(.44,.25,.035),'M_HullNavy',.016)
def lantern():
    cyl('Base',(0,0,.025),.105,.05,'M_HullNavy')
    cyl('WarmPane',(0,0,.16),.075,.22,'M_OilskinYellow')
    for x in (-.065,.065):
        for y in (-.065,.065):beam('Cage',(x,y,.05),(x,y,.28),.011,'M_HullNavy')
    cyl('Cap',(0,0,.29),.10,.045,'M_HullNavy')
    o=torus('Handle',(0,0,.36),.055,.009,'M_Steel');o.rotation_euler.x=math.pi/2
def hatch():
    for y in (-.43,.43):box('HatchEdge',(0,y,.018),(.77,.035,.036),'M_Steel',.009)
    for x in (-.37,.37):box('HatchEdge',(x,0,.018),(.035,.86,.036),'M_Steel',.009)
def generator():
    box('RubberFeet',(0,0,.03),(.65,.42,.06),'M_Rubber')
    box('NavyCase',(0,0,.27),(.62,.40,.48),'M_HullNavy',.045)
    box('IvoryFace',(0,-.209,.28),(.51,.025,.33),'M_RailIvory')
    for x in (-.15,-.05,.05,.15):box('Vent',(x,-.226,.30),(.025,.015,.18),'M_Rubber',.005)
    box('TopHandle',(0,0,.54),(.26,.075,.05),'M_Steel')
def mast():
    cyl('DeckFoot',(0,0,.035),.12,.07,'M_HullNavy')
    cyl('Mast',(0,0,.72),.025,1.40,'M_Steel')
    box('LightBody',(0,-.04,1.43),(.28,.12,.15),'M_HullNavy')
    box('LightFace',(0,-.108,1.42),(.22,.015,.095),'M_RailIvory',.008)
def hauler():
    box('Foot',(0,0,.04),(.40,.34,.08),'M_HullNavy')
    box('Mount',(0,0,.27),(.18,.20,.46),'M_Steel')
    o=cyl('RubberWheel',(0,0,.48),.15,.17,'M_Rubber',16);o.rotation_euler.y=math.pi/2
    o=cyl('IvoryHub',(.095,0,.48),.065,.02,'M_RailIvory');o.rotation_euler.y=math.pi/2
def ell(name,p,size,mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=p)
    o=bpy.context.object;o.name=name;o.scale=size;o.data.materials.append(material(mat))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def jig():
    box('RailClamp',(0,0,.07),(.20,.20,.14),'M_HullNavy')
    beam('JigRodLower',(0,0,.10),(.04,-.14,.75),.024,'M_DeckWood')
    beam('JigRodUpper',(.04,-.14,.75),(.10,-.45,1.15),.014,'M_HullNavy')
    beam('JigLine',(.10,-.45,1.15),(.10,-.45,.02),.005,'M_Rope')
    ell('SquidJig',(.10,-.45,.035),(.02,.025,.035),'M_SafetyOrange')
    o=cyl('JigReel',(.055,-.02,.25),.07,.065,'M_Steel');o.rotation_euler.y=math.pi/2
    beam('LampArm',(-.10,0,.12),(-.22,0,.38),.018,'M_Steel')
    cyl('LampShade',(-.22,0,.40),.075,.06,'M_HullNavy')
    cyl('LampGlass',(-.22,0,.34),.05,.08,'M_OilskinYellow')
def spare():
    cyl('Spool',(0,0,.04),.12,.08,'M_DeckWood')
    for z in (.01,.075):cyl('SpoolFlange',(0,0,z),.15,.025,'M_WoodHighlight')
    for z in (.027,.047,.067):torus('LineWrap',(0,0,z),.12,.009,'M_HullNavy')
    # Large legible hook silhouette, not hundreds of microscopic line turns.
    beam('RigSwivel',(.13,0,.025),(.23,0,.025),.009,'M_Steel')
    torus('HookCurve',(.25,.035,.025),.032,.007,'M_Steel')
def oil():
    box('Can',(0,0,.14),(.23,.15,.28),'M_RailIvory',.025)
    box('NavyBase',(0,0,.025),(.235,.155,.05),'M_HullNavy',.012)
    cyl('Cap',(-.05,0,.29),.035,.04,'M_HullNavy')
    beam('LongSpout',(.08,0,.25),(.22,0,.40),.017,'M_DeckWood')
    beam('TopHandle',(-.07,0,.31),(.07,0,.31),.013,'M_Steel')
def cutting():
    box('CuttingBoard',(0,0,.025),(.46,.27,.05),'M_WoodHighlight',.018)
    box('Handle',(.26,0,.025),(.12,.10,.05),'M_DeckWood',.018)
def processing():
    table(True)
    for x in (-.26,.26):
        box('CuttingBoard',(x,0,.602),(.40,.28,.035),'M_WoodHighlight',.012)
        box('KnifeBlade',(x+.02,.035,.625),(.19,.025,.009),'M_Steel',.003)
        box('KnifeGrip',(x+.15,.035,.635),(.09,.035,.025),'M_HullNavy',.007)
def jelly():
    for i,(x,y) in enumerate([(-.18,-.10),(.16,0),(0,.21)]):
        ell('JellyBell',(x,y,.24),(.18,.16,.12),'M_RailIvory')
        torus('BellRim',(x,y,.20),.15,.016,'M_SeaTeal')
        for j in range(4):
            xx=x+(j-1.5)*.065
            beam('Tentacle',(xx,y,.18),(xx+.025*(1 if j%2 else -1),y-.025,.025),.012,'M_SeaTeal')
def seal():
    ell('Head',(0,0,.14),(.25,.27,.23),'M_Steel')
    ell('Muzzle',(0,-.23,.13),(.15,.11,.10),'M_FishSilver')
    ell('Nose',(0,-.326,.16),(.05,.025,.03),'M_Rubber')
    for sign in (-1,1):
        ell('Eye',(sign*.12,-.21,.24),(.018,.016,.018),'M_Rubber')
        for j in range(2):beam('Whisker',(sign*.11,-.29,.13-j*.025),(sign*.25,-.31,.14-j*.04),.004,'M_RailIvory')
def fin():
    ell('SurfaceBack',(0,0,.025),(.22,.34,.07),'M_Steel')
    verts=[(-.035,-.22,0),(-.035,.18,0),(-.025,.04,.46),(-.025,-.03,.31),(.035,-.22,0),(.035,.18,0),(.025,.04,.46),(.025,-.03,.31)]
    mesh=bpy.data.meshes.new('DolphinFin');mesh.from_pydata(verts,[],[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]);mesh.update()
    o=bpy.data.objects.new('DolphinFin',mesh);bpy.context.scene.collection.objects.link(o);mesh.materials.append(material('M_Steel'))
def launch():
    rings=[(-1.45,.08),(-1.18,.43),(-.65,.58),(.75,.58),(1.25,.48)]
    vs=[]
    for y,w in rings:vs.extend([(-w,y,.12),(w,y,.12),(w*.73,y,-.25),(-w*.73,y,-.25)])
    fs=[]
    for j in range(len(rings)-1):
        for k in range(4):a=j*4+k;b=j*4+(k+1)%4;fs.append((a,b,b+4,a+4))
    fs.extend([(3,2,1,0),(16,17,18,19)])
    me=bpy.data.meshes.new('InspectorHull');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new('InspectorHull',me);bpy.context.scene.collection.objects.link(o);me.materials.append(material('M_HullNavy'))
    box('WorkingDeck',(0,0,.14),(.92,2.14,.06),'M_DeckWood',.08)
    for sign in (-1,1):beam('IvoryRail',(sign*.52,-.9,.29),(sign*.52,1,.29),.035,'M_RailIvory')
    box('SmallConsole',(0,.42,.44),(.50,.40,.54),'M_RailIvory',.05)
    box('Windshield',(0,.28,.81),(.60,.055,.27),'M_HullNavy',.025)
    beam('Mast',(0,.61,.72),(0,.61,1.20),.023,'M_Steel')
    cyl('AmberBeacon',(0,.61,1.23),.06,.08,'M_OilskinYellow')
    box('Outboard',(0,1.37,.12),(.32,.28,.50),'M_HullNavy',.055)
def offal():
    for i in range(7):
        a=i*2.4;r=.05+.02*(i%3)
        ell('CoarseOffcut',(r*math.cos(a),r*math.sin(a),.025+(i%2)*.03),(.08,.045,.025),'M_Skin' if i%2 else 'M_FishSilver')
def eel():
    points=[(-.32,.05,.045),(-.18,-.12,.05),(0,-.13,.05),(.17,0,.05),(.13,.16,.05),(-.02,.18,.05),(-.10,.10,.05)]
    cu=bpy.data.curves.new('CurvedEelBody','CURVE');cu.dimensions='3D';cu.resolution_u=6;cu.bevel_depth=.039;cu.bevel_resolution=2;cu.use_fill_caps=True
    sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for i,(p,co) in enumerate(zip(sp.bezier_points,points)):
        p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO';p.radius=max(.12,1-i*.13)
    ob=bpy.data.objects.new('EelBody',cu);bpy.context.scene.collection.objects.link(ob);cu.materials.append(material('M_HullNavy'))
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH')
    ell('EelHead',(-.32,.05,.055),(.08,.055,.05),'M_Steel')
    for sign in (-1,1):ell('Eye',(-.36,.05+sign*.038,.079),(.008,.008,.008),'M_Rubber')
def gull():
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'Assets/Art/Models/Harbour/Seagull.fbx'))
    # Rigid wing pivots are preserved; source gull itself is never overwritten.
    for o in bpy.context.scene.objects:
        if 'Wing' in o.name:
            o.rotation_euler.y=math.radians(80 if o.name.endswith('_L') else -80)
            o.scale.z=2.0
        if o.name=='SeagullBody':
            # Pull the perched feet into the belly on this derivative pose only.
            for v in o.data.vertices:
                if v.co.y<.10:v.co.y=.12+(v.co.y*.25)
def flying():
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'Art/Models/Fish043/FlyingFish/FlyingFish.fbx'))
KIT={'SortBoardRail':board,'SortTableSmall':table,'SortTableLarge':lambda:table(True),
 'BaitBin':bait,'NavigatorPost':nav,'NavigatorHelmBracket':lambda:nav(.08),'NavigatorSeat':seat,'Lantern':lantern,'HatchRing':hatch,
 'GeneratorBox':generator,'DeckLightMast':mast,'LineHauler':hauler,
 'JigRig':jig,'SpareRig':spare,'LanternOilCan':oil,'CuttingBoard':cutting,
 'JellyfishClump':jelly,'SealHead':seal,'DolphinFin':fin,'InspectorLaunch':launch,
 'OffalPile':offal,'TableEel':eel,'GullSwoop':gull,'ProcessingTableTwoPlace':processing,'FlyingFishEvent':flying}
for large in (False,True):
    for state in range(4):KIT[f'Basket{"Large" if large else "Small"}_{state}']=lambda l=large,s=state:basket(l,s)
def bounds(objs):
    pts=[o.matrix_world@Vector(v) for o in objs if o.type=='MESH' for v in o.bound_box]
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
def tris(objs):return sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objs if o.type=='MESH')
def export(name):
    bpy.ops.wm.read_factory_settings(use_empty=True);KIT[name]()
    root=bpy.data.objects.new('Art108_'+name,None);bpy.context.scene.collection.objects.link(root)
    for o in list(bpy.context.scene.objects):
        if o!=root and o.parent is None:o.parent=root
    bpy.context.view_layer.update();objects=list(bpy.context.scene.objects)
    record={'id':name,'runtimeModelId':'Art108_'+name,'runtimeFile':f'Assets/Art/Models/StationsV1/Art108_{name}.fbx','boundsSource':bounds(objects),'triangles':tris(objects),'pivot':[0,0,0],'front':'-Y source / -Z Unity','units':'metres'}
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/f'{name}.blend'))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(OUT/f'{name}.fbx'),use_selection=True,object_types={'EMPTY','MESH'},
       axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,
       apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,add_leaf_bones=False,use_triangles=True)
    shutil.copyfile(OUT/f'{name}.fbx',GAME/f'Art108_{name}.fbx')
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(GAME/f'Art108_{name}.fbx'))
    obs=list(bpy.context.scene.objects);bb=bounds(obs)
    err=max(abs(record['boundsSource'][j][i]-bb[j][i]) for j in range(2) for i in range(3))
    assert err<.0001,(name,err)
    assert record['triangles']==tris(obs),(name,record['triangles'],tris(obs))
    record['roundTripMaxError']=err
    record['exportSha256']=hashlib.sha256((GAME/f'Art108_{name}.fbx').read_bytes()).hexdigest()
    return record
if __name__=='__main__':
    names=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else list(KIT)
    old=json.loads((OUT/'kit-manifest.json').read_text())['assets'] if (OUT/'kit-manifest.json').exists() else []
    records=[r for r in old if r['id'] not in names]+[export(name) for name in names]
    (OUT/'kit-manifest.json').write_text(json.dumps({'schema':1,'assets':records},indent=2))
    print('ART108 KIT ROUNDTRIP PASSED',len(records),'assets')
