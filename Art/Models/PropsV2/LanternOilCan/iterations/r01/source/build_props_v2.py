"""A5/A6 PropsV2. Blender 5.2, -- --name JigRig [--revision r01].
New output paths only. StationsV1 and Art108 remain read-only style/provenance
references. Existing A6 meshes are deliberately reused, with provenance hashes.
Source metres, Z up, -Y front; FBX -Z/Y. No Unity/code/scene writes.
"""
import argparse, bpy, math, json, hashlib, shutil, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
NAMES=['JigRig','SpareRig','LanternOilCan','DeckLightPool','JellyfishClump',
       'FlyingFishEvent','GullSwoop','SealHead','DolphinFin','InspectorLaunch',
       'RivalBoat','SquallOverlay','OffalPile','TableEel']
p=argparse.ArgumentParser();p.add_argument('--name',choices=NAMES,required=True)
p.add_argument('--revision',default='r01');p.add_argument('--render',choices=['all','none'],default='all')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);NAME=a.name
OUT=ROOT/'Art/Models/PropsV2'/NAME;GAME=ROOT/'Assets/Art/Models/PropsV2';PRE=OUT/'iterations'/a.revision
for d in (OUT,GAME,PRE):d.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
PALETTE={'M_DeckWood':'C58B50','M_WoodHighlight':'DFB77A','M_WoodRecess':'8C5A36',
 'M_HullNavy':'173F57','M_RailIvory':'F3F0DC','M_SeaTeal':'168F9F',
 'M_Steel':'8FA6AC','M_Rubber':'28343B','M_Rope':'D1AF76',
 'M_SafetyOrange':'E36A35','M_FishSilver':'BAC9C6','M_OilskinYellow':'E6AD38','M_Skin':'B9784B'}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mat(name):
    m=bpy.data.materials.get(name)
    if m:return m
    m=bpy.data.materials.new(name);m.use_nodes=True
    rgb=[int(PALETTE[name][i:i+2],16)/255 for i in (0,2,4)]
    rgb=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*rgb,1)
    b.inputs['Roughness'].default_value=.72;m.diffuse_color=(*rgb,1)
    return m
def box(name,c,d,colour,bevel=.01):
    bpy.ops.mesh.primitive_cube_add(size=1,location=c);o=bpy.context.object;o.name=name;o.dimensions=d
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat(colour))
    if bevel:
        m=o.modifiers.new('Broad bevel','BEVEL');m.width=bevel;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
        m=o.modifiers.new('Weighted corner normals','WEIGHTED_NORMAL');bpy.ops.object.modifier_apply(modifier=m.name)
    return o
def cone(name,c,r1,r2,h,colour,n=12):
    bpy.ops.mesh.primitive_cone_add(vertices=n,radius1=r1,radius2=r2,depth=h,location=c)
    o=bpy.context.object;o.name=name;o.data.materials.append(mat(colour));return o
def cyl(name,c,r,h,colour,n=12):return cone(name,c,r,r,h,colour,n)
def beam(name,x,y,r,colour,r2=None,n=12):
    x,y=Vector(x),Vector(y);o=cone(name,(x+y)/2,r,r if r2 is None else r2,(y-x).length,colour,n)
    o.rotation_euler=(y-x).to_track_quat('Z','Y').to_euler();return o
def ell(name,c,r,colour):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=c)
    o=bpy.context.object;o.name=name;o.scale=r;o.data.materials.append(mat(colour))
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
def tube(name,points,r,colour,n=6):
    # Continuous, low-sided tube with actual open C/J silhouettes where requested.
    pts=[Vector(v) for v in points];vs=[]
    for j,c in enumerate(pts):
        t=(pts[min(j+1,len(pts)-1)]-pts[max(j-1,0)]).normalized()
        u=t.cross(Vector((0,0,1)))
        if u.length<.1:u=t.cross(Vector((0,1,0)))
        u.normalize();v=t.cross(u).normalized()
        vs.extend(c+r*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n)) for i in range(n))
    fs=[tuple(reversed(range(n)))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(pts)-1) for i in range(n)]
    fs.append(tuple(range((len(pts)-1)*n,len(pts)*n)));return mesh(name,vs,fs,colour)
def mesh(name,vs,fs,colour):
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    o=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(o);me.materials.append(mat(colour));return o
def ring(name,c,r,minor,colour,n=24):
    return tube(name,[(c[0]+r*math.cos(i*math.tau/n),c[1]+r*math.sin(i*math.tau/n),c[2]) for i in range(n+1)],minor,colour)
