# S7 Morning market — source-art handoff

Reference: `../../concepts/ui-7-market.png`, 844 × 390. Whole surplus fish have Sell/Keep controls; prepared restaurant stock is explicitly excluded. The buyer and demand are visible before the total and Sell & open action. The current assignment calls this the morning market; the older plan describes selling on arrival. This artwork follows the current assignment's screen name without changing the day loop.

Numbers are illustrative. Quotes use whole coins with the example 2.4 × 12 rounded down to 28; 28 + 54 + 16 = 98. This is a presentation example, not a proposed economy or rounding implementation.

Import `v2-s7-*` with `manifest.json`, `layout.json` and `text-styles.json`. All coordinates use the 844 × 390 top-left canvas; every repeated placement has a distinct `use`. Text remains live. `slices.json` borders are **left, bottom, right, top in exported pixels**. Currency emboss remains in the coin icon; other text is removed. The background is opaque and all foreground exports have transparent outer bounds and opaque paper/button centres.

Provenance retains the original generated mockup, complete generation prompts, sheet sources and measured reference crops. Clean sprite sheets isolate/recreate the painted objects, so details may differ from the original painting. The original mockup is 1844 × 853; the reference is mechanically resized to 844 × 390. Exports are alpha-trimmed and sized to three times each largest measured placement. This does **not** establish native 3× detail or pixel-identical cutouts.

`handoff.py` is an art-only mechanical crop/resize/measurement/audit helper. Review contacts compare the actual mockup crop with each final export. `reconstruction-compare.jpg` compares the painting with an offline composition of the delivered sprites and supplied Fredoka Bold text. This does not establish Unity integration, interactive behaviour or lead/Mo visual acceptance.

Delivery status is recorded in `audit.json` and `comms.md`; pending work must not be inferred complete from this report's existence. No Assets, production code, Git, saves or watchdog files are edited. Claude owns import and native acceptance.

Final: 24 sprites, 37 placements, 40 measured text entries, 11 sliced sprites. All four reference/export sheets, combined measurement overlays and offline reconstruction opened. Source isolation preserves the family but differs in bevels, buyer-frame pins, sign ropes and icon finishes; pixel identity is not claimed. Claude review/import remains.
