# Tier 5 Buoy fisher — BOAT071, 18 October 2026

Mo approved BOAT069 and requested the boat in the game. This delivers the approved
**8.5 × 4.2 m hull**, six hired crew plus captain, real fishing/processing/service
jobs, native desktop/landscape evidence and Windows players. No crew-card abilities
from Codex1's ongoing design discussion are implemented by this task.

## Current integration status — CREW096

This boat now ships with the real processing pipeline and accepted live Management
dashboard from [DASH087](DASH087.md); [DASH092](DASH092.md) routes every active
Real/DASH/Tier3/Tier4/Tier5 shortcut to that verified version. Boat/duties and
Management sit bottom-right. [Crew integration handoff](CREW-MANAGEMENT-INTEGRATION.md)
maps gameplay/forecast/telemetry connections for future cards. Cards are not yet
implemented. The maintenance implementation described below is the **legacy shipped
model**: latest [crew decisions](CREW-CARDS-DESIGN.md) require electrical-only
maintenance, no engineering wear on bare rods/nets/cages, and a redesigned repair
policy. Those decisions still need runtime/forecast/save integration.

## Boat and equipment

Saved hull ID **4**, model `Tier5FisherV1`. Existing hull IDs0–3 are unchanged.

| Port-selected layout | Rods | Independent nets | Buoys |
|---|---:|---:|---:|
| Rod-heavy |4|1|2|
| Net-heavy |2|2|2|

Both variants keep the prep station, raw storage, preserved catch storage and
engineer service fittings. The two fixed rods remain when the optional pair is
exchanged for net2. Tier5 includes the convertible module; switch it in harbour
at **Gear → Second net module**. Existing Tier4 module purchase/cost remains.

Six berths are shared. Default test team: three fishers, one net/collecting
Deckhand, one Deckhand assigned Prep, and one Engineer. The fourth rod is free
for the captain. The two-net example uses two fishers, two net/collecting
Deckhands, one processor and one Engineer. Processor is a Deckhand duty, not a
new mandatory profession/card. Crew contracts still use the existing temporary
system until the separate crew-card redesign is implemented.

Fishers service buoy stations during rod downtime. Each buoy soaks65seconds and
requires2seconds recovery plus walking; one edible crab weighing0.5–1.8kg goes
onto the deck. It then follows carrying → processing input → preparation →
processing output → separate carrying → main hold (DASH082/087 supersedes the
original direct-storage route). Full storage prevents recovery/reset, preserving readiness.
New saved species ID29 reuses the existing authored Crab mesh and receives a
matching transparent rendered portrait. Crab is buoy-only; existing rod/net
local species tables stay intact. Timings/weights/prices are initial tuning.
Existing bait rules are not redesigned here.

Tier5 processing retains the fish, stops further freshness loss and records a
**1.5× value multiplier**. Raw value is1×. Existing prepared fish retain their
legacy1.25× multiplier, including old saves. Tier5 processing makes no chum;
Tier4 chum/prep behavior remains. Processor helps collect loose fish when no
eligible processing input exists. **Boat / duties** opens condition information,
crew duties and processing priority (oldest or highest value first).

Engineer is appended role ID2. Engineers physically walk to installed equipment,
maintain condition and prioritise faults. All eight equipment records (four
possible rods, two possible nets and two buoys) retain condition/faults in saves;
only installed gear wears/receives service. Condition affects rod reeling and buoy
soaking efficiency; operating wear increases fault chance. Rod/net/buoy losses on
Tier5 come from equipment condition rather than the old random worker strike/net
recovery failure. The captain can help service equipment. Existing authored hand
work/reel clips animate maintenance, repairs and buoy recovery. Earlier boats'
worker-success rules are preserved.

## Access and initial tuning

Real progression: own Prep fisher, then buy **Buoy fisher / Tier5** in Gear for
**18,000 coins**. Base hold240kg; big-cooler upgrade360kg. Owned upgrades/crew
transfer and the new hull gets its convertible module. No automatic save credit,
hull replacement or progression skip is applied to the real game. These are
initial progression values, not measured grind-time guarantees.

Desktop **Catchline - Tier 5 Test** starts directly on the boat with six crew,
supplies and an isolated budget. It never reads or writes the player's save.
Return to harbour to switch layout or change crew. **Catchline - Real Game** is
retargeted to the current persistent build. Tier3/Tier4/Tier5 shortcuts now all
use the current isolated Test binary, preserving each trial flag; older versioned
installations remain historical archives (DASH092).

## Assets and implementation

- Generator/export: `Art/Source/export_tier5_071.py`.
- Editable production scene/export checks: `Art/Models/Tier5Production071/`.
- New boat FBX: `Assets/Art/Models/Boats/Tier5FisherV1.fbx`.
- Crab portrait: `Assets/Art/UI/fish-crab.png`; mesh reused from Props/Crab.
- New runtime partials: `GameStateTier5.cs`, `VoyageTier5.cs`, `VoyageTier5Capture.cs`.
- Focused native checks/builders: `Assets/Editor/Tier5Checks.cs`.
- Physical anchors and exported groups in `Art/Models/Tier5Production071/export.json`.
- Source/build/install receipts and capture/install scripts: `docs/screens/tier071/`.

The production asset removes the review figures, studio and baked rods. It retains
named switchable raw/iced storage and net2 groups plus exact working anchors. The
FBX roundtrip checks the hull and required names. Both material/import/ArtLibrary
contracts are installed in the main Unity source as well as the isolated build.

## Verification and limits

`check-tier071-integrated.log` passes Tier071, CompactFisher, Tier033, Prep035,
Pace036, NetHaul, Module042, Balance045 and PTS water checks and builds both players.
`check-tier071-delivery.log` passes final Tier071 gameplay, actual UI callbacks,
actual authored repair clip state, water guard and both player builds (exit0).

Both layout grids pass18distinct job/rest points and all pairwise routes. The
scripted180-second rod-heavy trace produces real catches, four buoy recoveries,
maintenance and prepared cargo with seven actors remaining on clear tiles. The
net-heavy trace confirms both net jobs; return/refit restores four rods. Tests
cover actual repairs, condition/role/hull save roundtrip, preserved old hull IDs,
exact refit charge/no duplicate purchase and Tier5 prepared value/no chum.

Native player captures include actual Canvas/crew/boat/processing/condition/port
controls at1440×900 and844×390. Readable overlapping-modal defects found during
review were fixed. Final exact-build native capture exits0 with no listed runtime
reference or shader exceptions.668 source/model/shader/UI/library inputs match
the tested scratch; each installed distribution has174 verified files. The
installed-build receipt records shortcut readback and real-save fingerprints.

These are desktop native/scripted checks and visual reviews. Actual mobile-device
performance, physical touch acceptance, long-run economy tuning and Mo's runtime
play acceptance are not claimed. Future crew-card modifiers require the separate
crew implementation. No commit/branch reset or unrelated asset replacement.
