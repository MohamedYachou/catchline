# Catch presentation and stored-net receipts — Codex 2 (WSL CLI)

Mo requested a finished catch presentation with subtle rarity backlights and a
species list when net fish reach storage. This replaces the plain catch portrait
panel with a navy specimen display and a matching stored-haul manifest.

| Current tier | Backlight | Meaning |
| --- | --- | --- |
| Common | Soft white | Normal common specimen |
| Common · big | Green | Large common specimen |
| Rare | Blue | Normal rare specimen |
| Rare · big | Purple | Large rare specimen |
| Legendary | Gold | Style reserved for future legendary fish |
| Mythical | Red | Style reserved for future massive legendary fish |

Current rare presentation species: sea bass, conger eel and turbot. Other current
species are common. “Big” begins at 75% of each species' existing min–max weight
range, so a large mackerel can be green despite weighing less than a normal cod.
This is presentation metadata, independent of market price, catch probability,
location, save IDs or actual rarity odds. No existing fish becomes legendary or
mythical; the two additional visual styles are ready for later special content.

The native Canvas graphic draws a rounded navy enamel surface and a soft radial
backlight behind the existing transparent fish artwork. There is no generated
replacement fish art, bloom, extra camera, or shared Canvas-source modification.
Catch cards show species, weight, estimated current value, rarity words and the
existing new-species/personal-best feedback. They last six simulation seconds,
with a brief settling movement. Captain feedback remains separate from automatic
fisher catches, which preserve the existing quiet feedback behavior.

Net receipts appear only after the actual storage insert. They list species and
counts, total weight and estimated value. Desktop rows also show each species'
value; compact phone rows prioritize species/count and weight. The footer shows
the whole stored batch. The manifest remains visible for eleven simulation
seconds, followed by a “Last net” review action. Reviewing is read-only: it does
not store fish again, award money, update records or consume random numbers.

Snapshots include only successfully inserted fish. An interrupted gather or
stow creates no false receipt. A partly full hold reports only the fish it
accepted; the leftover basket remains unstored. Manually storing a leftover net
fish also produces a truthful one-fish receipt. Empty callbacks do not overwrite
a previous receipt. New voyages clear the ephemeral receipt; no save migration
or persistent catch data is changed.

## Files and verification

Runtime: `CatchPresentation.cs`, `CatchRewardGraphic.cs`,
`VoyageCatchRewards.cs`, plus narrow hooks in `VoyageFeedback.cs`,
`VoyageInterface.cs`, `VoyageNetUnload.cs` and `VoyageGame.TryStow`.

`CatchRewardChecks` exercises active tier boundaries, no current gold/red fish,
actual set/soak/haul/gather/stow reporting, exact species/count/weight/value,
cancellation, full/partial/manual storage safety, snapshot immutability,
read-only review, RNG isolation and native viewport/control clearance.

Native captures cover white/green/blue/purple, desktop and landscape phone,
net manifest, larger type and review state. `net-list-*` are explicitly authored
presentation fixtures using five real supported fish through the production
snapshot/render methods; the actual net distribution/storage cycle is exercised
separately in the executable checks. They are Unity world plus production Canvas
captures, not browser mockups or a rendered-player input test.

Codex 1 concurrently owns CHART017 and the original Catchline-sim. This pass uses
an independent `Catchline-rewards-sim`, keeping that scratch and its held chart,
net-visual and shared Canvas paths untouched. Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File docs/tools/check-catch018.ps1
```

The runner syncs only the main Assets/Packages/ProjectSettings into the dedicated
scratch and runs hidden Unity, the existing first-voyage/net/economy/crew
regressions, the focused catch checks, native captures and a separate build.
Output: `Catchline-rewards-sim/Builds/Catch018/Catchline.exe`.
Use `-netboat-trial -native-display` for the existing isolated 200-coin boat trial.
No main-project batchmode, foreground restart, commit, staging or reset.

Physical playtest feel and Mo's visual acceptance remain user checks. Gold/red
are style support only. Existing small secondary HUD text and overlapping world
action bubbles remain outside this catch-presentation scope.

Final verification: `check-catch018-check.log` exited 0 with all listed
regressions, focused checks, captures and Windows build completed. Native
captures were inspected; no material scoped visual defect remained. The built
player passed a bounded headless isolated-startup check without runtime
exceptions/readability/Graphic errors; the diagnostic alone was stopped.
Evidence, exact verified source hashes and native images are under
`docs/screens/catch018/`. The dedicated build contains its captured main-source
snapshot; Codex 1 must re-sync released CATCH018 sources into any subsequent
CHART017 build before claiming those features integrated.
