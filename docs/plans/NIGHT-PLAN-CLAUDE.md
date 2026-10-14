# Night plan: Claude (code, gameplay, UI)

Goal for the morning: a **beta-feeling build 1-2** of Gull Harbour that is enjoyable to play and looks as close as possible to the concept screenshots (`Art/Concepts/15-gull-harbour-tier1.png`, `17-hud-fishing.png`, `18-hud-harbour.png`), plus the start of build 2 (the skiff). Mo tests in the morning and steers. Codex works its own queue (`docs/plans/NIGHT-PLAN-CODEX.md`) in parallel.

Work top to bottom. Tick boxes as you go, commit after every item, push to `proto/deck-sim`. Keep a running log at the bottom of this file. The last task of the night is `docs/MORNING-REPORT.md`.

## How to work (read after every context reset)

- **Repo:** `C:\Users\momoy\Projects\Catchline`, branch `proto/deck-sim`.
  - Game code: `Assets/Scripts/Game/`. The art import and library builder is `Assets/Editor/ArtImport.cs`.
  - Design: `docs/GAMEPLAY.md`. Keep it in sync when mechanics change.
- **Mo's Unity editor may be open on this project, so never run batchmode on it.** Verify on the scratch copy `C:\Users\momoy\Projects\Catchline-sim`:
  1. `robocopy Assets → Catchline-sim\Assets /MIR /XD Resources`
  2. Run `Unity.exe -batchmode -quit -projectPath Catchline-sim -executeMethod Catchline.EditorTools.PrototypeTools.VoyageSim -voyages N -snapshotPath <Logs\x.png>` with Start-Process -PassThru and WaitForExit.
  3. Read the `[Catchline]` lines in the log, and the renders `x.png` and `x-harbour.png`.
  4. Exit code 3 is the licensing token and is harmless.
  5. Never delete only `Library\Artifacts` there. If you must reset, delete the whole Library.
- **Fast compile check** without Unity: run Roslyn from `Editor\Data\DotNetSdkRoslyn\csc.dll` via `NetCoreRuntime\dotnet.exe`. Use a .rsp file listing:
  - `Managed\UnityEngine\*.dll`, `UnityEditor.dll`, `NetStandard\ref\2.1.0\netstandard.dll`
  - `Library\ScriptAssemblies\Unity.InputSystem.dll`
  - `-define:UNITY_EDITOR`
  - all of `Assets/Scripts/**/*.cs` and `Assets/Editor/*.cs`
- **Importing Codex art:**
  1. `git merge --no-edit <commit>` from `art/style-pass`. Codex pushes from WSL; the local branch ref may lag, so use `git fetch origin art/style-pass` first.
  2. Write `.meta` files for new files under `Assets/Art` immediately: folder metas with `folderAsset: yes`, file metas with `guid: md5(path)[:32]`.
  3. Add the new models to `ArtLibrary` (field) and `ArtImport.BuildLibrary`.
  4. Run the sim on the scratch copy.
  5. Copy back `Assets/Resources/ArtLibrary.asset` and the `Assets/Art/**/*.meta` files from the scratch copy.
  6. Commit.
- **Material rule:** the game remaps model materials by palette name (`ArtLibrary.PaletteHex`). If Codex reports a new `M_*` colour, add it there.
- **Don't** use `python` heredocs in Bash (it hangs). Use the Edit or Write tools, or sed.
- **Codex:** queue runner `Art/TASKS/run-queue.sh` in the art worktree (`C:\Users\momoy\Projects\Catchline-art-style`), log `Art/TASKS/queue.log`. Check it at every check-in:
  - If no codex process is running (`wsl.exe -d Ubuntu -- pgrep -f "codex exec"`) and tasks remain, restart the runner.
  - Merge whatever has been pushed.

## Items

### A. Import and wire Codex's art as it lands
- [ ] A1. Task 04 part B dressing kit:
  - shop fronts at each shop door
  - barrels, crates, fish crates and a net rack on the quay
  - seagulls perched on the quay and roofs, flapping `Wing_L`/`Wing_R` now and then, sometimes flying off
  - deck props on the rowboat: rope coil, tackle box, lantern
  - plaice and cod models into `ArtLibrary.Fish[5,6]`
  - sea modules per sea: SandBank (Sandbar), SeaRockCluster and CliffSegment8m (Rocky point), ChannelBuoy and DistantShip (Deep channel)
- [ ] A2. Task 04 part C skiff kit: the skiff hull plus winch, gill net, sort table and hold (used in B below).
- [ ] A3. Each later Codex task as it lands: the crew rig and animations, UI pass 2, the day boat. See the Codex plan.

