"""Consolidate the completed manual review; keep every PNG linked directly."""
from pathlib import Path

root = Path(__file__).resolve().parent
report = root.parents[1] / 'reports/POLISH-SWEEP-1.md'
body = """# Playable slice: native polish sweep

Codex 1 (Windows app), 2026-10-25. **Capture and defect-report delivery complete.** All **204 native PNGs** were opened individually at 1440x900 and 844x390, then bound by dimensions/SHA256 in [visual-review.json](../screens/polish-sweep/visual-review.json). Four visual defects remain for Claude. No blocker was established in this staged coverage; this does not establish bug-free play or player acceptance. No production fixes, git operations or player-save access were performed.

Coverage and actual results:

| Brief section | Evidence and result |
|---|---|
| P1 New game | Section 1: title, three intro moments, first harbour; 10 PNGs, native exit 0. Title is the isolated test tier chooser, not production persistence flow. |
| P2 Harbour | Section 2: hulls 0-4 harbour and all five tabs, seven chart pins, signs/bubbles and visiting skiff; 62 PNGs, exit 0. Section 6 adds all five hull refit selections, 10 PNGs, exit 0. The current Boatyard equivalent is Gear/Chandlery. |
| P3 Leaving/arrivals | Section 3: departure lane, trip chart, sea entry and seven map arrivals; 20 PNGs, exit 0. |
| P4 Fishing | Section 4 original rod/net/cage/gutting/sort/full-hold set: 32 PNGs, exit 0. Section 9 recaptures all 32 against the newer source snapshot, exit 0. Section 11 adds walking/carrying: four PNGs, exit 0. |
| P5 Home/sale/reload | Section 5: home sea/chart/lane, crates, market before/after, reload; 14 PNGs, exit 0. Production sell action changes 10,000 to 10,252 coins; explicit preview-file save/load retains 10,252. |
| P6 Phone | Section 8 shop-fix comparisons: four PNGs, exit 0. Section 10 current title/harbour/crew/chart/home/arrival/shop comparisons: 16 PNGs, exit 0. Sections 9-11 query production raycasters for 149 control instances. Full-frame phone captures have no hardware notch. |

The section-7 crew fixture failed during staging before any PNG (exit 22). It is retained as fixture failure, not a product defect. Corrected section 11 confirms `Walking=True, hands=0` and `Walking=True, hands=3` in [crew-state.txt](../screens/polish-sweep/section-11/crew-state.txt). The latter shows fish held by the walking worker at the left side of the forward deck. These frozen frames and state logs do not establish animation/touch acceptance or stress-test the whole scheduler.

Outstanding defects, sorted by severity (no blocker; all four ugly):

| ID | Severity | Screen / native evidence | Concrete symptom and location |
|---|---|---|---|
| PS-08 | ugly | Gut board: [desktop](../screens/polish-sweep/section-9/9-gut-board-1440.png), [phone](../screens/polish-sweep/section-9/9-gut-board-844.png) | A cream rail crosses the fish belly/cutting area and wooden rails cross the board: desktop x532-1030,y486-505; phone x340-544,y211-221. Still visible in the refreshed capture. |
| PS-09 | ugly | Head home from staged sorting: [desktop](../screens/polish-sweep/section-9/9-sort-home-1440.png), [phone](../screens/polish-sweep/section-9/9-sort-home-844.png) | The staged keep/throw instruction remains after those buttons disappear and masks the homeward header/coins: desktop x137-1300,y24-96; phone x40-802,y17-60. The fixture explicitly creates this production Toast text before invoking Keep and HeadHome; manual natural-play frequency is unverified. |
| PS-10 | ugly | Crew rail after Leave: [desktop](../screens/polish-sweep/section-9/9-gut-leave-1440.png) | Sam/Mira/Tess statuses wrap `overboard` beyond the cream card bottoms: x1145,y281-292/389-400/497-509. Short statuses in the larger seven-person rail fit; this is the long-status five-person layout. |
| PS-15 | ugly | Buoy fisher Owned card/detail: [desktop](../screens/polish-sweep/section-6/6-h4-boatyard-1440.png), [phone](../screens/polish-sweep/section-6/6-h4-boatyard-844.png) | Higher-hull Owned/refit cards use the small outboard-skiff illustration, including the Buoy fisher: desktop card x1100-1300,y273-397 and selected detail x50-202,y626-731. Current `VoyageInterfaceShop` Product("refit",...) still supplies icon-skiff. |

Earlier findings and corrections:

| ID | Status | Evidence / reason |
|---|---|---|
| PS-01 | Visually fixed | Known Mackerel now shows 13.0/kg on [current phone market](../screens/polish-sweep/section-10/10-market-844.png). [Original phone](../screens/polish-sweep/section-2/2-h0-Market-844.png) retained. Current phone undiscovered entries intentionally omit price. |
| PS-02 | Visually fixed | Rod holder explanation now displays its complete two lines in [current phone Gear](../screens/polish-sweep/section-10/10-rod-holder-844.png); [original](../screens/polish-sweep/section-2/2-h0-Chandlery-844.png) retained. |
| PS-05 | Lead-reported fixed; exact traffic retest not performed | Claude reports hidden-building bubble suppression. [Original visiting-skiff view](../screens/polish-sweep/section-2/2-traffic-basin-1440.png) had bubbles clamped into a column at x440,y597-724. [Current normal harbour](../screens/polish-sweep/section-10/10-harbour-1440.png) shows labels only over visible shops, but is not a repeat of that exact traffic camera. Historical severity nit. |
| PS-06 | Visually fixed | Mira now uses an illustrated portrait in [current crew rail](../screens/polish-sweep/section-9/9-gut-leave-1440.png) and [Crew office](../screens/polish-sweep/section-10/10-crew-office-844.png). Historical severity nit. |
| PS-07 | Visually fixed | [Current Kelp-bank phone arrival](../screens/polish-sweep/section-10/10-map1-844.png) has one labelled idle Fish bubble; the other three use rod icons. Compare [original crowded labels](../screens/polish-sweep/section-3/3-map1-arrival-844.png). |
| PS-03/04/11/12/13/14 | **Withdrawn** | These inferred undersized touch targets from Button artwork rectangles, omitting invisible child /hit Images. That evidence cannot support a touch-size defect. Do not retain the earlier claims as current defects. |

Keep: tactile cream/navy/orange panels, illustrated gear and crew portraits, selected-card borders/checks, large coin totals, legible intro captions, seven named chart pins and complete Wreck-bank 980-price label. Cooler panels and the distinct departure/trip hierarchy fit both sizes. Visiting skiff, quay props and signs give the harbour life. Current phone bottom tabs have readable labels.

Keep also: clear rod instructions and catch card; roller/net and crab-board silhouettes; clean versus ragged cut feedback; Leave removing gut controls; large Keep/Throw choices disappearing on HeadHome; readable hold/fuel/worm totals and full-hold feedback. Crew walking/carrying is visible and corroborated by fixture state. Sale feedback shows the exact +252 balance change. [Preview reload check](../screens/polish-sweep/section-5/preview-reload-check.txt) confirms 10,252 after reload. Reloading transient LastSale display is not treated as a persistence defect.

Phone hit-area evidence: [section 9](../screens/polish-sweep/section-9/effective-hit-samples.csv), [section 10](../screens/polish-sweep/section-10/effective-hit-samples.csv), [section 11](../screens/polish-sweep/section-11/effective-hit-samples.csv), consolidated [summary](../screens/polish-sweep/effective-hit-summary.json). The fixture includes active child raycast graphics, screen clipping and ancestor RectMask2D clipping, then calls the production EventSystem.RaycastAll without dispatching input. It samples 81 points over a 44-pixel square centred on the union bounds, at reported DPI 144 and canvas scale .813. **146/149 control instances route all 81 samples to the intended Button**, including Pause, Reel in, Leave and Crew Deploy despite smaller artwork. Three exceptions are retained, not hidden:

- Sorting rod/0: 0/81 at the union centre, covered by the catch card in that staged frame; not evidence of a small target.
- Chart pin/2: 72/81 at the union centre of its pin-plus-label shape; the enclosing bounds are 149.5x98.31. This centre sample does not establish the largest usable square elsewhere in that shape or prove a size defect.
- Gear refit/select: 63/81 on the partially visible next-row card at the scroll-mask edge; clipped bounds 153.85x40.63, artwork 153.85x121.88. The card is intentionally partially offscreen and can be scrolled; no global card-size failure inferred.

Raw [phone-artwork-under44.csv](../screens/polish-sweep/phone-artwork-under44.csv) is explicitly artwork-only. The routed sample is more informative but is not an exhaustive shape/overlap proof, a physical high-DPI-device check or a manual touch test. No hardware notch is emulated: some controls have 12-18px exterior margin, so device safe-area acceptance remains unverified; no observed notch-clipping claim is made.

Capture method and limits: [PolishSweepCapture.cs](../../Assets/Editor/PolishSweepCapture.cs) emits its runtime helper only into Catchline-sim, hard-checks the scratch path and SessionOnly, builds a separate native player and takes ScreenCapture frames with the real HUD. Required check.ps1 initial preparation passed; the current prepare first encountered a concurrently copied LeadShots dependency error, then passed after copying the lead's already-corrected file into scratch. Current native build passed with actual Unity exit 0. Logs remain in the evidence directory. [Native runner](../screens/polish-sweep/run-native.ps1) binds executable, assembly, level0 and all compiled Game source hashes in each section's native-run.json; each native-exit.json records the actual process result. Time is frozen for capture and simulation advanced explicitly. This is not installed-player, real-device, animation or natural-play acceptance. PlayerPrefs were not changed; only the explicit evidence-folder preview-save.json was used.

Source age is explicit in [source-age-final.json](../screens/polish-sweep/source-age-final.json): original sections 1-5 assembly A42EB992..., shop supplements 6/8 assembly 400ECF7C..., refreshed sections 9-11 assembly 8B83A3C1.... These generations are preserved separately. Later Claude changes are not silently attributed to an older build; production-source differences at handoff are recorded per file. Claude's 08:53 intro handover fix was reported after the original P1 snapshot and not recaptured here. This delivery leaves all production fixes with Claude.

Evidence validation: [evidence-check.json](../screens/polish-sweep/evidence-check.json) checks every PNG's reviewed hash/dimensions, every local report/index link, direct report coverage of every PNG and native exits (the documented section-7 fixture failure is the sole exception). [delivery-receipt.json](../screens/polish-sweep/delivery-receipt.json) binds this report, the fixture and evidence files; [receipt-readback.json](../screens/polish-sweep/receipt-readback.json) independently rereads every bound file. Hash integrity does not substitute for the recorded visual inspections.

Every native PNG opened individually (desktop and phone):

"""
index = (root / 'reviewed-index.md').read_text(encoding='utf-8')
index = index.replace('](section-', '](../screens/polish-sweep/section-')
report.write_text(body + index, encoding='utf-8')
print('Report written, 204 direct PNG links expected')
