# ART108 - Fable art-plan delivery

24 October 2026. Codex 1 (Windows app), finished with all currently defined, unblocked art work. Full v1 remains PARTIAL pending code-owned definitions and native integration. Source plan: origin/claude/nifty-galileo-i1ofka bb21248, docs/ART-PLAN.md. No C# integration, native acceptance or installed update is claimed. Publication is tracked below.

| Scope | Authored / verified | Native / dependency |
|---|---|---|
| A1 maps | All five expanded models, 15 grounds, 15 day + 15 night + 5 top plates. 9x footprint, independent FBX readback and centreline checks pass. | M4 finite-hull sweeps, import and native camera/water checks pending code owner. |
| A2 stations | All five station manifests, review scenes/plans and clearance/BFS receipts. 33 shared props including gear/event derivatives. | M1Checks, concurrent worker traces, source-axis import binding pending. |
| A3 crew | 11 portraits at 240/96/56, 4 editable card frames. Navigator shared20bone rig with Idle/Point/Warn readback. | UI choice/import and clip binding pending code owner. |
| A4 imagery | 41 packaged illustrations plus4textures/2effects verified: stages5, shop/supplies16, genericproducts2, buyers10, nightfish2, cheststates6. Textures4 have exact seam checks; effects2 reviewed. All40named event icons generated/exported/reviewed in batches15/15/10;87total imagery/texture/effect files in the manifest. | Special-product table and remaining20 event identities absent; do not invent. |
| A5 gear | JigRig, SpareRig, LanternOilCan, DeckLightPool sources/exports. | Power/material/animation binding pending. |
| A6 events | JellyfishClump, FlyingFishEvent, GullSwoop, SealHead, DolphinFin, InspectorLaunch, OffalPile, TableEel, SquallOverlay. Existing rival red rowboat referenced. | Event hooks and motion belong to code owner. |

## Index

- Stations: Art/Models/StationsV1/REPORT.md, kit-manifest.json; five <Hull>/validation.json and Assets/Art/Models/Boats/<Hull>.stations.json.
- Maps: Art/Models/Maps/<Map>/{grounds.json,lighting-presets.json,validation.json,review-sheet.png,three-grounds-top.png}.
- Navigator: Art/Models/NavigatorV1/REPORT.md.
- Cards: Art/Models/CardsV1/REPORT.md and review.png.
- Imagery: Art/Source/Art108/imagery/manifest.json and review sheets; Assets/Art/UI/v2/art108-manifest.json.
- Rebuild scripts and exact generation prompts: Art/Source/Art108/.

## Integration contracts

New runtime kit keys are Art108_<LogicalName>, map keys <Map>GroundsV1. Use runtimeModelId/runtimeFile, never the logical source name to resolve a model. Original hull dimensions/pivots/GUIDs are untouched. Portrait/stage/item art108 assets are alternatives to Claude's separately integrated v2 art; Mo chooses which ships. Do not replace v2 files.

Station positions are runtime Boat-local metres, Y up, bow -X. Ground anchors are world deck centres, not Boat-root translations; subtract the rotated HullDef.Center. Review water/lights are approximations and not exports. Native runtime and touch/player acceptance remain unverified.

## Current pickup

All40named event icons complete;3dualbackground plates reviewed atactual64px. final-imagery-audit.json verifies87manifestfiles,40event originals/prompts,33portrait variants,4frames and Navigator runtime/source parity. All35mapplates, last2stationplans,33propplate,6chests,texture repeats andeffects reviewed; reports written. final-audit.json verifies5originalhullhashes,5map-sourcehashes,33kit hashes,38unique runtime names andthe unchanged crew rig. Temporary cleanup was rejected by automatic approval review; namespace backup and42new Blender version backups remain (enumerated in final-imagery-audit.json). Code owner must supply the20 unnamed events and specific product IDs before those can be drawn. No subagents.


## Remaining work and release

1. Code owner defines20 further event identities and the special-product species/IDs, then commissions those illustrations. The plan names40events and targets60; no unapproved gameplay content was invented.
2. Code owner imports/binds models, station manifests, animation clips, maps and chosen UI art; runs M1/M4/M6 and native desktop/landscape/touch checks. Artwork export verification does not establish playability or visual acceptance in the assembled game.
3. Mo chooses whether any art108 UI alternatives replace the already integrated v2 set. Both sets remain intact.
4. Automatic approval review rejected temporary-backup cleanup. The backups remain; no bypass attempted.

No build, install or save change. No subagents. Codex1 is finished/idle; all ART108 reservations released, including source generators and imagery. Resume only the missing content or an integration correction that is actually assigned.

## GitHub publication - 24 October 2026

Mo explicitly authorized committing and pushing this ART108 delivery. Both existing delivery audits passed again before staging. Sources, exports, prompts, manifests, previews and reports are included; ignored Blender version backups and the external temporary backup are excluded. Other owners' crew-style work, fish work, Art/STYLE.md and unrelated drafts remain outside this commit. Shared comms history is preserved.

Target: origin/proto/deck-sim at github.com/MohamedYachou/catchline. Art delivery commit: 137ed00b3e1e14d6a08f8625a10989f6c74f416f (772 files). Normal push succeeded; GitHub refs/heads/proto/deck-sim was verified at that exact SHA. Git LFS confirmed420/420objects uploaded (226MB). This publication receipt is included in the following notes-only commit. Native/runtime acceptance and missing content definitions remain unchanged.
