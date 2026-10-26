# MAP11 Kelp forest

Codex 1 technical authoring/integration delivery complete; lead review and acceptance are separate.

The 320 x 260 m sheltered green-teal bay has rooted ribbon kelp, sandy clearings, low weed-capped rocks and four old wooden mooring posts. No buildings or baked wildlife. Three low unreachable horizon rocks continue the bay rim. Shallows use 3A8F86 and deeper water 205B64.

The source is GullKelpForestSeaV2.blend; accepted baseline export had 71,766 triangles and 299 meshes; the current sand-edge source export GullKelpForestSeaV2.fbx has 73,242 triangles and the same 299 meshes (see Sand edges below; Unity reimport pending). Four nearby kelp patches are localized for root sway; remaining kelp stays batched by 32 m cells. Independent source reopen/terrain slices/FBX reimport pass 62 checks; maximum vertex deviation is below 0.018 mm. Navigation includes eight real waterline outlines and 44 outer markers. The sand-fix audit retains the actual anchor pockets and raises surrounding connected bed to approximately 1.15 m below water. Accepted rock/post meshes and navigation bytes remain unchanged; [sand audit](sand-fix-audit.json) separates source geometry from native visibility. Native review also required sand on localized irregular clearings rather than the entire shallow sheet: 182 bed faces use house sand and 5,926 use teal. The [material audit](sand-material-audit.json) verifies all 299 meshes' vertices/faces/transforms, all empty transforms and nav bytes are exactly equal to B. The fresh source/FBX audit covers the final material export.

The raw broad-circle audit retains two post-line failures because four narrow foreground posts intersect the 13 m fishing circle. The scoped audit excludes only these posts from that broad-circle test and retains them in every real route and anchor clearance check. Inner post centres are 5.42 m from the anchor; actual obstacle clearance exceeds 4 m. Claude 2 accepted this specific exception at 08:45 on 2026-10-26. No coastline or route failure is waived.

| Life empty | World X | World Y | World Z |
|---|---:|---:|---:|
| KelpSway_1 | -90.816 | -0.320 | -27.590 |
| KelpSway_2 | -82.625 | -0.320 | -33.325 |
| KelpSway_3 | 3.194 | -0.320 | 29.101 |
| KelpSway_4 | 78.364 | -0.320 | -24.016 |
| OtterRaft_1 | -92.000 | -0.320 | -22.000 |
| PostGulls_1 | 79.601 | 1.280 | -24.516 |
| PostGulls_2 | 87.301 | 1.280 | -29.908 |

KelpSway anchors are at water level in foliage patches; OtterRaft is open water. PostGulls are on actual post caps, checked with independent downward rays. Orange markers are review aids only, absent from export. VoyageKelpLife.cs now binds four localized clusters with 4/5/6/7-second periods and rotation below two degrees, four existing post gulls, and Codex 2's static OtterRaft.fbx (two adults and one pup on kelp), imported byte-for-byte with gentle bob and owned two-sided materials. The fallback remains available but is not used in this delivery. Individual SeaOtter animation clips are outside this integration.

Existing-species substitutions: wrasse and gurnard use RedMullet; lobster uses Crab; garfish uses Herring; john dory uses Turbot. Other weights follow the brief. RowSeconds 28, BiteWait 1.4, chart 36,000 coins, spot index 10, exact requested blurb retained. Claude initially supplied chart point (.55,.12); COASTS-2 now uses (.216,.278) on the Outer coast page, retaining glyph15. Chart source remains his.

Blender water is a preview. The original ten native images are preserved as the rejected sand-read baseline. MAP11-FIX-AND-LIFE-1 adds native comparisons and life evidence at 1440x900 and 844x390 in the linked continuation. Production water shader is unchanged: only this active map's material receives green-teal scattering and depth absorption (.86,.84,.74). An initial (.91,.94,.89) transmission pass made the bed look dry; its failed visual evidence is preserved under fix/first-optics-pass. Final visual findings and review limits are recorded in fix/README.md. The post exception is accepted; final sand/life review belongs to Claude.

COASTS-2 lead update (08:07): chart price 36,000 and Prep fisher gate supersede the original brief. Original full eleven-map test/build passed660routes/33lanes/fiveharbour hulltrips/three new-ground trips. Current-economy recheck passed60affected MAP11routes/all33lanes/fiveharbour hulltrips/three new-ground trips,36000purchase and Hull>=3gate;build/Unity/native exits0. Full integration regression passed286ability/217tutorial plusM2/bite/cage. The other600routes retain baseline proof; no navigation changes intervened.

The requested species weights describe the authored base ground pools. Claude's COASTS-2 runtime shaping adds the Outer coast extras from Coasts.cs; that economy/fish shaping is lead-owned.

