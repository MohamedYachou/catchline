"""Bind MAP7's reviewed evidence; preserve every failed art assertion."""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT.parent / 'Catchline-sim'
ART = ROOT / 'Art/Models/Maps/GullWreckBank'
EVIDENCE = ROOT / 'docs/screens/map7-wreck-bank-1'
IMPORT = ROOT / 'Assets/Art/Models/Environment/GullWreckBank'
OWNED = ['Assets/Scripts/Game/' + n for n in [
    'GameData.cs', 'Data/Grounds.cs', 'Sea/SeaNav.cs', 'VoyageScenery.cs', 'Map7Capture.cs']]
LIMITS = [
    'Six unmodified full-zone art assertions fail: required close corner landmarks intersect the larger 12-20m ground-zone circles. Actual hull route checks are separate. Lead exception/visual acceptance pending.',
    'Claude fixed chart spot6 to(.72,.56); pin, Wreck bank label and980coin price are now readable at both sizes. Formal lead acceptance remains external.',
    'Claude kind6 sandy-green water optics and WreckLife are in this rebuilt snapshot. Exact on-screen hex colours are not asserted.',
    'Herring bank shows gannets and boils, clearest at844x390; desktop life is partly behind the left HUD/edge. Cardinal buoy is heavily cropped/covered at the wreck lower-right; perched wreck gulls are outside the tight frame. Native stills do not prove dive/splash/bobbing animation.',
    'The rusted bow/broken bulwark appears at the lower-right wreck corner; funnel and mast are outside the tight deck crop. Herring/Sand terrain is deliberately similar; Herring bank life distinguishes them.',
    'HUD/bottom controls partly cover lower terrain. Stills freeze presentation time; no animation, touch or installed-player acceptance.',
    'Native build pins118 compiled Game source hashes; concurrent Claude-only CoastalCanvas.cs, Skin.cs and VoyageInterfaceShop.cs differed in main at launch. All five owned runtime sources match the build. Historical pre-life/first-postlife evidence and121-file original safety snapshot are preserved separately.',
    'MapNav timing outside target is retained as an advisory about physical distance/one hull speed, separate from collision and border checks.',
    'Automatic approval review blocked deletion of temporary Catchline-sim/Backups/map7-before; backup retained without retrying through another mechanism.'
]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

def utc():
    return datetime.now(timezone.utc).isoformat()

def native_review():
    observations = {
        'chart': 'Corrected(.72,.56) Wreck bank steamer pin, full label and980coin price readable, clear of coin/contracts header and Harbour mouth at both sizes. All seven ground pins visible.',
        'sail-out': 'Normal SeaOut route, boat, route/progress and controls visible over greener water. Generic buoy/rock birds are not WreckLife anchor proof.',
        'the-wreck': 'Low stepped sand at lower left and cropped rusted bow/broken bulwark at lower right. Open water separates hull/bubbles from terrain. Cardinal buoy at extreme lower-right is heavily cropped/covered. Perched wreck gulls, funnel/mast outside deck crop.',
        'herring-bank': 'Both low angular pale sand shelves visible below boat, clear hull/bubbles. Gannets and silver boil patches present; desktop life is partly behind left HUD/edge, landscape shows airborne gannets and full upper-right boil. No dive/splash animation proved.',
        'sand-edge': 'Both angular pale sand shelves visible below the side-on boat; hull/bubbles remain clear. HUD and bottom controls cover portions. Terrain similar to Herring bank.'
    }
    images = {}
    notes = {}
    for frame, note in observations.items():
        for width, height in [(1440, 900), (844, 390)]:
            p = EVIDENCE / f'{frame}-{width}.png'
            with Image.open(p) as im:
                assert im.size == (width, height), p.name
            images[p.name] = sha(p)
            notes[p.name] = note + (' Landscape HUD fits; corner shelf portions cropped/covered.' if width == 844 else ' Desktop HUD readable.')
    write(EVIDENCE / 'native-visual-review.json', dict(
        task='MAP7-WRECK-BANK-1', reviewer='Codex 1 (Windows app)', reviewedUtc=utc(),
        allIndividuallyOpened=True, imageHashes=images, observations=notes,
        scope='Ten final native PNGs individually opened with view_image; this records manual review, not automated visual or Claude/Mo acceptance.',
        limits=LIMITS, acceptedByLead=False, runtimeWreckLifeVisible=True,
        herringGannetsAndBoilsVisible=True, cardinalBuoyFullyVisible=False, perchedWreckGullsVisible=False,
        chartVisualAccepted=False, chartPinAndLabelReadable=True, requestedWaterOpticsVisible=True))
    print('NATIVE REVIEW BOUND: ten individually opened images; external limits retained.')

