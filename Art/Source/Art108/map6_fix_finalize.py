"""Bind manually reviewed MAP6-FIX evidence; never changes audit outcomes."""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT.parent / 'Catchline-sim'
ART = ROOT / 'Art/Models/Maps/GullSkerries'
EVIDENCE = ROOT / 'docs/screens/map6-skerries-fix-1'
IMPORT = ROOT / 'Assets/Art/Models/Environment/GullSkerries'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

def utc():
    return datetime.now(timezone.utc).isoformat()

def art_review():
    audit = read(ART / 'SeaV2-audit.json')
    source = read(ART / 'SeaV2-source-audit.json')
    build = read(ART / 'SeaV2-validation.json')
    failed = [c['check'] for c in audit['checks'] if not c['passed']]
    assert len(audit['checks']) == 89 and len(failed) == 6
    assert all('full zone' in c for c in failed)
    assert source['allPassed'] and source['totalChecks'] == 109
    assert source['maps'][0]['fbxSha256'] == sha(ART / 'GullSkerriesSeaV2.fbx')
    assert build['triangles'] == 29232
    imgs = sorted(ART.glob('*.png'))
    assert len(imgs) == 11
    review = dict(map='GullSkerries', task='MAP6-SKERRIES-FIX-1', reviewer='Codex 1 (Windows app)',
        reviewedUtc=utc(), allIndividuallyOpened=True,
        imageHashes={p.name: sha(p) for p in imgs},
        scope='Eleven final images manually opened individually in view_image; this records that review, not an automated visual test or Claude/Mo acceptance.',
        camera=dict(projection='orthographic', horizontalSpanMetres=10.24,
                    pitchDegrees=45, yawDegrees=35, resolution=[1440, 900],
                    groundCentresUnchanged=True),
        observations=[
            'Grey-pink stepped/angular playable granite and cairn replace the sandbank appearance.',
            'Low flat colony slabs enter only the lower corners of the fixed 10.24m rowboat frame; their lower portions are cropped.',
            'The 13m parallel gully ridges with mandated hull clearance are outside the fixed 10.24m rowboat frame; native tier5 framing must be reviewed separately.',
            'Half-tide reef and thin static waterline foam enter the lower-right ground frame; no ReefBreak meshes or fin foam are baked into this map.',
            'Night ground silhouettes remain visible; the wide night view is deliberately dim.',
            'The rowboat art fixture does not contain runtime life or HUD; final native tier5 evidence is separate.',
            'Distant fogged horizon proxies remain outside the playable area.'
        ], acceptedByLead=False, artContractAllPassed=False, retainedFailedChecks=failed)
    write(ART / 'SeaV2-visual-review.json', review)
    runtime = {}
    for name in ['GullSkerriesSeaV2.fbx', 'navigation.json']:
        assert sha(ART / name) == sha(IMPORT / name)
        runtime[(IMPORT / name).relative_to(ROOT).as_posix()] = sha(IMPORT / name)
    write(ART / 'SeaV2-delivery.json', dict(map='GullSkerries', task='MAP6-SKERRIES-FIX-1',
        runtimeHashes=runtime, renderHashes=review['imageHashes'], published=True,
        sourceAndImportParity=True, overallAcceptance='PARTIAL: six unchanged full-zone assertions conflict with required close landmarks; narrow art gully framing and runtime life/lead visual acceptance remain unresolved.',
        artAuditAllPassed=False, artAuditPassed=83, artAuditTotal=89,
        retainedFailedChecks=failed, reviewedBy='Codex 1 (Windows app)', reviewedUtc=review['reviewedUtc']))
    return review

