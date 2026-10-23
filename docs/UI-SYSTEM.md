# Catchline UI system

Status: the single UI language for every screen, panel, button and label in the
game, agreed with Mo on 2026-10-23. The four concept images under
`docs/screens/ui-concept/` (voyage HUD, operations, crew, chandlery) are the
visual reference. Anything not covered here follows those images; anything that
contradicts them is wrong. This replaces the three current skins (UI kit,
FishReference raster panels, ManagementReference raster regions).

Reference games: Clash Royale and Bloons TD 6. The rule they share: every panel
is a physical object — a slab with an outline, a bevel and a shadow — with one
big number and an icon, and exactly one fat primary button per screen.

## 1. Tokens

### Colours

| Token | Hex | Use |
|---|---|---|
| `Plank` | `#1E4D7B` | page background: painted navy planks (tiled texture, never flat) |
| `PlankDark` | `#163A5E` | plank grooves, modal dim base |
| `Rope` | `#C9A46A` | rope border on full pages |
| `Brass` | `#D9A441` | nail heads, coin |
| `Cream` | `#F4EFE3` | slab surface |
| `CreamDeep` | `#E8E0CC` | slab inset / recessed areas |
| `Ink` | `#173F57` | all text on cream, outlines |
| `InkSoft` | `#52747C` | secondary text |
| `HeaderNavy` | `#1F4E79` | header bands on slabs |
| `Orange` | `#E36A35` | primary button top |
| `OrangeDeep` | `#B84D22` | primary button bottom edge |
| `Teal` | `#168F9F` | secondary accent, water in icons |
| `Good` | `#3E9A5B` | steady, progress fill |
| `Warn` | `#E6AD38` | busy, bite, attention |
| `Bad` | `#C8443A` | backed up, danger |
| `White` | `#FFFFFF` | fish-class white, text on navy |
| `Green` | `#4CAF50` | fish-class green |
| `Blue` | `#3B82F6` | fish-class blue |
| `Purple` | `#8E44AD` | fish-class purple |
| `Gold` | `#E6B422` | fish-class gold |
| `Red` | `#D7263D` | fish-class red |

Colour means something. Green/amber/red are only ever status. Fish-class colours
appear only on fish, bait and class toggles. Orange is only the primary action.

### Geometry

Logical canvas stays the existing 1280×720 (480 tall on phones, via `CoastalCanvas.Begin`).

| Token | Value |
|---|---|
| Grid | 8 px |
| Slab radius | 18 |
| Card radius | 14 |
| Button radius | 999 (pill) for primary and tabs; 14 for cards |
| Outline | 3 px `Ink` on every slab, card, button and portrait frame |
| Bevel | 2 px lighter top-left highlight inside the outline, 2 px darker bottom-right |
| Shadow | offset (0, 4), blur 0, `PlankDark` at 35% |
| Header band | 44 px tall, `HeaderNavy`, text `Cream`, radius follows slab top |
| Padding | 16 inside slabs, 12 inside cards, 10 inside buttons |
| Min touch target | 44 physical px, always; hit area may exceed artwork |

### Type

| Style | Font | Size (720 canvas) | Use |
|---|---|---|---|
| Display | Lilita One (OFL) | 36 | screen titles |
| Number | Lilita One | 32 | the one big number per card |
| Heading | Lilita One | 22 | header bands, card titles |
| Body | Fredoka Medium | 18 | everything else |
| Small | Fredoka Medium | 15 | labels under numbers, hints |
| Caption | Fredoka Medium | 13 | "Tap to cycle", footnotes |

Display and Number over artwork get a 2 px `Ink` outline. Body never does.
Sentence case everywhere except header bands, which are UPPERCASE. No
padding strings with spaces. No text smaller than 13. Text never overflows its
slab: fit or truncate with the existing `fitted` label.

## 2. Components

Each component lists anatomy, states and the rule that makes it this game.

### Slab
The panel. `Cream` fill, 3 px `Ink` outline, bevel, shadow, radius 18. Optional
header band. Optional four brass nails in the corners on full-page slabs only.
Everything on screen lives in a slab or a card; nothing floats on the world
except speech bubbles and toasts.

### Card
A slab's child: `White` fill, radius 14, outline 3 px, inset shadow when
recessed. Used for items, crew rows, stage cards. Selected state: 4 px `Blue`
outer glow and a tick badge top-right. Locked state: content at 60% and a lock
chip with the reason ("Needs fibreglass rods").

### Primary button
Orange 3D pill: `Orange` top, `OrangeDeep` 6 px bottom edge, 3 px `Ink` outline,
`Cream` heading text with 2 px `Ink` outline, icon left of label. Pressed: moves
down 4 px and loses its bottom edge, 80 ms. Disabled: `CreamDeep` with `InkSoft`
text, no bottom edge. **One per screen.** Height 64 on desktop, 56 on phone.

