"""RESTAURANT-PIER-1. Deterministic metres, Blender X right/Y inland/Z up.
Export follows the existing room FBXs. Unity handedness: (-x,z,-y).
Only writes RestaurantPier scope. No Unity or git invocation.
--phase 1: S1 + quay; --phase 2: S1..S4; --phase 3: finished harbour.
"""
import bpy, bmesh, math, json, sys, argparse, hashlib, random
from pathlib import Path
from mathutils import Vector
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent; R=O.parents[2]
P=R/'Assets/Resources/Restaurant'; A=R/'Assets/Resources/RestaurantAtlas'
NAMES=['Stage1V4','Stage2Bistro','Stage3Restaurant','Stage4Seafood']
args=argparse.ArgumentParser();args.add_argument('--phase',type=int,default=3);args.add_argument('--stage',type=int,nargs='*');args.add_argument('--samples',type=int,default=32);args.add_argument('--skip-render',action='store_true')
arg=args.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
sc=bpy.context.scene;sc.unit_settings.system='METRIC'
base=bpy.data.images.load(str(A/'Restaurant_BaseColor.png'));surface=bpy.data.images.load(str(A/'Restaurant_Surface.png'));surface.colorspace_settings.name='Non-Color'
def material(name):
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;b=n.get('Principled BSDF')
    c=n.new('ShaderNodeTexImage');c.image=base;c.name='Restaurant_BaseColor'
    s=n.new('ShaderNodeTexImage');s.image=surface;s.name='Restaurant_Surface'
    sep=n.new('ShaderNodeSeparateColor');l.new(s.outputs['Color'],sep.inputs[0]);l.new(sep.outputs[0],b.inputs['Roughness']);l.new(sep.outputs[1],b.inputs['Metallic'])
    # Match shader's vertex pigment and emission mask without a second material.
    col=n.new('ShaderNodeVertexColor');col.layer_name='Color';mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;l.new(c.outputs['Color'],mul.inputs[1]);l.new(col.outputs['Color'],mul.inputs[2]);l.new(mul.outputs[0],b.inputs['Base Color']);l.new(mul.outputs[0],b.inputs['Emission Color'])
    e=n.new('ShaderNodeMath');e.operation='MULTIPLY';e.inputs[1].default_value=2.8;l.new(sep.outputs[2],e.inputs[0]);l.new(e.outputs[0],b.inputs['Emission Strength']);return m
