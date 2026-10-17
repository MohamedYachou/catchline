# NET-012 active compact-net handoff

Codex 1 (Windows app) / net_systems. Source delivery only; root owns input, stern control, minigame visual feedback, scenery/chart, native checks/build/relaunch. No commit or scratch/Unity/foreground process used by delegate.

## Changed scope / backup

Modified `Assets/Scripts/Game/VoyageNet.cs` and `Assets/Editor/NetChoiceChecks.cs`; new `Assets/Scripts/Game/VoyageNetGame.cs`, `Assets/Editor/NetHaulChecks.cs`, this note, append diary. No other source/resources changed. Exact pre-edit backups are `%TEMP%/Catchline-NET012-backup/VoyageNet.cs` and `NetChoiceChecks.cs`; root should remove that dedicated directory after successful integration verification. Existing unrelated backups are untouched.

## Live contract

Compact hull only:20seconds soaking, same one2–5local-fish batch,2seconds setting. Deckhand Nets duty still automatically hauls in5working seconds. Captain HaulNet walks to real NetAccess and starts an active winch rather than timed automatic completion.

Public `NetGameActive`, `NetGameProgress`0–1, `NetGameTension`0–1, `NetGameHeld`; `NetHaulRedTension=.85f`; `SetNetHaulHeld(bool)`, `CancelNetHaulGame()`. Root supplies pointer/Space held state each normal input frame and resets held false when menu/unfocused; draw progress/tension and hold/ease feedback only while active. Root owns all visual/input hooks. Cancel works both walking-to-haul and active minigame; repeated cancellation is safe.

Hold: progress+.20/sec while under red; tension+.32/sec with small deterministic sinusoidal loading variation. Release: cool-.62/sec and keeps earned normal progress. Sustained red: stalls/slips-.055progress/sec while holding; fish are never lost or rerolled. No fish RNG consumed by work. Balanced hold to.72/release to.28 finishes in7.25seconds in an isolated numerical simulation of the source equations. Actual feel/physical controls must be checked natively. No-input does not advance progress. All gameplay clocks use TickNet simulationdt; zero dt freezes the game. Direct large fixture dt is internally subdivided50ms.

Captain is held in a long cancellable Person.Do ownership lock, with no timer completion callback. Success/cancel clears minigame callbacks before calling Person.Stop, preventing reentrant cancellation from restoringReady or invalidating the success token. Existing Complete/Cancel local closures still validate/consume the single-worker claim. ResetNet invalidates claim first, clears game/held input and stops its actor; stale callbacks cannot deliver catch. Hull0/1 original setting/soaking/hauling behavior remains.

## Root fixture changes needed

Old captain `Work(person)` alone must no longer finish hauling. Public `NetHaulChecks.ReachCaptainWinch(game)` steps walking until active; `NetHaulChecks.FinishCaptainHaul(game)` drives genuine tension-aware hold/release input and finishes. The latter returns active-work duration. Update root-owned CompactFisherChecks haul expectations/captures to drive that helper and ideally capture an actual active winch frame. NetChoiceChecks now expects20second soak and uses that helper. Other old fixture90second ticks still reachReady, but any assertion specifically expecting the old timing should become20.

## Authored checks / honest verification

`NetHaulChecks.Run` exercises actual captain walking cancel, exclusivity versus another hand, no-input waiting, hold progress/tension, zero-dt freeze, release cooling, overload progress slip preserving exact catch, explicit/repeated cancel, normal Person.Stop cancellation, no extra RNG/depletion, SessionOnly real-save hash guard and separate temporary state-save/load, balanced5–8.5second completion, exact one-time basket delivery, stale held/cancel after completion,5second automatic deckhand haul and ResetNet actor/callback invalidation. Temporary portable save is removed in finally.

Source diff whitespace checks clean; isolated Python source-equation simulation7.25seconds passed. No C# compilation, Unity runtime/input/render/physical control or visual acceptance claimed here. Root should mirror both runtime and both Editor files and run NetChoiceChecks.Run + NetHaulChecks.Run plus legacy SkiffChecks and its own integrated compact/UI checks. Native prompt/readability/progress/overload/pause/unfocus/cancel feedback remains root's acceptance gate.

NET012 supersedes NET010's90second compact soak and timed captain haul. Net batch/yield/basket/ordinary carry-stow/save-ID logic otherwise unchanged. Future net wear/repair remain unimplemented.

## Latest Mo steering: automatic batch unloading

Successful compact haul now invokes root `BeginNetUnload(person)` immediately after `FinishHaul()`, passing the actual captain/deckhand actor captured by the validated completion closure. Root owns NEW VoyageNetUnload.cs, TickNetUnload/Game.Step scheduling and capacity-safe carrying; it also removes the hold semaphore. This delegate adds no fetch loop or duplicate cargo conversion. The intended user flow is haul once, then the worker automatically unloads the entire batch; no per-fish click sequence.

Direct TickNet/Person-only source fixtures still assert the immediate landed basket because they do not drive root Game.Step/TickNetUnload. Root's integrated fixtures should verify full automatic unloading, capacity-safe retained backlog and concurrent workers. The callback is a new compile dependency on root BeginNetUnload(Person). Legacy Hull1 FinishHaul path has no callback change.
