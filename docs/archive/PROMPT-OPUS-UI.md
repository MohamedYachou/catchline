# Prompt for the local Claude Code session — Catchline UI v2

Copy everything below the line into a fresh Claude Code session started in
`C:\Users\momoy\Projects\Catchline`.

---

You are the UI engineer for Catchline, a Unity 6 (6000.3.25f1, URP) fishing
management game for landscape mobile and PC. You know nothing about this project
yet; the repo tells you everything. Your job is to rebuild every screen of the
game to match four concept images exactly, following one written UI system, and
to prove it with real native captures. Gameplay does not change.

## 0. Before anything else: tooling

I want the best tools available, not whatever is lying around.

1. List the skills already installed in `C:\Users\momoy\.claude\skills`,
   `C:\Users\momoy\.agents\skills` and the project `.claude` folder. Load
   `design-stack`, `impeccable` and `ui-ux-pro-max` if present.
2. Search the Claude Code plugin marketplace and the web for the strongest
   options for this job and install what helps: a Unity MCP server that can
   drive the open editor (inspect the scene and canvas, run play mode, take
   screenshots — e.g. the CoplayDev `unity-mcp` or `mcp-unity`), any UGUI/Unity
   UI skill, an SVG/PNG asset pipeline skill, and an image-generation tool for
   illustrated icons and portraits if one is available to this account.
   Verify each one actually works against this project before relying on it.
3. Only then start. Tell me in one short message what you installed.

## 1. Read first, in this order

- `AGENTS.md` (project rules). Coordination is `comms.md`: append one short
  START entry before you edit and one DONE entry when you stop. Skip the
  per-step checkpoint ceremony; keep entries to five lines.
- `git fetch origin && git merge --ff-only origin/claude/nifty-galileo-i1ofka`
  on `proto/deck-sim`. That brings in the two documents below and the concepts.
- `docs/UI-SYSTEM.md` — the UI language. It is the law for every element.
- `docs/screens/ui-concept/*.webp` — the four concept images (voyage HUD,
  operations, crew, chandlery). Open them and keep them open. "Exactly like
  these" is the acceptance bar.
- `docs/BLUEPRINT.md` §15 for what the management screen means. Ignore the
  rest of that file; it is gameplay design for later.
- How the UI is built today: `Assets/Scripts/Game/CoastalCanvas.cs` (UGUI
  built in code, retained elements, sliced sprites from `ArtLibrary.UiTex`),
  `VoyageInterface*.cs`, `VoyageManagement*.cs`, `VoyageHud.cs`,
  `VoyageMenus.cs`, `VoyageDeparture.cs`, `VoyageChart.cs`,
  `VoyageIllustratedChart.cs`, `VoyageCatchRewards.cs`, `Ui.cs` (IMGUI styles,
  still used by menus). Three skins coexist today (UI kit, `FishReference`
  raster panels, `ManagementReference` raster regions). You replace all three.
- The existing asset pipeline: `Assets/Art/UI/UI.md`, `Art/Source/build_ui_kit.py`
  and the SVG sources under `Art/Source/UI/`.

## 2. Hard rules

- Never run Unity batchmode on the main project. All checks, builds and
  captures run on the scratch copy `C:\Users\momoy\Projects\Catchline-sim`
  through `docs/tools/check.ps1`. Read that script before using it.
- Never touch the player's save. Captures run in TEST/no-save mode.
- Do not change gameplay, timings, economy, saves or crew behaviour. If a
  screen needs data the game does not have yet, show the current data and leave
  a `// TODO(BLUEPRINT)` comment.
- Every screen ships with real native captures at 1440×900 and 844×390 saved
  to `docs/screens/ui-v2/<screen>-1440.png` and `-844.png`, placed side by side
  with the concept image. Scene renders and editor screenshots do not count.
- Preserve existing illustrated map, water, boat and catch-card artwork.
- Commit per finished screen on `proto/deck-sim`, push after each commit. No
  model names in commit messages.

## 3. Order of work

1. `Assets/Scripts/Game/Skin.cs`: tokens and every component in UI-SYSTEM §2
   as methods on `CoastalCanvas` taking logical rects like the existing API.
2. The new sprite kit from UI-SYSTEM §6. Slabs, buttons, bars, chips and tabs go
   through the SVG pipeline. Planks, rope, stage illustrations, item
   illustrations and crew portrait busts are image-generated in the concept
   style, then cut out with transparent backgrounds; if no image tool is
   available, stop and tell me which assets you need and at what size. Add
   Lilita One (OFL) from Google Fonts next to Fredoka.
3. Screens, each one captured, compared and committed before the next:
   voyage HUD → operations → crew → harbour hub and the five shop pages →
   chart → departure → sale result → title and pause → catch card.
4. Remove the old skins: `Reference*` and `Dashboard*` methods in
   `CoastalCanvas`, the `FishReference` and `ManagementReference` resources,
   and `Ui.cs` once nothing uses them.

## 4. Acceptance per screen

Matches the concept at both sizes. Every touch target at least 44 physical
pixels. No text outside a slab. One primary button. Status is a word, never a
percentage. No charts, costs per minute or efficiency rings. All fonts and
colours from the tokens. Write a one-line status per screen in
`docs/UI-V2-PROGRESS.md`.

Ask me only when the spec and the concept disagree. Otherwise decide, build,
capture, show me.
