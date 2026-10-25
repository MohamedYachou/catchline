# PURCHASE-FX-1

Codex 1 (Windows app). Native Unity Canvas evidence from the isolated Catchline-sim project, using session-only production shop actions. No player save is loaded or written.

The new effects use the accepted PurchaseFx artwork: a single retained sale glint restarts for each landing and follows the actual wallet coin icon, including its bump; a purchase burst expands from the bought item on the first landing, above the original gold glow. Both are HasUi-guarded, nonblocking and fade away. The last effect keeps its full tail without changing the wallet count or extending the existing sound window.

## Frames

- [Purchase, desktop](buy-1440.png), [purchase, landscape phone](buy-844.png): 0.93 seconds after flight start, within the first-landing burst.
- [Sale, desktop](sell-1440.png), [sale, landscape phone](sell-844.png): 1.44 seconds after flight start, during the final landing glint.

## Verification status

Final revised capture suite: 139 assertions, Unity exit 0. Full CrewCardsAbilityChecks.Regression: ability 286, tutorial 217, M2 and integration PASS, Unity exit 0. All 233 scratch C# files match capture-inputs.json and the final regression snapshot. Main matched before regression; subsequent peer changes in VoyageChart.cs and VoyageIllustratedChart.cs are outside this receipt. Full final logs and artifact hashes are retained in verification.json.

Personally reopened all four final images after the anchor correction: the glint overlays the actual wallet coin, the burst stays centred on bought art, and controls remain clear at both sizes. Independent read-only visual and source reviews completed; the lead corrected the legacy endpoint offset and guarded the original sound window. No implementation checks remain pending; Claude review and Mo player/listening acceptance remain separate.

The capture harness checks actual transaction callbacks, imported art, onset/expiry including the tail, growth/fade, destination centres, one sale glint, purchase draw order above the original glow, nonblocking images and unchanged balances. Frames are scripted scene + production Canvas composites, not physical-device or interactive-player acceptance. No listening acceptance is claimed.