def final():
    audit, source, validation = [read(ART / n) for n in [
        'SeaV2-audit.json', 'SeaV2-source-audit.json', 'SeaV2-validation.json']]
    failures = [c for c in audit['checks'] if not c['passed']]
    assert len(audit['checks']) == 61 and len(failures) == 6
    assert all('full zone' in c['check'] for c in failures)
    assert source['allPassed'] and source['totalChecks'] == 55
    assert validation['allPassed'] and validation['triangles'] == 25236
    assert validation['sourceSha256'] == sha(ART / 'GullWreckBankSeaV2.blend')
    art_review = read(ART / 'SeaV2-visual-review.json')
    assert art_review['allIndividuallyOpened'] and len(art_review['images']) == 11
    assert len(list(ART.glob('*.png'))) == 11
    for name, digest in art_review['images'].items():
        assert sha(ART / name) == digest, name
    for name, field in [('GullWreckBankSeaV2.fbx', 'fbxSha256'), ('navigation.json', 'navigationSha256')]:
        assert sha(ART / name) == validation[field] == sha(IMPORT / name) == sha(SCRATCH / (IMPORT / name).relative_to(ROOT)), name
    check = read(EVIDENCE / 'map7-checks.json')
    assert (check['maps'], check['hullRoutes'], check['lanes']) == (7, 420, 21)
    assert all(check[k] for k in ['assets', 'chartPurchase', 'anchors', 'groundPoolsReady'])
    assert check['groundIds'] == ['the-wreck', 'herring-bank', 'sand-edge']
    assert len(check['trips']) == 4 and all('PASS' in s for s in check['trips'])
    assert all('bait-cast/home PASS' in s for s in check['trips'][1:])
    post = read(EVIDENCE / 'map7-postlife-checks.json')
    assert post['maps'] == 7 and post['lanes'] == 3 and len(post['trips']) == 3
    assert post['groundIds'] == check['groundIds']
    assert all('bait-cast/home PASS' in s for s in post['trips'])
    for name, marker in [('build.log', 'MAP7 TEST BUILD PASSED'), ('check-map7-safety.log', 'MAP7 CHECKS PASSED')]:
        log = (EVIDENCE / name).read_text(encoding='utf-8-sig')
        assert marker in log and 'Application will terminate with return code 0' in log, name
        assert not re.search(r'MAP7 check failed|error CS\d|NullReferenceException|executeMethod.*failed', log), name
    for stage in ['build', 'safety']:
        assert f'Verified map7-{stage} (Unity exit 0)' in (EVIDENCE / f'{stage}-runner.log').read_text(encoding='utf-8-sig')
    postlog = (EVIDENCE / 'check-map7-postlife.log').read_text(encoding='utf-8-sig')
    assert 'MAP7 POST-INTEGRATION PASSED' in postlog and 'Application will terminate with return code 0' in postlog
    assert not re.search(r'MAP7 check failed|error CS\d|NullReferenceException|executeMethod.*failed', postlog)
    assert 'Verified map7-postlife (Unity exit 0)' in (EVIDENCE / 'postlife-runner.log').read_text(encoding='utf-8-sig')
    historical = read(EVIDENCE / 'safety-source/source-hashes.json')['files']
    for name in OWNED[:3] + [(IMPORT / n).relative_to(ROOT).as_posix() for n in ['navigation.json', 'GullWreckBankSeaV2.fbx']]:
        assert sha(ROOT / name) == historical[name]['sha256'], name
    run = read(EVIDENCE / 'native-run.json')
    assert run['sessionOnly'] and run['sourceCount'] == len(run['sourceHashes']) >= 116
    launched = datetime.fromisoformat(run['launchedUtc'].replace('Z', '+00:00')).timestamp()
    snapshots = {x['path'].replace('\\', '/'): x for x in run['sourceHashes']}
    for name in OWNED:
        assert sha(ROOT / name).upper() == snapshots[name]['sha256'].upper(), name
        assert sha(ROOT / name) == sha(SCRATCH / name), name
    assert sha(ROOT / 'Assets/Editor/WreckBankMapChecks.cs') == sha(SCRATCH / 'Assets/Editor/WreckBankMapChecks.cs')
    native_log = (EVIDENCE / 'native.log').read_text(encoding='utf-8-sig')
    assert 'TEST / no save reads or writes' in native_log and 'MAP7 NATIVE CAPTURES COMPLETE' in native_log
    assert not re.search(r'Exception:|Error:|Assertion failed', native_log)
    manual = read(EVIDENCE / 'native-visual-review.json')
    assert manual['allIndividuallyOpened'] and len(manual['imageHashes']) == 10
    assert len(list(EVIDENCE.glob('*.png'))) == 10
    for name, digest in manual['imageHashes'].items():
        p = EVIDENCE / name
        assert sha(p) == digest and p.stat().st_mtime >= launched, name
        with Image.open(p) as im:
            assert im.size == ((1440, 900) if '-1440.' in name else (844, 390)), name
    build = SCRATCH / 'Builds/Map7Capture'
    for name, key in [('Catchline.exe', 'exeSha256'), ('Catchline_Data/Managed/Assembly-CSharp.dll', 'assemblySha256'), ('Catchline_Data/level0', 'sceneLevel0Sha256')]:
        assert sha(build / name).upper() == run[key].upper(), name
    delivery = read(ART / 'SeaV2-delivery.json')
    delivery.update(nativeSafetyPassed=True, postIntegrationPassed=True, nativeImagesReviewed=10, directedHullRoutes=420,
        seaLanes=21, newGroundBaitCastHomeTrips=3, acceptance='PARTIAL: own terrain/import/safety/fixed-chart post-life capture delivery complete; six retained art failures and tight life crops need lead review.',
        evidence='../../../../docs/screens/map7-wreck-bank-1/verification-receipt.json')
    write(ART / 'SeaV2-delivery.json', delivery)
    paths = set(p for p in ART.iterdir() if p.is_file())
    paths.update(p for p in EVIDENCE.rglob('*') if p.is_file() and p.name != 'verification-receipt.json')
    paths.update(p for p in IMPORT.iterdir() if p.is_file())
    paths.add(IMPORT.with_suffix('.meta'))
    for name in OWNED + ['Assets/Editor/WreckBankMapChecks.cs']:
        paths.add(ROOT / name)
    paths.update(ROOT / n for n in ['Assets/Editor/WreckBankMapChecks.cs.meta', 'Assets/Scripts/Game/Map7Capture.cs.meta'])
    paths.update((ROOT / 'Art/Source/Art108').glob('map7*'))
    paths.update(ROOT / 'Art/Source/Art108' / n for n in ['sea_v2_layouts.py', 'build_sea_v2.py', 'audit_sea_v2.py', 'verify_sea_v2_sources.py'])
    paths.update(build / n for n in ['Catchline.exe', 'UnityPlayer.dll', 'Catchline_Data/Managed/Assembly-CSharp.dll', 'Catchline_Data/level0'])
    links = 0
    for report in [ART / 'REPORT.md', EVIDENCE / 'README.md']:
        for target in re.findall(r'\]\(([^)]+)\)', report.read_text(encoding='utf-8-sig')):
            if not target.startswith(('http:', 'https:', '#')):
                assert (report.parent / target).resolve().exists(), (report, target)
                links += 1
    files = {}
    for p in sorted(paths):
        assert p.is_file(), p
        assert p.stat().st_size or p.suffix == '.err' or p.name.endswith('-stderr.log'), p
        try:
            key = p.relative_to(ROOT).as_posix()
        except ValueError:
            key = p.as_posix()
        files[key] = dict(sha256=sha(p), bytes=p.stat().st_size)
    receipt = dict(task='MAP7-WRECK-BANK-1', owner='Codex 1 (Windows app)', utc=utc(),
        ownDelivery='Terrain, import, seven-map safety and native evidence complete.', overallAcceptance='PARTIAL; see limits.',
        checks=dict(maps=7, directedHullRoutes=420, seaLanes=21, baselineHarbourHulls=5,
            newGroundBaitCastHomeTrips=3, sourceChecks=55, artAuditPassed=55, artAuditTotal=61,
            postIntegrationEntryLanes=3, postIntegrationBaitCastHomeTrips=3,
            reviewedArtImages=11, reviewedNativeImages=10, namedLifeAnchors=6,
            triangles=25236, realTerrainObstacles=7, localReportLinks=links),
        retainedFailures=failures, limits=LIMITS, nativeBuild=run, files=files,
        fixtureEvidence='BuildNative creates SessionOnly scratch scene. Actual built level0/assembly/exe and runtime no-save guard are bound; later required Assets mirroring removes the generated scratch scene source.',
        safety=dict(sessionOnly=True, noSaveReadsOrWrites=True, noInstalledPlayerReplacement=True,
            noGitOperation=True, noMainUnityBatchmode=True, noSubagents=True))
    target = EVIDENCE / 'verification-receipt.json'
    write(target, receipt)
    for name, expected in read(target)['files'].items():
        p = Path(name) if Path(name).is_absolute() else ROOT / name
        assert sha(p) == expected['sha256'] and p.stat().st_size == expected['bytes'], name
    print(f'FINAL RECEIPT PASS {len(files)} files, {links} local links; SHA256 {sha(target)}')

if __name__ == '__main__':
    {'native': native_review, 'final': final}[sys.argv[-1]]()