Continuation checks pass 60 MAP11 routes, all 33 lanes, five harbour hull roundtrips and three out/anchor/bait-cast/home trips. The route receipt predates the optional otter swap and explicitly records the fallback; subsequent LifeAndBuild checks verify the delivered raft and final optics on unchanged navigation/terrain geometry. Full integration regression passes including 286 ability and 217 tutorial assertions. Native capture also measures actual movement of all four clusters over 1.25 real seconds with gameplay frozen. This does not establish player approval of timing, installed-player or physical touch acceptance.

Complete native/check/provenance receipts and image links: [sand fix](../../../../docs/screens/map11-kelp-forest-1/fix/README.md), [life](../../../../docs/screens/kelp-life-1/README.md), [preserved baseline](../../../../docs/screens/map11-kelp-forest-1/README.md). No git mutations/commit, player-save or main Unity batchmode operations. Technical work is prepared for Claude review.

Final continuation imports the delivered KELP-RIBBON-FIX raft byte-for-byte, retaining its dark-olive colours. All 14 native frames and eight comparison pairs were individually opened; warm localized sand and rooted kelp read at both sizes. Ordinary-camera raft HUD occlusion and small/partly label-covered phone supplementary raft remain explicit review limits. See fix/visual-review.json for final image and imported-raft hashes.

## Sand edges

MAP11-SAND-EDGES-ART-1 — Codex 2 (WSL CLI), 2026-10-26. Only ConnectedBathymetry geometry and its sand/transition material assignments changed. Each of the three clearings now uses a rounded irregular 24-segment outline, with two inward radial bands of 0.32 m each. Their colours mix the existing sand and seabed at sand factors 0.67 and 0.33; the sand interior and surrounding teal retain the existing materials. Original triangle planes preserve the raised bed, anchor pockets and heights. No navigation data changed.

Independent accepted/new source reopen and actual-FBX import [audit](SeaV2-sand-edges-audit.json) passes: all 306 other objects (298 meshes and eight empties) match exactly, including geometry, materials, transforms and hierarchy. All 299 exported mesh bounds match. Units remain 1.0 and navigation SHA-256 remains `a09a0d874be264850a158b883d347a50a61cddf51ccee3535767cf522e26aa76`. Bidirectional surface deviation maxima are 0.000007634 m and 0.000003815 m; source-to-FBX maximum vertex deviation is 0.000017643 m. The audit contains the complete mesh bounds and anchor matrix tables.

Triangle accounting: 71,766 accepted baseline → 73,242 current export (+1,476, +2.06%). ConnectedBathymetry is 12,298 → 13,774; all other meshes retain their counts. The inherited REPORT gives an actual count, not a separate numerical cap. The working check used 75,000 as a conservative ceiling; this is not a claim that the lead specified that budget.

| Clearing | Centroid shift (m) | Maximum bounds shift (m) | Old/new area (m²) | Boundary Hausdorff (m) |
|---|---:|---:|---:|---:|
| 1 | 0.450 | 0.000 | 196.56 / 211.79 | 1.891 |
| 2 | 0.329 | 0.350 | 249.21 / 254.05 | 1.797 |
| 3 | 0.085 | 0.000 | 193.05 / 181.64 | 1.396 |

Footprint interpretation: the ±0.5 m check applies to bounding extents and centroid position. It does **not** hold for every old staircase boundary point: rounding the deep notches moves individual boundary points by the Hausdorff distances above (1.396–1.891 m). This interpretation and the missing explicit numerical budget were recorded as QUESTION/checkpoint lines for the lead; pointwise footprint compliance is not claimed.

Evidence: [12 old/new comparison pairs](SeaV2-sand-edges-comparisons.json), [visual review](SeaV2-sand-edges-visual-review.json), and [delivery receipt](SeaV2-sand-edges-receipt.json). All 24 captures and 12 unscaled side-by-side sheets were opened individually: three grounds × top/deck45 × 1440×900/844×390. The irregular outlines and narrow two-step transitions read at both sizes, with fixed kelp/posts and no visible holes. These are direct Blender surface inspections without water, boat or HUD, framed to show the full clearing; they do not reproduce native water optics or establish native gameplay acceptance. Claude owns Unity reimport and runtime review. Older audits/native images linked above describe the historical baseline, not this new export.

Reproducible helpers and accepted geometry snapshot live in Art/Source/Maps/GullKelpForest/. The accepted binary backup was temporary and removed after successful audit and evidence checks; rerunning the old-source Blender comparison requires restoring the accepted baseline into the documented scratch location. The JSON snapshot is retained as the exact geometry audit fixture. No Unity, Assets, .meta, C#, git or player-save changes; no commit.
