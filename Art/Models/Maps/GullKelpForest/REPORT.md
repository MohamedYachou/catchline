# MAP11 Kelp forest

Codex 1 technical authoring/integration delivery complete; lead review and acceptance are separate.

The 320 x 260 m sheltered green-teal bay has rooted ribbon kelp, sandy clearings, low weed-capped rocks and four old wooden mooring posts. No buildings or baked wildlife. Three low unreachable horizon rocks continue the bay rim. Shallows use 3A8F86 and deeper water 205B64.

The source is GullKelpForestSeaV2.blend; current runtime export GullKelpForestSeaV2.fbx has 71,766 triangles and 299 meshes. Four nearby kelp patches are localized for root sway; remaining kelp stays batched by 32 m cells. Independent source reopen/terrain slices/FBX reimport pass 62 checks; maximum vertex deviation is below 0.018 mm. Navigation includes eight real waterline outlines and 44 outer markers. The sand-fix audit retains the actual anchor pockets and raises surrounding connected bed to approximately 1.15 m below water. Accepted rock/post meshes and navigation bytes remain unchanged; [sand audit](sand-fix-audit.json) separates source geometry from native visibility. Native review also required sand on localized irregular clearings rather than the entire shallow sheet: 182 bed faces use house sand and 5,926 use teal. The [material audit](sand-material-audit.json) verifies all 299 meshes' vertices/faces/transforms, all empty transforms and nav bytes are exactly equal to B. The fresh source/FBX audit covers the final material export.

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
