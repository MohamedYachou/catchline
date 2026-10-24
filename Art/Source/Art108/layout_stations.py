"""Fit additive props; produce station JSON, route evidence and honest art renders.

Preview coordinates are runtime Boat x/-z/y in Blender. Hull originals untouched.
"""
import bpy, json, math, sys, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from collections import deque
sys.path.insert(0,str(Path(__file__).parent))
import build_stations as K
ROOT=K.ROOT; OUT=K.OUT
HULLS={
 'Rowboat':dict(size=[3,2],cell=1,center=[1,.5],sign=1,blocked=[[1,1]],seed=[1,0],ortho=3.2),
 'Skiff':dict(size=[5,3],cell=1,center=[2,1],sign=1,blocked=[[1,1],[2,1],[4,2],[4,1]],seed=[3,1],ortho=4.8),
 'CompactFisherV1':dict(size=[43,23],cell=.1,center=[2.1,1.1],sign=-1,blocked=[],seed=[34,11],ortho=4.8),
 'PrepFisherV1':dict(size=[57,29],cell=.1,center=[2.8,1.4],sign=-1,blocked=[],seed=[42,18],ortho=5.35),
 'Tier5DeepLines103':dict(size=[73,35],cell=.1,center=[3.6,1.7],sign=-1,blocked=[],seed=[63,30],ortho=6.15),
}
def station(id,kind,pos,tile,model=None,**kw):
    return dict(id=id,kind=kind,pos=pos,yaw=kw.pop('yaw',0),workTile=tile,**({'model':model} if model else {}),**kw)
