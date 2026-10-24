"""CREW3D-MEN: authored male crew on the immutable original 20-bone CrewRig.
Utility topology/rig/export conventions adapted from read-only build_mira_sol.py.
Blender 5.2 --background --factory-startup --python this-file -- --name Pim --render quick|all|none.
No Assets, female sources, original rig, Unity or git writes.
"""
import argparse, bpy, bmesh, hashlib, json, math, sys, struct, zlib, random, os, time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
ORIGINAL=ROOT/'Art/Models/CrewRig/CrewRig.blend'
p=argparse.ArgumentParser()
p.add_argument('--name', choices=['Pim','Dirk','Kofi','Sam','Mats','Olaf','Captain'],required=True)
p.add_argument('--render',choices=['quick','all','none'],default='quick')
p.add_argument('--samples',type=int,default=32)
p.add_argument('--revision',default='r01')
args=p.parse_args(sys.argv[sys.argv.index('--')+1:])
NAME=args.name
CFG=json.loads(Path(__file__).with_name('crew_male_settings.json').read_text())[NAME]
OUT=ROOT/'Art/Models/CrewV2'/NAME
PRE=OUT/'iterations'/args.revision
PRE.mkdir(parents=True,exist_ok=True)
bpy.context.preferences.filepaths.save_version=0
random.seed(42)
def publish_staged(staged,target):
    # Windows indexing can briefly hold a completed delivery. Never truncate it.
    for attempt in range(12):
        try:
            os.replace(staged,target)
            return
        except OSError as exc:
            if exc.errno not in (13,22) and getattr(exc,'winerror',0) not in (5,32,33):raise
            if attempt==11:raise
            time.sleep(.5)
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
col.name = 'MALE_EXPORT'

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
PALETTE['M_KnitNavy']='#124574'
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
        data.from_pydata(self.v, [], self.f)
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
if NAME=='Captain':
    profile=[(z-(.006*(.75-z)/.17 if z<.75 else 0),rx*(1.04 if .595<=z<=.66 else .97 if z<.75 else 1),fr,bk) for z,rx,fr,bk in profile]
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
nr=(.026,.031,.020) if CFG['age'] or CFG.get('moustache') else (.013,.017,.016)
if NAME=='Captain':nr=(.012,.021,.017)
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
for py in range(tex_size):
    raw.append(0); z=.98-(py+.5)/tex_size*.43
    for px in range(tex_size):
        x=-.21+(px+.5)/tex_size*.42
        blush=max(math.exp(-((x-cx)/.040)**2-((z-.714)/.030)**2) for cx in (-.12,.12))*.25
        raw.extend(round(base[i]*(1-blush)+rosy[i]*blush) for i in range(3))
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

detail=Mesh();detail.quality=.9
for s in (-1,1):
    x=s*.062;z=.779 if CFG['age'] else .776
    # Oval eyes/glints match the men's simpler portrait expression, no lashes.
    detail.ell((x,-.142,z),(.019,.009,.031) if NAME=='Captain' else (.022,.010,.035),'M_EyeCrew','Head',24,14,s*.15)
    detail.ell((x-.006,-.151,z+.014),(.0045,.0016,.007),'M_RailIvory','Head',14,8)
    points=[face_surface(s*x,z,.002) for x,z in [(.030,.826),(.044,.834),(.068,.832),(.086,.823)]]
    path=catmull(points,4)
    detail.sweep(path,[(.004+.0035*math.sin(math.pi*i/(len(path)-1)),.003) for i in range(len(path))],
                 'M_HairCrewLight' if CFG['age'] else 'M_HairCrew','Head',8)
    if CFG['age']:
        for j in range(2):
            cord(detail,[face_surface(s*x,z,.0009) for x,z in [(.095,.765-j*.013),(.111,.769-j*.013),(.121,.765-j*.013)]],
                 .0008,'M_SkinCrewShadow','Head',3,5)
cord(detail,[face_surface(x,z) for x,z in [(-.043,.687),(-.026,.679),(.003,.679),(.031,.685),(.047,.695)]],
     .0022,'M_HairCrewDeep','Head',4,7)
meshes.append(detail.object(NAME+'_Expression'))