### Secondary button
Same shape in `Cream` with `Ink` text and a `CreamDeep` bottom edge. Used for
Back, cancel, cycle, alternatives.

### Icon button
Round, 56 px, `Cream` with outline and bevel; icon 28 px; label in Small below
when it is a navigation target (Crew, Ops). Used bottom-right on the voyage HUD.

### Tab bar
Full-width row of equal cards at the bottom of harbour pages: icon 40 px above
a Heading label. Active tab is `HeaderNavy` with `Cream` text and sits 4 px
higher. Five tabs max; thumb reach is the reason it is at the bottom.

### Page switch
Two or three pills in one capsule at the top-right of a page (Operations | Crew).
Active pill `HeaderNavy`.

### Crew rail
Right edge of the voyage HUD and of management pages. Header band "CREW n/n"
with a menu icon. One Crew card per person: portrait bust 56 px in a framed
circle, role + name, one-line status ("Sorting", "Needs bait"), speciality icon,
a progress bar only when the person has a timed job. Max 8 rows; scroll beyond.

### Stage card (Operations)
Header band with the stage name, a 96 px illustrated icon, the one Number with
a Small unit, a Traffic light pill, the queue as fish icons (up to 8, then
"+n"), and a "Details ›" secondary. Backed-up cards get a 4 px `Bad` outer glow.

### Traffic light
Pill with a 14 px dot and one word: Steady (`Good`), Busy (`Warn`), Backed up
(`Bad`). Never a percentage.

### Progress bar
Recessed `CreamDeep` track with inner shadow, 14 px tall, fill in `Good` by
default, `Warn` for timers, `Bad` for danger. Fill is clipped, caps never squash.
Always paired with a value or icon.

### Stat tile
Icon 40 px left, Small label above a Number value, optional bar beneath. Used in
the voyage left cluster (Hold, Fuel, Chum, Goal).

### Speech bubble
Cream rounded body, outline, tail; icon 24 px then Body text. Hot variant
(`Warn` fill) for Bite!. Attached to the world object, clamped to the safe area.

### Toast
`HeaderNavy` pill, `Cream` text, icon left, 64 tall, top-centre, 200 ms in, 3 s
hold. Never stacks; newest replaces.

### Modal
Dim the page with `PlankDark` at 60%; centre slab with header band, body, one
primary and one secondary button. Escape and tapping the dim close it when the
action is reversible.

### Class chip
Pill with a fish icon tinted in its class colour and the class name; toggle
state shows a tick. Used for keep rules and table order inputs.

### Order stepper
Product icon, name, and a four-way segmented control **1 · 5 · 10 · ∞**; active
segment `HeaderNavy`. A trash icon removes the order.

### Duty slot
Card with a header "PRIMARY" / "SECONDARY", a 40 px duty icon, the duty name,
and a cycle icon. Tap anywhere on the card to cycle (Haul → Sort → Table).

### Price pill
`Cream` pill with the coin icon and a Number; `Bad` text when unaffordable.

### Portrait
Illustrated bust, 1:1, cream frame with outline. One per crew card; the same
art is used at 56, 96 and 240 px.

## 3. Screens

Every screen is its own full page on planks with a rope border, except the
voyage HUD, which sits over the world.

| Screen | Layout |
|---|---|
| Voyage HUD | top-left: day/time + coins slab. left: ground slab with Hold, Fuel, Chum/Bait, Goal stat tiles. right: crew rail. bottom-right: primary **Head home**, icon buttons Crew and Ops. bubbles on the world. strike panel bottom-centre. |
| Operations | header slab with back, title, ground/day, page switch. four stage cards in a row. warning slab with one recommendation and primary **Assign crew**. hold bar slab. crew rail. |
| Crew | header as above. left: large portrait slab with name, role, speciality. right: Primary/Secondary duty slots (deckhands) or gear family + allowed-bait class chips (fishers). footer slab with hint and primary **Save duties**. crew rail. |
| Harbour hub | world visible, left slab with harbour name and voyage; bottom tab bar Market · Chart · Crew · Gear · Supplies; primary **Set sail** bottom-left. |
| Shop page | header slab with back, shop name, coin pill. grid of item cards (illustration, name, one-line effect, price pill, lock chip). selection slab at the bottom with the chosen item and primary **Buy · price**. tab bar. |
| Chart | illustrated plate full-bleed inside the rope border; pins; a ground card on selection; primary **Choose**. Day/night toggle on the card. |
| Departure | slab with destination, crew portraits, "This trip costs n", bait/fuel steppers, primary **Let's go**, secondary **Back**. |
| Catch card | existing class templates, text fitted inside, never covers the action buttons. |
| Sale result | slab with the haul as class rows, coins Number, contract progress, primary **Collect**. |
| Pause / settings | modal. |
| Title | illustrated harbour, logo, one primary **Play**, secondaries Settings and Credits. |