def layouts(name):
    s=station
    if name=='Rowboat':return [
      s('sort1','SortTable',[1,.40,-.58],[1,0],'SortBoardRail',basketIn=[.60,0,-.46],basketOut=[1.40,0,-.46],mount='gunwale'),
      s('rod1','Rod',[0,.44,-.615],[0,0],basketOut=[0,0,-.46],existing=True,basketModel='BasketSmall'),
      s('rod2','Rod',[2,.44,-.615],[2,0],existing=True,optional='RodHolder',basketOut=[2,0,-.46],basketModel='BasketSmall'),
      s('bait','BaitBin',[.25,0,1.25],[0,1],existing=True),
      s('hold','HoldHatch',[1,0,1],[1,0],existing=True),
      s('nav','NavPost',[-.32,0,.85],[0,1],'NavigatorSeat',unlockTier=1,interaction='seated; seat is not a standing clearance obstacle')]
    if name=='Skiff':return [
      s('sort1','SortTable',[2.30,0,2.20],[3,2],'SortTableSmall',basketIn=[1.85,0,2.20],basketOut=[2.55,0,1.50]),
      s('rod1','Rod',[.25,.45,-.68],[0,0],existing=True,basketOut=[.25,0,-.52],basketModel='BasketSmall'),
      s('rod2','Rod',[2,.45,-.68],[2,0],existing=True,basketOut=[2,0,-.52],basketModel='BasketSmall'),
      s('rod3','Rod',[3.75,.45,-.68],[4,0],existing=True),
      s('bait','BaitBin',[.30,0,2.03],[0,1],'BaitBin'),
      s('hold','HoldHatch',[1,0,1],[1,0],existing=True),
      s('lantern','Lantern',[2.45,.58,2.20],[3,2],'Lantern',mount='sort table'),
      s('nav','NavPost',[4,.68,2],[3,1],'NavigatorPost',mount='existing console')]
    if name=='PrepFisherV1':return [
      s('sort1','SortTable',[2.20,0,2.75],[22,22],'SortTableSmall',yaw=180,basketIn=[2.0,.60,2.75],basketOut=[2.45,.60,2.75]),
      s('rod1','Rod',[2.8,.47,3.0],[28,24],existing=True,basketOut=[2.85,0,3.08],basketModel='BasketSmall'),
      s('rod2','Rod',[2.8,.47,-.2],[28,4],existing=True,basketOut=[2.35,0,-.12],basketModel='BasketSmall'),
      s('rod3','Rod',[5.0,.47,2.94],[50,24],existing=True,basketOut=[5.25,0,2.98],basketModel='BasketSmall'),
      s('net1','Net',[5.9,.4,1.6],[53,4],existing=True,basketOut=[5.65,0,1.6],basketModel='BasketLarge',replaceVisual='legacy runtime net basket'),
      s('table1','ProcessTable',[3.52,0,1.4],[42,18],existing=True,places=2,workTiles=[[42,18],[42,10]],basketIn=[2.85,0,1.4],basketOut=[3.52,0,.20],basketModel='BasketLarge'),
      s('bait','BaitBin',[1.65,0,.02],[17,5],'BaitBin'),
      s('hold','HoldHatch',[4.84,.02,1.4],[54,14],'HatchRing',existing=True),
      s('nav','NavPost',[.75,.78,1.50],[15,15],'NavigatorHelmBracket',mount='existing helm console'),
      s('lantern','Lantern',[2.20,.60,2.75],[22,22],'Lantern',mount='sort table')]
    if name=='Tier5DeepLines103':return [
      s('sort1','SortTable',[2.60,0,3.45],[26,29],'SortTableSmall',yaw=180,basketIn=[2.35,.60,3.45],basketOut=[2.85,.60,3.45]),
      s('sort2','SortTable',[6.80,0,.05],[66,6],'SortTableSmall',basketIn=[6.55,.60,.05],basketOut=[7.05,.60,.05]),
      s('rod1','Rod',[3.25,.47,3.60],[33,31],existing=True,basketOut=[3.60,0,3.55],basketModel='BasketSmall'),
      s('rod2','Rod',[3.25,.47,-.20],[33,3],existing=True,basketOut=[3.10,0,-.25],basketModel='BasketSmall'),
      s('net1','Net',[7.55,.35,.75],[67,8],existing=True,basketOut=[7.30,0,.75],basketModel='BasketLarge',replaceVisual='legacy runtime rear net basket'),
      s('table1','ProcessTable',[4.50,0,1.70],[54,22],existing=True,places=2,workTiles=[[54,22],[54,12]],basketIn=[3.80,0,1.70],basketOut=[5.35,0,1.70],basketModel='BasketSmall'),
      s('table2','ProcessTable',[5.30,0,3.50],[50,29],'ProcessingTableTwoPlace',yaw=180,places=2,workTiles=[[50,29],[57,29]],basketIn=[5.05,.64,3.50],basketOut=[5.55,.64,3.50],basketModel='BasketSmall'),
      s('cage1','Cage',[1.55,-.30,4.50],[16,31],existing=True,basketOut=[1.80,0,3.55],basketModel='BasketLarge'),
      s('cage2','Cage',[1.55,-.30,-1.10],[16,8],existing=True,basketOut=[1.30,0,.05],basketModel='BasketLarge'),
      s('line1','Line',[4.00,.46,-.17],[40,5],existing=True,basketOut=[4.00,0,.05],basketModel='BasketSmall'),
      s('line2','Line',[5.42,.46,-.17],[54,5],existing=True,basketOut=[5.42,0,.05],basketModel='BasketSmall'),
      s('line3','Line',[2.40,.46,-.17],[24,5],existing=False,optional='ThirdDeepLine',cloneSource='DeepLineRig_1',runtimeShift=[-1.6,0,0],basketOut=[2.40,0,.05],basketModel='BasketSmall'),
      s('bait','BaitBin',[2.80,0,1.70],[29,10],'BaitBin'),
      s('hold','HoldHatch',[6.15,.02,1.70],[68,25],'HatchRing',existing=True),
      s('nav','NavPost',[1.15,.78,1.84],[20,17],'NavigatorHelmBracket',mount='existing helm console'),
      s('gen','Generator',[.30,0,.50],[8,7],'GeneratorBox'),
      s('light1','DeckLight',[4.20,0,3.65],[42,31],'DeckLightMast'),
      s('light2','DeckLight',[7.00,0,3.65],[70,31],'DeckLightMast'),
      s('hauler','LineHauler',[4.80,0,-.05],[48,6],'LineHauler')]
    return [
      s('sort1','SortTable',[4.16,0,1.55],[36,12],'SortTableSmall',yaw=90,basketIn=[4.10,0,.95],basketOut=[4.10,0,2.25]),
      s('rod1','Rod',[2,.47,2.38],[21,18],existing=True,basketOut=[2.30,0,2.13],basketModel='BasketSmall'),
      s('rod2','Rod',[2,.47,-.18],[21,3],existing=True,basketOut=[2.25,0,.08],basketModel='BasketSmall'),
      s('rod3','Rod',[3.75,.47,2.33],[36,18],existing=True,basketOut=[3.40,0,2.25],basketModel='BasketSmall'),
      s('net1','Net',[4.72,.15,.40],[39,6],existing=True,basketOut=[3.85,0,.33],basketModel='BasketLarge',replaceVisual='legacy runtime net basket only'),
      s('bait','BaitBin',[1.43,0,.08],[14,5],'BaitBin'),
      s('hold','HoldHatch',[2.85,0,1.75],[29,11],'HatchRing',existing=True),
      s('nav','NavPost',[.60,.78,1.18],[13,12],'NavigatorHelmBracket',mount='existing helm console below canopy')]
