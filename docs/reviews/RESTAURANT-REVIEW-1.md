# RESTAURANT-REVIEW-1

Codex 1 (Windows app), 2026-10-27. Review of saved captures only. No game, Assets, source-art or Git changes; no live interaction, animation or native acceptance test.

The largest presentation gap is the room behind the service HUD: its lighting, materials and dressing are substantially plainer than the painted target. The clearest UI defects are the arrange-card collisions, prep controls crossing their panel border, stale service messaging, and the pause panel's missing background dimming. Several later capture filenames contain a transition instead of the advertised screen; those cannot establish that service has improved or regressed.

## Evidence and measurement

32 screen/state comparisons, each with phone and desktop JPGs, indexed in the [comparison gallery](restaurant-review-1/index.md). Each JPG places **concept, delivered reconstruction, saved game** side by side, at equal comparison dimensions. [Source ledger](restaurant-review-1/sources.json) identifies every input, original dimensions and SHA256. [Capture inventory](restaurant-review-1/capture-inventory.json) records the initial broader capture selection; the ledger additionally includes r98/r99, added during this review. The small overviews contain both devices; full JPGs preserve the supplied capture resolution. The review is frozen at r99 so concurrent work does not make it an endless moving target.

Phone measurements below are logical pixels in **844×390**, obtained from the 2532×1170 capture at 1/3 scale. Desktop measurements use **1440×900**, from 2880×1800 at 1/2 scale. Rectangles are `[x,y,width,height]`, top-left origin; visual bounds are approximate, normally ±3 px, and are not recovered runtime layout values. Font sizes describe visible glyph height, not a proven font point size. Font identity cannot be established from these rasters.

Dedicated desktop references exist for service, coach, moods, transitions and pause. Other references are phone compositions: the sheets contain them proportionally within a neutral desktop frame. Those neutral margins are **comparison padding**, not missing game pixels. Without an authored desktop reference, centered phone compositions and desktop outer margins are not scored as layout failures. Harbour-entry art is originally 1920×1080, fitted proportionally on both sheets. Stage 3 has no separate concept: its first two columns intentionally use the same reconstruction and are not independent corroboration.

No independent full-frame reconstructed proof was located for base arrange, plan, prep or closing. The middle columns say so; a collection of sprite cuts is not represented as a reconstructed screen. Original S3–S5 delivery notes also describe hand-measured placements and an approximate font match. The 3× reconstructed paintings are useful placement references, not proof of native 3× illustration detail.

Ranking: **P1** dominates the screen or contradicts the displayed state; **P2** obvious local layout/readability/asset mismatch; **P3** smaller fidelity/content difference. **E** means evidence is missing or exercises a different state. Entries within each screen are in visibility order. “Both” means observed in both saved devices, not inferred responsive behavior. Dynamic money, dates, dish counts, staff counts, popularity and unlocked stages are excluded unless their presentation itself fails.

## Highest-priority findings

| Rank | Finding | Evidence / affected area | Next action for the lead |
|---|---|---|---|
| P1 | Room presentation falls well below the restaurant paintings | Arrange and every service variant; most of the area between top bar and bottom rail | Treat as a room lighting/material/dressing pass, not a HUD sprite substitution. Preserve functional stage differences. |
| P1 | Service-start message persists at 19:10; “Doors open” persists with Closed at 22:12 | r85 service, r88 closed; phone `[180,50,485,50]` and `[190,50,360,48]` | Check message lifetime/state and remove the obsolete navy toast where the Mira call exists. |
| P2 | Arrange card title, price and insufficient-funds state collide | r86 base arrange; phone `[510,310,145,65]` | Give title, price and status separate vertical slots; recheck affordable and insufficient states. |
| P2 | Prep forecast row crosses the panel's lower outline | r97 prep; phone `[415,286,355,26]` | Move the row upward or extend/reflow the panel; retain bottom clearance. |
| P2 | Pause lacks the target's dimming scrim | r94 pause, both entire frames outside panel | Restore the target visual separation; verify whether “Upgrades” intentionally replaces “Back to the harbour”. |
| E | Latest service files are not service evidence | r96, r97 and r99 `day-service-orders` show Evening falls | Recapture actual running service before declaring the marker/HUD review current. |

## S1 arrange and drawer states

