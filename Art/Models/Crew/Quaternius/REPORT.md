

## Codex 1 (Windows) - CREW-QUATERNIUS-F - Phase 1 delivered

Eight crew: mira, noor, rosa, tess, ana, lise, ines, tove. Seven Superhero_Female bases; Rosa uses Superhero_Male because the portrait reads male. CC0 Quaternius Universal Base Characters; no new clothing meshes. The supplied whole-body surface is partitioned into Skin (head/neck/hands/fingers) and one flat role-coloured Suit placeholder. Hair/Eyes/Brows are independent material slots. Hair and replacement matching brows are rigid children of the original Head bone; the accessory skeletons are discarded and the original body skeleton is retained. The original eye mesh and supplied iris/sclera texture are preserved with a dark recoloured iris.

### Art and substitutions

Skin and hair swatches were sampled from the actual art108 PNGs using the recorded contact positions in female-palette.json. Mira's fair skin is an explicit Mo override compensating the warm orange portrait lighting. Skin textures are colour-modulated copies of the supplied diffuse, preserving facial and hand detail. Eyes retain the supplied white sclera, pupil and highlight instead of becoming a single flat dark surface. Hair is matte solid colour. The whole native body scale, rig and weights are untouched; these are human-height bases, not the retired 0.95 m crew proportions.

- **mira (F)**: Navigator. Brown hair, fair skin; mandated Hair_Buns substitutes for portrait curls. Cap omitted in Phase 1. Fair skin follows Mo explicit instruction; warm orange portrait lighting compensated.
- **noor (F)**: Deckhand. Warm tan skin and dark brown tied curls; Hair_Buns substitutes for curly tied-back hair. Beanie omitted.
- **rosa (M)**: Fisher. Portrait reads male: male base and regular brows used. Short dark brown hair; SimpleParted substitutes for tousled fringe. Beanie omitted.
- **tess (F)**: Fisher. Golden-blonde hair; Hair_Long substitutes for the long side braid. Beanie omitted.
- **ana (F)**: Deckhand. Brown hair and tan skin; Hair_Long substitutes for shoulder-length waves. Beanie omitted.
- **lise (F)**: Fisher. Copper-red hair and fair skin; Hair_Long substitutes for wavy bob. Freckles not reproduced by the supplied base texture. Beanie omitted.
- **ines (F)**: Engineer. Mandated light-blonde Hair_Long substitutes for twin braids. Hardhat omitted in Phase 1.
- **tove (F)**: Deckhand. Silver-grey hair; Hair_Long substitutes for short bob. Older portrait age is not sculpted onto the untouched base. Cap omitted.

### Deliverables and checks

- `<name>.fbx`: eight bind-pose FBXs, no animation; skin/eye textures embedded and also supplied as adjacent `female-<name>-{skin,eyes}.png` fallbacks. Editable `female-<name>.blend` source files retained.
- `crew-contact-1.jpg`: one labelled row per crew, portrait, fixed-scale game-camera full body on the 1 m grid, enlarged head crop, exact swatches and substitution notes.
- `crew-contact-1-grid.jpg` and `crew-contact-1-844.jpg`: all eight freshly imported FBXs together, original scale, orthographic camera pitch 38/yaw 2, 1 m grid; the overview is exactly 844 pixels wide. Labels and floor are proof-only.
- `female-build.py`, `female-prepare.py`, `female-package.py`, `female-palette.json`, eight `female-<name>-baseline.json` and eight `female-<name>-audit.json` make the result reproducible. Baselines capture the original source bones/hierarchy/rest transforms and hashes before styling.
- Fresh-import audit PASS for all eight: original 65 bone names/hierarchy each; no intentional bone, skeleton scale or rest changes. FBX numeric maximum rest-matrix deviation 0.000026 (tolerance 0.0001); root matrix maximum 0.000000076; bind-pose identity maximum 0.000020. Original body geometry, UVs and skin weights compare exactly (zero maximum error). Zero animation clips. Four mesh objects, exactly five named materials. Both Head children follow a tested Head rotation. No extra accessory rig, duplicate brows, floor or lights exported.

Total triangulated geometry for this roster: 142,137. See female-verify-all.log and per-crew audit JSONs. Final file/proof hashes are in female-delivery-audit.json.

### Boundaries and next owner

Phase 1 source delivery only. No Assets/, runtime scripts, git operations or Unity batchmode. Claude owns native Unity import, Humanoid avatar creation, Universal Animation Library retargeting, materials/shader assignment, integration and gameplay checks. Blender import/pose proofs do not establish native Unity acceptance or Mo visual acceptance. Phase 2 boat-work and restaurant clothing remains blocked on Mo's choice of outfit mesh source. No further outfit modelling performed. No commit. Codex 1 releases its named paths and is IDLE after visual/package verification.