def world_bb(o):return [o.matrix_world@Vector(v) for v in o.bound_box]
def to_preview(p):return Vector((p[0],-p[2],p[1]))
def load_hull(name,h):
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'Assets/Art/Models/Boats'/f'{name}.fbx'))
    hull=[o for o in bpy.context.scene.objects if o.type=='MESH']
    # The current runtime uses differently baked legacy and compact FBXs.
    cx,cz=h['center'];sg=h['sign']
    m=Matrix(((0,1,0,cx),(-sg,0,0,-cz),(0,0,1,0),(0,0,0,1)))
    for o in hull:
        o.matrix_world=m@o.matrix_world
        if o.name.startswith('RodVisual_'):o.hide_render=True
        p=o;ancestors=[]
        while p:ancestors.append(p.name);p=p.parent
        if name in ('PrepFisherV1','Tier5DeepLines103') and any(n.split('.')[0] in ('RawBuckets','RawIceCoolers','NetModule2') for n in ancestors):o.hide_render=True
    if name=='Tier5DeepLines103':
        # Review the optional third rig with all requested baskets; the source hull is unchanged.
        for o in list(hull):
            p=o;parts=[]
            while p:parts.append(p.name);p=p.parent
            if 'DeepLineRig_1' in parts:
                copy=o.copy();copy.data=o.data.copy();bpy.context.scene.collection.objects.link(copy)
                world=o.matrix_world.copy();copy.parent=None;copy.matrix_world=world;copy.location.x-=1.6;copy.name='REVIEW third rig '+o.name;hull.append(copy)
    return hull
def add_asset(model,pos,yaw=0,label=''):
    old=set(bpy.context.scene.objects)
    with bpy.data.libraries.load(str(OUT/f'{model}.blend'),link=False) as (a,b):b.objects=a.objects
    for o in b.objects:
        if o:bpy.context.scene.collection.objects.link(o)
    new=set(bpy.context.scene.objects)-old
    # Source +Y is away from operator; convert to preview's -runtime Z.
    mat=Matrix.Translation(to_preview(pos))@Matrix.Rotation(math.radians(-yaw),4,'Z')
    for o in new:
        if o.parent not in new:o.matrix_world=mat@o.matrix_world
        o.name=f'{label}_{o.name}'
    return [o for o in new if o.type=='MESH']
def segments_at(meshes):
    seg=[]
    for o in meshes:
        if o.hide_render:continue
        verts=[o.matrix_world@v.co for v in o.data.vertices]
        o.data.calc_loop_triangles()
        for t in o.data.loop_triangles:
            vs=[verts[i] for i in t.vertices]
            for height in (.20,.55,.95):
                points=[]
                for k in range(3):
                    a,b=vs[k],vs[(k+1)%3]
                    if (a.z<height)==(b.z<height) or abs(a.z-b.z)<1e-8:continue
                    p=a+(b-a)*((height-a.z)/(b.z-a.z));points.append(Vector((p.x,-p.y)))
                if len(points)>=2:seg.append(points[:2])
    return seg
def dist(p,a,b):
    d=b-a;t=max(0,min(1,(p-a).dot(d)/max(1e-12,d.length_squared)))
    return (p-a-d*t).length
def blocked_tiles(name,h,hull,props):
    blocked={tuple(p) for p in h['blocked']};w,d=h['size'];c=h['cell']
    if True:
        # A navigator sits ON the rowboat seat; never classify it as a standing obstacle.
        collision_props=[o for o in props if not (name=='Rowboat' and o.name.startswith('nav_'))]
        seg=segments_at((hull if h['cell']<1 else [])+collision_props)
        for x in range(w):
            for z in range(d):
                p=Vector((x*c,z*c))
                if any(dist(p,a,b)<.28 for a,b in seg):blocked.add((x,z))
                # Opening remains blocked even when lid rises, matching current native policy.
                nx,nz=h['center'][1]-p.y,h['center'][0]-p.x
                if name=='CompactFisherV1' and -1.25<nx<-.05 and -1.41<nz<-.09:blocked.add((x,z))
        # Low baskets require explicit filled rectangles; not just body-height slices.
        for s in layouts(name):
            for key in ('basketIn','basketOut'):
                if key not in s:continue
                b=s[key];half=(.28,.21) if s.get('basketModel')=='BasketLarge' else (.20,.15)
                for x in range(w):
                    for z in range(d):
                        dx=max(abs(x*c-b[0])-half[0],0);dz=max(abs(z*c-b[2])-half[1],0)
                        if math.hypot(dx,dz)<.28:blocked.add((x,z))
    return blocked