MAT=material('Restaurant_Atlas_URP_V4')
class G:
    def __init__(self):self.v=[];self.f=[];self.cells=[];self.tints=[]
    def add(self,v,f,c=6,tint=1):
        k=len(self.v);self.v.extend([tuple(p) for p in v]);self.f.extend([tuple(k+i for i in p) for p in f]);self.cells.extend([c]*len(f));self.tints.extend([tint]*len(f))
    def box(self,c,s,cell=6,bevel=.025,tint=1):
        x,y,z=c;w,d,h=[v/2 for v in s];b=min(bevel,w*.4,d*.4) if min(s)>.105 else 0
        loop=[(-w+b,-d),(w-b,-d),(w,-d+b),(w,d-b),(w-b,d),(-w+b,d),(-w,d-b),(-w,-d+b)] if b else [(-w,-d),(w,-d),(w,d),(-w,d)]
        n=len(loop);vs=[(x+xx,y+yy,z+zz) for zz in (-h,h) for xx,yy in loop];fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        self.add(vs,fs,cell,tint)
    def tube(self,path,r=.04,cell=6,n=6,tint=1):
        pp=list(map(Vector,path));vs=[]
        for j,p in enumerate(pp):
            t=(pp[min(j+1,len(pp)-1)]-pp[max(j-1,0)]).normalized();h=Vector((0,0,1)) if abs(t.z)<.9 else Vector((0,1,0));u=h.cross(t).normalized();v=t.cross(u).normalized()
            vs.extend([p+r*(u*math.cos(i*math.tau/n)+v*math.sin(i*math.tau/n)) for i in range(n)])
        fs=[tuple(reversed(range(n))),tuple(range((len(pp)-1)*n,len(pp)*n))]
        fs.extend([(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(pp)-1) for i in range(n)])
        self.add(vs,fs,cell,tint)
    def post(self,x,y,z0,z1,r=.16,cell=6,tint=1):self.tube([(x,y,z0),(x,y,z1)],r,cell,8,tint)
    def ring(self,c,r,minor=.025,cell=27):self.tube([(c[0]+r*math.cos(i*math.tau/8),c[1]+r*math.sin(i*math.tau/8),c[2]) for i in range(9)],minor,cell,4)
    def object(self,name,parent=None):
        me=bpy.data.meshes.new(name);me.from_pydata(self.v,[],self.f);me.update();ob=bpy.data.objects.new(name,me);sc.collection.objects.link(ob);ob.parent=parent;me.materials.append(MAT)
        uv=me.uv_layers.new(name='UVMap');cols=me.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
        for face,cell,tint in zip(me.polygons,self.cells,self.tints):
            row,col=divmod(cell,8);normal=face.normal;axis=max(range(3),key=lambda i:abs(normal[i]));ax=[i for i in range(3) if i!=axis];points=[me.vertices[i].co for i in face.vertices];lo=[min(p[i] for p in points) for i in ax];sz=[max(p[i] for p in points)-v for i,v in zip(ax,lo)]
            for li,pt in zip(face.loop_indices,points):
                u=.12+.76*((pt[ax[0]]-lo[0])/max(sz[0],1e-7));v=.12+.76*((pt[ax[1]]-lo[1])/max(sz[1],1e-7));uv.data[li].uv=((col+u)/8,1-(row+1-v)/4);cols.data[li].color=(tint,tint,tint,1)
        return ob
root=bpy.data.objects.new('RestaurantPier',None);sc.collection.objects.link(root)
prod=[];groups={};lights=[]
def group(name):
    o=bpy.data.objects.new(name,None);sc.collection.objects.link(o);o.parent=root;groups[name]=o;return o
def mesh(g,name,pa):
    ob=g.object(name,pa);prod.append(ob);return ob
def point(name,p,energy=18,radius=.35):
    lights.append(dict(name=name,type='POINT',position_blender_m=list(p),position_unity_m=[-p[0],p[2],-p[1]],blender_power=energy,linear_rgb=[1,.60,.22],range_recipe_m=3,radius_m=radius))
def deck(g,x0,x1,y0,y1):
    # Full-size broad planks, with seams in geometry and warm atlas timber.
    n=math.ceil((y1-y0)/.39);w=(y1-y0)/n
    for i in range(n):g.box(((x0+x1)/2,y0+(i+.5)*w,-.085),(x1-x0,w-.012,.17),4 if i%4 else 6,.014,.67)
    for y in (y0+.1,y1-.1):g.box(((x0+x1)/2,y,-.27),(x1-x0+.05,.21,.25),6,.035,.60)
    for x in (x0+.12,x1-.12):g.box((x,(y0+y1)/2,-.27),(.22,y1-y0,.25),6,.03,.60)
def piling(g,x,y,cap=True):
    g.post(x,y,-1.8,.17 if cap else -.18,.16,6,.55)
    if cap:
        g.post(x,y,.13,.21,.19,4,.70)
