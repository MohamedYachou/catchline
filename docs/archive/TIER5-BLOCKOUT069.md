# Tier5 — six-crew modular boat study / BOAT069

Mo supplied the missing original equipment discussion during this task. The following
brief supersedes the provisional legacy DayBoat/four-pot-rack assumptions.

## Confirmed boat brief

Six hired crew plus the captain, up from Tier4's four hired crew.

Fixed equipment: two rods, two buoy fishing/trap stations, one net, one fish
processing table and mechanic service access. One interchangeable bay fits
**two additional rods OR one additional net**. This gives:

| Configuration | Rods | Nets | Buoys |
|---|---:|---:|---:|
| A — rod-heavy |4|1|2|
| B — net-heavy |2|2|2|

One processor and one mechanic leave four flexible hired workers. A1 uses three
fishers and one deckhand, with the captain using rod4. A2 uses four fishers and
no dedicated deckhand: captain collects rod fish and operates the net, helped
by the processor when idle. B uses two fishers and two deckhands; captain helps
where needed. These staffing arrangements come from Mo's supplied discussion.

Fishers operate rods and buoys; buoy catch goes directly to storage. Deckhands
operate nets and collect loose rod catches. Processor collects fish when no
processing is available. Mechanic continually services equipment and interrupts
routine maintenance for repairs. Crew cards remain freely chosen within capacity;
the example placement of figures does not prescribe individual card identities.

Mo's accompanying gameplay direction: raw fish value100%, processed150%; food
processing is for sale rather than bait. Equipment durability and occasional
mechanical failures replace random crew failure. Operating wear increases failure
risk when neglected; mechanic maintains durability and repairs faults. This report
records those requirements; no gameplay values or failure logic changed here.

## Size and visual delivery

Candidate hull **8.5m long ×4.2m beam**, compared at identical scale with the
existing Tier4 **6.8×3.5m**. This is +25% length, +20% beam and +50% rectangular
envelope, not a claim of50% usable deck area. Crew meshes retain their delivered
size. Seven people aboard candidate, five aboard reference.

The source is an isolated blockout derived from existing Tier4 meshes. The
canopy/table/storage remain familiar while the hull, extra work positions,
engineer service point and modular fishing layout explore the next step. The two
buoy/crab-box positions are exterior conceptual placeholders, not a final trap
animation or an approved number of pots carried per buoy. No four-pot rack is
assumed. Bow is source-Y; screenshots label each boat explicitly.

- [Same-scale comparison](../Art/Models/Tier5Blockout069/comparison.png)
- [Rod-heavy top plan](../Art/Models/Tier5Blockout069/top.png)
- [Rod-heavy close view](../Art/Models/Tier5Blockout069/tier5-detail.png)
- [Net-heavy close view](../Art/Models/Tier5Blockout069/tier5-net-layout.png)
- [Net-heavy top plan](../Art/Models/Tier5Blockout069/tier5-net-top.png)
- [Editable Blender scene](../Art/Models/Tier5Blockout069/tier5-size-study.blend)
- [Generator](../Art/Source/build_tier5_blockout069.py)

## Verification boundary

Generator checks finite object positions, exact candidate hull dimensions within
2cm, and seven unchanged-scale body meshes. Renders show actual geometry.
Spatial placement is a first visual study; runtime routing, working clearances,
interactive bay switching, durability, catch/processing logic and Unity/mobile
camera acceptance remain unverified. No production FBX, game source, save, build
or installation changed. Final size remains Mo's review decision.
