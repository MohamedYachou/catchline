# NET-010 delegated systems handoff

Owner: Codex 1 (Windows app) / net_systems. Finished source delivery; lead owns integration and native verification. No commit or scratch/Unity/foreground execution.

Changed only `Assets/Scripts/Game/VoyageNet.cs`, new `Assets/Editor/NetChoiceChecks.cs`, this document, and append-only `comms.md` entries. Original net source backed up at `%TEMP%/Catchline-NET010-VoyageNet.backup.cs`; remove after lead verifies integration.

## Integration contract

Lead provides `VoyageGame.IsNetFisher` (Hull==2), `Transform netModelRoot` populated before BuildNetKit, `State.HullDef.NetAccess`, `Grid.GetLocal(Vector2Int)`, `DeckFish.FromNetBasket`. Existing Hull0/1 retain original set/soak/haul yield and kit paths. Compact hull reuses authored NetCrank/NetDrum and skips duplicate winch/coil. RodVisual hiding remains lead ownership.

Call `TryNetWork(Person)` from Nets-priority deckhand scheduling only. It accepts deckhands idle without carried fish; never captain/fishers. It handles only Stowed->set or Ready->haul; it releases actor while soaking. Fish-collecting default never calls it. Single actor/token ownership makes canceled paths/actions restore Stowed or Ready and retains ready catch; stale callbacks after ResetNet cannot deliver. Captain SetNet/HaulNet keep their existing signatures and require Manning==null; lead must release captain rod safely before explicit net commands.

`NetBasketCount`/`NetBasketBlocked` expose landed backlog. Any existing basket fish blocks setting another cycle, including a fish claimed but still OnDeck. A full hold blocks setting but does not prevent hauling an already ready net into the empty basket. No instant stow/sale. Basket contains at most one haul (2–5), landed timestamp is SimTime. Lead must skip escape removal for FromNetBasket in TickDeckFish, preserving freshness/carry/stow behavior. Basket fish remain ordinary carry targets.

## Provisional tuning

One stationary net, 2 seconds set / 90 seconds soak / 5 seconds haul. Yield once at ready: 2/3/4/5 fish with 20/40/30/10 percent chances. Weighted by local spot table filtered to herring/mackerel/whiting/pollock; smaller 10–50 percent position in each species weight range. All current spots have an eligible local schooling fish. Future unsupported spots yield zero instead of importing nonlocal fish. No bait bonus, condition, wear, repair or offline catch. State.OnCatch depletion occurs once per generated fish when ready. Leaving/resetting discards unlanded catch under existing HeadHome behavior; lead should explain this in UI or implement an explicit departure choice in its owned scope.

## Verification

Source diff whitespace check passed. Integration dependencies are being authored concurrently, so no compile/runtime/visual acceptance claimed. Executable scratch runner `Catchline.EditorTools.NetChoiceChecks.Run` covers actor exclusivity, walking and timed-set cancellation,90-second bounded yield, zero-time soak, ready waits without growth, canceled haul retry, full-hold recovery, safe basket/no instant stow, blocked next set, no repeat delivery, and100seeds x5locations local schooling yield. Lead should execute via docs/tools/check.ps1 in Catchline-sim, alongside legacy SkiffChecks.Automation.

Remaining native acceptance: scheduler Fish collecting/Nets switching while walking/working/soaking, captain rod-release UX, timed-haul cancel and reset callback invalidation, actual basket escape exemption/carry/stow, save/reload policy, return-during-net messaging, pause integration, crew traffic and imported drum axes/net location. Tests intentionally isolate Person and TickNet via reflection rather than claim scheduler or visual verification.

## Codex 1 integrated delivery — NET-010

Lead integrated additive `Hull == 2` using ART022 at its actual5.4×2.8m size.
Unity's FBX source-X reflection is accounted for in sockets, job tiles and rest
positions; source-Z-up conversion is retained once. The new.1m deck grid samples
the imported mesh at.20/.55/.95m with.28m body clearance and reserves the hatch
opening and low stern basket.393walkable cells connect every job/rest pair.
The lid opens upward around its source-X hinge; the propeller uses source Y,
net drum/crank source X. Static display rods are hidden; three functional rods
cast out over their own gunwale. Older hull IDs/geometry/net rules remain.

Fish duty handles rod catches/bait and deliberately leaves the net basket alone.
Nets duty sets/hauls/unloads the basket and leaves rod catches to the captain or
other hands. Both carry any already held fish to the hold before changing job.
Preference is saved per deckhand; older saves default to Fish. A single hold
worker prevents simultaneous stow actions. The captain can cover unclaimed fish
or leave an idle waiting rod for net work; a failed net command preserves the
previous rod state. Active cast/reel/timed work must finish first. Leaving with
a deployed/ready net prompts before abandoning the soak/catch.

The isolated preview's Chandlery has **Compact fisher · trial / Try net boat**.
It provides at least200trial coins,20fuel and full provisions; hire any three
crew at the Crew Office. No final boat price, early-tier tutorial or tier1/2
production economy is asserted. Main saves receive no trial grant. Existing
saved Hull0/1 IDs are unchanged, new hull/duty save round trips pass. The
resource ArtLibrary is refreshed from the verified scratch-generated library;
check.ps1 now carries the new reference HUD Resources dependency too.

Compact-only handling starts at1.4s pickup/3s stow plus walking. In the fixed
120s novice two-fisher + captain trace,18fish landed/18held, peak deck queue4,
no lost fish and hand88%active. This is an initial fixture, not broad final
balance or a claim that every map/grade has identical throughput. Net yield,
wear/repair and earlier economy still need playtesting before final progression.

Verification to date: full FirstVoyageChecks.Regression passed with existing
skiff/automation/crew/market/contracts/water/menu/native UI suites plus new
CompactFisherChecks, NetChoiceChecks and ReferenceHudChecks. Focused native
checks additionally passed upward lid/propeller axis,4-person return/relaunch,
captain carry, actual set/haul/order controls, saved IDs/default duty, full-hold
failed-action preservation, all-deckhand/all-fisher mixes, actor/token cancel,
ready waiting, full-hold haul, safe basket and100seeds×5local catch tables.
Desktop1440×900 and landscape phone844×390 actual Canvas+world captures in
`docs/screens/net010`; reference HUD evidence belongs to Codex2/UI024.
No foreground player launched, no real-save changes, no main batchmode.

Final basket-prompt aggregation/reference alignment capture and refreshed
preview build passed in `check-net010-delivery.log` (exit0). The user then
explicitly requested launch; preview process3440 started. Final evidence is in
`docs/screens/net010/verification.txt` and the adjacent native captures. Own
temporary backups removed after verification. All source remains uncommitted
alongside existing WIP. Windows owns mechanics; Codex2 owns its reference HUD.
