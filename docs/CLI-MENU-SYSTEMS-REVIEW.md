# CLI menu/system polish — 2026-10-16

Bounded source pass complete; Windows native verification pending. Asset production
is paused while Windows establishes PTS water. Supplied cream/navy panels, Fredoka,
title artwork and the existing gameplay loop are retained.

Changed files: `Assets/Scripts/Game/VoyageMenus.cs`, this review,
`docs/CLI-ARTIST-HANDOFF.md`, and append-only entries in canonical `comms.md`.
No Editor check added. No other runtime, art, settings, save or capture file edited;
no staging, commits, resets or pushes in main. Existing dirty code was the starting
point, not the art checkout's runtime code.

## Before → after

- Compact title card ended at logical y512 in a 480-high safe-area viewport;
  saved-game Quit ended at y492. Card now ends at y464, all saved-game actions
  by y434. Pause/settings also leave 16 units above/below; headings have more
  vertical room for Large text. These are rectangle calculations, not font checks.
- New Game was a second tap on an armed button without an explicit cancellation.
  It now replaces the card's actions with a consequence warning, **Cancel · keep
  progress** and **Erase & start over**. Only the erase action calls `NewGame`.
  Cancel/Escape recover without clearing progress; continue/settings clear the arm.
- Title settings ignored Escape. The title now handles it once per frame;
  settings buttons say **Back to main menu** or **Back to pause**. Existing pause
  Escape handling remains in the HUD. Hints name their On/Off state; missing audio
  reports unavailability instead of leaving an unexplained empty control.
- Pause → Main menu previously cleared `paused`, allowing food, freshness and
  fishing to advance behind the title. It now keeps the trip paused until Resume.
  Start says **Start in harbour**, loaded progress **Continue in harbour**, and an
  in-memory trip **Resume voyage**. Quit at sea says **Quit (lose trip)**, with
  explicit advice to return to harbour. Test sessions disclose that progress is
  not saved. This does not add mid-voyage persistence or claim saves succeeded.
- Market attention now includes unsold fish. Supplies attention requires an
  affordable relevant purchase, including its lunch-tin upgrade; unlimited free
  scraps no longer imply a bait emergency. Crew/chart/Chandlery eligibility stays
  aligned with the existing rules. Badges cannot repair hidden world shop labels.

## Three consequential remaining issues (outside write ownership)

1. **The Market still has a separate unsafe reset path.**
   [VoyageHud.cs:496](../Assets/Scripts/Game/VoyageHud.cs#L496) arms a 34-high
   destructive button; its second tap calls `NewGame`, without a dedicated cancel
   action. The title's protection does not protect this path. Windows should route
   it to the same explicit confirmation or remove the duplicate reset entry.

2. **The live haul can promise fish that cannot be brought home.**
   [VoyageHaul.cs:9](../Assets/Scripts/Game/VoyageHaul.cs#L9) quotes cooler, deck
   and carried fish together; [VoyageHud.cs:185](../Assets/Scripts/Game/VoyageHud.cs#L185)
   presents their full value. [VoyageGame.cs:600](../Assets/Scripts/Game/VoyageGame.cs#L600)
   only stows remaining capacity on departure and discards overflow. With a full
   cooler and extra deck fish, port earnings can therefore be lower than the
   counter suggested, independently of the fixed contract payout bug. Windows
   should distinguish secured value from fish still needing space and warn on
   overflow departure. The existing countdown helper
   [VoyageHaul.cs:17](../Assets/Scripts/Game/VoyageHaul.cs#L17) is also unused by
   that HUD, which shows a percentage instead of time until depreciation.

3. **Harbour shopping still compresses navigation and hides blocked-action reasons.**
   [VoyageHud.cs:387](../Assets/Scripts/Game/VoyageHud.cs#L387) reserves 410 logical
   units beside the shop. At 640×360, five tabs get about 67 units each at height40;
   wrapped labels at Large text are a clipping risk. Fixed horizontal crew/upgrade
   rows compete with their purchase buttons. [VoyageHud.cs:415](../Assets/Scripts/Game/VoyageHud.cs#L415)
   changes blocked-button colour but still renders an interactive button and gives
   no reason on activation. [VoyageHud.cs:608](../Assets/Scripts/Game/VoyageHud.cs#L608)
   combines crew-cap and affordability failures; [VoyageHud.cs:632](../Assets/Scripts/Game/VoyageHud.cs#L632)
   labels a purchase only with its price. Windows should reflow existing controls
   at narrow widths, name Buy/Hire actions, and expose the relevant shortfall or
   full-crew reason. This is a source-indicated risk, not an observed capture defect.

## Checks and deferred verification

- Tree-sitter C# parser: all **25 current runtime sources**, including the changed
  partial class, have zero syntax errors. Owned-file trailing whitespace: none.
  Exact dirty backup SHA256 verified; this pass's diff reviewed against it.
- Static review traced menu input, `Update`/`Tick`, `NewGame`, harbour arrival/sale,
  save serialization, crew hiring and upgrade prerequisites. Rectangle arithmetic
  checked against the shared safe-area transform at 1440×900, 844×390 and 640×360.
- Impeccable context loaded. Its mechanical detector returned `[]`; it does not
  validate Unity IMGUI. No visual acceptance or accessibility certification claimed.
- Background Roslyn compile prepared for 25 sources/207 references, but the Windows
  `dotnet.exe` launch failed with WSL `UtilAcceptVsock ... accept4 failed 110`
  **before compilation**. No compile or runtime pass claimed. No Unity, Blender,
  player, scratch project or foreground window used.

Windows, after releasing its water-check project, should run one focused native
pass using an isolated/session-only test state, never Mo's real save:

1. Compile current sources. At 1440×900, 844×390 and 640×360, exercise fresh/saved
   title, reset, pause and both settings parents at Small/Normal/Large, including
   nonzero safe-area insets. Check actual text, focus, touch targets and hit regions.
2. Cancel reset by button and Escape: coins/crew/haul unchanged. Confirm once:
   fresh state, settings preserved. Verify neither settings nor Resume erases data.
   SessionOnly protects disk; use a disposable save fixture for persistence checks.
3. While fishing, pause → title → settings; wait actual frames and verify SimTime,
   food and freshness stay unchanged. Resume must advance again. Test Escape from
   both settings parents and ensure the closing click cannot also hit gameplay.
4. Return with fish: Market badge visible, explicit sale pays once, repeats pay
   nothing. Zero coins/free scraps must permit fishing without a false purchasable
   Supplies badge; an affordable lunch tin should produce one. Test crew-full,
   prerequisite-locked and unaffordable states when fixing issue3.

Defer captures if they require a foreground player. Temporary exact backup and
pass diff remain at `/home/mo/catchline-menu-backup-20261016/` until Windows verifies
the change; remove afterward. Backup SHA256:
`2dd4169c80e18ba1b40019f2e5380310b84b83b6ed8a700a40aff1758c6fa710`.
Prepared compile response: `%LOCALAPPDATA%/Temp/CatchlineMenuStatic-20261016/compile.rsp`.
No product decision is required to complete the scoped pass; duplicate-reset policy
and treatment of at-risk deck value belong to Windows' follow-up review.