Evidence: r86 `day-arrange`, `day-arrange-lift`, `day-arrange-buy`, `day-arrange-store`, `day-arrange-kitchen`.

Comparisons: [base phone](restaurant-review-1/01-arrange-844.jpg), [desktop](restaurant-review-1/01-arrange-1440.jpg); [lift overview](restaurant-review-1/02-arrange-states-overview.jpg); [buy overview](restaurant-review-1/25-arrange-buy-overview.jpg); [stored overview](restaurant-review-1/26-arrange-store-overview.jpg); [kitchen overview](restaurant-review-1/27-arrange-kitchen-overview.jpg). [Measured phone detail](restaurant-review-1/detail-arrange.png).

| Rank | Visible mismatch | Measurement / attribution |
|---|---|---|
| P1 | Room has bright, nearly white kitchen tiles, a largely bare flat orange floor and uniform light. Target has warm pools of light, richer surfaces, dressed kitchen, furnishings and harbour detail. | Phone room approximately `[110,40,640,265]`; desktop central room. Rendering/content difference, not evidence that a UI sprite is absent. Layout/stage can legitimately reduce furnishing count. |
| P2 | “Table for 4” title and underlying price block collide with the item illustration; the gray price capsule cuts through the card's content hierarchy. | Base phone second card `[510,310,145,65]`; title around y319, large price/illustration spans y326–357. The target separates the compact title, price and footprint. Affordable buy state avoids the large gray capsule and is visibly cleaner. |
| P2 | “Not enough coins” runs on/through the lower card outline rather than sitting inside it with padding. | Phone first and second cards, text around y364–374 and lower card outline around y370. This is a **card-border collision**, not clipping at the viewport edge. Also inspect the much smaller desktop labels at actual size. |
| P3 | Drawer cards and room props are drawn with different silhouettes/textures from the illustration. The target's selected item is a small illustrated round table; current selection/room uses different 3D table geometry. | Selection phone around `[530,165,75,80]`. Item geometry may follow the actual furniture; resolve visual authority before changing it. |
| E | Red invalid placement and pressed button feedback are not demonstrated in this set. | Do not infer interaction correctness from a green valid placement. |

The stored ribbon and “Place for free” are present in the **stored** capture. Bistro lock is present in the locked card, and Store/Sell actions are present in the lift state. Their absence in the affordable buy image is appropriate to state. Kitchen category shows stove/kettle/grill cards rather than guest tables: that is expected. No additional overlap found in the affordable or stored cards. Prices and wallet differences are data, not fidelity defects.

## S2 service, S10/S15 markers and Mira call

Evidence: r85 `day-service-orders`; later mood/pause images for the call strip. [Phone](restaurant-review-1/03-service-844.jpg), [desktop](restaurant-review-1/03-service-1440.jpg), [measured detail](restaurant-review-1/detail-service.png).

| Rank | Visible mismatch | Measurement / attribution |
|---|---|---|
| P1 | Dominant room presentation differs as described for S1; service still reads brightly lit and sparsely dressed rather than the warm occupied night room. | Phone `[150,50,600,280]`; desktop room between stock sidebar and lower crew rail. Both. |
| P1 | Obsolete navy start toast covers the upper room/call area at 19:10 and says service starts at 18:00. Desktop shows competing toast/call treatments. | Phone navy toast roughly `[180,55,485,45]`. Cream call target uses phone bubble `[190,50,320,44]` with bust `[511,47,38,52]`; navy toast is ~165 px wider. Text styling is thin/light compared with the bold navy-on-cream call family. |
| P2 | Order bubble plus ring occupies a large area over a single guest and competes with the guest/plate rather than forming the compact stacked target marker. | Phone bubble about `[455,130,70,42]`, ring about `[520,145,25,26]`; compare target bubble near `[408,130,44,38]`. World/camera placement changes position; the size and visual crowding are the actionable difference, not the x offset by itself. |
| P3 | Desktop stock/rail treatment differs from the concept: current bottom cream rail remains largely empty after Host/Help, while the reference distributes five crew slots across it. | Desktop lower strip around y815–890. Could be correct for a two-member state; capture a populated roster before treating empty slots as missing UI. |
| E | Guest question card, all dish icons, warnings, event badges, task icons, mood states and steam frames are not all exercised. | The target's right-side question card is conditional. No missing-feature claim from its absence. No animation can be assessed from a still. |

