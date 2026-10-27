"""Verify the complete additive SeaV2 delivery and compose its handoff index.

System Python; read-only for all protected and runtime assets. Recomputes the
polygon audit, but never regenerates or changes manually reviewed map images.
"""
import datetime
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
from audit_sea_v2 import audit, sha
from sea_v2_layouts import LAYOUTS

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'Art/Models/Maps'
CHECKS = []


def check(label, passed):
    CHECKS.append(dict(check=label, passed=bool(passed)))
    assert passed, label


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/' + ('segoeuib.ttf' if bold else 'segoeui.ttf'), size)


def overview(rows):
    cream, navy, muted, orange = '#f1ebdd', '#102f3b', '#52656a', '#bd663c'
    canvas = Image.new('RGB', (2040, 1640), cream)
    d = ImageDraw.Draw(canvas)
    d.text((32, 18), 'CATCHLINE / FIVE NAVIGABLE SEAS', fill=navy, font=font(39, True))
    d.text((34, 72), 'SeaV2 art handoff  |  15 grounds  |  day + night  |  24 October 2026', fill=muted, font=font(22))
    columns = [(256, 360, 'NAVIGATION'), (624, 448, 'GROUND / DAY'),
               (1080, 448, 'GROUND / NIGHT'), (1536, 448, 'SEA / DAY')]
    for x, w, title in columns:
        d.text((x, 111), title, fill=navy, font=font(17, True))
    for i, row in enumerate(rows):
        y = 145 + i * 284
        folder = OUT / row['map']
        d.line((32, y-5, 2008, y-5), fill='#c9c9b8', width=1)
        d.text((32, y+12), f'{i+1:02}', fill=orange, font=font(27, True))
        # Two-line longest title keeps labels entirely within their own column.
        title = row['title'].split(' ')
        for k, word in enumerate(title):
            d.text((32, y+51+k*32), word, fill=navy, font=font(27, True))
        d.text((32, y+130), f'{row["sizeMetres"][0]} x {row["sizeMetres"][1]} m', fill=muted, font=font(21))
        d.text((32, y+164), f'{row["triangles"]:,} triangles', fill=muted, font=font(17))
        d.text((32, y+191), f'{row["buoys"]} border buoys', fill=muted, font=font(17))
        d.text((32, y+218), f'{row["navigationChecks"]} nav checks', fill=muted, font=font(17))
        ground = 'trench' if row['map'] == 'GullDeepChannel' else row['groundIds'][0]
        images = ['SeaV2-navigation-plate.png', f'SeaV2-{ground}-day.png',
                  f'SeaV2-{ground}-night.png', 'SeaV2-wide-day.png']
        for (x, w, _), filename in zip(columns, images):
            with Image.open(folder / filename) as im:
                thumb = ImageOps.contain(im.convert('RGB'), (w, 280), Image.Resampling.LANCZOS)
                canvas.paste(thumb, (x+(w-thumb.width)//2, y+(280-thumb.height)//2))
    d.text((32, 1591), 'Blender art evidence. Native water, sailing, HUD and touch acceptance remain pending.', fill=navy, font=font(21))
    canvas.save(OUT / 'SeaV2-overview.png')


def main():
    source_audit = read(OUT / 'SeaV2-source-audit.json')
    check('fresh independent five-source audit passed', source_audit['allPassed'] and len(source_audit['maps']) == 5)
    fresh = {m['map']: m for m in source_audit['maps']}
    baseline = read(ROOT / 'Art/Source/Art108/sea_v2_protected_baseline.json')
    check('114-file legacy baseline retained', len(baseline) == 114)
    for p, digest in baseline.items():
        check('protected SHA256 ' + p, sha(ROOT / p) == digest)
    for name in ('Pim', 'Dirk', 'Kofi', 'Sam', 'Mats', 'Olaf', 'Captain'):
        folder = ROOT / 'Art/Models/CrewV2' / name
        check('complete man skipped ' + name, (folder/'REPORT.md').is_file() and (folder/f'{name}-review.png').is_file())
    rows, files = [], []
    for name, layout in LAYOUTS.items():
        folder = OUT / name
        nav, nav_audit = audit(name)
        v = read(folder / 'SeaV2-validation.json')
        visual = read(folder / 'SeaV2-visual-review.json')
        delivery = read(folder / 'SeaV2-delivery.json')
        independent = fresh[name]
        check(name + ' independent source checks all true', independent['allPassed'] and all(c['passed'] for c in independent['checks']))
        for suffix, field in ((f'{name}SeaV2.blend', 'sourceSha256'),
                              (f'{name}SeaV2.fbx', 'fbxSha256'), ('navigation.json', 'navigationSha256')):
            check(name + ' fresh audit current ' + suffix, sha(folder/suffix) == independent[field] == v[field])
        check(name + ' current 11 images manually opened', visual['allIndividuallyOpened'] and len(visual['imageHashes']) == 11)
        check(name + ' render hash inventories agree', visual['imageHashes'] == delivery['renderHashes'])
        for filename, digest in visual['imageHashes'].items():
            path = folder / filename
            check(name + ' reviewed SHA256 ' + filename, sha(path) == digest)
            with Image.open(path) as im:
                im.load()
                expected = (1800, 1400) if filename in ('SeaV2-top-base.png', 'SeaV2-navigation-plate.png') else ((1440, 2020) if filename == 'SeaV2-review-sheet.png' else (1440, 900))
                check(name + ' PNG dimensions ' + filename, im.size == expected and im.format == 'PNG')
        check(name + ' published exactly two runtime files', delivery['published'] and len(delivery['runtimeHashes']) == 2)
        for raw, digest in delivery['runtimeHashes'].items():
            runtime = Path(raw)
            check(name + ' runtime bytes ' + runtime.name, sha(runtime) == digest == sha(folder/runtime.name))
            files.append(runtime)
        for filename in (f'{name}SeaV2.blend', f'{name}SeaV2.fbx', 'navigation.json',
                         'SeaV2-Review-only.blend', 'SeaV2-validation.json', 'SeaV2-audit.json',
                         'SeaV2-visual-review.json', 'SeaV2-delivery.json', 'SeaV2-lighting-presets.json', 'SeaV2-REPORT.md'):
            path = folder / filename
            check(name + ' handoff file exists ' + filename, path.is_file() and path.stat().st_size > 0)
            files.append(path)
        files.extend(folder/p for p in visual['imageHashes'])
        rows.append(dict(map=name, title=layout['title'], sizeMetres=list(layout['size']),
                         triangles=v['triangles'], meshParts=v['meshCount'], islands=v['islandCount'],
                         shallows=v['shallowCount'], buoys=v['buoyCount'],
                         groundIds=[g['id'] for g in nav['grounds']], navigationChecks=len(nav_audit['checks']),
                         freshSourceChecks=len(independent['checks']),
                         maxFbxVertexErrorMetres=independent['maxFbxErrorMetres'],
                         report=f'{name}/SeaV2-REPORT.md', plate=f'{name}/SeaV2-navigation-plate.png'))
    overview(rows)
    nav_total = sum(r['navigationChecks'] for r in rows)
    fresh_total = sum(r['freshSourceChecks'] for r in rows)
    check('fresh source total matches audit', fresh_total == source_audit['totalChecks'])
    lines = ['# Catchline / SeaV2 art handoff', '',
             '24 October 2026. Codex 1 (Windows app). All five approved MAP-PLAN art packages complete; native/Mo acceptance pending.', '',
             '[Five-map overview](SeaV2-overview.png). Each map report links the authored geometry, navigation contract and review evidence.', '',
             '| Map / report | Playable size | Triangles / parts | Land / shallow outlines | Buoys | Nav / fresh source checks |',
             '|---|---|---|---|---|---|']
    for r in rows:
        lines.append(f'| [{r["title"]}]({r["report"]}) | {r["sizeMetres"][0]} x {r["sizeMetres"][1]} m | {r["triangles"]:,} / {r["meshParts"]} | {r["islands"]} / {r["shallows"]} | {r["buoys"]} | {r["navigationChecks"]} / {r["freshSourceChecks"]} |')
    lines += ['', f'{sum(r["triangles"] for r in rows):,} triangles across five models; 15 original ground IDs/names/pool IDs/nominal depths retained. {nav_total} freshly recomputed art-side navigation checks and {fresh_total} independent saved-source/actual-FBX checks pass. All 55 current per-map PNGs were individually opened and hash-recorded. The index decodes all 55 again and verifies both runtime copies for every map. All 114 protected legacy files match the pre-task SHA256 baseline.', '',
              '## Files to integrate', '',
              'Each `Art/Models/Maps/<Map>/` contains `<Map>SeaV2.blend`, `<Map>SeaV2.fbx`, `navigation.json`, three ground day/night pairs, wide day/night, a top base, an annotated navigation plate and a review sheet. `SeaV2-Review-only.blend` retains the boat/water/lighting setup. Source models contain geometry only; review boat, camera, water, fog and lights are excluded from FBX.', '',
              'Byte-identical new `<Map>SeaV2.fbx` and `navigation.json` are published under `Assets/Art/Models/Environment/<Map>/`. Do not substitute old GroundsV1 anchors or recenter the export. All existing assets and metadata remain intact. New Unity metadata/import binding belongs to the integrating owner.', '',
              'Place the model at WORLD `(0,-0.32,0)`, identity rotation/scale. Navigation uses WORLD XZ metres. Boat anchors are WORLD deck centres at Y=0, independent of the map-root translation. Authoring Blender coordinates are `(worldX,-worldZ,height)`; the compensated FBX transform is covered by actual importer readback. Model bounds include seabed and unreachable horizon art, so they do not describe playable camera bounds.', '',
              'Navigation polygons are actual closed mesh slices at local waterline0 and -1m, CCW and at most64 vertices. Ground zones/harbour/buoys clear land inflated2m; ground zones also clear shallows and stay inside the border. Border buoys are25-30m apart. Independent routes for radius2m and4m connect all six harbour/ground pairs in each map; at least one ground pair per map has a blocked direct line. The annotated plates show the three direct ground-pair arrows and audited detours.', '',
              '## Review and remaining acceptance', '',
              'The orthographic ground camera has horizontal span10.24m, pitch45/yaw35 at1440x900. Each recorded sample anchor lies within its ground zone. Day/night share the same model; lighting/depth water/fog presets are in each map folder. Rocky point uses a clearer review-water preset to expose submerged reef crowns and the shelf edge; its preset is recorded explicitly. Wide views include smooth30m border-fog falloff and distant silhouettes.', '',
              'The views are Blender art evidence. They do not establish native water appearance, HUD/crew composition, sailing feel, touch behaviour or Mo acceptance. Claude/code-owner still owns runtime binding/imports, hull clearance/turning/shallow costs, arrival/departure, camera clamps, timing, and native1440x900 plus844x390 captures. Art-side static routes do not certify runtime travel duration;10-20s is a tuning request whose feasibility depends on physical distances and the speed policy.', '',
              'The seven men and their completed hair fixes were skipped as instructed. Codex2 women/PropsV2 and runtime code remained outside this task. No Unity launch, C# or scene change, git operation or commit was made by this art task.', '',
              '## Evidence and reproducibility', '',
              '- `SeaV2-manifest.json`: exact file hashes, consolidated checks and map counts; excludes its own hash.',
              '- `SeaV2-source-audit.json`: independent saved-source reopen, closed terrain, fresh edge slices compared to JSON and fresh actual-FBX imports.',
              '- Per-map `SeaV2-validation.json`, `SeaV2-audit.json`, `SeaV2-visual-review.json` and `SeaV2-delivery.json`: geometry/route/current-image/runtime evidence.',
              '- Builders/auditors: `Art/Source/Art108/{sea_v2_layouts,build_sea_v2,audit_sea_v2,finish_sea_v2,verify_sea_v2_sources,consolidate_sea_v2}.py`.', '',
              'Read-only delivery recheck: `python Art/Source/Art108/consolidate_sea_v2.py`. It refreshes audits/index/overview only and verifies published files; it does not rebuild model geometry or individually reviewed map images.', '',
              'Independent source recheck: Blender background with `--python Art/Source/Art108/verify_sea_v2_sources.py`. Rebuilding a map with `build_sea_v2.py -- <Map> build` or `review` invalidates its earlier review evidence: reopen every current image and use `finish_sea_v2.py <Map> --reviewed-all` only after that inspection. Publishing refuses changes to already-existing runtime bytes; coordinate any later revision with the integrating owner.', '']
    (OUT / 'SeaV2-REPORT.md').write_text('\n'.join(lines), encoding='utf-8')
    files.extend(OUT/p for p in ('SeaV2-source-audit.json', 'SeaV2-overview.png', 'SeaV2-REPORT.md'))
    files.extend(ROOT/'Art/Source/Art108'/p for p in (
        'sea_v2_layouts.py', 'build_sea_v2.py', 'audit_sea_v2.py', 'finish_sea_v2.py',
        'verify_sea_v2_sources.py', 'consolidate_sea_v2.py', 'sea_v2_protected_baseline.json'))
    hashes = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(set(files))}
    # A second pass catches inconsistent reads while constructing this index.
    for p, digest in hashes.items():
        check('final manifest SHA256 ' + p, sha(ROOT/p) == digest)
    manifest = dict(generatedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    owner='Codex 1 (Windows app)', allPassed=True, status='art complete; native/Mo acceptance pending',
                    maps=rows, totals=dict(maps=5, grounds=15, triangles=sum(r['triangles'] for r in rows),
                        meshParts=sum(r['meshParts'] for r in rows), buoys=sum(r['buoys'] for r in rows),
                        navigationChecks=nav_total, freshSourceChecks=fresh_total, individuallyOpenedMapPngs=55,
                        protectedLegacyFiles=len(baseline), indexedFiles=len(hashes)),
                    checks=CHECKS, hashes=hashes,
                    limits='Source/FBX and Blender review evidence; no native gameplay, touch or player acceptance. No git operations/commit.')
    (OUT / 'SeaV2-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    print('SEAV2 CONSOLIDATED PASS', len(CHECKS), 'checks;', len(hashes), 'indexed files;', nav_total, 'navigation;', fresh_total, 'source/FBX;', '55 reviewed PNGs; 114 protected files')


if __name__ == '__main__':
    main()
