"""CREW3D-WOMEN: authored female crew on the immutable original 20-bone CrewRig.
Utility topology/rig/export conventions adapted from read-only build_mira_sol.py.
Blender 5.2 --background --factory-startup --python this-file -- --name Lise --render quick|all|none.
No Assets, male sources, original rig, Unity or git writes.
"""
import argparse, bpy, bmesh, hashlib, json, math, sys, struct, zlib, random
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).parent))
from crew_female_shape import female_shape,region_for_weights,VERSION as FEMALE_VERSION
from crew_female_hair import build_hair
ORIGINAL=ROOT/'Art/Models/CrewRig/CrewRig.blend'
p=argparse.ArgumentParser()
p.add_argument('--name', choices=['Lise','Tess','Ines','Noor','Ana','Rosa','Tove','CaptainF'],required=True)
p.add_argument('--render',choices=['quick','all','none'],default='quick')
p.add_argument('--samples',type=int,default=32)
p.add_argument('--revision',default='r01')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
NAME=args.name
CFG=json.loads(Path(__file__).with_name('crew_female_settings.json').read_text())[NAME]
OUT=ROOT/'Art/Models/CrewV2'/NAME
PRE=OUT/'iterations'/args.revision
PRE.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
random.seed(42)
def curves(action):
    return list(action.layers[0].strips[0].channelbag(action.slots[0]).fcurves)


def signature(arm):
    bones = {b.name: {'parent': b.parent.name if b.parent else None,
                     'head': list(b.head_local), 'tail': list(b.tail_local),
                     'matrix': [list(r) for r in b.matrix_local],
                     'deform': b.use_deform} for b in arm.data.bones}
    actions = {}
    for a in bpy.data.actions:
        channels = [(f.data_path, f.array_index,
                     [(tuple(p.co), p.interpolation, tuple(p.handle_left),
                       tuple(p.handle_right)) for p in f.keyframe_points])
                    for f in curves(a)]
        actions[a.name] = {'range': list(a.frame_range), 'curves': len(channels),
                           'sha256': hashlib.sha256(json.dumps(channels, sort_keys=True).encode()).hexdigest()}
    return {'bones': bones, 'actions': actions}


bpy.ops.wm.open_mainfile(filepath=str(ORIGINAL))
scene = bpy.context.scene
arm = bpy.data.objects['CrewRig']
baseline = signature(arm)
original_hash = hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()
(OUT/'rig-contract.json').write_text(json.dumps({'original_sha256': original_hash, **baseline}, indent=2)+'\n')
for action in bpy.data.actions:
    action.use_fake_user = True
for ob in list(bpy.data.objects):
    if ob != arm:
        bpy.data.objects.remove(ob, do_unlink=True)
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.render.fps = 24
arm.animation_data.action = None
for p in arm.pose.bones:
    p.matrix_basis.identity()
bpy.context.view_layer.update()
col = arm.users_collection[0]
col.name = 'FEMALE_EXPORT'

PALETTE = {
    'M_HullNavy': '#173F57', 'M_HullBlue': '#2A6685',
    'M_RailIvory': '#F3F0DC', 'M_OilskinYellow': '#E6AD38',
    'M_Rubber': '#28343B', 'M_Steel': '#8FA6AC',
    'M_SkinCrew': '#F29A52', 'M_SkinCrewShadow': '#CE7B47',
    'M_HairCrew': '#48271D', 'M_HairCrewLight': '#633727',
    'M_HairCrewDeep': '#321E19', 'M_EyeCrew': '#07141F',
    'M_CoatCrew': '#103F70', 'M_CoatCrewEdge': '#225681',
    'M_VisorCrew': '#102D4A', 'M_BrassCrew': '#DF9A24',
    'M_BrassCrewLight': '#F7C754', 'M_LeatherCrew': '#74472C',
    'M_BinocularCrew': '#213343', 'M_LensCrew': '#168FBE',
    'M_LensCrewLight': '#51C9E5', 'M_SoleCrew': '#142B3C',
}


def linear(c):
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


mats = {}
PALETTE.update({'M_SkinCrew': CFG['skin'], 'M_SkinCrewShadow': CFG['shadow'], 'M_HairCrew': CFG['hair'], 'M_HairCrewLight': CFG['hairlight'], 'M_HairCrewDeep': CFG['hairdeep'], 'M_Beanie': '#144C86' if CFG['role']=='Fisher' else '#E36A35', 'M_BeanieLight': '#225E99' if CFG['role']=='Fisher' else '#F68240', 'M_Apron': '#168F9F', 'M_ApronEdge': '#39A7AE', 'M_SafetyOrange': '#E36A35', 'M_Skin': CFG['skin'], 'M_HardHat': '#F2BB24'})
PALETTE['M_KnitNavy']='#173F57'
PALETTE['M_LipCrew']=CFG.get('lip','#B75A48')
PALETTE['M_BrowCrew']=CFG.get('brow',CFG['hairdeep'])
PALETTE['M_NoseWarm']='#F18D56' if CFG['age'] else '#F4995E'
for name, hx in PALETTE.items():
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    rgb = tuple(linear(int(hx[i:i+2], 16) / 255) for i in (1, 3, 5))
    mat.diffuse_color = (*rgb, 1)
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb, 1)
    bs.inputs['Roughness'].default_value = .78
    bs.inputs['Specular IOR Level'].default_value = .22
    if 'Brass' in name:
        bs.inputs['Metallic'].default_value = .38
        bs.inputs['Roughness'].default_value = .31
    if name == 'M_EyeCrew':
        bs.inputs['Roughness'].default_value = .36
        bs.inputs['Specular IOR Level'].default_value = .16
    if 'Lens' in name:
        bs.inputs['Roughness'].default_value = .2
        bs.inputs['Metallic'].default_value = .25
    if 'HairCrew' in name:
        bs.inputs['Roughness'].default_value = .57
        bs.inputs['Specular IOR Level'].default_value = .27
    if name in ('M_Apron','M_ApronEdge','M_SafetyOrange'):
        bs.inputs['Roughness'].default_value = .56
        bs.inputs['Specular IOR Level'].default_value = .28
    mats[name] = mat


