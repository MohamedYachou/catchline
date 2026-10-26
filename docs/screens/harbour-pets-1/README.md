# Harbour pets — HARBOUR-PETS-1

Codex 1 (Windows app), 2026-10-26. Review evidence for Claude; no git commit or player-save changes.

The accepted Dog and Cat FBX bytes are copied unchanged into `Assets/Art/Models/HarbourLife`, with fresh import GUIDs. `ArtImport.cs` enables their Legacy animations. The existing recursive library builder already exposes `lib.M("Dog")` and `lib.M("Cat")`; no duplicate library entries are needed. `VoyageScenery.cs` adds exactly one call beside `DressTownsfolk`. See `scope-review.txt` for the complete two-file diff against the pre-task backup.

`VoyageHarbourPets.cs` adds an eight-metre dog beat along the quay at 0.75 m/s, random 3–8 second Sit/Sniff stops, and smooth turns before walking. The cat sleeps on a solid three-board lid over the artist's open top crate, looking around for three seconds every 20–40 seconds. The final perch is at x=-14, z=4.65 on the back paving; the dog's lane is z=3.95, x=-14.5…-6.5. Both retain artist scale. Pet materials are mapped locally to matte game materials.

## Verified captures and behavior

All four final images were opened individually. Both animals are visible outside the overview HUD buttons at 1440×900 and 844×390. The close views show the cat supported by the crate lid, the dog on the quay, and their scale beside a townsperson. No pink materials. A townsperson is staged solely for scale evidence; the overview camera and Canvas use the production presentation. Close crops use the same scene with a closer camera and no HUD.

- [Desktop harbour](harbour-1440.png)
- [Landscape phone harbour](harbour-844.png)
- [Dog close view](dog-close.png)
- [Cat close view](cat-close.png)

`PetsCapture.Run` in isolated `Catchline-sim` completed with Unity exit 0 and 66,894 assertions. The 600-second simulation exercised all actions, 50 dog stops, 20 cat looks, the full patrol, fixed ground heights, speed and turn limits, timing, clip lookup, scenery clearance, and material validity. It sampled all 172 Dog and 213 Cat imported animation frames: foot contact remained within 2.8 mm and exported root motion was absent. The first two capture runs were superseded after correcting a frontage obstruction and then phone HUD overlap.

`checks.json` records the behavior result. `review.json` binds the four reviewed image hashes, imported model hashes and source hashes. `capture.log` records the final third capture run.

## Integration check

Full `CrewCardsAbilityChecks.Regression` passed with wrapper exit 0 and actual Unity exit 0: 286 ability assertions, M2 data/live wages, bite/cage checks, and 217 tutorial assertions with zero unresolved targets. `regression.log` contains the integration completion marker and actual Unity shutdown result; `regression.json` is the ability-suite receipt. The four touched/new source files match the tested scratch bytes, and the main source hashes still match the capture receipt.

These are Editor URP captures with production Canvas composites and imported animation sampling. They do not claim standalone runtime, installed-player, listening, touch, or Mo's acceptance.

Temporary backup cleanup was rejected by automatic approval review as 'blocked by policy'. The two-file pets backup remains at ../Catchline-sim/Backups/harbour-pets-before; no alternate deletion attempt. The earlier strike backup is also retained after its separate rejection. MAP10 backups remain pending its chart handoff.
