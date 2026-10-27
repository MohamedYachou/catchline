# RESTAURANT-ART-3 handoff — Codex 1

Delivered source art for Claude import:

- `exact/coach-card/`:3 exports, reusable Mira tutorial card, phone844x390+desktop1440x900 layout/text, sliced panel/button, 110-character3-line proof. Concepts `ui-coach-phone.png`, `ui-coach-desktop.png`.
- `exact/s1-card-states/`:4 exports, Stored/free placement, Bistro stage lock and disabled-price state, layout/live labels, actual-size drawer proof `ui-arrange-card-states.png`.
- `exact/closed-sign/`:1 blank wooden sign, separate Closed label, entrance placement proof `ui-closed-sign.png`.

Each has manifest, layout, text-styles, slices, provenance and contact review. Slices are left,bottom,right,top in exported3x pixels. Labels remain live; all public names are new. Caller owns tutorial progression, Skip, item-state conditions/affordability, world anchoring and closed-door visibility. Last orders remains call-strip text; no extra art generated.

`generation-prompts.json` records the4 built-in ImageGen prompts. Existing accepted paintings are reused for coach/card backing. Resampled3x is not a native3x-detail claim. All new work is under Art/Source/Restaurant; comms appended. No Assets, production code, metas, saves, watchdog or Git edits. No commit, no subagents.

Validation: `uv run --with pillow python Art/Source/Restaurant/exact/coach-card/audit_delivery.py`. `delivery-audit.json` records current result; `visual-review.json` records actually-opened proofs and hashes. Native import/runtime and Mo/lead acceptance remain separate.
