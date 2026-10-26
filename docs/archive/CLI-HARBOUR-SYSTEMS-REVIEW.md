# CLI haul and harbour systems pass — 2026-10-16

Bounded source implementation complete; native compilation, input and visual review remain with Windows. This supersedes the three open findings in [the menu review](CLI-MENU-SYSTEMS-REVIEW.md). Supplied cream/navy components, artwork and existing rules are retained. Asset production remains paused.

## Actual changes

Runtime edits are limited to `Assets/Scripts/Game/VoyageHud.cs` and `VoyageHaul.cs`. Documentation: this new review, the CLI checkpoint, and appended canonical `comms.md` entries. No Editor test file was added. Exact dirty input versions, SHA256 receipts, per-pass diffs and static results are in `/home/mo/catchline-harbour-backup-20261016/`; retain until Windows native verification, then remove temporary backups.

- **Reset:** Market's second, unsafe New Game control and its armed state are removed. Only the title's existing explicit consequence warning, Cancel and erase action remain. This pass does not edit menus or reset/save rules.
- **Haul:** the hold panel now separates stowed count and **Secured · N coins now** from **Needs space: N · ~X coins**, covering deck and carried fish. Pending value is the difference between the combined quote and secured quote, so contract completion bonuses are counted once. “Now” is a current estimate: travel/freshness can still lower arrival value. The existing freshness helper is visible: countdown until depreciation, oldest percentage/rate, minimum, or iced/full value.
- **Departure:** both H and Head home request the same protected choice when deck/carried fish exceed remaining cooler space. The modal states the exact number lost, no earnings for them, and offers **Keep fishing** or **Head home · leave N fish**. Escape cancels; Enter/numpad Enter confirms. H/Space/pointer strikes cannot bypass the modal. The existing pause flag freezes simulation while choosing. No-overflow departure remains immediate. `HeadHome()` and automation calls, capacity, fish disposal order, payout and progression are untouched.
- **Harbour:** shared safe-area widths replace the fixed left reservation. Narrow shops use three tabs on the first row, two on the second, and vertically stacked purchase cards; artwork and scroll areas remain. Existing purchases now say Buy/Hire/Refit and show shortfall, prerequisite, owned, crew-full or contract-full states. Blocked shop buttons disable interaction and restore GUI state afterwards. Sale, fishing-ground and sail controls have separate vertical bounds on compact phones. Net controls are bounded beside the central cast/strike panels rather than overlapping them.

## Checks actually performed

Tree-sitter parsed all **26 current runtime C# sources**, with zero syntax errors. Scoped `git diff --check` passed; exact dirty backups and diffs were checked. Traced pickup/removal, carry/stow, `HeadHome`, `Tick(0)`, sale quotation and shop eligibility. Quotes clone state; the HUD does not sell fish. Impeccable context/guidance loaded; detector exited 0 with no output, which provides no Unity visual assurance.

Safe-area rectangle arithmetic at 1440×900, 844×390, 640×360 and inset-safe 608×340 gives positive shop scroll heights of 500/296/242/242 logical units. Narrow phone sale ends y332, fishing-ground action starts y344; net/centre controls have at least 12 units horizontal separation. Font wrapping, scaled touch sizes and actual rendering remain unverified.

Windows concurrently changed ArtLibrary, CoastalWater, VoyageGame and VoyageScenery relative to the initial protected-source hashes. This pass did not write those files or roll anything back. No foreground apps, Unity/Blender/player, scratch project, check.ps1, native compiler or main git mutations were used.

## Focused Windows regression after the water study

Use an isolated/session-only state and disposable persistence fixtures, never Mo's save. Compile the current combined dirty sources first; the previous menu-only compile does not validate this pass.

1. **Return protection:** seed capacity10, cooler8, carried2 and deck3. Expect exactly3 lost; wait real frames with the modal open and verify SimTime, fish, food and quote stay stable. Cancel by touch/Escape with no loss or accidental strike/bait use. Reopen via H/touch; repeated H must not confirm. Confirm separately by touch/Enter/numpad Enter: cooler10, three discarded, normal return. Also cover empty/exact-fit, full cooler, capacities16/40, claimed deck fish and pickup transition without double counting. Automation must retain its original route.
2. **Value/freshness/sale:** compare displayed secured quote to cooler-only quote and pending increment to combined-minus-secured. Exercise a pending fish completing a contract and an already-secured completion: one bonus only, no quotation mutations. Check grace boundary at59/60 seconds,120 seconds, minimum freshness and ice. Return and explicitly sell once; repeat pays nothing. Market has no reset; title reset still cancels safely.
3. **Purchases:** test zero/exact coins, shortfall, owned upgrade, missing prerequisite, crew full, contracts full, refit goal unmet, full food and locked chart. Disabled actions must change nothing; enabled actions retain existing fees, Save/Sync and selections. Free scraps remain unlimited.
4. **Native UI/input:** inspect every tab and scroll purchase row at all three device sizes, Small/Normal/Large text, nonzero safe-area offsets, long names and current artwork. Check both tab rows/close, sale versus departure hit regions, modal keyboard focus and touch release without click-through. Exercise rowboat/skiff strike, cast choice, net, reward and hints together. If captures require foreground, defer them and report pending.

## Remaining limits

`VoyageFeedback.cs:72` still places the skiff reward at y410 with height174 in a compact 480-high viewport; clipping risk is outside this pass's ownership. Windows should check reward/guide stacking alongside these controls. No new gameplay decision is required for this implementation. Source checks do not establish native correctness or Mo's visual acceptance; stop this CLI queue here.
