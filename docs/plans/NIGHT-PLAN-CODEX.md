# Night plan: Codex (models, 2D art)

Codex works on the **art/style-pass** branch in the worktree `C:\Users\momoy\Projects\Catchline-art-style`, running unattended. Claude checks in every hour: it merges what Codex has pushed into `proto/deck-sim`, wires it into the game, and restarts the queue if it stalls.

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
