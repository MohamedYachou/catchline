Mo's current direction, 2026-10-16: use the actual PTS/Boat Attack water if
compatible, with NO white wave wash/foam, and show it now on the Catchline map.
Windows is testing the original PTS package/settings on the existing harbour
map in scratch, in background only. Keep the ART-012 map geometry checkpoint;
do not compensate model colours/geometry for the outgoing coastal shader or
start more map expansion while this water choice is being established.
No foreground Unity, Blender or preview windows: Mo is taking school notes.
The final runtime water screenshots will be the integration reference.

## WATER-005 — current direction and implementation

Mo asks for clean blue stylized 3D water, rounded visible wave shapes and little
white. Codex 2 is separately working on the skiff; no further map authoring is
being requested by Windows against the previous water.

The active main shader is now `Catchline/PTS Water`, a bounded adaptation of the
actual local PTS/Unity Boat Attack HLSL and packed normals. Reproduction script:
`docs/tools/port_pts_water.py`; upstream notice/license and hash receipt are in
`Assets/Art/Shaders/PtsWater/`. PTS source remains unchanged. Main pipeline
settings/package manifest are unchanged. Scratch's experimental package was
archived and its original manifest/project settings restored before normal tests.

PTS WorldMap clean preset inspected directly: amplitude .12, wavelength11,
heading35, micro .055, absorption(.06,.76,.8), scattering(.025,.31,.43), foam .035.
Catchline uses the same optical/shading basis with shorter wavelengths for its
boat-sized camera patch; foam is forced to zero. Orthographic depth/view and
Forward+ lighting fixes are needed for this camera/renderer. An identical preset
alone does not give an identical image under a different angle, scale and seabed.

Prior `check-pts-integrated.log` passed native shader/integration checks and
rendered all five maps at desktop1440x900 and landscape844x390, plus twenty
water-only-clock frames. Those show functioning animated PTS water, but remain
an intermediate look. WATER-005 reduces the small noisy highlights, tunes blue
colour, and strengthens rounded geometric waves. Latest verification is pending.
No native HUD input acceptance or current-water mobile performance claim.

WATER-005 verification update: `check-water005-regression.log` passed with Unity
exit0, including PTS integration/mipmaps, all five travel routes and menu/haul
state checks. `check-water005-clean-blue.log` passed all-map native capture.
Water-only clock frame0/10 mean RGB difference was(6.510,5.150,4.211)/255;
boat/camera were frozen. This establishes visible animation, not frame rate.
The intermediate animation is `docs/screens/polish-004/pts-water/water005-clean-blue.gif`.
A last rounded-height colour pass is being rendered: broad colour rolls follow
actual Gerstner displacement, with foam still hard zero. No claim of final visual
acceptance, current native HUD review or mobile performance proof.

Final WATER-005 render for this iteration: `check-water005-rounded.log`, Unity
exit0, PTS WATER INTEGRATION CHECKS PASSED. Full five-map desktop/landscape-phone
capture completed; harbour, kelp, sandbar, rocky and deep views inspected across
this pass. Current animation: `docs/screens/polish-004/pts-water/water005-rounded.gif`.
Twenty native1080x675 frames at .16s, frozen boat/camera, water clock only; mean
frame0/10 RGB change(6.327,6.729,6.420)/255. This is a scene-camera render without
IMGUI HUD. Full regression passed immediately before the last shader-only colour
adjustment; final shader then passed native compilation/integration and capture.
The visual is a reviewable iteration, not Mo's accepted final water. Current mobile
performance, native HUD and physical boat-following-wave motion are unverified.

## WATER-006 — supplied game-reference direction

Mo supersedes the large-wave request: small overlapping ripples and soft broken
reflections, clear shallows, no foam. The boat remains steady, so large water
swells look disconnected. Geometric amplitude is reduced from .26 to .035;
shorter crossing waves and packed moving surface normals carry the texture.
Height-based broad colour rolls are removed. Native verification in progress.

WATER-006 visual comparison: native equal-clock captures at detail scales .8,
1.6 and3.2 were inspected. .8 is selected for broader, softer overlapping facets
rather than fine grain. Packed normals carry the surface detail; five shallow
crossing waves retain only .035 base amplitude (roughly centimetres of motion).
Blue depth/refraction remains; no height-based broad bands and foam hard zero.
`check-water006-ripples.log` and `check-water006-surface.log` both passed with
Unity exit0. Final chosen-setting capture `check-water006-reference` is running.
No changes to boat movement, ship progression, UI, pipeline settings or PTS source.

Final WATER-006: `check-water006-reference.log` passed, Unity exit0 / PTS WATER
INTEGRATION CHECKS PASSED. Current chosen-setting native animation:
`docs/screens/polish-004/pts-water/water006-reference.gif` (20 actual1080x675frames,
.16s/frame, only water clock changes). Full five-map1440x900/844x390 capture
completed; harbour desktop/phone, sandbar phone and deep desktop inspected.
Water-only-clock mean frame0/10 RGB change(2.914,1.675,1.219)/255. Captures omit
IMGUI HUD and are not a hardware performance test. Real save and both pipeline
settings hashes still equal recorded baselines. Supplied third-party references
are retained as water006-user-reference-{day,sunset}.png for visual guidance only,
not shipped game assets. Temporary WATER-006 source backup removed after checks;
older native-acceptance backups remain separate. No commit.

### WATER-007 — slower ripples and coupled hull motion
Mo asks for slower motion and subtle natural boat response. Surface/Gerstner
clock now runs at65% of WATER-006 speed. Boat pose samples the same five Gerstner
height terms at the centre and across the hull, averages short ripples, and fits
small pitch/roll capped at.8degrees. This replaces unrelated sine bobbing. Full
hull-centre pivot correction preserves deck/route position while rocking. Crew,
rods, deck fish and fittings inherit the boat transform; gameplay grid unchanged.
Foam remains zero, ripple scale/colour preserved. Approximate visual buoyancy,
not a rigidbody/fluid simulation; tiny horizontal Gerstner offset is not inverted.

Verified: `check-water007-coupled.log` and `check-water007-regression.log`, Unity
exit0. Full first-voyage/skiff/automation/sale/menu/route/map regression passes.
New native invariants: pause freezes boat/water, eight seconds of heave stay below
.055m with nonzero movement, and hull-centre horizontal position does not drift.
Route assertions now measure hull centre rather than the rocking deck-grid corner.
Current capture `docs/screens/polish-004/pts-water/water007-coupled.gif`:40 native
1080x675frames at.16s/frame, actual boat and water ticking together, fixed camera.
Phone844x390 inspected. No HUD/current mobile FPS acceptance implied. Save and
pipeline hashes unchanged. All verification stayed hidden.