class Mesh:
    def __init__(self):
        self.v, self.f, self.mi, self.w = [], [], [], []
        self.materials = []
        self.quality = .80

    def add(self, verts, faces, mat, bone, weights=None):
        n = len(self.v)
        if mat not in self.materials:
            self.materials.append(mat)
        self.v.extend([tuple(v) for v in verts])
        self.f.extend([tuple(n+i for i in f) for f in faces])
        self.mi.extend([self.materials.index(mat)] * len(faces))
        self.w.extend(weights if weights else [{bone: 1.0} for _ in verts])

    def ell(self, c, r, mat, bone, seg=16, rings=8, rot=0):
        seg = max(10, round(seg*self.quality))
        rings = max(6, round(rings*self.quality))
        # Single pole vertices: no degenerate triangles or disconnected normals.
        v = [(c[0], c[1], c[2]+r[2])]
        for j in range(1, rings):
            a = math.pi * j / rings
            for i in range(seg):
                t = math.tau * i / seg
                x, y = r[0]*math.sin(a)*math.cos(t), r[1]*math.sin(a)*math.sin(t)
                v.append((c[0]+x*math.cos(rot)-y*math.sin(rot),
                          c[1]+x*math.sin(rot)+y*math.cos(rot), c[2]+r[2]*math.cos(a)))
        v.append((c[0], c[1], c[2]-r[2]))
        f = [(0, 1+i, 1+(i+1) % seg) for i in range(seg)]
        for j in range(rings-2):
            for i in range(seg):
                a, b = 1+j*seg+i, 1+j*seg+(i+1) % seg
                f.append((a, b, b+seg, a+seg))
        f += [(len(v)-1, 1+(rings-2)*seg+(i+1) % seg,
               1+(rings-2)*seg+i) for i in range(seg)]
        self.add(v, f, mat, bone)

    def sweep(self, path, radii, mat, bone, sides=8, up=(0, 1, 0), weights=None):
        path = [Vector(p) for p in path]
        v = []
        for j, p in enumerate(path):
            d = (path[min(j+1, len(path)-1)] - path[max(0, j-1)]).normalized()
            u = Vector(up).cross(d).normalized()
            if u.length < .5:
                u = Vector((1, 0, 0)).cross(d).normalized()
            vv = d.cross(u).normalized()
            rr = radii[j] if isinstance(radii, list) else radii
            rx, ry = rr if isinstance(rr, tuple) else (rr, rr)
            for i in range(sides):
                a = math.tau*i/sides
                v.append(p + rx*math.cos(a)*u + ry*math.sin(a)*vv)
        f = [tuple(reversed(range(sides)))]
        for j in range(len(path)-1):
            for i in range(sides):
                a = j*sides+i
                b = j*sides+(i+1) % sides
                f.append((a, b, b+sides, a+sides))
        f.append(tuple((len(path)-1)*sides+i for i in range(sides)))
        ww = [weights[j] for j in range(len(path)) for _ in range(sides)] if weights else None
        self.add(v, f, mat, bone, ww)

    def patch(self, points, mat, bone, thickness=.003):
        # Closed bevelled tailoring pieces. Convex outline in front projection.
        centre = sum((Vector(p) for p in points), Vector()) / len(points)
        inside = [centre+(Vector(p)-centre)*.86+Vector((0, -thickness, 0)) for p in points]
        n = len(points)
        f = [tuple(range(n, n*2)), tuple(reversed(range(n)))]
        f += [(i, (i+1) % n, (i+1) % n+n, i+n) for i in range(n)]
        self.add(list(points)+inside, f, mat, bone)

    def object(self, name):
        data = bpy.data.meshes.new(name)
        shaped=[]
        for co,w in zip(self.v,self.w):
            region=region_for_weights(w)
            shaped.append(female_shape(co,region=region) if region else co)
        data.from_pydata(shaped, [], self.f)
        for mat in self.materials:
            data.materials.append(mats[mat])
        for p, i in zip(data.polygons, self.mi):
            p.material_index = i
            p.use_smooth = True
        bm = bmesh.new()
        bm.from_mesh(data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(data)
        bm.free()
        data.update()
        ob = bpy.data.objects.new(name, data)
        col.objects.link(ob)
        ob.parent = arm
        for bone in arm.data.bones:
            ob.vertex_groups.new(name=bone.name)
        for i, w in enumerate(self.w):
            for bone, weight in w.items():
                if weight > 0:
                    ob.vertex_groups[bone].add([i], weight, 'REPLACE')
        mod = ob.modifiers.new('OriginalCrewRig', 'ARMATURE')
        mod.object = arm
        return ob


def catmull(points, steps=3):
    p = [Vector(x) for x in points]
    out = []
    for j in range(len(p)-1):
        a, b, c, d = p[max(0, j-1)], p[j], p[j+1], p[min(j+2, len(p)-1)]
        for k in range(steps):
            t = k/steps
            out.append(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t))
    return out+[p[-1]]


def cord(g, points, r, mat, bone, steps=3, sides=6):
    g.sweep(catmull(points, steps), r, mat, bone, sides)


def lock(g, points, width, depth, light=False, ridge=True):
    p = catmull(points, 5)
    rr = []
    for i in range(len(p)):
        t = i/(len(p)-1)
        taper = min(1, .3+t*5, max(.045, (1-t)*5))
        rr.append((width*taper, depth*taper))
    g.sweep(p, rr, 'M_HairCrewLight' if light else 'M_HairCrew', 'Head', 10)
    if ridge:
        # Sculpted broad tonal ridge, following the front of each lock.
        q = [p[i]+Vector((0, -rr[i][1]*.87, .001)) for i in range(len(p))]
        # Two open strips are a broad sculpted groove/highlight, not extra tubes.
        vv = []
        for i, point in enumerate(q):
            vv += [point+Vector((-rr[i][0]*.025, 0, 0)),
                   point+Vector((rr[i][0]*.025, 0, 0))]
        g.add(vv, [(i*2, i*2+1, i*2+3, i*2+2) for i in range(len(q)-1)],
              'M_HairCrewLight', 'Head')


# Male head/flat torso use the original CrewRig proportions and attachment axes.
meshes=[]
profile=[(.580,.006,.008,.010),(.594,.052,.055,.054),(.612,.093,.084,.083),
         (.638,.125,.108,.107),(.672,.150,.132,.125),(.713,.168,.145,.140),
         (.755,.173,.151,.151),(.801,.171,.146,.155),(.842,.162,.134,.149),
         (.880,.144,.116,.131),(.914,.111,.087,.103),(.938,.067,.050,.060),
         (.950,.002,.002,.002)]
profile=[(z,rx*CFG.get('facewidth',1),fr,bk) for z,rx,fr,bk in profile]
face=Mesh(); face.quality=1
N=48
v=[(rx*math.cos(math.tau*i/N),math.sin(math.tau*i/N)*(fr if math.sin(math.tau*i/N)<0 else bk),z)
   for z,rx,fr,bk in profile for i in range(N)]
f=[tuple(reversed(range(N)))]+[(j*N+i,j*N+(i+1)%N,(j+1)*N+(i+1)%N,(j+1)*N+i)
   for j in range(len(profile)-1) for i in range(N)]+[tuple(range((len(profile)-1)*N,len(profile)*N))]
face.add(v,f,'M_SkinCrew','Head')
face.ell((0,0,.566),(.053,.045,.061),'M_SkinCrew','Neck',20,10)
for s in (-1,1):
    face.ell((s*.169,.001,.742),(.031,.026,.043),'M_SkinCrew','Head',22,12)
    face.ell((s*.180,-.020,.741),(.016,.009,.027),'M_SkinCrewShadow','Head',18,10)
    face.ell((s*.176,-.028,.734),(.009,.005,.014),'M_SkinCrew','Head',14,8)
nr=(.016,.021,.022) if CFG.get('adultface') else (.016,.018,.018) if CFG['age'] else (.013,.017,.016)
face.ell((-.004,-.145,.729),nr,'M_NoseWarm' if CFG.get('moustache') else 'M_SkinCrew','Head',24,14)
face_ob=face.object(NAME+'_Face'); meshes.append(face_ob)

