"""Independent geometry/clearance audit and dimensioned plates. System Python.

python ... MAP [--publish] --publish only after all nine images + plate opened.
Requires Shapely and Pillow. Does not invoke Unity or write code/scenes/metas.
"""
import sys,json,math,hashlib,heapq,shutil,itertools
from pathlib import Path
from shapely.geometry import Point,Polygon,LineString
from shapely.ops import unary_union
from PIL import Image,ImageDraw,ImageFont
from sea_v2_layouts import LAYOUTS
ROOT=Path(__file__).resolve().parents[3]

def xy(p):return p['x'],p['z']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def font(size,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('segoeuib.ttf' if bold else 'segoeui.ttf'),size)

def routes(nav,radius):
    obstacles=unary_union([Polygon([xy(p) for p in a['vertices']]).buffer(radius,join_style='mitre') for a in nav['islands']])
    # Candidate vertices just outside true inflated obstacles, for conservative tangencies.
    outlines=obstacles.buffer(.03,join_style='mitre');parts=list(outlines.geoms) if hasattr(outlines,'geoms') else [outlines]
    border=Polygon([xy(p) for p in nav['border']]).buffer(-radius)
    nodes=[xy(nav['harbour'])]+[xy(g['centre']) for g in nav['grounds']]
    nodes += [p for ob in parts for p in list(ob.exterior.coords)[:-1] if border.covers(Point(p))]
    edges=[[] for _ in nodes]
    for i,a in enumerate(nodes):
        for j in range(i+1,len(nodes)):
            b=nodes[j];line=LineString([a,b])
            if not obstacles.intersects(line) and border.covers(line):
                d=math.dist(a,b);edges[i].append((j,d));edges[j].append((i,d))
    result=[]
    for a,b in itertools.combinations(range(4),2):
        queue=[(0,a)];dist={a:0};prev={}
        while queue:
            d,u=heapq.heappop(queue)
            if d!=dist[u]:continue
            if u==b:break
            for v,c in edges[u]:
                if d+c<dist.get(v,math.inf):dist[v]=d+c;prev[v]=u;heapq.heappush(queue,(d+c,v))
        assert b in dist,('no route',a,b,radius)
        path=[b]
        while path[-1]!=a:path.append(prev[path[-1]])
        path=[nodes[i] for i in reversed(path)]
        assert all(not obstacles.intersects(LineString([p,q])) for p,q in zip(path,path[1:]))
        direct=LineString([nodes[a],nodes[b]]);blocked=obstacles.intersects(direct)
        ratio=dist[b]/direct.length
        assert blocked or ratio<=1.6+1e-6
        result.append(dict(fromIndex=a,toIndex=b,radius=radius,length=round(dist[b],3),direct=round(direct.length,3),ratio=round(ratio,4),directBlocked=blocked,polyline=path))
    return result

