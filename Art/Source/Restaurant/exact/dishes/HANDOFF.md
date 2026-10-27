# RESTAURANT-ART-4 handoff

Import these source-art exports:

- `exact/dishes/`: nine `v2-dish-*` menu icons; use manifest logical sizes, preserve aspect. Direct dish-reference and 24/48/91px review sheets included.
- `exact/s15/`: three new `v2-s15-mood-*` table markers. Main manifest includes additive entries; `moods/` contains layout, review and preservation evidence.
- `exact/s5/`: `v2-s5-best-night-ribbon` and `v2-s5-full-house-stamp`, plus separate live labels and measured optional placements.

Total: 14 new tight RGBA 3× sprites. Existing four-frame `v2-s15-steam-strip` is unchanged, already delivered; reuse its parent-manifest frame rects.

Each package includes manifest/layout/text-styles/slices and an actual-size review. Empty text sheets mean icon-only art. Blank stamp labels stay live. Original paintings and prompts retained. New packages only, except three S15 manifest additions. Accepted art is hash-audited; no Assets/production code/metas/save/watchdog/Git edits and no commit.

Final audit: `dishes/delivery-audit.json`; actual opened-review hashes: `dishes/visual-review.json`. Audit script can be rerun with `uv run --with pillow python Art/Source/Restaurant/exact/dishes/audit_delivery.py`.

Claude imports and binds menu IDs, table mood anchors/conditions and celebration triggers, then checks native HUD sizing. Source-art delivery is not Unity or Mo acceptance. Paths are released after the DONE diary line.