# Fine layered flattened locks. Width is tangential; depth remains shallow.
# Each lock has a controlled curved profile and ends in a real tapered point.
hair=Mesh();hair.quality=.8
curl_uv={};hair_texture_image=None
def strand(g,points,width,depth,mat='M_HairCrew',bone='Head',steps=4,sides=8,up=(0,1,0)):
    pts=catmull(points,steps);rr=[]
    for i in range(len(pts)):
        t=i/(len(pts)-1)
        taper=max(.025,min(1,.28+t*5,(1-t)*4))
        rr.append((width*taper,depth*taper))
    g.sweep(pts,rr,mat,bone,sides,up=up)

# Complete short-hair shell; lower open edge is covered by directional layers.
rows=[(.638,.121,.104),(.665,.151,.136),(.698,.170,.151),(.745,.178,.162),(.794,.178,.162),
      (.842,.166,.153),(.881,.146,.135),(.917,.107,.100),(.943,.044,.043)]
if CFG['style']=='short':rows=[(.674,.144,.127)]+rows[2:]
hn=48
def scalp_point(z,angle,lift=.004):
    for lower,upper in zip(profile,profile[1:]):
        if lower[0]<=z<=upper[0]:
            blend=(z-lower[0])/(upper[0]-lower[0])
            radius=lower[1]*(1-blend)+upper[1]*blend+lift
            depth_index=2 if math.sin(angle)<0 else 3
            depth=lower[depth_index]*(1-blend)+upper[depth_index]*blend+lift
            return Vector((radius*math.cos(angle),depth*math.sin(angle),z))
    raise ValueError(z)
hv=[]
for row_index,(z,rx,ry) in enumerate(rows):
    for index in range(hn):
        temple_limit=1.18 if NAME in ('Mats','Captain') else 1.10
        angle=-temple_limit+(math.pi+2*temple_limit)*index/(hn-1)
        lower_edge=(.780+.045*max(0,min(1,(-math.sin(angle)-.5)/.4)) if math.sin(angle)<0 else
                    max(rows[0][0],.780-.14*min(1,math.sin(angle)/.55)))
        zz=lower_edge+(z-rows[0][0])*(.943-lower_edge)/(.943-rows[0][0])
        if row_index==0:
            zz+=.004*math.sin(angle*17)
        hv.append(scalp_point(zz,angle,-.003 if row_index==0 else .009))
hf=[(j*hn+i,j*hn+i+1,(j+1)*hn+i+1,(j+1)*hn+i) for j in range(len(rows)-1) for i in range(hn-1)]
hair.add(hv,hf,'M_HairCrewDeep','Head')
if NAME=='Olaf':
    # Close the narrow scalp strip between the parted white fringe and helmet.
    # This is part of the fitted original hair volume, with an irregular lower
    # edge and thin short strands; no additional object or recovery overlay.
    front_angles=[-2.15+1.16*i/24 for i in range(25)]
    front_rows=(.875,.890,.907,.925)
    front_vertices=[scalp_point(z+(.003*math.sin(a*19) if j==0 else 0),a,.009)
                    for j,z in enumerate(front_rows) for a in front_angles]
    front_faces=[(j*25+i,j*25+i+1,(j+1)*25+i+1,(j+1)*25+i)
                 for j in range(3) for i in range(24)]
    hair.add(front_vertices,front_faces,'M_HairCrew','Head')
    for index,a in enumerate(front_angles[1:-1]):
        strand(hair,[scalp_point(.910,a,.011),scalp_point(.895,a+.015,.013),
                     scalp_point(.876+.003*math.sin(a*19),a+.025,.011)],
               .004,.002,'M_HairCrewLight' if index%3==0 else 'M_HairCrew',
               steps=3,up=(0,-1,0))