def audit(name):
    folder=ROOT/'Art/Models/Maps'/name;nav=json.loads((folder/'navigation.json').read_text());rec=json.loads((folder/'SeaV2-validation.json').read_text())
    checks=[]
    def check(label,passed,detail=None):
        checks.append(dict(check=label,passed=bool(passed),detail=detail))
    check('saved source SHA256',sha(folder/f'{name}SeaV2.blend')==rec['sourceSha256'])
    check('actual FBX SHA256',sha(folder/f'{name}SeaV2.fbx')==rec['fbxSha256'])
    check('navigation SHA256',sha(folder/'navigation.json')==rec['navigationSha256'])
    check('actual FBX triangle and vertex roundtrip',rec['allPassed'] and rec['triangles']==rec['actualFbxTriangles'] and rec['roundTripMaxVertexError']<.0001,rec['roundTripMaxVertexError'])
    border=Polygon([xy(p) for p in nav['border']]);w,h=LAYOUTS[name]['size']
    check('approved playable dimensions',border.bounds==(-w/2,-h/2,w/2,h/2))
    legacy=json.loads((folder/'grounds.json').read_text())['grounds']
    check('three original ground IDs, names, depths and pool IDs retained',
          len(nav['grounds'])==3 and [(g['id'],g['name'],g['nominalDepth'],g['poolId']) for g in nav['grounds']]==
          [(g['id'],g['name'],g['seabedDepth'],g['poolId']) for g in legacy])
    polys={}
    for field in ('islands','shallows'):
        for p in nav[field]:
            poly=Polygon([xy(q) for q in p['vertices']]);polys[p['id']+'-'+field]=poly
            check(field+':'+p['id']+' valid, simple, CCW, <=64 vertices',poly.is_valid and poly.exterior.is_simple and poly.exterior.is_ccw and len(p['vertices'])<=64,len(p['vertices']))
            check(field+':'+p['id']+' actual terrain-slice provenance',p['sourceObject'].startswith('Terrain_') and p['sliceY']==(0 if field=='islands' else -1))
    islands=unary_union([Polygon([xy(p) for p in a['vertices']]) for a in nav['islands']]);inflated=islands.buffer(2)
    shallows=unary_union([Polygon([xy(p) for p in a['vertices']]) for a in nav['shallows']])
    check('each island contained in its shallow shelf',shallows.buffer(.001).covers(islands))
    for g in nav['grounds']:
        c=Point(xy(g['centre']));zone=c.buffer(g['radius'],quad_segs=128)
        check(g['id']+' full zone clear of islands +2m',not inflated.intersects(zone),round(islands.distance(c)-g['radius'],3))
        check(g['id']+' full zone outside shallows (anchoring)',not shallows.intersects(zone),round(shallows.distance(c)-g['radius'],3))
        check(g['id']+' full zone inside border',border.covers(zone))
        check(g['id']+' 12-20m radius',12<=g['radius']<=20)
        check(g['id']+' art review anchor inside its zone',c.distance(Point(xy(nav['artReviewAnchors'][g['id']])))<=g['radius'])
    hp=Point(xy(nav['harbour']));check('harbour clear of island inflation2m',not inflated.intersects(hp),round(islands.distance(hp),3))
    check('harbour outside shallows',not shallows.intersects(hp));check('harbour inside border',border.contains(hp))
    buoys=[xy(b['position']) for b in nav['outerBuoys']]
    spacing=[math.dist(a,b) for a,b in zip(buoys,buoys[1:]+buoys[:1])]
    check('outer buoy spacing25-30m',all(25-1e-5<=s<=30+1e-5 for s in spacing),[min(spacing),max(spacing)])
    check('outer buoy bases clear of islands +2m',all(not inflated.intersects(Point(b).buffer(.6)) for b in buoys))
    check('outer buoys on border',all(border.boundary.distance(Point(b))<.0001 for b in buoys),len(buoys))
    check('horizon centres beyond border',all(not border.covers(Point(xy(o['centre']))) for o in nav['fog']['horizonSilhouettes']))
    allroutes=[]
    for radius in (2,4):
        try:
            rr=routes(nav,radius);allroutes.extend(rr);check('all6 harbour/ground routes exist with continuous clearance at radius'+str(radius),True)
        except AssertionError as e:check('routes at radius'+str(radius),False,str(e))
    check('at least one land-blocked ground pair',any(r['radius']==2 and r['fromIndex']>0 and r['directBlocked'] for r in allroutes))
    baseline=json.loads((ROOT/'Art/Source/Art108/sea_v2_protected_baseline.json').read_text())
    changed=[p for p,d in baseline.items() if not (ROOT/p).exists() or sha(ROOT/p)!=d]
    check('all114 pre-existing protected file bytes preserved',not changed,changed)
    result=dict(map=name,allPassed=all(c['passed'] for c in checks),checks=checks,routes=allroutes,
      sourceSha256=rec['sourceSha256'],fbxSha256=rec['fbxSha256'],navigationSha256=rec['navigationSha256'],
      limits='Art-side static geometry and 2m/4m disc visibility routes; not native turning/speed/hull acceptance. Full gameplay camera remains orthographic10.24m.')
    (folder/'SeaV2-audit.json').write_text(json.dumps(result,indent=2))
    print(name,'PASS' if result['allPassed'] else 'FAIL',len(checks),'checks')
    for c in checks:
        if not c['passed']:print('FAIL',c['check'],c['detail'])
    return nav,result

