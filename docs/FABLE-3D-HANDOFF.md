# Fable: current 3D art handoff

Repository: MohamedYachou/catchline. Start from branch `proto/deck-sim`.

Read `AGENTS.md`, `CURRENT.md`, `Art/STYLE.md`, then this handoff.

## Crew references and editable work

- Portraits: `Assets/Art/UI/Portraits/art108-<name>.png`.
- All 14 current crew: `Art/Models/Crew/Quaternius/crew-manifest.json`.
- Current source FBXs: `Art/Models/Crew/Quaternius/<name>.fbx`.
- Editable female crew: adjacent `female-*.blend` and textures.
- Editable male crew: `_codex2/<name>.blend` and adjacent textures; inspect actual names in that directory.
- Contact sheets: `crew-contact-1.jpg`, `crew-contact-2.jpg`, their grid and 844px variants.
- `REPORT.md` records skeleton, materials, substitutions, checks and limitations.
- Runtime models: `Assets/Art/Models/Crew/Quaternius/`.
- Animation wiring: `Assets/Scripts/Game/CrewAnim.cs`, `DeckActors.cs`, and `Restaurant/RestaurantWorld.cs`; import settings: `Assets/Editor/ArtImport.cs`.

Phase 1 bodies/hair are delivered; clothing is still the placeholder bodysuit.
Preserve the supplied 65-bone skeleton and skin weights. Read the manifest and portraits before changing appearances. Native runtime acceptance of the latest wiring is still pending.

## Other current 3D

Restaurant sources and accepted CC0-based pieces: `Art/Models/Restaurant/`, especially `Pack/`; runtime imports: `Assets/Art/Models/`. Project and source notes remain alongside the assets. Raw third-party download archives under `Art/Downloads/` and `Art/Audio/Downloads/` are excluded.

## Download actual binary assets

This repository uses Git LFS for FBX, Blender, images and other binaries. After checking out the branch, run:

```sh
git lfs install
git lfs pull
```

A small text file beginning `version https://git-lfs.github.com/spec/v1` is a pointer; fetch its LFS content before inspecting or editing it.

Use the current branch as the source for your art task, and return your changes on a separate working branch. Record exact changed files and show rendered proofs.
