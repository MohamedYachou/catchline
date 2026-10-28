# UI v3 kit 2 evidence

Requested by `docs/briefs/UI-V3-KIT-2.txt`; follows accepted kit 1 (`837bede5`). Codex 2 (WSL CLI), no git commands or commit.

Native screenshots use `docs/tools/uiv2-capture.ps1`, the isolated `Catchline-ui2-sim` editor/player and TEST launch mode. Layout sizes are 1440×900 at 2× density and 844×390 at 3× density. These are actual Canvas + scene captures. The pipeline checks for completion, exceptions and a byte-identical player save.

## 1. Day-flow art

[Contact sheet, cream and sea](../art-kit-2.png). Twelve transparent PNGs and Unity metadata in `Assets/Art/UI/v3-*`. Editable SVG originals and the safe-text/slice manifest are in `Art/Source/UIv3/kit-2/`; that directory's README describes wiring. All words and stop numbers are live text.

[Asset audit](art/asset-check.txt) passes RGBA, transparent margins, dimensions, import GUID uniqueness, no mipmaps and slice metadata. `art/initial/` preserves the first native review, which exposed a collapsed dash and narrow-screen label; these are diagnostic frames. Final [desktop](art/kit3-art-1440.png) and [phone](art/kit3-art-844.png) frames were opened: live day/arrival/fuel/number labels, complete pins, route stroke and all four prep silhouettes fit. [Final capture log](art/native-final.log) records completion and unchanged save. New art and SVG sources were released to Claude after item 1.

## 2. Operations and crew management

Six before/after pairs in [management](management/) cover `operations`, `crew` and `crew-deckhand` at both sizes. All original frames were opened. The full Deep lines label, compact duty controls/hints, eight-person crew rail, navy card headers and page switches fit. `native-before.log`, `native-after.log` and player logs record the successful isolated runs.

## 3. Crew, goals and menus

Ten before/after pairs in [crew-menus](crew-menus/) cover `title`, `settings`, `kit3-pause`, `kit3-settings-pause` and `voyage` at both sizes. All original frames were opened. The live crew and goal HUD already uses the accepted kit-1 components; old unused reference entries now forward to those responsive components. Those live HUD pairs are control evidence, not a second redesign.

`kit3-reset-{1440,844}.png` are separately captured, opened confirmation frames showing the whole warning and both actions. There is no valid reset baseline pair: the combined baseline inherited the settings state, so those images are retained only under `diagnostic/`. `baseline-failed-player.log` preserves an initial capture attempt that reached an existing null reference in the excluded `StageRestaurantDay` fixture. Retrying the independent menu/live HUD stages succeeded; no excluded day-flow source was changed.

## 4. Open shops

Eight before/after pairs in [shop](shop/) cover `kit3-shop-grid`, `kit3-supplies`, `kit3-refit` and `kit3-shop-poor` at both sizes. All sixteen original frames were opened. Item names, prices, selection descriptions and disabled refit text fit; open tabs and the supplies switch use the v3 treatment. Phone item names have more wrapping space. [Native after log](shop/native-after.log) records completion and unchanged save. Source comparison preserves chart dispatch, harbour hub, control IDs/aliases, prices, purchase actions, availability and product rules.

## Source scope

Drawing changes are in `CoastalCanvasV3.cs`, `VoyageManagement.cs`, `VoyageManagementPages.cs`, `VoyageInterfaceCrew.cs`, `VoyageInterfaceGoals.cs`, `VoyageMenus.cs` and `VoyageInterfaceShop.cs`. Capture-only fixtures are in `VoyageInterfaceV3Capture.cs` and `VoyageUiV2Capture.cs`. `VoyageManagementForecast.cs` and the existing `VoyageInterfaceV3.cs` are unchanged. No excluded day-flow, chart, state, deck, crew-model, CrewUi or restaurant simulation/world source was edited.

Each production entry scopes the existing v3 kit and Fredoka fonts through `InterfaceV3`; the chart dispatch remains outside the new shop wrapper. New canvas helpers retain the existing control actions and IDs while composing paper/navy surfaces, coral selection and compact duty content. The retired crew/goals drawing entries forward to the existing responsive live HUD. `build_kit2.py` and `review_kit2.py` under `Art/Source/UIv3/` reproduce art and comparison sheets.

## 5. Final checks

`ReferenceHudChecks.Run` **PASS, Unity exit 0** via `run-lead-check.ps1`: live wallet/goal state, containment at three sizes, imported fonts and kit art, text scaling, retained 44px physical pause target and its action. [Full log](checks/ReferenceHudChecks.log), [runner output](checks/reference-run.log).

`RestaurantChecks.Run` **PASS, 47,183 assertions, Unity exit 0** in the same scratch project after the HUD log was archived. This covers layout, portions, 1,000 forecasts, simulation, edge cases and service. [Full log](checks/RestaurantChecks.log), [runner output](checks/restaurant-run.log).

[Source comparison](checks/source-audit.txt) records drawing-only normalization checks; [review diff](checks/owned-source.diff) records the owned source changes against the pre-task backup. [Artifact audit](checks/artifact-check.txt) passes all 24 pairs, final art/reset images, native TEST completion, unchanged-save markers and README links. All 48 paired originals and four final art/reset originals were opened during their respective item reviews.

[SHA256 manifest](checks/source-and-evidence.sha256) records the owned source, generated art/source assets and evidence. Temporary pre-task source backups were removed after verification; the reviewed diff remains. All assigned reservations are released.

Native reviews and the two required automated checks are complete. No physical-device, whole-game playthrough or Mo acceptance is claimed. The initial fixture failure and invalid reset baseline are retained as diagnostics rather than successful evidence. No git commands or commit.
