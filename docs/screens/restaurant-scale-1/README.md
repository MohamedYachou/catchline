# Restaurant room and camera scale study

Use **52° orthographic, straight on from the front (yaw 0°)** as the working camera. Orthographic has no FOV; the perspective comparison uses vertical FOV 30°. Keep a whole-room service overview and provide a distinct placement zoom with pan on phone. **None of the four tested rooms meets 44 px in both floor-tile dimensions in a whole-room phone view.** This is a measured limit, not a touch-acceptance result.

## Decision for the proposed stages

The brief’s 8×5, 10×5, 12×6 and 14×7 floors correspond to the draft Café/Bistro/Restaurant/Seafood house stages. Terraces are outside this study. The largest tested room usable for direct 44 px tile placement with the entire room visible on phone is **none** at every stage. 10×5 is as readable as 8×5 at these camera fits because vertical space, rather than width, limits the view. Do not advertise later stages as single-screen placement.

| Stage floor | 52° ortho back tile, phone | Minimum zoom for 44 px depth | Zoom for 48 px depth | Whole-room desktop tile |
|---|---:|---:|---:|---:|
| 8×5 | 44.3×35.0 px | 1.26× | 1.37× | 118.9×93.7 px |
| 10×5 | 44.3×35.0 px | 1.26× | 1.37× | 118.9×93.7 px |
| 12×6 | 38.8×30.6 px | 1.44× | 1.57× | 104.3×82.2 px |
| 14×7 | 34.6×27.3 px | 1.61× | 1.76× | 92.8×73.2 px |

Zoom ratios are calculated from the measured orthographic projection, not additional rendered/touch-tested modes. At a 48 px tile depth, the phone viewport spans about 13.9 m horizontally and 5.46 m of floor depth before wall allowance. Thus 8×5 and 10×5 may need mainly a vertical pan or reduced wall presentation; 12×6 needs vertical pan; 14×7 needs horizontal and vertical pan. Keep one-step reset to overview. If a fixed whole-room placement view is mandatory, revise room depth/HUD/wall framing and run a new study; no untested smaller floor is certified here.

## Reading the comparison

- **52° ortho:** best balance for this study. Consistent tile size front/back, still recognizable bodies and furniture faces. Phone crew are only about 30 px at the two smallest overviews, so use separate service/action targets rather than requiring taps on tiny crew.
- **60° ortho:** best phone floor depth (37.5 px for 8×5/10×5), still below 44; crew shrink to about 24 px and read as heads. The small depth improvement does not remove the need for zoom.
- **45° ortho:** strongest body read, but only 32.6 px tile depth for the smallest rooms.
- **Perspective 30°:** room-like depth, but the back kitchen shrinks most. Back-row tile depth is only 17.8–29.7 px on phone. Perspective 14×7/45° also misses 44 px on desktop; 23 of 24 desktop configurations pass the geometric threshold. All 12 desktop orthographic configurations pass.

At every view the sampled rear stove-top centres are visible past the pass/crew. This is **not** a claim that the whole kitchen floor or all feet are visible. The separate aisle-floor rays below show partial or complete occlusion behind the counter and crew. Material contrast was corrected after visual review: light pass countertop over navy front, still within the 0.9 m counter envelope. This improves the pass read without removing the real occluder.

## Placement implications

- Use an explicit placement zoom and bounded pan; retain an overview reset and a clear selected tile.
- Float the drag ghost roughly 56–72 phone pixels above the finger, with a tether or highlighted footprint showing the actual destination. Keep rotation/confirm controls outside the drag contact. These offsets are proposed, not tested.
- Show blocked cells/aisles, and use a deliberate confirm after selection. Inflating adjacent invisible tile hit boxes cannot solve overlapping targets.
- Consider fading the front face of the pass/side walls when a hidden tile is selected. Retest before accepting it: the present floor-ray failures remain real.

## Method and reproducibility

Unity 6000.3.25f1 renders in **Catchline-sim only** via `RestaurantScaleStudy.Run`. Reproduction source is `RestaurantScaleStudy.cs.txt`; the live editor source and throwaway final scene are in `../Catchline-sim/Assets/Editor/RestaurantScaleStudy.cs` and `../Catchline-sim/Assets/RestaurantScaleStudy.unity`. Run the generator to reconstruct procedural materials/each room; the retained scene represents the last 14×7 configuration, not all 48 views. No gameplay, scene or C#/meta in main Assets was edited. No play mode, save, installation, time-scale change, commit or staging.

Four room sizes × three pitches × perspective/orthographic × two resolutions = **48 captures**, plus eight contact sheets (one room/resolution each). Contact-sheet rows are 45°,52°,60°; left perspective, right ortho. Every final image is opened individually by Codex 1; see `visual-review.json`.

