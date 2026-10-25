# UI-POLISH-ART-1

Codex 2 (WSL CLI). All A–C art delivered; required review sheet opened and inspected.

| Group | Source PNGs and identical Assets/Art/UI/Crew copies | Canvas |
|---|---|---|
| A | ui-badge.png | 64 × 64 |
| B | gem-{white,green,blue,purple,gold,mythic}.png | 64 × 64 |
| C | reward-band-{white,green,blue,purple,gold,mythic}.png | 256 × 40 |

13 editable geometric SVG masters live in svg/. Exports use the existing catchline-ui CairoSVG/Pillow environment, fourfold supersampling and Lanczos downsampling, with a clear two-pixel outer margin. No existing assets were edited. No generator script file was created. This extends FirstCatch's navy-edged vector UI family, rather than generating bitmap illustrations.

The badge is coral #E2683A with a lit top rim, darker lower bevel and navy ink edge. Its centre is opaque and free of symbols/numbering: overlay the live number in game. All gems share exactly the same silhouette, facet paths and top-left light. White is deliberately grey-silver #A9B2B5, matching RarityColour rather than pure white. Other exact bases: green #4CAF50, blue #3B82F6, purple #8E44AD, gold #E6B422, mythic crimson #D7263D. Mythic alone adds a prismatic top/side sheen. The colour method cited by the brief is actually defined at CrewGarage.cs:21–25 and resolves Skin.cs:15–16; CrewGarageFx calls it. Those source files were read only.

Bands use the same colours, navy edge, inset gloss, short swallowtail folds, and no text. Keep the 256:40 aspect ratio to preserve folds; these files do not encode a nine-slice border or import configuration. Live values and rarity labels belong to integration.

review/sheet.png is 1920 × 1080: all sprites on exact #F4EBDA and #1C3A5A, badge/gems at native64 and actual28px, bands at256 × 40, plus explicitly static ability/reward composition samples. Opened and visually inspected: small silhouettes/hues remain readable, badge number area is clear, mythic sheen is visible, band folds/gloss stay subordinate. Review labels/sample text are not part of sprite exports.

Verification:13/13 exact dimensions, RGBA, transparent outer border, source/Assets byte equality and SHA256 checks pass. SVG inspection confirms the same gem contour across six variants and no text elements in any master. delivery-checks.json records measurements, hashes and actual visual observations. This is a static sprite delivery; Unity import/material/runtime HUD and player acceptance remain Claude/Mo's work. Browser/Lighthouse and gameplay tests are outside this asset-only brief.

No scripts, scenes, metas, audio, saves, watchdog files, peer folders or git writes. No commit, subagents, background processes or temporary backups. New assets only. Reservations released in comms.md after final readback.
