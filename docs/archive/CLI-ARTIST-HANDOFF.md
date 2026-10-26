# Codex 2 — current Catchline checkpoint — 2026-10-24

Codex 1 = Windows; Codex 2 = existing WSL CLI. Main `comms.md` is canonical:
START before edits, ordered steps, last verified/in-progress checkpoints during
work, DONE/PARTIAL with released scope at turn end. On pickup inspect the first
unfinished step's actual partial files; do not restart verified earlier steps.
Thread `01a13eac-e066-72e2-b226-f7f85c5cf5d4`; preserve account/model/effort.
No new delegation without current authorization. No active subagent.

## MIRA-R10 — Codex 2 — 2026-10-24 — DONE, final r16

Updated [Mira-sol](../Art/Models/CrewV2/Mira-sol/) source/FBX, two 512-square
textures, [review](../Art/Models/CrewV2/Mira-sol/Mira-review.png) and
[REPORT](../Art/Models/CrewV2/Mira-sol/REPORT.md): **19,974 triangles**.
Rear scalp layers/twelve narrow wavy pony locks/loose ends replace the rear block.
Approved front geometry/materials/weights exact; r09 files/renders archived intact.
Shared female shape: `Art/Source/crew_female_shape.py`, enabled by default in
`build_mira_r10.py` (`--no-female` retains original male shape). Height/head,
existing weights and rig unchanged; REPORT explains reuse for later outfits.

VERIFIED: independent saved-source and actual-FBX PASS20original bones,
11unchanged source actions, normalized weights,44sampled poses/bounds,scale,
textures; separate r09/front/female-field/male-flag/rear-texture audit PASS.
All17final views and composed sheet reopened, including same-scale body and
crew comparisons, rear close-up, Idle/Walk/Carry/Cast front/side checks.
No obvious clothing clipping in those selected frames. Extreme close-up curls
remain angular; hair rigidly follows Head. Claude/Mo own native acceptance.
No Assets/game source/Unity/git changes, generation credits or subagents.
All MIRA-R10 paths RELEASED; finished. No automatic later-roster pickup.

## Historical MIRA-GEN — superseded by Mo's MIRA-R10; do not resume generation

Mo/Claude requests a third Mira: keep r09 face/body/outfit and use image-to-3D
mainly for finer, voluminous wavy hair. Mira-sol stays read-only; Claude owns
comparison/integration. Output scope is `Art/Models/CrewV2/Mira-gen/`, with
[brief](MIRA-3D-BRIEF.md), raw model beside hybrid, at most3 new generation jobs.

**A VERIFIED:** Blender5.2.1LTS now connects; Hyper3D ON, telemetry OFF. Default
Cube/Camera/Light scene inventoried and copied before generation. No scene geometry
changes; own temporary backup removed after failure. **B attempted, BLOCKED:**
one fullbody `generate_3d` request returned `Error: API_INSUFFICIENT_FUNDS`.
No model/job handle,0 successful jobs, no retry; credit debit not reported.
This supersedes the previous connection failure. Mo must fund the Hyper3D account
configured in Blender, or the lead configure a funded provider. Then recheck
status and resume B with fullbody; inspect raw hair before optional portrait retry.
C hybrid and D source/FBX/rig/texture/review checks remain unstarted. Details:
[blocked-attempt REPORT](../Art/Models/CrewV2/Mira-gen/REPORT.md).

r09 source/FBX SHA256 checked unchanged. No new character, raw preview or final
review sheet exists for Mira-gen; no native/visual acceptance. No subagents,
Assets/game source/Unity/git changes or commit. All reservations RELEASED;
Codex2 stopped waiting for funded generation. Do not resume old asset queues.

**Prior hand-built run interrupted at r09:**
[builder](../Art/Source/build_mira_sol.py) produced `Mira.blend`, `Mira.fbx`,
512-square face texture and8 renders in `Mira-sol/iterations/r09/` at19891tris.
Those final8 renders have not yet been reopened; independent `validation.json`
is r08 PASS (19892tris), **not r09 validation**. r09 refinements include finer
ponytail layers, seated lapels/raised collar and wider sleeve weight blending;
review sheet and REPORT were unfinished when Mo pivoted. Do not imply those
checks/deliverables exist. Original CrewRig unchanged; no native acceptance.
Mo's new verdict prefers Sol face/body, rejects thick rope hair in both entries.
Earlier CREW-STYLES-2 finishing ambiguity below was superseded by Claude's
completed composition recorded in canonical comms; do not restart it.