def make_pier(stage):
    pa=group(f'Pier_S{stage}');g=G();end=[4.85,9,11,13][stage-1];x0=-5.25;x1=end+.68;y0=-5.05;y1=3.6
    deck(g,x0,x1,y0,y1)
    # Left rear entrance stays visible even in the later stages' current off-centre game lens.
    # Entire bridge is outside the inherited room shell x>=-4.86.
    deck(g,-6.4,-4.95,2.85,4.55)
    for x in [x0+.18,x1-.16]:
        for y in (y0+.2,-1.5,1.6,3.4):piling(g,x,y)
    for x in [x0+2.1+i*2.3 for i in range(math.ceil((x1-x0-2)/2.3))]:
        if x<x1-.5:piling(g,x,y0+.2);piling(g,x,y1-.2,False)
    for y in (4.2,):
        for x in (-6.25,-5.10):piling(g,x,y)
    # Low rope guides at the approach, behind the room, never across its open interior.
    for x in (-6.30,-5.05):
        for y in (3.8,4.4):g.post(x,y,-.03,.68,.075,4,.65)
        g.tube([(x,3.8,.62),(x,4.1,.48),(x,4.4,.62)],.022,27,5,.7)
    mesh(g,'Deck_Planks_Beams_Pilings_S'+str(stage),pa)
    pa['deck_top_unity_y']=0.;pa['footprint_blender']=[x0,x1,y0,y1];pa['approach_blender']=[-6.4,-4.95,2.85,4.55]
    return pa
for stage in range(1,2 if arg.phase==1 else 5):make_pier(stage)
quay=group('Quay');g=G()
g.box((2,23.4,-.70),(48,33.2,1.4),17,.12,.55)
# A continuous land-backed stone edge, with staggered courses and broad coping stones.
for row,z in enumerate((-.68,-.30)):
    for i in range(33):g.box((-21.5+i*1.5+(row%2)*.3,6.86,z),(1.46,.38,.36),16 if i%3 else 17,.055,.53)
for i in range(38):g.box((-21.5+i*1.3,6.78,-.045),(1.27,.86,.17),3,.045,.58)
# Readable paving follows the edge; the large land base continues behind all houses.
for y in (7.55,8.4):
    for i in range(24):g.box((-20.8+i*2, y,.018),(1.94,.78,.05),16,.018,.53)
mesh(g,'Quay_Stonework_And_Coping',quay)
def house(x,y,w,d,h,cell,idx):
    g=G();g.box((x,y,h/2),(w,d,h),cell,.08,.40)
    # Chunky gabled navy roof, restrained ridge and a chimney.
    a=w/2+.18;b=d/2+.2;z=h-.02;peak=h+1.1
    g.add([(x-a,y-b,z),(x+a,y-b,z),(x,y-b,peak),(x-a,y+b,z),(x+a,y+b,z),(x,y+b,peak)],[(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)],0,.33)
    g.tube([(x,y-b,peak+.025),(x,y+b,peak+.025)],.065,0,6,.5)
    for sx in (-1,1):g.tube([(x+sx*a,y-b-.015,z),(x,y-b-.015,peak)],.065,7,5,.46)
    g.box((x+w*.28,y+.25,h+.65),(.42,.5,1.15),16,.055,.4)
    for dx in (-.12,.12):g.post(x+w*.28+dx,y+.25,h+1.18,h+1.43,.08,28,.6)
    g.box((x,y-d/2-.025,.68),(.65,.10,1.35),0,.03,.4)
    for xx in [-w*.27,w*.27]:
        for zz in (1.,2.45) if h>3 else (1.45,):
            g.box((x+xx,y-d/2-.06,zz),(.76,.14,.91),0,.028,.5)
            g.box((x+xx,y-d/2-.145,zz),(.61,.025,.73),19,.006,.20)
            g.box((x+xx,y-d/2-.18,zz),(.035,.025,.76),7,.0,.55);g.box((x+xx,y-d/2-.18,zz),(.63,.025,.035),7,.0,.55)
            for side in (-1,1):g.box((x+xx+side*.47,y-d/2-.08,zz),(.18,.1,.88),1,.02,.4)
            g.box((x+xx,y-d/2-.18,zz-.47),(.96,.27,.09),3,.02,.48)
    mesh(g,f'House_{idx:02d}_Gable_Windows',quay)
