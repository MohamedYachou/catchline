# Task 03 — build 1 UI kit and review fixes

Completed on `art/style-pass`. Unity was never opened; `Assets/Scripts`, `Assets/Scenes` and both CrewBody files are unchanged.

- Six corrected model sources in `Art/Models/GullHarbour/`, matching FBXs in `Assets/Art/Models/`, refreshed previews/contact sheets, numerical reports and hashes. Captain cap: attached curved visor/band/anchor. Rocks: 188 triangles each and flat bottoms. Kelp: exactly planar leaf-and-bulb mat with no overlapping faces. Rod: 48 mm blank butt, visible cork and reel, 1.6 m height retained.
- `Assets/Art/UI/`: 44 transparent 2x PNGs covering every requested panel/button state, bubble/tail, strike element, progress piece and 14 icons. `UI.md` lists every file and intended/export dimensions; `slices.json` gives source-pixel borders. `Fonts/` contains Fredoka Medium TTF, full OFL licence and source attribution.
- `Art/Concepts/16-ui-kit.png`, `17-hud-fishing.png`, `18-hud-harbour.png`: all 1920×1080, assembled from exported kit sprites. HUDs follow current `VoyageHud.cs` anchors at 1.5× its 1280×720 virtual coordinate system. Fishing/harbour backgrounds are headless Blender renders of project assets, not Unity captures.
- `Art/Source/`: editable SVGs, font-aware PNG/composition builder, background-stage script, planar kelp preprocessor/JSON and validation scripts. No AI-generated image assets were needed.

Verification: all 26 source/FBX pairs passed dimensions, transforms, palette and FBX round-trip checks. New asset-specific checks passed. UI verification checks all 44 sprites, exact sizes, transparent alpha, slice bounds, sRGB/provenance metadata, packaged font/licence, three mockup dimensions, unchanged crew hashes and protected paths. Visual review at 1920×1080 and reduced 1280×720 caught and corrected missing arrow glyphs, harbour goal-card spacing and button text contrast. Web-only browser/Lighthouse checks do not apply to these offline game sprites.

Nothing remains unfinished in Task 03. Unity import/material/font integration, real device validation and tier 3 skiff art are later work, outside this task. The pre-existing untracked `Art/TASKS/` folder is left as found and excluded from the commits.
