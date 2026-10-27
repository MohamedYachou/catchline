# Fishing polish: items 3-5

Codex 1 (Windows app), 2026-10-25. HARBOUR-IMPORT-1 limits this delivery to overlay suppression, atmosphere and readable float/water cues. Claude owns the other FISH-POLISH-1 items.

The installed Test player produced all twelve PNGs here at 1440x900 and 844x390 with the native HUD, D3D11 and the production rod-view simulation. Every final PNG was opened individually. Captures are deterministic SessionOnly fixtures, not hand-played or physical-touch acceptance.

## Delivered behavior

- **Item 3:** the rod view hides ground-border and sailing-route overlay renderers, including overlays created after the cast begins. Disposing the view restores each renderer's previous visibility, including pre-hidden renderers. No Sea source or navigation state was changed.
- **Item 4:** a camera-relative gradient sky, soft cream cloud banks and scoped horizon haze replace the flat rod-view backdrop. Disposal restores the prior fog settings and destroys owned materials. Real map buoys remain visible; this helper adds no buoys.
- **Item 5:** the bobber has a broad orange cap, ivory waist and navy stem, with a small drift wake. Mint ripple rings and bubble puffs provide visible bite cues. The focused phone-size projection measured the orange cap at **10.30 pixels**; native phone images confirm it is discernible.

The implementation lives in `RodViewAtmosphere.cs`, `Resources/RodViewSky.shader` and `Resources/RodViewCue.shader`, integrated with `VoyageRodView.cs`. The bounded capture driver is `VoyageFishPolishCapture.cs`; source and scratch hashes are recorded in [verification-receipt.json](verification-receipt.json).

## Individually opened native stages

Each row covers both `-1440.png` and `-844.png`.

| Stage | Native review |
| --- | --- |
| `cast-mid` | Downward cast view renders with the float and rod; ground/route overlays do not cut across the water. |
| `waiting` | Gradient sky, cloud banks and horizon haze are visible at both sizes. Orange float remains clear on phone, with a small pale wake. Real horizon buoys remain visible. |
| `bubbles` | Mint bubble puffs and a broader faint water ring are visible; the small phone puffs can be distinguished against the water. |
| `fake` | Dipping float and ripple cue render at both sizes without sea-map overlay lines. |
| `take` | The float dips under the surface and its orange is dimmer, as expected for this sampled bite phase. Ripple cue remains visible. This is not fight or landing acceptance. |
| `restored-deck` | Deck, captain and normal HUD return after the rod view closes. The local crop does not expose the complete ground ring, so renderer restoration is established by the focused lifecycle checks rather than this image alone. |

**Owner review remains:** dark navy foreground geometry intrudes from the bottom of waiting/bubbles/fake/take frames. Its identity and camera treatment were raised as a QUESTION for Claude, who owns the rod-only/camera work. This delivery does not claim arms, hanging fish, species variety, fight, landing or tutorial acceptance. Distant buoy repetition and the island silhouette are existing world presentation outside items 3-5.

![Phone waiting view: orange float, wake, gradient sky and clouds](waiting-844.png)

## Verification

[final-check.log](final-check.log) records scratch PASS and exit 0 for actual cast/cancel cleanup, late overlays, pre-hidden visibility preservation, fog restoration, material cleanup, shader compilation and phone-size bobber projection. [board-stage-check.log](board-stage-check.log) separately checks the corrected cage evidence fixture. [check-build.log](check-build.log) records final Real and Test builds from `Catchline-lead-sim`; the main project was never run in batchmode.

The canonical install script installed both modes. [harbour-1/verification-receipt.json](../harbour-1/verification-receipt.json) records full built-versus-installed file hashes and the exact desktop Test shortcut startup. [verification-receipt.json](verification-receipt.json) records this set's source/binary/frame checks. The player's save SHA256, length and modification time match [save-before.json](save-before.json) and [save-after.json](save-after.json). [frames.json](frames.json) and [reviewed-images.txt](reviewed-images.txt) identify final reviewed images. Old preview/probe logs are development evidence, not the final native acceptance set. No git commit.
