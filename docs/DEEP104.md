# DEEP104 — Tier 5 fishing, crew setup, third rig and chum

Codex 2 (WSL CLI), 21 October 2026. Delivered and installed in Test and Real; all five launchers verified. GitHub commit/push is the remaining delivery step; latest `comms.md` records its result.

## Mo's selected rules

- Six hired crew plus captain. Fishers operate rods, nets, cages and deep lines. Deckhands collect, carry and work the existing two-place processing station.
- Management's third **Crew** page selects each worker. Fishers get independent Rods / Nets / Crab cages / Deep lines tickboxes and four permitted-bait toggles. Any combination, including all off, is saved. Ready nets/cages take priority, then bait empty deep lines, then ordinary rods. Current committed work finishes safely.
- Two standard deep-line rigs. **Third deep-line rig** costs **3,500 coins**, available on Tier 5 with no additional prerequisite; price selected under Mo's explicit discretion within the existing 1,500–5,000 upgrade range. The third uses approved 103 geometry between the starboard cage and normal rod. All deep rigs and optional normal rods are excluded in the side-net layout; ownership survives switching layouts.
- Fisher walks to a rig and commits one self-made chum portion (only if Chum is allowed). Deep lines accept **only self-made chum**; worms/squid/scraps remain normal-rod bait choices. Two seconds baiting, one second dropping, **60 seconds passive soak**, two seconds automatic raising, then **one actual fish per rod** lands for ordinary collection. Two standard rods give two fish; three upgraded rods give three. Pausing freezes the cycle. Pending deck catch prevents rebaiting that rig; no unbounded unattended production or duplicate charges.
- Deep-line class targets: **5% white, 5% green, 10% blue, 75% purple, 3% gold, 2% red**. Use the current spot's species and hull eligibility only. Missing classes redistribute their probabilities among locally available classes. Species weights within a class retain local and existing chum species weighting. Gameplay and forecasts consume the same distribution, including real class-specific specimen ranges.
- Tier 5's existing processing station remains intact and now makes chum. Consuming **one white fish yields one chum, green yields two, blue yields three**. Purple, gold and red cannot be selected or consumed for chum, including old saved all-class filters. Whole-fish yields are retained when crossing the stock target (9 + blue = 12).
- Existing chum timing and maintain-stock orders remain: 3.5 work seconds plus handling; saved targets 0/10/20, priority and independent input class filters; two places shared with preparation. Chum is per-voyage stock, discarded on return and never persisted or purchased. Existing Tier 4 preparation by-products remain unchanged. Tier 5 preparation still produces the existing 150% prepared value, separate output and separate carrying into the hold.
- Manual rods, nets and cages have no Engineer condition, faults or servicing requirement. Legacy serialized condition arrays remain compatible but do not affect work or forecasts. Already hired Engineers are preserved in saved inactive records with their contracts, freeing active berths; no Tier 5 Engineer offers or default trial Engineer.
- Astra's card/balance research stays parked. No cards, new professions, electrical machines or extra wages are introduced.

## Implementation

`DeepLineRules.cs` owns the cycle, actual local class distribution and expectation. `VoyageDeepLines.cs` owns rig geometry/anchors, worker claims, bait commitments, automatic return and retained individual specimens. Third ownership uses an additive `UpgradeId` in the existing saved `Owned` collection. The runtime third rig clones approved geometry; original 103 FBX/Blender assets are unchanged.

`GameState.cs` retains legacy fisher presets as migration input and adds saved task bits. Old fishers retain rods/cages/deep access; explicit all-off survives saving. Engineer migration preserves the original member in `InactiveEngineers`, without deleting or charging a replacement.

Net operator assignments are distinct from basket collection. Tier 5 fishers set/haul; deckhands collect. Both rigs have independent claims, timers, catches and basket backpressure. A basket pending on one rig does not discard or block the other rig's haul. Older boats retain their existing deckhand net operation.

Management retains accepted Income/Operations art and bottom-right entry, with a third Crew tab and a fourth Income method for deep lines. Rectangular native surfaces cover replaced sample content. Controls use production UGUI with touch targets. Forecasts share local rolls, bait costs, installed counts, preparation/chum timings and finite worker budgets. Chum completions count in processing work but do not create phantom outbound fish. Policy/bait/duty/upgrade/order changes invalidate estimates; hauling learning resets for effective crew changes. Income remains estimated raw nominal catch value, not guaranteed sale proceeds or a processing premium.

Leaving sea cancels unpaid approaches and active soaks without refunding already committed bait. Existing return salvage preserves landed/input/output cargo; chum expires. All preview/save checks use `Catchline-sim` or a cloned save root. Never batchmode the main project.

## Verification and reproduction

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File docs/tools/deep104-check.ps1 -Name deep104-regression -Mode Regression
powershell -NoProfile -ExecutionPolicy Bypass -File docs/tools/deep104-check.ps1 -Name deep104-build -Mode Build
powershell -NoProfile -ExecutionPolicy Bypass -File docs/tools/deep104-capture.ps1
# Run installation only after native inspection and native-review.json acceptance:
powershell -NoProfile -ExecutionPolicy Bypass -File docs/tools/deep104-install.ps1
```

Focused `Expanded` checks cover base/third clocks, actual bait use, cancellation, pause, bounded backlog, normal carrying/processing, two independent nets, full class probabilities, migration, UI controls and saves. Third worker tile is **(24,4)**; all three actual tips have **Y=3.14 m**. Worker access is clear and connected to cages, all rods, processing, rest positions, helm and hold.

Latest broad pass: `deep104-shipping-regression`, Unity exit 0, wrapper exit 0, `DEEP104 REGRESSION PASSED`. Includes 60,000 actual chum-baited deep rolls over five spots; 80×20,000 actual ordinary rod rolls; 120 net oracle comparisons; Management, processing, older boats, grade pace, class filters, both Tier 5 layouts, net games and water integration. Source compilation alone is not native acceptance.

Final evidence lives in `docs/screens/deep104/`: `regression.log`, `deep-distribution.csv`, native logs/PNGs, `native-review.json`, `real-save-probe.json`, `installed-build.json` and launcher inventories. Final capture covers standard two-rig, upgraded three-rig and side-net configurations at 1440×900 and 844×390; Crew/bait/duties/table/chum filters, native pointer hit testing and Escape. Real runs against a copy of the real save, including departure, dashboard, return and saving; actual save fingerprints must remain unchanged.

Final installation is versioned `Catchline-play/Deep104/{Test,Real}` and preserves the existing five shortcuts' exact mode flags. The current receipt, rather than older DASH087 hashes, identifies shipped files. Earlier candidates and core-only evidence are historical; latest diary/checkpoints identify acceptance and GitHub commit/push status.
