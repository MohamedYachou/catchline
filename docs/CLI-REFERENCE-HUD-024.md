# UI-024 — fish.png crew and goal HUD

Codex 2 (WSL CLI) leads; Mo-authorized GPT-6.1 Sol medium built and reviewed the left panels. Canonical diary: ../comms.md. No main commit/staging/reset/push. Windows NET-010 owns gameplay and scratch; UI changes preserve current gameplay/save rules.

## Delivery

Both requested sides are integrated in the fishing HUD. Right: original cream Crew toolbar, real capacity including captain, original hamburger wired to pause, Crew Roles and portrait cards. Left: sun, Day/voyage, elapsed voyage time, live coins and Current Goal. Shared primitives, typography and source artwork serve both sides.

Files: `VoyageInterface.cs` narrow fishing wiring; additive primitives in `CoastalCanvas.cs`; new `FishReferenceStyle.cs`, `VoyageInterfaceCrew.cs`, `VoyageInterfaceGoals.cs`; `Assets/Resources/FishReference/` (24 mechanically extracted image fragments, two static font instances and OFL license); `Assets/Editor/ReferenceHudChecks.cs`. Reproducible extraction: `/home/mo/pts-v3-tools-env/bin/python docs/tools/extract_reference_hud024.py`; optional `--fonts` uses a hash-checked official font source and distinct internal face names. Original reference is byte-preserved at [fish-original.png](reference-hud024/fish-original.png), SHA256 `f01502cb0518a8c91a942434ae714df8413952078d37af3e623e61ff36e08e5f`.

The requested literal reuse drives the implementation. Icons/static captions preserve original crop RGB, keylines and cream pixels. Panel perimeters come from original crops; removed sample text/portraits are replaced with clean source strips. The empty progress track is reconstructed from the genuinely empty tan portion (zero green pixels), rather than leaving the reference's 70% fill underneath. Resources use uncompressed/no-mipmap/native-size metadata, established source GUIDs untouched. New metadata is additive.

## Reference geometry and honest limits

1672 × 941 source canvas. Left status20,25,320,65; Current Goal20,130,220,104. Right toolbar1407,25,248,49; Crew panel1365,85,290,568 at six rows. Actual source row tops130/215/301/387/475/562. Right anchored by viewport edge, height scale shared with left. Runtime roster height follows actual people rather than inventing six crew. Static captions retain source dimensions/top anchors; live text is bounded to slots. Original-resolution capture exposed1–3px caption/coin drift, corrected in final source; final precision changes were recaptured and compared in native Unity. Ten static icon/heading regions have zero RGB error and100% pixel identity; see docs/screens/ui024/final-precision-comparison.json. Whole-panel/live-font identity is not claimed.

**This is not a certified pixel-perfect match.** The PNG does not identify a font file. Live text uses shared Nunito500/800 instances as an approximation; static captions preserve actual rendered lettering. Font source/license: [Google Fonts Nunito](https://github.com/google/fonts/tree/main/ofl/nunito), original OFL included. Source perimeter/blank-field reconstruction, different game data/portraits, variable roster, proportional viewport scaling and text fit cause intentional or remaining pixel differences. Phone fine print is small at reference-proportional scale; mobile legibility is not accepted. Do not silently advertise perfect font or visual parity.

## Real data, retained controls

- Crew count includes captain; capacity is existing hired cap +1. Names appear in the reference's right metadata slot; no invented experience levels. Bar captions identify actual provisions/contract trips and retain live person/rod activity. Percentages reflect those real resources, not reference sample numbers.
- Day is existing `State.Voyage`. Clock is actual elapsed voyage time (pause freezes it), not fabricated time of day. Large values use bounded coin/time strings; full reference balance2,845 remains full.
- Goal uses actual SOLD/delivered contract progress. Unsold fish cannot pretend to be delivered. Without a contract, show existing sold-haul refit requirement/funds or upgraded hold target. No new progression or professions.
- Secured count/value, food, bait, unstowed count and existing freshness countdown remain below the goal. Existing Head home/discard confirmation is preserved below the crew panel. Existing catch feedback remains right-bottom.
- Windows' `InterfaceNetOrders()` is wired last, replaces the duplicate legacy net button and keeps its modal above strike/catch controls. Net card remains left-bottom, clear of crew/goal. Windows owns its mechanics and styling.
- Pause has an invisible44physical-pixel target without stretching the original menu artwork; matching blocking rectangle prevents world clicks through that target. Physical pointer testing remains separate from retained-action invocation checks.

## Verified evidence

Full combined current runtime and Editor source compiled via installed Unity Roslyn, exit0; only preexisting audio hiding warning. Evidence `Logs/ui024-compile/combined-final.log`, `editor-final.log`, source hashes. This does not itself verify Unity runtime.

Codex1 executed hidden native `ReferenceHudChecks.Capture`: `Catchline-sim/Logs/check-ui024.log` reports **REFERENCE HUD CHECKS PASSED** and paired real world+transparentCanvas captures at1672×941,1440×900,844×390,Larger type,bite and catch. Its state checks cover real wallet updates, huge balances, pending-vs-delivered contracts, existing refit goal without purchase, containing rectangles, real imported assets/fonts, retained pause, type-toggle stale-caption cleanup and44px touch target. Main/scratch Canvas/check hashes matched when evidence was read. Windows NET010 also captured the actual four-person roster and net/orders controls. No foreground app or scratch writes/processes by Codex2.

Inspected native original-resolution, four-crew desktop/phone and catch-phone images. [Actual four-crew native capture](screens/ui024/native-compact-desktop.png), [phone](screens/ui024/native-compact-phone.png), with source/byte receipt. [Asset assembly study](screens/ui024/asset-assembly-study.png) is explicitly NOT a native capture and predates final alignment fixes. Never use it as runtime proof.

## Handoff / first remaining fidelity work

Final precision corrections were compiled, recaptured by Codex1 in the hidden
NET010 delivery check and inspected. `check-net010-delivery.log` reports the
reference checks and paired captures complete. All owned main/scratch source and
FishReference dependencies byte-match. Ten native original-resolution static
regions have ZERO RGB error and100% pixel identity against original crops:
sun, coin icon, goal target/title, crew badge/group/menu/title, Captain title/wheel.
[Final comparison](screens/ui024/final-precision-comparison.png),
[actual original-resolution game](screens/ui024/native-reference-1672.png).
This verifies the sampled static regions, not the whole UI or dynamic font.

Implementation/native delivery is finished; full literal font parity and phone
fine-print readability remain unresolved fidelity work, not an approved new queue.
Mo visual review and physical pointer testing remain separate. No active
subagent/source reservation. Windows retains its own NET010/runtime/scratch/build
ownership. No main commit/staging/reset/push. Own temporary source backup removed
after final native/source verification; unrelated backups untouched.

`docs/tools/check.ps1` originally excluded Resources; Codex1 has authorized its
narrow resource-copy tooling update. Ensure `Assets/Resources/FishReference/` and
its folder.meta are mirrored explicitly if using an older copy of the tool;
preserve scratch ArtLibrary.asset. No main batchmode/foreground apps/player save
writes. Future scoped fidelity pickup starts with this final native comparison,
not redoing the completed source/extraction/integration steps.
