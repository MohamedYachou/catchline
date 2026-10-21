# Catchline visual standard

## Authority and scope

Close translation of the existing goal renders, confirmed by Mo on 2026-10-15.
The fishing view sets the bar; harbour, menu and subsequent features inherit it.
Art/STYLE.md remains authoritative for model geometry, palette and materials.

## World

An inviting miniature working harbour. Broad bevels, honey timber, ivory rails,
navy paint, warm sunlight, cool ambient fill and small busy sailors. No global
outlines, noisy texture detail, heavy bloom, depth of field or glittering ocean.
Frame the boat generously, leaving quiet water for interface and interactions.

## Tokens

| Role | Value |
|---|---|
| Ink / navy | #173F57 |
| Cream surface | #F4EFE3 |
| Primary action | #E36A35 |
| Sea / secondary action | #168F9F |
| Water highlight | #64C7C4 |
| Bite / attention | #E6AD38 |
| Success | #3E9A5B, accompanied by words or an icon |
| Error | #C8443A, accompanied by recovery copy |
| Typography | supplied Fredoka Medium; navy on cream, ivory on navy |

## Composition and components

- Fishing: compact cream status panel upper left; coins/pause/return upper
  right; portrait crew strips lower left; action bubbles attached to the task.
  The centre belongs to the boat. Strike panel occupies lower-centre water.
- Use supplied sliced artwork, icons and fish/crew portraits consistently.
  Icons get real space; do not pad button strings with spaces to fake alignment.
- Stable readable type hierarchy, generous internal padding, short copy and
  grouped resources. Avoid rows of tiny debug statistics.
- Catch reward: restrained portrait, species, weight, value and record badge.
  Never cover the Carry action or open a blocking reward modal.
- Menu: supplied illustrated harbour, real logo and left-aligned cream menu
  with one clear primary action. Settings and pause share the component family.
- Harbour shops use the same typography, illustrated headers, item icons,
  accessible controls and explicit owned/unavailable states.

## Motion

Calm layered sea colour and broad moving light patterns. Narrow broken hull
contact foam; wakes only while travelling. No dense white bars crossing the sea.
Feedback enters briefly and settles; animations must not delay actions.

Harbour departure first slides sideways clear of the quay, then turns onto the
selected fishing ground's bearing. Return reverses the journey, aligns parallel
and slides into berth. Turn about the hull centre; the camera keeps the whole
manoeuvre readable. Water highlights stay restrained enough to show shallow
seabed and underwater kelp/fish; dense white sheen is rejected.

Sound is quiet tactile coastal foley, confirmed by Mo on 2026-10-16. The captain's
cast, splash, bite and reel are audible; crew automation stays quiet. Keep the
sea bed subdued, avoid melodic arcade rewards, and expose a sound control.

## Acceptance

Compare actual native captures to the references at desktop and landscape-phone
sizes. Verify waiting/bite/reel/catch/carry/full/return states, menus, affordability
and save behaviour. Preserve deliberate changes in shared components; fix those
components rather than independently reskinning each feature later. Native Unity
render/input checks replace browser/Lighthouse checks for this project.

## Revised world requirement — POLISH-003

Author the complete camera-visible fishing-location patch as a cohesive miniature
coastal scene: connected shoreline and cliff forms, grass/vegetation, deliberate
working-coast detail and submerged shelf/seabed. Derive dimensions from gameplay
camera coverage, with framing margin. Mo's 10x20 m example expresses bounded
scope, not literal dimensions. Generic scattered pale rocks are rejected.

Use detailed Blender-authored static environment geometry with live Unity water,
boat, shadows and interactions. Water must support animated normals/waves,
shore/hull contact, shallow/deep variation and per-location colour controls.
Evaluate Plunder's adapted Boat Attack package before inventing another minimal
water shader. A beauty render is a composition target; runtime parity must be
checked independently. The UI still requires a faithful rebuild against goal
renders, especially References/day03-small-boat.png; POLISH-002 is not accepted.

### Water direction — Mo, 16 October 2026
Clean stylized blue 3D water with broad rounded wave shapes visible from the
fishing camera. Use the current PTS clean preset as the reference. Reduce fine
surface noise; keep white glints sparse and foam/wash disabled. Codex 1 owns the
water adaptation; Codex 2 owns the new skiff work and its separate design brief.
Keep all verification hidden while Mo is at school. Current water is a working
iteration, not visually accepted.

