"""ART108 A1: expanded maps with three grounds, explicit paths and lighting.

Preserve the existing authored map as ground1; extend seabed and hand-place new
ground-specific dressing. Export with the previously verified Unity X compensation.
Run -- <Map> [build|review]. All original source/FBX/meta inputs are read-only.
"""
import bpy,bmesh,sys,math,json,hashlib,shutil
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
sys.path.insert(0,str(Path(__file__).parent));import build_stations as K
ROOT=K.ROOT;ART=ROOT.parent/'Catchline-art-style'
NAMES=['GullHarbourMouth','GullKelpBank','GullSandbar','GullRockyPoint','GullDeepChannel']
GROUNDS={
 'GullHarbourMouth':[('quay-shallows','Quay shallows',1.2),('channel','Channel',3.8),('mouth-flats','Mouth flats',1.4)],
 'GullKelpBank':[('kelp-shallows','Kelp shallows',1.2),('kelp-edge','Kelp edge',2.3),('open','Open',5.2)],
 'GullSandbar':[('the-bar','The bar',1.1),('gully','Gully',3.6),('open','Open',5.2)],
 'GullRockyPoint':[('reef','Reef',1.8),('drop-off','Drop-off',3.7),('open','Open',5.8)],
 'GullDeepChannel':[('drop-off','Drop-off',4.2),('trench','Trench',14.0),('open','Open',9.0)]}
K.PALETTE.update({'M_SeabedSand':'BEA77D','M_CoastStone':'A99A7C','M_CoastWet':'696F64',
 'M_KelpGreen':'477A56','M_CoastSand':'D9C393','M_CoastGrass':'729053'})
def get_source(name):
    return ART/('Art/Models/HarbourMouth11' if name=='GullHarbourMouth' else f'Art/Models/Locations12/{name}')/f'{name}.blend'
def mesh(name,verts,faces,mat):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);bpy.context.scene.collection.objects.link(ob);me.materials.append(K.material(mat));return ob
def rock(x,z,size,under=False):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,-z,-.28 if under else .12))
    o=bpy.context.object;o.name='GroundRock';o.scale=(size,size*.7,size*.65);o.data.materials.append(K.material('M_CoastWet' if under else 'M_CoastStone'))