def native_review():
    native = EVIDENCE / 'native'
    log = (native / 'native.log').read_text(encoding='utf-8-sig')
    assert 'MAP6 NATIVE CAPTURES COMPLETE' in log
    observations = {
        'chart-1440.png': 'Chart overview readable, Seal skerries glyph and 700-coin price visible; harbour remains selected before purchase.',
        'chart-844.png': 'Landscape overview readable, six labels and bottom navigation fit; Seal skerries 700-coin label visible.',
        'sail-out-1440.png': 'Normal SeaOut route with tier5 boat, route line and progress header. Navigation marker buoy visible; this is not evidence of the missing crab-buoy life set.',
        'sail-out-844.png': 'Landscape sailing header/progress/faster control readable; boat and route visible without blank frame.',
        'seal-rocks-1440.png': 'Two low flat stepped colony slabs occupy lower corners with water separating them from hull; kelp visible. Left HUD and lower controls partly cover slabs. No seals or crab-buoy life set visible.',
        'seal-rocks-844.png': 'Both low slabs visible below clear hull; left panel and bottom controls cover parts of the rocks. Fish bubbles stay around boat. No seals or crab-buoy life set visible.',
        'kelp-gully-1440.png': 'Parallel long low ridges enter top-left and lower-right edges, heavily cropped; ample open water around hull and kelp between. HUD readable. No life integration evidenced.',
        'kelp-gully-844.png': 'Lower-right ridge visible and opposite ridge only a thin top-left crop; kelp channel and hull clearance visible. Lower controls cover part of ridge. Not a full two-wall overview.',
        'outer-reef-1440.png': 'Half-tide rock foreground and right-edge reef rocks with narrow waterline foam; no sharp fin foam or baked breaking meshes. Foreground cropped/covered by bottom controls. Animated surf absent.',
        'outer-reef-844.png': 'Half-tide rock chain visible along right edge, foreground rock cropped by bottom controls; hull clear. No sharp fin foam, animated breaking surf absent.'
    }
    hashes = {}
    for name in observations:
        p = native / name
        with Image.open(p) as im:
            assert im.size == ((1440, 900) if '-1440.' in name else (844, 390)), name
        hashes[name] = sha(p)
    write(EVIDENCE / 'native-visual-review.json', dict(
        task='MAP6-SKERRIES-FIX-1 addendum A-D', reviewer='Codex 1 (Windows app)',
        reviewedUtc=utc(), allIndividuallyOpened=True, imageHashes=hashes,
        scope='All ten final native PNGs individually opened in view_image; visual observations are manual and do not establish Claude/Mo acceptance.',
        observations=observations, sealsVisible=False, animatedSurfVisible=False, crabBuoyLifeSetVisible=False,
        limits=[
            'D remains partial: SealColony empties sit on slab tops, but seals, animated surf and crab-buoy life set are absent. Current BuildNavigableSea does not call DressSkerries; runtime integration belongs to Claude.',
            'Six original full-ground-circle art assertions remain failed; mandated close landmarks intersect these circles. No checks relaxed.',
            'Gully walls are outside the fixed10.24m rowboat art fixture; native tier5 shows heavily cropped opposing ridges, especially the top-left ridge at844x390.',
            'HUD and bottom controls partially occlude lower terrain. Terrain framing remains subject to Claude review.',
            'SessionOnly native evidence does not establish touch, installed-player, seal-animation or interactive fishing acceptance.',
            'MapNav reports physical-distance timing outside target on some routes; this is a retained advisory, separate from collision/border route safety.'
        ], acceptedByLead=False))