def reachable(h,blocked,seed):
    w,d=h['size'];seen={tuple(seed)};q=deque(seen)
    while q:
        x,z=q.popleft()
        for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
            p=x+dx,z+dz
            if 0<=p[0]<w and 0<=p[1]<d and p not in blocked and p not in seen:seen.add(p);q.append(p)
    return seen
def label(text,p,size=.115):
    cu=bpy.data.curves.new('PlanLabel','FONT');cu.body=text;cu.size=size;cu.align_x='CENTER'
    ob=bpy.data.objects.new('LABEL '+text,cu);bpy.context.scene.collection.objects.link(ob)
    ob.location=p;ob.rotation_euler.z=math.pi;cu.materials.append(K.material('M_HullNavy'));return ob
def light_and_camera(h):
    sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=24
    sc.render.resolution_x=1440;sc.render.resolution_y=900;sc.render.resolution_percentage=100
    sc.world=bpy.data.worlds.new('Cool maritime fill');sc.world.use_nodes=True
    bg=next(n for n in sc.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.39,.56,.64,1);bg.inputs[1].default_value=.55
    sc.view_settings.view_transform='AgX'
    for name,p,power,size,color in [('Warm key',(-3,-5,8),1500,6,(1,.86,.66)),('Cool fill',(5,3,6),950,5,(.68,.84,1))]:
        data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
        o=bpy.data.objects.new(name,data);sc.collection.objects.link(o);o.location=p
        o.rotation_euler=(Vector((2,-1,0))-o.location).to_track_quat('-Z','Y').to_euler()
    cam=bpy.data.cameras.new('Art review camera');o=bpy.data.objects.new('Art review camera',cam);sc.collection.objects.link(o);sc.camera=o;cam.type='ORTHO'
    return sc,o