def kelp(x,z,depth,count=5):
    for i in range(count):
        dx=(i%3-1)*.35;dy=(i//3-.5)*.4;h=depth-.18-(i%3)*.07
        # Wide silhouette blades, sparse readable geometry; all rooted below waterline.
        v=[(x+dx-.10,-z+dy,-depth),(x+dx+.10,-z+dy,-depth),(x+dx+.21,-z+dy-.05,-depth+h*.6),(x+dx+.05,-z+dy-.08,-depth+h)]
        v+= [(a,b+.014,c) for a,b,c in v]
        mesh('RootedKelpBlade',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'M_KelpGreen')
def post(x,z):
    K.cyl('MooringPost',(x,-z,.18),.10,.75,'M_DeckWood')
    K.torus('PostRope',(x,-z,.37),.105,.017,'M_Rope')
def buoy(x,z,orange=True):
    K.cyl('NavigationBuoy',(x,-z,.14),.16,.33,'M_SafetyOrange' if orange else 'M_RailIvory')
    K.cyl('BuoyPole',(x,-z,.47),.018,.46,'M_HullNavy')
    K.box('BuoyTopmark',(x,-z,.72),(.13,.045,.13),'M_HullNavy',.012)
def terrain(width,depth,anchors,name):
    nx,ny=101,65;vs=[];fs=[]
    def level(x,z):
        # A continuous offshore bottom under the old terrain; old terrain stays intact.
        result=-6.4
        for g in anchors[1:]:
            dx=x-g['position'][0];dz=z-g['position'][2];d=g['seabedDepth']
            if g['id']=='trench':
                if abs(dx)<9 and abs(dz)<8:result=-14
                continue
            bump=math.exp(-(dx/10)**4-(dz/9)**4)
            result+=max(0,6.4-d)*bump
            if name=='GullSandbar' and g['id']=='gully':
                result+=3.1*math.exp(-((dx-2)/1.8)**2-((dz+4)/5)**2)
            if name=='GullRockyPoint' and g['id']=='drop-off':
                result+=2.2*math.exp(-((dx-2)/3)**2-((dz+4.5)/5)**2)
        return min(-.22,result+.03*math.sin(x*.7+z*.6))
    for j in range(ny):
        z=-depth/2+j*depth/(ny-1)
        for i in range(nx):
            x=-width/2+i*width/(nx-1);vs.append((x,-z,level(x,z)))
    for j in range(ny-1):
        for i in range(nx-1):
            a=j*nx+i;fs.append((a,a+nx,a+nx+1,a+1))
    # Close underside and perimeter; no zero-thickness box posing as land.
    perimeter=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range((ny-1)*nx+nx-2,(ny-1)*nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
    bottom=[]
    for idx in perimeter:bottom.append(len(vs));vs.append((vs[idx][0],vs[idx][1],-16))
    for k,a in enumerate(perimeter):
        n=(k+1)%len(perimeter);fs.append((a,perimeter[n],bottom[n],bottom[k]))
    center=len(vs);vs.append((0,0,-16))
    for k,a in enumerate(bottom):fs.append((center,bottom[(k+1)%len(bottom)],a))
    return mesh('ExpandedConnectedSeabed',vs,fs,'M_SeabedSand' if name not in ('GullRockyPoint','GullDeepChannel') else 'M_CoastWet')
def dressing(name,anchors):
    def visible(x,z,s,t):return (x+.819152*s-.81116*t,z-.573576*s-1.158456*t)
    for g in anchors[1:]:
        x,z=g['position'][0],g['position'][2];kind=g['id'];d=g['seabedDepth']
        if name=='GullHarbourMouth':
            if kind=='channel':
                for side in (-1,1):buoy(*visible(x,z,side*3.8,1.5),side==1)
            else:
                for dx,dz in [(-4,3),(4,3),(5,-3)]:post(x+dx,z+dz)
                for dx,dz in [(-3,2),(3,3),(-4,-3)]:kelp(x+dx,z+dz,d,4)
        elif name=='GullKelpBank':
            if kind=='kelp-edge':
                for s,t in [(3,1.4),(3.8,.7),(3.5,2.2)]:kelp(*visible(x,z,s,t),d,6)
                for s,t,r in [(-3.7,-.6,.8),(-4.2,.2,.55),(-3.5,.3,.45)]:rock(*visible(x,z,s,t),r,True)
            else:buoy(*visible(x,z,-4.0,1.0),False)
        elif name=='GullSandbar':
            if kind=='gully':
                # Pale submerged bar runs beside the dark gully, away from the boat/path.
                for i in range(6):K.box('PaleSandRipple',(x+2,-(z-5+i*.6),-.77),(.65,.045,.025),'M_CoastSand',.009)
                post(*visible(x,z,4.0,1.5))
            else:buoy(*visible(x,z,-4,1.0),False)
        elif name=='GullRockyPoint':
            if kind=='drop-off':
                for s,t,r in [(3.8,1.5,1.1),(4.5,.9,.8),(4.1,2.2,.6)]:rock(*visible(x,z,s,t),r,True)
            else:buoy(*visible(x,z,-4,1.0),False)
        else:
            if kind=='trench':
                for side in (-1,1):buoy(*visible(x,z,side*4,1.5),side==1)
            else:
                # Distant ship is deliberately scenery, not a new gameplay hull.
                sx,sz=visible(x,z,-3.7,2.5)
                K.box('DistantShipHull',(sx,-sz,.12),(1.8,.45,.30),'M_HullNavy',.08)
                K.box('DistantShipCabin',(sx-.50,-sz,.39),(.45,.35,.28),'M_RailIvory',.04)
                K.box('DistantShipFunnel',(sx-.16,-sz,.56),(.15,.15,.15),'M_SafetyOrange',.02)
                for side in (-1,1):buoy(*visible(x,z,side*4,.2),side==1)
def bvh_for(obs):
    vs=[];fs=[]
    for o in obs:
        if o.type!='MESH':continue
        off=len(vs);vs.extend(o.matrix_world@v.co for v in o.data.vertices);fs.extend(tuple(off+i for i in f.vertices) for f in o.data.polygons)
    return BVHTree.FromPolygons(vs,fs)
def build(name):
    source=get_source(name);folder=ROOT/'Art/Models/Maps'/name;folder.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source))
    originals=[o for o in bpy.context.scene.objects if o.type=='MESH']
    baseline=K.bounds(originals);base_size=[baseline[1][i]-baseline[0][i] for i in range(3)]
    for o in list(bpy.data.objects):
        if o.type!='MESH':bpy.data.objects.remove(o,do_unlink=True)
    lowered=0
    for o in originals:
        o.parent=None
        # Derived-map deep skirt joins the extension; retain the visible coast/shallow shelf.
        for v in o.data.vertices:
            if v.co.z < -2.3:v.co.z=-6.6+(v.co.z+2.3);lowered+=1
    # New anchors beyond the retained old shore envelope; 3–5 large-boat lengths apart.
    offset=max(22,max(abs(baseline[j][0]) for j in (0,1))+8)
    width=max(base_size[0]*3,2*offset+24);depth=max(base_size[1]*3,42)
    anchors=[]
    for i,(id,title,d) in enumerate(GROUNDS[name]):
        anchors.append(dict(id=id,name=title,position=[1+(0 if i==0 else offset*(1 if i==1 else -1)),0,.5],heading=0,seabedDepth=d,seabedDepthKind='nominal water-colour preset; physical terrain varies',poolId=f'{name}/{id}'))
    terrain(width,depth,anchors,name);dressing(name,anchors)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    for o in meshes:
        o.hide_viewport=False;o.hide_render=False;o.hide_set(False)
        bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.transform_apply(location=True,rotation=True,scale=True);o.select_set(False)
    bpy.context.view_layer.update();bvh=bvh_for(meshes)
    # All three grounds must be free for hull centres. Physical depth is also reported.
    samples=[]
    for g in anchors:
        x,_,z=g['position'];hit=bvh.ray_cast(Vector((x,-z,6)),Vector((0,0,-1)))[0]
        assert hit is not None and hit.z<-.35,(name,g['id'],'anchor obstructed',hit)
        g['physicalAnchorDepth']=-hit.z;samples.append(dict(id=g['id'],surfaceZ=hit.z))
    paths=[]
    for a,b in [(0,1),(0,2),(1,2)]:
        p,q=anchors[a]['position'],anchors[b]['position'];points=[p,[p[0],0,-depth*.38],[q[0],0,-depth*.38],q]
        # Art path candidates. Check centreline every .5m; finite hull clearance belongs to M4.
        checked=0;obstructions=[]
        for start,end in zip(points,points[1:]):
            length=math.dist(start,end);n=max(1,math.ceil(length/.5))
            for j in range(n+1):
                t=j/n;x=start[0]+(end[0]-start[0])*t;z=start[2]+(end[2]-start[2])*t
                hit=bvh.ray_cast(Vector((x,-z,6)),Vector((0,0,-1)))[0]
                if hit is not None and hit.z>=-.35:obstructions.append([x,z,hit.z])
                checked+=1
        paths.append(dict(fromGround=anchors[a]['id'],toGround=anchors[b]['id'],polyline=points,centrelineSamples=checked,centrelineClear=not obstructions,obstructions=obstructions))
    root=bpy.data.objects.new('Catchline_'+name+'GroundsV1',None);bpy.context.scene.collection.objects.link(root)
    root['waterline_local_y']=0;root['world_y']=-.32
    for o in meshes:o.parent=root
    sc=bpy.context.scene;sc.unit_settings.system='METRIC';sc.unit_settings.scale_length=1;sc.render.fps=24
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/f'{name}.blend'))
    record={'map':name,'baselineSource':str(source),'baselineSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'baselineBounds':baseline,
      'expandedBounds':K.bounds(meshes),'baselineFootprint':base_size[0]*base_size[1],'expandedFootprint':width*depth,'footprintRatio':width*depth/(base_size[0]*base_size[1]),
      'triangles':K.tris(meshes),'deepSkirtVerticesLowered':lowered,'anchorChecks':samples,'pathCentrelineAllClear':all(p['centrelineClear'] for p in paths),'nativePathAndFramingAcceptance':'pending M4 code-owner hull sweep + runtime captures'}
    assert record['footprintRatio']>=3
    (folder/'grounds.json').write_text(json.dumps(dict(schema=1,map=name,runtimeModelId=name+'GroundsV1',runtimeFile=f'Assets/Art/Models/Environment/{name}/{name}GroundsV1.fbx',units='metres',anchorSpace='World deck-centre position, deck Y=0 above water Y=-0.32; runtime Boat translation = anchor - rotated HullDef.Center. Never add map root Y offset to boat deck.',waterlineLocal=0,worldPosition=[0,-.32,0],rotation=[0,0,0],scale=[1,1,1],grounds=anchors,paths=paths),indent=2))
    presets={'day':{'keyColor':'#FFF2DC','keyIntensity':1.3,'ambient':'#BCD6DF','ambientIntensity':.45},
      'night':{'keyColor':'#FFC875','keyIntensity':.22,'ambient':'#445C8F','ambientIntensity':.24,'deckPools':[{'boatLocal':[.4,1.6,.5],'color':'#FFD593','range':3.2,'intensity':1.2},{'boatLocal':[2,1.6,1],'color':'#FFD593','range':3.2,'intensity':1.2}]},
      'note':'Runtime light intensities are integration starting values, not lumen equivalence to Blender review area lights. One model, two presets.'}
    (folder/'lighting-presets.json').write_text(json.dumps(presets,indent=2))
    source_positions={o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in meshes}
    source_triangles={o.name:K.tris([o]) for o in meshes}
    # Match the retained ART011/012 Unity import compensation, then independent readback.
    for o in meshes:
        for v in o.data.vertices:x,y,z=v.co;v.co=(-x,z,-y)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    bpy.ops.object.select_all(action='SELECT')
    fbx=folder/f'{name}.fbx'
    bpy.ops.export_scene.fbx(filepath=str(fbx),use_selection=True,object_types={'MESH','EMPTY'},axis_forward='-Z',axis_up='Y',
      apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',use_space_transform=False,bake_space_transform=False,use_triangles=True,bake_anim=False,add_leaf_bones=False)
    game=ROOT/'Assets/Art/Models/Environment'/name;game.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(fbx))
    imported=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert K.tris(imported)==record['triangles'],(name,'triangles',K.tris(imported),record['triangles'],[(o.name,K.tris([o]),source_triangles.get(o.name)) for o in imported if K.tris([o])!=source_triangles.get(o.name)])
    maxerr=0
    for o in imported:
        actual=[o.matrix_world@v.co for v in o.data.vertices]
        kd=KDTree(len(actual))
        for i,p in enumerate(actual):kd.insert(Vector((-p.x,p.y,p.z)),i)
        kd.balance()
        err=max(kd.find(p)[2] for p in source_positions[o.name]);maxerr=max(maxerr,err)
    assert maxerr<.0001,(name,maxerr)
    record['roundTripMaxVertexError']=maxerr;record['fbxSha256']=hashlib.sha256(fbx.read_bytes()).hexdigest()
    shutil.copyfile(fbx,game/f'{name}GroundsV1.fbx')
    for path in [folder/'grounds.json',folder/'lighting-presets.json']:shutil.copyfile(path,game/path.name)
    (folder/'validation.json').write_text(json.dumps(record,indent=2));print('ART108 MAP BUILD PASSED',name,record['footprintRatio'],maxerr,flush=True)