Phone (480 logical height): same components, crew rail collapses to portraits
only, stage cards drop the illustration to 64 px, tab labels stay.

## 4. Content rules

- One Number per card. Labels in Small beneath it.
- Status is a word, never a percentage.
- No per-minute costs, no charts, no efficiency rings, no "measuring".
- Icon on every button and every stat.
- Copy is short, present tense: "Processing is backing up." then one action.
- Locked things say why in five words.
- Never show two primary buttons.

## 5. Motion

Press: scale 0.96 and 4 px drop, 80 ms. Page in: slide 24 px up and fade,
150 ms. Toast: 200 ms. Traffic light change: dot pulses once. Nothing bounces.
Animations never delay an action.

## 6. Asset manifest

Authored at 2x like the existing kit, sliced where noted. Slabs and buttons go
through `Art/Source/build_ui_kit.py` (SVG → PNG). Illustrations and portraits are
image-generated to the concept style, then cut out.

| Sprite | Size (logical) | Slice | Notes |
|---|---|---|---|
| `plank-tile` | 256×256 | tile | navy planks, subtle grain |
| `rope-h`, `rope-v` | 256×24 / 24×256 | tile | page border |
| `nail` | 16×16 | — | brass |
| `slab` | 128×128 | 40 | cream, outline, bevel, shadow baked |
| `slab-header` | 128×44 | 40 | navy band, top radius |
| `card`, `card-selected`, `card-locked` | 96×96 | 32 | |
| `btn-primary`, `btn-primary-pressed` | 128×64 | 44/40 | orange 3D |
| `btn-secondary`, `btn-secondary-pressed` | 128×64 | 44/40 | cream 3D |
| `btn-disabled` | 128×64 | 44/40 | |
| `btn-round` | 56×56 | — | |
| `tab-on`, `tab-off` | 128×96 | 40 | |
| `pill-switch-on`, `pill-switch-off` | 96×44 | 22 | |
| `bar-track`, `bar-good`, `bar-warn`, `bar-bad` | 64×14 | 7 | |
| `light-good`, `light-warn`, `light-bad` | 14×14 | — | |
| `bubble`, `bubble-hot`, `bubble-tail` | existing sizes | existing | restyle to outline + bevel |
| `toast` | 128×64 | 32 | navy |
| `chip-class-{white,green,blue,purple,gold,red}` | 96×36 | 18 | |
| `portrait-frame` | 64×64 | — | |
| `icon-*` | 40×40 | — | coin, fish, hold, fuel, chum, bait-scraps, worms, squid, rod, net, cage, line, jig, sort, table, haul, crew, ops, home, map, gear, supplies, market, lock, tick, cycle, trash, sun, moon, wheel, radio, warning, clock, anchor |
| `illus-stage-{fishing,hauling,sorting,table,hold}` | 96×96 | — | concept style |
| `illus-item-*` | 160×120 | — | one per shop item |
| `portrait-{crew name}` | 240×240 | — | bust, concept style |
| `fish-queue` | 24×24 | — | queue icon |

## 7. Implementation plan

1. Add `Assets/Scripts/Game/Skin.cs`: static tokens (colours, sizes, type styles)
   and the component builders listed in §2, each a method on `CoastalCanvas`
   (`Slab`, `Header`, `Card`, `Primary`, `Secondary`, `IconButton`, `TabBar`,
   `PageSwitch`, `CrewCard`, `StageCard`, `Light`, `ProgressBar`, `StatTile`,
   `Bubble`, `Toast`, `Modal`, `ClassChip`, `OrderStepper`, `DutySlot`,
   `PricePill`, `Portrait`). Builders take logical rects like the existing API.
2. Load the new kit through `ArtLibrary.UiTex` alongside the old names; add the
   display font to `ArtLibrary`.
3. Migrate screens in this order, each with 1440×900 and 844×390 captures:
   voyage HUD → operations → crew → harbour hub + shop pages → chart → departure
   → sale result → title/pause → catch card.
4. Delete `Reference*` and `Dashboard*` paths from `CoastalCanvas`, the
   `FishReference` and `ManagementReference` resources, and `Ui.cs` IMGUI styles
   once no screen uses them.
5. Acceptance per screen: matches the concept at both sizes, every touch target
   ≥ 44 physical px, no text outside a slab, one primary button, status words
   only, no charts.
