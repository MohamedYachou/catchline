# DASH092 — all five launchers use the current verified release

Current release: **Deep104**, delivered by Codex 2 (WSL CLI), 21 October2026.
DASH087 is historical. Current binary/source hashes, mode inventory, native
review and actual-save fingerprints are pinned in
[the Deep104 installed receipt](screens/deep104/installed-build.json).
Gameplay, third rig, chum and verification details are in [DEEP104](DEEP104.md).

| Existing Desktop shortcut | Current player | Preserved arguments |
|---|---|---|
| Catchline - Real Game | Deep104/Real | `-native-display` |
| Catchline - DASH Management Test | Deep104/Test | `-native-display` |
| Catchline - Tier 3 Test | Deep104/Test | `-crew-mix-trial -native-display` |
| Catchline - Tier 4 Test | Deep104/Test | `-prepboat-trial -native-display` |
| Catchline - Tier 5 Test | Deep104/Test | `-tier5-trial -native-display` |

Installed paths are `C:/Users/momoy/Projects/Catchline-play/Deep104/{Test,Real}`.
Both player trees passed full shipping-file hash verification. All five targets,
working directories and exact arguments passed shortcut readback. Installed
DASH/Tier3/Tier4/Tier5 Test modes started isolated and shut down cleanly. The
hidden borderless window fallback closes only the launched PID's Unity window,
without foregrounding or killing unrelated sessions.

Real remains persistent; Test never loads or writes the player's progress.
The Real candidate ran against a temporary copy of the real save and completed
load, departure, native Management, return and saving. Actual player-save
fingerprints matched before and after native checks and installation. No real
save was migrated or replaced during verification. Future normal Real play will
apply compatible crew/upgrade state rules when it loads and saves progress.

Final native evidence contains46frames: standard two-rig, upgraded three-rig and
side-net layouts at1440x900 and844x390, each with boat, Income, Operations,
Crew/bait/duties and chum settings; plus four Real-copy frames. Production UGUI
pointer hit testing/click and native Escape passed. Reviewed frames and limits
are listed in `docs/screens/deep104/native-review.json`.

`docs/tools/deep104-install.ps1` verifies current evidence and source fingerprints,
backs up shortcuts before mutation, installs checked binaries, preserves all mode
flags, verifies installed startup/shutdown and save hashes, writes the receipt,
then removes temporary shortcut backups. The historical
`docs/tools/dash092-sync-launchers.ps1` now prefers the completed Deep104 receipt,
so rerunning it cannot silently move current launchers back to Dash087. Its
historical Dash087 fallback remains available only when no Deep104 receipt exists.

Older versioned players and their historical evidence are retained. No future
crew cards or electrical machinery are implemented by this release; the separate
research/design documents remain proposals and their owners keep their scope.
