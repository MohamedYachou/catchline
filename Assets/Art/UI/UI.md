# Catchline build 1 UI kit

Authored vector sprites in the STYLE.md palette. PNGs are straight-alpha RGBA, sRGB, at 2x. The three comps are 1920×1080 RGB design references, not Unity screenshots. All labels except TAP! are live text, never baked into buttons.

## Import contract

Use Sprite (2D and UI), Single, sRGB on, alpha transparency on, Clamp, Bilinear, no mipmaps, no compression for the initial integration. These are recommendations; Unity was not opened and importer settings are not claimed. Set Image type Sliced only for entries with a border. Border values below and in slices.json are **exported PNG pixels**, ordered left, bottom, right, top. PPU 200 gives a 2x sprite a 100-PPU logical size; set explicit UI RectTransforms to the intended logical sizes. Do not trim the transparent gutters; slices include soft shadow padding.

The native HUD uses 1280×720 virtual coordinates. Comps scale those coordinates 1.5× to 1920×1080, preserving the panel anchors. Strike water is 460×220 logical / exactly 920×440 exported. Icons are 128×128 logical / 256×256 exported. 9-slice specimens are small reusable textures, not forced panel sizes. Do not stretch icons, bobbers, tails, rings or the water panel non-uniformly.

## Text, states and composition

Fredoka Medium is the one shipped display/UI font. Navy text on cream, white, gold and light grey; ivory text on navy and teal. Use navy on normal orange buttons and ivory on their darker pressed state. Orange and teal button labels must be at least 24px at the 1920px reference size: those pairings meet the 3:1 large-text threshold; body text on cream exceeds 4.5:1. Keep orange for the main action. Selection has a border and active-tab value change; rod states, progress and urgency always retain words/icons. Grey buttons must also be non-interactable. Pressed artwork lowers and darkens the surface. No extra shadow is needed on top of baked sprite shadows.

Speech bubble: minimum logical 88×42 body plus icon slot, though the styled comps widen to 107×51 to fit the requested icon slot. Tail overlaps body by 3px. Hot body and tail are gold, with ! text and a rod icon. Fish / Watch / Carry / ! labels are code-owned. Fish and Carry appear together with the strike panel to demonstrate all required kit placements; action availability still follows game state.

Progress: the source bar caps are 12 logical px. Render a full-width sliced fill then clip it to progress; this preserves cap radius below 24px. A fill at zero is hidden. Teal=cooler, green=food/reeling, red=warning/bite timer. Values remain live text.

Strike: use the same 80×80 logical bobber frame for all states. Waiting=floating, nibble=dipped, bite=underwater + ripple + TAP!; tap anywhere outside UI buttons, as current gameplay specifies. Water has no baked bobber. Ring scales uniformly and fades. These sprites add no timing or animation clips.

## Files

