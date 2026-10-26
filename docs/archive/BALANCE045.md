# Prep fisher balance and automation — BALANCE045

Mo approved the new Prepare priority and individual fisher Bait controls, then
confirmed captain help is available only once the actual hold weight is full.
Mo approved the green-zone Help prepare game and one chum by-product when
preparing purple, gold or red fish, preserving their weight and sale value.

- Skiff hold:40/60kg. Compact fisher:100/150kg. Prep fisher:160/240kg.
- Production Prep fisher refit: own Compact fisher, deliver100kg in one voyage,
  then pay9500coins at Chandlery. Delivery is recorded at actual docking before
  sale and persists in the save. Old saves start the new record at zero.
- Prep fisher nets:15kg base/22kg Heavy system. Existing Compact10/15kg retained.
  Both primary and optional second rig use their hull's capacity.
- Chum filters:0.5kg/6c,1kg/15c,2kg/35c. The value cap is derived from weight,
  so legacy saved10c cannot silently block the larger setting.
- Chum yields ceil(weight/0.5kg), minimum1. Reservations account for promised
  stock across both workers. Production is clipped to the outstanding target;
  a1.4kgPollock normally makes3, but makes1 if only one stock unit is missing.
- Basic work phases:0.15s take,3.5s chum or4.5s prepare,0.15s place, before
  normal crew speed/pace. Station positions and fast delivery remain intact.
- Prepare selection switches between oldest raw input and highest current sale
  value, breaking value ties by age. In-progress jobs finish their reserved fish.
- Each fisher's Crew Office Bait button opens scraps/worms/squid/chum permissions.
  Legacy crew allow all. Explicit all-off waits; forbidden bait is never consumed
  as a fallback. Deckhands baiting an assigned fisher's rod honor its policy.
  Already-baited hooks retain their bait. No crew levels were invented.
- Nets hands cover rod catches/bait during soak. Ready primary/secondary net
  preempts an uncollected fallback with normal claim release. A fish already
  carried is delivered safely first. Existing front storage is the raw input;
  prep then freezes existing quality, with no freshness restoration.
- Captain's Help prepare button is in the Prep panel. Actual full hold/free hands
  required. Up to two ordinary hands continue working on distinct reservations.
  Green hits start one short cut; misses/cancel retain raw fish. No Chef's Cut
  bonus was added. New fishing casts stop at full weight; in-water casts resolve.
- Purple corresponds to current BigRare presentation tier; BigRare, Legendary
  and Mythical preparation yields one voyage-only chum exactly once. Prepared
  state prevents repeated premiums/by-products. By-products may exceed the chum
  order target, which only limits deliberate chum production.

DayBoat factory stations, ice/fillet weight reduction, sonar/school chasing and
mechanical jams remain proposals. No DayBoat UI or economy was invented.

Verification complete for this delivery: combined `balance045-integrated` Unity
run exited0 with BALANCE045, CREW046, MODULE042, PACE036, PREP035, TIER033,
COMPACT FISHER and NET HAUL checks passing in isolated `Catchline-ui041-sim`.
Codex1 finished Codex2's handoff: fixed the capture-only background startup,
built current source in `Catchline-sim` (`balance045-handoff`, exit0), then
inspected all ten fresh native desktop1440x900/landscape844x390 captures.
Prep controls, fisher Bait entries/permissions, full-hold green-zone captain
panel and paid refit are readable/contained. No gameplay changed after the
combined suite; the other source difference is CREW046's independently checked
capture-only background flag. Main project was never batchmode-opened.

Installed the verified final combined build in `Catchline-play/Tier033`.
Existing **Catchline - Tier 4 Test** shortcut and its arguments are unchanged.
The old save-isolated Tier4 test was closed gracefully to release file locks;
reopen the shortcut to play. Real/Tier3 installations and player saves untouched.
All installed distribution files match build SHA256; receipts, native PNGs and
capture/install scripts are in `docs/screens/balance045/`. These scripted native
captures do not establish physical touch or Mo's play acceptance. No commit.