def dashed(draw,a,b,fill,width=3,dash=15):
    d=math.dist(a,b)
    for i in range(0,int(d),dash*2):
        t=i/d;u=min(1,(i+dash)/d);draw.line([(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t),(a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)],fill=fill,width=width)

def plate(name,nav,rec):
    folder=ROOT/'Art/Models/Maps'/name;base=folder/'SeaV2-top-base.png'
    if not base.exists():return
    im=Image.open(base).convert('RGBA');layer=Image.new('RGBA',im.size);draw=ImageDraw.Draw(layer)
    w,h=LAYOUTS[name]['size'];scale=1800/(w*1.24)
    def pos(p):return (900+p[0]*scale,700-p[1]*scale)
    for p in nav['shallows']:
        v=[pos(xy(a)) for a in p['vertices']];draw.polygon(v,fill=(240,213,142,45));draw.line(v+[v[0]],fill=(250,220,149,245),width=3)
    for p in nav['islands']:
        v=[pos(xy(a)) for a in p['vertices']];draw.line(v+[v[0]],fill=(243,240,220,255),width=4)
    v=[pos(xy(a)) for a in nav['border']];draw.line(v+[v[0]],fill=(233,111,60,255),width=3)
    for b in nav['outerBuoys']:
        x,y=pos(xy(b['position']));draw.ellipse((x-4,y-4,x+4,y+4),fill='#F3F0DC',outline='#C84B39',width=2)
    for r in rec['routes']:
        if r['radius']!=2 or r['fromIndex']==0:continue
        a,b=pos(r['polyline'][0]),pos(r['polyline'][-1]);color='#F2AD70' if r['directBlocked'] else '#C8E9DF'
        dashed(draw,a,b,color,3)
        ang=math.atan2(b[1]-a[1],b[0]-a[0]);tip=(a[0]+(b[0]-a[0])*.58,a[1]+(b[1]-a[1])*.58)
        draw.polygon([tip,(tip[0]-14*math.cos(ang-.5),tip[1]-14*math.sin(ang-.5)),(tip[0]-14*math.cos(ang+.5),tip[1]-14*math.sin(ang+.5))],fill=color)
        if r['directBlocked']:
            pp=[pos(p) for p in r['polyline']];draw.line(pp,fill='#F3F0DC',width=4)
    for i,g in enumerate(nav['grounds']):
        x,y=pos(xy(g['centre']));r=g['radius']*scale
        draw.ellipse((x-r,y-r,x+r,y+r),fill=(100,199,196,38),outline='#F3DEA1',width=4)
        draw.ellipse((x-12,y-12,x+12,y+12),fill='#E36A35');draw.text((x,y-1),str(i+1),font=font(16,True),fill='#173F57',anchor='mm')
        label=g['name'];box=draw.textbbox((0,0),label,font=font(24,True));tw=box[2]
        yy=y+r+18;draw.rounded_rectangle((x-tw/2-12,yy-4,x+tw/2+12,yy+34),radius=8,fill='#F4EFE3')
        draw.text((x,yy),label,anchor='mt',font=font(24,True),fill='#173F57')
    x,y=pos(xy(nav['harbour']));draw.rectangle((x-9,y-9,x+9,y+9),fill='#E36A35',outline='#F3F0DC',width=2);draw.text((x-16,y-22),'Harbour',anchor='rb',font=font(21,True),fill='#F3F0DC')
    im=Image.alpha_composite(im,layer).convert('RGB');draw=ImageDraw.Draw(im)
    draw.rectangle((0,0,1800,105),fill='#F4EFE3');draw.text((38,18),LAYOUTS[name]['title'].upper()+' / NAVIGABLE SEA',font=font(34,True),fill='#173F57')
    draw.text((40,66),f'{w} x {h} m  /  3 anchor zones  /  {len(nav["islands"])} terrain outlines  /  {len(nav["outerBuoys"])} red-white outer markers',font=font(23),fill='#173F57')
    draw.rectangle((0,1275,1800,1400),fill='#F4EFE3')
    draw.text((38,1290),'IVORY  waterline    SAND  -1m shallow shelf    GOLD  anchor zones    ORANGE  border + blocked direct line',font=font(24,True),fill='#173F57')
    draw.text((38,1328),'Dashed arrows connect every ground pair. Solid ivory = verified detour around a land obstruction (2m disc).',font=font(23),fill='#173F57')
    draw.text((38,1365),'World X right / Z up. Navigation outlines from saved mesh slices. Native sailing and water acceptance pending.',font=font(21),fill='#173F57')
    # 40m scale bar, guaranteed metric under the orthographic source.
    x,y=1320,1215;draw.line([(x,y),(x+40*scale,y)],fill='#F3F0DC',width=5);draw.text((x,y-8),'40 m',font=font(22,True),fill='#F3F0DC',anchor='lb')
    im.save(folder/'SeaV2-navigation-plate.png')

