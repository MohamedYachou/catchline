# CREW-FX-ART-1 — Group A

Codex 2 (WSL CLI). Artist delivery complete; runtime animation and native acceptance belong to Claude/Mo. Source-only work: no Unity or Assets edits.

21 transparent RGBA PNGs: 18 requested exports and three optional opening-interior overlays. `manifest-A.json` records dimensions and SHA256. Rebuild with `/home/mo/.venvs/catchline-ui/bin/python -B Art/Source/CrewFx/build.py` from the project root. Accepted CrewFinal sources are read only.

| Exports | Size | Review |
|---|---|---|
| fx-rays | 512×512 | Twelve soft warm shafts; transparent centre/end falloff |
| fx-glow | 512×512 | White radial alpha, tint in code |
| fx-sparkle | 128×128 | Four-point white twinkle with pale gold core |
| fx-burst | 512×512 | Hollow cream impact ring, navy contour |
| fx-confetti-1..4 | 64×64 | White strip, square, curl, triangle; tint in code |
| fx-coin-trail | 128×32 | Soft warm streak |
| fx-levelup-arrow | 256×256 | Chunky token-gold arrow, navy outline |
| fx-rank-ribbon | 640×160 | Blank cream ribbon, navy outline |
| fx-chest-shadow | 512×128 | Soft oval ground shadow |
| v2-chest-crate/sea/captain-base and -lid | 512×512 | Same alignment as accepted closed originals; latch follows lid |
| v2-chest-crate/sea/captain-interior | 512×512 | Optional opaque opening patch; see below |

## Chest integration

Draw base then lid at identical canvas coordinates when closed. Standard straight-alpha source-over in Pillow reconstructs each accepted closed original with **zero mismatched pixels and zero RGBA error**, including transparent RGB. `chest-checks.json`, `review/*-recomposite.png`, `review/*-diff.png` and labelled `review/*-diff-review.png` preserve the proof.

The accepted originals contain alpha251/252 across most painted areas. A fully opaque hidden base would change that accepted alpha. The supplied base/lid pair uses a solved translucent dark-wood fill under the lid to preserve the exact original. The exposed exact base consequently retains faint lid traces. **While opening, draw the matching interior PNG above base, below lid; keep it OFF when fully closed.** It supplies an opaque dark upper plane and adjacent same-face texture behind the moving latch. This additional layer is the explicit workaround, not a claim that the two-layer exposed base is clean alone. Fade/toggle it as the opening begins; Claude controls timing. Native sampling/color-space/blend behavior has not been tested here.

## Evidence and visual review

Opened and inspected `review/contact.png` (cream and navy, all 21 exports, small-size samples), `review/lifted-layers.png`, and all three labelled chest diff sheets. Soft lights remain legible on navy; solids match the accepted cream/navy/gold language and remain readable at icon scale. Lifted review demonstrates static separation and the opaque interior workaround, not a finished perspective hinge animation. Dark interior is intentionally simple and unlit. SVGs preserve solid effect construction; analytic light/shadow construction and pixel cuts live in build.py.

Checks: requested filenames and sizes, RGBA mode, transparent pixels, 21 manifest hashes, twelve-ray formula, and all three exact source-over comparisons passed. No audio, native HUD, animation, or gameplay acceptance claimed by Group A. Group B evidence lives in Art/Audio/Real/.

### Hinge/pivot notes (Claude-approved overlay order)

Coordinates use the original 512×512 canvas, origin top-left. Rear wood edge endpoints and midpoint suggestions: crate (79,210)–(207,164), midpoint **(143,187)**; sea (65,215)–(197,157), midpoint **(131,186)**; captain (57,225)–(190,168), midpoint **(123.5,196.5)**. The rear hinge is an oblique segment in this three-quarter art, not a horizontal line; these are art-derived attachment guides, not a mechanically validated rotation rig. If using a simple horizontal pivot, use the midpoint y (crate187, sea186, captain196.5 px) and tune the perspective/lift in IMGUI. Lid/front separation is traced independently, including the hanging latch; do not use its lower edge as the rear hinge. Closed draws base/lid; open draws base/interior/lid, as approved by Claude in comms.md. All layers retain the same full-canvas alignment.
