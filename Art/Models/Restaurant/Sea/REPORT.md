# Painted restaurant night sea

Delivered `night-water-2048.png` (opaque RGB blue painted ripples) and `lantern-reflections-additive-2048.png` (RGB gold streaks on black for a separate additive layer). Both are 2048 square. Built-in imagegen created the artwork; original 1254-square outputs, complete prompts, receipts and selected seam-repair source are retained in `provenance/`. Delivery was Lanczos resized; this is not native 2048 generation. No procedural painting was used.

Use sRGB textures with Repeat wrapping and bilinear/trilinear filtering. The proof uses an 8 m base repeat, roughness0.74 and subtle emission0.65. Reflections are independent: black contributes zero under additive blending, and gain/UV placement can be adjusted per lantern. The proof places the layer12mm above the water surface, over an11.2x3.3m front-quay region, repeating twice across its width, with a material fade toward the room. Blender uses Transparent+Emission to preview the additive effect; Claude supplies the game material.

`NightSea-V4-check.blend` packs the textures and original room images. It is a review copy of `Stage1V4/LookProof.blend`, with original guests, lights, grade and both exact saved V4 cameras. Source scene is unchanged. Opened final `renders/night-sea-room-1440x900.png` and `renders/night-sea-room-844x390.png`: broad painted ripples and broken warm reflection columns remain readable at both sizes. The first overlay was below the water box top; this was corrected before final review.

Both2x2 contacts were opened. Repetition has no conspicuous border at the reviewed game scale, but opposing edge pixels are not identical. `texture-audit.json` records raw edge mean absolute RGB differences: blue x5.95/y6.86 and reflection x0.41/y7.46 on a0–255 scale. These are measurements, not a mathematical seamlessness pass. `visual-review.json` records reviewed artifacts and final hashes; `blender-check.json` records source hash, cameras and placement.

No Assets, code, metas, git, player save or production room edits. Native Unity integration and final in-game intensity remain with Claude. No temporary backups were required for these additive files.