def face_surface(x,z,lift=.0015):
    for a,b in zip(profile,profile[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]); rx,fr=(a[j]*(1-t)+b[j]*t for j in (1,2))
            return (x,-fr*math.sqrt(max(.01,1-(x/rx)**2))-lift,z)
    raise ValueError((x,z))

# UV skin has only authored colour/blush, never studio illumination.
def png_chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
tex_size=512; raw=bytearray()
base=tuple(int(CFG['skin'][i:i+2],16) for i in (1,3,5))
rosy=tuple(int(CFG['shadow'][i:i+2],16) for i in (1,3,5))
freckles=[(random.choice((-1,1))*random.uniform(.035,.125),random.uniform(.700,.738),random.uniform(.0008,.0017)) for _ in range(40)] if CFG.get('freckles') else []
for py in range(tex_size):
    raw.append(0); z=.98-(py+.5)/tex_size*.43
    for px in range(tex_size):
        x=-.21+(px+.5)/tex_size*.42
        blush=max(math.exp(-((x-cx)/.040)**2-((z-.714)/.030)**2) for cx in (-.12,.12))*CFG.get('blush',.25)
        colr=[round(base[i]*(1-blush)+rosy[i]*blush) for i in range(3)]
        if freckles:
            dot=max(math.exp(-((x-fx)/r)**2-((z-fz)/r)**2) for fx,fz,r in freckles)*.32
            colr=[round(c*(1-dot)+v*dot) for c,v in zip(colr,(168,82,43))]
        raw.extend(colr)
texture_path=OUT/(NAME+'_Face.png')
texture_path.write_bytes(b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',struct.pack('>IIBBBBB',512,512,8,2,0,0,0))+
    png_chunk(b'sRGB',b'\0')+png_chunk(b'IDAT',zlib.compress(bytes(raw),9))+png_chunk(b'IEND',b''))
skin_mat=mats['M_SkinCrew'].copy(); skin_mat.name=NAME+'_Face'
image=bpy.data.images.load(str(texture_path),check_existing=True)
node=skin_mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
skin_mat.node_tree.links.new(node.outputs['Color'],skin_mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
face_ob.data.materials[face.materials.index('M_SkinCrew')]=skin_mat
uv=face_ob.data.uv_layers.new(name=NAME+'_SkinUV')
for loop in face_ob.data.loops:
    co=face_ob.data.vertices[loop.vertex_index].co
    uv.data[loop.index].uv=((co.x+.21)/.42,(co.z-.55)/.43)

detail=Mesh();detail.quality=1
for sign in (-1,1):
    x=sign*CFG.get('eyespace',.064);z=CFG.get('eyez',.774)
    adult=CFG.get('adultface',False)
    if adult:
        detail.ell((x,-.142,z),(.033,.010,.034),'M_RailIvory','Head',28,18,sign*.12)
    eyey=-.151 if adult else -.144
    detail.ell((x-sign*.003 if adult else x,eyey,z),(CFG.get('eyewidth',.024),.011,CFG.get('eyeheight',.037)),'M_EyeCrew','Head',28,18,sign*.08)
    detail.ell((x-.006,eyey-.011,z+.015),(.0047,.0015,.007),'M_RailIvory','Head',16,10)
    # Sweeping upper lash and a compact pointed outer wing.
    cord(detail,[(x-sign*(.029 if adult else .020),-.145,z+.022),(x,-.154 if adult else -.150,z+.036),(x+sign*(.030 if adult else .021),-.143,z+.026),(x+sign*(.041 if adult else .032),-.130,z+.034)],.003 if adult else .0024,'M_EyeCrew','Head',3,6)
    points=[face_surface(sign*xx,zz,.002) for xx,zz in [(.030,.827),(.046,.837),(.069,.835),(.088,.826)]]
    path=catmull(points,4)
    detail.sweep(path,[(.003+(.0045 if adult else .003)*math.sin(math.pi*i/(len(path)-1)),.0026) for i in range(len(path))],'M_BrowCrew','Head',8)
    if CFG['age']:
        for j in range(3):
            cord(detail,[face_surface(sign*xx,zz,.001) for xx,zz in [(.096,.768-j*.011),(.111,.771-j*.011),(.123,.765-j*.011)]],.00085,'M_SkinCrewShadow','Head',3,5)
        cord(detail,[face_surface(sign*xx,zz,.0009) for xx,zz in [(.062,.704),(.074,.689),(.070,.678)]],.0008,'M_SkinCrewShadow','Head',3,5)
cord(detail,[face_surface(x,z,.0019) for x,z in [(-.042,.689),(-.024,.681),(.004,.680),(.031,.685),(.046,.695)]],.0022,'M_LipCrew' if CFG.get('adultface') else 'M_HairCrewDeep','Head',4,7)
cord(detail,[face_surface(x,z,.0015) for x,z in [(-.020,.677),(.004,.674),(.026,.680)]],.0016,'M_LipCrew','Head',3,6)
if CFG.get('adultface'):
    cord(detail,[face_surface(x,z,.0021) for x,z in [(-.034,.685),(-.017,.682),(.001,.679),(.020,.684),(.035,.691)]],.0042,'M_LipCrew','Head',4,8)
if CFG.get('scar'):
    cord(detail,[face_surface(x,z,.004) for x,z in [(.045,.851),(.052,.837),(.060,.821)]],.0022,'M_RailIvory','Head',3,5)
meshes.append(detail.object(NAME+'_Expression'))

# Hair is authored as nested, flattened, tapered locks with colour-only fibre UVs.
def strand(g,points,width,depth,mat='M_HairCrew',bone='Head',steps=4,sides=8,up=(0,1,0)):
    pts=catmull(points,steps);rr=[]
    for i in range(len(pts)):
        t=i/(len(pts)-1);taper=max(.025,min(1,.28+t*5,(1-t)*4))
        rr.append((width*taper,depth*taper))
    g.sweep(pts,rr,mat,bone,sides,up=up)
hair_ob,hair_texture_image=build_hair(Mesh,catmull,mats,CFG,NAME,OUT,png_chunk)
meshes.append(hair_ob)

def disk(g,c,radius,depth,mat,bone,seg=24):
    g.sweep([(c[0],c[1]+depth/2,c[2]),(c[0],c[1]-depth/2,c[2])],radius,mat,bone,seg,up=(0,0,1))

hat=Mesh();role=CFG['role']
def loft(g,rows,mat,bone='HatMount',n=48):
    vv=[(rx*math.cos(math.tau*i/n),ry*math.sin(math.tau*i/n),z) for z,rx,ry in rows for i in range(n)]
    ff=[tuple(reversed(range(n)))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i)
        for j in range(len(rows)-1) for i in range(n)]+[tuple(range((len(rows)-1)*n,len(rows)*n))]
    g.add(vv,ff,mat,bone)