def build(name):
    h=HULLS[name];folder=OUT/name;folder.mkdir(exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);hull=load_hull(name,h);props=[];ss=layouts(name)
    for s in ss:
        if s.get('model'):props+=add_asset(s['model'],s['pos'],s['yaw'],s['id'])
        for key in ('basketIn','basketOut'):
            if key in s:
                model=s.get('basketModel','BasketSmall')+'_0'
                props+=add_asset(model,s[key],label=s['id']+'_'+key)
    bpy.context.view_layer.update()
    blocked=blocked_tiles(name,h,hull,props);assert tuple(h['seed']) not in blocked,(name,'seed blocked')
    seen=reachable(h,blocked,h['seed'])
    (folder/'route-grid.json').write_text(json.dumps({'blocked':sorted(blocked),'reachable':sorted(seen),'grid':h['size']}))
    changes=[]
    for s in ss:
        wanted=tuple(s['workTile'])
        if wanted not in seen:
            nearest=min(seen,key=lambda p:(p[0]-wanted[0])**2+(p[1]-wanted[1])**2)
            assert math.dist(nearest,wanted)*h['cell']<=.65,(name,s['id'],wanted,nearest)
            s['workTile']=list(nearest);changes.append({'station':s['id'],'from':list(wanted),'to':list(nearest)})
        assert tuple(s['workTile']) in seen
        if 'workTiles' in s:
            adjusted=[]
            for wanted in s['workTiles']:
                nearest=tuple(wanted) if tuple(wanted) in seen else min(seen,key=lambda p:math.dist(p,wanted))
                assert math.dist(nearest,wanted)*h['cell']<=.65,(name,s['id'],'second place',wanted,nearest)
                adjusted.append(list(nearest))
            assert len({tuple(p) for p in adjusted})==s['places'],(name,s['id'],'duplicate place')
            s['workTiles']=adjusted;s['workTile']=adjusted[0]
    manifest={'schema':1,'hull':name,'coordinates':'runtime Boat-local metres; Y up; bow -X; workTile is GameData grid (x,z)',
      'grid':{'width':h['size'][0],'height':h['size'][1],'cellSize':h['cell']},
      'modelBinding':{'path':f'Assets/Art/Models/Boats/{name}.fbx','spawnPosition':[h['center'][0],0,h['center'][1]],'yaw':-90,'preserveImporterRoot':True},
      'stations':ss,'blocked':[list(p) for p in sorted(blocked)],
      'visibilityPolicy':{'disableExistingGroups':['RawBuckets','RawIceCoolers','NetModule2'] if name in ('PrepFisherV1','Tier5DeepLines103') else [],'reason':'Basket-based table route replaces loose/raw prop bins; rod/deep-line layout is the validated default. Original hull bytes untouched.'},
      'basketFillStates':['BasketSmall_0','BasketSmall_1','BasketSmall_2','BasketSmall_3','BasketLarge_0','BasketLarge_1','BasketLarge_2','BasketLarge_3'],
      'notes':['Existing=true refers to station/gear ownership; model, if present, is an additive trim or post.',
        'Never spawn both legacy baskets and these replacements. Rod3 on Skiff shares rod2 output basket by design.',
        'Paths are art validation only; native M1Checks and final Unity import acceptance remain with code owner.']}
    for row in manifest['stations']:
        if row.get('model'):row['runtimeModelId']='Art108_'+row['model']
        if row.get('basketModel'):row['runtimeBasketPrefix']='Art108_'+row['basketModel']
    manifest['runtimeBasketFillStates']=['Art108_'+id for id in manifest['basketFillStates']]
    target=ROOT/'Assets/Art/Models/Boats'/f'{name}.stations.json';target.write_text(json.dumps(manifest,indent=2))
    (folder/f'{name}.stations.json').write_text(json.dumps(manifest,indent=2))
    evidence={'hull':name,'allWorkTilesReachable':True,'seed':h['seed'],'reachableCount':len(seen),'blockedCount':len(blocked),'adjustedWorkTiles':changes,
      'hullSha256':hashlib.sha256((ROOT/'Assets/Art/Models/Boats'/f'{name}.fbx').read_bytes()).hexdigest(),
      'method':'Four-neighbour BFS; new prop mesh slices .20/.55/.95m plus .28m body and basket clearance on all grids; compact also rasterizes hull and persistent hatch opening; legacy grids preserve original blocked cells. Navigator seat is seated interaction.',
      'nativeM1Checks':'not run: not implemented by code session yet'}
    (folder/'validation.json').write_text(json.dumps(evidence,indent=2))
    # Export additive hull-local overlay only; no original hull geometry.
    bpy.ops.object.select_all(action='DESELECT')
    for ob in props:ob.select_set(True)
    bpy.ops.export_scene.fbx(filepath=str(folder/f'{name}-stations-overlay.fbx'),use_selection=True,object_types={'MESH'},axis_forward='-Z',axis_up='Y',bake_anim=False,use_triangles=True)
    sc,cam=light_and_camera(h)
    # Quiet water is presentation only, never in exported prop files.
    K.box('PREVIEW water',(h['center'][0],-h['center'][1],-.35),(80,80,.04),'M_SeaTeal',0)
    center=Vector((h['center'][0],-h['center'][1],.20))
    direction=Vector((-.405,.579,.707))
    cam.location=center+direction*30;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    cam.data.ortho_scale=h['ortho']*2*1440/900
    sc.render.filepath=str(folder/'gameplay-camera.png');bpy.ops.wm.save_as_mainfile(filepath=str(folder/f'{name}-layout.blend'))
    bpy.ops.render.render(write_still=True)
    # Labelled technical plate, bow left, port upper edge in runtime coordinates.
    per_side=(len(ss)+1)//2
    for i,s in enumerate(ss):
        p=to_preview(s['pos']);p.z=2.1
        spacing=min(1.35,9.0/max(1,per_side-1))
        tx=h['center'][0]+(i//2-(per_side-1)/2)*spacing
        ty=1.20 if i%2==0 else -2*h['center'][1]-1.20
        K.box('PREVIEW label plate',(tx,ty,2.08),(min(1.26,spacing-.04),.26,.018),'M_RailIvory',.02)
        label(s['id']+' '+str(s['workTile']),(tx,ty+.04,2.1),min(.11,spacing*.085))
        K.beam('PREVIEW leader',(p.x,p.y,2.0),(tx,ty+.07,2.0),.008,'M_RailIvory')
    for s in ss:
        p=s['workTile'];c=h['cell'];K.torus('PREVIEW work tile',(p[0]*c,-p[1]*c,.04),.09,.012,'M_SeaTeal')
    cam.location=(h['center'][0],-h['center'][1],18);cam.rotation_euler=(0,0,math.pi)
    cam.data.ortho_scale=8.2 if name=='Rowboat' else 13.5 if len(ss)>10 else 10.4
    sc.render.filepath=str(folder/'top-plan.png');bpy.ops.render.render(write_still=True)
    print('ART108 LAYOUT PASSED',name,json.dumps(evidence))
if __name__=='__main__':
    for name in (sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else HULLS):build(name)