def sheet(name,nav):
    folder=ROOT/'Art/Models/Maps'/name
    names=[f'SeaV2-{g["id"]}-{time}.png' for g in nav['grounds'] for time in ('day','night')]+['SeaV2-wide-day.png','SeaV2-wide-night.png']
    if not all((folder/p).exists() for p in names):return
    im=Image.new('RGB',(1440,2020),'#F4EFE3');d=ImageDraw.Draw(im)
    d.text((24,14),LAYOUTS[name]['title']+' / SeaV2 / art camera review',font=font(28,True),fill='#173F57')
    for i,p in enumerate(names):
        tile=Image.open(folder/p).convert('RGB');tile.thumbnail((720,450));x=(i%2)*720;y=62+(i//2)*486;im.paste(tile,(x,y))
        d.text((x+12,y+455),p.replace('SeaV2-','').replace('.png',''),font=font(21),fill='#173F57')
    im.save(folder/'SeaV2-review-sheet.png')

def publish(name,nav,rec):
    assert rec['allPassed'],'do not publish failed navigation'
    folder=ROOT/'Art/Models/Maps'/name;game=ROOT/'Assets/Art/Models/Environment'/name
    reviewed=json.loads((folder/'SeaV2-visual-review.json').read_text())
    assert reviewed['allIndividuallyOpened'] and all(sha(folder/p)==d for p,d in reviewed['imageHashes'].items()),'stale or missing visual review'
    for p in [f'{name}SeaV2.fbx','navigation.json']:
        target=game/p
        assert not target.exists() or sha(target)==sha(folder/p),'refuse replacement of changed runtime file '+str(target)
        if not target.exists():shutil.copyfile(folder/p,target)
    paths=[f'SeaV2-{g["id"]}-{t}.png' for g in nav['grounds'] for t in ('day','night')]+['SeaV2-wide-day.png','SeaV2-wide-night.png','SeaV2-top-base.png','SeaV2-navigation-plate.png','SeaV2-review-sheet.png']
    for p in paths:
        with Image.open(folder/p) as im:im.load()
    receipt=dict(map=name,runtimeHashes={str(game/p).replace('\\','/'):sha(game/p) for p in [f'{name}SeaV2.fbx','navigation.json']},renderHashes={p:sha(folder/p) for p in paths},openedByLead='See comms per-map visual checkpoint; existence/decoding is not visual acceptance.',published=True)
    (folder/'SeaV2-delivery.json').write_text(json.dumps(receipt,indent=2))
    print('PUBLISHED',name)

if __name__=='__main__':
    name=sys.argv[1];nav,rec=audit(name);plate(name,nav,rec);sheet(name,nav)
    if '--publish' in sys.argv:publish(name,nav,rec)
    sys.exit(0 if rec['allPassed'] else 1)
