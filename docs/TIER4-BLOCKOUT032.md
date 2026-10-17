# Tier 4 preparation boat — BOAT032, 2026-10-17

Crude, editable spatial study requested by Mo. **Not a production boat, gameplay
implementation or approved final size.** No existing FBX, scene, save or build changed.

## Current comparison

Reference: actual `CompactFisherV1.fbx`, 5.4 m hull length by 2.8 m beam.
First candidate was 6.2 by 3.1 m; Mo requested a larger boat after seeing it.
Current candidate is **6.8 by 3.5 m**, approximately 26% longer and 25% wider than
tier 3. These are hull dimensions, excluding rods, net gear and motor overhang.
The bigger candidate has roughly 57% greater length-times-beam envelope; it is a
meaningful deck-space increase even though neither linear dimension grows by half.

Both boats use the delivered crew rig at its original 0.95 m body height.
Reference shows four people; candidate shows captain, two fishers and two hands.
Five figures demonstrate fit only: final crew capacity remains to be decided.

- [Same-scale comparison](../Art/Models/Tier4Blockout032/comparison-buckets.png)
- [Top plan](../Art/Models/Tier4Blockout032/top-buckets.png)
- [Bucket station detail](../Art/Models/Tier4Blockout032/station-buckets.png)
- [Upgraded station detail](../Art/Models/Tier4Blockout032/station-ice-coolers.png)
- Editable scenes: `Art/Models/Tier4Blockout032/tier4-{buckets,ice-coolers}.blend`.
- Generator: `Art/Source/build_tier4_blockout032.py`.

## Layout

Slightly longer and wider familiar working hull, with a shorter squared canopy,
teal brow, short beacon mast and a distinct two-person work station. No enlarged
enclosed cabin, extra net system or industrial gantry. Existing rods/net remain
reference equipment, not a new tier-4 equipment specification.

One 1.48 by 0.64 m preparation table, about 0.67 m high, has two cutting boards,
knives and an orange chum pail beneath. Two hands stand abreast facing the table.
Raw storage sits immediately in front of the table. Prepared catch goes into two
freezer boxes directly behind the workers; the box centres are 0.64 m behind their
standing centres, so depositing should use a turn/reach rather than a deck crossing.
Storage contains only a few representative fish, not a literal visible 200 kg pile.

Two model variants show raw-storage buckets versus insulated ice coolers. Prepared
storage remains behind the workers in both. Art does not grant ownership of an
upgrade or imply that a separate rear-freezer purchase is required.

## Mo's current gameplay direction — design requirements, not implemented

These supersede earlier discussion about preserving freshness after preparation.

- Ordinary deckhands staff this shared preparation/chum station; up to two can
  work on separate fish with the same order list. The captain can also help via
  a quick head-cutting minigame with an acceptable green cutting zone.
- Drag work orders to set priority. `Maintain 10 chum` means stock on hand, not
  ten portions produced over the voyage. Finish the current fish before switching.
  When the target is met or no eligible input exists, do eligible lower-priority
  preparation. Consuming chum makes its order eligible again.
- Chum consumes eligible caught fish, is unpurchasable top-tier bait for the
  biggest fish, and must be earned again each voyage; it spoils/no carryover.
  Input filters can limit fish value or weight. Exact yield/timing still open.
- Sale preparation can select species and/or a minimum fish weight; exact filter
  semantics need final agreement. Approximately +25% sale value is a tuning
  proposal, not an implemented or tested reward.
- **Raw fish in ordinary front buckets still spoils and needs treatment.**
- **Prepared fish does not spoil.** Only after preparation is it deposited in
  the rear preserved/freezer storage. It should not need another paid upgrade
  to receive this no-spoil benefit.
- **Upgrading the front buckets to ice coolers protects raw fish as well.**
  Do not silently keep one global ice-upgrade flag that protects everything
  before this distinction is implemented.
- Efficient boats process while catching. Two hands should process quickly;
  fuel already limits voluntary end-of-voyage waiting. Mo explicitly accepts
  waiting to finish some preparation or returning with untreated fish.
- Track raw, on-table and prepared cargo once each. Preserve fish identity,
  contract/record eligibility and total accounted cargo; final capacity and any
  conversion yields remain to be designed. No silent cargo duplication/loss.

## Checks and limits

Rendered isolated Blender scenes, real production hull reference, same-scale
delivered crew, true orthographic comparison and top plan. Inspected bucket and
ice-cooler station views. Manifests record dimensions and station centres.
This is visual layout review, not native Unity import, route finding, gameplay,
freshness implementation or final player acceptance. No production export yet.

Initial candidate evidence stays under `v1-6.2x3.1/`; its oblique comparison had
reversed labels, so use its correctly labelled top plan for historical size review.
The current comparison corrects stage/caption orientation.