Latest filename checks: [r96 phone/desktop overview](restaurant-review-1/23-service-latest-overview.jpg) and [r99 overview](restaurant-review-1/31-current-service-overview.jpg) show **Evening falls**, not service; r97 `day-service-orders` does too. r85 therefore remains the requested service comparison, not proof of the latest build. Recapture a stable service state, plus an active guest question, breakdown, busy full rail and marker overlap stress case.

## Coach card

Evidence r88 `day-service-coach`: [phone](restaurant-review-1/04-coach-844.jpg), [desktop](restaurant-review-1/04-coach-1440.jpg).

No material card-specific sprite, alignment, overlap or clipping mismatch found at the reviewed sizes. Cream panel, host Mira bust, orange Got it and quiet Skip follow the delivered proof. Three-line text remains contained. The underlying service room retains the P1 presentation gap. Reference backgrounds vary because this is a reusable overlay; an arrange background in the concept is not a demand to show arrange during service. Other tutorial lines, long text and localization remain untested.

## Closed sign

Evidence r88 `day-service-closed`: [phone](restaurant-review-1/05-closed-844.jpg), [desktop](restaurant-review-1/05-closed-1440.jpg), [measured detail](restaurant-review-1/detail-closed.png).

| Rank | Visible mismatch | Measurement / attribution |
|---|---|---|
| P1 | Call says “Doors open! Service starts at 18:00.” while time is 22:12 and Closed is visible. | Phone call `[190,50,360,48]`; both devices. A visible state contradiction, regardless of whether the fixture deliberately advanced the clock. |
| P2 | Hanging sign floats across a staff member/room floor instead of reading as attached to the entrance/reception. | Phone sign approximately `[543,207,111,27]`, directly across the lower torso/legs of the figure above it. Anchor should follow the actual doorway, not copy the reference's screen position blindly. |

Closed text fits the board and the sprite itself matches its delivered wooden treatment. Absence of Close door after closing is correct.

## S3 plan

Evidence r97 `day-plan`: [phone](restaurant-review-1/06-plan-844.jpg), [desktop](restaurant-review-1/06-plan-1440.jpg), [measured detail](restaurant-review-1/detail-plan.png). Current r99: [phone](restaurant-review-1/28-current-plan-844.jpg), [desktop](restaurant-review-1/28-current-plan-1440.jpg).

| Rank | Visible mismatch | Measurement / attribution |
|---|---|---|
| P2 | Mira is fitted as a full-body character rather than the large torso crop. Her face loses prominence and the lower legs run to the frame edge. | Game phone character roughly `[5,20,260,370]`; face about x80–165/y70–135. Target's large face occupies roughly x65–190/y120–225, with torso cropped at bottom. This is the explicit integration risk in the S3–S5 art delivery notes. |
| Resolved in r99 | r97 Fillets used a flat green whole fish amongst rendered plated food. r99 replaces it with plated cooked fillets in the right illustration family. | Phone dish slot approximately `[405,165,115,110]`. Keep r97 as revision evidence; no outstanding asset fix requested. |
| P3 | Text composition is denser/bolder in the date and guest line than the reference; main menu-card labels also sit lower under the art. | Phone date block `[350,95,265,50]`; dish-name baseline about y248. No clipping seen. Exact font family/point size is unproven. |

No-special-request state appropriately replaces Accept/Not tonight with an empty-state message. Different date, catch, dishes and guest forecast are data. Desktop has no authored bespoke target; its outer blue margins are not scored as failure. No complete S3 full-frame proof available for a three-way import diagnosis.

## S4 prep

Evidence r97 `day-prep`: [phone](restaurant-review-1/07-prep-844.jpg), [desktop](restaurant-review-1/07-prep-1440.jpg), [measured detail](restaurant-review-1/detail-prep.png). Current r99: [phone](restaurant-review-1/29-current-prep-844.jpg), [desktop](restaurant-review-1/29-current-prep-1440.jpg); the forecast-border collision remains.