## CREW-STYLES-2 — Codex 2 — 2026-10-24 — PARTIAL, finishing choice pending

**Last verified B:** seven redesigned portraits saved to
[crew-styles](../Art/Source/UIv2/crew-styles/): `portrait-tess.png`,
`portrait-ines.png`, `portrait-mira.png`, `portrait-noor.png`, `portrait-ana.png`,
`portrait-rosa.png`, `portrait-tove.png`. Each reopened,1254x1254 RGB;
visually checked role outfit, hair silhouette and no lettering. Tess is
honey-ash with waves/side braid; Ines platinum twin braids/headlamp; Mira
high brown ponytail/hoop/compass/binoculars; Noor black blunt bob; Ana
chestnut top bun; Rosa dark pixie/eyebrow scar; Tove short silver hair/smile lines.
This supersedes CREW-STYLES-1 female identities except Lise. Lise plus all7
male portrait files are byte-identical to pre-task backups (SHA256 checked).
No native56px or Mo visual acceptance claimed.

**C implemented but not published:** new10-figure lineup generated and opened;
top row matches Lise/Ana/Ines/Mira/new auburn-low-bun woman Captain, with
correct full-body role clothes/accessories. The generator redrew bottom-row
pixels despite preservation instructions:712560 changed pixels below y450,
mean absolute channel difference2.911. Final project `lineup-2d.png` is STILL
THE ORIGINAL. Candidate:
`/home/mo/.codex/generated_images/01a13eac-e066-72e2-b226-f7f85c5cf5d4/exec-61a7a110-3463-4dce-91d6-8b983c365e77.png`.
Exact originals/hashes retained at `/tmp/catchline-crew-styles-2.3ETBE1/`.

**D compliance still partial:** portrait backgrounds fail uniform RGB192;
corner samples176–182 with21–29 unique colours per30px corner. They must be
cleaned before use as keyed sprites. An async question asks Mo to authorize
deterministic compositing/background cleanup because imagegen tool instructions
require explicit authorization for non-imagegen image editing. No answer yet;
no compositing performed. Next: after authorization, preserve original lineup
bottom pixels, compose generated top, flatten only authorized backgrounds,
reopen/recheck and report any conflict between unchanged old background pixels
and exact-grey requirements. Otherwise Claude can compose from the candidate
and original. Do not regenerate protected portraits or launch native apps.

Built-in imagegen only,8 calls (7individual portraits +1lineup). Prompt set:
Mo's CREW-STYLES-2 named hair/skin/age designs, role wardrobe/palette from
CREW-STYLES-1, chunky navy-outline ART108 style, left-facing shoulder bust,
flat#C0C0C0/no text. Each portrait used its old portrait for wardrobe/framing
and crew.webp for style; identities deliberately redesigned. Lineup used old
sheet + Lise/Ana/Ines/Mira portraits, top-row-only replacement/bottom unchanged
constraints (latter failed pixel comparison). No Assets/game source/git edits,
no commit, no subagents, no foreground apps. Remaining C/D above; seven
portraits delivered for lead review. Prior art/UI delivery links retained below.

## CREW-STYLES-1 — Codex 2 — 2026-10-24

Step 1 generation delivered to [crew-styles](../Art/Source/UIv2/crew-styles/):
15 individual `portrait-<name>.png` (1254x1254 RGB) and
[lineup-2d.png](../Art/Source/UIv2/crew-styles/lineup-2d.png) (1774x887 RGB).
Roster: Pim/Kofi/Lise/Dirk/Rosa/Tess fishers; Noor/Ana/Mats/Sam/Tove deckhands;
Olaf/Ines engineers; Mira navigator; male Captain. Rosa has dark curls (30s),
Ines a black pixie cut (40s), Tess a blonde braid (20s). No 3D work in this step.

A references, B individual generations, C lineup and D review performed.
Opened all16 final PNGs; inventory/decode16/16; visually checked existing
identity features, role colours/accessories and absence of lettering. Captain
framing corrected and reopened; no ART108 captain exists, so used
`Assets/Art/UI/v2-portrait-captain.png` as identity reference. Other existing
portraits each used their own ART108 reference. Identity continuity is visually
reviewed generative redraw, not pixel identity. Lineup is ten outfit variants,
women top/men bottom, Fisher/Deckhand/Engineer/Navigator/Captain columns;
it is not an exact named-roster identity sheet.

