"""Hash-bound scratch input and image evidence for MAP9, without save access."""
import json,hashlib,shutil,sys,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[3]
SCRATCH=ROOT.parent/'Catchline-sim'
E=ROOT/'docs/screens/map9-whale-shelf-1'
ART=ROOT/'Art/Models/Maps/GullWhaleShelf'
IMPORT=Path('Assets/Art/Models/Environment/GullWhaleShelf')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def snapshot(folder='safety-source'):
    paths=list((SCRATCH/'Assets/Scripts/Game').rglob('*.cs'))+[SCRATCH/'Assets/Editor/WhaleShelfMapChecks.cs']
    paths += [SCRATCH/IMPORT/n for n in ['GullWhaleShelfSeaV2.fbx','navigation.json','grounds.json']]
    paths += [p for p in (SCRATCH/'Assets/Resources/Shaders').rglob('*') if p.is_file()]
    files={}
    for p in paths:
        rel=p.relative_to(SCRATCH);dest=E/folder/rel
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        assert sha(p)==sha(dest)
        files[rel.as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
    write(E/folder/'source-hashes.json',dict(utc=datetime.now(timezone.utc).isoformat(),files=files,scope='Actual scratch inputs copied during exclusive MAP9 safety/build run. Later geometry/main updates do not rewrite this snapshot.'))
    print('SNAPSHOT',len(files))
def preflight():
    targets=list((ROOT/IMPORT).glob('*.meta'))+[(ROOT/IMPORT).with_suffix('.meta'),ROOT/'Assets/Editor/WhaleShelfMapChecks.cs.meta',ROOT/'Assets/Scripts/Game/Map9Capture.cs.meta']
    guids={}
    for p in (ROOT/'Assets').rglob('*.meta'):
        m=re.search(r'^guid: ([a-f0-9]{32})$',p.read_text(encoding='utf-8-sig'),re.M)
        if m:guids.setdefault(m[1],[]).append(p)
    for p in targets:
        guid=re.search(r'^guid: ([a-f0-9]{32})$',p.read_text(encoding='utf-8-sig'),re.M)[1]
        assert len(guids[guid])==1,(p,guids[guid])
    for name in ['GullWhaleShelfSeaV2.fbx','navigation.json','grounds.json']:assert sha(ART/name)==sha(ROOT/IMPORT/name),name
    count=0
    for p in [ART/'REPORT.md',E/'README.md']:
        for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8-sig')):
            if not link.startswith(('http:','https:','#')):assert (p.parent/link).resolve().exists(),link;count+=1
    print('PREFLIGHT PASS',len(targets),'unique import/fixture GUIDs,',count,'local links; imported bytes match')

def art_review():
    from PIL import Image
    paths=sorted(ART.glob('*.png'))
    assert len(paths)==17,len(paths)
    files={p.name:dict(sha256=sha(p),size=list(Image.open(p).size),openedIndividually=True) for p in paths}
    write(E/'art-review.json',dict(utc=datetime.now(timezone.utc).isoformat(),reviewer='Codex 1 (Windows app)',
        files=files,observations=['All 17 final PNGs opened individually: six deck-camera day/night, two wide, top, plate, sheet and six anchor markers.',
        'One angular sea mount and one sand patch; long connected shelf drop. Clear hull and lower-corner underwater ledges.',
        'Corner ledges are faint, especially at night; Unity water visibility remains a native review item.',
        'Five orange water-anchor markers rest unobstructed at water level; gull marker rests on ivory crown. Review markers are not exported.'],
        limits=['Author review, not Claude/Mo acceptance.', 'Blender review water is not Unity runtime water.']))
    print('ART REVIEW',len(files))

def native_review():
    from PIL import Image
    observations={
        'chart':'Whale shelf and 1920 price readable at both sizes. Spot8 shares the Harbour mouth fallback pin; its card partly covers the Harbour selected-ground subtitle. Claude integration needed.',
        'sail-out':'Correct Whale shelf route HUD, dashed route and hull visible; left-side buoy present. Landscape shows a distant boat. No claim of final chart-trip landmarks.',
        'herring-shoals':'Both pale sand-coloured faceted corner ledges clearly visible; left partly behind existing HUD. Hull and fishing bubble space clear. Production water remains blue.',
        'shelf-edge':'Both grey faceted corner ledges visible; cardinal buoy floats between hull and right ledge. Hull clear. Production water does not yet establish requested teal-to-navy shelf biome.',
        'whale-road':'Both corner ledges visible, left partly behind HUD; whale-tail silhouette and birds visible to right. Frozen capture does not prove spout/tail animation.'}
    files={}
    for stage,note in observations.items():
        for width in [1440,844]:
            p=E/f'{stage}-{width}.png'
            files[p.name]=dict(sha256=sha(p),size=list(Image.open(p).size),openedIndividually=True,observation=note)
    write(E/'native-visual-review.json',dict(utc=datetime.now(timezone.utc).isoformat(),reviewer='Codex 1 (Windows app)',
        files=files,allTenOpened=True,authorTerrainReview='Clear corner landmarks at both sizes; no terrain over hull or bubbles.',
        leadIntegrationPending=['Distinct chart8 point/glyph and trip-chart landmarks.', 'Requested clear-water teal/navy shelf biome review.', 'Life animation and contextual suitability.'],
        limits=['Frozen-time author still review; no physical touch, installed-player or Claude/Mo acceptance.']))
    print('NATIVE REVIEW',len(files))

def receipt():
    from PIL import Image
    names=[f'{s}-{w}.png' for s in ['chart','sail-out','herring-shoals','shelf-edge','whale-road'] for w in [1440,844]]
    images={}
    for name in names:
        p=E/name; size=Image.open(p).size
        assert size==((1440,900) if '-1440.' in name else (844,390)),(name,size)
        images[name]=dict(sha256=sha(p),size=list(size),openedIndividually=True)
    completed=(E/'capture-complete.txt').read_text().splitlines()
    assert len(completed)==10 and all(any(n in line for line in completed) for n in names)
    exit=json.loads((E/'native-exit.json').read_text(encoding='utf-8-sig'));assert exit['exitCode']==0
    checks=json.loads((E/'map9-final-checks.json').read_text(encoding='utf-8-sig'))
    assert checks['maps']==9 and checks['hullRoutes']==60 and checks['lanes']==27
    assert all(checks[k] for k in ['assets','chartPurchase','anchors','groundPoolsReady'])
    assert len(checks['trips'])==4 and all('PASS' in t for t in checks['trips'])
    old=(E/'check-map9-safety-build.log').read_text(encoding='utf-8-sig')
    final=(E/'check-map9-final-build.log').read_text(encoding='utf-8-sig')
    assert '540 directed hull routes' in old and 'Exception: Sea scene: GullWhaleShelf horizon silhouettes' in old
    assert 'MAP9 TEST BUILD PASSED' in final and 'MAP9 CHECKS PASSED' in final
    assert 'error CS' not in final and 'Shader error' not in final and 'NullReferenceException' not in final
    for name in ['SeaV2-source-audit.json','SeaV2-audit.json']:
        assert json.loads((ART/name).read_text())['allPassed'],name
    preflight()
    files={}
    paths=list(ART.glob('*'))+list((ROOT/IMPORT).glob('*'))+[ROOT/'Assets/Editor/WhaleShelfMapChecks.cs',ROOT/'Assets/Scripts/Game/Map9Capture.cs']
    paths += [ROOT/'Assets/Scripts/Game'/n for n in ['GameData.cs','VoyageScenery.cs','Sea/SeaNav.cs','Data/Grounds.cs']]
    paths += list((ROOT/'Art/Source/Art108').glob('map9_*'))+[ROOT/'Art/Source/Art108/sea_v2_layouts.py']
    paths += [p for p in E.iterdir() if p.is_file() and p.name!='verification-receipt.json']
    for p in paths:
        if p.is_file():files[p.relative_to(ROOT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
    write(E/'verification-receipt.json',dict(utc=datetime.now(timezone.utc).isoformat(),owner='Codex 1 (Windows app)',
        status='Own MAP9 delivery; Claude review/commit and production chart/water/life acceptance pending',
        checks=checks,nativeFrames=images,files=files,sourceSnapshots=['safety-source/source-hashes.json','final-source/source-hashes.json'],
        limits=['Original full run passed 540 routes then failed inherited horizon assertion; actual failed log retained.',
        'Final run passed 60 affected-map routes, all nine scene assets and 27 lanes, five baseline hull trips and three MAP9 bait/cast/home trips.',
        'MAP9 open-water horizon assertion is adapted only in the own fixture; shared checks remain unchanged.',
        'Frozen native stills do not prove animated life, physical touch, caught-fish yield, installed-player acceptance or player-save migration.',
        'Chart position/glyph, trip landmarks, water optics and life remain Claude-owned. See native review and comms QUESTION lines.'],
        commit=None,playerSaveAccess=False,installedPlayerReplaced=False,subagents=[]))
    for rel,v in files.items():assert sha(ROOT/rel)==v['sha256'],rel
    print('RECEIPT REHASH PASS',len(files),'files,',len(images),'native frames')
if __name__=='__main__':
    if 'preflight' in sys.argv:preflight()
    elif 'art-review' in sys.argv:art_review()
    elif 'native-review' in sys.argv:native_review()
    elif 'receipt' in sys.argv:receipt()
    else:snapshot('final-source' if '--final' in sys.argv else 'safety-source')