| Rank | Visible mismatch | Measurement / attribution |
|---|---|---|
| P2 | Forecast icon/label and Tight/+10%/+20% controls straddle the lower paper outline. The cream card border passes behind controls/text. | Phone row `[415,286,355,26]`; paper lower outline ~y302–309. Move row about 12–16 px upward or provide equivalent extra panel clearance. Same relative fault on desktop. |
| P3 | Header is a smooth dark navy band rather than the target's textured blue painted/wood treatment. | Phone `[0,0,844,50]`; desktop top header. Large-area material fidelity difference; not a missing button. |

One dish row versus three is a stock/menu state, not evidence of missing rows. +/- controls and quantity remain legible, bottom summary/Prepare do not collide. No complete S4 reconstructed screen was delivered, so sprite-cut attribution remains limited.

## S5 closing: requested fixture and newer live result

Evidence r89 `restaurant-closing`: [overview](restaurant-review-1/08-closing-overview.jpg); r97 `day-closing`: [phone](restaurant-review-1/22-latest-closing-844.jpg), [desktop](restaurant-review-1/22-latest-closing-1440.jpg), [measured detail](restaurant-review-1/detail-closing.png). Current r99: [phone](restaurant-review-1/30-current-closing-844.jpg), [desktop](restaurant-review-1/30-current-closing-1440.jpg); host identity/crop and quote density observations remain.

| Rank | Visible mismatch | Measurement / attribution |
|---|---|---|
| P2 | Large Mira remains in the sailing uniform, unlike the accepted restaurant host identity used in the call/coach/crew screens. | r97 phone approximately `[578,202,145,188]`. This is a cross-screen identity inconsistency; the old S5 concept itself also has sailing Mira, so it is not a literal mockup-import failure. Lead should settle whether to preserve that old concept or use host Mira consistently. |
| P2 | Full character continues below the board and behind/below Sleep, rather than ending as the target's compact torso treatment. | r97 phone lower body visible around x635–710/y365–390, board ends ~y350; target torso is mostly contained above/behind the bottom action. Both devices. |
| P3 | Three reviews have heavier, more tightly filled text than the target. Long third quote almost fills the available horizontal space. | r97 phone review column `[330,68,218,193]`; third quote around `[395,234,150,15]`. No definite clipping visible, but this is the first place to test longer review copy. |
| Resolved | r89 uses old deck-style guest faces; r97 uses the newly delivered restaurant review faces; r99 additionally shows three distinct faces. | Do not file placeholder/repetition findings as still current. |

Cats, receipt, popularity, speech bubble and Sleep remain readable. Added Best night/Full house stamps in the fixture are accepted additions, not mockup defects. Captain versus Jo as crew of the night and 1→2 versus 42→46 popularity are state. No complete independent closing reconstruction located.

## Mira moods

Evidence r93 `day-service-moods`: [phone](restaurant-review-1/09-moods-844.jpg), [desktop](restaurant-review-1/09-moods-1440.jpg).

P1 room gap remains. The call treatment itself is close to the delivered call proof: cream panel, host bust and bold text are consistent. **E:** this still shows a normal call, not all worried/excited/proud call and coach variants. A coach absent when no coaching overlay is active is not a defect. No basis to claim all mood imports or transitions verified.

## Evening and morning transitions

Evidence r92 `day-evening`: [phone](restaurant-review-1/10-evening-844.jpg), [desktop](restaurant-review-1/10-evening-1440.jpg). r91 `day-morning`: [phone](restaurant-review-1/11-morning-844.jpg), [desktop](restaurant-review-1/11-morning-1440.jpg).

No material painting, band placement, slice, clipping or overlap mismatch found. Both use the full-frame paintings and low cream title band in the delivered compositions. Live text is slightly heavier than the painted reference and optical baseline differs by only a few pixels; P3, not a blocker. “Your first guests” versus “your guests” is runtime copy. These are stills; transition timing and fade smoothness were not tested.

## S8 upgrades

Evidence r92 `day-upgrades`: [phone](restaurant-review-1/12-upgrades-844.jpg), [desktop](restaurant-review-1/12-upgrades-1440.jpg).

P3 source-art fidelity: title mounting/ropes and oversized bright brass fasteners differ from the concept; the same changed fasteners and backings are already in the **reconstructed proof**, so this is not attributable to game import. Affected area is the title and card corners across the phone composition, especially upper cards. Current layout and live labels broadly follow that proof. No definite clipping or button collision seen. Owned/locked/dimmed prices are appropriate to upgrade state; capture purchase burst frames to assess animation. Different stage requirements need design validation, not a raster verdict.