Tiles are 1 m centres with 0.025 m grid gaps; side/back walls are 2.4 m, front wall absent. Warm kitchen zone back-left, wood guest zone front-right; pass one tile deep at 0.9 m height, stoves 0.9×0.6×0.9 m, two/four-seat table/chair boxes, orange entrance tile/reception and a back kitchen door. Real `Assets/Art/Models/Crew/CrewRig.fbx`, original unit scale and sampled Idle, Deckhand outfit/Beanie: measured renderer height 1.096 m. This is the game’s stylized crew scale, not a rescaled 1.8 m human. Stove height is consequently close to crew height.

HUD bands are plain offline composited overlays as permitted by the brief, not implemented restaurant HUD. At 844×390: top44/bottom84, usable262px. `CoastalCanvas.Begin` uses logical height480 below600px, otherwise720. Calibrating the brief’s phone pixel bands to those scale factors produces rounded desktop top68/bottom129, usable703px. No safe-area inset is modelled. The gold reference is a literal44px square at both resolutions.

Camera uses a viewport bounded by those bands. It fits the complete room envelope (floor, full-height walls) with 2.5% viewport margin on every side. Orthographic scale or perspective distance is binary-searched for each resolution; centre is room bounds centre, yaw0. The whole room fits in all48 by construction and visual inspection; this maximizes fit for the declared centred-camera policy, not every possible off-axis lens shift.

Measurements use the same projection as the render: smallest far-edge horizontal width across the back row (z=depth), and projected front-to-back edge depth of that row. Perspective width was corrected from near to far edge after independent review. No diagonal width or bounding-box area substitutes for the44px depth check. Crew height is projected vertical renderer-bounds extent at the back worker centre, not segmented visible silhouette. Kitchen top visibility uses two/three rays to rear stove top centres at0.94m; aisle-floor visibility uses the same x centres at z=depth-1.5,y=0.03m. Rays include real box/crew occluders and stop before the sampled point. They do not certify arbitrary placements, all pixels or walkable routes.

No full game regression is needed or claimed for this isolated study. Unity compilation/render completion, exact artifact dimensions, geometric measurements and visual review are checked. Native gameplay UI, touch hardware, crowded-night service, animations, pathfinding, terrace layouts and final art remain untested. Independent read-only design and metric assessments are recorded in `review-notes.md`; no browser/Lighthouse applies to the native Unity greybox.

## Every capture

`Top/floor` = visible stove-top centre probes / visible rear-aisle floor probes, each out of the shown sample count. `Fit` includes walls between HUD bands; `44px` needs both tile dimensions=44. All pixel values are screen pixels.

