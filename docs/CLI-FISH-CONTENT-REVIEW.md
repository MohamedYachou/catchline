# Fish, bait, economy and catch UI — 2026-10-16

Mo authorized this content pass, then explicitly assigned GPT-6.1 Sol at medium
reasoning the fish models/portraits while the lead retained gameplay and math.
Implementation and background source/asset checks are complete. Native Unity
import, interactive HUD and listening review remain pending with Windows.

## Delivered gameplay

Three species join the **existing five grounds**, without new locations or
progression systems:

| Fish | Weight | Price/kg | Grounds |
|---|---:|---:|---|
| Whiting | 0.4–1.3 kg | 12 | Harbour mouth, Kelp bank |
| Red mullet | 0.6–1.6 kg | 16 | Sandbar, Rocky point |
| Turbot | 1.5–5 kg | 18 | Sandbar, Deep channel |

Pollock/bass/conger/cod prices per kg change from 8.5/12.5/5.5/7 to 10.5/15/7/9,
about 20–29% more. Herring/mackerel/plaice prices remain 17/14/15. Existing size,
freshness, market saturation, contracts and explicit-sale rules still apply.
New species also participate in the existing known-ground contract pool and log.
Species IDs 0–6 are unchanged; new IDs 7–9 append to the enum. Existing saves keep
coins/crew/haul and grow species arrays with normal market/default log values.

Squid keeps its 0.4 power bonus, now multiplies small-school table weight by .04,
favours substantial species and rolls specimens in the upper 65% of each species'
weight range. Small catches and missed strikes remain possible. Power is bounded
to 0–1.4. Unlimited scraps still roll only small herring/mackerel regardless of
premium flags. No change to crew's 80/85/90% strike rates or quiet catch/miss feedback.

Supplies adds 30 worms for 24 coins and 15 squid for 36 alongside the original 10-for10
and 5-for15. These are extra purchase options for existing bait types. The cards
show standard/bulk cost per hook, squid targets for the selected ground and clear
purchase reasons. The fishing HUD names the next bait; its condition is shared
with actual bait consumption. Use squid first remains a preference, with squid
fallback when worms are exhausted. Quiet original wood/paper/coin effects now
accompany shop selection and enabled purchase actions through the existing volume
control; blocked buttons remain silent. No recordings or audio package added.

## Catch presentation and fish art

Desktop catch cards give the model portrait a broad image area, a cream heading
on the supplied coloured header, a centred species name, weight and coin estimate.
Phone cards use the existing cream panel, a wider portrait and concise two-line
copy. The log preserves portrait aspect in wider image bounds. Catch feedback
remains nonblocking and captain-only; payout estimates still say approximate.
All ten species have distinct authored models and matching transparent portraits.
See [fish art handoff](CLI-FISH-ART-HANDOFF.md) and
[asset lineup](../Art/Models/FishPolish16/Fish-lineup.png).

## Balance evidence

Executed the actual GameData/GameState and FishContentChecks source in an isolated
Linux C# harness with small Unity math/data and System.Text.Json adapters. This
checks algorithms; it is **not Unity execution or proof of JsonUtility parity**.
12,000 samples per ground test species availability, specimen bounds, scraps and
premium outcomes. Harbour squid produced 1,928 small-school fish versus 10,512 with
worms: about 84% of squid catches were whiting. A separate 10,000-sample scenario per
ground estimates per-cast fish income after standard bait cost, using the real
basic fisher's 80% strike chance:

| Ground | Fresh worms | Fresh squid | Depressed worms | Depressed squid |
|---|---:|---:|---:|---:|
| Harbour mouth | 3.69 | 6.84 | 2.03 | 3.36 |
| Kelp bank | 9.96 | 17.18 | 6.07 | 10.03 |
| Sandbar | 17.20 | 25.81 | 10.73 | 15.58 |
| Rocky point | 18.92 | 25.57 | 11.85 | 15.43 |
| Deep channel | 29.86 | 37.42 | 18.91 | 23.07 |

Depressed means 75% market price and three-minute-old fish. This excludes crew
fees, food, fuel, capacity loss and travel/catch timing; it is not voyage profit
or a guarantee for manual players. At the deliberately severe 50% market/60%
freshness floor, harbour squid is about−0.06 versus worms+0.39 per cast. Preserve
that reason to use cheap/free bait and return promptly rather than guaranteeing
profit from every premium hook. Bulk squid improves these bait-only figures by 0.6
coins/cast; bulk worms by 0.2. Raw results: `checks/FishContent16/state-and-balance.log`.

## Files and checks

Runtime: GameData.cs, GameState.cs, DeckActors.cs, VoyageHud.cs, VoyageAudio.cs,
VoyageFeedback.cs only. Added Editor FishContentChecks.cs and FishArtChecks.cs
with metadata. Art files, sources, receipt and checks are enumerated in the linked
art handoff. Updated PRODUCT.md, docs/GAMEPLAY.md, CLI checkpoint and comms.
No VoyageGame/shared Ui/menu/travel/water/scenery/settings/save edits, scratch use,
foreground apps or main git staging/commits/resets/pushes.

Roslyn on a background Linux .NET host compiled all 26 runtime sources plus the
two new checks and existing ArtImport against installed Unity assemblies: zero
errors, one existing CS0108 warning for VoyageGame.audio. Exact dirty backups,
per-pass diffs and hashes are in `/home/mo/catchline-content-backup-20261016/`.
State checks cover old seven-species save growth, new-species unsold save roundtrip,
actual new-species quotation/sale/log credit, bulk shortfall/exact payment and bait
preference/fallback. Asset receipts verify all 20 installed FBX/PNG byte hashes and
metadata; fourteen established GUID files are preserved. Mechanical UI detector
returned[]; this is not native layout acceptance.

## Windows checks when scratch is available

1. Run `Catchline.EditorTools.FishContentChecks.Run` and
   `Catchline.EditorTools.FishArtChecks.Run` in the Windows-owned scratch check
   flow, after the water study releases it. Native JsonUtility, model/material/
   lookup/scale/axis/Tail checks must pass. Use isolated/disposable save fixtures.
2. Rerun existing MenuSystemChecks, UrgentCrewChecks, FisherFeedbackChecks and
   SalePayoutChecks with the current combined sources. Confirm new-species fish
   earn coins, explicit sale pays once, overflow modal still freezes/cancels and
   guaranteed test crew/free scraps remain intact.
3. Review captain catches for all ten species at 1440×900,844×390 and640×360 with
   Small/Normal/Large text and safe-area insets. Check whole portraits, header
   text, long names, fish-log wrapping, new bait rows, net/cast/strike separation,
   held/deck fish and tail animation. No desktop capture while Mo requires quiet.
4. Listen to selection/purchase/cast/reel/sale at normal/low/muted volume; blocked
   actions should be silent and crew catches/misses should not intrude. Re-enter
   play after Auto Refresh to avoid stale models/portrait/library caches.

Keep temporary backups until native verification, then remove them. This bounded
content and fish-art pass is delivered; original water and Mo visual acceptance
remain Windows/Mo work.