## Service pause

Evidence r94 `day-service-paused`: [phone](restaurant-review-1/13-pause-844.jpg), [desktop](restaurant-review-1/13-pause-1440.jpg).

| Rank | Visible mismatch | Measurement / attribution |
|---|---|---|
| P2 | Missing background scrim leaves room, stock and HUD as bright as normal service. Concept and proof visibly dim everything behind the modal. | Entire phone `[0,0,844,390]` outside panel roughly `[245,52,355,286]`; entire desktop outside centered modal. Clear on both. |
| P2 / decision | Third action reads “Upgrades”; both references read “Back to the harbour”. | Phone third button roughly `[285,260,275,42]`. This establishes a label/flow difference, not the button's actual route. Confirm intended service escape action. |

Panel and other two buttons are close to the delivered placement; text fits. Room presentation gap remains visible behind it.

## S11 stage-up

Evidence r95 `restaurant-stageup`: [phone](restaurant-review-1/14-stage2-844.jpg), [desktop](restaurant-review-1/14-stage2-1440.jpg). Stage 3 r95 `restaurant-stageup3`: [phone](restaurant-review-1/15-stage3-844.jpg), [desktop](restaurant-review-1/15-stage3-1440.jpg).

Stage 2: no material layout/clipping issue found. New stage ribbon and celebration additions are expected extensions beyond the first concept. Facade painting differs slightly from the earliest concept but follows delivered art. Confetti/rays animation cannot be validated from a single still.

Stage 3: **P2 content decision** in the unlock-list area (phone right half, roughly `[455,135,310,155]`): proof lists “12×5 floor plan / Booths for six / Joined next-door house”; game lists “A proper dining room / A bar / Bigger kitchen”. Resolve list authority before changing labels or layout. Neither list visibly clips. No independent stage-3 concept was found; the duplicate first/middle columns are labeled accordingly. Stage 4 has only older r53 capture evidence in this collection and is not certified against the r95 celebration implementation.

## S16 week report

Evidence r97 `day-week` (supersedes r96): [phone](restaurant-review-1/16-week-844.jpg), [desktop](restaurant-review-1/16-week-1440.jpg), [measured detail](restaurant-review-1/detail-week.png).

No material missing-piece, overlap or clipping mismatch found. Seven bars, medal/dish, restaurant Mira bust, popularity, coins and Next week are all present. The longer crew commendation fits phone `[575,255,235,25]` with limited spare width: test a longer name/line, but it is not currently clipped. P3 copy difference “Seven nights” versus “Seven lovely nights” in the left heading `[40,90,175,25]`. Bar values, best dish, crew, total and unchanged popularity are data. Desktop's centered composition has no bespoke desktop reference, so margins are not a defect.

## S6 dashboard

Evidence r82 `day-dashboard`: [phone](restaurant-review-1/17-dashboard-844.jpg), [desktop](restaurant-review-1/17-dashboard-1440.jpg).

P3 art-fidelity differences in title/backing/fasteners already exist between concept and reconstruction; game largely follows the delivered panel family. Arrange replacing an earlier Live service tab is an accepted later addition. **E:** week-zero state leaves income/trend/menu performance empty, so the seven-night populated layout, live node/segment/fill pieces and empty-day bars cannot be visually accepted here. No visible panel overlap established in the empty state. Use r97 week report for its separate screen, not as proof of this dashboard chart.

## S7 market

Evidence r81 `day-market`: [phone](restaurant-review-1/18-market-844.jpg), [desktop](restaurant-review-1/18-market-1440.jpg), [measured detail](restaurant-review-1/detail-market.png).

| Rank | Visible mismatch | Measurement / attribution |
|---|---|---|
| P2 | Sell text is substantially smaller than Keep beside it, weakening the primary action despite equal-sized buttons. | Phone Sell glyphs about 11–12 px tall, Keep about 15–17 px; first pair within `[399,114,153,44]`, repeated at y190 and267. Both devices. Target uses a more balanced label scale. |
| P3 / decision | Buyer mood has text but no illustrated mood face/sun, unlike the target's keen-mood treatment. | Phone buyer section approximately `[575,215,230,42]`. “Steady” is valid dynamic copy; decide whether neutral moods should retain an icon rather than calling the value wrong. |
| P3 | Thick inset row borders/brass fittings depart from the original painting. | Already visible in delivered reconstruction; art-source delta, not an import-only issue. |