### Reference update — WATER-006 (supersedes WATER-005 wave scale)
Mo supplied two third-party game screenshots on16 October. Target: clear stylized
water with small overlapping ripple/reflection texture and transparent shallows.
Colour may differ. Large geometric swells are rejected while the boat remains
steady; retain only tiny surface displacement. Zero foam/white wash stays. Keep
this direction over the preceding request for pronounced rolling wave shapes.

Water motion — WATER-007: ripples run at65% of WATER-006 speed. Gentle hull
heave/pitch/roll follows hull-averaged Gerstner heights on the same clock, capped
at.8degrees tilt. Preserve a steady readable deck and route heading/centre; pause
freezes the shared motion. Foam stays disabled.

## Cohesive native interface — HUD-008
Fishing uses one connected cream/navy instrument, portrait crew rail, world
interaction bubbles and a single illustrated fishing-action instrument. Keep
hold count/value, food/bait and contract progress readable without covering the
boat. Catch feedback shares portrait, typography and button materials.

Harbour is a proper shop workspace: smaller harbour/departure view, illustrated
category rail and shop sign, roomy two-column product displays, prices and
explicit disabled/owned/prerequisite states. All five categories inherit the
same layout; retain real inventory, contracts, sale and upgrade rules.

Use the supplied Fredoka and86-texture kit consistently. ScreenSpaceOverlay
keeps UI artwork clear of world tonemapping. Respect safe areas, logical phone
targets, Larger type, visible keyboard selection and existing confirmations.
Native capture evidence/checks and remaining physical input limits are in
`docs/HUD-008.md`; browser/Lighthouse checks do not substitute for Unity evidence.

## Direct reference HUD — UI-024

Mo requests literal reproduction of Downloads/fish.png crew/right and day/time/coin/goal
left, superseding HUD008 lower-left crew placement for the fishing view. Use the
shared FishReferenceStyle/CoastalCanvas reference primitives and measured1672x941
coordinates. Reuse original cream contours/icons/static headings; no independent
fonts or restyling per side. Actual crew/data stays honest; no fake professions,
levels or percentages. Phone readability and final pixel parity remain unaccepted.
See docs/CLI-REFERENCE-HUD-024.md for delivery/native evidence and sampled static pixel comparison; dynamic font identity is unproven, so do not call it pixel-perfect.

## Illustrated coastal map — CHART017, 2026-10-16

Mo's map reference replaces the former paper/vector chart. Use the richly
illustrated full-screen coastal plate at Resources/Charts/gull-coast: crystalline
turquoise shallows, dark-blue channel, kelp, sandbar, rocky headlands and a warm
working harbour. Keep the supplied geography and visual richness. Overlay real
native pins, white dashed routes, cream cards, navy reference lettering and the
Boat/Crew/Map/Gear/Port navigation. Prices, selection, money, hold and contracts
are live state; never bake them into artwork. Landmark coordinates belong to the
illustration; they do not claim compass-exact cartography. Contract/details panels
open on demand so the map remains the main screen. Keep44physical-pixel targets.
Reference and final native views: docs/screens/chart017. Image generation prompt
and integration/verification handoff: docs/CHART017.md.

## Departure manifest and fuel — FUEL021

Set sail opens a focused cream coastal departure sheet using the existing sliced
reference panels, Fredoka, supplied supply icons and exact crew portraits. Destination
and wallet lead; fuel/bait purchases sit beside real inventory, crew/contract duration
and fitted net remain a read-only manifest. Back to port and Let's go are clear final
actions. Desktop and landscape phone inherit the native safe-area logical canvas.
Food indicators are replaced by fuel percentage; oar-powered boats explicitly need
no fuel. No hunger/penalty language or crew/upgrade selling belongs in this sheet.

## Fish cards retained; fishing HUD restored — HUD044

Mo rejected UI041's smaller trip HUD. Keep the original ReferenceGoals, crew,
hold, day/money, voyage supplies and Head home layouts, original global kit
panels/buttons/icons and original text sizing. No Gemini instrument rail or
bottom dock. Retain six new catch cards/glows and authored fish portraits/models;
fit and parent-clip catch receipt lettering only. Future HUD changes require Mo's
new direction rather than resuming the discarded UI041 instruments.

## Clear prep orders and action placement — PREP047

