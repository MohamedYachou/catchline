"""Bind individually reviewed MAP8 evidence; keep contract failures explicit."""
import hashlib, json, re, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
SCRATCH=ROOT.parent/'Catchline-sim'
ART=ROOT/'Art/Models/Maps/GullLighthouseRock'
E=ROOT/'docs/screens/map8-lighthouse-rock-1'
IMPORT=ROOT/'Assets/Art/Models/Environment/GullLighthouseRock'
TASK='MAP8-LIGHTHOUSE-ROCK-1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def logtext(p):
    data=p.read_bytes()
    return data.decode('utf-16' if data.startswith((b'\xff\xfe',b'\xfe\xff')) else 'utf-8-sig')
def write(p,v):p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def utc():return datetime.now(timezone.utc).isoformat()

def preflight():
    metas=list(IMPORT.glob('*.meta'))+[IMPORT.with_suffix('.meta'),ROOT/'Assets/Editor/LighthouseRockMapChecks.cs.meta',ROOT/'Assets/Scripts/Game/Map8Capture.cs.meta']
    all_guids={}
    for p in (ROOT/'Assets').rglob('*.meta'):
        match=re.search(r'^guid: ([a-f0-9]{32})$',p.read_text(encoding='utf-8-sig'),re.M)
        if match:all_guids.setdefault(match[1],[]).append(p)
    for p in metas:
        guid=re.search(r'^guid: ([a-f0-9]{32})$',p.read_text(encoding='utf-8-sig'),re.M)[1]
        assert len(all_guids[guid])==1,(p,all_guids[guid])
    links=0
    for report in [ART/'REPORT.md',E/'README.md']:
        for target in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8-sig')):
            if not target.startswith(('http:','https:','#')):assert (report.parent/target).resolve().exists(),target;links+=1
    print('PREFLIGHT PASS',len(metas),'unique GUIDs',links,'report links')

def age_snapshot():
    before=read(E/'safety-source/source-hashes.json')['files'];diff=[]
    for name,record in before.items():
        p=SCRATCH/name
        if sha(p)!=record['sha256']:diff.append(name)
    for name in ['Assets/Scripts/Game/Data/Grounds.cs','Assets/Scripts/Game/Sea/SeaNav.cs']:
        assert name not in diff, 'Geometry/pool input changed; assess full route evidence: '+name
    rel=IMPORT.relative_to(ROOT)
    assert (rel/'grounds.json').as_posix() not in diff
    old=read(E/'safety-source'/rel/'navigation.json');new=read(SCRATCH/rel/'navigation.json')
    assert {k:v for k,v in old.items() if k!='lifeAnchors'}=={k:v for k,v in new.items() if k!='lifeAnchors'}
    assert old['lifeAnchors'][3:6]==new['lifeAnchors'][3:6]
    assert read(ART/'SeaV2-anchor-fix-audit.json')['allPassed']
    files={}
    paths=list((SCRATCH/'Assets/Scripts/Game').rglob('*.cs'))+[SCRATCH/'Assets/Editor/LighthouseRockMapChecks.cs']
    paths += [SCRATCH/rel/n for n in ['GullLighthouseRockSeaV2.fbx','navigation.json','grounds.json']]
    paths += list((SCRATCH/'Assets/Resources/Shaders').rglob('*.*'))
    for p in paths:
        rel=p.relative_to(SCRATCH);target=E/'postintegration-source'/rel
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        assert sha(target)==sha(p)
        files[rel.as_posix()]={'sha256':sha(p),'bytes':p.stat().st_size}
    write(E/'postintegration-source/source-hashes.json',dict(utc=utc(),files=files,changedSinceFullSafety=diff,scope='Actual post-integration scratch inputs; original full safety snapshot retained separately. Three elevated puffin shelves/anchors and the off-rock buoy anchor changed; every navigation field other than these life anchors and all ground/pool data unchanged.'))
    print('POST-INTEGRATION INPUTS',len(files),'changed from full safety',diff)

def snapshot():
    paths=list((SCRATCH/'Assets/Scripts/Game').rglob('*.cs'))
    paths += [SCRATCH/'Assets/Editor/LighthouseRockMapChecks.cs']
    paths += [SCRATCH/IMPORT.relative_to(ROOT)/n for n in ['GullLighthouseRockSeaV2.fbx','navigation.json','grounds.json']]
    files={}
    for p in paths:
        rel=p.relative_to(SCRATCH);target=E/'safety-source'/rel
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        files[rel.as_posix()]={'sha256':sha(target),'bytes':target.stat().st_size}
        assert sha(p)==sha(target)
    write(E/'safety-source/source-hashes.json',dict(utc=utc(),files=files,scope='Actual scratch inputs copied while the exclusive MAP8 check runs; later main changes do not rewrite this snapshot.'))
    print('SAFETY INPUT SNAPSHOT',len(files))