**Export compliance remains PARTIAL:** backgrounds visibly grey but pixel
samples contain tonal/noise variation (mostly177–190), not uniform RGB192.
Captain correction also failed exact-flat background. Claude must clean/mask
backgrounds before final use; do not treat these as compliant keyed sprites.
No native56px readability or Mo visual acceptance claimed. Gloves, boots and
wrench appear in lineup; portraits intentionally crop below shoulders.

Built-in imagegen used, one call per portrait plus lineup and targeted captain
framing edit. Prompt set: [assigned brief](../Art/Source/UIv2/ASSIGNMENT-CREW-STYLES.txt),
per-character identity-only references, crew.webp style reference, fixed role
palette, navy contours/cel shading/top-left light, left-facing bust, no text,
solid#C0C0C0 requested. New women were fresh designs with style-only references;
lineup used crew3d-current proportions + crew.webp + Rosa/Noor/Ines portraits.
Claude owns comparison composition/showing Mo and any subsequent steps.
No Assets/game source/git mutations, subagents or foreground apps. All owned
paths released; Codex2 idle. Older UIV2/UI024/ART012 links below retained.

## UIV2-ART — Codex 2 checkpoint — 2026-10-23 (PARTIAL)

Eight freshly generated PNGs are in `Art/Source/UIv2/generated/`: `icons-a`,
`icons-b`, `stages`, `items`, `portraits-a`, `portraits-b`, `plank-tile`, `rope-tile`.
Claude owns slicing/integration; these are **raw exports, not final compliant sheets**.
No Assets, game source, git operations, foreground apps or subagents this pass.

A references/instructions and B generation are verified. Used built-in imagegen;
all four supplied UI concept webps attached as style references on every call,
never cropped. Prompt set: supplied row-major subjects per sheet, chunky casual
mobile illustration, navy #173F57 outlines, top-left light, soft cel shading,
warm colours, no lettering/numerals, invisible regular grids, full silhouettes,
uniform #C0C0C0 background. Textures requested painted #1E4D7B horizontal planks
and tan braided horizontal rope. Targeted corrections fixed stages/table spacing
and portraits-a's left-facing direction; corrected outputs replaced raw variants.
Opened all eight outputs: counts/order18/18/6/16/9/9 verified; no written labels
observed. Warning exclamation and snowflake/anchor symbols are requested artwork.

**First unfinished step C: export compliance.** Grey backgrounds contain subtle
noise around177–189 instead of exact192. Icons1774x887, stages1536x1024,
items/portraits1254x1254. Portraits-b needs more cell padding to match portraits-a.
Plank1254x1254 and rope2172x724 must become1024x1024 and1024x128; their raw
left/right seam mean absolute RGB differences are3.53 and22.92 respectively.
Do not assume seamlessness, final cell clearance or runtime acceptance.
An asynchronous question asks Mo to authorize deterministic export processing
(background flattening, margins, exact dimensions/seams). No reply received at
checkpoint; dependent processing has not occurred. Resume C after reply, reopen
all eight final images and validate, then D final handoff. No integration ready
claim; raw source originals remain in Codex generated_images thread directory.
Reservations released while waiting; coordinate with Claude before replacing
these outputs if another owner picks up. Existing older delivery links follow.

## Previous — UI-024 paired reference HUD

Mo redirected Codex2 to literal fish.png HUD reproduction. Codex2 owns crew/right;
GPT6.1 Sol medium completed left sun/time/coins/goal and follow-up review. No active
subagent. Both sides integrated with one measured style/art/font implementation;
real crew/goal/resource state, existing pause/home/freshness/catch retained. Windows
NET010 net/orders hook integrated last; Windows owns gameplay and native scratch.
[UI024 handoff](CLI-REFERENCE-HUD-024.md), [Sol handoff](CLI-REFERENCE-HUD-024-LEFT.md),
[actual four-crew native capture](screens/ui024/native-compact-desktop.png).

