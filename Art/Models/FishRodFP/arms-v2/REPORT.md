# Optional anatomical arms — FISH-ARMS-2

Codex 2 (WSL CLI), 2026-10-25. Staged for Claude's review; reinsertion into the game requires Claude's acceptance. Rod-only is separately complete in [rod-only/REPORT.md](../rod-only/REPORT.md).

[Editable source](../FishRodFP_ArmsV2.blend), [FBX](../FishRodFP_ArmsV2.fbx), [shared atlas](../FishRodFP_Atlas.png). One mesh/material, **6,574 triangles** (2,712 new arm triangles plus 3,862 rod triangles), 33 bones, seven 40 fps clips. Original root v1 and rod-only assets remain unchanged. Exact original files and source/evidence are archived with hashes in `../iterations/v1/`.

Fixed shoulders sit just outside the inherited eye camera; each arm has a bent elbow, tapering navy oilskin, sleeve folds, rolled cuff, captain stripes and exposed wrist. Mustard gloves have three closed finger groups and opposing thumbs. The screen-right **right hand encloses the forecork**, and the screen-left **left hand turns the crank knob**. The reel/rest equipment is mirrored across source X relative to v1 to establish that handedness. Continuous glove surfaces replace intersecting shell seams.

## Rig and integration contract

The original fourteen rod/reel/bend bone names are retained. `ArmRoot` adds UpperArm, Forearm, Hand, Fingers1/2/3, Thumb, WristTarget and ElbowPole for each `.R` and `.L` side. WristTarget and ElbowPole are helper bones; fixed-shoulder two-link IK is solved in the authoring script and **baked** into each clip at 40 fps. An active Blender IK constraint is not required at playback. The finger groups have separate skin bones in their closed grip pose. The right hand follows RodRoot; the left follows the rotating crank position while retaining the rod's wrist orientation.

The existing Idle 0–80, Cast 0–36, Hold 0–40, Twitch 0–16, Strike 0–10, Reel 0–32 and Lift 0–48 actions retain their durations. Idle/Hold/Reel loop. Rod_01..08 and LineTip retain the inherited bend chain. New arm bones do not follow the rod-tip bend; their contact is on the rigid grip/reel assembly. Use the baked clips or re-solve the arm chains if driving hand targets procedurally.

Source axes are X lateral, −Y forward, Z up; source −X appears screen-right. The exporter uses −Z forward/Y up, metre units, no leaf bones, no animation simplification, and excludes camera/water/lights. Import as Generic animation, use the existing atlas and retain bind rotations. No Assets or Unity edits were performed.

## Evidence and limits

`validation.json` records **PASS** over all 269 integer-frame poses, including an actual FBX reimport. Maximum bone difference is 1.721 micrometres and vertex difference 1.351 micrometres; source wrist contact error is below 0.4 micrometres, shoulder movement below 0.1 micrometres and loop endpoint differences below 0.2 micrometres. At most four normalized skin influences per vertex; one atlas material; no review stage objects exported. Original v1 and rod-only hashes match.

`renders.json` lists the exact inherited player camera, complete side and top views for eleven action poses (all seven actions, two cast poses and four reel quarters), both grip closeups, a phone view and a freshly rendered v1 comparator. Camera source position `(0.34, 1.15, 0.30)`, target `(0.34, −4, −0.75)`, 24 mm / 36 mm sensor. Player 1440×900, side/top/contact 900×700 and landscape phone 844×390. `v1-v2-comparison.png` puts the identical-camera Idle renders beside one another. Final review hashes are recorded separately after opening every image.

These are isolated Blender asset renders. FBX parity and analytic contact checks do not prove native material, actual game-camera/HUD, touch-input or player acceptance. Claude/Codex 1 own integration and native review. Intermediate failed glove renders/logs are superseded by the final hashes; do not use the earlier 5,926-triangle review as the current asset.

Final visual review: all 37 final pose/contact/phone/v1 images and the labelled same-camera comparator were individually opened (38 total). Closed contacts, elbow bends, sleeve taper/folds and wrists remain legible across the reviewed poses; no visible contact gaps or unintended intersections were found. `reviewed-images.json` binds that review to the final PNG and delivery hashes. Artist handoff is complete; Claude review and native acceptance remain pending.
