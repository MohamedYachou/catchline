# Illustrated coast and stern net — CHART017

Codex 1 (Windows app), 2026-10-16. Replaces the rejected vector chart with Mo's
supplied illustration style. Built-in imagegen edit; no CLI/API fallback.

Project artwork: `Assets/Resources/Charts/gull-coast.png` (1672x941). Original
generated output is retained under `.codex/generated_images/01a1436e-bb92-7922-91a0-f5baf6467f26/exec-5b63d252-d17b-4e2f-8dbf-260eae602e06.png`.
Supplied reference is archived at `docs/screens/chart017/map-reference.png`.

Full-screen native overlay uses real selected ground, prices, wallet, day/time,
hold count, chart purchase and contracts. All navigation buttons lead to existing
game screens. Boat returns to the physical harbour boat; Gear opens Chandlery,
Crew opens Crew Office, Port opens Market. Inspect a pin before selecting/buying.
Close the map with Boat/home to use the existing Set sail action. No fabricated
compass/depth/precise-distance claims; the landmarks follow the illustration.

Floating net panels are centered behind +X stern, clear by.65m, with two attached
ropes; the small stationary net visual fits within2.2x1.35m. Actual moving-water
frames verify stern clearance/centering. Catch timing/yield/tear mechanics and
Codex2's completed CREW016 actor/portrait changes are preserved.

## Verification

`check-chart017.log` exit0: native chart image/fullscreen, all five real marker
actions, insufficient funds, purchase once, known selection, contract cap/stale
callback, live wallet,44pixel targets and navigation at1920x1080/1440x900/844x390;
stern/rope/bob checks over100frames; existing net-haul and crew-polish tests;
separate Chart017 build. `check-chart017-review.log` exit0 after actual visual
critique corrected transparent card padding and reference-raster caption sizing.
Final startup helper is opt-in/session-only; final build and standalone result
are recorded in comms.md. Native world+Canvas screenshots in docs/screens/chart017.

Separate preview: `C:/Users/momoy/Projects/Catchline-sim/Builds/Chart017/Catchline.exe`.
Launch flags `-netboat-trial -chart-review -native-display` start directly at the
map with the isolated compact fisher/200coins/3crew trial. No normal save override.
Background checks do not establish physical touch feel, mobile GPU performance,
whole-image pixel parity or Mo's visual acceptance. The artwork fills landscape
ratios; geography is stretched with the native overview to keep all landmarks
visible. Secondary text remains small on narrow landscape phones.

Codex2 independently completed CATCH018 during this pass. All seven released
reward runtime files byte-match main and the scratch snapshot used by the final
chart build; reward verification remains documented by its lead in CATCH018.md.
No reward source was edited here. Existing uncommitted work kept; no commit,
staging, reset or push.

## Final generation prompt

Use case: precise-object-edit. Asset type: production Unity game illustrated world-map BACKGROUND, landscape16:9, high-resolution. Edit target: attached coastal game-map screenshot. Preserve its EXACT richly detailed colorful miniature3D/painterly illustration style, water texture, lighting, perspective, geography, cliffs, shallow turquoise reefs, fish silhouettes, kelp on upper-left bank, dark deep-channel trench upper-centre/right, pale sandbar on right, rocky coast lower-left, charming Gull Harbour wooden docks/red-roofed village/lighthouse at bottom centre, clouds framing outer corners. Change ONLY by removing EVERY UI element: all cream panels, all text/numbers, top HUD, bottom navigation, location cards, all map pins/circular icons, dotted white route lines/arrows. Seamlessly reconstruct the underlying original water/harbour terrain behind those removed elements. Keep the little harbour buildings and buoy within deep channel; remove the central sailing boat/wake (we draw live routes and boat separately). Final artwork is edge-to-edge clean finished scenery with NO WORDS, NO SYMBOLS, NO LABELS, NO UI, no flat vector simplification. Same original visual richness, vibrant sapphire and turquoise water with crisp stylized wave shapes and white shoreline accents, golden sunlight, honey wooden harbour. Do not reimagine composition or move landmark regions. Preserve landmarks at their original normalized positions: harbour .48,.76; kelp .22,.29; sandbar .83,.42; rocky coast .12,.60; deep trench .60,.15; harbour-mouth open water .46,.48. This is a clean background plate for dynamic UI overlays, not a UI mockup.
