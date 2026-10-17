# Catchline — current local game for Gemini

Prepared 2026-10-17 by Codex 2 (WSL CLI). Upload `catchline-current-for-gemini.zip` to Gemini, together with any newer play screenshot and your preferred target renders. Paste `PROMPT-FOR-GEMINI.md` as the request. This is a local handoff; nothing has been pushed to GitHub.

## Why the previous upload looked empty

Live remote heads checked with git ls-remote:
- main: 641c8bfc5b4f596d76f1f92b4017d02862b673c3 — initial Unity template; matches the ZIP Gemini described.
- proto/deck-sim: 1f7bcf020946a1728f03ce28a639d8efc84f3830 — older gameplay.
- art/style-pass: 42289f7090161364883bbe3d479fead6f3c16d4c — older art.

The working checkout is proto/deck-sim at 1bc8a59 PLUS modified and untracked files. A GitHub download cannot contain those uncommitted changes. This archive captures the actual local files, including untracked runtime scripts and assets, rather than exporting a commit.

## Contents and limits

- Complete current Assets, Packages and ProjectSettings with Unity .meta files.
- Root product/design/gameplay coordination and all Markdown docs under docs.
- Existing target concept/reference renders, selected native HUD/catch/map captures and their available evidence manifests.
- Current Tier4 comparison/top/station images, report, generator and manifests. Editable Blender scenes and other authoring sources are omitted to keep the upload focused; Tier4 has no production Unity export yet.
- SHA256 manifest and Git status at capture. Excludes .git, Unity Library, caches, executable builds and player saves.

This is a source/reference handoff, not a newly built or newly playtested version. Existing screenshots are historical evidence from their named task, NOT freshly captured from the snapshot and NOT necessarily the executable Mo currently launches. Some show the previous food system; newer code uses fuel. Treat screenshot freshness honestly.

## Read order and authority

1. This handoff and Mo's current request.
2. Latest relevant comms.md entries (append-only history; older statements may be superseded).
3. DESIGN.md, PRODUCT.md, Art/STYLE.md and actual goal renders.
4. docs/GAMEPLAY.md and focused reports such as CATCH018, CLI-REFERENCE-HUD-024, FUEL021, NET023, CREW026 and TIER4-BLOCKOUT032.
5. Actual current source for every gameplay or implementation claim.

Some old docs describe historical Windows/WSL ownership or obsolete food/storage rules. Mo's current assignment and latest decisions win; do not infer permanent restrictions or current behavior from an old paragraph.

## Current Tier4 status

BOAT032 delivered a crude editable blockout: tier3 reference 5.4 x 2.8 m, tier4 candidate 6.8 x 3.5 m, same-scale crew and one two-worker preparation/chum station. This is a spatial study, not integrated gameplay, final hull approval or an approved five-person capacity. Prepared fish never spoils / raw buckets spoil / upgraded front coolers preserve raw fish are recorded design requirements, not implemented mechanics. Read docs/TIER4-BLOCKOUT032.md before advising on it.

## UI implementation already exists

Do not start from the default SampleScene. Runtime scenes are assembled largely by scripts. Inspect Assets/Scripts/Game/VoyageInterface*.cs, CoastalCanvas.cs, FishReferenceStyle.cs, VoyageCatchRewards.cs, CatchPresentation.cs, CatchRewardGraphic.cs, VoyageFeedback.cs, VoyageNetUnload.cs, VoyageIllustratedChart.cs and VoyageDeparture.cs. Existing artwork is under Assets/Art/UI and Assets/Resources/FishReference; use the supplied Fredoka font.

CATCH018 already provides nonblocking captain catch cards with portrait/species/weight/estimated value, new-species/record feedback and white/green/blue/purple specimen backlights. Net receipts report fish actually stored, not just caught or hauled. Automatic individual crew catches intentionally stay quiet. Gold/red presentation is reserved for future species, not current content.

## Useful first UI task

Make two comparable mockups over the SAME supplied native gameplay capture: one normal catch and one new-species/personal-best catch. Preserve the boat and action locations. Keep the existing cream/navy/Fredoka language; improve fish portrait prominence, species hierarchy, weight/value readability and card placement. Do not redesign the entire HUD while solving catch feedback. Target visual identity comes from the actual renders, not unverified sampled hex values from a prior answer.

For nets, improve the existing aggregate stored-haul receipt and review action. Avoid a burst of individual catch popups. Keep landed, awaiting carry, stowed and sold feedback distinct; estimated value is not earned coins until sale. Do not invent UI stats, rarity odds, species or mechanics.

## Proposed output location

Mo requests Gemini's proposed files under a new gemini folder. Use gemini/ for documents, mockups and isolated proposals. Any eventual Unity-importable trial assets should live under Assets/gemini/ (Unity does not import a repo-root gemini folder). A folder is not an integration boundary: proposals that require hooks in existing scripts must describe them for local integration, rather than silently replacing current gameplay. Start with pictures and clear answers; no code in chat.
