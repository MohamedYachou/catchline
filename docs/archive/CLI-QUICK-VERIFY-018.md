# Shared quick verification — VERIFY-018 — 2026-10-16

Codex 2 checked current main for Codex 1/2 without launching Unity, Blender,
a player or any desktop preview, using scratch, touching saves, or changing
runtime/art/water/settings. No git mutations. Fish asset agent remains finished.

## Confirmed now

- All **20 installed fish FBX/PNG files and metadata** match final delivery
  receipts. Established model/portrait GUIDs match the pre-pass backup.
- Ten model validation reports remain intact: **13,348 total triangles**.
  Their previously checked saved-source/FBX results still correspond to delivered
  hashes; this quick pass did not rerun Blender roundtrips.
- All portraits are RGBA 512×256 with transparent margins and whole silhouettes.
- Delivered gameplay/art source hashes are unchanged since the last verified pass.
- A fresh background Roslyn compile covers **all 26 current runtime sources**, the
  two fish checks and existing ArtImport against installed Unity assemblies:
  zero errors; one existing CS0108 warning for VoyageGame.audio.
- The isolated C# state regression passes, including new-fish payout/log updates,
  old-save array growth, bulk bait, free scraps and bait/pre-cast economy scenarios.
  It uses Unity math/data and JSON adapters, not native Unity JsonUtility.
- The main library's **202 existing GUID references resolve**; no duplicate GUIDs
  were found across current Assets metadata.

## Actual integration gap — Codex 1 pickup

The files are delivered, but **main's serialized ArtLibrary has not been rebuilt
for the latest deliveries**. Its timestamp is 2026-10-15 20:10 UTC. It lacks:

- Whiting, RedMullet, Turbot FBX references and their three portrait references.
- GullKelpBank, GullSandbar, GullRockyPoint, GullDeepChannel environment references.

HarbourMouth and seven original species remain registered. DeckActors has the
model-name fallback for new fish; VoyageScenery has all five environment names;
ArtImport discovers all model FBXs/UI PNGs and queues rebuild after model imports.
Those source hooks exist, but missing registry entries can still produce fallback
fish/scenery and absent portraits until native import/rebuild. No serialized FBX
file IDs were guessed or Windows-owned files overwritten.

When Codex 1 is ready, allow main import and use **Catchline → Rebuild Art Library**
(`Catchline.EditorTools.ArtImport.BuildLibrary`). This does not require switching
scenes; avoid PlaytestReady.Open merely to rebuild, since it also opens Voyage and
stops Play. Then stop/re-enter Play when Mo is ready to clear runtime caches.
Respect background-only preference; do not activate a window to do this now.

Run `FishContentChecks.Run` and `FishArtChecks.Run` through Codex 1's available
background native check flow after it releases its water-study scratch reservation.
FishArtChecks rebuilds its own library before testing all ten native models and
portraits. **Current check.ps1 does not recognize either check's success marker**:
its fallback expects `Snapshot written to`. Codex 1 should update its owned runner
or explicitly check nonfailure exit/log evidence and the real markers:
`FISH CONTENT STATE CHECKS PASSED` / `FISH ART IMPORT CHECKS PASSED`.
No scratch/runner edit or native check was performed by Codex 2 here.

## Codex 1 water and native acceptance

Main's saved WaterShader reference still resolves to **CoastalWater.shader**.
This confirms the saved main registry, not which scratch water experiment passed.
No PTS acceptance is inferred or water configuration changed. The default main
Editor.log is dated 2026-10-14 and cannot prove today's native import/play checks.
Native model/material/axis/scale/tail, actual UI/input/phone layouts, audio, shaders
and end-to-end trip/sale verification remain pending; use the prior content/art
checklists. This quick report does not claim all gameplay or visuals are accepted.

Evidence: `docs/checks/Verify18/{assets.json,integration.json,compile.log,state.log}`.

Codex 2 is idle after this check; documentation reservation released, no runtime
or art files held. Codex 1 may pick up import/rebuild/native verification. No new
content or polish queue started.
