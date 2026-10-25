# MAP7 Wreck bank — native and safety evidence

Codex 1 (Windows app), 2026-10-25. Own terrain/import/check/post-life capture work is complete; overall acceptance is **PARTIAL**. Claude integrated chart point/glyph/landmarks, water optics and WreckLife; the final build/capture includes them. The corrected(.72,.56) chart pin/title/price are readable at both sizes. Six unchanged art full-zone failures and tight life crops require lead review. See the [terrain report](../../../Art/Models/Maps/GullWreckBank/REPORT.md).

Required scratch commands (Catchline-sim only):

```powershell
powershell -File docs/tools/check.ps1 -Name map7-build -Method Catchline.EditorTools.WreckBankMapChecks.BuildNative
powershell -File docs/tools/check.ps1 -Name map7-safety -Method Catchline.EditorTools.WreckBankMapChecks.Run
powershell -File Art/Source/Art108/map7_native.ps1
powershell -File docs/tools/check.ps1 -Name map7-postlife -Method Catchline.EditorTools.WreckBankMapChecks.PostIntegration
uv run --with pillow python Art/Source/Art108/map7_finalize.py final
```

The scratch build succeeded with MAP7 TEST BUILD PASSED and actual Unity exit0: [build log](build.log), [runner](build-runner.log). The full safety run passed MAP7 CHECKS PASSED and actual exit0: [log](check-map7-safety.log), [runner](safety-runner.log), [receipt](map7-checks.json). This proves420 directed hull routes across seven maps/five hulls,21 lanes, five baseline harbour hulls, six imported anchor transforms and three complete new-ground out/anchor/normal bait-cast/home trips. The retained route timing warnings concern physical distance/one hull speed; collision/border assertions are independent.

Claude changed the chart point during that run, changing the sea entry direction. After rebuilding current Assets, a targeted follow-up passed all three new-entry lanes (minimum4.5m clearance), three additional complete bait-cast/home trips, four GannetDive and one BuoyBob components per trip: [post-integration log](check-map7-postlife.log), [runner](postlife-runner.log), [receipt](map7-postlife-checks.json), actual Unity exit0. Geometry/data/import bytes match the [original121-file source snapshot](safety-source/source-hashes.json); its compiled assembly/original fixture are preserved alongside it. The420 unchanged geometry routes were not repeated. The final verification-receipt.json is created only after all completion markers and bound hashes pass.

The native SessionOnly fixture bought the980coin chart, departed normally, reached each named ground, returned home and quit: [completion](capture-complete.txt), [native log](native.log), [build/source snapshot](native-run.json). The snapshot binds the actual executable, Assembly-CSharp, built level0 and118 compiled Game source hashes. At launch Claude's concurrent CoastalCanvas.cs, Skin.cs and VoyageInterfaceShop.cs differed from main. All five owned map runtime sources match the captured build; unrelated current-main changes are not represented as captured. Subsequent required scratch Assets mirroring removes the temporary generated .unity scene source; the built scene is retained and hash-bound. [Superseded pre-life evidence](pre-life/README.md) and [first post-life chart evidence](first-postlife-chart/README.md) are preserved separately and do not stand for final acceptance.

All ten native PNGs were opened individually at final1440×900 and844×390 sizes; [manual review](native-visual-review.json) binds their hashes and observations.

| View | Desktop | Landscape | Finding |
| --- | --- | --- | --- |
| Chart | [1440](chart-1440.png) | [844](chart-844.png) | Corrected steamer pin, full Wreck bank label and980price readable; all seven ground pins visible, no header/Harbour-mouth overlap. |
| SeaOut | [1440](sail-out-1440.png) | [844](sail-out-844.png) | Normal route/progress and boat shown; generic markers/gulls do not prove WreckLife. |
| The wreck | [1440](the-wreck-1440.png) | [844](the-wreck-844.png) | Sand shelf lower-left, cropped rusty bow/bulwark lower-right, clear hull/bubbles. Cardinal buoy heavily cropped/covered lower-right; perched gulls/funnel/mast off-frame. |
| Herring bank | [1440](herring-bank-1440.png) | [844](herring-bank-844.png) | Two low angular shelves, clear hull/bubbles. Gannets/boils visible; desktop partly behind HUD/edge, landscape clear upper-right boil and airborne birds. |
| Sand edge | [1440](sand-edge-1440.png) | [844](sand-edge-844.png) | Two angular shelves below side-on boat, clear hull/bubbles; similar terrain to Herring bank. |

HUD and bottom controls partly cover lower terrain at both sizes. The new map's actual water is now visibly greener with Claude's kind6 optics; exact rendered hex values are not asserted. Six life empties and runtime gannet/cardinal components are verified in Unity. Full cardinal buoy/perched gull presentation remains unproven by these tight crops. Time is frozen for still capture; no dive/splash/bobbing animation, touch, installed-player or caught-fish yield acceptance is claimed.

The first brief step is complete: [fresh MAP6 recapture](../map6-life-recapture/README.md) shows seals on both colony slabs, crab buoy/flag and Outer reef runtime surf. Surf's long pointed white/turquoise streaks were disclosed to Claude. MAP6 accepted terrain was preserved. No player-save reads/writes, installed build replacement, main Unity batchmode, git or watchdog marker; no subagents.

Automatic approval review blocked deletion of the temporary pre-change backup at Catchline-sim/Backups/map7-before. It remains in place; no alternative deletion mechanism was attempted. This housekeeping limit does not change the safety results.
