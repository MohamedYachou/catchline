# FABLE-RESTAURANT-1: the evening service rebuilt end to end

For Fable, working in the cloud on branch `fable/current-game` of `MohamedYachou/catchline`. You have no Unity and no
Blender. Claude (the lead, on Mo's machine) compiles, runs the checks, captures frames and builds Mo's games from
your branch. Mo owns every product decision below; they are settled.

## Why

Mo, 2026-10-28, after playing tonight's build: "this is anything but playable, crew is invisible, it's only captain
and Mira, not the rest, people just spawn in instead of walking from the left edge up the street into the bar, this
just feels way too janky." Mo picked this job for you over a look system or a character system: **rebuild the evening
service as one piece (the room, the flow, staff and guest behaviour, and the HUD) so it feels like a finished,
production-quality game.**

## Mo's decisions (do not reopen)

1. **Your role: manager with quick taps.** The player steers with taps on tables, stations and crew: seat this group,
   sell a round, shoo the gull, send someone to the stove. The crew do all the walking. A calm evening that still keeps
   you busy.
2. **Camera: the whole scene, fixed.** One fixed view of the whole restaurant plus the quay street in front of it. The
   HUD is trimmed so the room fills the screen.
3. **Guests walk the street: in from the left, out to the right.** Groups appear off-screen at the left edge, stroll
   together along the quay street, queue at the door, get seated, eat, pay and leave along the quay to the right edge.
   Nobody ever pops into or out of existence on screen.
4. **HUD: essentials only.** Top: clock, coins, stars. Bottom: tonight's crew. Orders, moods and problems show as bubbles
   on the tables, stations and people themselves. Night cards shrink to three buttons at most.
5. **Tonight's crew is picked in the evening.** Before the doors open, the player picks who works tonight from everyone
   they have hired (no longer "who sailed today works tonight"). The number who can work is limited by the restaurant's
   size: each stage has job slots (the café, for example: host, one cook, one waiter), and bigger stages add slots.
   Mira is the host. Fit the pick into the existing evening flow (`DayPhase` Plan/Prep) with one clear screen.
6. **Every person is visible and alive.** Staff walk in from the kitchen or back door at opening and leave at closing.
   Everyone turns, walks, sits, carries and idles with the animations we have; no sliding, no T-poses, no teleporting.

## Known bugs in the current service (fix as part of the rebuild)

- **Staff are invisible.** In every service frame (`docs/screens/fable-restaurant/day-service*.png`) guests are in the
  room but no staff are, not even Mira or the captain; they only appear as portraits on the bottom bar. Diagnosis so far:
  the staff puppets (`Assets/Art/Models/Crew/Quaternius/<id>.fbx`, loaded by `ArtLibrary.M(id)` in
  `RestaurantWorld.MakeActor`) load with 4–5 enabled renderers, sane bounds (about 1.1 m before `CrewAnim.FitHeight`,
  scale about 0.6) and URP Lit materials. They have no Animation component and are posed with the shared clips
  (`Armature|Idle_Loop`, `Armature|Walk_Loop`) via `AnimationClip.SampleAnimation`. So the fault is in how they are
  placed, posed, layered or culled at runtime, not in the models. Find it and fix it for good.
- **Guests pop in at the queue spot** (`RestaurantWorld.Refresh`: `if(!a.Placed){a.Root.position=queue;...}`).
- Big banners and Mira's call strip sit over the middle of the room; the stock panel and nine card buttons crowd it.

## Read first (just these, then follow the code)

- `docs/plans/RESTAURANT.md`: the design. Update its sections where Mo's decisions above change it.
- `Assets/Scripts/Game/Restaurant/`: `RestaurantSim.cs` (the deterministic rules), `RestaurantWorld.cs` (the 3D
  presentation: room, actors, camera), `RestaurantData.cs`, `RestaurantLayout.cs`, `RestaurantState.cs`.
- `Assets/Scripts/Game/VoyageRestaurantDay.cs` (the day flow and the night's setup) and `VoyageRestaurantUi.cs` (the
  service HUD, immediate-mode `coastalUi`: draw order is call order, anything not drawn in a frame is hidden).
- `Assets/Editor/ServiceV2Checks.cs` and `RestaurantChecks.cs`: the checks Claude will run.
- Frames of today's evening: `docs/screens/fable-restaurant/` (plan, prep, market, service open/mid/late, closing,
  night cards; 1440×900 and one phone frame at 844×390). The art direction: `Art/STYLE.md`, `Art/HIFI.md`.

## Constraints

- **Code only.** No new 3D models or textures. Use the models, rigs and animation clips already in the project; list
  any model or clip you wish existed in your report instead. Mo is making new, very high-quality crew models: keep the
  per-crew-id puppet lookup (`ArtLibrary.M(id)`) so his models drop in without code changes, and don't touch
  `Art/Source/Crew`, `Assets/Scripts/Game/CrewUi`, or the crew FBX files.
- **It must compile blind.** Unity 6000.3, URP, C# 9 (no C# 10+ features such as file-scoped namespaces or global
  usings), no new packages. Match the surrounding code's style. Keep `RestaurantSim` deterministic and free of
  `UnityEngine` presentation types so the editor checks can run it headless.
- **Keep the rest of the game working**: the sea and market phases, saves (`GameState` fields may be added, never
  renamed or removed), the Test build title's "Restaurant day" button (`VoyageTestDay.cs`), and the capture steps in
  `VoyageRestaurantDay.cs` (`day-service`, `day-closing` and the rest), which Claude uses to take frames.
- Phone and desktop both matter (844×390 and 1440×900 logical); taps go to tables, stations, bubbles and the crew rail,
  never to tiny bodies.

## Deliver

1. Your work as commits on a new branch `fable/restaurant-rebuild`, pushed to GitHub.
2. `docs/reports/FABLE-RESTAURANT-1.md`:
   - what changed, file by file;
   - **every small decision you made** (pacing, slot counts per stage, bubble rules, route shapes, timings), one line
     each, because Mo wants to see the small decisions;
   - the checks you added or updated, and the exact frames Claude should capture to verify each of Mo's six decisions;
   - anything you could not finish, and why.
3. New or updated editor checks that prove the rules: everyone enters from the left and leaves to the right, nobody
   spawns on screen, the evening pick respects each stage's slots, and every staff member has a visible, posed puppet.

Claude merges your branch, fixes anything that does not compile, runs the checks, captures the evening, and puts it in
Mo's Real and Test games.