if role in ('Fisher','Deckhand'):
    crown=[(.884,.174,.152),(.914,.178,.157),(.947,.172,.151),(.980,.155,.137),
           (1.007,.126,.112),(1.028,.088,.079),(1.040,.040,.036),(1.043,.001,.001)]
    loft(hat,crown,'M_Beanie')
    # Rolled cuff, clean continuous profile with fine low relief knit channels.
    cuff=[(.879,.171,.148),(.882,.183,.160),(.889,.186,.163),(.926,.185,.161),(.934,.178,.154)]
    loft(hat,cuff,'M_Beanie')
    for i in range(56):
        a=math.tau*i/56
        pts=[(rx*math.cos(a),ry*math.sin(a),z) for z,rx,ry in [(.885,.185,.162),(.895,.187,.164),(.917,.187,.163),(.930,.181,.157)]]
        cord(hat,pts,.0013,'M_BeanieLight','HatMount',2,5)
    for i in range(12):
        a=math.tau*i/12
        pts=[(rx*math.cos(a),ry*math.sin(a),z) for z,rx,ry in crown[1:-1]]
        cord(hat,pts,.0011,'M_BeanieLight','HatMount',2,5)
elif role=='Engineer':
    loft(hat,[(.895,.181,.157),(.936,.183,.159),(.977,.167,.146),(1.016,.128,.112),(1.039,.067,.058),(1.047,.002,.002)],'M_HardHat')
    loft(hat,[(.890,.204,.181),(.896,.208,.185),(.903,.204,.181),(.907,.184,.160)],'M_HardHat')
    # Raised safety crown strips, retaining one coherent helmet dome.
    for s in (-1,1):
        cord(hat,[(s*.083,-.137,.938),(s*.075,-.104,1.003),(s*.064,0,1.037),(s*.075,.106,1.001),(s*.083,.139,.934)],.005,'M_OilskinYellow','HatMount',4,7)
    # Same connected housing and fitted strap as the shared male Engineer kit.
    bv=[(rx*math.cos(math.tau*i/48),ry*math.sin(math.tau*i/48),z)
        for z,rx,ry in [(.914,.185,.164),(.918,.185,.164),(.935,.184,.163),(.939,.183,.162)] for i in range(48)]
    hat.add(bv,[(j*48+i,j*48+(i+1)%48,(j+1)*48+(i+1)%48,(j+1)*48+i) for j in range(3) for i in range(48)],'M_HullNavy','HatMount')
    lamp_rows=[(-.149,.021),(-.157,.032),(-.164,.036),(-.183,.035),(-.188,.031),(-.191,.028),(-.196,.027),(-.199,.024),(-.200,.001)]
    lv=[(rr*math.cos(math.tau*i/32),yy,.952+rr*math.sin(math.tau*i/32)) for yy,rr in lamp_rows for i in range(32)]
    lf=[tuple(reversed(range(32)))]+[(j*32+i,j*32+(i+1)%32,(j+1)*32+(i+1)%32,(j+1)*32+i) for j in range(len(lamp_rows)-1) for i in range(32)]
    lf.append(tuple(range((len(lamp_rows)-1)*32,len(lamp_rows)*32)))
    first=len(hat.f);hat.add(lv,lf,'M_HullNavy','HatMount')
    for mm in ('M_Steel','M_RailIvory'):
        if mm not in hat.materials:hat.materials.append(mm)
    for j in range(len(lamp_rows)-1):
        if j>=4:
            mi=hat.materials.index('M_Steel' if j<6 else 'M_RailIvory')
            for i in range(32):hat.mi[first+1+j*32+i]=mi
    hat.mi[-1]=hat.materials.index('M_RailIvory')
else:
    loft(hat,[(.899,.176,.151),(.934,.191,.163),(.971,.210,.175),(1.006,.200,.166),(1.032,.143,.120),(1.044,.001,.001)],'M_RailIvory')
    loft(hat,[(.890,.178,.153),(.919,.182,.157)],'M_HullNavy')
    # Projecting navy visor with a softly bevelled curved edge.
    vv=[];count=28
    for zoff in (0,-.008):
        for r in (.15,.188,.225):
            for i in range(count):
                a=-1.32+2.64*i/(count-1)
                vv.append((math.sin(a)*r,-math.cos(a)*r,.899-.018*(r-.15)/.075+.018*math.sin(a)**2+zoff))
    ff=[(l+j*count+i,l+j*count+i+1,l+(j+1)*count+i+1,l+(j+1)*count+i)
        for l in (0,count*3) for j in range(2) for i in range(count-1)]
    ff += [(2*count+i,2*count+i+1,5*count+i+1,5*count+i) for i in range(count-1)]
    hat.add(vv,ff,'M_VisorCrew','HatMount')
    cord(hat,[(-.166,-.063,.921),(-.121,-.132,.925),(0,-.165,.927),(.121,-.132,.925),(.166,-.063,.921)],.004,'M_BrassCrew','HatMount',5,8)
    disk(hat,(0,-.174,.973),.034,.010,'M_BrassCrew','HatMount',32)
    disk(hat,(0,-.182,.973),.028,.006,'M_HullNavy','HatMount',32)
    # Explicit anchor: eye, shank, crossbar, curved flukes.
    pts=[(.005*math.cos(math.tau*i/16),-.188,.989+.005*math.sin(math.tau*i/16)) for i in range(17)]
    hat.sweep(pts,.0022,'M_BrassCrewLight','HatMount',6)
    cord(hat,[(0,-.188,.984),(0,-.188,.954)],.0028,'M_BrassCrewLight','HatMount',1,7)
    cord(hat,[(-.012,-.188,.979),(.012,-.188,.979)],.0022,'M_BrassCrewLight','HatMount',1,6)
    cord(hat,[(-.018,-.188,.966),(-.014,-.188,.956),(0,-.188,.951),(.014,-.188,.956),(.018,-.188,.966)],.0027,'M_BrassCrewLight','HatMount',3,6)
    for s in (-1,1): disk(hat,(s*.166,-.067,.922),.008,.005,'M_BrassCrew','HatMount',16)
meshes.append(hat.object(NAME+'_Hat'))

# Flat male body: original .15m shoulder centre, .085m leg centres, .95m scalp.
body=Mesh();body.quality=.85
base_mat='M_HullBlue' if role=='Engineer' else 'M_CoatCrew' if role=='Captain' else 'M_KnitNavy'
torso=[(.289,.134,.093),(.313,.141,.097),(.371,.140,.099),(.432,.141,.098),(.491,.146,.086),(.529,.131,.070),(.549,.064,.047)]
tv=[];tw=[];n=36
for z,rx,ry in torso:
    for i in range(n):
        a=math.tau*i/n;tv.append((rx*math.cos(a),ry*math.sin(a),z))
        t=max(0,min(1,(z-.32)/.19));tw.append({'Hips':1-t,'Spine1':t})
tf=[tuple(reversed(range(n)))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(torso)-1) for i in range(n)]
tf.append(tuple(range((len(torso)-1)*n,len(torso)*n)))
body.add(tv,tf,base_mat,'Spine',tw)
if role=='Fisher':
    body.materials.append('M_OilskinYellow')
    for i in range(1+2*n):body.mi[i]=body.materials.index('M_OilskinYellow')
