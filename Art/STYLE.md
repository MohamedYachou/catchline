# Catchline — art style and modelling contract

Status: concept and first-prop handoff for `art/style-pass`. The PNG sheets are modelling references. Actual Blender meshes and FBX exports now accompany them: the [six Crab Coast props](Models/Props/REPORT.md) and [26 Gull Harbour assets](Models/GullHarbour/REPORT.md). Unity was not opened for either pass. The gameplay prototype and its scenes/scripts are outside this branch's changes.

## Visual authority

Mo's [Day 3 small-boat](Concepts/References/day03-small-boat.png) and [Day 28 tuna-boat](Concepts/References/day28-tuna-boat.png) mockups are the visual targets. Preserve their inviting miniature working-boat character: navy hulls, warm timber, ivory rails, orange safety equipment, small busy sailors, sea teal and soft sunlight. Aim for their shape language and material warmth as closely as possible. The PNGs in `Concepts/` adapt that look into isolated orthographic references for modelling; they are not screenshots of a finished Unity build.

Use chunky silhouettes, broad bevels, a few deliberate planar facets and clean colour blocks. Low-poly does not mean every surface is triangulated visibly. Round heads, gloves and boots can use smooth normals; hull corners, tools and machinery retain selected flat planes. Keep most detail in silhouettes and large parts rather than texture noise, tiny rivets, scratches or complicated piping.

**Outline decision: no global outlines.** Separate shapes using value, colour, bevel highlights and restrained contact shading. Do not add black inverted-hull or screen-space outlines to every object. A selection ring or local interaction highlight is a separate gameplay affordance.

## Palette

These are proposed canonical **sRGB base colours**, chosen to match the mockups' visual families. They are not pixel samples from lit renders. Exact values here override generated colour-chip text and image sampling. Lighting will change their apparent colour.

| Use | Hex | Notes |
| --- | --- | --- |
| Deck wood | `#C58B50` | Warm honey timber; broad planks, sparse seams |
| Wood highlight | `#DFB77A` | Restrained lighter plank variation |
| Wood recess | `#8C5A36` | Seams and sheltered underside only |
| Hull navy | `#173F57` | Hull, frames, captain garments |
| Hull lit blue | `#2A6685` | Optional secondary painted panel |
| Rail white / ivory | `#F3F0DC` | Rails, cabin, crate rims; avoid pure white |
| Safety orange-red | `#E36A35` | Equipment, beanie, buoy, lifering, trim |
| Sea teal | `#168F9F` | Sea, sorter bib and trays |
| Shallow-water highlight | `#64C7C4` | Broad moving accents, not glitter |
| Yellow oilskins | `#E6AD38` | Deckhand and engineer helmet |
| Steel | `#8FA6AC` | Sorting surface, simple metal details |
| Rubber / deepest shadow | `#28343B` | Boots, roller, rope recesses |
| Rope | `#D1AF76` | Warm rope; `M_Rope` |
| Band ivory | `#F3DEA1` | Pale yellow crab safety bands; `M_BandIvory` |
| Kelp green | `#477A56` | Kelp and pollock back; `M_KelpGreen` |
| Fish silver | `#BAC9C6` | Fish flank; `M_FishSilver` |
| Skin base | `#B9784B` | Initial shared reference; later variants reuse body |
| Sheet / UI cream | `#F4EFE3` | Reference background and future panel family |

Reserve orange for useful accents rather than painting every station orange. Role readability also comes from hat silhouette. Status indicators need icons/shape as well as colour; hat colours alone do not communicate station state.

## Materials and light

- Timber: matte, wide planks, subtle broad value variation, little grain. Planks follow the boat's fore-aft axis. Do not model every seam as a gap.
- Painted hull and equipment: clean opaque painted surfaces with small bevels. The navy hull should still read blue in shadow. Keep metallic response low on paint.
- Steel worktops: muted satin rather than mirrored chrome. Rubber is dark matte. Glass uses dark blue opaque/low-complexity glazing for early models; avoid needing cabin interiors.
- Nets and pot mesh: sparse coarse openings, thick readable outer frames. Treat tiny knots as texture or omit them; do not create thousands of strands for a concept-matching first asset.
- Water: teal base with restrained broad highlights, gentle motion and a narrow foam/contact treatment around the hull. Avoid physically simulated waves or dense reflections as prerequisites for this style.