def jig():
    # Clamp floor pivot. Deck/rail shown in context renders only, never exported.
    box('RailClamp_Base',(0,0,.025),(.20,.19,.05),'M_HullNavy',.012)
    for s in (-1,1):box('RailClamp_Jaw',(s*.078,0,.086),(.044,.19,.122),'M_HullNavy',.009)
    beam('ClampScrew',(0,-.118,.08),(0,.11,.08),.012,'M_Steel')
    box('ClampThumbGrip',(0,-.145,.08),(.09,.032,.024),'M_Steel',.006)
    cyl('RodSocket',(0,0,.135),.038,.12,'M_Steel')
    beam('JigRod_Lower',(0,0,.16),(.045,-.14,.76),.024,'M_DeckWood',.017)
    beam('JigRodTip',(.045,-.14,.76),(.10,-.45,1.15),.014,'M_HullNavy',.009)
    for t in (.22,.62,.96):
        c=Vector((.045,-.14,.76)).lerp(Vector((.10,-.45,1.15)),t)
        ring('RodGuide',c,.017,.004,'M_Steel',12)
    beam('JigLine',(.10,-.45,1.15),(.10,-.45,.063),.0045,'M_Rope',n=6)
    ell('JigLure',(.10,-.45,.055),(.022,.028,.045),'M_SafetyOrange')
    ring('LureBand',(.10,-.45,.052),.021,.004,'M_RailIvory',12)
    for j in range(6):
        angle=math.tau*j/6;dx,dy=math.cos(angle),math.sin(angle)
        tube('JigHookCrown',[(.10+dx*.008,-.45+dy*.008,.027),(.10+dx*.024,-.45+dy*.024,.013),(.10+dx*.031,-.45+dy*.031,.025)],.0028,'M_Steel',5)
    beam('JigReel',(.016,-.028,.27),(.095,-.028,.27),.057,'M_HullNavy',n=16)
    for x in (.016,.095):beam('ReelFlange',(x-.004,-.028,.27),(x+.004,-.028,.27),.069,'M_Steel',n=16)
    beam('ReelCrank',(.105,-.028,.27),(.105,-.072,.30),.008,'M_Steel')
    beam('ReelGrip',(.104,-.072,.30),(.137,-.072,.30),.012,'M_DeckWood')
    tube('LampArm',[(-.08,.025,.11),(-.20,.025,.22),(-.23,.025,.40)],.015,'M_Steel')
    cyl('LampFoot',(-.23,.025,.285),.059,.022,'M_HullNavy')
    cone('LampWarmPane',(-.23,.025,.337),.046,.052,.09,'M_OilskinYellow')
    for j in range(4):
        t=math.tau*j/4;d=Vector((.054*math.cos(t),.054*math.sin(t),0))
        beam('LampGuard',Vector((-.23,.025,.286))+d,Vector((-.23,.025,.386))+d,.006,'M_HullNavy',n=6)
    cone('LampShade',(-.23,.025,.399),.086,.048,.035,'M_HullNavy')
    cyl('LampCap',(-.23,.025,.425),.035,.018,'M_Steel')
def spare():
    cyl('SpoolCore',(0,0,.053),.105,.072,'M_DeckWood',16)
    for z in (.012,.094):cyl('SpoolFlange',(0,0,z),.148,.024,'M_WoodHighlight',16)
    for j in range(4):ring('SpareLineWrap',(0,0,.028+j*.016),.113,.010,'M_HullNavy',24)
    cyl('SpoolAxle',(0,0,.108),.024,.012,'M_WoodRecess')
    tube('LooseRigLine',[(.113,0,.053),(.164,-.02,.016),(.192,-.083,.012),(.236,-.101,.012),(.264,-.074,.012)],.007,'M_HullNavy')
    beam('RigSwivel',(.264,-.074,.012),(.288,-.074,.012),.010,'M_Steel',n=8)
    # Open J hook, never a closed torus mistaken for a hook.
    hook=[(.29,-.074,.012),(.341,-.074,.012)]
    hook += [(.341+.027*math.cos(t),-.101+.027*math.sin(t),.012) for t in [math.pi/2-i*math.pi*1.55/15 for i in range(16)]]
    tube('OpenHook',hook,.0055,'M_Steel',6)
    beam('HookPoint',hook[-1],(hook[-1][0]-.014,hook[-1][1]+.004,.012),.0055,'M_Steel',0,n=6)
