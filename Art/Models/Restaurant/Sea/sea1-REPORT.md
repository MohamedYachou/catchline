# RESTAURANT-SEA-1

Delivered `sea1-night-water-1024.png` and `sea1-night-water-2048.png`: deep navy painted night water with fine blue/turquoise ripples and sparse warm gold lamp glints, following the surrounding sea in `Art/Source/Restaurant/concepts/ui-service-desktop.png`. Both are opaque RGB, sRGB. Use Repeat wrapping with bilinear or trilinear filtering.

Built-in imagegen painted the selected fourth candidate at1254 square. Exports use mechanical Lanczos resize to1024/2048;2048 is an upscale, not native generation. No procedural painting, edge replacement or texture synthesis. Four unmodified generated candidates and exact prompts are retained in `sea1-provenance/`. Candidates1–2 showed stronger joins; candidate3's quiet borders created a dark grid in repeat and was rejected. Candidate4 retained ripple density through the joins and had the best visual repeat.

`sea1-tiling-proof-1024-2x2.png` is an unaltered2048-square repeat proof, and `sea1-tiling-proof-2048-2x2.png` is4096 square. Compact `sea1-tiling-review-*.jpg` contacts were opened at1024 display size. There is no broad blank border or dark grid in the chosen repeat. Opposing pixels are not mathematically identical: edge mean absolute RGB differences on0–255 are x5.58/y4.78 for1024 and x5.79/y5.10 for2048. These are recorded honestly in `sea1-texture-audit.json`; this delivery claims a visually reviewed repeat at the shown game scale, not exact periodic pixel equality. A small fine-ripple discontinuity can remain under magnification.

`Sea1-V4-check.blend` is a packed additive copy of the accepted `Stage1V4/RoomLook3-Check.blend`. Its current saved V4 cameras produced `renders-sea1/sea1-room-1440x900.png` and `sea1-room-844x390.png`; both were opened. Water uses global XY position with an8m repeat, roughness0.8 and emission strength0.55, no extra reflection overlay. Gold glints are part of this single new base tile. Adjust repeat/intensity in the game material as needed. Source room, furnishings, lights and camera definitions were preserved. `sea1-blender-check.json` records the source hash and exact camera settings.

Opened `sea1-review.jpg`: painting reference beside desktop proof, both repeat contacts and phone proof. The water reads as darkblue behind the warm room with small broken glints; it keeps the warm interior prominent. These are Blender checks, not native game acceptance.

Reproduce texture exports/proofs using `sea1-package.py`; render with Windows Blender5.2 using `sea1-run.py sea1-check`. Decode/dimensions and final artifact hashes are recorded in `sea1-final-audit.json`. Accepted `night-water-2048.png`, `lantern-reflections-additive-2048.png` and their proof files remain untouched; all delivery paths are additive and prefixed sea1/Sea1.

No Assets, code, metas, git, save or accepted scene edits. Unity import, material setup and final in-game acceptance remain with Claude. No temporary backups were needed.