def art_review():
    notes={
        'the-pinnacle-day':'Broken grey/lichen triangular ridge surfaces in both lower corners. Hull and casting space clear; central lighthouse outside deck crop.',
        'the-pinnacle-night':'Dim but visible low angular corner silhouettes; lit boat remains separate. No baked life or foam.',
        'tide-race-day':'Both low ridge shelves have varied grey/wet/lichen faces; full lighthouse and external tide-race life outside this isolated terrain preview.',
        'tide-race-night':'Low corner ridges remain distinguishable against dark water; this still does not prove runtime race/glow.',
        'deep-ledge-day':'Two angular grey corner shelves frame clear boat water; broad cap replaced by unequal-height triangular ridge faces.',
        'deep-ledge-night':'Dark low corner ledges remain visible; no hull overlap. Buoy is an empty in terrain export.',
        'wide-day':'A lone angular stack carries white/red lighthouse and keeper cottage, surrounded by open ocean and small ground ledges. Distant freighter silhouettes outside border.',
        'wide-night':'Lighthouse/stack silhouette visible at wide scale; runtime lamp emission belongs to lead integration.',
        'top-base':'Top view shows single main stack, six close corner rocks, bathymetry and outer boundary buoys. No broad horizon islands.',
        'navigation-plate':'Real waterline/shallow contours, harbour/three grounds/routes and retained full-circle conflicts visible.',
        'review-sheet':'Overview of final terrain cameras and map bounds; individual source images also opened.',
        'stack-detail':'Tall white/red tower, lantern gallery, keeper cottage and stepped granite stack visible; lower puffin shelves are empty anchors.'}
    images={}
    for name in notes:
        p=ART/f'SeaV2-{name}.png'
        with Image.open(p) as im:assert min(im.size)>0
        images[p.name]=sha(p)
    assert len(list(ART.glob('*.png')))==12
    write(ART/'SeaV2-visual-review.json',dict(task=TASK,reviewer='Codex 1 (Windows app)',utc=utc(),allIndividuallyOpened=True,images=images,observations=notes,acceptedByLead=False,scope='Twelve final PNGs individually opened with view_image; manual author review, not lead/player acceptance.'))
    print('ART REVIEW BOUND',len(images))

def native_review():
    notes={
        'chart':'Chart overview and Lighthouse rock purchase UI inspected at both sizes; record exact lead integration/crop limits in README.',
        'sail-out':'Normal trip SeaOut presentation inspected; route/progress/hull/HUD visible.',
        'the-pinnacle':'Native anchor view inspected for broken corner rocks, hull/bubble clearance and readable controls.',
        'tide-race':'Native Tide race view inspected for both corner rocks and available life; stills alone do not prove animation.',
        'deep-ledge':'Native Deep ledge view inspected for corner terrain, clear hull/bubbles and available buoy presentation.'}
    images={}
    for stage in notes:
        for w,h in [(1440,900),(844,390)]:
            p=E/f'{stage}-{w}.png'
            with Image.open(p) as im:assert im.size==(w,h)
            images[p.name]=sha(p)
    write(E/'native-visual-review.json',dict(task=TASK,reviewer='Codex 1 (Windows app)',utc=utc(),allIndividuallyOpened=True,imageHashes=images,observations=notes,acceptedByLead=False,scope='Ten final native PNGs individually opened; detailed findings/limits in README.'))
    print('NATIVE REVIEW BOUND',len(images))

def life_review():
    images={}
    for p in sorted(list(E.glob('perch-*.png'))+list((E/'life-check').glob('*.png'))):
        with Image.open(p) as im:assert im.size==(1440,900)
        images[p.relative_to(E).as_posix()]=sha(p)
    assert len(images)==10
    write(E/'life-visual-review.json',dict(task=TASK,utc=utc(),allIndividuallyOpened=True,imageHashes=images,observations='All three outward ledges support visible puffin groups and the separate animated bird in both deck/top views; no rock occludes them. Required production LighthouseLifeChecks map/puffin2/tide-race/lamp views individually opened. Bright white perch tops reflect the production review lighting; animation is not established by stills.',acceptedByLead=False))
    print('LIFE REVIEW BOUND',len(images))

