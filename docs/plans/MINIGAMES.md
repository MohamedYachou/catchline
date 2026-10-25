# Minigames — mobile taps and drags

Mo, 2026-10-25: "think about the net mini game, other mini games, its mobile so even like just taps and stuff im
thinking tap or drag quickly for like the cages thers no minigame for those yet". Mo is away, so Claude decided the
designs below; each is open to Mo's review.

## Shared rules

- **One finger, one gesture per game.** Tap, hold, drag or flick. Never two at once, never a virtual stick.
- **Ten seconds or less.** A minigame is a beat in the voyage, not a level. The crew does the same job automatically
  and more slowly, so playing is always optional and always a bit better.
- **Skill pays, failure is mild.** A good run gives a bonus (more kg, a size grade, time saved). A bad run gives the
  crew result, or a small loss (a torn net, one crab escapes). Never a hard fail that costs a whole trip.
- **The rod view is the template.** Full-screen view, the same cream UI, the same tip line at the bottom for the
  first two plays, the same exit button. The view zooms in from the deck and back out to it.
- **Readable at 390 px wide.** Every target is at least 64 px. Every cue has both a shape and a sound, never colour
  alone.
- **Sound on every touch.** A tap gets a click, a good tap a brighter one, a mistake a dull thud.

## 1. Net: cast and haul (upgrade of VoyageNetGame.cs)

Today the net game is a bar: three timed taps to set, and tapping to winch while keeping tension out of the red.
The rules stay. The view becomes a real scene.

- **Cast (setting).** The camera sits behind the stern looking aft. The net is bundled on the rail. A marker swings
  across the water (NetGamePhase). **Flick up** when the marker is in the green: the net flies out and opens in an arc
  where you threw it. Three flicks pay out three panels. A flick outside the green lands the panel in a heap; it
  counts as today's mistake.
- **Haul.** The view looks down at the drum and the net rising out of the water. **Tap** to turn the drum; each tap
  is one pull. The rope creaks louder and the drum glows warmer as tension rises. Over the red mark the mesh
  stretches visibly and the creak becomes a twang: that is the mistake.
- **The bunt.** The last third of the haul shows the catch: fish shapes thrashing in the bag. A **big fish** flashes
  once near the edge of the bag. Tap it within 0.6 s to hold it in; miss it and it slips out. This is the skill
  bonus: the crew never saves the big one.
- **Result card.** The catch fans out on deck (the existing crate animation), kg counted up.

## 2. Crab cages: pull, shake and sort (new)

Cages are Tier 5 buoys today (VoyageTier5.cs, TryBuoyWork). The crew recovers them on a timer and the captain cannot
play. The captain now can, from the buoy station, when a cage has soaked.

- **Pull (tap fast).** The cage rope runs over the hauler wheel. **Tap as fast as you can.** Each tap lifts the cage
  a little; the line slips back slowly between taps. About 12 taps bring it up. The cage swings into view through the
  water, crabs visible inside.
- **Snag (drag).** About one cage in three snags on rock halfway up. The rope goes tight and shudders, with a left or
  right arrow. **Drag that way** to free it. Dragging the wrong way costs a second. That is the only way to lose time.
- **Sort (flick).** The cage tips open on the rail. Two to four crabs drop onto the sorting board one at a time. Most are under the legal size, as in a real pot.
  Each shows its size against a gauge on the board. **Flick up** keeps it (to the hold). **Flick down** throws it back.
  - Undersize crabs and berried females (eggs under the tail, a distinct orange shape) must go back. Keeping one is a
    fine on the sale, shown on the result card, and lowers the spot's richness. That gives the sort its point.
  - A kept keeper lands in the hold and pays a 10 % "hand-sorted" bonus at once. A kept undersize or berried crab is
    confiscated and fined half its value. A sorted cage is worth about 1.5 times a crew recovery (one crab).
- **Result.** "Cage 2: 4 kept, 2 back · +12 %".

Model needs (Codex 2): an open-top crab cage with a hinged lid, a hauler wheel, a sorting board with a size gauge,
and a berried female crab (orange egg mass).

## 3. Process table: gutting (new, later)

At the process table the captain can gut a fish: **one drag** along a dotted line from the vent to the gills. On the
line, the fish is cleaned and grades up (it sells as "dressed", +15 %). Off the line it still gets cleaned with no
bonus. Three fish in a row on the line make a streak.

## 4. Jig: rhythm (new, later, for jig rigs)

The jig station is a short vertical line. A lure bobs. **Tap on the beat** (a ring closes on the lure): each on-beat
tap adds attraction, and a fish rises in from the dark. Three good beats hook it, which leads into a short rod-style
fight.

## 5. Net repair (new, later)

When a net tears, the captain can mend it in harbour instead of buying a new one: **trace** a zigzag over the hole,
following the dotted path. A clean trace saves the replacement cost. The crew mends it for the same coins it would
cost to buy.

## Order of work

1. Cage pull/snag/sort: simulation and checks first (Claude), then the full-screen view (Claude), then art (Codex 2).
2. Net view: the scene behind the existing bar rules (Claude), with drum and bunt art (Codex 2).
3. Gutting, jig and repair are logged as to-do items; they are not started until 1 and 2 are accepted.

### Status (2026-10-25, overnight)

- Cage: built (CageModel.cs, VoyageCageView.cs), CageModelChecks + CageViewChecks pass; renders in
  docs/screens/overnight/cage-*.png. Runs on stand-in hauler/board and the EmptyPot until CAGE-ART-1 lands.
- Net view: built (VoyageNetView.cs) on the unchanged VoyageNetGame rules: setting shows the float swinging over a
  green window on the water and throws a panel (or a heap on a miss) per tap; hauling shows the drum warming toward
  red, the net strands taut or stretched and the bunt of fish rising in the last third. NetViewChecks; renders
  net-*.png. Not yet done: the big-fish tap in the bunt (a new rule with a payout; needs Mo's OK on the bonus size).
- Gutting (section 3), design settled 2026-10-25 (Claude, Mo away; rules can be tuned): no price change. The reward is
  speed, so the economy stays as it is. The captain takes a table job (DeckScheduler.CaptainTable, a TableWork job
  that hands its finish to a CaptainBench hook instead of Actor.Act). The camera drops to the board (GutView), one
  drag vent to gills: on the line the fish is done in 0.5 s and the streak grows; off the line it is a ragged cut
  that still finishes after the crew's normal 3 s. Art: docs/briefs/GUT-ART-1.txt (Codex 2). Code starts when the kit
  lands; stand-in primitives are not built first, per Mo's "new features inherit finished components".

### For Mo (2026-10-25 morning): two minigames wait on a decision

Art for both is done and accepted (Art/Models/JigKit, Art/Models/RepairKit). Code is not started, because each changes
the game beyond a view:

- **Jig (section 4):** no boat has a jig station today (StationKind.Jig and JobKind.JigCycle exist but nothing builds
  them). The minigame needs jig gear first: which boat gets a jig station (proposal: the tier-5 boat, as a night rig,
  matching Lise's "Jigs (night)" card), and what it catches (proposal: mackerel/pollock/cod from the existing tables).
- **Net repair (section 5):** today a shallow-net tear simply uses up a net (replacement 30 coins). Mending makes a
  tear cost time instead of coins. Proposal: a torn net goes to a "torn" pile; in harbour the captain mends it free
  with the trace minigame (a clean trace restores it; a ragged one needs another go), or the crew mends it for the
  replacement price. This lowers net costs for active players.
Say yes/no/change to either and Claude builds it.