def review(name):
    folder=ROOT/'Art/Models/Maps'/name;bpy.ops.wm.open_mainfile(filepath=str(folder/f'{name}.blend'))
    sc=bpy.context.scene;ground=json.loads((folder/'grounds.json').read_text());root=bpy.data.objects['Catchline_'+name+'GroundsV1']
    root.scale=(1,-1,1);root.location.z=-.32
    # Reuse the exact original hull source without changing any original data.
    src=ROOT/'Art/Models/GullHarbour/Boats/Rowboat.blend'
    with bpy.data.libraries.load(str(src),link=False) as (a,b):b.objects=[n for n in a.objects if n.startswith('Catchline_Rowboat') or n in ['Hull','PlankDeck','IvoryGunwale','CentreThwart','Oar_Port','Oar_Starboard','Oarlock_Port','Oarlock_Starboard','RodSocket_Port_Bow','RodSocket_Port_Stern']]
    for o in b.objects:
        if o:sc.collection.objects.link(o)
    boat=next(o for o in b.objects if o and o.type=='EMPTY');boat.rotation_euler.z=math.pi/2;boat.scale=(1,-1,1)
    # Transmissive water is a review approximation, never exported or substituted for runtime water.
    water=K.box('REVIEW water',(0,0,-8.32),(240,240,16),'M_SeaTeal',0)
    mat=water.data.materials[0].copy();water.data.materials[0]=mat
    shader=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');shader.inputs['Base Color'].default_value=(.32,.70,.66,1);shader.inputs['Transmission Weight'].default_value=.82;shader.inputs['Roughness'].default_value=.30;shader.inputs['IOR'].default_value=1.333
    shader.inputs['Emission Color'].default_value=(.008,.24,.28,1);shader.inputs['Emission Strength'].default_value=.12
    absorption=mat.node_tree.nodes.new('ShaderNodeVolumeAbsorption');absorption.inputs['Color'].default_value=(.11,.66,.65,1);absorption.inputs['Density'].default_value=.055
    output=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL');mat.node_tree.links.new(absorption.outputs[0],output.inputs['Volume'])
    sc.world=bpy.data.worlds.new('Review ambient');sc.world.use_nodes=True;bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND')
    lights=[]
    for id,power,size in [('Key',1200,5),('Fill',350,6)]:
        d=bpy.data.lights.new(id,'AREA');d.energy=power;d.size=size;o=bpy.data.objects.new(id,d);sc.collection.objects.link(o);lights.append(o)
    pools=[]
    for i in range(2):
        d=bpy.data.lights.new('Deck lantern','SPOT');d.energy=45;d.color=(1,.66,.30);d.shadow_soft_size=.08;d.spot_size=math.radians(78);d.spot_blend=.55
        o=bpy.data.objects.new('Deck lantern',d);sc.collection.objects.link(o);pools.append(o)
    d=bpy.data.cameras.new('Gameplay framing');d.type='ORTHO';cam=bpy.data.objects.new('Gameplay framing',d);sc.collection.objects.link(cam);sc.camera=cam
    pitch,yaw=math.radians(45),math.radians(35);forward=Vector((math.sin(yaw)*math.cos(pitch),math.cos(yaw)*math.cos(pitch),-math.sin(pitch)))
    cam.rotation_euler=forward.to_track_quat('-Z','Y').to_euler();d.ortho_scale=10.24;d.clip_end=500
    sc.render.engine='CYCLES';sc.cycles.samples=16;sc.cycles.use_denoising=True;sc.cycles.max_bounces=6;sc.cycles.transmission_bounces=4
    try:
        prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
        for dev in prefs.devices:dev.use=dev.type=='OPTIX'
        if any(dev.use for dev in prefs.devices):sc.cycles.device='GPU'
    except Exception:pass
    sc.view_settings.view_transform='AgX';sc.render.resolution_x=1440;sc.render.resolution_y=900;sc.render.resolution_percentage=100
    sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB'
    for g in ground['grounds']:
        x,_,z=g['position'];boat.location=(x,z,0)
        target=Vector((x+.35,z-.30,0));cam.location=target-forward*40
        depth=g['seabedDepth'];mix=max(0,min(1,(depth-1.2)/7))
        shallow=(.025,.48,.50);deep=(.008,.12,.24)
        tint=tuple(a+(b-a)*mix for a,b in zip(shallow,deep))
        shader.inputs['Base Color'].default_value=(*tint,1)
        shader.inputs['Emission Color'].default_value=(*tint,1)
        for light,off in zip(lights,[(-4,0,7),(5,4,6)]):
            light.location=(x+off[0],z+off[1],off[2]);light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        for i,p in enumerate(pools):p.location=(x+.3+i*1.4,z+.5,1.35)
        for night in (False,True):
            shader.inputs['Emission Strength'].default_value=.018 if night else .18
            bg.inputs[0].default_value=(.08,.13,.26,1) if night else (.55,.73,.80,1);bg.inputs[1].default_value=.30 if night else .50
            lights[0].data.energy=150 if night else 1200;lights[0].data.color=(1,.64,.29) if night else (1,.9,.73)
            lights[1].data.energy=150 if night else 350;lights[1].data.color=(.34,.49,1) if night else (.66,.84,1)
            for p in pools:p.hide_render=not night
            sc.render.filepath=str(folder/f'{g["id"]}-{"night" if night else "day"}.png');bpy.ops.render.render(write_still=True)
    # Top-down overview with all three anchors and every candidate path.
    for p in pools:p.hide_render=True
    boat.hide_render=True
    for o in boat.children_recursive:o.hide_render=True
    bg.inputs[0].default_value=(.55,.73,.80,1);bg.inputs[1].default_value=.7
    for light in lights:light.data.type='SUN';light.data.energy=1.3;light.data.color=(1,.92,.8)
    for g in ground['grounds']:
        x,_,z=g['position'];K.torus('REVIEW anchor',(x,z,.06),.75,.09,'M_SafetyOrange')
        cu=bpy.data.curves.new('Ground label','FONT');cu.body=g['name'];cu.size=1.0;cu.align_x='CENTER';o=bpy.data.objects.new('REVIEW '+g['id'],cu);sc.collection.objects.link(o);o.location=(x,z+2,3);cu.materials.append(K.material('M_HullNavy'))
    for path in ground['paths']:
        for a,b in zip(path['polyline'],path['polyline'][1:]):K.beam('REVIEW travel path',(a[0],a[2],.04),(b[0],b[2],.04),.07,'M_RailIvory')
    width=json.loads((folder/'validation.json').read_text())['expandedBounds'];span=width[1][0]-width[0][0]
    pathdepth=max(abs(p[2]) for path in ground['paths'] for p in path['polyline'])
    maxanchor=max(abs(g['position'][0]) for g in ground['grounds'])
    cam.location=(0,-pathdepth*.5+3,140);cam.rotation_euler=(0,0,0);cam.data.ortho_scale=max(2*maxanchor+18,(pathdepth+22)*1.6)*1.08
    sc.render.filepath=str(folder/'three-grounds-top.png');bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'Review-only.blend'));print('ART108 MAP REVIEW RENDERED',name,flush=True)
if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:];name=args[0];mode=args[1] if len(args)>1 else 'build'
    (build if mode=='build' else review)(name)
