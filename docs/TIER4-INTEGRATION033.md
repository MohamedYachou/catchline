# Tier 4 boat integration — TIER033 (2026-10-17)

Mo approved the larger BOAT032 boat exactly. The production asset preserves its
6.8 m hull length, 3.5 m beam, short squared cream canopy with teal brow/beacon,
1.48 × 0.64 m two-person table, knives/boards/chum pail, front raw storage and
rear prepared-fish boxes. The source comparison scene remains unchanged.

## Delivered model

- Editable production scene: `Art/Models/Tier4Production033/PrepFisherV1.blend`.
- Game asset: `Assets/Art/Models/Boats/PrepFisherV1.fbx` and `.placements.json`.
- Repeatable exporter: `Art/Source/export_tier4_033.py`.
- No comparison crew, labels, lights or stage are exported. The game uses actual
  animated crew at their existing scale, not frozen scale-study figures.
- `RawBuckets` and `RawIceCoolers` are independently switchable subtrees.
  `PreparedHold` is always present. Ice Box ownership selects the front variant.
- Two `PrepWorker_*`, two `RawInput_*` and two `PreparedOutput_*` anchors retain
  the approved positions. Rotating machinery and rod sockets have local pivots.
- Native mesh access is enabled so physical routing works in standalone players.

## First game integration

The boat is appended as saved hull ID3; IDs0–2 are unchanged. Four hired berths
plus the captain match the approved five-person layout. Three rods and one
stern net remain. The initial hold stays100kg/150kg with Big Cooler; this is
inherited test tuning, not a final tier4 economy decision. No extra rods/net,
purchase price or unlock goal has been invented.

The game derives walkable space from actual active model geometry at body
clearance heights. Both table positions, every rod, all resting positions,
front delivery access and stern net access connect through the real side aisles.
Changing front storage at port rebuilds the grid for its different footprint.
Net catch lands in a relocated basket behind the prepared boxes. Camera/water
contact dimensions and harbour offset account for the wider hull. Tier3 mass
market/depletion/upgrade rules also apply to tier4.

Select the new trial in the save-isolated Chandlery, or run the isolated player
with `-prepboat-trial`. `-prepboat-ice` selects upgraded front coolers. The trial
starts at Harbour mouth with two temporary deckhands and two temporary fishers,
60worms,200coins and a full tank. Trial-only downgrade to tier3 releases the
fourth trial berth. Real progression still stops at the existing tier3 refit.

## Verification

`docs/tools/check.ps1 -Name tier033-final -Method Catchline.EditorTools.PrepFisherChecks.ValidateAndBuild`
runs against Catchline-sim, never the main project in batchmode. Checks cover
native imported hull dimensions/upright orientation, exact socket placement,
readable meshes, both front-storage states, every job-to-job path including
both preparation spots, four live crew staying on clear tiles, actual catches
and stowing, stern net work/basket, return to port, additive hull/crew scratch
save round-trip, both shipyard trial controls and the existing tier3 regression.

Native Windows player captures include the actual HUD at1440×900 and844×390,
for both storage variants, under `docs/screens/tier033/`. This checks rendered
layout; scripted actions and desktop phone-sized frames do not prove physical
touch acceptance or player approval. A startup-black first capture was found
and the capture warm-up corrected before final delivery.

The editable model, source and normal game references are in the main checkout.
Playable preview build is `Catchline-sim/Builds/Tier033/Catchline.exe`; the
separate installation/shortcut, if present, points to `Catchline-play/Tier033`.
The real player save and existing Real/Tier3 shortcuts are untouched.

## Next station implementation — authorized direction, not present yet

The model and interaction positions are integrated; processing/chum jobs are
not functional in this first boat pass. Keep these requirements when adding them:

1. Up to two ordinary deckhands share one order list and reserve distinct fish
   and worker positions. The captain can help with a quick head-cut green-zone
   minigame. Work should be quick enough to run alongside fishing. Fuel bounds
   optional waiting; the player may wait or go home.
2. Drag to prioritize orders. Maintain10chum is a stock target; when satisfied
   or missing eligible input, lower-priority preparation can run. Using chum
   makes its order eligible again. Finish the current fish before switching.
3. Chum consumes eligible fish under configurable value/weight limits. It is
   earned each voyage, unpurchasable, attracts the largest fish and does not
   carry into the next voyage. Exact yield/time are still tuning decisions.
4. Sale preparation supports species/minimum-weight selection; +25% is a
   provisional bonus, not yet an economy value. Preserve species, specimen
   weight, contracts and cargo mass, and prevent preparing the same fish twice.
5. Raw fish in front buckets loses freshness until treated. The front Ice Box
   upgrade protects raw fish too. **Prepared fish never spoils, even without
   that upgrade**, and goes only then into the boxes behind each hand. This
   requires persistent per-fish prepared state; the current global ice rule
   alone is not the finished processing system.

No commit was created. Existing unrelated dirty work is preserved.
