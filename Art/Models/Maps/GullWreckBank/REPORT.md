# Wreck bank — MAP7-WRECK-BANK-1

Codex 1 (Windows app), 2026-10-25. Terrain/import/safety/post-life capture delivery is complete; overall acceptance remains **PARTIAL** pending lead visual/contract review. Claude's corrected chart point(.72,.56), glyph/landmarks, sandy-green water and WreckLife integration are included in the final rebuild. This report does not grant acceptance.

The seventh map is a 300 × 240 m offshore sandbank with a 30 m half-sunk rusted steamer, leaning funnel/mast, flooded hold, broken bulwark and low angular sand shelves in the three fishing frames. No wildlife, cardinal buoy or baked foam fins are included. Six named empty anchors are exported for Claude's runtime life. Source: [blend](GullWreckBankSeaV2.blend), [FBX](GullWreckBankSeaV2.fbx), [navigation](navigation.json), [ground data](grounds.json).

Spot6 is Wreck bank, 980 coins (1.4 × Seal skerries), RowSeconds26, BiteWait1.3, appended after Skerries. Exact brief blurb and per-ground daytime pools are wired in GameData/Grounds; prior map slots remain in order. Existing BuyChart has no previous-chart requirement; no new progression gate was invented. Life integration and prohibited chart/trip/minigame files were not edited.

| Ground | Anchor X,Z | Depth | Day pool |
| --- | --- | --- | --- |
| The wreck / the-wreck | -72,-24 | 4.2m | Conger40, Cod30, Pollock25, Turbot2 |
| Herring bank / herring-bank | 2,61 | 2.0m | Herring50, Mackerel30, Whiting20 |
| Sand edge / sand-edge | 99,-35 | 3.2m | Plaice50, Turbot12, Whiting25, SpottedEagleRay1 |

The map has 25,236 triangles, 295 meshes, seven real closed navigation obstacles and seven actual shallow slices. Navigation is independently cut from real terrain edges at local waterline0 and -1m; no hidden collision proxy substitutes for visible terrain. Root transforms are identity/metres and imported anchor positions were checked after the runtime -0.32m map offset. [Validation](SeaV2-validation.json) records source/FBX/navigation hashes and actual FBX roundtrip vertex error below0.000018m. [Independent source audit](SeaV2-source-audit.json) passes55/55 checks. [Art audit](SeaV2-audit.json) passes55/61, retaining **six failed full-zone exclusions**, two per ground. No assertion was relaxed.

The required 6–12m lower-corner landmarks conflict with the inherited 12–20m full-ground-circle exclusions. Shelf centres are about7.22m from their anchor; the wreck bow about6.05m. Closest visible obstacle edges are about4.67m away; this is distinct from the larger zone radius. Actual navigation safety is checked separately. The114 protected old-map file hashes remain unchanged in the audit. Claude must review this explicit exception, as with accepted MAP6 terrain.

All eleven final Blender images were individually opened after the final terrain rebuild, with hashes in [visual review](SeaV2-visual-review.json). Day frames show low stepped sand in the lower corners and cropped rusty bow at the wreck. Night corner silhouettes are dim but visible. Funnel/mast are present in wide/top views, outside the tight bow-focused deck frame. Herring/Sand shelves are similar; runtime Herring bank life now distinguishes them. Far horizon proxies stay outside the playable area.

- [The wreck day](SeaV2-the-wreck-day.png), [night](SeaV2-the-wreck-night.png)
- [Herring bank day](SeaV2-herring-bank-day.png), [night](SeaV2-herring-bank-night.png)
- [Sand edge day](SeaV2-sand-edge-day.png), [night](SeaV2-sand-edge-night.png)
- [Wide day](SeaV2-wide-day.png), [wide night](SeaV2-wide-night.png), [top](SeaV2-top-base.png), [navigation plate](SeaV2-navigation-plate.png), [review sheet](SeaV2-review-sheet.png)

Runtime asset import is byte-identical to the delivered FBX/navigation, with fresh GUIDs and project metre import policy. Additive map lists are in SeaNav and VoyageScenery. The scratch-only WreckBankMapChecks fixture verifies seven maps, chart980 purchase/unaffordable979, all six empty-anchor world transforms, exact species weights,420 directed routes across five hulls,21 sea lanes, five baseline harbour hull trips and three new-ground full departure/anchor/normal captain bait-cast/home trips. It checks collision/border and all six travel legs. Fishing proof stops at a normally cast rod in water; caught-fish yield is not asserted.

Claude changed spot6's chart point after the full geometry run began. The targeted PostIntegration fixture then passed the three updated home-facing approach lanes, three additional complete normal bait-cast/home trips, four runtime GannetDive components and one cardinal BuoyBob per trip, with actual Unity exit0. Unchanged terrain/data/import hashes are tied to the original safety source snapshot;420 geometry routes were not unnecessarily repeated. Component presence does not establish animation presentation.

Native capture and safety results, exact commands and limits are in the [evidence handoff](../../../../docs/screens/map7-wreck-bank-1/README.md). The [delivery summary](SeaV2-delivery.json) and final verification receipt in that evidence folder bind the final state. All ten fresh post-integration frames were individually opened. Greener water, airborne gannets and silver boils are visible (best at844×390); cardinal buoy is heavily cropped/covered at the wreck lower-right, and perched wreck gulls are outside the tight view. Hull/bubble space remains clear. The corrected chart pin, full Wreck bank label and980coin price are now readable at both sizes, clear of the header and Harbour mouth. Full wreck/funnel/mast and complete buoy/perched-gull presentation remain review limits. No installed-player replacement, save access, main-project batchmode, git operation or subagent was used.

Rebuild using the existing Blender/uv workflow: `map7_wreck_bank.py build`, `review`, `audit`; independent actual-source audit via `verify_sea_v2_sources.py -- GullWreckBank`. [Builder](../../../Source/Art108/map7_wreck_bank.py), [evidence finalizer](../../../Source/Art108/map7_finalize.py). Do not rerun accepted earlier map authoring unnecessarily. The first assignment step, fresh MAP6 life recapture, is separately documented in [MAP6 life evidence](../../../../docs/screens/map6-life-recapture/README.md).
