# Visual foundation — POLISH-002

Mo tested the core loop, then set a different development priority: finish a
small slice to the intended visual quality before adding more systems. Mo
confirmed close matching to the existing renders, led by the fishing view.
PRODUCT.md and DESIGN.md now record that direction; AGENTS.md carries it forward.

## Implemented

- Real title artwork and Catchline logo, gentle drift, a deliberate left menu,
  consistent pause/settings surfaces and readable navy Fredoka typography.
- Shared type hierarchy, icon spacing, cream cards, portrait crew strips,
  themed scrollbars, short shop tabs and supplied illustrated shop headers.
- Fishing resources regrouped, camera centred more deliberately, harbour-mouth
  scenery moved toward the edges, floating storage/debug-style labels removed.
- Supplied portrait reward frame, weight/value/new-species feedback, brief entry
  motion and no duplicate hooked toast after landing. Carry remains unobstructed.
- Illustrated sea chart and item icons wired into existing shops.
- Custom URP water: layered broad colour, authored tile detail, sparse curved
  moving highlights, broken hull contact foam, travel-only wake and splash rings.
  Flat moving white bars are removed when the water shader is available.
- Landscape HUD uses 540 layout units on a small window instead of squeezing
  the 720-unit desktop layout. Text-size settings change text while bottom
  actions remain anchored. Actual mobile-device touch/comfort testing remains.
- Water importer explicitly uses Texture2D/repeat/mipmaps, and the runtime art
  library holds shader/texture references so builds retain them. The new check
  rejects missing textures instead of silently showing an untextured fallback.

## Evidence

Unity 6000.3.25f1 on Catchline-sim. FirstVoyageChecks.Regression passes the manual
command loop, early-strike recovery, carry/stow/sale, upgrade price and save
roundtrip, old-save compatibility, skiff/refit/routes/fuel/rig, crew roles and net
automation. It also checks shader compilation and all seven imported water/effect
textures with repeating sea wrapping. The Windows standalone build succeeds.

`VoyageCapture` is an opt-in session-only presentation check. It drives real
game commands and captures actual player frames including OnGUI, then exits.
It does not mock up interfaces, load the main save or write preview progress.
Normal play does not activate it. Twelve states are captured at 1440×900 and
844×390: menu, harbour, fishing, waiting, bite, catch, stow, sale, gear, chart,
pause and settings. Evidence is under docs/screens/polish-002.

Review found and fixed the thick initial foam halo, crowded breakwater, duplicate
feedback, unthemed scrollbar and linear-project IMGUI text colour. Pixel evidence
for intended navy is (23,62,87), compared with the old (2,12,24). Shared font and
layout review replaced browser-only checks; the mechanical detector found no
issues in the C# UI targets, but its applicability to Unity is limited.

Logs: Catchline-sim/Logs/check-polish-002-texture-regression.log,
check-polish-002-texture-preview.log and final player capture logs. The captures
are scripted presentation evidence; Mo's next playtest judges comfort and feel.

## Try and steer

Run Catchline-sim/Builds/FirstVoyage/Catchline.exe. It starts a temporary fresh
session. Inspect the menu, then cast/catch/carry/return and visit Gear/Chart.
Look especially at whether the water feels calm and alive, the boat is inviting,
the bite is obvious and reward feedback leaves the next action clear.

## Coordination and remaining work

Ubuntu Codex's installed `queue` command was verified, its existing ChatGPT
login checked, and ART-010 delivered to the existing artist conversation
01a13eac-e066-72e2-b226-f7f85c5cf5d4 without spawning another agent. Its START
entry is in comms.md. Scope is exact-camera render comparison, in-place rowboat
detail and lighting/water reference sheets. Art contracts remain unchanged.

ART-010 geometry is not in this build yet. ART-009 f5ce155 remains separately
queued. Audio, a richer sale/refit transition, further harbour composition and
device-specific mobile polish remain; this is a reviewable visual foundation,
not a claim that the entire game has reached final art quality. Content growth
is deferred while Mo steers the small slice toward that standard.

## Player review supersedes this pass

Mo rejected this presentation on 2026-10-15. All three visual areas remain far
from his goal. Functional/build checks reported here remain valid for that WIP,
but do not establish visual acceptance. See DESIGN.md revised world requirement,
comms.md POLISH-003 and artist Art/TASKS/11-authored-fishing-location.md. Keep
source backup while replacement work is being evaluated.