def oil():
    box('CanBody',(0,0,.146),(.23,.15,.278),'M_RailIvory',.026)
    box('CanBase',(0,0,.020),(.236,.156,.040),'M_HullNavy',.012)
    box('CanShoulder',(0,0,.267),(.212,.142,.038),'M_RailIvory',.014)
    box('TealPanel',(0,-.0755,.148),(.119,.007,.103),'M_SeaTeal',.009)
    box('PanelStripe',(0,-.080,.148),(.074,.004,.012),'M_RailIvory',.004)
    cyl('FillNeck',(-.062,.005,.293),.032,.032,'M_Steel')
    cyl('FillCap',(-.062,.005,.315),.039,.025,'M_HullNavy')
    tube('CarryHandle',[(-.084,.005,.281),(-.093,.005,.375),(-.070,.005,.393),(.030,.005,.393),(.052,.005,.374),(.061,.005,.281)],.012,'M_Steel',8)
    beam('SpoutLower',(.088,0,.240),(.143,0,.320),.020,'M_Steel',.015)
    beam('SpoutUpper',(.143,0,.320),(.226,0,.407),.015,'M_Steel',.010)
    # An annular lip and recessed dark bore make the spout visibly open.
    c=Vector((.226,0,.407));direction=Vector((.083,0,.087)).normalized();u=Vector((0,1,0));v=direction.cross(u)
    vs=[c+direction*d+rr*(u*math.cos(i*math.tau/12)+v*math.sin(i*math.tau/12)) for d,rr in [(0,.013),(.004,.013),(.004,.0075),(-.006,.0075)] for i in range(12)]
    fs=[(j*12+i,j*12+(i+1)%12,(j+1)*12+(i+1)%12,(j+1)*12+i) for j in range(3) for i in range(12)]
    mesh('SpoutLip',vs,fs,'M_Steel');beam('SpoutBore',c-direction*.007,c-direction*.006,.0074,'M_Rubber',n=12)
def add_net():
    # Shallow open landing-net basket, jellyfish above the visible rope lattice.
    ring('LandingNet_Rim',(0,.035,.135),.43,.014,'M_Rope',32)
    # Orthogonal lattice lifted towards the circular rim; broad, sparse cells.
    for s in (-1,1):
        for j in range(-4,5):
            off=j*.082;span=math.sqrt(.415**2-off**2)
            pts=[]
            for k in range(13):
                t=-span+2*span*k/12;x,y=(off,t) if s<0 else (t,off)
                rr=math.sqrt(x*x+y*y)/.43;pts.append((x,y+.035,.012+.12*rr**2))
            tube('LandingNet_Lattice',pts,.0045,'M_Rope',5)
    beam('LandingNet_Handle',(.39,.035,.135),(.70,.035,.135),.019,'M_DeckWood',.015)
def bounds(obs):
    pts=[o.matrix_world@v.co for o in obs if o.type=='MESH' for v in o.data.vertices]
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
def tris(obs):return sum(len(p.vertices)-2 for o in obs if o.type=='MESH' for p in o.data.polygons)
def clean():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
provenance=[]
def protected(path,purpose):
    p=ROOT/path;provenance.append({'file':path.as_posix(),'sha256':sha(p),'purpose':purpose});return p

def setup_asset():
    clean()
    if NAME in ('JigRig','SpareRig','LanternOilCan'):
        protected(Path('Art/Source/Art108/build_stations.py'),'read-only chunky primitive/palette reference')
        {'JigRig':jig,'SpareRig':spare,'LanternOilCan':oil}[NAME]()
        origin='New geometry in StationsV1 palette; earlier kit used as read-only reference.'
    elif NAME=='RivalBoat':
        src=protected(Path('Assets/Art/Models/Harbour/Rowboat_VariantRed.fbx'),'existing named rival-boat derivative')
        bpy.ops.import_scene.fbx(filepath=str(src));origin='Reuses the existing red rowboat model; no invented rival hull.'
    else:
        src=protected(Path('Art/Models/StationsV1')/(NAME+'.blend'),'existing named A6 geometry derivative')
        bpy.ops.wm.open_mainfile(filepath=str(src))
        for o in list(bpy.context.scene.objects):
            if o.type not in ('MESH','EMPTY'):bpy.data.objects.remove(o,do_unlink=True)
        if NAME=='JellyfishClump':add_net()
        origin='Reuses named StationsV1 geometry'+('; adds visible rope landing net.' if NAME=='JellyfishClump' else '; fresh export and evidence, no claim of new sculpt.')
    # Reparent preserving world matrices, with an identity floor/waterline root.
    objects=list(bpy.context.scene.objects)
    for o in objects:
        m=o.matrix_world.copy();o.parent=None;o.matrix_world=m
    for o in objects:
        if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
    if NAME in ('SpareRig','LanternOilCan','JellyfishClump','OffalPile','TableEel'):
        bpy.context.view_layer.update()
        low,high=map(Vector,bounds(list(bpy.context.scene.objects)))
        delta=Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
        for o in bpy.context.scene.objects:o.location-=delta
        origin+=' Horizontal bounds centred and lowest contact set to zero for floor placement.'
    root=bpy.data.objects.new('PropsV2_'+NAME,None);bpy.context.scene.collection.objects.link(root)
    for o in list(bpy.context.scene.objects):
        if o!=root:o.parent=root
    bpy.context.view_layer.update();return root,origin

