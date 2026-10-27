"""Record completed manual visual review and produce additive SeaV2 handoff files.

Only run MAP --reviewed-all after opening every current image individually.
This flag records the human/agent review; it does not perform visual inspection.
"""
import sys,json,datetime
from pathlib import Path
from audit_sea_v2 import audit,plate,sheet,publish,sha
from sea_v2_layouts import LAYOUTS
ROOT=Path(__file__).resolve().parents[3]

def finish(name):
    assert '--reviewed-all' in sys.argv,'manual visual review required first'
    nav,rec=audit(name);assert rec['allPassed']
    folder=ROOT/'Art/Models/Maps'/name
    paths=[f'SeaV2-{g["id"]}-{t}.png' for g in nav['grounds'] for t in ('day','night')]+['SeaV2-wide-day.png','SeaV2-wide-night.png','SeaV2-top-base.png','SeaV2-navigation-plate.png','SeaV2-review-sheet.png']
    review=dict(map=name,reviewer='Codex 1 (Windows app)',reviewedUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      allIndividuallyOpened=True,imageHashes={p:sha(folder/p) for p in paths},
      scope='Each current day/night ground, wide day/night, top base, annotated navigation plate and review sheet opened in view_image. Art framing/readability/geometry review; not native or Mo acceptance.',
      camera=dict(projection='orthographic',horizontalSpanMetres=10.24,pitchDegrees=45,yawDegrees=35,resolution=[1440,900],
                  anchors=nav['artReviewAnchors'],boatReference='Art/Models/GullHarbour/Boats/Rowboat.blend',boatDeckY=0))
    (folder/'SeaV2-visual-review.json').write_text(json.dumps(review,indent=2))
    # Blender values are explicit authoring presets, not equivalent Unity light units.
    lighting=dict(map=name,units='Blender authoring values; translate and verify separately in native runtime',
      day=dict(sunEnergy=1.5,sunRGB=[1,.90,.74],ambientRGB=[.55,.73,.80],ambientStrength=.48,boatFillWatts=350,boatFillRGB=[.66,.84,1]),
      night=dict(sunEnergy=.12,sunRGB=[.44,.58,1],ambientRGB=[.08,.13,.26],ambientStrength=.25,boatFillWatts=75,boatFillRGB=[.32,.46,1],
                 deckPools=[dict(deckRelativeXZ=[.3+i*1.4,.5],worldY=1.35,powerWatts=45,rgb=[1,.66,.30],spotAngleDegrees=78,blend=.55) for i in range(2)]),
      water=dict(transmission=.82,roughness=.32,ior=1.333,volumeAbsorptionDensity=.055,
        colourRule='lerp RGB (.025,.48,.50) to (.008,.12,.24) by clamp((nominalDepth-1.2)/8)',dayEmission=.14,nightEmission=.018),
      fog=dict(insetMetres=30,densityRule='0.010 * max(clamp((abs(x)-(width/2-30))/30), clamp((abs(z)-(height/2-30))/30))',wideReviewOnly=True),
      limits='Static Blender water/light/fog review. Runtime water, fog, lantern attachment and daylight switching are integration work; source model intentionally contains no water or review boat.')
    if name=='GullRockyPoint':
        lighting['water'].update(transmission=.96,roughness=.20,dayEmission=.035,nightEmission=.005)
    (folder/'SeaV2-lighting-presets.json').write_text(json.dumps(lighting,indent=2))
    publish(name,nav,rec)
    v=json.loads((folder/'SeaV2-validation.json').read_text());layout=LAYOUTS[name];w,h=layout['size']
    lines=[f'# {layout["title"]} / SeaV2', '', '24 October 2026. Codex 1 (Windows app). Approved MAP-PLAN art delivery; additive files only.', '',
      f'{w} x {h} m playable water; {v["triangles"]:,} triangles / {v["meshCount"]} mesh parts. {len(nav["grounds"])} anchor zones, {v["islandCount"]} actual waterline outlines and {v["shallowCount"]} shallow outlines, {v["buoyCount"]} red-white border buoys.', '',
      f'Independent actual-FBX import matched triangle counts and source vertices within {v["roundTripMaxVertexError"]*1e6:.3f} micrometres. Independent polygon/clearance/routing audit passed {len(rec["checks"])} checks. All 11 current PNGs opened individually, then hash-recorded in SeaV2-visual-review.json.', '',
      '| Ground | Centre X, Z (m) | Radius | Nominal depth | Pool ID |','|---|---|---|---|---|']
    for g in nav['grounds']:lines.append(f'| {g["name"]} | {g["centre"]["x"]}, {g["centre"]["z"]} | {g["radius"]} m | {g["nominalDepth"]} m | {g["poolId"]} |')
    lines += ['', '## Model and placement', '',
      f'Editable source: `{name}SeaV2.blend`; triangulated export: `{name}SeaV2.fbx`. Runtime copies are `Assets/Art/Models/Environment/{name}/{name}SeaV2.fbx` and `navigation.json`, byte-identical to the reviewed art delivery. Existing GroundsV1/original assets, JSON and .meta files remain untouched.', '',
      'Source axes follow ART108 `(world X, -world Z, height)`. The export retains verified X compensation. Unity model placement is world `(0,-0.32,0)`, identity rotation/scale. Do not centre or rescale the model to fit its bounds: bounds include unreachable horizon art and the continuous seabed. Boat positions are WORLD deck centres at Y=0; translation is deck anchor minus rotated HullDef.Center, independent of map root Y.', '',
      'navigation.json uses world XZ metres: islands/shallows are objects with id and CCW vertices `{x,z}`, obtained by actual closed terrain-edge slices at local waterline0 / -1m. Each outline is <=64 vertices. Border is CCW; cameraBounds uses `{min:{x,z},max:{x,z}}`. All three legacy IDs/names/pool IDs/nominal depths are preserved; the new centres/zones supersede old GroundsV1 anchors.', '',
      'Every whole ground circle is outside the actual shallow polygons and the islands inflated2m, and contained by the border. Harbour and 0.6m-radius buoy bases clear the 2m island inflation. Outer markers are on the border at25-30m spacing. Horizon centres are beyond the border.', '',
      'All6 harbour/ground-pair static visibility routes exist for discs of radius2m and4m. At least one ground-to-ground straight line is blocked by inflated land. Route polylines are art-side audit evidence, not runtime navigation data. Shallow costs, hull turns, speed, collision recovery and10-20s timing remain code-owner checks.', '',
      '## Islands and views', '']
    for spec in layout['islands']:lines.append(f'- **{spec["id"]}:** {spec["purpose"]}')
    lines += ['', 'SeaV2-navigation-plate.png shows actual waterline and -1m slices, zones, all border markers, a dashed straight arrow for each ground pair, and solid verified detours around blocked lines. SeaV2-review-sheet.png pairs all3 day/night gameplay-camera renders and the wide fog/horizon day/night views. Review sample points are recorded in navigation.json artReviewAnchors; each lies inside its zone.', '',
      'SeaV2-lighting-presets.json records warm daytime key/cool ambient, cool night lighting, two warm deck pools, depth water tints and smooth30m fog falloff. Night/day share one exported model. Review-only water, fog, camera, boat and lights are retained in SeaV2-Review-only.blend and excluded from the model export.', '',
      '## Evidence and limits', '',
      '- SeaV2-validation.json: saved source/export/navigation hashes, counts, bounds and independent actual-FBX vertex error.',
      '- SeaV2-audit.json: polygon/zone/harbour/buoy/border/routes/protected114-file checks.',
      '- SeaV2-visual-review.json: exact opened-image hashes and camera/sample contract.',
      '- SeaV2-delivery.json: runtime-copy and all11 PNG hashes.', '',
      'These are Blender art reviews, without native HUD, crew, runtime water, sailing or touch behaviour. Claude/code-owner must bind SeaV2 model/navigation, import new metadata, reconcile fish pools/depths, verify all5 hulls and camera clamps, tune sailing and inspect1440x900/844x390 native captures. No Unity scenes, C#, git operations, commits or player-save changes were made by this art task.', '',
      'Builder: Art/Source/Art108/build_sea_v2.py; independent audit/plate/sheet: audit_sea_v2.py; manual-review handoff: finish_sea_v2.py. Old map reports/receipts remain historical GroundsV1 evidence.']
    (folder/'SeaV2-REPORT.md').write_text('\n'.join(lines)+'\n')
    print('FINISHED',name,v['triangles'],len(rec['checks']))

if __name__=='__main__':finish(sys.argv[1])