Fish rows, weight/price/total, keep controls and bottom total fit. Sold-out, Fresh today and pressed quantity states are not all exercised, and cannot be accepted from this capture.

## S9 crew priorities

Evidence r82 `restaurant-crew`: [phone](restaurant-review-1/19-crew-844.jpg), [desktop](restaurant-review-1/19-crew-1440.jpg), [measured detail](restaurant-review-1/detail-crew.png).

| Rank | Visible mismatch | Measurement / attribution |
|---|---|---|
| P2 | Mira's bust intrudes into the header/large left brass fastener rather than leaving a clean header/first-row boundary. | Phone bust approximately `[35,68,61,57]`, header spans y60–84; head overlaps its lower ~16 px. Similar protrusion repeats on following rows, so adjust portrait crop/row mask as a system. |
| P2 / decision | Bottom instruction says tap two tasks to swap; original concept says drag to reorder, while drag-handle glyphs remain on each chip. | Phone footer `[55,360,430,16]`; chips span x355–815, handle at right of each. Resolve interaction/copy consistency; stills do not prove either behavior. |
| P3 | Save priorities text is smaller/less prominent than target despite a large orange action area. | Phone button `[658,351,174,31]`, glyph height around15 px. Increase only after fitting the intended type family. |

Current row role type is much more uniform than the old reconstruction's oversized, inconsistent role text. **Do not restore the stale proof's extreme row type sizes.** The accepted remeasurement takes precedence. Current fixed-job wording correctly uses Waiter. New/old portrait mixes should be checked against the approved roster mapping; this screenshot alone does not establish every identity's intended job outfit. Drag/drop target and locked-job tooltip states are not demonstrated.

## S12 sleep

Evidence r78 `restaurant-sleep`: [phone](restaurant-review-1/20-sleep-844.jpg), [desktop](restaurant-review-1/20-sleep-1440.jpg).

No material panel, icon placement, text containment or button mismatch found against the delivered proof. Title, tonight result, popularity/weather/booking rows and orange Sleep retain their intended hierarchy. Weather variants and very long booking copy need their own state evidence; a sun/fair still cannot certify rain/storm swaps. Desktop has no bespoke target.

## S13 first-night coaching

Evidence r91 `day-service-late`: [phone](restaurant-review-1/21-firstnight-844.jpg), [desktop](restaurant-review-1/21-firstnight-1440.jpg).

No material mismatch found: the four painted instruction frames, Mira, bubble and action match the delivered assembly closely. This is the **first-night instruction sheet**, despite the filename; it is not evidence of running late service. It also does not prove that the four coaching pointers track moving room objects at runtime. No definite overlap, clipping or added blur found at reviewed size.

## S14 harbour entry

Evidence r85 `new-harbour`: [phone](restaurant-review-1/24-harbour-entry-844.jpg), [desktop](restaurant-review-1/24-harbour-entry-1440.jpg).

**E, not an import verdict:** both files show the ordinary MARKET fish grid with tutorial UI and a new-game toast. They do not show the harbour HUD area containing the Mira's restaurant entry target. A whole-screen visual mismatch is obvious, but measuring a missing button against a different screen would be misleading. Capture the actual harbour hub with the restaurant entry enabled; then review icon, label and Service tonight badge against S14's 1920×1080 art at proportional scale.

## S3 reservation follow-up, added during review

Evidence r98 `restaurant-plan`: [phone](restaurant-review-1/32-reservation-844.jpg), [desktop](restaurant-review-1/32-reservation-1440.jpg). This is a later extension of the old Special request ticket, so the original S3 concept is context and the reservation reconstruction is the closer authority.

