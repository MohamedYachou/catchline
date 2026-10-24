# FISH-VIEW-1 - Codex 1 runtime handoff

Status: runtime and delivery checks verified; partial against the full design until the lead supplies tutorial persistence across launches. All 132 final native images were individually opened at 1440x900 and 844x390. Both Real and Test builds are installed, with exact desktop shortcuts checked. No commit.

The captain's cast now opens a continuous first-person rod view. The existing production fish roll supplies species/kg; Claude's unchanged `BiteModel` supplies waiting, fakes, takes and strike results. Crew rods retain their previous clock. The catch is delivered once through the existing `LandFish` path, after surface thrashing, lifting and the camera return. Reeling in abandons the bait, including during a take.

The view uses Codex 2's released 5,878-triangle FP rod, gloved hands and seven authored clips. Runtime copies live in `Assets/Art/Models/FishRodFP/`; source artist files were not changed. `FishRodImport` imports Legacy transform clips for explicit sampling on the voyage clock and creates the isolated `RodViewArt` resource. Eight bone rotations add progressive bite tension to the sampled bind pose. The old FishingRod remains the resource-free fallback.

The 1.2-second cast passes over the shoulder; deck controls fade within 0.4 seconds. The view keeps pause and Reel in, uses a 25-point sagging line, model-driven bobber/fish motion, rings/bubbles and existing audio cues. Hooked fish thrash for 1-2.5 seconds by kg, lift for 0.9 seconds and hang for 0.4 seconds before the one-second return. The returned fish and rig recede in world space; the line follows the rod's animated `LineTip` and the lifted fish's head end (authored `Nose`, or the mesh head opposite its tail pivot).

## Evidence

- `native-legacy-check-build.log`: final `FishViewChecks.VerifyAndBuild`; runs `BiteModelChecks`, five captain outcomes, once-only exact species/kg delivery, bait loss, camera/UI checks, unchanged crew flow, shader checks, all seven imported clips and baked mesh-to-tip clearance (0.0025 m), then both Real and Test builds.
- `native.log`: installed, visible, save-free Test player. Actual screen captures include the retained Canvas. The deterministic fixture selects a real production Cod roll (seed 3, about 5.7484 kg); only capture clocks and fixture RNG are controlled.
- `cast-mid-{1440,844}.png`, `waiting-{1440,844}.png`, `fake-{1440,844}.png`, `take-{1440,844}.png`, `lifted-{1440,844}.png`: requested stills. Fake is captured at its deepest plateau, rather than just entering the phase.
- `cast-00` through `cast-12`: every 0.1 seconds during the cast, at each size.
- `landing-00` through `landing-46`: every 0.1 seconds from strike through return, at each size. `back` includes the existing catch card after delivery.
- `reviewed-images.txt` and `frames.json`: individually opened final images and their dimensions/SHA256 hashes.
- `install-receipt.json`: built versus installed executable/managed DLL hashes, exact Desktop shortcut targets and `-native-display` arguments. Real was installed but was not launched for testing.
- `verification-receipt.json`: owned source/scratch byte parity, installation and native/save verification.
- `save-before.json` / `save-after.json`: player's save hash, length and modification time are identical (SHA256 `9C5E02886DF870D441338F2FA86DAE4686184D2A43573304BB37D09205F045E1`, 7,610 bytes).

The delivery verifier passed for 29 source/resource/metadata files matching the checked scratch project, both installed executable/managed DLL pairs and desktop shortcuts, the unchanged save, and all 132 reviewed image dimensions/hashes.

Run `verify-delivery.ps1` to recheck this handoff against the current scratch/install. `run-scratch.ps1` only uses the assigned `Catchline-lead-sim` editor; the main project and the unrelated UI2 editor are not used for batchmode.

## Review limits and lead decision

**Tutorial persistence is incomplete:** the quiet tip currently appears on the first two casts of the current session when Tips is enabled. The design asks for the first two casts of a save, across launches. The brief explicitly excludes save changes; the required lead-owned persistence hook is logged as a QUESTION in `comms.md`. No sidecar or player-save change was introduced. Capture fixtures suppress the tip to inspect the requested view without tutorial text.

Native captures demonstrate the clock-controlled Test presentation and delivery. They do not establish hand-played Real or physical touch acceptance. Continuous intermediate frames, rather than successful compilation alone, are the visual evidence.

The first hidden-window pass was rejected for black captures and Generic runtime-sampling errors. Subsequent visible passes exposed a floating fish-line endpoint, a camera-relative return scale error and an older Cod prefab without a nose locator. The hook now derives that prefab's head from its tail and mesh bounds; a real-prefab regression checks the correct head end. These issues were corrected before the final pass. Superseded frames are not accepted evidence. The attempt-black/ and attempt-line-gap/ folders remain marked REJECTED because automatic approval review blocked their cleanup; frames.json lists only the 132 final root images. The preview/ folder contains earlier Editor diagnostics, not native delivery evidence.

No commit was made; Claude reviews and commits. Sea, BiteModel, save schema, artist source and completed deck/art assignments remain outside this work.