if CFG['style']=='curls':
    # Small overlapping curl crescents, layered around forehead, temples and nape.
    # No single large balls: each visible curl has an inner bent strand ridge.
    # Tiny authored colour-only spiral atlas supplies fine curl strands without
    # spending most of the mesh budget on separate raised wire spirals.
    hr=bytearray();hb=(37,26,21);hl=(68,48,34)
    for py in range(256):
        hr.append(0)
        for px in range(256):
            xx=(px+.5)/256*2-1;zz=1-(py+.5)/256*2
            rho=math.sqrt(xx*xx+zz*zz);phi=math.atan2(zz,xx)
            phase=(phi+rho*math.tau*1.55+math.pi)%math.tau-math.pi
            groove=math.exp(-(phase/.11)**2)*math.exp(-((rho-.50)/.45)**6)
            glow=math.exp(-((abs(phase)-.23)/.16)**2)*.55
            hr.extend(round(hb[i]*(1-groove*.48)*(1-glow)+hl[i]*glow) for i in range(3))
    hp=OUT/(NAME+'_Hair.png')
    hp.write_bytes(b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',struct.pack('>IIBBBBB',256,256,8,2,0,0,0))+
        png_chunk(b'sRGB',b'\0')+png_chunk(b'IDAT',zlib.compress(bytes(hr),9))+png_chunk(b'IEND',b''))
    hm=mats['M_HairCrew'].copy();hm.name=NAME+'_Hair'
    hair_texture_image=bpy.data.images.load(str(hp),check_existing=True)
    hn=hm.node_tree.nodes.new('ShaderNodeTexImage');hn.image=hair_texture_image
    hm.node_tree.links.new(hn.outputs['Color'],hm.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    mats[NAME+'_Hair']=hm
    def curl_base(z,a):
        front=math.sin(a)<-.15
        table=profile if front or z<rows[0][0] else rows
        for lo,hi in zip(table,table[1:]):
            if lo[0]<=z<=hi[0]:
                tt=(z-lo[0])/(hi[0]-lo[0]);rx=lo[1]*(1-tt)+hi[1]*tt
                idx=2 if front or len(lo)==3 else 3
                ry=lo[idx]*(1-tt)+hi[idx]*tt
                off=.004 if front else .002
                return Vector(((rx+off)*math.cos(a),(ry+off)*math.sin(a),z))
        return Vector((.17*math.cos(a),.15*math.sin(a),z))
    curl_rows=[(.878,.163,.133),(.825,.179,.163),(.772,.180,.165),(.719,.174,.157),(.665,.151,.136)]
    for row,(rz,rx,ry) in enumerate(curl_rows):
        for i in range(24):
            a=math.tau*i/24+.13*(row%2)+random.uniform(-.035,.035)
            z=rz+random.uniform(-.014,.014)
            if row>0 and math.sin(a)<{1:-.98,2:-.50,3:-.13,4:.12}[row]: continue
            c=Vector((rx*math.cos(a),ry*math.sin(a),z))
            r=random.uniform(.028,.034);start=len(hair.v)
            normal=Vector((math.cos(a),math.sin(a),0));tangent=Vector((-math.sin(a),math.cos(a),0))
            # Curl domes are embedded in the scalp, with a curled central dimple.
            # Spend topology on the visible surface rather than hidden sphere backs.
            cv=[curl_base(z,a)+normal*r*.50];uvs=[(.5,.5)];cs=14
            for rho in (.20,.42,.65,.84,1.0):
                for j in range(cs):
                    ph=math.tau*j/cs
                    depth=r*(.65*math.sqrt(max(0,1-rho*rho))-.10)
                    depth+=r*.035*math.sin(ph+rho*math.tau*1.55)
                    az=a+r*rho*math.cos(ph)/.16
                    zz=z+r*rho*math.sin(ph)
                    cv.append(curl_base(zz,az)+Vector((math.cos(az),math.sin(az),0))*depth)
                    uvs.append((.5+.5*rho*math.cos(ph),.5+.5*rho*math.sin(ph)))
            cf=[(0,1+j,1+(j+1)%cs) for j in range(cs)]
            cf += [(1+k*cs+j,1+k*cs+(j+1)%cs,1+(k+1)*cs+(j+1)%cs,1+(k+1)*cs+j)
                   for k in range(4) for j in range(cs)]
            cf.append(tuple(reversed(range(1+4*cs,1+5*cs))))
            hair.add(cv,cf,NAME+'_Hair','Head')
            for vi,uvco in enumerate(uvs):curl_uv[start+vi]=uvco
else:
    # Swept fringe: broad planes of many overlapping thin strands, not ropes.
    groups=[(-.045,-.132,.882,-.143,-.100,.817),(.000,-.139,.888,.064,-.151,.828),
            (.045,-.127,.887,.145,-.075,.826),(.105,-.097,.878,.172,-.032,.798)]
    if CFG['style']=='short':
        groups=[(-.045,-.132,.890,-.141,-.100,.848),(.000,-.139,.894,.064,-.151,.852),(.045,-.127,.893,.145,-.075,.849)]
    if CFG['style']=='grey':
        groups=[(-.112,-.104,.893,-.165,-.060,.838),(.108,-.102,.893,.166,-.054,.838)]
    for k,(x0,y0,z0,xe,ye,ze) in enumerate(groups):
        strand(hair,[(x0,y0+.003,z0),((x0+xe)*.45,min(y0,ye)-.006,z0-.014),
                     (xe*.85,ye-.004,ze+.012),(xe,ye,ze)],
               (.018 if CFG['style']=='grey' else .028 if k<3 else .019),.011,'M_HairCrew',steps=5,sides=12)
        for j in range(6):
            off=(j-2.5)*.005
            strand(hair,[(x0+off,y0,z0+off*.2),((x0+xe)*.45+off,min(y0,ye)-.012,z0-.013),
                         (xe*.85+off,ye-.009,ze+.010),(xe+off,ye,ze)],
                   .0048,.0027,'M_HairCrewLight' if j in (1,4) else 'M_HairCrew',steps=4)
    for sign in (-1,1):
        for index in range(18):
            angle=-1.10+1.53*index/17
            root=.895+.003*math.sin(index*2.1)
            end=.816-(.073 if NAME=='Captain' else .095)*index/17+.005*math.sin(index*1.9)
            wave=.075 if NAME=='Sam' else .14 if NAME=='Mats' else .17 if NAME=='Captain' else .035
            points=[]
            for fraction,drift in ((0,0),(.32,-wave),(.70,wave), (1,.12)):
                zz=root+(end-root)*fraction
                aa=angle+drift
                point=scalp_point(zz,aa,.011+.002*math.sin(fraction*math.pi))
                if NAME in ('Sam','Mats') and fraction==1:
                    point.x+=.006 if NAME=='Sam' else .012
                    point.z+=.004
                point.x*=sign
                points.append(point)
            normal=(sign*math.cos(angle),math.sin(angle),0)
            strand(hair,points,.0105,.0032,'M_HairCrewLight' if index%7==3 else 'M_HairCrew',
                   steps=3,sides=8,up=normal)
        if NAME in ('Sam','Mats'):
            for index in range(3):
                points=[scalp_point(.885,-.55+index*.14,.012),
                        scalp_point(.849,-.35+index*.14,.016),
                        scalp_point(.805,-.12+index*.14,.018),
                        scalp_point(.814+index*.002,.13+index*.14,.020)]
                points[-1].x+=.012 if NAME=='Sam' else .020
                for point in points:point.x*=sign
                strand(hair,points,.008,.003,'M_HairCrewLight' if index==1 else 'M_HairCrew',
                       steps=4,sides=8,up=(sign,0,0))
    # Back flow is individually layered and visible under the hat.
    def rear_surface(z,a,offset=.003):
        return scalp_point(z,a,.011+offset)
    for layer in range(3 if CFG['style']=='short' else 4):
        for j in range(22):
            a=-.05+(math.pi+.10)*j/21
            a+=.07*(layer%2)+random.uniform(-.025,.025)
            z=.889-layer*.058+random.uniform(-.015,.014)
            edge=.745-.075*min(1,max(0,math.sin(a))/.55) if CFG['style']=='short' else .738-.104*min(1,max(0,math.sin(a))/.55)
            length=random.uniform(.082,.111);end=max(edge+.007*math.sin(j*1.7),z-length)
            # Irregular overlapping flat strands conform to the scalp surface.
            # Vary their roots/lengths to avoid regular horizontal rows or hooks.
            bend=.10 if NAME=='Captain' else .025
            strand(hair,[rear_surface(z,a,.002),rear_surface(z-(z-end)*.30,a+bend,.005),
                         rear_surface(z-(z-end)*.70,a-bend if NAME=='Captain' else a+.05,.005),rear_surface(end,a+.07,.002)],
                   random.uniform(.009,.013),.0025,'M_HairCrewLight' if j%7==0 else 'M_HairCrew',steps=3,up=(0,0,1))

if CFG.get('moustache'):
    hair.ell((0,-.160,.705),(.019,.010,.013),'M_HairCrew','Head',18,10)
    for s in (-1,1):
        def mustache_point(t):
            x=s*(.001+(.104 if CFG['age'] else .092)*t)
            y=-.159+.027*t**1.5
            z=.704-.010*math.sin(math.pi*t)+.020*t**4
            fullness=(1-t)**.55*(.8+.4*math.sin(math.pi*t))
            return x,y,z,.020*fullness+.0008,.012*fullness+.0005
        mv=[];ns=14;nrings=21
        for i in range(nrings):
            x,y,z,h,dep=mustache_point(i/(nrings-1))
            for j in range(ns):
                a=math.tau*j/ns;mv.append((x,y+dep*math.cos(a),z+h*math.sin(a)))
        mf=[tuple(reversed(range(ns)))]+[(i*ns+j,i*ns+(j+1)%ns,(i+1)*ns+(j+1)%ns,(i+1)*ns+j)
            for i in range(nrings-1) for j in range(ns)]+[tuple(range((nrings-1)*ns,nrings*ns))]
        hair.add(mv,mf,'M_HairCrew','Head')
        # Fine shallow combed ridges follow the smooth moustache surface.
        for j in range(10):
            endfrac=-.82+1.64*j/9;pts=[]
            for k in range(12):
                t=.035+(.78+.18*(j%4)/3)*k/11
                x,y,z,h,dep=mustache_point(t)
                frac=.82*(1-t)+endfrac*t
                pts.append((x,y-dep*math.sqrt(1-frac*frac)-.0006,z+h*frac))
            strand(hair,pts,.0009,.0007,'M_HairCrewLight' if j%4==0 else 'M_HairCrew',steps=1,sides=6)
if CFG.get('beard'):
    # Fine colour strands continue across the support volume between sculpted
    # layers. This is authored albedo, not baked light or a particle groom.
    hr=bytearray()
    for py in range(512):
        hr.append(0);zz=.80-(py+.5)/512*.25
        for px in range(512):
            xx=-.18+(px+.5)/512*.36
            flow=(xx+.0035*math.sin(zz*43+xx*20)+xx*(.73-zz)*.35)/.0045
            phase=(flow+.5)%1-.5
            line=math.exp(-(phase/.12)**2)
            variation=.70+.30*math.sin(zz*75+math.floor(flow)*2.1)**2
            amount=line*.65*variation
            base=(221,221,209);shade=(183,188,181)
            hr.extend(round(base[k]*(1-amount)+shade[k]*amount) for k in range(3))
    hp=OUT/(NAME+'_Hair.png')
    hp.write_bytes(b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',struct.pack('>IIBBBBB',512,512,8,2,0,0,0))+
        png_chunk(b'sRGB',b'\0')+png_chunk(b'IDAT',zlib.compress(bytes(hr),9))+png_chunk(b'IEND',b''))
    hm=mats['M_HairCrew'].copy();hm.name=NAME+'_Hair'
    hair_texture_image=bpy.data.images.load(str(hp),check_existing=True)
    hn=hm.node_tree.nodes.new('ShaderNodeTexImage');hn.image=hair_texture_image
    hm.node_tree.links.new(hn.outputs['Color'],hm.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    mats[NAME+'_Hair']=hm
    # A full rounded beard volume supports thin layered surface clumps.
    # Individual strands must follow that volume rather than hang as tubes.
    beard_core=Mesh();beard_core.quality=1
    beard_core.ell((0,-.095,.655),(.140,.080,.085),'M_HairCrew','Head',32,18)
    for s in (-1,1):beard_core.ell((s*.115,-.060,.700),(.050,.055,.080),'M_HairCrew','Head',24,14)
    core=beard_core.object(NAME+'_BeardVolumeTemporary')
    bpy.context.view_layer.objects.active=core
    remesh=core.modifiers.new('ContinuousBeardVolume','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.0045
    remesh.use_smooth_shade=True;remesh.use_remove_disconnected=False
    bpy.ops.object.modifier_move_up(modifier=remesh.name);bpy.ops.object.modifier_apply(modifier=remesh.name)
    sm=core.modifiers.new('SoftBeardContour','SMOOTH');sm.factor=.75;sm.iterations=3
    bpy.ops.object.modifier_move_up(modifier=sm.name);bpy.ops.object.modifier_apply(modifier=sm.name)
    hair.add([v.co.copy() for v in core.data.vertices],[tuple(f.vertices) for f in core.data.polygons],NAME+'_Hair','Head')
    core_data=core.data;bpy.data.objects.remove(core,do_unlink=True);bpy.data.meshes.remove(core_data)
    def beard_y(x,z):
        candidates=[]
        for cx,cy,cz,rx,ry,rz in [(0,-.095,.655,.140,.080,.085),(-.115,-.060,.700,.050,.055,.080),(.115,-.060,.700,.050,.055,.080)]:
            q=1-((x-cx)/rx)**2-((z-cz)/rz)**2
            if q>=0:candidates.append(cy-ry*math.sqrt(q))
        if not candidates:candidates=[face_surface(x,max(.581,min(.945,z)))[1]]
        return min(candidates)-.0004
    for j in range(41):
        x=(j-20)*.0055
        edge=abs(x)/.108
        ztop=.694+.032*edge; zend=.572+.045*edge;pts=[]
        for k in range(7):
            t=k/6;xx=x*(1-.17*t)+.0015*math.sin(t*math.pi*2+j*.3)
            zz=ztop*(1-t)+zend*t
            pts.append((xx,beard_y(xx,zz),zz))
        strand(hair,pts,.0042,.0017,NAME+'_Hair',steps=2)
    for s in (-1,1):
        for j in range(10):
            off=(j-4.5)*.002
            pts=[]
            for xx,zz in [(.142+off,.735),(.149+off*.8,.707),(.137+off*.7,.668),(.108+off*.5,.614)]:
                pts.append((s*xx,beard_y(s*xx,zz),zz))
            strand(hair,pts,.0032,.0012,NAME+'_Hair',steps=3)
hair_ob=hair.object(NAME+'_Hair')
if curl_uv:
    huv=hair_ob.data.uv_layers.new(name=NAME+'_CurlUV')
    for loop in hair_ob.data.loops:huv.data[loop.index].uv=curl_uv.get(loop.vertex_index,(.5,.5))
elif CFG.get('beard'):
    huv=hair_ob.data.uv_layers.new(name=NAME+'_HairUV')
    for loop in hair_ob.data.loops:
        co=hair_ob.data.vertices[loop.vertex_index].co
        huv.data[loop.index].uv=((co.x+.18)/.36,(co.z-.55)/.25)
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
    captain_crown=[(.899,.176,.151),(.934,.191,.163),(.971,.210,.175),(1.006,.200,.166),(1.032,.143,.120),(1.044,.001,.001)]
    loft(hat,captain_crown,'M_RailIvory')
    bv=[(rx*math.cos(math.tau*i/48),ry*math.sin(math.tau*i/48),z)
        for z,rx,ry in [(.890,.180,.157),(.894,.181,.158),(.917,.185,.161),(.921,.186,.161)] for i in range(48)]
    hat.add(bv,[(j*48+i,j*48+(i+1)%48,(j+1)*48+(i+1)%48,(j+1)*48+i) for j in range(3) for i in range(48)],'M_HullNavy','HatMount')
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
    badge_start=len(hat.v)
    br=[(-.149,.024),(-.153,.034),(-.159,.034),(-.162,.031),(-.163,.028),(-.164,.001)]
    vv=[(rr*math.cos(math.tau*i/32),yy,.973+rr*math.sin(math.tau*i/32)) for yy,rr in br for i in range(32)]
    ff=[tuple(reversed(range(32)))]+[(j*32+i,j*32+(i+1)%32,(j+1)*32+(i+1)%32,(j+1)*32+i) for j in range(len(br)-1) for i in range(32)]
    ff.append(tuple(range((len(br)-1)*32,len(br)*32)))
    first=len(hat.f);hat.add(vv,ff,'M_BrassCrew','HatMount')
    for j in range(3,len(br)-1):
        for i in range(32):hat.mi[first+1+j*32+i]=hat.materials.index('M_HullNavy')
    hat.mi[-1]=hat.materials.index('M_HullNavy')
    # Explicit anchor: eye, shank, crossbar, curved flukes.
    pts=[(.005*math.cos(math.tau*i/16),-.168,.989+.005*math.sin(math.tau*i/16)) for i in range(17)]
    hat.sweep(pts,.0022,'M_BrassCrewLight','HatMount',6)
    cord(hat,[(0,-.168,.984),(0,-.168,.954)],.0028,'M_BrassCrewLight','HatMount',1,7)
    cord(hat,[(-.012,-.168,.979),(.012,-.168,.979)],.0022,'M_BrassCrewLight','HatMount',1,6)
    cord(hat,[(-.018,-.168,.966),(-.014,-.168,.956),(0,-.168,.951),(.014,-.168,.956),(.018,-.168,.966)],.0027,'M_BrassCrewLight','HatMount',3,6)
    # Conform the badge backing to the rounded crown. The back intersects the
    # cap slightly; the relief sits above it without hovering at side angles.
    for index in range(badge_start,len(hat.v)):
        x,y,z=hat.v[index]
        for lower,upper in zip(captain_crown,captain_crown[1:]):
            if lower[0]<=z<=upper[0]:
                t=(z-lower[0])/(upper[0]-lower[0])
                rx=lower[1]*(1-t)+upper[1]*t;ry=lower[2]*(1-t)+upper[2]*t
                surface=-ry*math.sqrt(max(0,1-(x/rx)**2))
                hat.v[index]=(x,surface+.004+(y+.149),z)
                break
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
if role in ('Fisher','Deckhand'):
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
    loft(garment,[(.540,.068,.054),(.568,.057,.049)],'M_RailIvory','Neck',32)
    def chest_panel(spec,mat,lift,cols=7):
        vv=[];ww=[]
        for zz,width in spec:
            for i in range(cols):
                xx=-width+2*width*i/(cols-1);vv.append(torso_surface(xx,zz,lift))
                t=max(0,min(1,(zz-.32)/.19));ww.append({'Hips':1-t,'Spine1':t})
        garment.add(vv,[(j*cols+i,j*cols+i+1,(j+1)*cols+i+1,(j+1)*cols+i) for j in range(len(spec)-1) for i in range(cols-1)],mat,'Spine1',ww)
    chest_panel([(.451,.001),(.470,.012),(.491,.025),(.515,.040),(.538,.052)],'M_RailIvory',.004)
    chest_panel([(.451,.0005),(.467,.008),(.503,.006),(.512,.012),(.527,.006)],'M_HullNavy',.007,3)
    def board_z(x,y):
        table=[(.115,.56144,.0187),(.150,.56867,.0107),(.190,.54839,.0177)]
        for a,b in zip(table,table[1:]):
            if a[0]<=x<=b[0]+1e-6:
                t=(x-a[0])/(b[0]-a[0]);centre=a[1]*(1-t)+b[1]*t;dip=a[2]*(1-t)+b[2]*t
                return centre-dip*(y/.032)**2+.0035
        return .555
    for s in (-1,1):
        garment.patch([torso_surface(s*x,z,.010) for x,z in [(0,.537),(.029,.542),(.055,.529),(.020,.508)]],'M_RailIvory','Spine1',.001)
        garment.patch([torso_surface(s*x,z,.006) for x,z in [(.045,.548),(.109,.529),(.113,.499),(.079,.507)]],
                      'M_CoatCrew','Spine1',.002)
        garment.patch([torso_surface(s*x,z,.006) for x,z in [(.077,.507),(.102,.488),(.043,.422),(.047,.500)]],
                      'M_CoatCrew','Spine1',.002)
        cord(garment,[torso_surface(s*x,z,.014) for x,z in [(.045,.545),(.087,.487),(.041,.407)]],.0011,'M_CoatCrewEdge','Spine1',2,5)
        garment.patch([torso_surface(s*x,z,.004) for x,z in [(.074,.338),(.123,.346),(.122,.333),(.073,.326)]],
                      'M_CoatCrewEdge','Hips',.001)
        for z in (.337,.385,.433):
            begin=len(garment.v)
            disk(garment,(s*.047,torso_surface(s*.047,z,.006)[1],z),.0075,.006,'M_BrassCrew','Spine1' if z>.35 else 'Hips',18)
            t=max(0,min(1,(z-.32)/.19))
            for vi in range(begin,len(garment.v)):garment.w[vi]={'Hips':1-t,'Spine1':t}
        side='Left' if s>0 else 'Right'
        # Epaulettes atop T-pose upper arms, move with original arm action.
        xs=[.115,.1325,.150,.170,.190];ys=[-.032,-.016,0,.016,.032]
        vv=[(s*x,y,board_z(x,y)) for x in xs for y in ys]
        garment.add(vv,[(j*5+i,j*5+i+1,(j+1)*5+i+1,(j+1)*5+i) for j in range(4) for i in range(4)],'M_CoatCrew',side+'Shoulder')
        for j in range(3):
            xx=.131+j*.017
            cord(garment,[(s*xx,y,board_z(xx,y)+.0015) for y in ys],.0025,'M_BrassCrew',side+'Shoulder',1,6)
        for yy in (-.032,.032):
            cord(garment,[(s*x,yy,board_z(x,yy)+.001) for x in xs],.0013,'M_BrassCrew',side+'Shoulder',1,5)
        for x in (.352,.365):
            pts=[(s*x,.043*math.cos(math.tau*i/20),.51+.043*math.sin(math.tau*i/20)) for i in range(21)]
            garment.sweep(pts,.0025,'M_BrassCrew',side+'ForeArm',6,up=(1,0,0))
meshes.append(body.object(NAME+'_MaleBody'))
meshes.append(garment.object(NAME+'_OutfitDetails'))

# Commit topology in rest pose and preserve skinning. All parts stay <=20k total.
budgets={NAME+'_Face':2300,NAME+'_Expression':1600,NAME+'_Hair':5900,
         NAME+'_Hat':2900,NAME+'_MaleBody':3600,NAME+'_OutfitDetails':3500}
if NAME=='Captain':budgets.update({NAME+'_Expression':1700,NAME+'_Hat':3800})
if NAME=='Kofi':budgets[NAME+'_Hair']=6200
if CFG.get('moustache'):
    budgets.update({NAME+'_Expression':1500,NAME+'_Hair':6500,NAME+'_Hat':2500,
                    NAME+'_MaleBody':3500,NAME+'_OutfitDetails':3500})
if CFG.get('beard'):
    budgets.update({NAME+'_Face':2200,NAME+'_Expression':1400,NAME+'_Hair':9000,
                    NAME+'_Hat':2900,NAME+'_MaleBody':3100,NAME+'_OutfitDetails':2300})
assert signature(arm)==baseline
for ob in meshes:
    if ob.name in (NAME+'_Hair',NAME+'_Hat',NAME+'_MaleBody'):
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
    if NAME=='Captain' and ob.name==NAME+'_Hair':
        # Tuck thick fringe roots inside the visor's inner radius. The exposed
        # lower waves retain their silhouette; no brown tips pierce the brim.
        for vertex in ob.data.vertices:
            co=vertex.co
            radius=math.hypot(co.x,co.y)
            if co.z>.880 and radius>0 and -co.y/radius>.30:
                limit=.170-.030*max(0,min(1,(co.z-.880)/.010))
                if radius>limit:co.x*=limit/radius;co.y*=limit/radius
        ob.data.update()
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
bpy.ops.export_scene.fbx(filepath=str(OUT/(NAME+'-staging.fbx')),use_selection=True,
    object_types={'MESH','ARMATURE'},axis_forward='-Z',axis_up='Y',global_scale=1,
    apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=True,
    bake_space_transform=False,add_leaf_bones=False,use_armature_deform_only=False,
    bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,
    bake_anim_force_startend_keying=True,bake_anim_simplify_factor=0,
    use_custom_props=True,mesh_smooth_type='FACE',path_mode='RELATIVE')
publish_staged(OUT/(NAME+'-staging.fbx'),OUT/(NAME+'.fbx'))
arm.animation_data.action=bpy.data.actions['Idle'];scene.frame_set(1)
stats={'name':NAME,'role':role,'revision':args.revision,'original_sha256':original_hash,'contract':baseline,
       'triangles':triangles,'meshes':{o.name:len(o.data.loop_triangles) for o in meshes},
       'textures':[{'file':NAME+'_Face.png','size':[512,512],'use':'authored colour/blush, no baked lighting'}],
       'palette_srgb':PALETTE,'source_axes':'X right, -Y forward, Z up','bare_scalp_m':.95,
       'male_body':'flat original CrewRig proportion contract; original arm/leg attachment positions',
       'settings':CFG}
if hair_texture_image:
    stats['textures'].append({'file':NAME+'_Hair.png','size':list(hair_texture_image.size),'use':'authored fine hair/beard colour strands, no baked lighting'})
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
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(NAME+'-staging.blend')),relative_remap=False)
publish_staged(OUT/(NAME+'-staging.blend'),OUT/(NAME+'.blend'))
if args.render!='none':
    shot('three-quarter',27,elevated=.22)
    shot('face',18,(0,-.018,.807),.53,(1024,1024),elevated=.03)
if args.render=='all':
    shot('front',0);shot('side',90);shot('back',180)
    shot('idle',22,action='Idle',frame=13);shot('walk',22,action='Walk',frame=7)
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
print('MALE BUILD COMPLETE',NAME,args.revision,triangles,'triangles',flush=True)