The new guest-face/name, party/reward, wished dish and Accept/Decline composition is readable and contained. Phone ticket is approximately `[675,75,155,210]`; portrait/name around `[683,105,125,32]`, buttons around `[680,194,145,90]`. No definite clipping or overlap found in the short Ada/Grilled fish sample. The main Mira crop remains the S3 P2 issue. **E:** a reservation time is not visible in this sample; the original art request included time, so the lead should confirm whether party/reward intentionally replaces it. Longer guest/dish names and accepted/declined states are untested.

## Typography, blur and source attribution

- Across the illustrated screens the live font is a close rounded display substitute, not a demonstrated exact painted-font match. Some live text is heavier/wider. Concrete hierarchy problems are called out above; no guessed font family is filed as a confirmed defect.
- Native logical-size grids were inspected for arrange, service, closed, plan, prep, closing, market, crew and week. No broad new downsampling blur or damaged alpha fringe was established. Tiny market Sell labels and desktop drawer labels have readability limits; making 3× exports does not itself add illustration detail.
- Where concept and reconstructed proof already differ (brass fasteners, panel shapes, facade details), report the source-art discrepancy to the art owner. Where proof and game differ (pause dimming, live text/state), inspect integration. Do not fix legitimate runtime data to match mock values.

## Remaining capture gaps and handoff

This completes the requested saved-image review, not player acceptance. Highest-value next evidence: actual latest running service (not transition), populated full crew rail and dashboard, guest question/breakdown/events together, invalid placement and pressed states, long localized text, all Mira/weather variants, stage 4 with current celebration, and actual harbour restaurant entry. S17 hiring is pending Mo's decision and has no matching current game capture; no verdict invented.

Every one of the 32 state overviews was visually inspected, covering both devices. Full-resolution comparison files are supplied for independent inspection; nine explicit logical-pixel grids support the detailed bounds. Regeneration preserves aspect ratios, original input files and their hashes. No runtime or regression suite was run because this task changes review documents/images only.

Reproduce images with `uv run --with pillow python docs/reviews/restaurant-review-1/build_comparisons.py`. Supporting scripts are confined to the review folder. Exact source paths and checksums are in `sources.json`; source hashes are checked again in `audit.json`. Final diary records completion and releases review reservations.

## Re-check — RESTAURANT-REVIEW-2, 2026-10-27

**Five PASS; one residual FAIL.** Rechecked the six requested fixes in r101/r101a/r112 at **844×390 and 1440×900**, against the concepts and the findings above. This appendix supersedes the earlier findings only for those fixes. Measurements remain approximate ±3 logical px. Saved-image review only; toast lifetime, interaction and animation are untested. Pause scrim deliberately skipped. No Assets/code/Git changes or new art.

Comparison JPGs contain the reference, earlier evidence and new capture(s), each at the stated logical device size. Phone-only references are fitted proportionally on desktop, without inventing a desktop layout. [Measured crops](restaurant-review-1/recheck-2/measured-details.png) use nearest-neighbour enlargement for border/glyph inspection; [source hashes](restaurant-review-1/recheck-2/sources.json) identify the inputs.