for i,(x,y,w,d,h,cell) in enumerate([(-12,10.3,3.2,3.4,3.4,16),(-8.4,10.4,3.6,3.8,4.2,3),(-4.6,10.8,3.3,3.6,3.5,28),(-.9,10.6,3.6,3.6,4.0,16),(3.1,10.5,3.6,3.8,3.3,3),(7.1,10.6,3.7,3.6,4.1,28),(11.2,10.5,3.7,3.6,3.4,16),(15.4,10.6,3.6,3.6,4.0,3),(19.4,10.6,3.6,3.6,3.1,28)]):house(x,y,w,d,h,cell,i)
def lamp(g,x,y):
    g.post(x,y,0,.18,.16,0,.55);g.post(x,y,.10,2.15,.055,0,.55)
    g.tube([(x,y,1.95),(x,y-.16,2.2),(x,y-.48,2.2)],.045,0,6,.55)
    g.box((x,y-.45,1.96),(.24,.24,.36),19,.035,.38)
    for dx in (-.115,.115):
        for dy in (-.115,.115):g.post(x+dx,y-.45+dy,1.77,2.16,.015,0,.6)
    g.box((x,y-.45,2.18),(.33,.33,.10),0,.035,.6);g.box((x,y-.45,1.75),(.29,.29,.07),0,.025,.6)
    point('QuayLamp_'+str(len(lights)),(x,y-.45,1.95),20,.3)
g=G()
for x in (-15,-9,-3,3,9,15,21):lamp(g,x,7.35)
mesh(g,'Quay_Lamp_Posts',quay)
for ob in quay.children:
    for v in ob.data.vertices:v.co.y-=2.5
for rec in lights:
    rec['position_blender_m'][1]-=2.5;rec['position_unity_m'][2]+=2.5