def render_review(obs,record):
    sc=bpy.context.scene;sc.render.engine='BLENDER_EEVEE';sc.render.resolution_x=700;sc.render.resolution_y=700;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.world=bpy.data.worlds.new('PropsV2 Review');sc.world.use_nodes=True
    sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.72,.76,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.65
    sc.view_settings.view_transform='AgX'
    bb=record['bounds_source_m'];lo,hi=map(Vector,bb);centre=(lo+hi)/2;size=max(hi-lo);size=max(size,.15)
    floor_z=0 if lo.z>=-.001 else lo.z-.005
    floor=box('REVIEW_ONLY_Surface',(centre.x,centre.y,floor_z-.018),(size*200,size*200,.036),'M_RailIvory',0)
    lights=[]
    for label,offset,energy,colour in [('Key',(-2,-3,4),500,(1,.85,.66)),('Fill',(3,-1,2),300,(.64,.82,1)),('Rim',(-1,3,3),450,(1,.91,.78))]:
        d=bpy.data.lights.new('REVIEW_ONLY_'+label,'AREA');d.energy=energy*max(.25,size*size);d.shape='DISK';d.size=size*3;d.color=colour
        o=bpy.data.objects.new(d.name,d);sc.collection.objects.link(o);o.location=centre+Vector(offset)*size;o.rotation_euler=(centre-o.location).to_track_quat('-Z','Y').to_euler();lights.append(o)
    cam=bpy.data.objects.new('REVIEW_ONLY_Camera',bpy.data.cameras.new('Review'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=size*1.55
    directions={'three-quarter':(1.5,-2.4,1.35),'front':(0,-3,.65),'left':(3,0,.65),'back':(0,3,.65),'right':(-3,0,.65),'top':(0,-.001,3)}
    for label,direction in directions.items():
        cam.location=centre+Vector(direction)*size;cam.rotation_euler=(centre-cam.location).to_track_quat('-Z','Y').to_euler()
        sc.render.filepath=str(PRE/(label+'.png'));bpy.ops.render.render(write_still=True)
    if NAME=='JigRig':
        for light in lights:light.data.energy*=.015
        sc.world.node_tree.nodes['Background'].inputs[1].default_value=.035
        ld=bpy.data.lights.new('REVIEW_ONLY_LampLight','POINT');ld.energy=9;ld.color=(1,.64,.25);ld.shadow_soft_size=.09
        lamp=bpy.data.objects.new(ld.name,ld);sc.collection.objects.link(lamp);lamp.location=(-.23,-.045,.327)
        cam.location=centre+Vector((1.5,-2.4,1.35))*size;cam.rotation_euler=(centre-cam.location).to_track_quat('-Z','Y').to_euler()
        sc.render.filepath=str(PRE/'night-context.png');bpy.ops.render.render(write_still=True)
    record['render_files']=[str(p.relative_to(ROOT)).replace('\\','/') for p in sorted(PRE.glob('*.png'))]

def effect():
    clean();n=256 if NAME=='DeckLightPool' else 1024;h=256 if NAME=='DeckLightPool' else 512
    rgba=[0.]*(n*h*4)
    if NAME=='DeckLightPool':
        for y in range(h):
            for x in range(n):
                r=math.hypot(x-127.5,y-127.5)/124
                stops=[(0,.65),(.35,.40),(.72,.12),(1,0)]
                alpha=0
                for (r0,a0),(r1,a1) in zip(stops,stops[1:]):
                    if r0<=r<=r1:alpha=a0+(a1-a0)*(r-r0)/(r1-r0);break
                i=(y*n+x)*4;rgba[i:i+4]=[1,213/255,147/255,alpha]
        svg='<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256"><defs><radialGradient id="p"><stop stop-color="#FFD593" stop-opacity=".65"/><stop offset=".35" stop-color="#FFD593" stop-opacity=".40"/><stop offset=".72" stop-color="#FFD593" stop-opacity=".12"/><stop offset="1" stop-color="#FFD593" stop-opacity="0"/></radialGradient></defs><circle cx="128" cy="128" r="124" fill="url(#p)"/></svg>'
        purpose='Single station soft warm deck light pool, 1m suggested diameter, centre pivot. Alpha blended/emissive material binding by code owner.'
    else:
        paths=[]
        for j in range(28):
            xx=24+(j*137)%970;yy=20+(j*83)%450;length=28+(j%4)*13;width=1+j%2;alpha=.12+(j%4)*.035
            paths.append(f'<path d="M{xx} {yy}l-12 {length}" stroke="#B9D5DF" stroke-opacity="{alpha}" stroke-width="{width}" stroke-linecap="round"/>')
            for step in range(int(length*2)+1):
                t=step/(int(length*2));cx=xx-12*t;cy=h-1-(yy+length*t)
                for y in range(max(0,int(cy)-2),min(h,int(cy)+3)):
                    for x in range(max(0,int(cx)-2),min(n,int(cx)+3)):
                        coverage=max(0,min(1,width/2+.5-math.hypot(x-cx,y-cy)))
                        i=(y*n+x)*4
                        if coverage*alpha>rgba[i+3]:rgba[i:i+4]=[185/255,213/255,223/255,coverage*alpha]
        svg='<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="512">'+''.join(paths)+'</svg>'
        purpose='Transparent rain-streak sprite; scroll/crossfade during existing Squall event. No scene dimming or flashing baked in.'
    # Set colour space before writing pixels; byte colours are explicitly sRGB.
    im=bpy.data.images.new(NAME,width=n,height=h,alpha=True);im.colorspace_settings.name='sRGB';im.pixels=rgba
    im.filepath_raw=str(OUT/(NAME+'.png'));im.file_format='PNG';im.save()
    (OUT/(NAME+'.svg')).write_text(svg);shutil.copyfile(OUT/(NAME+'.png'),GAME/(NAME+'.png'))
    record={'name':NAME,'revision':a.revision,'kind':'RGBA effect','logical_size':[n,h],'pivot':[.5,.5],'use':purpose,
            'provenance':[{'file':'Art/Source/Art108/build_effects.py','sha256':sha(ROOT/'Art/Source/Art108/build_effects.py'),'purpose':'read-only existing named effect design'}],
            'delivery_sha256':{NAME+'.png':sha(OUT/(NAME+'.png')),NAME+'.svg':sha(OUT/(NAME+'.svg'))},'runtime_file':str((GAME/(NAME+'.png')).relative_to(ROOT)).replace('\\','/'),'palette':PALETTE}
    (OUT/'build-manifest.json').write_text(json.dumps(record,indent=2));print('PROPSV2 EFFECT COMPLETE',NAME,flush=True)

if NAME in ('DeckLightPool','SquallOverlay'):effect()
else:
    root,origin=setup_asset();obs=[o for o in bpy.context.scene.objects if o.type=='MESH'];record={'name':NAME,'revision':a.revision,'kind':'mesh','origin':origin,'provenance':provenance,'bounds_source_m':bounds(obs),'triangles':tris(obs),'mesh_parts':{o.name:sum(len(p.vertices)-2 for p in o.data.polygons) for o in obs},'pivot':[0,0,0],'pivot_use':'rail clamp contact' if NAME=='JigRig' else 'waterline' if NAME in ('SealHead','DolphinFin','InspectorLaunch','RivalBoat') else 'airborne centre' if NAME in ('GullSwoop','FlyingFishEvent') else 'floor/contact','source_axes':'+X right / -Y front / +Z up','fbx_axes':'-Z forward / Y up','units':'metres','palette':PALETTE}
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(NAME+'.blend')))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(OUT/(NAME+'.fbx')),use_selection=True,object_types={'EMPTY','MESH'},axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,add_leaf_bones=False,use_triangles=True)
    shutil.copyfile(OUT/(NAME+'.fbx'),GAME/('PropsV2_'+NAME+'.fbx'))
    record['delivery_sha256']={NAME+ext:sha(OUT/(NAME+ext)) for ext in ('.blend','.fbx')};record['runtime_file']=str((GAME/('PropsV2_'+NAME+'.fbx')).relative_to(ROOT)).replace('\\','/')
    if a.render=='all':render_review(obs,record)
    (OUT/'build-manifest.json').write_text(json.dumps(record,indent=2));print('PROPSV2 BUILD COMPLETE',NAME,record['triangles'],flush=True)