### B. Build 2 start: the skiff refit (tier 3)
- [ ] B1. **Refit flow.** At the Chandlery, the skiff refit unlocks when you've landed 16 fish in one voyage and have 1,500 coins. Buying it plays a short refit moment (fade, new hull) and persists in the save as `Hull = 1`.
- [ ] B2. **Hulls as data:**
  - a `HullDef` (rowboat 3x2, skiff 5x3) with deck size, blocked tiles (console, hold), rod sockets, cooler/hold capacity, crew cap and row speed
  - The boat builds from the hull def, using the skiff model when present and primitives otherwise.
  - The skiff has an outboard: shorter travel times, plus a fuel cost per trip (Supplies sells fuel).
- [ ] B3. **Fisherman role (tier 3):** a hired fisherman stands at a rod and fishes it himself. He casts and strikes with a skill-based hit rate (hand 55%, experienced 70%, veteran 85%) and leaves landed fish for the deckhand. The crew cap goes up on the skiff (3 crew + captain). Crew Office contracts get a role: deckhand or fisherman.
- [ ] B4. **Gill net (tier 3 manual):**
  1. Tap "Set net": the captain drops it at the stern.
  2. The net soaks 60-90 s while you rod-fish; floats bob and catch counters tick up.
  3. Tap "Haul": hold-to-crank on the hand winch (a one-tap version: tap to start, the captain cranks over a few seconds).
  4. Net fish land in a pile on deck. The deckhand carries them to the hold.
  - Nets catch many small fish (herring, mackerel) with some bycatch, which matters for the sort table later.
- [ ] B5. Balance with the bot (extend the bot for the skiff, nets and fisherman). Target: the skiff earns 2-3x the rowboat per minute, and bottlenecks show up (the deckhand overloaded by net hauls).

### C. Shops, contracts and the economy loop
- [ ] C1. **Contract variety:**
  - deliver N of a species
  - deliver X kg total of a species
  - "fresh" contracts (fish must come in iced)
  - a weekly special with a big reward
  - a rush contract (1 voyage)
  - The contract board shows the giver: a restaurant, the cannery or a local.
- [ ] C2. **Rival captains:** 3 AI captains with names and boats, shown on a harbour scoreboard (Harbour Master). They earn per voyage at their own pace. A Weekly Weigh-off every 7 voyages: the heaviest single fish wins a prize, and the rivals have plausible records. Rivals sometimes take a contract off the board ("Captain Brann took the cod contract").
- [ ] C3. **Daily reward:** first launch of the day gives a small coin and bait gift with a popup. PlayerPrefs date; part of the save.
- [ ] C4. **Events at sea (light, never punishing):**
  - a seagull swoops and steals a fish left on deck too long
  - a seasick deckhand: half speed for one voyage
  - fog at a sea: slower bites, shown on the chart
  - a lucky school: bites twice as fast for 60 s, with a toast and sparkles

### D. UI and feel (toward the mockups)
- [ ] D1. Match `17-hud-fishing.png` and `18-hud-harbour.png` layouts precisely: spacing, icon rows, chip styles, the tap burst and ripple in the strike panel. Use the kit sprites everywhere; no generated fallbacks visible.
- [ ] D2. **Title screen:** Codex's logo and title illustration (Codex UI pass 2) once they land; until then a styled wordmark. A gentle camera drift over the harbour.
- [ ] D3. **Feedback:**
  - a coin pop-up (+N) on sale and purchase
  - a catch card when a fish lands (portrait, name, kg, value), small and non-blocking
  - floating "+1" on the cooler
  - a splash ring on casts
  - shop purchase animation, i.e. a button flash
- [ ] D4. **Fish portraits** (Codex UI pass 2) in the fish log, market prices and catch cards.
- [ ] D5. **Harbour Master chart:** use Codex's illustrated sea chart image as the map background, with pins at `SpotDef.MapPos`.
- [ ] D6. Crew models and animations (Codex task): swap the capsule people for the rigged crew, with idle, walk, carry, cast and reel. Hats per role.

### E. Wrap-up for the morning
- [ ] E1. Full 30-voyage sim and renders: harbour, each sea, the skiff. Save the renders to `docs/screens/`.
- [ ] E2. Write `docs/MORNING-REPORT.md`:
  - what's new
  - how to test (step list)
  - known issues
  - decisions Mo should make
  - Codex status
  - screenshots
- [ ] E3. Update `docs/GAMEPLAY.md` and the README.

## Log
- (start) Plans written, Codex queue started, hourly check-in scheduled.
