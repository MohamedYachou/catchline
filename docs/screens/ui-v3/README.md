# UI-V3-KIT-1 evidence

Codex 2 (WSL CLI), 2026-10-27. Completed in order: radio → sailing → fishing → harbour. Uses the supplied restaurant `rx-*` / `v3-*` art and Fredoka Bold/SemiBold; no new art style or crew assets.

## Native visual review

Every listed migrated state was captured through `docs/tools/uiv2-capture.ps1` and opened at **1440×900 and 844×390**. These are logical viewport sizes; original PNGs retain the native device pixel resolution. `*-pair.png` places the preserved baseline beside the result. The comparison sheets are resized for review; inspect the original PNG for small type.

| Item | Native states in `after/` | Review result / useful pair |
|---|---|---|
| A — Radio | `radio/new-radio-out`, `new-radio-out2`, `new-radio-home`; additional `kit3-radio-reply`, `kit3-radio-disabled` | Mira mood/bust, caller chip/name, ringing radio and answer styles fit. Complete Janssens booking wraps on the ticket with its new-line tick. Hotel offers 60 coins. Reply fits; disabled Buy is grey. Prep labels, separate bars and Lend a knife fit. [Phone booking pair](after/radio/new-radio-out2-844-pair.png), [phone prep pair](after/radio/new-radio-home-844-pair.png), [desktop call pair](after/radio/new-radio-out-1440-pair.png). |
| B — Sailing | `sailing/depart-lane`, `sea-entry`, `return-lane` | Journey title/stage/progress, Faster, wallet and menu use the kit in both harbour lane and open sea. Full homeward title confirmed at native resolution. [Phone lane pair](after/sailing/depart-lane-844-pair.png), [desktop return pair](after/sailing/return-lane-1440-pair.png). |
| C — Fishing | `fishing/voyage`, `new-fishing` | Migrated status/ground cards, then crew rail, then action controls and common overlays. Full eight-person rail and first-trip rowboat state checked. Ground/crew headings, goal wrapping, primary/secondary actions and stow tag fit. [Phone voyage pair](after/fishing/voyage-844-pair.png), [desktop first-trip pair](after/fishing/new-fishing-1440-pair.png). |
| D — Harbour hub | `harbour/harbour-h4`, additional `harbour-h0` | Migrated title/destination and goal, Set sail, wallet/menu, then five navigation tabs. Both hull states fit; rowboat Skiff goal/best-haul text is visible. [Phone hub pair](after/harbour/harbour-h4-844-pair.png), [desktop hub pair](after/harbour/harbour-h4-1440-pair.png), [rowboat phone original](after/harbour/harbour-h0-844.png). |

`new-harbour` opens the **Market page**, not the harbour hub. Its pairs are control evidence for the existing shop presentation. `new-plan` is also retained as surrounding-flow evidence. Additional reply/disabled/rowboat states have no baseline pair; each main item has the before/after coverage above. Harbour fixtures deliberately grant 10,000 coins; that is fixture setup, not a new-game economy change.

## Verification

- [RestaurantChecks.Run](checks/RestaurantChecks.log): **47,183 checks passed**, Unity exit 0, after all runtime UI edits.
- [ReferenceHudChecks.Run](after/fishing/ReferenceHudChecks.log): **PASS**, Unity exit 0. Covers live wallet/contract/goal data, three-size containment, real fonts/art, text scaling, physical pause target and invoking the pause action.
- [Source comparison](checks/source-audit.txt): fishing/travel bodies unchanged behind theme wrappers; harbour body unchanged except panel composition; tab geometry, aliases and actions retained; radio logic unchanged except the explicitly requested hotel reward floor of 60.
- Each completed native capture ran in **TEST** mode without native exceptions. The script confirmed the player's save stayed byte-identical: `8BF5D969E3EF2CBFFE05FF098BD6F476114AE045B45AA7045CDF331F03DA817F`. Per-group `native*.log` files are archived alongside the frames.
- Native frames and source/runtime checks establish the results above. No physical phone touch session, full-game playthrough, browser/Lighthouse audit, or Mo acceptance is claimed. The Unity runtime HUD is the visual evidence.

## Implementation and scope

Changed existing sources:

- `Assets/Scripts/Game/VoyageMiraRadio.cs` — scoped v3 drawing, measured notebook wrapping/tick, reply and prep layout; hotel reward floor.
- `Assets/Scripts/Game/VoyageInterface.cs` — scoped sailing/fishing presentation and common HUD overlays.
- `Assets/Scripts/Game/VoyageInterfaceVoyage.cs` — ground card header composition.
- `Assets/Scripts/Game/VoyageInterfaceShop.cs` — harbour hub theme/header and v3 navigation surfaces.
- `Assets/Scripts/Game/VoyageUiV2Capture.cs` — dispatch for the two additional TEST radio fixtures.

Added `CoastalCanvasV3.cs`, `VoyageInterfaceV3.cs`, `VoyageInterfaceV3Capture.cs` and their `.meta` files under the same script directory. Helpers add a titled paper slab, navigation surfaces and wrapped-text measurement; theme overrides restore in `finally`. Existing callers retain their previous kit. The two radio fixtures use the real call builders/answer action and require `SessionOnly`.

`Art/Source/UIv3/review_pairs.py` generates pair sheets from archived originals, e.g. `python3 Art/Source/UIv3/review_pairs.py harbour harbour-h4`. It requires Pillow.

No git commands or commit. Crew models, `CrewUi/**`, restaurant world/simulation and `VoyageRestaurantDay.cs` were untouched. Shop pages, minigame screens and other UI families are outside this migration's delivered scope. Temporary source backups were removed after verification. TIER6-WIRE-1 remains for the lead's next assignment.
