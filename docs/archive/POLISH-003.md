# POLISH-003 — authored fishing location and water evaluation

Mo rejected POLISH-002's UI, water and scattered scenery. Functionality is
preserved, but the visual work is not accepted. Judge the next complete location
against the original goal renders before expanding content.

The existing Ubuntu artist acknowledged ART-011 and began work after safely
committing ART-010 as 1c53bc8. No new subagent was created. Brief:
Catchline-art-style/Art/TASKS/11-authored-fishing-location.md.
ART-009 and ART-010 remain unintegrated in Unity.

Artist owns the complete bounded coastal diorama: connected warm stone coast,
vegetation, deliberate harbour details and shallow shelves around a clear central
channel. Camera coverage determines dimensions. Seven terrain material slots and
environment placement (0,-.32,0) are acknowledged in comms.md. Windows owns live
water, faithful UI and runtime integration.

## Water research

Plunder_The_Seas was inspected read-only. It contains an adapted Boat Attack
package 2.0.0-preview.5 declaring Unity 6000.3 and URP 17.3.0, matching Catchline.
Its existing captures show reflective moving water at a different camera angle.

- Upstream: https://github.com/Unity-Technologies/boat-attack-water
- License notice: Unity Companion License; preserve license and notices.
- Terms: https://unity.com/legal/licenses/unity-companion-license

Second candidate: https://github.com/MatrixRex/Uber-Stylized-Water
Evaluation commit: 1fdd16c6312611fef7fb248dee86cdd3fd456a1e.
MIT license; retain MatrixRex notice and Cyanilux custom-lighting MIT notice.
Its docs advertise Unity 6 URP, depth colours, shoreline/intersection foam,
refraction and caustics. Source explicitly branches for orthographic depth.

## Isolated studies

Only Catchline-sim contains candidate packages/assets and study editor scripts.
Main Packages, player scenes, pipeline settings and preview executable have not
been replaced by these candidates. Scratch includes added package dependencies
and compatibility-mode settings for the Boat Attack study. Before regular checks,
restore/sync scratch configuration deliberately: check.ps1 mirrors Assets except
Resources, and does not mirror Packages.

Boat Attack's exact-camera editor study did not show a working water surface.
Its buffers/caustic passes lack RenderGraph implementations; scratch compatibility
mode alone did not resolve the missing surface. This remains unresolved, rather
than proof that the package cannot work.

The Matrix subset initially lacked a relative custom-lighting include. Its
original include and MIT notice were added before repeating the study. Subsequent
captures compiled and rendered the surface; tuned variants show moving-pattern
inputs and wave/depth controls, but still fall below the original visual target.
No motion acceptance is claimed from a still. Logs: scratch Logs/matrix-water-study-*.log;
latest image: Logs/water-study/matrix-ortho.png. Source experiments are retained in
scratch Assets/Editor/MatrixWaterStudy.cs and WaterStudy.cs, with checkpoint copies
under main Logs/polish-003-water-study. Studies render actual Unity camera geometry
without HUD; they do not establish playable-preview or visual acceptance.

## Remaining acceptance work

Review the artist's composition, integrate selected water and authored seabed,
rebuild fishing UI faithfully to the cream/navy illustrated references, then check
animated player captures at desktop and landscape-phone sizes. Depth and biome
controls must visibly change water. Preserve fishing, carry/stow/return and saves.