| Image | Tile W×D px | Crew px | Fit | Top/floor visible | 44px |
|---|---:|---:|---|---|---|
| [8x5-45-persp-844x390.png](8x5-45-persp-844x390.png) | 34.3×23.9 | 30.4 | yes | 2/2 top; 1/2 floor | FAIL |
| [8x5-45-persp-1440x900.png](8x5-45-persp-1440x900.png) | 92.3×64.2 | 81.7 | yes | 2/2 top; 1/2 floor | PASS |
| [8x5-45-ortho-844x390.png](8x5-45-ortho-844x390.png) | 46.0×32.6 | 35.7 | yes | 2/2 top; 1/2 floor | FAIL |
| [8x5-45-ortho-1440x900.png](8x5-45-ortho-1440x900.png) | 123.4×87.3 | 95.7 | yes | 2/2 top; 1/2 floor | PASS |
| [8x5-52-persp-844x390.png](8x5-52-persp-844x390.png) | 34.4×26.5 | 27.2 | yes | 2/2 top; 1/2 floor | FAIL |
| [8x5-52-persp-1440x900.png](8x5-52-persp-1440x900.png) | 92.7×71.2 | 73.2 | yes | 2/2 top; 1/2 floor | PASS |
| [8x5-52-ortho-844x390.png](8x5-52-ortho-844x390.png) | 44.3×35.0 | 29.9 | yes | 2/2 top; 1/2 floor | FAIL |
| [8x5-52-ortho-1440x900.png](8x5-52-ortho-1440x900.png) | 118.9×93.7 | 80.3 | yes | 2/2 top; 1/2 floor | PASS |
| [8x5-60-persp-844x390.png](8x5-60-persp-844x390.png) | 35.3×29.7 | 23.7 | yes | 2/2 top; 1/2 floor | FAIL |
| [8x5-60-persp-1440x900.png](8x5-60-persp-1440x900.png) | 94.9×79.7 | 63.8 | yes | 2/2 top; 1/2 floor | PASS |
| [8x5-60-ortho-844x390.png](8x5-60-ortho-844x390.png) | 43.3×37.5 | 23.8 | yes | 2/2 top; 1/2 floor | FAIL |
| [8x5-60-ortho-1440x900.png](8x5-60-ortho-1440x900.png) | 116.2×100.7 | 63.7 | yes | 2/2 top; 1/2 floor | PASS |
| [10x5-45-persp-844x390.png](10x5-45-persp-844x390.png) | 34.3×23.9 | 30.7 | yes | 3/3 top; 1/3 floor | FAIL |
| [10x5-45-persp-1440x900.png](10x5-45-persp-1440x900.png) | 86.7×60.4 | 76.8 | yes | 3/3 top; 1/3 floor | PASS |
| [10x5-45-ortho-844x390.png](10x5-45-ortho-844x390.png) | 46.0×32.6 | 35.7 | yes | 3/3 top; 1/3 floor | FAIL |
| [10x5-45-ortho-1440x900.png](10x5-45-ortho-1440x900.png) | 123.4×87.3 | 95.7 | yes | 3/3 top; 1/3 floor | PASS |
| [10x5-52-persp-844x390.png](10x5-52-persp-844x390.png) | 34.4×26.5 | 27.7 | yes | 3/3 top; 1/3 floor | FAIL |
| [10x5-52-persp-1440x900.png](10x5-52-persp-1440x900.png) | 88.3×67.9 | 70.2 | yes | 3/3 top; 1/3 floor | PASS |
| [10x5-52-ortho-844x390.png](10x5-52-ortho-844x390.png) | 44.3×35.0 | 29.9 | yes | 3/3 top; 1/3 floor | FAIL |
| [10x5-52-ortho-1440x900.png](10x5-52-ortho-1440x900.png) | 118.9×93.7 | 80.3 | yes | 3/3 top; 1/3 floor | PASS |
| [10x5-60-persp-844x390.png](10x5-60-persp-844x390.png) | 35.3×29.7 | 24.4 | yes | 3/3 top; 1/3 floor | FAIL |
| [10x5-60-persp-1440x900.png](10x5-60-persp-1440x900.png) | 90.7×76.3 | 62.0 | yes | 3/3 top; 1/3 floor | PASS |
| [10x5-60-ortho-844x390.png](10x5-60-ortho-844x390.png) | 43.3×37.5 | 23.8 | yes | 3/3 top; 1/3 floor | FAIL |
| [10x5-60-ortho-1440x900.png](10x5-60-ortho-1440x900.png) | 116.2×100.7 | 63.7 | yes | 3/3 top; 1/3 floor | PASS |
| [12x6-45-persp-844x390.png](12x6-45-persp-844x390.png) | 29.9×20.4 | 27.1 | yes | 3/3 top; 0/3 floor | FAIL |
| [12x6-45-persp-1440x900.png](12x6-45-persp-1440x900.png) | 73.9×50.5 | 65.9 | yes | 3/3 top; 0/3 floor | PASS |
| [12x6-45-ortho-844x390.png](12x6-45-ortho-844x390.png) | 40.6×28.8 | 31.6 | yes | 3/3 top; 0/3 floor | FAIL |
| [12x6-45-ortho-1440x900.png](12x6-45-ortho-1440x900.png) | 109.2×77.2 | 84.6 | yes | 3/3 top; 0/3 floor | PASS |
| [12x6-52-persp-844x390.png](12x6-52-persp-844x390.png) | 29.9×22.6 | 24.5 | yes | 3/3 top; 0/3 floor | FAIL |
| [12x6-52-persp-1440x900.png](12x6-52-persp-1440x900.png) | 75.4×57.1 | 60.9 | yes | 3/3 top; 0/3 floor | PASS |
| [12x6-52-ortho-844x390.png](12x6-52-ortho-844x390.png) | 38.8×30.6 | 26.2 | yes | 3/3 top; 0/3 floor | FAIL |
| [12x6-52-ortho-1440x900.png](12x6-52-ortho-1440x900.png) | 104.3×82.2 | 70.4 | yes | 3/3 top; 0/3 floor | PASS |
| [12x6-60-persp-844x390.png](12x6-60-persp-844x390.png) | 30.4×25.3 | 21.7 | yes | 3/3 top; 0/3 floor | FAIL |
| [12x6-60-persp-1440x900.png](12x6-60-persp-1440x900.png) | 77.7×64.6 | 54.6 | yes | 3/3 top; 0/3 floor | PASS |
| [12x6-60-ortho-844x390.png](12x6-60-ortho-844x390.png) | 37.6×32.6 | 20.6 | yes | 3/3 top; 0/3 floor | FAIL |
| [12x6-60-ortho-1440x900.png](12x6-60-ortho-1440x900.png) | 101.0×87.5 | 55.4 | yes | 3/3 top; 0/3 floor | PASS |
| [14x7-45-persp-844x390.png](14x7-45-persp-844x390.png) | 26.5×17.8 | 24.2 | yes | 3/3 top; 0/3 floor | FAIL |
| [14x7-45-persp-1440x900.png](14x7-45-persp-1440x900.png) | 64.3×43.4 | 57.7 | yes | 3/3 top; 0/3 floor | FAIL |
| [14x7-45-ortho-844x390.png](14x7-45-ortho-844x390.png) | 36.4×25.8 | 28.3 | yes | 3/3 top; 0/3 floor | FAIL |
| [14x7-45-ortho-1440x900.png](14x7-45-ortho-1440x900.png) | 96.1×67.9 | 74.5 | yes | 3/3 top; 0/3 floor | PASS |
| [14x7-52-persp-844x390.png](14x7-52-persp-844x390.png) | 26.4×19.7 | 22.0 | yes | 3/3 top; 0/3 floor | FAIL |
| [14x7-52-persp-1440x900.png](14x7-52-persp-1440x900.png) | 65.8×49.3 | 53.8 | yes | 3/3 top; 0/3 floor | PASS |
| [14x7-52-ortho-844x390.png](14x7-52-ortho-844x390.png) | 34.6×27.3 | 23.4 | yes | 3/3 top; 0/3 floor | FAIL |
| [14x7-52-ortho-1440x900.png](14x7-52-ortho-1440x900.png) | 92.8×73.2 | 62.7 | yes | 3/3 top; 0/3 floor | PASS |
| [14x7-60-persp-844x390.png](14x7-60-persp-844x390.png) | 26.8×22.0 | 19.6 | yes | 3/3 top; 0/3 floor | FAIL |
| [14x7-60-persp-1440x900.png](14x7-60-persp-1440x900.png) | 68.0×56.1 | 48.8 | yes | 3/3 top; 0/3 floor | PASS |
| [14x7-60-ortho-844x390.png](14x7-60-ortho-844x390.png) | 33.2×28.8 | 18.2 | yes | 3/3 top; 0/3 floor | FAIL |
| [14x7-60-ortho-1440x900.png](14x7-60-ortho-1440x900.png) | 89.3×77.3 | 48.9 | yes | 3/3 top; 0/3 floor | PASS |