Combined runtime/Editor compilation passes. Windows hidden ReferenceHudChecks
passed live state/assets/pause/type-toggle/touch-target checks and produced real
1672/1440/phone/Larger/bite/catch Canvas/world captures, inspected by Codex2.
Final recapture passed: ten native static icon/heading crops have zero RGB error
and100% pixel identity against source. Main/scratch owned sources/resources match.
[Final comparison](screens/ui024/final-precision-comparison.png). Implementation
and native delivery finished; literal live-font parity and phone fine-print
readability remain unresolved. Dynamic font is shared approximation; no whole-UI
pixel-perfect or Mo acceptance claim. No main commit/foreground app/art/water/save
changes by Codex2; Windows owns ongoing NET010/scratch/build. Sol finished/released.
UI024 scope released; own temporary backup removed after native verification.
Retain all earlier art delivery links below; do not resume old queues automatically.

## Previous — ART-022 finished approved compact motor fisher

Art commit **a709cf0** (local, not pushed); main delivery remains uncommitted.

Mo approved ART021's size review and authorized finishing; ART022 completes the
3D model at unchanged5.4×2.8m hull/2.2×4.2m conservative deck. Roof over helm only,
three sockets/optional rods, four-person layout, small stern net retained. Added
real hold opening/tub, retained independent lid, helm/wiper/roof/running lamps,
navy band, engine fittings and separate fixed net frame/rotating drum/crank.
29parts/10,164tri. [Final handoff](CLI-COMPACT-FISHER-022.md),
[finished sheet](screens/art022/Finished-review.png), [net TODO](../TODO.md).
Saved source/actual FBX vertices/materials/parents/triangles/pivots and effective
axis/socket checks pass; protected approved roof/console/lid/propeller/sockets and
hull extents unchanged. Five hold rays and lid90degree source-X opening verified
in source/FBX. Actual-mesh body slices.20/.55/.95m,.28m radius/5cm grid connect
four stations and all job approaches (1,771samples); nominal clearance also passes.
Finite vertices/triangle areas checked. Desktop/phone/top/stern/open-hold/actual
Rowboat scale renders inspected; static sampling is not native crowd acceptance.

Finished CompactFisherV1 FBX updated in main preserving current meta/GUID;
new placement JSON/meta delivered. Original Rowboat/Skiff/GUIDs unchanged. Source,
blend/review blend/FBX/manifest/checks/renders/receipt are art
`Art/Models/CompactFisher22/`; builder `Art/Source/finish_compact_fisher22.py`.
ART021 commit111b12c source/review stays immutable as approved baseline.
No gameplay selection/grid/crew/net economy/UI/water/settings changed.

First unfinished step is Codex1 native fitting/integration from the manifest:
existing5×3Skiffgrid is not a drop-in match, do not resize crew to conceal it.
Test orientation/palette/routes/rods/hold/net/travel/phone and open-hatch occupancy;
optional rods/net must not duplicate old dynamic spawns. Native roof fading remains
open. Codex1 HUD008 finished/released; no scratch/foreground apps used here. No
active subagent/process or held art scope after final delivery. No new asset queue.

## Latest — ART-019 boat/harbour detail

[ART-019 handoff](CLI-ART-019-HANDOFF.md), art commit **9bed005** (local): finished Rowboat (3,414 triangles),
Quay4m (2,058), Quay4mLadder (2,218) copied into matching main Assets paths with
existing GUID/metadata bytes preserved. Cleats, compact outer rope fenders, visible
stern coil; quay rope wraps, bolts/end-grain pads and rubbing blocks. Original
hull/deck/oar/oarlock/socket/ladder meshes unchanged; names, pivots, walking deck,
quay footprint and mapped palette retained. Sources/actual FBX and raw axes/units/
node transforms verified. No runtime/water/UI/settings edits or foreground apps.
Sources, before/after renders and receipt: art checkout `Art/Models/BoatHarbour19/`;
builder `Art/Source/polish_boat_harbour19.py`. Immutable baseline inputs prevent
repeat additions. Original GullHarbour .blend sources remain intact. Backups
`/home/mo/catchline-art19-backup/` stay until native verification.

## Maps — delivered, native acceptance pending

ART-011 working-quay/orientation delivery: **796c485**. HarbourMouth retained native
evidence: 33 meshes/30,516 triangles; positive-X beacon/quay confirmed. Source,
Unity evidence and before/after: art `Art/Models/HarbourMouth11/`, including
NIGHT-DELIVERY.md and REPORT.md. Main GUID `eb7d251de9cf754459226b050bad1631` retained.

