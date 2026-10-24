"""Crew women: layered opaque flattened locks, tapered ends and colour-only fibres.
No ropes, particles, external generation or baked illumination. Each clump has a
shallow lenticular cross section and continuous UVs. All hair follows Head.
"""
import math,random,struct,zlib
from mathutils import Vector
import bpy

def build_hair(Mesh,catmull,mats,cfg,name,out,png_chunk):
    g=Mesh();g.quality=1;uvs={};rng=random.Random(231)
    # Colour fibre atlas. Cross-sectional variation follows individual fine fibres;
    # independent of scene lights, portable to ordinary game materials.
    base=[int(cfg['hair'][i:i+2],16) for i in (1,3,5)]
    light=[int(cfg['hairlight'][i:i+2],16) for i in (1,3,5)]
    deep=[int(cfg['hairdeep'][i:i+2],16) for i in (1,3,5)]
    raw=bytearray()
    for y in range(256):
        raw.append(0);v=y/255
        for x in range(256):
            u=x/255
            phase=u*9+.12*math.sin(v*10+u*9)+.06*math.sin(v*21)
            fibre=(.5+.5*math.sin(math.tau*phase))**8
            groove=(.5+.5*math.cos(math.tau*(phase+.23)))**12
            glow=.10+.13*fibre;shadow=.07*groove
            raw.extend(round((base[i]*(1-glow)+light[i]*glow)*(1-shadow)+deep[i]*shadow) for i in range(3))
    hp=out/(name+'_Hair.png')
    hp.write_bytes(b'\x89PNG\r\n\x1a\n'+png_chunk(b'IHDR',struct.pack('>IIBBBBB',256,256,8,2,0,0,0))+png_chunk(b'sRGB',b'\0')+png_chunk(b'IDAT',zlib.compress(bytes(raw),9))+png_chunk(b'IEND',b''))
    image=bpy.data.images.load(str(hp),check_existing=True)
    mat=mats['M_HairCrew'].copy();mat.name=name+'_Hair'
    node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image
    mat.node_tree.links.new(node.outputs['Color'],mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    mats[name+'_Hair']=mat
    def clump(points,w=.014,d=.004,steps=3,sides=6,normal=(0,-1,0),blunt=False):
        pts=catmull(points,steps);vv=[];local=[]
        for j,p in enumerate(pts):
            t=j/(len(pts)-1)
            tangent=(pts[min(j+1,len(pts)-1)]-pts[max(j-1,0)]).normalized()
            u=Vector(normal).cross(tangent).normalized()
            if u.length<.1:u=Vector((1,0,0)).cross(tangent).normalized()
            dep=tangent.cross(u).normalized()
            taper=min(1,.45+t*7,max(.06,(1-t)*5)) if not blunt else min(1,.7+t*8,max(.65,(1-t)*12))
            for i in range(sides):
                a=math.tau*i/sides
                vv.append(p+u*(w*taper*math.cos(a))+dep*(d*taper*math.sin(a)))
                local.append(((.5+.5*math.cos(a))*.96+.02,t*.96+.02))
        ff=[tuple(reversed(range(sides)))]+[(j*sides+i,j*sides+(i+1)%sides,(j+1)*sides+(i+1)%sides,(j+1)*sides+i) for j in range(len(pts)-1) for i in range(sides)]+[tuple(range((len(pts)-1)*sides,len(pts)*sides))]
        start=len(g.v);g.add(vv,ff,name+'_Hair','Head')
        for i,uv in enumerate(local):uvs[start+i]=uv
    style=cfg['style']
    # Fitted continuous hair underlayer, from temples around the nape. Its
    # boundary is buried under the SAME layered locks, never a separate flat fill.
    # The old half-cylinder began behind the ears and left the temple band bare.
    profile=[(.630,.125,.108,.107),(.672,.150,.132,.125),(.713,.168,.145,.140),
             (.755,.173,.151,.151),(.801,.171,.146,.155),(.842,.162,.134,.149),
             (.880,.144,.116,.131),(.914,.111,.087,.103),(.938,.067,.050,.060)]
    def fitted(a,z,lift=.007):
        lo,hi=next(((lo,hi) for lo,hi in zip(profile,profile[1:]) if lo[0]<=z<=hi[0]),(profile[-2],profile[-1]))
        t=max(0,min(1,(z-lo[0])/(hi[0]-lo[0])))
        rx,fr,bk=[lo[i]*(1-t)+hi[i]*t for i in (1,2,3)]
        return ((rx*cfg.get('facewidth',1)+lift)*math.cos(a),
                ((fr if math.sin(a)<0 else bk)+lift)*math.sin(a),z)
    n=65;levels=14;vv=[]
    for j in range(levels):
        t=j/(levels-1)
        for i in range(n):
            a=-1.16+(math.pi+2.32)*i/(n-1)
            side=abs(math.cos(a))
            bottom=(.643 if style in ('waves','bob','sidebraid') else .694)
            # Higher front temple hairline sweeps down behind the ear; irregular
            # hem sits inside the existing thin tips, with no visible cut plane.
            edge=max(0,-math.sin(a))
            bottom+=.200*edge**2+.003*math.sin(a*11)
            z=bottom+(.930-bottom)*t
            vv.append(fitted(a,z))
    ff=[(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i) for j in range(levels-1) for i in range(n-1)]
    start=len(g.v);g.add(vv,ff,name+'_Hair','Head')
    for j in range(levels):
        for i in range(n):uvs[start+j*n+i]=(i/(n-1),j/(levels-1))
    # Thin swept temple locks overlap the support's front boundary, connecting
    # forelock and rear flow. At the side their width faces the side camera.
    for sign in (-1,1):
        for j in range(7):
            a=-1.04+j*.18 if sign>0 else math.pi+1.04-j*.18
            pts=[]
            for k in range(8):
                t=k/7;aa=a+sign*.12*math.sin(t*math.pi)
                end=.710 if style in ('pixie','short') else .665 if style in ('bob','waves','sidebraid') else .719
                z=.905-(.905-end)*t
                p=Vector(fitted(aa,z,.010))
                p.x+=sign*(.005 if style=='bob' else .010)*math.sin(t*math.tau+j*.7)*math.sin(math.pi*t)
                pts.append(p)
            clump(pts,.016,.004,steps=3,normal=(sign,0,0),blunt=style=='bob')
    # Different back contours, each covered from crown through nape.
    count=(24 if name=='Lise' else 16) if style=='waves' else 24 if style in ('sidebraid','bob') else 20
    for i in range(count):
        a=math.pi*i/(count-1);phase=rng.uniform(0,math.tau)
        length=.260+rng.uniform(-.025,.035) if style in ('waves','sidebraid','bob') else .205+rng.uniform(-.020,.025)
        if style in ('pixie','short'):length=.175+rng.uniform(-.025,.020)
        if style=='bob':length=.255+rng.uniform(-.003,.003)
        points=[]
        for k in range(7):
            t=k/6;z=.902-length*t
            radx=.148+(.057 if style=='waves' else .040)*math.sin(math.pi*t*.8);rady=.132+(.052 if style=='waves' else .036)*math.sin(math.pi*t*.8)
            wave=(.022 if style=='waves' else .007 if style=='sidebraid' else .0015)*math.sin(t*math.tau*1.7+phase)*math.sin(math.pi*t*.85)
            aa=a+(.12 if style=='waves' else .035)*math.sin(t*8+phase)
            points.append(((radx+wave)*math.cos(aa),(rady+wave)*math.sin(aa)+.005,z))
        clump(points,.017+rng.uniform(-.003,.003) if style=='waves' else .016+rng.uniform(-.003,.003),.006,steps=2 if name=='Lise' else 3,normal=(math.cos(a),math.sin(a),.1),blunt=style=='bob')
    # Swept forehead locks. Bob fringe has an intentionally straight blunt edge.
    if style=='bob':
        for i in range(12):
            x=-.143+.286*i/11
            clump([(x*.84,-.084,.924),(x*.99,-.119,.883),(x,-.139,.850),(x*.99,-.144,.823+rng.uniform(-.002,.002))],.015,.005,steps=3,blunt=True)
    else:
        for i in range(6):
            s=-1 if i<3 else 1;j=i%3
            rootx=s*(.007+j*.014);endx=s*(.089+j*.026)
            bottom=.844-j*.009+(0.008 if style=='short' else 0)
            clump([(rootx,-.095,.927),(s*(.035+j*.020),-.134,.896),(s*(.071+j*.025),-.150,.862),(endx,-.137,bottom)],.027-j*.003,.007,steps=5)
        # Fine overlapping tips retain Mira's layered forelock language.
        for i in range(9):
            s=-1 if i<3 else 1;j=i%3
            clump([(s*(.014+j*.017),-.138,.901),(s*(.046+j*.021),-.154,.877),(s*(.075+j*.023),-.141,.849-j*.004)],.0048,.0018,steps=3)
        if name in ('Lise','Ines'):
            # Continue the existing swept fringe into the side waves, with the
            # same broad shallow lock and fine overlapping tips as the forelock.
            for s in (-1,1):
                clump([(s*.065,-.108,.909),(s*.114,-.128,.878),
                       (s*.155,-.112,.845),(s*.168,-.078,.803)],.019,.005,steps=5,normal=(s*.8,-.6,0))
                for j in range(4):
                    off=(j-1.5)*.004
                    clump([(s*(.071+off),-.113,.906),(s*(.122+off),-.135,.876),
                           (s*(.158+off),-.118,.844),(s*(.167+off),-.083,.803+j*.003)],.0048,.0018,steps=3,normal=(s*.8,-.6,0))
    # Face framing sides: stay outside cheeks and avoid the ear/eye planes.
    if style in ('waves','sidebraid','twinbraid','bob','highbun','lowbun'):
        for s in (-1,1):
            nside=5 if name in ('Lise','Tess','Ines','Noor') else 3
            for j in range(nside):
                x=s*(.155+j*(.007 if name in ('Lise','Tess','Ines','Noor') else .012));y=-.095+j*(.017 if name in ('Lise','Tess','Ines','Noor') else .030);phase=j*.8
                end=.607+rng.uniform(-.025,.030) if style in ('waves','sidebraid','bob') else .670+rng.uniform(-.025,.005)
                if style=='bob':end=.648+rng.uniform(-.003,.003)
                pts=[]
                for k in range(8):
                    t=k/7;amp=.026 if style=='waves' else .014 if style in ('sidebraid','highbun','twinbraid') else .004
                    top=.910
                    pts.append((x+s*amp*math.sin(t*math.tau*1.4+phase),y-.014*math.sin(math.pi*t),top-(top-end)*t))
                clump(pts,.013 if style=='bob' else .014,.005,steps=3 if name in ('Lise','Tess','Ines','Noor') else 4,normal=(s,0,0) if name in ('Lise','Tess','Ines','Noor') else (0,-1,0),blunt=style=='bob')
    else:
        for s in (-1,1):
            for j in range(5):
                clump([(s*.151,-.058+j*.018,.864),(s*(.170+j*.003),-.044+j*.02,.809),(s*(.161+j*.002),-.012+j*.02,.748-j*.009)],.012,.004,steps=3)
    # Flattened interwoven braid leaves; each leaf has its own fibre flow and end.
    if style in ('sidebraid','twinbraid'):
        for s in ((1,) if style=='sidebraid' else (-1,1)):
            bottom=.410 if style=='sidebraid' else .362;top=.795 if style=='sidebraid' else .768
            centre=s*(.179 if style=='sidebraid' else .172);cy=-.075 if style=='sidebraid' else -.092
            levels=10 if style=='sidebraid' else 13
            for j in range(levels):
                z=top-(top-bottom)*j/levels;step=(top-bottom)/levels
                width=(.038 if style=='sidebraid' else .030)*(1-.42*j/levels)
                for sign in (-1,1):
                    clump([(centre+sign*width,cy+.002,z+.010),(centre+sign*width*.55,cy-.009,z),(centre-sign*width*.60,cy-.013,z-step*.64),(centre-sign*width*.45,cy-.003,z-step)],width*.64,.0055,steps=3)
            clump([(centre,cy,bottom+.008),(centre+s*.003,cy-.003,bottom-.022),(centre-s*.010,cy+.002,bottom-.050)],.023 if style=='sidebraid' else .020,.006,steps=4)
            # Navy tie around each braid, geometry included in hair mesh group.
            g.sweep([(centre-.018,cy,bottom+.006),(centre-.01,cy-.015,bottom+.006),(centre+.012,cy-.015,bottom+.006),(centre+.018,cy,bottom+.006)],.003,'M_HullNavy','Head',6)
    if style in ('highbun','lowbun'):
        c=Vector((.018,.171,1.005 if style=='highbun' else .724));rx=.095 if style=='highbun' else .087;rz=.113 if style=='highbun' else .069
        # Solid support volume is buried under flattened swept clumps.
        start=len(g.v);g.ell(c,(rx*.87,.073,rz*.89),name+'_Hair','Head',24,14)
        for idx in range(start,len(g.v)):
            p=Vector(g.v[idx])-c;uvs[idx]=(.5+math.atan2(p.x,p.y)/math.tau,.5+p.z/(rz*2))
        for j in range(28):
            a=math.tau*j/28;phase=rng.uniform(-.15,.15);pts=[]
            for k in range(7):
                t=k/6;theta=-1.2+2.5*t
                aa=a+theta*.58
                pts.append(c+Vector((rx*math.cos(aa)*math.cos(theta),.083*math.sin(aa)*math.cos(theta),rz*math.sin(theta))))
            clump(pts,.014,.0045,steps=3,normal=(math.cos(a),math.sin(a),.4))
        for j in range(5):
            a=j*math.tau/5;pts=[c+Vector((rx*math.cos(a),.079*math.sin(a),rz*.1)),c+Vector((rx*1.15*math.cos(a),.095*math.sin(a),rz*.65)),c+Vector((rx*1.22*math.cos(a+.2),.1*math.sin(a+.2),rz*.91))]
            clump(pts,.004,.0016,steps=4)
    if style=='waves':
        # Lower overlapping springy ends give the redhead a broad curly silhouette.
        for j in range(6):
            a=math.pi*j/5;pts=[]
            for k in range(7):
                t=k/6;rad=.192+.024*math.sin(t*math.tau*1.3+j*.7)
                aa=a+.13*math.sin(t*math.tau+j)
                pts.append((rad*math.cos(aa),rad*.91*math.sin(aa),.755-.153*t+rng.uniform(-.004,.004)))
            clump(pts,.016,.005,steps=4,normal=(math.cos(a),math.sin(a),0))
    if name in ('Lise','Tess','Ines','Noor'):
        # Roots above the rolled cuff stay inside its inner ellipse. Only the
        # portions hidden by the hat are fitted; visible strand widths stay intact.
        for i,point in enumerate(g.v):
            x,y,z=point
            if z>.883:
                fit=math.sqrt((x/.165)**2+(y/.142)**2)
                if fit>1:g.v[i]=(x/fit,y/fit,z)
    ob=g.object(name+'_Hair');uv=ob.data.uv_layers.new(name=name+'_FibreUV')
    for loop in ob.data.loops:uv.data[loop.index].uv=uvs.get(loop.vertex_index,(.5,.5))
    return ob,image
