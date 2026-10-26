# JIG-BOAT-WIRE-1 integration evidence

Codex 1 (Windows app), 2026-10-26. Technical delivery complete; ten native frames reviewed and pacing measured. No commit: Claude owns review/publication.

## Implementation

Saved IDs remain append-only: 0 Rowboat, 1 Skiff, 2 Compact, 3 Prep, 4 Buoy, 5 Jig. `HullTier` maps IDs to 0/1/2/4/5/3. CardTier equals Tier. Old Prep/Buoy saves retain their model and progression; scratch save round-trips verify this without accessing the player save.

Compact refits to Jig for 6,500 with no haul gate; Jig refits to Prep for 9,500 with the existing 100 kg best-voyage goal; Prep refits to Buoy for 18,000. The chandlery, savings goal, harbour progression, species/crew gates, net/prep/deep-line eligibility now follow tier order. Claude's current 500-coin/5-kg Skiff goal and 5/8-kg rowboat hold changes are preserved.

The measured Jig hull has 130 kg capacity, five card berths, three rods/reels, one net and no preparation station or second net. Native FBX measurement is in native-measure.txt. Grid61x25 at0.1m; physical body-clearance raster at0.20/0.55/0.95m retains cabin, hatch, gunwale and equipment obstacles. The station graph copies that raster. Sorting access49,9; net54,9; captain23,12; hold access36,5; rest28,5 /45,12 /24,21 /45,20 /53,12; rod work29,20 /41,20 /52,20. All sockets are unblocked and every pair has a real runtime path.

Eight bulb meshes share a separately owned emissive material. Accepted JigLampGlow uses the existing additive vertex-alpha shader with no shadow/depth writes; pool follows actual sea-plane height. Effects enable at dusk, on night voyages and while anchored at a fishing ground; daylight harbour is off. The existing dusk-light transition now also follows NightVoyage at sea. Temporary materials are destroyed with the boat.

COMPARISONS.md lists old/current comparison lines; current-comparison.diff provides complete surrounding context. Source art was copied, never modified. Own pre-Jig and resume baselines remain in Catchline-sim/Backups: cleanup command was rejected by automatic approval policy. No peer files/backups changed.

## Verification status

- VERIFIED focused scratch runtime: tier/card mapping for all six IDs, prices/atomic affordability/haul/fuel, old ID3/4 saves, coast gates, real raster socket connectivity,130kg/five berths/three rods/one net/no prep, lamp state, actual Deep channel out/anchor/bait/cast/home and all six trip legs.
- VERIFIED full regression: abilities286, tutorial217, M2/bite/cage,792 directed hull routes across six hulls/eleven maps;33 sea lanes and all existing harbour trips plus Jig Deep channel trip. Detailed timing warnings retained in log.
- VERIFIED latest focused rerun includes the runtime hatch edge hinge and real sea-night lighting; native build succeeded398810936bytes/errors0. Additional explicit bulb/glow binding checks accompany the recapture build.
- VERIFIED final player capture: all10frames individually opened (visual-review.json); real refit, deployed crew, Deep channel out/anchor/cast/home completed. Existing EndCaptainFishing restores the deck for work/night frames. Warm lamp spill and sea pool visible at night; phone bulbs remain small/subtle. Desktop selected refit grid card is below fold but selected detail/art/price remain readable.
- VERIFIED pacing2400runs/432000days, all accounting/restoration checks PASS. HULL-PACING.md reports every hull day for each profile/price. Baseline chest-spending policy keeps all600runs on Skiff; this conditional result is recorded, not hidden or corrected by economy changes. Full generated report, CSV and source hashes retained.

## Lead-owned follow-up

CrewRecruit's legacy tier3 text override still says prep fisher. Only the TierBoat lookup was released; QUESTION is logged for Claude to remove the override in held UI. Existing Prep/Buoy shop copy says four/six hired crew despite six/eight current berth caps; preserved for lead review.

This report distinguishes scratch technical checks from native visual review and Mo's player acceptance. No installed player or shortcut changed; no player save read or written by the fixtures.
