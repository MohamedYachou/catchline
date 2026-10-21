# MODULE042 - optional second-net module

Tier 4 Prep fisher gets a dedicated Chandlery module costing **2,000 coins once**. Buying fits it immediately; its card then switches it on/off for free **at port**. Saved ownership and enabled state are separate. Earlier hulls cannot buy it; owning it while using another trial hull does not make that hull a two-net boat.

- Off: three actual rods and the original net.
- On: one stern rod and two independently deployed nets. The other two rod objects are removed, and a matching rail winch/roller is fitted where the rod module was.
- Both nets have separate workers, claims, soak timers, catches, captain timing-game ownership and reset/cancel state. Nets duty chooses a ready haul before starting another set; two hands can run both. One hand can set the second while the first soaks.
- Both use the current shallow/deep selection, local species roller and shared hull capacity (30kg base / 44kg with Heavy Net System on Hull3). The module does not grant free replacement nets or deep uses. Other deployed gear counts against available inventory; one net cannot be fitted to two rigs at once. One failed deep recovery spends one use. One rig's completion/failure never clears the other rig's catch or active captain game.
- Unloading shares the existing stern basket and cargo capacity. An active unload keeps its owner; subsequent catch remains safely in the basket until a hand can deliver it. No duplicated cargo, instant sale or changed fish freshness rules.

## Final departure check

Pressing **Let's go** on the existing final supplies/crew confirmation counts hired fishermen against actual unlocked rods. If there are more fishermen, it stays in harbour and explains how many lack a rod and that they cannot run nets or prepare fish. **Back / change crew** returns to the Crew Office; **Sail anyway** explicitly proceeds. This is a warning, not a forced role change. Restoring the rods removes a mismatch where appropriate. Applies to any actual rod/crew mismatch, not just the module's default two-fisher trial.

## Coordination and validation

Codex1 owns module/runtime/lifecycle work. Codex2/UI041 applied the additive GameState2bool save hooks and explicitly released only VoyageNet lifecycle methods to Codex1; its canonical fish-roll/filter work and other UI/fish changes are preserved. It uses separate Catchline-ui041-sim while MODULE042 uses Catchline-sim. No GameData upgrade-enum edit was needed.

First `module042` behaviour run and `module042-final` full checks/build passed: insufficient funds/exact2000/no repeat purchase; free on/off with actual1/3rod objects; both saved states; final native UI warning/back/explicit sail;2/3fishers; independent timers/yields/primary catch preservation; both hauls/unload; stock reservation/return; captain second timing game surviving primary completion; PACE036/PREP035/TIER033/compact regressions. Latest delivery validation adds second-winching approach cancellation, two deep nets and second failure consuming one use while retaining the first exact catch, plus the complete pre-existing NetHaulChecks. Final result/native evidence appended below.

The Tier4 playable trial remains save-isolated. Final paid hull progression and the separate UI041/FISH043 art acceptance are not claimed by this module task.

Latest full delivery validation `module042-delivery` exit0: MODULE042, PACE036, PREP035, TIER033, COMPACT FISHER and complete NET HAUL checks passed; standalone built. Includes pre-arrival secondary captain cancellation and two deep nets, hard mass capacity and failed second recovery spending exactly one use while retaining primary catch.

First native capture confirmed correct1rod/two nets with independent10s/3s counters, price2000, owned toggle and mismatch warning. It also exposed UI041 shared skin's thin button artwork and parchment content bounds; evidence handed to that owner in comms. Narrow local fallback uses existing kit pressed button textures for module card and departure/warning buttons, popup-panel for warning, preserving the shared skin work. No global UI files changed. `module042-visible` passed complete NET HAUL checks and rebuilt those presentation-only changes plus session-only Tier4 fixture2200coins (immediate module trial; real starting coins untouched). Final native recapture pending.

Presentation follow-up: `module042-visible` exit0 (full NetHaulChecks plus rebuilt fixture/presentation), native final captures show the module card Buy/Toggle buttons and warning choices full height with contained text. The own popup header needed cream title text against its navy header; that single-colour correction is the only change in the final title build. Shared UI041 HUD/artwork issues remain recorded for its active owner and are not claimed as accepted here.

## Final delivery

`module042-title` build-only exit0 after the single title-colour change. Final native PID19532 completed normally; `module042-native-title.log` confirms TEST/no-save and MODULE042 NATIVE CAPTURES COMPLETE. Inspected final desktop/landscape warning, price card and toggle, plus two-net view: own title/body/buttons contained and readable, actual one pole/two separate nets and10s/3s counters visible. Eight final PNGs are under `docs/screens/module042`. This accepts module presentation only; the separate shared UI041 HUD/slicing/layout findings remain with that owner. Scripted native captures do not establish physical touch acceptance.

Installed the verified build to `Catchline-play/Tier033`; **Catchline - Tier 4 Test** still launches it with `-prepboat-trial -native-display`. Trial now has2,200session-only coins so buying the2,000module is immediately reviewable; visit Chandlery at port. EXE, Assembly-CSharp.dll and resources.assets SHA256 match the built scratch (`installed-build.json`). Module-owned sources match tested scratch; dependency hashes recorded separately in `verified-source.json` because UI041/FISH043 continue independently. No capture player remains. All11own temporary source backups removed after verification. No commit/push and no real save/launcher edits.
