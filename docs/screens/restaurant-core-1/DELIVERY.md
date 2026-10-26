# RESTAURANT-CORE-1 handoff

Codex 1 (Windows app). Explicit brief A-F complete; standalone technical delivery for lead review, no production wiring or player acceptance claim.

Seven new C# files: RestaurantData, RestaurantState, RestaurantLayout, RestaurantForecast, RestaurantPortions, RestaurantSim, and Editor/RestaurantChecks, with stable metas. Codex 1 edited no existing C#. Final audit:249 starting hashes unchanged; VoyageInterface.cs and VoyageUiV2Capture.cs changed concurrently under Claude2's logged19:05 UI reservation. Their main/scratch/before hashes are in existing-source-audit.json; preserved untouched. No commit, staging, installation, player-save operations or subagents.

Validation: final scratch run `docs/tools/check.ps1 -Name restaurant-core-1-sealed -Method Catchline.EditorTools.RestaurantChecks.Regression`, Unity exit0. 33,091 restaurant assertions include1,000 forecast seeds,100 mixed-appliance seeds, deterministic service,20 special-stock comparisons, layout/save/preparation/repair/manager checks, and food conservation in six reports. Same five specialists over ten seeds served131 with four cooks/one waiter versus252 with two cooks/three waiters.

Existing regression passed on the scratch tree: crew abilities, M2, bites, cages, tutorial,11 maps/792 directed hull routes, harbour/jig trips, and Gull coast life. Existing navigation timing warnings remain in the log; no native feel/touch acceptance. Owned source-under-test hashes match main and scratch. Concurrent lead UI changes are not claimed verified by this run.

[Six scenario tables and API](README.md). [Ten individually opened room captures and measured scale](view/README.md). Phone tile depth44.13px; widths8-14 fit;17 requires sideways pan. Greybox pictures only.

**Design boundary:** explicit brief baseline240s, assignable jobs,no plates/sink. The newer600s/fixed jobs/haulers/plates/trash/cold food/till/captain queue/dashboard requirements need follow-up before integration. Starting two-seat tables reject groups3/4; reports expose lost guests. Tuning provisional, not accepted balance. No existing-code change needed to review this standalone core.

Core reservations released. Lead review required; subsequent assignment is separate.
