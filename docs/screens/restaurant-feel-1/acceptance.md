# RESTAURANT-FEEL-1 — verified delivery

Codex 2 (WSL CLI), 2026-10-27. Presentation changes complete. No git or commit.

Changed source: `RestaurantWorld.cs`, `RestaurantPlayCapture.cs`, `Assets/Editor/RestaurantChecks.cs`. Sim rules/numbers, Day/UI/Data, camera/lights/grade, main scenes, crew models and CrewAnim were not edited. No subagents.

Guests follow the host in a spaced file, then follow cached floor routes to their chairs, face travel and sit on arrival. Gone guests walk out and fade beyond the doorway. Queue groups occupy ordered rows with every member side by side. Plates follow individual Delivered tickets and hide at Payment. Carry props follow carrying legs and their fish/drink/coffee/dirty-plate type. Staff chase interpolated positions with damping and bounded local spacing. Externally driven World.Update now leaves Refresh to RestaurantDay, preventing a second presentation update and movement during pause.

## Checks

[verification.txt](verification.txt) preserves PASS lines, commands and full scratch-log paths. [source-hashes.json](source-hashes.json) records the tested sources; main and both scratch copies matched before final capture/check completion.

- Final canonical `RestaurantChecks.Regression`: Unity exit 0, `RESTAURANT CHECKS PASSED: 47183` (Run executes first), crew-ability integration PASS, jig regression PASS, coast focused PASS, `RESTAURANT FULL REGRESSION PASSED`.
- Scratch FeelBuild: exit 0, native Windows player build succeeded, zero build errors. Generated acceptance scene exists only in scratch.
- FeelBalance: exit 0, 80 nights, guest conservation and bounded completion checked. [balance.md](balance.md) contains 20 seeds × four crews, every requested metric and staff idle percentage. Report only; no tuning.
- Both enabled-World SessionOnly native players: exit 0, `RESTAURANT FEEL NATIVE PASS`, three strips each. No player save reads/writes.

## Native review

Actual HUD/framebuffer PNGs plus per-frame transform/ticket metadata are in `1440x900/` and `844x390/`. Each size has seating 80 frames, serving 60 and leaving 80 at .1 seconds of presentation time (five .02s steps); capture wall time varies. The native component remains enabled, as in the externally driven game.

Contact sheets are framebuffer crops/scales with time labels; `contact-sheets.py` reproduces all 22 sheets. Opened and inspected final desktop seating01/02, serving01/02, leaving01/02; phone seating01/02, serving01/02 and leaving01, plus full desktop seating015 and phone serving022. Every action/size was inspected over at least 24 consecutive frames.

- [Desktop seating](strip-seating-1440x900-01.png) and [arrival](strip-seating-1440x900-02.png): guests walk around tables, turn with travel and sit only at their chairs. No observed furniture crossing, sustained backward walk, stacked guests or position pop in these sequences.
- [Departure](strip-leaving-1440x900-01.png) and [threshold fade](strip-leaving-1440x900-02.png): Gone actors remain visible while walking to the doorway, fade outside, then deactivate. Queue rows visibly shuffle forward.
- [Serving](strip-serving-1440x900-01.png) and [delivery](strip-serving-1440x900-02.png): Ana carries FishSoup for the Soup ticket. Captain is empty on the approach leg and carries FilletsLemon on delivery. PanFish becomes Delivered before Soup; its individual plate is already visible during Kitchen. Props disappear after delivery.
- [Phone seating](strip-seating-844x390-01.png), [leaving](strip-leaving-844x390-01.png), [serving](strip-serving-844x390-01.png): same motion under landscape-phone framing; full HUD also inspected.

[motion-metrics.json](motion-metrics.json) complements visual review: maximum guest displacement .2201m/.1s; target seating pair minimum .4723m (initial defect was .055m), departure pair minimum 1.024m. Staff roots never coincide in the recorded strips; minimum .0905m, so this is soft spacing, not full body collision avoidance. Facing metric includes short corner/arrival turns and does not establish clip fidelity. Drinks/coffee/dirty props were checked against source task legs/models; the selected serving strip proves fish/soup delivery.

## Mo-owned crew issue — logged QUESTION, skipped

Staff bodies render as thin/fractured silhouettes in the native fixture. Existing crew loading/FitHeight/wardrobe and Animate sampling were compared with the pre-task source and remain unchanged. Native renderer metadata records the narrow bounds and stable scale. Crew models and CrewAnim were never written. Crew-body appearance and animation fidelity are not visually accepted by this task; root motion and carry props were reviewed separately. This remains with Mo's crew work, outside this brief's ownership.

Evidence is automated checks plus agent native review, not Mo acceptance or coverage of every possible furniture arrangement. Temporary pre-change backups removed after verification. All task reservations released; stopped after DONE.