## Camera settings

| Room / pitch / projection | Phone size or distance | Desktop size or distance |
|---|---:|---:|
| 8×5 / 45° / persp | 11.6412 m | 11.6035 m |
| 8×5 / 45° / ortho | 2.8502 m | 2.8475 m |
| 8×5 / 52° / persp | 11.7071 m | 11.6680 m |
| 8×5 / 52° / ortho | 2.9581 m | 2.9553 m |
| 8×5 / 60° / persp | 11.5688 m | 11.5288 m |
| 8×5 / 60° / ortho | 3.0273 m | 3.0245 m |
| 10×5 / 45° / persp | 11.6412 m | 12.5206 m |
| 10×5 / 45° / ortho | 2.8502 m | 2.8475 m |
| 10×5 / 52° / persp | 11.7071 m | 12.3781 m |
| 10×5 / 52° / ortho | 2.9581 m | 2.9553 m |
| 10×5 / 60° / persp | 11.5688 m | 12.1687 m |
| 10×5 / 60° / ortho | 3.0273 m | 3.0245 m |
| 12×6 / 45° / persp | 13.3871 m | 14.7920 m |
| 12×6 / 45° / ortho | 3.2233 m | 3.2203 m |
| 12×6 / 52° / persp | 13.5666 m | 14.6038 m |
| 12×6 / 52° / ortho | 3.3738 m | 3.3707 m |
| 12×6 / 60° / persp | 13.5240 m | 14.3365 m |
| 12×6 / 60° / ortho | 3.4842 m | 3.4810 m |
| 14×7 / 45° / persp | 15.1329 m | 17.0634 m |
| 14×7 / 45° / ortho | 3.5963 m | 3.6589 m |
| 14×7 / 52° / persp | 15.4260 m | 16.8295 m |
| 14×7 / 52° / ortho | 3.7896 m | 3.7860 m |
| 14×7 / 60° / persp | 15.4792 m | 16.5044 m |
| 14×7 / 60° / ortho | 3.9411 m | 3.9374 m |
