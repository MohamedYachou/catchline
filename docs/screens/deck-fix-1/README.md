# DECK-FIX-1 evidence

Codex 1 (Windows app), 2026-10-24. All three requested fixes implemented and verified. No commit; Claude reviews and commits.

- Throw is orange on the left; Keep is white on the right.
- An idle captain automatically carries unclaimed rod-basket fish to sorting. Settings has **Auto-carry catch**, default On. Off retains manual Carry. Busy captain actions, active rod work/minigame and other workers' claims are protected.
- Sort decisions render only while Fishing with an unclaimed fish at the sort table. Unused Canvas controls deactivate after sorting and on travel/harbour transitions. Existing return-trip scheduler and keeper handling remain intact.

## Verification

`DeckFixChecks.Run` passed in `Catchline-lead-sim`: Rowboat and Skiff default On, Off/manual Carry, On resumption, busy/rod/claim guards, fish accounting, actual settings preference changes, and control retirement after Keep, empty table, Head home, harbour and outbound travel. The check restores the original preference. See [Editor log](editor-check.log).

`GameBuild.BuildBoth` built Real and Test successfully in the scratch project; [build log](build.log). Installed using `docs/tools/install-shortcuts.ps1`; [install log](install.log). Built and installed executable/managed DLL hashes match, and both desktop shortcut targets/arguments were inspected: [receipt](install-receipt.json). All five owned source files match the checked/built scratch copy.

Installed Test native captures completed with no save reads or writes: [native log](native.log). Existing player-save SHA256, length and modification time stayed identical: [before](save-before.json), [after](save-after.json).

Every image below was opened and visually inspected. Sort buttons have the requested colours/positions; Head home has neither button; title and the four-row Settings panel fit at both resolutions.

| Screen | 1440 × 900 | 844 × 390 |
| --- | --- | --- |
| Sort | [Desktop](sort-1440.png) | [Landscape mobile](sort-844.png) |
| Head home after Keep | [Desktop](sort-home-1440.png) | [Landscape mobile](sort-home-844.png) |
| Test title | [Desktop](title-1440.png) | [Landscape mobile](title-844.png) |
| Settings | [Desktop](settings-1440.png) | [Landscape mobile](settings-844.png) |

The Head home fixture reuses the live Canvas after Keep/stow, then adds another waiting table fish before departure to reproduce the return-trip scheduler case. It asserts both controls are inactive immediately after the mode change.

Limits: scripted native inspection and focused Editor checks; no full hand-played Real session or touch acceptance. Existing homebound toast/status overlap and a rectangular water transition are visible in the capture; recorded for the UI/sea owners, outside this deck-fix scope. No Sea/art/player-save changes. No subagents.