| PNG | Intended px | Export px | Slice L/B/R/T (export px) | Use |
| --- | --- | --- | --- | --- |
| `panel-cream.png` | 128×128 | 256×256 | 56/64/56/56 | Reusable panel; keep text in the content inset. |
| `card-white.png` | 128×128 | 256×256 | 56/64/56/56 | Reusable panel; keep text in the content inset. |
| `card-selected.png` | 128×128 | 256×256 | 56/64/56/56 | Reusable panel; keep text in the content inset. |
| `toast-dark.png` | 128×128 | 256×256 | 56/64/56/56 | Reusable panel; keep text in the content inset. |
| `chip-dark.png` | 128×128 | 256×256 | 56/64/56/56 | Reusable panel; keep text in the content inset. |
| `button-primary-normal.png` | 128×64 | 256×128 | 44/40/44/40 | primary button normal; labels are live text. |
| `button-primary-pressed.png` | 128×64 | 256×128 | 44/40/44/40 | primary button pressed; labels are live text. |
| `button-secondary-normal.png` | 128×64 | 256×128 | 44/40/44/40 | secondary button normal; labels are live text. |
| `button-secondary-pressed.png` | 128×64 | 256×128 | 44/40/44/40 | secondary button pressed; labels are live text. |
| `button-disabled-normal.png` | 128×64 | 256×128 | 44/40/44/40 | disabled button normal; labels are live text. |
| `button-disabled-pressed.png` | 128×64 | 256×128 | 44/40/44/40 | disabled button pressed; labels are live text. |
| `button-tab-on-normal.png` | 128×64 | 256×128 | 44/40/44/40 | tab-on button normal; labels are live text. |
| `button-tab-on-pressed.png` | 128×64 | 256×128 | 44/40/44/40 | tab-on button pressed; labels are live text. |
| `button-tab-off-normal.png` | 128×64 | 256×128 | 44/40/44/40 | tab-off button normal; labels are live text. |
| `button-tab-off-pressed.png` | 128×64 | 256×128 | 44/40/44/40 | tab-off button pressed; labels are live text. |
| `bubble-white.png` | 128×64 | 256×128 | 48/40/48/40 | Speech body; reserve left 34px for a separate icon. Tail separate. |
| `bubble-white-tail.png` | 24×18 | 48×36 | — | Centre under body; overlap 3 logical px to conceal seam. |
| `bubble-hot.png` | 128×64 | 256×128 | 48/40/48/40 | Speech body; reserve left 34px for a separate icon. Tail separate. |
| `bubble-hot-tail.png` | 24×18 | 48×36 | — | Centre under body; overlap 3 logical px to conceal seam. |
| `bar-background.png` | 64×24 | 128×48 | 24/18/24/18 | Progress track; always pair state colour with a text value or icon. |
| `bar-teal.png` | 64×24 | 128×48 | 24/18/24/18 | teal progress fill; use clipping at low values, never squash the caps. |
| `bar-green.png` | 64×24 | 128×48 | 24/18/24/18 | green progress fill; use clipping at low values, never squash the caps. |
| `bar-red.png` | 64×24 | 128×48 | 24/18/24/18 | red progress fill; use clipping at low values, never squash the caps. |
| `strike-water.png` | 460×220 | 920×440 | — | Strike close-up; no bobber baked in. Export is exactly 920×440. |
| `bobber-floating.png` | 80×80 | 160×160 | — | Strike bobber floating; share an 80×80 frame and bottom-centre anchor. |
| `bobber-dipped.png` | 80×80 | 160×160 | — | Strike bobber dipped; share an 80×80 frame and bottom-centre anchor. |
| `bobber-underwater.png` | 80×80 | 160×160 | — | Strike bobber underwater; share an 80×80 frame and bottom-centre anchor. |
| `fish-shadow.png` | 128×64 | 256×128 | — | Fish shadow beneath bobber, rotate around centre. Fixed size; no outlines. |
| `ripple-ring.png` | 128×128 | 256×256 | — | Scale uniformly and fade; transparent centre. |
| `tap-burst.png` | 128×96 | 256×192 | — | Bite-only TAP! burst. Lettering rendered from bundled Fredoka. |
| `icon-coin.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-fish.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-bait-worm.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-food.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-cooler.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-ice.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-rod.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-crew.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-contract-scroll.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-map-pin.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-home-anchor.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-clock.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-star.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |
| `icon-lock.png` | 128×128 | 256×256 | — | 128px intended icon; 256px PNG (2x). Original authored silhouette. |

## Font and reproducibility

`Fonts/Fredoka-Medium.ttf`: unrenamed Fredoka family, static Medium (weight 500, width 100) instantiated from the Google Fonts variable source. `Fonts/OFL.txt`: complete SIL Open Font License 1.1, permits bundling/redistribution. Source: [Google Fonts Fredoka](https://github.com/google/fonts/tree/main/ofl/fredoka). `Fonts/SOURCE.md` records the download URL and static-instance parameters. The original font copyright is retained inside the TTF. No external icon pack or generated art was used.

`slices.json`: complete manifest of all PNGs, logical/export dimensions, source paths and optional slice borders. `validation.json`: mechanical delivery checks. Every PNG maps to an authored SVG under `Art/Source/UI/`; soft shadows and the TAP! lettering are composed by `Art/Source/build_ui_kit.py`. Original icon geometry belongs to this project. Backgrounds are renders of existing project meshes staged by `Art/Source/render_ui_backgrounds.py`; they contain no UI.

Rebuild with Python 3.12+ and Pillow/CairoSVG/fontTools: `python Art/Source/build_ui_kit.py`. Render the two backgrounds first in Blender 5.2 using `Art/Source/render_ui_backgrounds.py`. Rebuild model fixes separately with the existing Gull Harbour builder and the six asset arguments. `Art/Source/validate_ui_kit.py` verifies manifest coverage, sizes, alpha and slices.

## Mockups and live layout reference

`Art/Concepts/16-ui-kit.png`: every shipped piece including both states, tails and all 14 icons. `17-hud-fishing.png`: status top left, coin/home top right, crew bottom left, action bubbles and strike bottom centre. `18-hud-harbour.png`: harbour/goal left, five-tab Shop right, Set sail at its foot. Composed from the exported kit using genuine nine-slice raster assembly, not an unrelated painted UI. Example state values are illustrative. Shop prices, names, food and skiff limits follow proto/deck-sim `GameData.cs` / `VoyageHud.cs` as read on 2026-10-14 (47373b7 plus live working copy).

The harbour and fishing panels follow those HUD anchors; the bubble bodies are slightly wider for the requested icon slot. Unity integration, font import, device testing and final interaction behaviour are a later code pass.

## Task 05 — UI pass 2

Additive illustrated sprites in the existing palette and Fredoka. All listed dimensions are final exported pixels, at 2x (logical size is half). Keep alpha gutters and aspect ratios. Title backdrop is an opaque full-screen RGBA scene; all other additions have transparent margins. Lettering in the logo, shop headers, NEW badge and unknown fish is intentionally baked; gameplay labels remain live. Source SVG lettering uses outlines from the bundled Fredoka font. No new M_ materials.

| PNG | Export px | Logical px | Slice L/B/R/T | Use |
| --- | --- | --- | --- | --- |
| `logo-catchline.png` | 1024×384 | 512×192 | — | Fredoka wordmark; cream keyline, C fishing line/hook and orange bobber. Preserve aspect ratio. |
| `title-backdrop.png` | 1920×1080 | 960×540 | — | Golden-hour harbour. Menu safe rectangle export x=80..650, y=420..940. Full-screen opaque RGBA backdrop; preserve aspect ratio. |
| `header-market.png` | 1240×220 | 620×110 | — | Fish Market illustrated counter banner. Fredoka shop name baked; no slice. |
| `header-harbourmaster.png` | 1240×220 | 620×110 | — | Harbour Master illustrated counter banner. Fredoka shop name baked; no slice. |
| `header-crewoffice.png` | 1240×220 | 620×110 | — | Crew Office illustrated counter banner. Fredoka shop name baked; no slice. |
| `header-chandlery.png` | 1240×220 | 620×110 | — | Chandlery illustrated counter banner. Fredoka shop name baked; no slice. |
| `header-supplies.png` | 1240×220 | 620×110 | — | Supplies illustrated counter banner. Fredoka shop name baked; no slice. |
| `fish-herring.png` | 256×256 | 128×128 | — | herring side portrait, head left. Species shapes and markings; fixed shared frame, not common physical scale. |
| `fish-mackerel.png` | 256×256 | 128×128 | — | mackerel side portrait, head left. Species shapes and markings; fixed shared frame, not common physical scale. |
| `fish-pollock.png` | 256×256 | 128×128 | — | pollock side portrait, head left. Species shapes and markings; fixed shared frame, not common physical scale. |
| `fish-seabass.png` | 256×256 | 128×128 | — | seabass side portrait, head left. Species shapes and markings; fixed shared frame, not common physical scale. |
| `fish-conger.png` | 256×256 | 128×128 | — | conger side portrait, head left. Species shapes and markings; fixed shared frame, not common physical scale. |
| `fish-plaice.png` | 256×256 | 128×128 | — | plaice side portrait, head left. Species shapes and markings; fixed shared frame, not common physical scale. |
| `fish-cod.png` | 256×256 | 128×128 | — | cod side portrait, head left. Species shapes and markings; fixed shared frame, not common physical scale. |
| `fish-unknown.png` | 256×256 | 128×128 | — | unknown side portrait, head left. Species shapes and markings; fixed shared frame, not common physical scale. |
| `icon-rodholder.png` | 256×256 | 128×128 | — | 128px logical item icon. rodholder. Preserve square frame. |
| `icon-bigcooler.png` | 256×256 | 128×128 | — | 128px logical item icon. bigcooler. Preserve square frame. |
| `icon-icebox.png` | 256×256 | 128×128 | — | 128px logical item icon. icebox. Preserve square frame. |
| `icon-lunchtin.png` | 256×256 | 128×128 | — | 128px logical item icon. lunchtin. Preserve square frame. |
| `icon-rod-fibreglass.png` | 256×256 | 128×128 | — | 128px logical item icon. rod fibreglass. Preserve square frame. |
| `icon-rod-carbon.png` | 256×256 | 128×128 | — | 128px logical item icon. rod carbon. Preserve square frame. |
| `icon-chart.png` | 256×256 | 128×128 | — | 128px logical item icon. chart. Preserve square frame. |
| `icon-squid.png` | 256×256 | 128×128 | — | 128px logical item icon. squid. Preserve square frame. |
| `icon-fuel.png` | 256×256 | 128×128 | — | 128px logical item icon. fuel. Preserve square frame. |
| `icon-net.png` | 256×256 | 128×128 | — | 128px logical item icon. net. Preserve square frame. |
| `icon-skiff.png` | 256×256 | 128×128 | — | 128px logical item icon. skiff. Preserve square frame. |
| `icon-trophy.png` | 256×256 | 128×128 | — | 128px logical item icon. trophy. Preserve square frame. |
| `icon-gift.png` | 256×256 | 128×128 | — | 128px logical item icon. gift. Preserve square frame. |
| `sea-chart.png` | 1240×520 | 620×260 | — | Unlabelled chart. Harbour left. Five area centres use the documented sea rectangle, no pins/text baked. |