ART-012 four-map delivery **babf585**, kelp readability correction **42289f7**:
Kelp14,140 triangles, Sandbar9,750, RockyPoint11,556, DeepChannel9,554. Closed
connected terrain, source/actual-FBX vertices/parenting/bounds/totals and513 channel
rays/map checked; broad near-surface kelp blades, connected sand shelves, coherent
rocky spur and calm deep trough. Sources/reports/renders/receipts:
`Art/Models/Locations12/<asset>/`; overview sheets unify all four. Plunder/licenses
and unrelated protected art preserved. All five maps have authored models delivered;
this is not native registration or Mo visual acceptance. Existing maps were not
changed during ART-019. Retain local waterline0/worldY−.32, identity placement;
never recenter by bounds. Unity-specific environment handedness is documented.

## Fish / gameplay / menus retained

[Fish content/math](CLI-FISH-CONTENT-REVIEW.md), [fish art](CLI-FISH-ART-HANDOFF.md):
three added species, big-fish values, squid bias, bulk bait, quiet shop foley,
catch/log layout. GPT-6.1 Sol/medium finished ten distinct models/portraits;
13,348 total triangles, source/FBX/alpha/GUID checks pass. Source compilation and
isolated state/balance tests pass; native Unity/HUD/audio still pending.
[Menu](CLI-MENU-SYSTEMS-REVIEW.md) and [harbour](CLI-HARBOUR-SYSTEMS-REVIEW.md)
reviews cover safe reset, pause/settings, secured/pending haul and overflow return.

## Codex 1 pickup / current status

[VERIFY-018](CLI-QUICK-VERIFY-018.md) last confirmed main saved ArtLibrary lacked
three new fish/portrait pairs and four newer maps. Files/hooks exist; native
import/rebuild and actual camera/input/audio review remain. The default main log
was stale; main saved shader was CoastalWater, no PTS acceptance claimed. New Fish*
check methods need their actual success markers in the Windows runner. Codex 1
owns water/scenery/runtime integration and scratch availability. No main batchmode,
no foreground preview, no main staging/commit/reset/push or dirty-work discard.

ART-019 complete; Codex 2 waiting on ART-020 design choice, reservations released.
No old queue auto-resumed. Technical checks/reference renders do not replace
native review or Mo's acceptance against original Day3.

## Codex 1 / 2026-10-24 / current art checkpoint

CREW3D-MEN + FIX-CREW3D-HAIR complete for all7 men. Final revisions/tris:
Pim hair-r05/19617; Dirk hair-r01/19617; Kofi hair-r02/19917;
Sam hair-r02/19784; Mats hair-r02/19784; Olaf hair-r02/19892;
Captain hair-r04/19658. Each folder has current source/FBX/REPORT, full review,
six-head hair review, source/actual-FBX validation and649saved scalp-band rays
with zero skin-first hits. Captain badge seated against crown, clean visor.
First4 nonhair baseline surfaces within0.634mm; Mats/Olaf exact5parts,
Captain exact4parts with documented badge-only Hat change. All current hashes
and98individual renders +14sheets checked. No native/Mo acceptance claimed.

A1 all5 maps already complete; fresh continuation audit PASS9xfootprint,
15anchors/15centreline paths/15day+15night+5top plates. No model/runtime edits.
See Art/Models/Maps/continuation-audit.{md,json,log}; focused reproducer is
Art/Source/Art108/audit_maps.py. Original GUID files unchanged; derived keys
await Unity import. Native hull sweeps/HUD/live water/M4 acceptance remain
code-owner work. Codex1 art reservations released; Codex2 women/A5/A6 untouched.
No Unity scenes/C#/git/commit/subagents. All currently assigned Codex1 art is
finished; do not rebuild completed folders on another automatic launch.

Cleanup limitation: automatic approval review rejected deleting six stray Mats
headshot PNGs under C:\Art and the verified temporary baseline backup at
C:\Users\momoy\.codex\tmp\crew-men-hair-20261024 (blocked by policy).
Both remain. Correct project renders are used; no retry/bypass was attempted.

### Codex 1 relaunch verification / 2026-10-24