def torso_surface(x,z,lift=.003,back=False):
    for a,b in zip(torso,torso[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);rx,ry=(a[i]*(1-t)+b[i]*t for i in (1,2))
            return (x,(1 if back else -1)*(ry*math.sqrt(max(.01,1-(x/rx)**2))+lift),z)
    return (x,-.06-lift,z)

for s in (-1,1):
    side='Left' if s>0 else 'Right'
    xx=[.085,.099,.12,.15,.18,.21,.24,.265,.28,.30,.33,.36,.38,.393]
    rr=[.003,.034,.052,.058,.056,.054,.051,.049,.048,.047,.044,.041,.039,.038]
    ww=[]
    for x in xx:
        t=max(0,min(1,(x-.205)/.15));t=t*t*(3-2*t);ww.append({side+'Arm':1-t,side+'ForeArm':t})
    start=len(body.f)
    body.sweep([(s*x,0,.51) for x in xx],rr,base_mat,side+'Arm',20,up=(0,0,1),weights=ww)
    cuffmat='M_SafetyOrange' if role=='Deckhand' else 'M_CoatCrewEdge' if role=='Captain' else base_mat
    if cuffmat not in body.materials: body.materials.append(cuffmat)
    for i in range(start+1+(len(xx)-3)*20,len(body.f)): body.mi[i]=body.materials.index(cuffmat)
    handmat='M_SafetyOrange' if role=='Deckhand' else 'M_SkinCrew'
    body.ell((s*.426,-.001,.510),(.043,.038,.037),handmat,side+'Hand',20,12)
    body.ell((s*.408,-.032,.485),(.020,.020,.020),handmat,side+'Hand',16,8)
    legmat='M_OilskinYellow' if role=='Fisher' else base_mat
    zs=[.317,.280,.235,.200,.180,.157,.126,.090];rads=[.067,.065,.060,.055,.053,.051,.048,.046]
    lw=[{side+'UpLeg':1-max(0,min(1,(.207-z)/.065)),side+'Leg':max(0,min(1,(.207-z)/.065))} for z in zs]
    body.sweep([(s*.085,0,z) for z in zs],rads,legmat,side+'UpLeg',18,weights=lw)
    # Coherent bevelled rubber boots: sole/toe/shaft in one surface.
    br=[(0,-.028,.046,.075),(.008,-.030,.060,.096),(.019,-.032,.065,.103),(.041,-.033,.064,.102),
        (.065,-.027,.059,.090),(.088,-.010,.050,.066),(.116,0,.049,.051),(.124,0,.049,.051)]
    bv=[(s*.085+rx*math.cos(math.tau*i/28),cy+ry*math.sin(math.tau*i/28),z) for z,cy,rx,ry in br for i in range(28)]
    bf=[(j*28+i,j*28+(i+1)%28,(j+1)*28+(i+1)%28,(j+1)*28+i) for j in range(len(br)-1) for i in range(28)]
    bf += [tuple(reversed(range(28))),tuple(range((len(br)-1)*28,len(br)*28))]
    start=len(body.f);body.add(bv,bf,'M_VisorCrew',side+'Foot')
    if 'M_SoleCrew' not in body.materials:body.materials.append('M_SoleCrew')
    for i in range(start,start+56):body.mi[i]=body.materials.index('M_SoleCrew')
    # Oilskin seam and cuff rim retain readable practical clothing construction.
    cord(body,[(s*.134,.003,.125),(s*.137,.002,.175),(s*.146,.002,.240),(s*.151,.002,.290)],.0013,
         'M_BrassCrew' if role=='Fisher' else 'M_CoatCrewEdge',side+'UpLeg',2,5)

garment=Mesh();garment.quality=.8
if role=='Fisher':
    gm='M_OilskinYellow' if role=='Fisher' else 'M_Apron';edge='M_BrassCrewLight' if role=='Fisher' else 'M_ApronEdge'
    # Fitted bib front as a curved patch (not a rigid flat box).
    rows=[(.297,.130),(.358,.125),(.419,.107),(.475,.099)]
    if role=='Deckhand':rows=[(.205,.151),(.222,.158),(.290,.153),(.358,.140),(.419,.107),(.475,.099)]
    gv=[];gw=[];cols=13
    for z,width in rows:
        for i in range(cols):
            x=-width+2*width*i/(cols-1)
            if z<.289:y=-.109-.006*math.cos(x*20)
            else:y=torso_surface(x,z,.007)[1]
            gv.append((x,y,z));t=max(0,min(1,(z-.32)/.19));gw.append({'Hips':1-t,'Spine1':t})
    gf=[(j*cols+i,j*cols+i+1,(j+1)*cols+i+1,(j+1)*cols+i) for j in range(len(rows)-1) for i in range(cols-1)]
    if role=='Deckhand':
        # 3 mm closed rubber apron: visible side/back edge, no paper-thin sheet.
        count=len(gv)
        gv=gv+[(x,y+.003,z) for x,y,z in gv]
        gw=gw+gw
        gf=gf+[tuple(count+i for i in reversed(f)) for f in gf]
        border=list(range(cols))+[j*cols+cols-1 for j in range(1,len(rows))]
        border+=list(range((len(rows)-1)*cols+cols-2,(len(rows)-1)*cols-1,-1))
        border+=[j*cols for j in range(len(rows)-2,0,-1)]
        gf += [(a,b,b+count,a+count) for a,b in zip(border,border[1:]+border[:1])]
    garment.add(gv,gf,gm,'Spine',gw)
    for s in (-1,1):
        # Wide shoulder straps continue over shoulder and cross on the back.
        path=[torso_surface(s*.075,.458,.010),torso_surface(s*.087,.510,.010),
              (s*.090,-.048,.545),(s*.085,.020,.550),torso_surface(s*.060,.501,.009,True),
              torso_surface(-s*.025,.360,.009,True)]
        pts=catmull(path,3)
        weights=[]
        for pt in pts:
            t=max(0,min(1,(pt.z-.32)/.19));weights.append({'Hips':1-t,'Spine1':t})
        garment.sweep(pts,(.013,.004),gm,'Spine1',8,up=(0,1,0),weights=weights)
        # Rectangular buckles with actual open centre and metal slider.
        x=s*.076;z=.472;y=torso_surface(x,z,.015)[1]
        cord(garment,[(x-.014,y,z-.012),(x-.014,y,z+.012),(x+.014,y,z+.012),(x+.014,y,z-.012),(x-.014,y,z-.012)],.003,
             'M_BrassCrew' if role=='Fisher' else 'M_Steel','Spine1',1,6)
        cord(garment,[(x-.011,y-.001,z),(x+.011,y-.001,z)],.002,gm,'Spine1',1,5)
        cord(garment,[torso_surface(s*x,z,.009) for x,z in [(.095,.459),(.118,.414),(.130,.361)]],.0012,edge,'Spine1',3,5)
    # Front utility pocket, top welt and inset stitching.
    z0=.345 if role=='Fisher' else .324
    pp=[torso_surface(x,z,.012) for x,z in [(-.048,z0+.042),(.048,z0+.042),(.046,z0),(-.046,z0)]]
    garment.patch(pp,gm,'Spine',.001)
    cord(garment,[torso_surface(x,z0+.042,.015) for x in [-.047,0,.047]],.0016,edge,'Spine',3,5)
    for s in (-1,1):disk(garment,(s*.045,torso_surface(s*.045,z0+.036,.014)[1],z0+.036),.0025,.002,'M_BrassCrew','Spine',10)
    # Rib-knit neck ring, cuffs, fine sleeve channels; same original body profile.
    collar=[(.531,.071,.056),(.540,.070,.057),(.562,.059,.050),(.570,.057,.049)]
    loft(garment,collar,'M_KnitNavy','Neck',32)
    rib_count=20 if role=='Deckhand' else 28
    for i in range(rib_count):
        a=math.tau*i/rib_count
        cord(garment,[(rx*math.cos(a),ry*math.sin(a),z) for z,rx,ry in collar[1:-1]],.0007,'M_CoatCrewEdge','Neck',3,5)
    for s in (-1,1):
        side='Left' if s>0 else 'Right'
        for i in range(8):
            a=math.pi*1.05+math.pi*.9*i/7
            # Arm only above elbow, fine longitudinal low relief knit.
            cord(garment,[(s*x,r*math.cos(a),.51+r*math.sin(a)) for x,r in [(.145,.0575),(.19,.0545),(.205,.0535)]],
                 .0005,'M_CoatCrewEdge',side+'Arm',3,5)
elif role=='Deckhand':
    gm='M_OilskinYellow' if role=='Fisher' else 'M_Apron';edge='M_BrassCrewLight' if role=='Fisher' else 'M_ApronEdge'
    def bib_surface(x,z,lift=0):
        if role=='Deckhand':
            y=(-.125+.008*(x/.16)**2) if z<.30 else min(torso_surface(x,z,.014)[1],-.105+.013*(x/.16)**2)
        else:y=torso_surface(x,z,.007)[1]
        return (x,y-lift,z)
    # Fitted bib front as a curved patch (not a rigid flat box).
    rows=[(.297,.130),(.358,.125),(.419,.107),(.475,.099)]
    if role=='Deckhand':rows=[(.205,.151),(.222,.158),(.290,.153),(.358,.140),(.419,.107),(.475,.099)]
    gv=[];gw=[];cols=13
    for z,width in rows:
        for i in range(cols):
            x=-width+2*width*i/(cols-1)
            y=bib_surface(x,z)[1]
            gv.append((x,y,z));t=max(0,min(1,(z-.32)/.19));gw.append({'Hips':1-t,'Spine1':t})
    gf=[(j*cols+i,j*cols+i+1,(j+1)*cols+i+1,(j+1)*cols+i) for j in range(len(rows)-1) for i in range(cols-1)]
    if role=='Deckhand':
        # 3 mm closed rubber apron: visible side/back edge, no paper-thin sheet.
        count=len(gv)
        gv=gv+[(x,y+.003,z) for x,y,z in gv]
        gw=gw+gw
        gf=gf+[tuple(count+i for i in reversed(f)) for f in gf]
        border=list(range(cols))+[j*cols+cols-1 for j in range(1,len(rows))]
        border+=list(range((len(rows)-1)*cols+cols-2,(len(rows)-1)*cols-1,-1))
        border+=[j*cols for j in range(len(rows)-2,0,-1)]
        gf += [(a,b,b+count,a+count) for a,b in zip(border,border[1:]+border[:1])]
    garment.add(gv,gf,gm,'Spine',gw)
    if role=='Deckhand':
        loft(garment,[(.347,.147,.106),(.366,.147,.106)],gm,'Hips',32)
    for s in (-1,1):
        # Wide shoulder straps continue over shoulder and cross on the back.
        path=[bib_surface(s*.075,.458,.003) if role=='Deckhand' else torso_surface(s*.075,.458,.010),torso_surface(s*.087,.510,.010),
              (s*.090,-.048,.545),(s*.085,.020,.550),torso_surface(s*.060,.501,.009,True),
              torso_surface(-s*.025,.360,.009,True)]
        pts=catmull(path,3)
        weights=[]
        for pt in pts:
            t=max(0,min(1,(pt.z-.32)/.19));weights.append({'Hips':1-t,'Spine1':t})
        garment.sweep(pts,(.013,.004),gm,'Spine1',8,up=(0,1,0),weights=weights)
        # Rectangular buckles with actual open centre and metal slider.
        x=s*.076;z=.472;y=torso_surface(x,z,.015)[1]
        if role=='Deckhand':y=bib_surface(x,z,.007)[1]
        cord(garment,[(x-.014,y,z-.012),(x-.014,y,z+.012),(x+.014,y,z+.012),(x+.014,y,z-.012),(x-.014,y,z-.012)],.003,
             'M_BrassCrew' if role=='Fisher' else 'M_Steel','Spine1',1,6)
        cord(garment,[(x-.011,y-.001,z),(x+.011,y-.001,z)],.002,gm,'Spine1',1,5)
        cord(garment,[(bib_surface(s*x,z,.002) if role=='Deckhand' else torso_surface(s*x,z,.009))
                     for x,z in [(.095,.459),(.118,.414),(.130,.361)]],.0012,edge,'Spine1',3,5)
    # Front utility pocket, top welt and inset stitching.
    z0=.345 if role=='Fisher' else .324
    pp=[bib_surface(x,z,.005) for x,z in [(-.048,z0+.042),(.048,z0+.042),(.046,z0),(-.046,z0)]]
    if role=='Deckhand':
        pvs=[];pws=[];pxs=[-.048,-.024,0,.024,.048]
        for zz in [z0,z0+.021,z0+.042]:
            for xx in pxs:
                pvs.append(bib_surface(xx,zz,.006))
                t=max(0,min(1,(zz-.32)/.19));pws.append({'Hips':1-t,'Spine1':t})
        pfs=[(j*5+i,j*5+i+1,(j+1)*5+i+1,(j+1)*5+i) for j in range(2) for i in range(4)]
        garment.add(pvs,pfs,gm,'Spine',pws)
        for s in (-1,1):
            cord(garment,[bib_surface(s*.046,zz,.007) for zz in [z0,z0+.021,z0+.04]],.001,edge,'Spine',2,5)
    else:garment.patch(pp,gm,'Spine',.001)
    cord(garment,[bib_surface(x,z0+.042,.008) for x in [-.047,0,.047]],.0016,edge,'Spine',3,5)
    for s in (-1,1):disk(garment,(s*.045,bib_surface(s*.045,z0+.036,.007)[1],z0+.036),.0025,.002,'M_BrassCrew','Spine',10)
    # Rib-knit neck ring, cuffs, fine sleeve channels; same original body profile.
    collar=[(.531,.071,.056),(.540,.070,.057),(.562,.059,.050),(.570,.057,.049)]
    loft(garment,collar,'M_KnitNavy','Neck',32)
    rib_count=20 if role=='Deckhand' else 28
    for i in range(rib_count):
        a=math.tau*i/rib_count
        cord(garment,[(rx*math.cos(a),ry*math.sin(a),z) for z,rx,ry in collar[1:-1]],.0007,'M_CoatCrewEdge','Neck',3,5)
    for s in (-1,1):
        side='Left' if s>0 else 'Right'
        for i in range(8):
            a=math.pi*1.05+math.pi*.9*i/7
            # Arm only above elbow, fine longitudinal low relief knit.
            cord(garment,[(s*x,r*math.cos(a),.51+r*math.sin(a)) for x,r in [(.145,.0575),(.19,.0545),(.205,.0535)]],
                 .0005,'M_CoatCrewEdge',side+'Arm',3,5)
elif role=='Engineer':
    for s in (-1,1):
        # Cream braces and calf/sleeve bands are geometry with original weights.
        for back in (False,True):
            vv=[];ww=[]
            for zz in (.387,.427,.467,.504,.528):
                for xx in (.068,.092):
                    vv.append(torso_surface(s*xx,zz,.004,back))
                    t=max(0,min(1,(zz-.32)/.19));ww.append({'Hips':1-t,'Spine1':t})
            garment.add(vv,[(j*2,j*2+1,j*2+3,j*2+2) for j in range(4)],'M_RailIvory','Spine1',ww)
        side='Left' if s>0 else 'Right'
        vv=[];ww=[]
        for xx,rr in ((.317,.0472),(.341,.0448)):
            t=max(0,min(1,(xx-.205)/.15));t=t*t*(3-2*t)
            for i in range(24):
                a=math.tau*i/24;vv.append((s*xx,rr*math.cos(a),.51+rr*math.sin(a)))
                ww.append({side+'Arm':1-t,side+'ForeArm':t})
        garment.add(vv,[(i,(i+1)%24,24+(i+1)%24,24+i) for i in range(24)],'M_RailIvory',side+'ForeArm',ww)
        loftrows=[(.141,.053,.053),(.157,.054,.054)]
        vv=[(s*.085+rx*math.cos(math.tau*i/24),ry*math.sin(math.tau*i/24),z) for z,rx,ry in loftrows for i in range(24)]
        garment.add(vv,[(i,(i+1)%24,24+(i+1)%24,24+i) for i in range(24)],'M_RailIvory',side+'Leg')
    # Tool belt: continuous leather, two shaped pouches, steel open-jaw wrench.
    loft(garment,[(.331,.145,.106),(.358,.145,.107)],'M_LeatherCrew','Hips',40)
    for s in (-1,1):
        garment.ell((s*.102,-.080,.322),(.034,.028,.038),'M_LeatherCrew','Hips',20,12)
        disk(garment,(s*.091,-.106,.334),.004,.003,'M_BrassCrew','Hips',12)
    cord(garment,[(.105,-.114,.323),(.105,-.114,.415)],.006,'M_Steel','Hips',1,8)
    cord(garment,[(.087,-.114,.428),(.087,-.114,.410),(.105,-.114,.403),(.124,-.114,.410),(.124,-.114,.428)],.007,'M_Steel','Hips',2,8)
    # Coverall collar and zipper.
    for s in (-1,1):garment.patch([torso_surface(s*x,z,.006) for x,z in [(.025,.541),(.089,.529),(.063,.476)]],'M_HullBlue','Spine1',.002)
    cord(garment,[(0,-.101,.37),(0,-.103,.447),(0,-.080,.509)],.0017,'M_Steel','Spine1',3,5)
else:
    # White shirt, navy tie, tailored lapels, double-breasted buttons.
    garment.patch([torso_surface(x,z,.004) for x,z in [(-.052,.538),(.052,.538),(0,.450)]],'M_RailIvory','Spine1',.002)
    garment.patch([torso_surface(x,z,.009) for x,z in [(0,.527),(.012,.512),(.006,.465),(0,.451),(-.008,.468),(-.012,.512)]],'M_HullNavy','Spine1',.001)
    for s in (-1,1):
        garment.patch([torso_surface(s*x,z,.011) for x,z in [(.045,.547),(.113,.520),(.088,.486),(.111,.478),(.040,.405),(.052,.493)]],
                      'M_CoatCrew','Spine1',.002)
        cord(garment,[torso_surface(s*x,z,.014) for x,z in [(.045,.545),(.087,.487),(.041,.407)]],.0011,'M_CoatCrewEdge','Spine1',2,5)
        for z in (.337,.385,.433):disk(garment,(s*.047,torso_surface(s*.047,z,.012)[1],z),.0075,.006,'M_BrassCrew','Spine1' if z>.35 else 'Hips',18)
        side='Left' if s>0 else 'Right'
        # Epaulettes atop T-pose upper arms, move with original arm action.
        garment.patch([(s*.124,-.035,.566),(s*.185,-.035,.566),(s*.185,.033,.566),(s*.124,.033,.566)],'M_BrassCrew',side+'Arm',.003)
        for j in range(3):
            cord(garment,[(s*(.134+j*.016),-.032,.570),(s*(.134+j*.016),.031,.570)],.003,'M_RailIvory',side+'Arm',1,5)
        for x in (.352,.365):
            pts=[(s*x,.043*math.cos(math.tau*i/20),.51+.043*math.sin(math.tau*i/20)) for i in range(21)]
            garment.sweep(pts,.0025,'M_BrassCrew',side+'ForeArm',6,up=(1,0,0))
meshes.append(body.object(NAME+'_FemaleBody'))
meshes.append(garment.object(NAME+'_OutfitDetails'))

# Commit topology in rest pose and preserve skinning. All parts stay <=20k total.
budgets={NAME+'_Face':2200,NAME+'_Expression':1600,NAME+'_Hair':8500,
         NAME+'_Hat':2200,NAME+'_FemaleBody':3000,NAME+'_OutfitDetails':2450}
if role=='Engineer':budgets.update({NAME+'_Hat':2900,NAME+'_Hair':7800})
assert signature(arm)==baseline
for ob in meshes:
    if ob.name in (NAME+'_Hat',NAME+'_FemaleBody'):
        bpy.context.view_layer.objects.active=ob
        smooth=ob.modifiers.new('SculptSofteningBindPose','SUBSURF');smooth.levels=1
        bpy.ops.object.modifier_move_up(modifier=smooth.name);bpy.ops.object.modifier_apply(modifier=smooth.name)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    # Collapse decimation's material delimit option only affects planar mode.
    # Explicitly disconnect material boundaries to keep tailoring edges planar.
    borders=[e for e in bm.edges if len(e.link_faces)==2 and e.link_faces[0].material_index!=e.link_faces[1].material_index]
    if borders:bmesh.ops.split_edges(bm,edges=borders)
    tiny=[f for f in bm.faces if f.calc_area()<1e-10]
    if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
    bm.normal_update();bm.to_mesh(ob.data);bm.free();ob.data.validate(clean_customdata=False)
    ob.data.calc_loop_triangles();before=len(ob.data.loop_triangles)
    if before>budgets[ob.name]:
        bpy.context.view_layer.objects.active=ob
        mod=ob.modifiers.new('BindTopologyBudget','DECIMATE');mod.ratio=budgets[ob.name]/before
        mod.delimit={'MATERIAL','SEAM'}
        bpy.ops.object.modifier_move_up(modifier=mod.name);bpy.ops.object.modifier_apply(modifier=mod.name)
    bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    tiny=[f for f in bm.faces if f.calc_area()<1e-10]
    if tiny:bmesh.ops.delete(bm,geom=tiny,context='FACES_ONLY')
    bm.normal_update();bm.to_mesh(ob.data);bm.free();ob.data.validate(clean_customdata=False)
    ob.data.calc_loop_triangles()
    for poly in ob.data.polygons:poly.use_smooth=True
    for vert in ob.data.vertices:
        total=sum(g.weight for g in vert.groups)
        assert total>0
        for g in list(vert.groups):ob.vertex_groups[g.group].add([vert.index],g.weight/total,'REPLACE')
    print('PART TRIANGLES',ob.name,before,len(ob.data.loop_triangles),flush=True)
triangles=sum(len(ob.data.loop_triangles) for ob in meshes)
assert triangles<=20000,triangles
for ob in meshes:
    for vert in ob.data.vertices:assert abs(sum(g.weight for g in vert.groups)-1)<1e-5
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True)
for ob in meshes:ob.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(filepath=str(OUT/(NAME+'.fbx')),use_selection=True,
    object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',global_scale=1,
    apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=True,
    bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,
    bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,
    bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,
    use_custom_props=True,mesh_smooth_type='FACE',path_mode='RELATIVE')
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_set(1)
stats={'name':NAME,'role':role,'revision':args.revision,'original_sha256':original_hash,'contract':baseline,
       'triangles':triangles,'meshes':{o.name:len(o.data.loop_triangles) for o in meshes},
       'textures':[{'file':NAME+'_Face.png','size':[512,512],'use':'authored colour/blush, no baked lighting'}],
       'palette_srgb':PALETTE,'source_axes':'X right, -Y forward, Z up','bare_scalp_m':.95,
       'female_body':FEMALE_VERSION+'; same deformation field as approved Mira r16; original limb weights/attachment positions',
       'settings':CFG}