boats=group('Boats');clutter=group('Clutter')
def boat(cx,cy,length,width,angle,name,cabin=False):
    g=G();N=12
    # Two rounded hull rings with a tapered bow. Upright solid faceted sides; open warm cockpit.
    ring=[(-.42,-.43),(.25,-.49),(.45,-.29),(.52,0),(.45,.29),(.25,.49),(-.42,.43),(-.5,.28),(-.5,-.28)]
    n=len(ring);verts=[]
    for k,(scale,z) in enumerate(((.65,-.83),(1,-.42))):verts.extend([(x*length*scale,y*width*scale,z) for x,y in ring])
    fs=[tuple(reversed(range(n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    g.add(verts,fs,0,.58)
    g.add([(x*length*.84,y*width*.80,-.48) for x,y in ring],[tuple(range(n))],4,.60)
    for scale,z,r,c in ((1,-.40,.045,2),(.91,-.68,.026,10)):
        g.tube([(x*length*scale,y*width*scale,z) for x,y in ring+[ring[0]]],r,c,6,.7)
    for x in (-.27,0,.23):g.box((x*length,0,-.35),(.21,width*.70,.12),4,.025,.65)
    if cabin:
        g.box((-.22*length,0,.03),(.82,width*.67,.86),2,.06,.48)
        g.box((-.22*length,-width*.35,.16),(.55,.035,.32),29,.025,.6)
        g.box((-.22*length,0,.49),(.95,width*.8,.13),0,.04,.55)
        g.post(-.25*length,0,.5,1.0,.035,7,.5)
        g.box((-.25*length,0,1.04),(.16,.16,.15),19,.025,.28)
    else:
        g.box((-.43*length,0,-.24),(.26,.31,.40),8,.04,.6)
        g.tube([(-.15*length,-.1,-.23),(.32*length,.35,-.13)],.035,4,6,.65)
    for x in (-.3,.2):
        g.post(x*length,-width*.55,-.58,-.25,.075,10,.65)
    # Transform the finished assembly, then put a mooring line into the shared boat group.
    co=math.cos(angle);si=math.sin(angle)
    def trans(p):return (cx+p[0]*co-p[1]*si,cy+p[0]*si+p[1]*co,p[2])
    g.v=[trans(p) for p in g.v];mesh(g,name,boats)
    start=trans((.35*length,.42*width,-.36));gg=G()
    end=(-5.25,cy+.45,.05) if name=='Boat_Rowboat' else (cx,4.25,.05)
    mid=((start[0]+end[0])/2,(start[1]+end[1])/2,-.24)
    gg.tube([start,mid,end],.018,27,5,.65);mesh(gg,name+'_Mooring',boats)
def crate(g,x,y,z,s=.5):
    g.box((x,y,z+s/2),(s,s*.8,s),6,.035,.6)
    for zz in (.10,.40):g.box((x,y-s*.415,z+zz),(.92*s,.035,.075),4,.01,.7)
    for xx in (-s*.42,s*.42):g.box((x+xx,y-s*.42,z+s*.5),(.075,.055,s*.92),4,.01,.7)
    g.tube([(x-s*.33,y-s*.44,z+.07),(x+s*.33,y-s*.44,z+s-.07)],.035,4,4,.7)
if arg.phase>=3:
    boat(-6.5,-3.5,2.7,1.15,1.57,'Boat_Rowboat',False)
    boat(-6.65,.1,3.2,1.3,1.57,'Boat_Moored_Fisher',True)
    boat(17.0,2.7,3.5,1.5,-.25,'Boat_Harbour_Launch',True)
    g=G()
    for x in (-14,-7,0,7,14,21):
        g.box((x,6.8,.09),(.40,.30,.18),0,.04,.65);g.post(x,6.8,.08,.40,.075,0,.6);g.tube([(x-.22,6.8,.34),(x+.22,6.8,.34)],.065,0,6,.6)
    for x,y in [(-6.1,7.8),(4.5,8.0),(12.6,7.9)]:
        crate(g,x,y,.05,.64);crate(g,x+.7,y+.1,.05,.5);crate(g,x,y,.69,.46)
        g.post(x-1,y,.02,.66,.28,6,.6)
        for z in (.12,.52):g.ring((x-1,y,z),.284,.025,8)
        g.ring((x+.5,y-.55,.10),.24,.035,27);g.ring((x+.5,y-.55,.15),.21,.035,27)
    mesh(g,'Harbour_Crates_Barrels_Bollards_Rope',clutter)
    # Rings fixed to quay face, hanging down to the water.
    g=G()
    for x in (-10,-5,0,5,10,15):
        path=[(x+.24*math.cos(i*math.tau/8),6.52,-.30+.24*math.sin(i*math.tau/8)) for i in range(9)];g.tube(path,.065,8,5,.6)
        g.tube([(x,6.53,.02),(x,6.52,-.1)],.016,27,5,.6)
    mesh(g,'Quay_Hanging_Tyre_Fenders',clutter)
    # Small festoon stays inland of the coping. Warm notes across water, no tall foreground poles.
    g=G()
    for left in (-9,3,15):
        for x in (left,left+4):g.post(x,7.95,0,2.55,.045,0,.55)
        path=[(left+i*.5,7.95,2.55-.32*math.sin(i*math.pi/8)) for i in range(9)];g.tube(path,.012,8,4,.6)
        for i in range(1,8):
            x,y,z=path[i];g.post(x,y,z-.13,z-.04,.042,19,.35)
    mesh(g,'Quay_Festoon_Lights',clutter)
    for ob in clutter.children:
        for v in ob.data.vertices:v.co.y-=2.5

def stats():
    rows=[]
    for ob in prod:
        ob.data.calc_loop_triangles();pts=[ob.matrix_world@v.co for v in ob.data.vertices]
        lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
        rows.append(dict(name=ob.name,group=ob.parent.name,triangles=len(ob.data.loop_triangles),bounds_blender=[lo,hi],bounds_unity=[[-hi[0],lo[2],-hi[1]],[-lo[0],hi[2],-lo[1]]]))
    return rows
rows=stats();total=sum(r['triangles'] for r in rows);print('PIER TRIANGLES',total,flush=True);assert total<=25000,total
(O/f'phase{arg.phase}-metrics.json').write_text(json.dumps(dict(total_triangles=total,objects=rows),indent=2))
# Only the pier asset, with stages separated, is saved/exported. Rooms/sea never enter production.
if arg.phase==3:
    for im in (base,surface):im.pack()
    bpy.ops.wm.save_as_mainfile(filepath=str(O/'RestaurantPier.blend'))
    bpy.ops.object.select_all(action='DESELECT');root.select_set(True)
    for ob in list(groups.values())+prod:ob.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(P/'RestaurantPier.fbx'),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',bake_anim=False,colors_type='LINEAR',path_mode='RELATIVE')
    (P/'RestaurantPier-lighting.json').write_text(json.dumps(dict(lights=lights),indent=2)+'\n')

def setup_render():
    sc.render.engine='CYCLES';sc.cycles.samples=arg.samples;sc.cycles.use_denoising=True
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
        for dev in prefs.devices:dev.use=dev.type=='OPTIX'
        if any(d.type=='OPTIX' for d in prefs.devices):sc.cycles.device='GPU'
    except Exception:pass
    sc.world=bpy.data.worlds.new('Review_Dusk');sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.10,.16,.28,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.32
    sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast';sc.view_settings.exposure=.1
    sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB'
    cam=bpy.data.objects.new('REVIEW_GameCamera',bpy.data.cameras.new('REVIEW_GameCamera'));sc.collection.objects.link(cam);sc.camera=cam;cam.data.type='PERSP';cam.data.clip_end=70;cam.data.sensor_fit='VERTICAL';cam.data.sensor_height=24
    # Geometry and atlas colors are untouched; review water approximates AddSea exactly in level/texture repeat.
    bpy.ops.mesh.primitive_plane_add(size=90,location=(0,0,-.57));sea=bpy.context.object;sea.name='REVIEW_AddSea'
    m=bpy.data.materials.new('REVIEW_NightWater');m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;b=n['Principled BSDF'];t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(P/'NightWater.png'));uv=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeVectorMath');v.operation='SCALE';v.inputs[3].default_value=8;l.new(uv.outputs['UV'],v.inputs[0]);l.new(v.outputs[0],t.inputs[0]);mul=n.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1;mul.inputs[2].default_value=(.32,.32,.32,1);l.new(t.outputs['Color'],mul.inputs[1]);l.new(mul.outputs[0],b.inputs['Base Color']);l.new(mul.outputs[0],b.inputs['Emission Color']);b.inputs['Emission Strength'].default_value=.45;b.inputs['Roughness'].default_value=.35;b.inputs['Metallic'].default_value=.15;sea.data.materials.append(m)
    d=bpy.data.lights.new('REVIEW_BlueDusk','SUN');d.energy=.6;d.color=(.39,.60,1);ob=bpy.data.objects.new(d.name,d);sc.collection.objects.link(ob);ob.rotation_euler=(math.radians(30),math.radians(-20),math.radians(-25))
    return cam
if not arg.skip_render:
    cam=setup_render();review=[]
    for stage in arg.stage or ([1] if arg.phase==1 else [1,2,3,4]):
        for n,g in groups.items():
            if n.startswith('Pier_S'):
                for ob in g.children:ob.hide_render=n!=f'Pier_S{stage}'
        before=set(sc.objects);bpy.ops.import_scene.fbx(filepath=str(P/(NAMES[stage-1]+'.fbx')),use_anim=False);room=[o for o in sc.objects if o not in before]
        # The game remaps every room material to the same atlas. Bind the actual resource atlas on the imported mesh.
        for ob in room:
            if ob.type=='MESH':
                ob.data.materials.clear();ob.data.materials.append(MAT)
                if 'Color' not in ob.data.color_attributes:
                    source=ob.data.color_attributes.active_color
                    saved=[tuple(v.color) for v in source.data] if source else []
                    a=ob.data.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='CORNER')
                    for i,v in enumerate(a.data):v.color=saved[i] if saved else (1,1,1,1)
        recipe=json.loads((P/(NAMES[stage-1]+'-lighting.json')).read_text())['lights'];roomlights=[]
        for rec in recipe+lights:
            if rec['type'] not in ('POINT','AREA'):continue
            d=bpy.data.lights.new('REVIEW_'+rec['name'],'POINT');d.energy=rec['blender_power'];d.color=rec.get('linear_rgb',[1,.6,.22]);d.shadow_soft_size=max(.12,rec.get('radius_m',.2));ob=bpy.data.objects.new(d.name,d);sc.collection.objects.link(ob);ob.location=rec['position_blender_m'];roomlights.append(ob)
        # Gentle broad key is review-only, recreating the room's realtime ambient/practical bounce.
        d=bpy.data.lights.new('REVIEW_RoomBounce','AREA');d.energy=1500;d.shape='RECTANGLE';d.size=8;d.size_y=5;d.color=(1,.77,.5);ob=bpy.data.objects.new(d.name,d);sc.collection.objects.link(ob);ob.location=([0,2.5,3.5,4.5][stage-1],-.5,6);roomlights.append(ob)
        pos=Vector((.598,-17.088,13.359)) if stage==1 else Vector(json.loads((P/(NAMES[stage-1]+'-cameras.json')).read_text())[0]['position_blender_m'])
        distance=pos.length;hw=7 if stage==1 else 7*distance/Vector((-.598,13.359,17.088)).length
        # Unity X mirror also reverses yaw: (38,178,0) maps to Blender (52,0,+2),
        # unlike the older unmirrored source camera JSON rotation of -2.
        cam.location=pos;cam.rotation_euler=(math.radians(52),0,math.radians(2))
        for w,h in [(1440,900),(844,390)]:
            top,bottom=(46/390,72/390) if w/h>1.9 else (78/900,140/900);aspect=w/(h*(1-top-bottom));inner=2*math.atan(hw/distance/aspect);fov=2*math.atan(math.tan(inner/2)/(1-top-bottom))
            cam.data.lens=cam.data.sensor_height/(2*math.tan(fov/2));cam.data.shift_y=(top-bottom)*.5;sc.render.resolution_x=w;sc.render.resolution_y=h;sc.render.resolution_percentage=100
            out=O/'renders'/(('stage%d-%dx%d.png'%(stage,w,h)) if arg.phase==3 else ('item%d-stage%d-%dx%d.png'%(arg.phase,stage,w,h)))
            sc.render.filepath=str(out);bpy.ops.render.render(write_still=True)
            review.append(dict(file=out.name,stage=stage,resolution=[w,h],camera_blender=list(pos),camera_unity=[-pos.x,pos.z,-pos.y],rotation_unity=[38,178,0],vertical_fov_deg=math.degrees(fov),lens_shift_y=cam.data.shift_y,frame_half_width=hw))
        if arg.phase==3:
            # Supplemental asset review only: same position, wider lens, aim at whole room.
            # Never presented as the current game camera or exported into the asset.
            target=Vector(([0,2.5,3.5,4.5][stage-1],2,0));cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler()
            widefov=math.radians(40 if stage==1 else 35);cam.data.lens=24/(2*math.tan(widefov/2));cam.data.shift_y=0
            sc.render.resolution_x=1440;sc.render.resolution_y=900;out=O/'renders'/f'overview-stage{stage}.png';sc.render.filepath=str(out);bpy.ops.render.render(write_still=True)
            review.append(dict(file=out.name,stage=stage,resolution=[1440,900],camera_blender=list(pos),supplemental_wide_overview=True,vertical_fov_deg=math.degrees(widefov)))
        for ob in room+roomlights:bpy.data.objects.remove(ob,do_unlink=True)
    (O/f'phase{arg.phase}-cameras.json').write_text(json.dumps(review,indent=2))
print('RESTAURANT-PIER phase',arg.phase,'COMPLETE',flush=True)