| Fix | Verdict | Device-size evidence and pixel notes |
|---|---|---|
| Transition leaking into service captures | **PASS** | r101 and r112 `day-service-orders` both show the room, 19:10 HUD, stock and guest marker, with no Evening falls painting/band. The former whole-frame evidence gap is closed for this state on both devices. [Phone](restaurant-review-1/recheck-2/service-844.jpg), [desktop](restaurant-review-1/recheck-2/service-1440.jpg). This does not test the transition's playback. |
| Stale Mira call / Doors-open contradiction | **PASS** | r101/r112: stock shows soup **0** and the call says “Soup's all gone!”; at **22:12**, with Closed visible, it says “Doors closed. Last plates!” Phone call approximately `[190,50,360,48]`, desktop `[445,85,490,62]`. The obsolete service-start line is gone. **Separate residual:** a navy “Haul sold! +162 coins · 1 crate” toast remains over the service room, phone `[240,102,365,48]`, desktop `[440,238,560,70]`. It obscures room/character detail and competes with the cream call; stills cannot establish whether it is stuck or briefly crossing the market/service hand-off. [Closed phone](restaurant-review-1/recheck-2/closed-844.jpg), [desktop](restaurant-review-1/recheck-2/closed-1440.jpg); service links above. |
| Prep forecast crossing paper border | **PASS** | r101/r112 phone controls now roughly `[530,275,240,23]`, with lower paper stroke around y302–308: about **4–6 px** clear space. Desktop controls `[905,586,410,39]`, lower stroke y634–640: about **9 px** clear. The ~14 px phone upward correction removes the former collision. [Phone](restaurant-review-1/recheck-2/prep-844.jpg), [desktop](restaurant-review-1/recheck-2/prep-1440.jpg). |
| Market Sell too small beside Keep | **PASS** | r101a: first phone pair remains around `[398,115,155,44]`; Sell and Keep glyphs now both approximately **16–18 px** high, versus the old Sell's ~11–12 px. Desktop both are approximately **27–30 px**. All three rows fit; the primary action no longer loses hierarchy through smaller type. [Phone](restaurant-review-1/recheck-2/market-844.jpg), [desktop](restaurant-review-1/recheck-2/market-1440.jpg). |
| Arrange locked card art/text collision | **PASS** | r101a base and buy: phone locked card `[660,310,168,64]` now separates the small left illustration (roughly `[678,333,31,33]`) from Terrace table / Stage 2 at x727–813 and the Bistro tag above. Desktop card `[1138,764,270,107]` has similarly separate art/name/stage areas. No art/label collision seen. [Phone](restaurant-review-1/recheck-2/arrange-844.jpg), [desktop](restaurant-review-1/recheck-2/arrange-1440.jpg); [affordable phone](restaurant-review-1/recheck-2/arrange-buy-844.jpg), [desktop](restaurant-review-1/recheck-2/arrange-buy-1440.jpg). |
| Arrange insufficient-coins card clearance | **FAIL — partial fix** | r101a removes the illustrations and separates Table for 2/4 from the grey price capsule, fixing those collisions. **The reason still touches/crosses the bottom card stroke:** phone text roughly y361–371, stroke y369–373; desktop text y851–866, stroke y864–871. This is still a card-border collision, not viewport clipping. First two cards phone x353–654; desktop x603–1120. Move the reason up about **5–6 phone px / 8–10 desktop px**, or add equivalent card height while retaining separation from price. Same arrange evidence above; enlarged crops show the remaining contact. |

### Remaining P2s, in player-notice order

The room's lighting/material/dressing gap remains **P1**, ahead of this list. Items outside the six fixes below are carried forward from REVIEW-1, not certified against a newly captured version of those screens. Pause scrim is excluded as requested.

1. **Service's navy sale toast over the room** — newly visible in r101/r112; largest local obstruction. Check market-to-service message clearing and lifetime before attributing it to a stuck toast.
2. **Plan Mira's small face/full-body fit** — large focal-character mismatch; restore the intended torso crop/face prominence (phone character area `[5,20,260,370]`). r112 plan is not part of the six-item recheck; original S3 finding remains the basis.
3. **Arrange “Not enough coins” on the card border** — confirmed above on both devices; the remaining part of the drawer collision finding.
4. **Closing Mira's sailing outfit and lower-body crop** — resolve host identity and contain the character relative to the board/Sleep action (original phone `[578,202,145,188]`).
5. **Service order bubble/ring crowding** — still visually large in r112: phone bubble about `[456,129,66,41]` plus ring near `[520,145,25,26]`, compared with the target's compact bubble (~44×38). Preserve world anchoring; tighten the marker footprint rather than copying the target's x coordinate.
6. **Crew-priorities portraits intruding into the header** — original phone Mira `[35,68,61,57]`, header y60–84; review row masking/crop across the roster.
7. **Crew priorities drag handles versus “tap two tasks” instructions** — resolve the interaction/copy contract before changing the art; footer `[55,360,430,16]`.
8. **Pause third action differs from reference** — “Upgrades” versus “Back to the harbour”; content/flow decision, separate from the excluded scrim.
9. **Stage-3 unlock-list authority** — game and delivered proof list different benefits; resolve intended content before treating it as a layout fix (original phone `[455,135,310,155]`).

The earlier Closed-sign torso overlap is **not reproduced** in r101/r112: the sign is now beside the right-hand entrance without crossing a staff body. World attachment through camera motion remains untested. Weather/mood variants, populated dashboard/crew states and the actual harbour-entry capture remain evidence requests, not measured P2 failures. No new general blur or clipping was established in the six checked fixes.