## Codex 2 (WSL CLI) — CREW-QUATERNIUS-2 — Phase 1

Delivered **sam, dirk, kofi, mats, olaf, pim**, all on **Superhero_Male_FullBody** because all six portraits read male. The original body, eye mesh, 65-bone skeleton, bone names, hierarchy, rest transforms and native scale were retained. Body height is approximately **1.820 m**; the retired crew-height convention was not applied. No clothing meshes were created or imported.

### Portrait matching and substitutions

Skin targets match actual art108 portrait pixels; selected hair/eye targets approximate their illustrated shading. `_codex2/portrait-palette.json` records reference coordinates and colour differences. Skin textures derive from the supplied diffuse with reduced baked-lighting contrast, retaining facial and hand details. Eyes retain the source sclera, pupil and highlight with a dark iris. Hair and brows use flat portrait colours. Manifest hex values are the target swatches, while textured skin varies around its target.

| Crew | Role / flat Suit | Hair / facial hair | Portrait limitation |
|---|---|---|---|
| sam | Deckhand / #1E3A5F | Chestnut Hair_SimpleParted, clean shaven | Closest supplied style to tufts beneath the beanie. |
| dirk | Fisher / #2F6E6A | Silver Hair_SimpleParted and moustache | Upper-lip patch retained from Hair_Beard; shorter and straighter than the illustrated moustache. |
| kofi | Fisher / #2F6E6A | Very dark Hair_Buns, darker warm-brown skin | No free curly style. Buns is the specified curl substitute; bun silhouette and longer side strands are a visible compromise. Supplied hair geometry raised 0.050 m to fit the male head; skeleton unchanged. |
| mats | Deckhand / #1E3A5F | Copper Hair_SimpleParted and moustache | Upper-lip patch retained from Hair_Beard instead of an inaccurate full beard. |
| olaf | Engineer / #B5542A | Off-white Hair_SimpleParted and full Hair_Beard | Supplied beard is shorter than portrait. Older facial proportions not sculpted onto the untouched body. |
| pim | Fisher / #2F6E6A | Dark chestnut Hair_SimpleParted, clean shaven | Closest free style to the tousled portrait fringe. |

Portrait hats/helmet and outfits are deferred. Skin covers head/neck/hands; Suit is one flat placeholder on the existing bodysuit surface. The five independently named materials are **Skin, Suit, Hair, Eyes, Brows**. Skin and Eyes use already recoloured textures, so leave their material tint white when assigning those maps; applying the manifest colour again would double-tint them. Hair, brows and facial hair use the hair swatch.

### Files and verification

- Six `<name>.fbx` bind-pose exports with embedded skin/eye textures, no baked animation. `_codex2/<name>.blend` editable sources and `<name>-{skin,eyes}.png` fallback textures are included.
- `crew-contact-2.jpg`: six labelled rows with portrait, fixed-scale full body at pitch 38/yaw 2 on a 1 m grid, separate face detail, swatches and substitutions. Face-detail camera pitch is 12 degrees for attachment inspection.
- `crew-contact-2-grid.jpg`: all six freshly imported FBXs at pitch 38/yaw 2, original scale and 1 m floor grid. `crew-contact-2-844.jpg` is its exactly 844-pixel-wide phone overview. Floor, labels, cameras and lights are proof-only and excluded from exports.
- `_codex2/audit-all.log`, individual `*-audit.json`, `*-build.json`, `build.py`, `audit.py`, `render.py` and `package.py` retain source signatures and checks. Fresh-import audits PASS all six: exact 65 bone names/parents, one original armature, five named materials, nonempty expected meshes, zero clips, two decoded embedded maps, and rigid Head children following a tested Head rotation. Duplicate accessory skeletons were discarded; original body skinning retained.
- Maximum FBX roundtrip rest-matrix difference **0.00001318**, bind identity difference **0.00001856**, both below recorded matrix tolerance **0.0001**. Maximum world-space body vertex difference **0.000000164 m**; UV difference **0**; bone membership and skin weights unchanged within 0.00001. No intentional skeleton/rest/scale edits; exact in-memory source signatures are asserted before export.
- Total geometry: **96,907 triangles** across six crew, including eyes, hair, brows and facial hair. All **118** baseline pack/portrait hashes remain unchanged (`source-preservation.json`). Final FBX/proof hashes and dimensions are sealed in `_codex2/delivery-audit.json` after visual review.

### Next owner and limits

Source delivery and Blender proofs establish the checks above. Native Unity import, shader assignment, Humanoid avatars, Universal Animation Library retargeting, gameplay and Mo visual acceptance remain **Claude/Mo-owned and unverified here**. Phase 2 boat-work and restaurant outfits remain blocked on Mo's choice of clothing mesh source. No Assets/runtime scripts/git operations or Unity batchmode; no commit. No subagents. Finished reservations are released; Codex 2 is IDLE.
