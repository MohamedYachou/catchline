# ART-012 — polish the existing fishing maps (2026-10-16)

Mo explicitly asks Windows to direct the existing WSL artist. Preserve your
existing CLI account/model/settings; no new sessions or app subagents. Work in
Catchline-art-style, art/style-pass. Read applicable guidance, comms.md,
Art/STYLE.md and original day03-small-boat.png. Windows owns water/shaders,
runtime, travel, sound and HUD. Do not edit these or use Catchline-sim while
Windows is running checks. No new content or gameplay expansion.

First close last night's working-quay/orientation handoff: inspect actual dirty
files, validate positive-X Unity landmarks using retained evidence (or report
the outstanding check), commit only finished source/export/report files and
record the delivery. Preserve main GUIDs and all dirty runtime/settings work.

Then improve the EXISTING locations, prioritising Kelp bank and Sandbar, which
Mo finds ugly. Replace floating flat kelp mats and scattered sand pancakes with
cohesive bounded dioramas at the existing camera: orthographic3.2, rotation45/35,
target(1.35,0,.20), 1440x900 and844x390; waterline local0/world-.32. Kelp should
grow from a shaped seabed with sparse broad underwater fronds, clear central
boat/cast channel and restrained surface tips. Sandbar should read as connected
warm sand shelves/sloping shoals, one exposed island/ridge, shallow lagoons and
purposeful coastal detail, not separate floating discs. Use coherent connected
terrain, readable silhouettes, canonical palette; report any needed new slots.
Apply the same bounded quality pass to existing Rocky point and Deep channel
after those two; use calm open-water depth for deep channel, not clutter.

Export self-contained environments named GullKelpBank, GullSandbar,
GullRockyPoint, GullDeepChannel in Assets/Art/Models/Environment, matching
HarbourMouth conventions/root/waterline, with placement manifests and per-map
sources/reports. Verify saved source AND actual FBX, camera/channel clearance,
triangle budgets and handedness. Import finished FBXs/manifests into main only,
preserving metadata; Windows adds runtime lookup hooks. Append START/DONE in
main comms.md, scoped art commit and 300–600 word checkpoint in
docs/CLI-ARTIST-HANDOFF.md. Technical checks do not equal Mo's visual acceptance.
