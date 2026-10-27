# RESTAURANT-SEA-1C — brighter painted water

Codex 2 (WSL CLI). Source delivery complete; native Unity import/acceptance remains Claude's.

## Delivery

- `sea1-night-water-1024.png` and `sea1-night-water-2048.png`: opaque RGB, azure/mid-blue water, cyan ripples and small warm gold glints. These replace the too-dark SEA-1B tiles. Original `night-water-2048.png` and additive lantern tile are untouched.
- `sea1-package.py` now calls `sea1c-package.py`. Historical sea1/sea1b package scripts and audits remain provenance; their hashes for the three replaced files are superseded.
- `sea1c-review.jpg`: painting and native r127 BEFORE paired with Blender AFTER desktop1440x900 and phone844x390. `sea1c-before-after.jpg`: identical-camera Blender comparisons and texture comparison.
- `sea1c-tiling-proof-{1024,2048}-4x4.png`: native4096/8192 repeats. Compact reviews and seam-intersection4x nearest zooms provided at both sizes.
- `sea1c-V4-check.blend`: packed additive check scene. Production Stage1V4 scene unchanged.

## Art production

Used builtin `image_gen.imagegen`, not CLI. Exact submitted prompt: `sea1c-provenance/prompt.txt`; generation metadata and selected raw candidate in that directory. Target was the previous sea1 tile; style reference was `Art/Source/Restaurant/concepts/ui-service-desktop.png`, water only. Generated candidate is1254x1254:2048 delivery is explicitly a Lanczos enlargement, not native2K generation. Python performs only resize, constrained seam correction, comparison layout and measurements; no artistic repaint.

Symmetric opposing-edge mean correction falls to zero through1/32-width bands (32/64px), leaving the interior unchanged. Explicit identical endpoint pixels survive PNG encoding. Exact periodic boundary values do not assert that every ripple is analytically periodic in its derivative.

## Verification and review

Independent decoded-file audit passes exact X/Y edge and corner equality at both sizes; all16 cells in each native4x4 proof equal their delivered tile. RGB dimensions/modes pass. Mean weighted sRGB brightness116.53/255 versus32.25 previously,3.61x (a display-space comparison, not physical luminance); no pixels under30 weighted brightness. Packed scene texture bytes independently match the delivered2048 PNG.

Both compact4x4 repeats, both seam zooms, both V4 camera renders and both comparison sheets opened and reviewed. Water stays visibly blue at phone scale; cyan facets and sparse warm glints remain legible without a black base. Some repeated gold motifs remain inherent in a repeating tile. Room/station/actor geometry is unchanged.

The Blender comparison uses the same scene, camera and water settings as SEA-1B:8m repeat,roughness.8,emission strength.55. Native r127 is BEFORE evidence only. The native material/shader, colour space, exposure, UI framing and lamp reflection overlay still require Claude's import check; no native AFTER acceptance is claimed. Original additive reflection tile is not layered in the Blender proof.

`sea1c-independent-audit.json`, `sea1c-texture-audit.json`, `sea1c-packed-audit.json`, `sea1c-blender-check.json`, `sea1c-visual-review.json` and `sea1c-final-audit.json` provide the evidence. Temporary original backup removed after verification; baseline hashes and a reduced512px BEFORE review remain. No Assets, gameplay code, git or commit.