if hair_texture_image:
    stats['textures'].append({'file':NAME+'_Hair.png','size':[256,256],'use':'authored fine curl colour strands, no baked lighting'})
(OUT/'build-manifest.json').write_text(json.dumps(stats,indent=2)+'\n')

# Review-only studio; never included in the FBX selection.
studio=bpy.data.collections.new('REVIEW_STUDIO_not_exported');scene.collection.children.link(studio)
def area(name,location,energy,size,colour):
    light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='DISK';light.size=size;light.color=colour
    ob=bpy.data.objects.new(name,light);studio.objects.link(ob);ob.location=location
    ob.rotation_euler=(Vector((0,0,.65))-ob.location).to_track_quat('-Z','Y').to_euler()
scene.render.engine='CYCLES';scene.cycles.samples=args.samples;scene.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    if any(d.type=='OPTIX' for d in prefs.devices):
        for d in prefs.devices:d.use=d.type=='OPTIX'
        scene.cycles.device='GPU'
except Exception:pass
scene.world.use_nodes=True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.43,.47,.53,1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.45
area('Warm portrait key',(-2,-3,4),220,3,(1,.93,.83))
area('Cool fill',(3,-1,2),90,2.8,(.83,.91,1));area('Hair rim',(1,2,3),160,2.5,(1,.92,.80))
data=bpy.data.meshes.new('ReviewFloor');data.from_pydata([(-200,-200,-.004),(200,-200,-.004),(200,200,-.004),(-200,200,-.004)],[],[(0,1,2,3)])
ground=bpy.data.objects.new('ReviewFloor',data);studio.objects.link(ground)
mat=bpy.data.materials.new('Review warm grey');mat.use_nodes=True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.48,.46,.42,1)
mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85;data.materials.append(mat)
camera=bpy.data.objects.new('ReviewCamera',bpy.data.cameras.new('ReviewCamera'));studio.objects.link(camera);scene.camera=camera
camera.data.type='ORTHO';scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.render.resolution_percentage=100
def shot(name,angle=0,target=(0,0,.52),scale=1.17,size=(768,896),action='Idle',frame=1,elevated=.12):
    arm.animation_data.action=bpy.data.actions[action];scene.frame_set(frame)
    a=math.radians(angle);target=Vector(target)
    camera.location=target+Vector((math.sin(a)*3.4,-math.cos(a)*3.4,elevated))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    scene.render.resolution_x,scene.render.resolution_y=size;scene.render.filepath=str(PRE/(name+'.png'))
    bpy.ops.render.render(write_still=True)