Mo's17October correction replaces weight/value prep settings with two explicit
columns: Chum settings on the left, Fish preparation on the right. Explain the
outcome in ordinary language before the controls. Independent class dropdowns
list Common, Big common, Rare, Big rare, Legendary, Big legendary in white,
green, blue, purple, gold, red; allow explicit inclusion/exclusion of each.
Worker duties stay in Crew duties. Prep table/chum belongs in the right action
stack below Head home/Crew duties, leaving the bottom-left catch list clear.
Retain the existing component art and HUD dimensions. Net activity captions
must identify the rig actually being unloaded; Nets workers keep stable rigs.

## Live production overview — MANAGEMENT078

Mo requests a player-facing working fish-flow screen. Extend the coastal Canvas
with cream stage panels, real fish/net/cooler icons, navy numeric hierarchy and
Fredoka. Three numbered stages distinguish landing, carrying/stowing and optional
preparation; the shared hold stays explicit. A Fishing tab compares rods/nets/crab
traps. Traffic bars use labeled green spare/orange near-limit/red bottleneck states;
unknown capacity is neutral, never a fabricated success state. Teal comparative
method bars are clearly distinguished from load bars. Rates use actual game events;
capacity and catch-value estimates say so. The game continues behind the blocking
modal. Keep the existing fishing HUD, art, crew rail and gameplay intact.


## DASH082 — Mo's exact management references (supersedes MANAGEMENT078 layout)

DASH1/DASH2 are the pinned Income/Operations tabs. Use original unchanged artwork
from Resources/ManagementReference with native live values and interactive fields;
do not substitute the earlier cream-card management design. Preserve 1672x941
composition/proportions when fitting the safe area, with original coastal art in
surplus space. Right-side Management entry; visible back arrow and Escape close.
Method/stage detail panels expose probability mixes, queues and real duty/order
controls. Income is expected nominal catch value from probabilities and current
gear/bait, without freshness/market depletion; Operations measures the actual
inbound → processing → outbound → main-hold pipeline. Small hulls bypass processing.
Green/orange/red traffic states include text; unavailable/learning states remain
neutral. See docs/DASH082.md for definitions and native evidence.


## DASH087 — boat-specific values and bottom-right entry

Retain Mo's accepted DASH1/DASH2 artwork and tab composition. Management now
anchors bottom-right, with Boat / duties immediately to its left in the same
cluster. Home, Crew and Prep actions have nonoverlapping footer slots; fishing
hints leave those controls clear. The header identifies the actual saved boat.
Absent gear shows explicit No nets fitted / No traps fitted, zero income and
zero share. Fitted but unoperated gear explains the missing worker. Nominal
raw catch value excludes an assumed processing premium; integer shares sum100
only when positive income exists. Details distinguish per100catch/perhaul
potential from staffed income perminute. Existing actual processing/bypass
routes and text-labeled bottleneck colors remain. See docs/DASH087.md.


## CREW096 — crew effects and honest Management numbers

Preserve the accepted DASH1/DASH2 art, interactive details and bottom-right actions.
Future card effects change the actual work rules and the matching predictions;
never attach a bonus only to a displayed value. Distinguish expected raw catch
worth, real completed throughput, estimated capacity, busy workers and actual
queues. Batches retain original fish/count/mass; partial or changing abilities
need correct cache invalidation and hauling relearning. Do not retroactively
rewrite the voyage chart. Gameplay integration and acceptance are mapped in
[docs/CREW-MANAGEMENT-INTEGRATION.md](docs/CREW-MANAGEMENT-INTEGRATION.md); crew
choices remain in their canonical design record. No new card UI is specified here.


## DEEP104 — Crew setup and working Tier 5 gear

Keep the accepted Income/Operations references and add Crew as the third tab.
Use the same dashboard lettering, navy, cream and teal, with one clear list of
crew and a selected worker's settings. Fisher tasks are independent square
checkboxes; bait permissions sit below. Large native hit targets, selection
states and Escape remain functional at desktop and landscape sizes. New body
panels fully cover the former sample content, without exposing background labels.

Income has four live methods including deep lines, with a matching fourth chart
legend and real local catch-class details. Table orders retain the existing
side-by-side chum/preparation interface and original working processing station;
Tier 5 explains its50%preparation premium. Chum labels state white1/green2/blue3,
with purple/gold/red disabled. Explain that deep lines require self-made chum.
Preserve the fishing HUD, boat footprint, six hired crew plus captain, both gear
layouts and the supplied103mesh language; the optional third rig reuses it.