Lighting target: soft warm sunlight from the upper-left of the gameplay frame, cooler ambient fill, short soft shadows, lightly darkened contacts. Maintain readable equipment in shadow. Avoid crushed blacks, strong bloom, depth of field, film grain, sharp specular glitter and excessive ambient occlusion. Begin with restrained neutral colour grading; saturated palette colours do the work.

**Moving-boat caveat:** a boat that changes layout or moves through world space must not rely on a world-fixed scene lightmap for its changing shadows. Achieve the baked-light *look* with controlled materials, optional asset-local baked AO/vertex shading, ambient fill and a small real-time lighting setup. Evaluate actual scene baking only for genuinely fixed geometry. Moving crew need a compatible dynamic lighting path. Do not stack strong baked AO with strong screen-space AO.

URP implementation is a later integration step, not part of these concepts. [Unity 6.3 URP Baked Lit reference](https://docs.unity3d.com/6000.3/Documentation/Manual/urp/baked-lit-shader.html) and [Unity light probes](https://docs.unity3d.com/6000.3/Documentation/Manual/LightProbes.html) describe available lighting mechanisms; the aesthetic recommendations above are this project's art direction, not a claim that lightmaps can follow arbitrary changing layouts.

## Camera and reference conventions

- Game: landscape, fixed orthographic 3/4 camera. Starting art-review angle: about 45 degrees down from horizontal, yaw about 35 degrees off the stern axis; tune later for readable jobs and clear walkways.
- Model sheets: true orthographic front/right/back/top, plus an orthographic 3/4 where helpful. A 3/4 view is still parallel-projected, never a perspective hero shot.
- Rendered hull top plans and starboard side elevations: bow to the right, stern to the left. In those top plans port is up and starboard down. The exact grid supplement deliberately uses bow-up for coordinate readability and labels its orientation. Hull plan and elevation must agree about cabin, motor and rails.
- Station front: the operator-facing edge. For the hauler, the plan labels its sea edge on the right and worker edge below; mount that sea edge against the rail. Rotation on deck is allowed; dimensions rotate with it.
- Neutral background and soft contact shadow are presentation only; do not bake either into albedo.

Generated multiview sheets can contain small view-to-view differences or misleading ruler/grid marks. **Written dimensions, the exact grid supplement and a single coherent model take precedence.** Treat views as shape/colour references and reconcile them in Blender; they are not CAD or guaranteed multiview reconstruction inputs. For image-to-3D, isolate one subject/view rather than feeding an entire labelled sheet as a single object. Inspect resulting topology, scale and hidden surfaces manually.

## World scale and axes

- One deck tile = **1 m × 1 m**. Model in metres, apply transforms before export, use positive unit scale.
- Unity convention: `+Y` up, `+Z` toward bow, `+X` toward starboard. Blender modelling is Z-up; verify export conversion so the imported Unity result follows this convention.
- Hull pivot: centre of its rectangular build deck at deck height, `(0, 0, 0)` in local Unity coordinates. Deck walking plane is `Y = 0`; hull extends below it.
- Station pivot: footprint centre at deck contact, `Y = 0`. Front working edge faces local `-Z`. Define working/interaction points separately from visual meshes.
- Crew root: floor between boots, facing local `+Z`. Hand attachment points are on the shared rig. Crate pivot: centre of underside. Crab pivot: ground centre. Buoy pivot: centre of base. Pot pivot: centre of underside. Prop roots use their horizontal bounding-box centre with minimum height at zero; variant parts share the same root origin.
- Footprint borders, dimension arrows, labels and scale figures are guides, never mesh geometry.

## Crew: one shared body

Body height is **0.95 m sole to bare scalp**. Hats add approximately 0.06–0.10 m above the scalp (module origins overlap the head); do not stretch different roles to fit their hats. Proposed shoulder width 0.34 m, head width about 0.30 m, head height about 0.33 m. Short thick legs, rounded mitten gloves with a thumb, chunky rubber boots, a small nose and very simple eyes. Keep fingers, ears and facial features economical. Initial proportions are art targets, not anatomy measurements.

All five jobs share body geometry, proportions, skeleton, hand positions and animation set. Hats are removable modules; role clothing primarily uses recoloured material regions on the shared garment silhouette. Initial sheets use the same skin/hair to make this relationship obvious. Later skin/hair variants do not require a new body or job rig.

| Role | Hat silhouette | Main clothing | Readable cue |
| --- | --- | --- | --- |
| Captain | White peaked cap, navy band | Navy with ivory trim | Wide white cap |
| Deckhand | Orange rolled beanie | Yellow oilskin bib, navy sleeves | Orange + yellow |
| Sorter | Navy baseball cap | Teal bib, navy sleeves | Forward cap peak + teal |
| Bander | Short-brim orange-red cap | Orange-red bib, navy sleeves, ivory gloves | Red-orange workwear |
| Engineer | Yellow hard hat | Muted steel-grey bib, navy sleeves | Helmet dome + brim |

The six reference actions are **walk, carry crate, work at table, idle, cheer and panic**. Use one animation library for all roles. For carry, two hands support a 0.45 × 0.32 × 0.25 m crate near waist height; use an attachment constraint/pose rather than letting the crate intersect the belly. For table work, the 0.55 m worktop is deliberately low enough for a 0.95 m sailor. Cheer and panic must remain distinct at gameplay zoom. Pose sheet drawings are key-pose intent, not animation timing or a final rig.

## Hulls

Hull 1's 3 × 2 tile deck and hull 2's 5 × 3 tile deck are confirmed by Mo. Their outer hull dimensions remain proposed art envelopes; hull 3's deck and centred wheelhouse footprints are authoritative. Keep hull topology, rail thickness, timber treatment and navy/ivory/orange material family consistent across tiers.

| Hull | Overall hull length × beam | Rectangular build deck, fore-aft × across | Fixed content |
| --- | --- | --- | --- |
| 1 — Rowboat | 4.2 × 2.4 m | 3 × 2 tiles | Removable rowing bench, separate oars; no motor/cabin |
| 2 — Outboard skiff | 6.5 × 3.5 m, excluding motor | 5 × 3 tiles | One-tile forward console, outboard outside stern |
| 3 — Day boat | 12.0 × 5.8 m | **10 × 5 tiles** | **3 across × 2 fore-aft tile wheelhouse, centred at bow**, low white rails |

Day boat: deck rectangle includes the wheelhouse. It has 50 tiles total, of which 6 are cabin, leaving 44 before equipment and aisle allocations. Do not interpret the requirement as a 10 × 5 aft work area plus another cabin area. The tapered bow and hull margins are outside the build rectangle.

Exact day-boat deck in local Unity coordinates: `X = [-2.5, +2.5]`, `Z = [-5, +5]`, `Y = 0`. Tile columns `c = 0..4` run port to starboard; rows `r = 0..9` run stern to bow. Tile centre is `(c - 2.0, 0, r - 4.5)`. The wheelhouse is **centred**, occupying **columns 1, 2 and 3, rows 8 and 9**: **3 m across × 2 m fore-aft**, `X = [-1.5, +1.5]`, `Z = [+3, +5]`. One clear tile column remains on each side. Its centre is `(0, 0, 4)` on the deck plane.

Proposed day-boat outer hull extends to `X = ±2.9`, `Z = [-5.5, +6.5]`. Keep the full build rectangle inside the hull; start the bow taper ahead of `Z = +5`. Wheelhouse body height: 1.65 m above deck, with roof, fittings and small mast above. Rail height: about 0.60 m. These chibi-scale proportions prioritise a visible deck and matching the references over real vessel certification.

Keep cabins, rail sections, motor, oars, hatch covers and fittings modular. Empty hull references intentionally omit stations so equipment arrangement stays a gameplay choice. Avoid decorative props blocking walkways or hiding job animations.

## Location order

**Location 1 is Gull Harbour**, beginning with manual rod fishing on the 3 × 2 m rowboat deck, then progressing towards nets. Harbour Mouth supplies herring/mackerel, Kelpbank pollock/sea bass, and Rocky Point the rare conger eel. Cooler storage, bait and voyage provisions support the active gameplay loop. **Crab Coast is location 2.** The older crab sheets remain valid asset references, but do not describe the starting location. This follows the live `proto/deck-sim` checkout’s `docs/GAMEPLAY.md`, read before this modelling pass; that working document was not yet committed when read.

## Gull Harbour tier 1 — built asset contract

Sources, exports, measured bounds and topology checks are in [the Gull Harbour report](Models/GullHarbour/REPORT.md). Source Blender axes are X right, -Y forward, Z up; exported Unity axes are X right, +Z forward, +Y up. Part origins listed below are **Unity local metres**, relative to the asset root. Rotations are zero and scales one; offset part translations deliberately locate animation pivots. Moving parts are siblings under one empty root. No rig or animation clips are included.

| Asset | Size / root | Moving parts and placement |
| --- | --- | --- |
| Rowboat | Hull 4.2 m fore-aft × 2.4 m beam; deck 3 × 2 m, deck-centre root at Y=0 | Plank deck, centre thwart, separate oars. Oar pivots at (-1.12,.49,0) and (1.12,.49,0). Port sockets (-1.115,.44,-1) and (-1.115,.44,+1): 0.5 m and 2.5 m from **rectangular deck stern** Z=-1.5. Bow taper lies outside the build rectangle. |
| Fishing rod | Butt root; 1.6 m upright from butt to tip | Separate reel handle, pivot (.107,.24,0). Rotate/attach whole rod for casting. |
| Bobber | 0.12 m total height, 0.08 m diameter; waterline root | Lower 0.045 m submerged, upper 0.075 m above water; orange-red/ivory bands. |
| Cooler / ice box | 0.80 × 0.50 × 0.45 m W × D × H; underside root | Identical body mesh; lid origin (0,.40,-.25), rear hinge, rotate local X. Ice variant has teal lid and solid ivory frost motifs. |
| Bait bucket | 0.30 m diameter; approximately 0.367 m including bail | Underside root; open interior. Art-selected size. |
| Lunch tin | 0.25 × 0.18 × 0.12 m body; latch adds 0.004 m depth | Underside root; separate lid. Art-selected size. |
| Herring / mackerel / pollock / sea bass / conger | Exact nose-to-tail lengths 0.26 / 0.34 / 0.48 / 0.50 / 0.80 m | Face +Z, grounded root; separate tail at body-tail join. Mackerel stripes are geometry, no textures. |
| Shared crew | 0.95 m sole-to-scalp; T-pose, ground root between boots | One connected closed all-quad body with separate face/garment details. No armature. Hat anchor (0,.91,0); cap, beanie and hood roots at their mounting seats. |
| Quay | 4 m long × 2 m deep; walking surface/root Y=0 | Piles extend below walking plane; end-to-end repeat along X. |
| Harbour dressing | Bollard, 2.8 m lamp, two houses, 6 m lighthouse, three rocks | Grounded roots. House walls 3×2.6 m and 3.4×2.8 m; roof overhangs included in reported bounds. Art-selected dimensions. |
| Kelp | Exactly flat at Y=0, floating root | Drift-aligned overlapping leaf silhouettes and four inset bulb disks; a planar union prevents overlapping faces. Use a two-sided material for underwater views. |

Palette material names extend the prop batch with `M_DeckWood`, `M_WoodHighlight`, `M_WoodRecess`, `M_HullBlue`, `M_OilskinYellow`, `M_Skin`, `M_KelpGreen` and `M_FishSilver`. All use the canonical sRGB colours above. No bitmap textures or Unity `.mat` assets are included. Preview lights/background are source-only and excluded from FBX.

## Crab Coast stations

Footprint is reserved occupancy, not a demand that every mesh touches its tile border. Listed visual envelopes leave inset margins. Work positions and routes live in adjacent walkable tiles and are not included in the station occupancy. Do not place another machine over those access positions.

| Station | Footprint | Visual envelope W × D × H | Design and operation |
| --- | --- | --- | --- |
| Pot hauler | **1 × 1** | 0.85 × 0.85 × 1.25 m | Navy pedestal, compact orange davit, rubber roller; back at rail, worker inboard |
| Sorting table | **2 × 1** | 1.80 × 0.80 × 0.55 m | Satin steel top, two teal trays, navy legs; front edge along long side |
| Banding bench | **1 × 1** | 0.80 × 0.80 × 0.55 m worktop; tool to 0.85 m | Wood top, ivory restraint pad, orange applicator, teal band spool |
| Live tank | **2 × 1** | 1.80 × 0.80 × 0.65 m | Navy tub, ivory rim, teal water, two compartments; aerator inside envelope |
| Pot rack | **2 × 1** | 1.80 × 0.80 × 1.10 m | Navy open frame, timber shelves; four pot slots, two wide × two high |

Pot hauler's rigid structure stays inside its tile. Rope and a suspended moving pot may travel outboard into water during the hauling animation; neither reserves an extra deck equipment tile. Avoid an oversized crane boom that visually sweeps through neighbouring stations. Station plan drawings must not imply additional pipework, handles or stored pots projecting into an aisle.

One-metre clear aisles are the layout target. Keep operator-facing edges accessible; two-tile machines can rotate by 90 degrees. Animated parts get separate meshes/pivots: hauler roller, banding applicator, tank surface, pot rack contents. Do not join crabs, water, rope and machine into one uneditable object.

## Crab Coast props

| Prop | Proposed envelope | Shared parts / treatment |
| --- | --- | --- |
| Empty pot | 0.70 × 0.55 × 0.35 m | Chunky 0.036 m navy rails/posts, coarse mesh, four closed rope lashings, broad teal hatch latch |
| Full pot | Same as empty | Same pot mesh, toggle a small crab load inside |
| Crab | 0.28 m width across legs, 0.18 m body length | Orange-red, two broad claws, four short walking legs per side |
| Banded crab | Same as crab | Same crab mesh plus ivory-yellow band on each closed pincer |
| Crate | 0.45 × 0.32 × 0.25 m | Navy slotted box, ivory chunky rim, integrated handles |
| Buoy | 0.25 m diameter × 0.38 m height | Orange-red, broad ivory stripe, small rope eye |

The full pot is a state of the empty pot, and banded crab a state of the crab. Match their silhouettes and transforms. The prop sheet is the canonical prop design: reuse that pot and crab mesh in station content slots rather than modelling each small station thumbnail as a different species or trap. Keep the crate small enough to carry with the shared rig; do not use a 1 m cube for a 0.95 m worker. Optional pots/crabs in station views are content examples, not permanently fused station geometry.

## Concept index and reproducibility

| PNG | Contents |
| --- | --- |
| [01-style-sheet.png](Concepts/01-style-sheet.png) | Palette families, material samples, lighting and outline decision |
| [02-crew-turnaround.png](Concepts/02-crew-turnaround.png) | Shared deckhand body: front, right side, back, orthographic 3/4 |
| [03-crew-roles.png](Concepts/03-crew-roles.png) | Five shared-body role treatments and hat cues |
| [04-crew-poses.png](Concepts/04-crew-poses.png) | Walk, carry, work, idle, cheer, panic |
| [05-hull-01-rowboat.png](Concepts/05-hull-01-rowboat.png) | Rowboat plan, side and 3/4 |
| [06-hull-02-skiff.png](Concepts/06-hull-02-skiff.png) | Skiff plan, side and 3/4 |
| [07-hull-03-day-boat.png](Concepts/07-hull-03-day-boat.png) | Day boat plan, side and 3/4 |
| [08-station-pot-hauler.png](Concepts/08-station-pot-hauler.png) | Rail hauler, 1 × 1 |
| [09-station-sorting-table.png](Concepts/09-station-sorting-table.png) | Sorting table, 2 × 1 |
| [10-station-banding-bench.png](Concepts/10-station-banding-bench.png) | Banding bench, 1 × 1 |
| [11-station-live-tank.png](Concepts/11-station-live-tank.png) | Live tank, 2 × 1 |
| [12-station-pot-rack.png](Concepts/12-station-pot-rack.png) | Pot rack, 2 × 1 |
| [13-crab-coast-props.png](Concepts/13-crab-coast-props.png) | Six props with state variants |
| [15-gull-harbour-tier1.png](Concepts/15-gull-harbour-tier1.png) | Starting harbour, rowboat, fishing gear, shared crew, fish and deck props |
| [14-day-boat-deck-grid.png](Concepts/14-day-boat-deck-grid.png) | Exact 10 × 5 deck / 3 across × 2 fore-aft cabin dimensional supplement |

Sheet 15 uses built-in `image_gen` with the existing art references; its [prompt](Source/gull-harbour-concept-prompt.txt) is preserved. Its drawn rod-socket ruler is schematic: the written coordinates above control placement. Sheets 01–13 use the built-in `image_gen` tool with the two approved mockups as style references. Their full prompt set is [Concepts/PROMPTS.json](Concepts/PROMPTS.json). Sheet 14 is a deterministic dimension diagram, supplementing rather than replacing the rendered hull art; its source is in `Source/`. Final images live in this worktree and use the repository's existing Git LFS rules.

## Build 1 UI kit

The [UI handoff](../Assets/Art/UI/UI.md) documents 44 transparent PNG sprites, their logical/export sizes and slice borders, plus Fredoka Medium and its OFL licence. Cream panels, navy text, orange primary, teal secondary and oilskin-gold bite feedback extend the established visual world. Selected cards and action bubbles deliberately use local borders as interaction affordances; world art still has no outlines. Green `#3E9A5B` and red `#C8443A` are the existing prototype's progress/status colours, always accompanied by words or icons.

[16 — kit sheet](Concepts/16-ui-kit.png), [17 — fishing HUD](Concepts/17-hud-fishing.png) and [18 — harbour HUD](Concepts/18-hud-harbour.png) are exact 1920×1080 compositions built from the exported kit, with Blender-rendered project assets behind the two HUDs. They are design mockups, not Unity captures. Reproducible vector geometry, compositors, stage scripts and validation live in `Art/Source/`. The existing crew asset is unchanged; the mockup stage temporarily lowers the copied crew's arms in memory and never saves it back to the model source. Tier 3 skiff UI remains the next task.

## Modelling acceptance checks

1. Compare silhouettes and colours to the Day 3/28 references; maintain softness without turning objects into glossy toys or flat icons.
2. Check body height, deck grid and station bounds numerically in Blender. Written values and the exact grid supplement override generated dimension marks.
3. Keep role body/rig shared, hats separate, pot/crab state variants reusable, and animated station components separate.
4. Check models in front, side, top and the intended orthographic gameplay camera. Keep feet, hands, crates and worktops from intersecting.
5. Check at landscape phone gameplay size: hats, station purpose, carrying state and walkways must read. These concepts do not establish a device-performance benchmark.
6. During later Unity integration, verify scale, shading, shadows and visibility on the actual prototype and target hardware. No editor or runtime validation is claimed by this art pass.

## Task 04 world dressing

The expanded Gull Harbour inventory is measured in [REPORT.md](Models/GullHarbour/REPORT.md). Dressing reuses the canonical palette, without new material names. Rope coils, coarse nets, a navy tackle box, muted anchor, ivory/orange fender and warm lantern support the boats. Plaice lies flat with both eyes on top; Cod retains a separate tail and a short chin barbel. Perched Seagull is 0.4 m nose-to-tail with separate wing pivots.

ShopFront_FishMarket, ShopFront_HarbourMaster, ShopFront_CrewOffice, ShopFront_Chandlery and ShopFront_Supplies have ground roots at the door centre, front facing Unity −Z; place the root at the building door rather than centring the decoration bounds. They leave a central approach clear. MarketStallAwning is a separate open stall. SandBank is exactly flat at waterline, 4 × 2 m; CliffSegment8m repeats along X with matching ends and a level green top. Two-sided material handling is required for views below flat sea dressing.

## Task 04 skiff kit

Skiff keeps hull 2’s 5 × 3 m build deck centred at Y=0, with bow +Z and a 6.5 × 3.5 m hull envelope excluding the motor. Task 04 supersedes the forward-console proposal: the low console occupies stern-starboard tile c=2, r=0 (zero-based columns port→starboard, rows stern→bow), Unity centre (1,0,−2). Three port rod sockets sit at Unity Z=−1.75, 0, +1.75. Propeller spins around local Z. The open hold is built into the deck; HoldLid rotates about local X, from its hinge at Unity (0,.025,.5).

HandWinch reserves 1 × 1 m with a separate Crank. SortTable reserves 2 × 1 m; its .55 m worktop, tray, chute and open bin stay within that footprint. GillNetCoil sits on deck; GillNetFloatLine and GillNetSection repeat every 2 m along local X. The float-line root is at waterline, and laid mesh lies .18 m below it. The kit has coarse visible geometry and no simulation or animation clips.

## Task06 rigged crew addition

`Assets/Art/Models/Crew/CrewRig.fbx` is a new shared chibi rig; the old CrewBody and its exports remain untouched. Source, turnaround renders, three-keyframe animation contact sheets and integration contract: [CrewRig report](Models/CrewRig/REPORT.md). Bare scalp height 0.95m; 0.38m head (40%). Four outfit meshes and three rigid HatMount modules share 20 Mixamo-style bones and eleven in-place actions at 24fps. Select one outfit and one hat; leave Body enabled. There are no root-motion or prop animations.

Two new canonical sRGB materials: `M_HairChestnut` = `#50392E` and `M_HairSilver` = `#ADB6AF`; matte hair / veteran beard. Other materials reuse existing palette names. Hat_Hood uses yellow oilskin; Outfit_Fisherman includes an orange hood-down collar. Importers must set clip loop flags from the report/manifest; Blender action custom properties do not configure Unity import settings.

## Task07 world and upgrade kit

[WorldPolish report](Models/WorldPolish/REPORT.md) lists31 additive assets: larger coolers, rod/material variants, clamp/motor/bait props, harbour backdrop and dressing, static crew poses, boat repaints and sea landmarks. Prior assets remain untouched; repaints/rods retain exact original part names and pivots. No new palette names. Static NPCs reuse Task06 hair materials. KelpForest is4x4m planar and needs two-sided rendering; waterline modules may extend below their root. WhaleTail has a separate Tail part for consumer-driven rise/sink.

## Task08 day boat and texture kit

[DayBoatKit report](Models/DayBoatKit/REPORT.md) covers the exact 50-tile deck and centred six-tile bow wheelhouse, six rod sockets, port stern-quarter rail gap and nine grid stations. [Station contract](Models/DayBoatKit/Stations/REPORT.md) lists footprints, access and moving pivots. New geometry is additive and uses existing M_* names. [Texture contract](../Assets/Art/Textures/TEXTURES.md) covers three seamless palette water tiles, foam/wake/splash effects and an optional subtle deck-grain overlay. No future-tier gameplay or Unity configuration is included.