target=Vector((0,0,.52));camera.location=target+Vector((1.54,-3.03,.22))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=1.17
scene.render.resolution_x=768;scene.render.resolution_y=896
image.filepath='//'+NAME+'_Face.png'
if hair_texture_image:hair_texture_image.filepath='//'+NAME+'_Hair.png'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(NAME+'.blend')),relative_remap=False)
if args.render!='none':
    shot('three-quarter',27,elevated=.22)
    shot('face',18,(0,-.018,.807),.53,(1024,1024),elevated=.03)
    shot('back-hair',155,(0,.035,.807),.62,(1024,1024),elevated=.05)
if args.render=='all':
    shot('front',0);shot('side',90);shot('back',180)
    shot('idle',22,action='Idle',frame=13);shot('walk',22,action='Walk',frame=7)
    shot('carry',25,action='Carry',frame=7);shot('cast',25,action='Cast',frame=17)
    # Same scale, same camera, same frame: original crew, approved r09 Mira, man.
    refs=[]
    for path,names,offset in [(ORIGINAL,['CrewRig','Body','Outfit_Captain','Hat_CaptainCap'],-.53),
                            (ROOT/'Art/Models/CrewV2/Mira-sol/Mira.blend',None,0)]:
        with bpy.data.libraries.load(str(path),link=False) as (src,dst):
            dst.objects=names if names else [n for n in src.objects if n=='CrewRig' or n.startswith('Mira_')]
        refarm=next(o for o in dst.objects if o.type=='ARMATURE')
        for ob in dst.objects:
            studio.objects.link(ob);ob.hide_render=False;ob.hide_viewport=False;ob.hide_set(False);refs.append(ob)
        refarm.location.x=offset;refarm.animation_data.action=bpy.data.actions['Idle']
    arm.location.x=.56
    shot('same-scale',0,(0,0,.53),2.18,(1800,1000))
    arm.location.x=0
    for ob in refs:bpy.data.objects.remove(ob,do_unlink=True)
    for action in list(bpy.data.actions):
        if action.name not in baseline['actions']:bpy.data.actions.remove(action)
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_set(1)
assert signature(arm)==baseline
assert hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()==original_hash
print('FEMALE BUILD COMPLETE',NAME,args.revision,triangles,'triangles',flush=True)