Standing order complete on disk; skip all7finished men and all5finished A1 maps.
Read-only recheck PASS130SHA256 comparisons/152PNG decodes; current male
source/FBX/texture hashes,649saved hair rays each, REPORTs and both sheets agree.
All5map protected/render hashes and day/night presets current. No art rebuild,
Blender rerun, native acceptance, Unity/C#/git work or subagents this launch.
Next: Claude review/integration; no unfinished item in Codex1's assigned scope.
Assets released; Codex2 scope untouched. Preserve prior cleanup limitation above.

### Codex 1 standing-order receipt check / 2026-10-24
All assigned work remains complete. Current watchdog last-message is
`Art/Models/CrewV2/_codex1/last-message.txt`; read this on the next launch.
Fresh read-only check PASS130 SHA256 comparisons/152 PNG decodes; all7 men
including hair fixes and all5 A1 three-ground/day-night maps preserved.
No asset changes or fresh Blender/native acceptance. No unfinished Codex1
art item; Claude review/integration remains. All asset reservations released.

### Codex 2 / 2026-10-24 / women complete; PropsV2 active
All eight women and unlocked Mira hair work complete. Current revisions/tris:
Lise hair-r02/19948; Tess hair-r03/19948; Ines hair-r01/18791;
Noor hair-r01/19949; Ana r04/19949; Rosa r04/19949; Tove r03/19949;
CaptainF r02/19059; Mira r26/19940 (r20 immutable archive retained).
Each current source/FBX/REPORT/full sheet/six-head sheet/validation/hit list
is present; saved source+actualFBX rig/actions/44poses pass;396rays each
with zero scalp-first hits. All current delivery hashes independently checked.
Mo/native acceptance remains pending. Female sources and asset paths released.
Codex2 now owns only new PropsV2 outputs/helpers/runtime folder and diary/handoff
append: A5 then only ART-PLAN A6 named pieces. StationsV1/Art108/men/maps/runtime
code read-only. Resume precise latest comms checkpoint; no roster rebuild.
### Codex 1 / 2026-10-24 / SeaV2 B verified, C active
Approved CODEX1-MAPS-V2 replaces old A1. Men/hair remain complete/skipped.
Harbour mouth DONE25596tri,220x160m,3zones,7terrain slices,28buoys;
61checks + actual-FBX <=0.1mm + all11current images individually opened.
New runtime SeaV2 FBX/navigation published; SeaV2-REPORT/receipts in map folder.
C Kelp review/audit/publish next; D Sandbar/E Rocky/F Deep built preliminary
PASS, still unreviewed/unpublished. See latest comms for exact state.
Only new SeaV2 outputs/helpers held; no legacy/Codex2/runtime code changes.

Codex1 SeaV2 checkpoint: B Harbour/C Kelp/D Sandbar done and published (61/45/37checks,33images opened). E Rocky rendered/audit49PASS, individual review next; F Deep rendering. New SeaV2 only; all legacy files preserved. Latest comms is canonical.

### Codex 2 / 2026-10-24 / standing-order art complete
Hair UPDATE16:55, all8women and Mira r26 complete; prior roster table above is current.
Fresh37female delivery +5immutable Mira r20archive hashes PASS. Preserve complete folders.
A5 all4 and A6 all10 now DONE; exact revisions/counts/runtime paths/pivots in
`Art/Models/PropsV2/delivery-index.json`; consolidated `REPORT.md` and `overview.png`.
Final source+actual-runtime-FBX enhanced audits PASS1483checks,15582tri/142parts;
every vertex both directions/part origin/material/scale/bounds checked. Standalone
integrity PASS315SHA comparisons/108PNG decodes, including77individual views;
all individual views/context reviews previously opened, consolidated overview opened.
Two effects PNG+SVG with alpha/restraint checks; all protected references unchanged.
New runtime copies only `Assets/Art/Models/PropsV2/`. Native import/material/lamp/
placement/event behaviour and Mo acceptance remain Claude/code-owner integration.
Six own temporary backup dirs removed after verification; art iterations/r20 retained.
No Unity scenes/C#/git/commit/subagents. All Codex2 paths RELEASED, no worker running.
Watchdog pickup: `Art/Models/CrewV2/_codex2/last-message.txt`. Nothing unfinished in
current Codex2 standing order; preserve completed art on automatic relaunch. Do not
restart historical queues or invent events. Claude commits. Codex1 scope untouched.
