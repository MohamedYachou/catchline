# FishRodFP — first-person fishing rod

Codex 2 (WSL CLI), 2026-10-24. Delivery for FISH-ROD-ART-1. Source and export are metres; the butt-to-tip rod length is 2.1 m.

- [Blender source](FishRodFP.blend), [FBX export](FishRodFP.fbx), [256 × 256 atlas](FishRodFP_Atlas.png).
- One skinned mesh, one material, **5,878 triangles**, fourteen bones, eight connected bend bones, six line guides.
- Navy oilskin, captain-style gold cuff stripes, mustard gloves/orange cuffs, honey cork, ivory line and satin steel. Atlas swatches preserve the house palette, including `#173F57`, `#2A6685`, `#E6AD38`, `#E36A35`.
- The left glove wraps the forecork; the right glove cups the crank knob. Extended sleeves continue below the player frame when the rod rises.

## Clips

All actions are authored at 40 fps, starting at source frame 0. Configure Generic animation and the indicated loop flags on import.

| Action | Frames | Seconds | Loop | Motion |
|---|---:|---:|---|---|
| Idle | 0–80 | 2.0 | Yes | Slow restrained sway |
| Cast | 0–36 | 0.9 | No | Upward wind-up, forward flick, settle |
| Hold | 0–40 | 1.0 | Yes | Quiet held rod with light tip weight |
| Twitch | 0–16 | 0.4 | No | Small tip response |
| Strike | 0–10 | 0.25 | No | Sharp upward yank and loaded tip |
| Reel | 0–32 | 0.8 | Yes | Full crank revolution, turning spool, wrist follows knob |
| Lift | 0–48 | 1.2 | No | Raised rod for landing |

## Integration for Codex 1

Import only `FishRodFP.fbx` and the atlas into the runtime project. The FBX contains only `FishRodFP_Rig` and `FishRodFP_Mesh`; the water, camera, lights and review chain are excluded. Set the atlas to sRGB, clamp wrapping, and assign it to the game's opaque lit material. Source roughness is 0.57. No runtime fishing line, bobber, fish or effects are included: draw the real line from `LineTip` to the actual bobber.

`RodRoot` moves the held assembly. `GripHand.L` supports the grip. `ReelHandle` is the crank pivot; `ReelSpool` turns the spool. `ReelHand.R` is a child of the crank, so its centre follows the knob. In Blender a rotation constraint keeps this wrist upright; FBX clips bake that compensation. Use the baked Reel clip, or supply the same wrist counter-rotation when driving the crank procedurally. Unity does not import the Blender constraint itself.

`Rod_01` through `Rod_08` form the connected bend chain; `LineTip` follows the last bone. Positive **local X** bends toward the water. At full bend, the per-bone rotations in radians are `[0.01, 0.035, 0.06, 0.09, 0.13, 0.17, 0.22, 0.26]` (degrees approximately `[0.57, 2.01, 3.44, 5.16, 7.45, 9.74, 12.61, 14.90]`). Scale these by the bend amount and compose them with the clip pose in the appropriate animation layer/LateUpdate. Preserve bind rotations; do not replace imported local rotations with global Euler values. The blank has 65 cross-sections and continuous cubic B-spline weights, with at most four influences per vertex. The tip is fully attached to `Rod_08`.

Authoring axes are **−Y forward, Z up**; screen-right in the authored forward view is −X. The FBX exporter uses **−Z forward / Y up**, metre units, no leaf bones, no animation simplification, and baked actions. Unity placement, handedness and final camera matching remain Codex 1's integration checks. No Unity import was performed here.

The saved review camera is at `(0.34, 1.15, 0.30)`, looking at `(0.34, −4.00, −0.75)` in source coordinates, 24 mm on a 36 mm sensor. The rod enters from the lower right, leaving open water on the left. Do not use these Blender coordinates directly as Unity transforms; frame the imported assembly against the actual game water. `build-manifest.json` records the full camera/export/control contract.

## Review evidence

Every final image below was individually opened. The player views show the two gloves enclosing their respective grip/knob and the reel below the rod. Cast, strike and lift raise the rod; the upper tip naturally leaves the player frame in raised poses, so separate complete-pose views show the entire asset. Reel quarter-turn views check that the crank stays under the right glove. The three bend views and offset orange chain views show progressively increasing curvature toward the tip; the overlays are review-only.

| View | Evidence |
|---|---|
| Player, desktop / phone | [1440 × 900](renders/player-idle-1440.png), [844 × 390](renders/player-idle-844.png) |
| Idle / Hold / Twitch | [Idle](renders/action-Idle-20.png), [Hold](renders/action-Hold-20.png), [Twitch](renders/action-Twitch-04.png) |
| Cast wind-up / flick | [Player wind-up](renders/action-Cast-12.png), [player flick](renders/action-Cast-25.png), [complete wind-up](renders/pose-Cast-12.png), [complete flick](renders/pose-Cast-25.png) |
| Strike / Lift | [Player strike](renders/action-Strike-06.png), [player lift](renders/action-Lift-48.png), [complete strike](renders/pose-Strike-06.png), [complete lift](renders/pose-Lift-48.png) |
| Reel quarter turns | [0](renders/action-Reel-00.png), [¼](renders/action-Reel-08.png), [½](renders/action-Reel-16.png), [¾](renders/action-Reel-24.png) |
| Bend 0 / 0.5 / 1 | [0](renders/bend-0.png), [0.5](renders/bend-0_5.png), [1](renders/bend-1.png) |
| Bone chain 0 / 0.5 / 1 | [0](renders/chain-0.png), [0.5](renders/chain-0_5.png), [1](renders/chain-1.png) |
| Orthographic / contact | [Side](renders/side.png), [top](renders/top.png), [hands and reel](renders/hands-detail.png) |

`validation.json` records the final saved-source reopen and actual FBX import: **PASS**, 269 integer-frame poses across all seven clips, maximum bone difference 0.001721 mm and vertex difference 0.001352 mm. Source frame 0 is compared with the imported clip's first frame (Blender's FBX importer starts at frame 1). Loop endpoints, normalized weights, atlas resolution and exclusion of the review stage also pass.

`receipts.json` lists all 26 reviewed image dimensions/hashes and delivery/source hashes. `build.log` and `validation.log` preserve Blender output. `contact-review.log` records the final wider contact-camera render; `review_contact.py` refreshes that evidence without altering the saved source or FBX. Blender 5.2 emits API deprecation notices for future 6.0; they do not affect this delivery.

The acceptance here is the authored asset and its actual FBX round trip. These Blender renders use an isolated sea stage, not the native minigame/HUD. No Unity material, installed-player, touch-input or full game-camera acceptance is claimed.

## Rebuild

Use Windows Blender 5.2.1 LTS (the existing Linux Blender installation has an incomplete FBX operator). From the checkout, run Blender background with six threads and `--python Art/Source/FishRodFP/build.py -- --render all`, using an absolute Windows script path when launching from WSL. Then run `validate.py` with Blender. After opening/reviewing every final PNG, run `receipts.py` with ordinary Python. Scripts are in [Art/Source/FishRodFP](../../Source/FishRodFP/).

No other models, Unity Assets, scenes or saves were changed. No commit or push; the lead can review and commit these two new asset/source folders.