def final():
    preflight()
    audit=read(ART/'SeaV2-audit.json');src=read(ART/'SeaV2-source-audit.json');v=read(ART/'SeaV2-validation.json')
    fail=[c for c in audit['checks'] if not c['passed']]
    assert len(audit['checks'])==61 and len(fail)==6 and all('full zone' in c['check'] for c in fail)
    assert src['allPassed'] and src['totalChecks']==57 and v['allPassed'] and v['triangles']==21830
    anchor=read(ART/'SeaV2-anchor-fix-audit.json')
    assert anchor['allPassed'] and anchor['unchangedNavigationExceptLifeAnchors'] and anchor['buoyRockClearance']>1.3
    assert anchor['sourceSha256']==sha(ART/'GullLighthouseRockSeaV2.blend')
    assert len(anchor['checks'])==3 and sum(c['samples'] for c in anchor['checks'])==84
    assert sha(ART/'GullLighthouseRockSeaV2.blend')==v['sourceSha256']
    for name,key in [('GullLighthouseRockSeaV2.fbx','fbxSha256'),('navigation.json','navigationSha256')]:
        assert sha(ART/name)==v[key]==sha(IMPORT/name)==sha(SCRATCH/IMPORT.relative_to(ROOT)/name)
    assert sha(ART/'grounds.json')==sha(IMPORT/'grounds.json')
    for record in read(E/'protected-map-files.json'):
        p=ROOT/record['path'];assert sha(p).upper()==record['sha256'].upper() and p.stat().st_size==record['bytes'],p
    ar=read(ART/'SeaV2-visual-review.json');nr=read(E/'native-visual-review.json')
    assert ar['allIndividuallyOpened'] and len(ar['images'])==12
    assert nr['allIndividuallyOpened'] and len(nr['imageHashes'])==10
    for folder,images in [(ART,ar['images']),(E,nr['imageHashes'])]:
        for name,digest in images.items():assert sha(folder/name)==digest,name
    check=read(E/'map8-checks.json')
    assert (check['maps'],check['hullRoutes'],check['lanes'])==(8,480,24)
    assert all(check[k] for k in ['assets','chartPurchase','anchors','groundPoolsReady'])
    assert check['groundIds']==['the-pinnacle','tide-race','deep-ledge']
    assert len(check['trips'])==4 and all('PASS' in t for t in check['trips'])
    assert all('bait-cast/home PASS' in t for t in check['trips'][1:])
    log=(E/'check-map8-safety-build.log').read_text(encoding='utf-8-sig')
    for marker in ['MAP8 CHECKS PASSED','MAP8 TEST BUILD PASSED','480 directed hull routes','24 sea lanes clear','Application will terminate with return code 0']:assert marker in log,marker
    assert 'Verified map8-safety-build (Unity exit 0)' in (E/'safety-build-wrapper.log').read_text(encoding='utf-8-sig')
    assert not re.search(r'error CS\d|MAP8 check failed|NullReferenceException',log)
    post=read(E/'map8-postintegration-checks.json')
    assert (post['maps'],post['hullRoutes'],post['lanes'])==(8,0,3)
    assert len(post['trips'])==3 and all('bait-cast/home PASS' in t for t in post['trips'])
    postlog=(E/'check-map8-postintegration.log').read_text(encoding='utf-8-sig')
    for marker in ['MAP8 POST-INTEGRATION PASSED','MAP8 TEST BUILD PASSED','Application will terminate with return code 0']:assert marker in postlog,marker
    assert 'Verified map8-postintegration (Unity exit 0)' in logtext(E/'postintegration-wrapper.log')
    assert not re.search(r'error CS\d|MAP8 check failed|NullReferenceException',postlog)
    lifelog=(E/'life-check/check-map8-lighthouse-life.log').read_text(encoding='utf-8-sig')
    assert 'LIGHTHOUSELIFE PASS' in lifelog and 'System.Exception:' not in lifelog
    # Production method calls EditorApplication.Exit directly; check.ps1 records
    # its actual process exit even though the generic snapshot sentinel is absent.
    assert 'Unity exit 0' in logtext(E/'lighthouse-life-wrapper.log')
    lr=read(E/'life-visual-review.json')
    assert lr['allIndividuallyOpened'] and len(lr['imageHashes'])==10
    for name,digest in lr['imageHashes'].items():assert sha(E/name)==digest,name
    for folder in ['safety-source','postintegration-source']:
        for name,record in read(E/folder/'source-hashes.json')['files'].items():
            p=E/folder/name;assert sha(p)==record['sha256'] and p.stat().st_size==record['bytes'],p
    run=read(E/'native-run.json');exitrec=read(E/'native-exit.json')
    assert run['sessionOnly'] and exitrec['exitCode']==0
    assert run['sourceCount']==125 and not run['mainDriftAtLaunch']
    nlog=(E/'native.log').read_text(encoding='utf-8-sig')
    assert 'TEST / no save reads or writes' in nlog and 'MAP8 NATIVE CAPTURES COMPLETE' in nlog
    assert not re.search(r'Exception:|Error:|Assertion failed',nlog)
    assert len((E/'capture-complete.txt').read_text().strip().splitlines())==10
    launch=datetime.fromisoformat(run['launchedUtc'].replace('Z','+00:00')).timestamp()
    for name in nr['imageHashes']:assert (E/name).stat().st_mtime>=launch
    build=SCRATCH/'Builds/Map8Capture'
    for name,key in [('Catchline.exe','exeSha256'),('Catchline_Data/Managed/Assembly-CSharp.dll','assemblySha256'),('Catchline_Data/level0','sceneLevel0Sha256')]:assert sha(build/name).upper()==run[key].upper()
    limits=[
        'Six full-ground-circle exclusions retained as FAIL; required 6-12m corner landmarks intersect inherited 12-20m circles. Actual navigation checked independently. Lead contract/visual acceptance pending.',
        'Central lighthouse/cottage visible in wide and detail art views, outside tight deck camera crops; low grey ridges frame fishing grounds.',
        'Native source snapshot and source-age differences are bound in native-run.json; see README for chart/water/life readiness and exact visual limits.',
        'Native stills do not prove animation, physical touch, installed-player behavior or caught-fish yield. Fishing checks prove normal bait/cast into water and return home.',
        'MapNav timing advisories retained; route collision, border and lane results are separate.']
    write(ART/'SeaV2-delivery.json',dict(task=TASK,utc=utc(),terrainComplete=True,importComplete=True,sourceChecks=57,artPassed=55,artTotal=61,retainedFailures=fail,maps=8,directedHullRoutes=480,seaLanes=24,newGroundTrips=3,reviewedArtImages=12,reviewedNativeImages=10,triangles=21830,namedEmptyLifeAnchors=7,acceptance='PARTIAL: own delivery complete, lead acceptance/integration limits in REPORT and README.',limits=limits))
    paths=set(p for p in ART.iterdir() if p.is_file())
    paths.update(p for p in E.rglob('*') if p.is_file() and p.name!='verification-receipt.json')
    paths.update(p for p in IMPORT.iterdir() if p.is_file());paths.add(IMPORT.with_suffix('.meta'))
    paths.update(p for p in (ROOT/'Art/Source/Art108').glob('map8*') if p.is_file())
    paths.update(ROOT/'Art/Source/Art108'/n for n in ['sea_v2_layouts.py','build_sea_v2.py','audit_sea_v2.py','verify_sea_v2_sources.py'])
    for rel in ['Assets/Editor/LighthouseRockMapChecks.cs','Assets/Scripts/Game/Map8Capture.cs']:
        paths.update([ROOT/rel,ROOT/(rel+'.meta')])
    paths.update(ROOT/'Assets/Scripts/Game'/n for n in ['GameData.cs','Data/Grounds.cs','Sea/SeaNav.cs','VoyageScenery.cs'])
    paths.update(build/n for n in ['Catchline.exe','UnityPlayer.dll','Catchline_Data/Managed/Assembly-CSharp.dll','Catchline_Data/level0'])
    links=0
    for report in [ART/'REPORT.md',E/'README.md']:
        for target in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8-sig')):
            if not target.startswith(('http:','https:','#')):assert (report.parent/target).resolve().exists(),target;links+=1
    files={}
    for p in sorted(paths):
        assert p.is_file()
        try:key=p.relative_to(ROOT).as_posix()
        except ValueError:key=p.as_posix()
        files[key]=dict(sha256=sha(p),bytes=p.stat().st_size)
    write(E/'verification-receipt.json',dict(task=TASK,owner='Codex 1 (Windows app)',utc=utc(),files=files,localLinks=links,limits=limits,retainedFailures=fail,overallAcceptance='PARTIAL; lead decision external.',checks=dict(maps=8,hullRoutes=480,lanes=24,newGroundTrips=3,artImages=12,nativeImages=10,sourceChecks=57),nativeBuild=run,noGit=True,noSubagents=True,noPlayerSaveAccess=True,noInstalledPlayerReplacement=True,noMainUnityBatchmode=True))
    independent()

def independent():
    receipt=read(E/'verification-receipt.json')
    for name,expected in receipt['files'].items():
        p=Path(name) if Path(name).is_absolute() else ROOT/name
        assert sha(p)==expected['sha256'] and p.stat().st_size==expected['bytes'],name
    print('RECEIPT READBACK PASS',len(receipt['files']),'files',receipt['localLinks'],'links',sha(E/'verification-receipt.json'))

if __name__=='__main__':
    {'snapshot':snapshot,'age':age_snapshot,'preflight':preflight,'art':art_review,'native':native_review,'life':life_review,'final':final,'readback':independent}[sys.argv[-1]]()