def final():
    review = read(ART / 'SeaV2-visual-review.json')
    assert review['allIndividuallyOpened']
    for name, digest in review['imageHashes'].items():
        assert sha(ART / name) == digest, name
    check = read(EVIDENCE / 'map6-checks.json')
    assert check['maps'] == 6 and check['hullRoutes'] == 360 and check['lanes'] == 18
    assert all(check[k] for k in ['assets', 'chartPurchase', 'anchors', 'groundPoolsReady'])
    assert len(check['trips']) == 4 and all('PASS' in s for s in check['trips'])
    log = (EVIDENCE / 'check-map6-addendum-final.log').read_text(encoding='utf-8-sig')
    assert 'MAP6 CHECKS PASSED' in log
    assert 'Application will terminate with return code 0' in log
    assert not re.search(r'MAP6 check failed|error CS\d|NullReferenceException|executeMethod.*failed', log)
    native = EVIDENCE / 'native'
    run = read(EVIDENCE / 'native-run.json')
    launched = datetime.fromisoformat(run['launchedUtc'].replace('Z', '+00:00')).timestamp()
    nlog = (native / 'native.log').read_text(encoding='utf-8-sig')
    assert 'TEST / no save reads or writes' in nlog
    assert 'MAP6 NATIVE CAPTURES COMPLETE' in nlog
    assert not re.search(r'Exception:|Error:|Assertion failed', nlog)
    images = {}
    for frame in ['chart', 'sail-out', 'seal-rocks', 'kelp-gully', 'outer-reef']:
        for width, height in [(1440, 900), (844, 390)]:
            p = native / f'{frame}-{width}.png'
            assert p.stat().st_mtime >= launched, 'stale native frame: ' + str(p)
            with Image.open(p) as im:
                assert im.size == (width, height), str(p)
            images[p.name] = dict(size=[width, height], sha256=sha(p))
    assert len(list(native.glob('*.png'))) == 10
    manual = read(EVIDENCE / 'native-visual-review.json')
    assert manual['allIndividuallyOpened'] and manual['imageHashes'] == {n: x['sha256'] for n, x in images.items()}
    source_paths = [
        'Assets/Scripts/Game/GameData.cs', 'Assets/Scripts/Game/Data/Grounds.cs',
        'Assets/Scripts/Game/VoyageChart.cs', 'Assets/Scripts/Game/VoyageScenery.cs',
        'Assets/Scripts/Game/VoyageSkerriesLife.cs', 'Assets/Scripts/Game/Map6Capture.cs',
        'Assets/Scripts/Game/Sea/SeaScenery.cs', 'Assets/Scripts/Game/Sea/SeaCamera.cs',
        'Assets/Scripts/Game/Sea/SeaNav.cs', 'Assets/Scripts/Game/Sea/SeaLanes.cs',
        'Assets/Editor/SkerriesMapChecks.cs', 'Assets/Editor/SkerriesLifeImport.cs'
    ]
    snapshots = []
    for name in source_paths:
        p = ROOT / name
        assert sha(p) == sha(SCRATCH / name), name
        snapshots.append(dict(path=name, sha256=sha(p), scratchMatches=True))
    assert {x['path']: x['sha256'] for x in run['sourceSnapshots']} == {x['path']: x['sha256'] for x in snapshots}
    for name in ['GullSkerriesSeaV2.fbx', 'navigation.json']:
        assert sha(ART / name) == sha(IMPORT / name) == sha(SCRATCH / (IMPORT / name).relative_to(ROOT))
    for p in (ROOT / 'Art/Models/Skerries').glob('*.fbx'):
        target = ROOT / 'Assets/Art/Models/Environment/Skerries' / p.name
        assert sha(p) == sha(target) == sha(SCRATCH / target.relative_to(ROOT)), p.name
    paths = set(p for p in ART.iterdir() if p.is_file())
    for name in ['map6_skerries.py', 'map6_fix_finalize.py', 'sea_v2_layouts.py', 'build_sea_v2.py',
                 'audit_sea_v2.py', 'verify_sea_v2_sources.py', 'map6-fix-build.log',
                 'map6-fix-review.log', 'map6-fix-source-audit.log']:
        paths.add(ROOT / 'Art/Source/Art108' / name)
    paths.update(ROOT / s for s in source_paths)
    paths.update(IMPORT.glob('*'))
    paths.update((ROOT / 'Assets/Art/Models/Environment/Skerries').glob('*'))
    paths.update(p for p in EVIDENCE.rglob('*') if p.is_file() and p.name != 'verification-receipt.json')
    build = SCRATCH / 'Builds/Map6Capture'
    assert sha(build / 'Catchline.exe') == run['exeSha256']
    assert sha(build / 'Catchline_Data/Managed/Assembly-CSharp.dll') == run['assemblySha256']
    paths.update(build / n for n in ['Catchline.exe', 'UnityPlayer.dll', 'Catchline_Data/Managed/Assembly-CSharp.dll', 'Catchline_Data/level0'])
    files = {}
    for p in sorted(paths):
        assert p.is_file(), str(p)
        assert p.stat().st_size > 0 or p.name.endswith('-stderr.log'), str(p)
        try:
            key = p.relative_to(ROOT).as_posix()
        except ValueError:
            key = p.as_posix()
        files[key] = dict(sha256=sha(p), bytes=p.stat().st_size)
    links = 0
    for report in [ART / 'REPORT.md', ART / 'SeaV2-REPORT.md', EVIDENCE / 'README.md']:
        for target in re.findall(r'\]\(([^)]+)\)', report.read_text(encoding='utf-8-sig')):
            if not target.startswith(('http:', 'https:', '#')):
                assert (report.parent / target).resolve().exists(), (report, target)
                links += 1
    receipt = dict(task='MAP6-SKERRIES-FIX-1', owner='Codex 1 (Windows app)', utc=utc(),
        ownDelivery='Revised terrain imported; full exact-geometry safety checks and native evidence complete.',
        overallAcceptance='PARTIAL: retained full-zone contract conflict, runtime life visibility and Claude visual acceptance pending.',
        checks=dict(maps=6, directedHullRoutes=360, seaLanes=18, baselineHarbourHulls=5,
                    newGroundHomeTrips=3, sourceChecks=109, artAuditPassed=83, artAuditTotal=89,
                    reviewedArtImages=11, reviewedNativeImages=10, namedLifeAnchors=9,
                    triangles=29232, closedTerrainObstacles=14, localReportLinks=links,
                    groundPoolsReady=True, sourceScratchParity=True, sourceImportParity=True),
        limits=manual['limits'], sourceSnapshots=snapshots, nativeBuild=run, nativeImages=images, files=files,
        fixtureEvidence='BuildNative source creates the SessionOnly fixture; built level0 and the runtime SessionOnly/no-save guard are bound. The subsequent required Assets mirror removes the generated scratch .unity source; it was not recreated or represented as a preserved original.',
        safety=dict(sessionOnly=True, noSaveReadsOrWrites=True, noInstalledPlayerReplacement=True,
                    noGitOperation=True, noMainUnityBatchmode=True))
    target = EVIDENCE / 'verification-receipt.json'
    write(target, receipt)
    for name, expected in read(target)['files'].items():
        p = Path(name) if Path(name).is_absolute() else ROOT / name
        assert sha(p) == expected['sha256'] and p.stat().st_size == expected['bytes'], name
    print(f'FINAL RECEIPT PASS {len(files)} current SHA256 files, {links} links; {sha(target)}')

if __name__ == '__main__':
    if sys.argv[-1] == 'art':
        art_review()
        print('ART REVIEW/DELIVERY BOUND: eleven manually opened images; 83/89 retained art assertions; partial overall.')
    elif sys.argv[-1] == 'final':
        final()
    elif sys.argv[-1] == 'native':
        native_review()
        print('NATIVE REVIEW BOUND: ten individually opened images; life absent, lead review pending.')
    else:
        raise ValueError('Expected art or final')
