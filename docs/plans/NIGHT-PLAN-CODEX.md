# Night plan: Codex (models, 2D art)

**Current status, 2026-10-15:** GPT-6.1 Sol medium completed tasks05–08 on **art/style-pass**, and parent Codex reviewed and merged the results into `proto/deck-sim`. The queue is stopped with no outstanding asset task. The original unattended workflow and briefs are preserved below; see the recovery section for validation and remaining integration work.

## Queue

The runner is `Art/TASKS/run-queue.sh`, started detached in WSL. It runs one `codex exec` per task and writes:
- the queue progress to `Art/TASKS/queue.log`
- each task's log to `Art/TASKS/<task>-log.txt`
- a done marker per task in `Art/TASKS/done/`

| # | Task file | What | Why it matters for the morning |
|---|---|---|---|
| 04 | `04-detail-dressing-and-skiff.md` | Detail pass, world dressing, sea modules, plaice and cod, the skiff kit | **Done** (`3ddbe1f`) |
| 05 | `05-ui-pass-2.md` | Logo, title backdrop, shop headers, fish portraits, item icons, illustrated sea chart, crew portraits, feedback sprites | Screens look like the mockups |
| 06 | `06-crew-rig.md` | Rigged chibi crew, outfits per role, hats, 11 animation clips | Replaces the capsule people |
| 07 | `07-upgrade-visuals-and-world-polish.md` | Upgrades visible on the boat, hill backdrop, shipyard shed, NPCs, sea landmarks, a whale tail | A world that feels lived in |
| 08 | `08-day-boat-and-textures.md` | Day boat (hull 3) and its stations, stylised water textures | The next ships, and nicer water |

## Recovery and completion — 2026-10-15

Mo asked Codex to take over gameplay/design and a GPT-6.1 Sol medium subagent to take the assets. The old queue had incorrectly marked usage-limit failures as completed. Its control flow is fixed and validated; it has not been restarted.

- **05 complete:** recovered UI compositions and all39 additions validated (83 total). Imported into the main art library; title/chart/portrait UI wiring remains on the gameplay plan.
- **06 complete:** skinned crew, four outfits, three hats,11 clips; Blender/FBX and actual Unity clip/skin checks passed. Captain, deckhands and fishermen now use it.
- **07 complete:**31 upgrade/world assets validated and merged. World dressing uses the existing scene hooks; big cooler and upgraded rods now visibly replace their starter variants. Market display and bench seating were reviewed and corrected.
- **08 complete as assets:** day boat plus nine stations, seven textures, sources, previews, reports and round-trip/seam/alpha validation delivered. Day-boat gameplay and applying water textures remain future integration work.

Reports: `Art/Models/CrewRig/REPORT.md`, `Art/Models/WorldPolish/REPORT.md`, `Art/Models/DayBoatKit/REPORT.md`, `Assets/Art/Textures/TEXTURES.md`. New palette names only `M_HairChestnut` and `M_HairSilver`, both added to the runtime remap. Continue the main plan's C and remaining D items next; there is no pending item in this asset queue.

## Rules Codex follows (in every brief)
- Blender sources, FBX exports, previews, contact sheets and a REPORT for every batch.
- Existing FBX names, part names and pivots never change; upgrades are made in place.
- Materials only from the `M_*` palette. New colours go in STYLE.md and are listed in the REPORT, so Claude adds them to the game's remap.
- Never open Unity, never touch `Assets/Scripts` or `Assets/Scenes`. Push from WSL after each part.

## If the queue stops
Check `Art/TASKS/queue.log`. To restart, from Windows:

```
wsl.exe -d Ubuntu -- bash -lc 'cd /mnt/c/Users/momoy/Projects/Catchline-art-style && setsid nohup ./Art/TASKS/run-queue.sh >/dev/null 2>&1 </dev/null &'
```

Finished tasks are skipped. To add work, write a new `NN-name.md` brief and append it to `QUEUE` in the script.
