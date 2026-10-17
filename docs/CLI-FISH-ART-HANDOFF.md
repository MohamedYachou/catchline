# Fish art handoff — 2026-10-16

Mo assigned GPT-6.1 Sol the fish models and matching caught-fish portraits while
CLI lead retained gameplay/economy. This is a bounded asset delivery in the current
main checkout, with no staging, commit, reset, push, foreground applications,
Unity, live Blender/MCP, scratch, or Catchline-sim use.

## Delivered art

Ten authored species: Herring, Mackerel, Pollock, SeaBass, CongerEel, Plaice, Cod,
Whiting, RedMullet, Turbot. Sources, matching exports, transparent portraits and
individual validation reports are in `Art/Models/FishPolish16/<Name>/`.
`Fish-lineup.png` is an asset-review contact sheet, not a native game capture.

The first pass supplied chunky silver-bellied fish, eyes/gills/mouths, geometric
mackerel stripes, flatfish spots, cod/mullet barbels, a spiny bass and matching
model-rendered portraits. This refinement fixes shared silhouettes: pollock is
slimmer with three dorsal fins; mackerel and mullet have two distinct dorsals;
cod, plaice and turbot have broad fan tails; pollock/whiting/mullet have shallow
forks. Herring retains a compact schooling silhouette. The eel details follow its
curved centreline, placing the visible eye on the face instead of above the head.
Turbot uses wider portrait framing to preserve its whole diamond outline.

`Art/Source/build_fish_polish16.py` builds editable `.blend` sources, FBXs and
512×256 transparent PNGs with quiet warm/cool lighting. Existing Unity portrait
metadata reduces the imported textures to 256×128. `compose_fish_polish16.py`
composes the overview; it does not modify model portraits.

## Validation and installation

Each saved source was reopened and compared to generated world vertices at
1e-5 metre quantization and triangle counts. Independently imported actual FBXs
match triangle/vertex counts, spatial vertices in both directions within .0001 m,
material names and mesh parenting. Unit mesh scales, canonical palette names and
absence of image dependencies are checked. Reports retain source bounds, pivots,
materials, counts and `.blend`/FBX/PNG SHA256 hashes. All ten are under 4,000
triangles: 1,100–1,832, totaling 13,348; nine have Body/Tail meshes and eel has one
continuous Body. Portrait dimensions, RGBA and transparent margins are checked.

Finished exports only are installed in `Assets/Art/Models/Fish/<Name>.fbx` and
`Assets/Art/UI/fish-<name>.png` (`fish-conger.png` for CongerEel).
`main-import-receipt.json` records all 20 installed SHA256 values, metadata hashes,
GUIDs and source validation paths. All 20 metadata files remain byte-identical;
the fourteen original model/portrait GUID files are preserved against the exact
pre-pass backup. No external textures, palette slots, runtime materials, source
SVGs, water, scenery, shared UI, gameplay code or settings changed here.

Source faces -Y; FBX targets Unity +Z / Y up. Root/body centre and runtime naming
remain intact. Nine separate `Tail` objects pivot at attachment (.32×length in
source Y); eel intentionally has no separate Tail. Runtime name fallback resolves
all ten models; no ArtLibrary/ArtImport changes are required by this delivery.

## Windows verification still required

Allow normal Auto Refresh and inspect all ten native imports for material remaps,
metre scale, +Z nose, root centre and intact Tail pivot/animation. Confirm runtime
lookup resolves Whiting/RedMullet/Turbot and that no old thumbnail is cached.
Review actual caught-fish cards and fish-log portraits at desktop and landscape
phone sizes for whole silhouettes, clear species labels and alpha edges. Review
held/deck fish, net catches, tails and clipping with current runtime lighting.
Defer player captures while Mo requires background-only work. Blender renders and
roundtrip validation do not establish Unity appearance or Mo visual acceptance.

Retain `/home/mo/catchline-content-backup-20261016/` until native verification;
the CLI lead owns cleanup and the combined gameplay checkpoint. Logs:
`/tmp/catchline-fish-sol-final.log` and
`/tmp/catchline-fish-sol-turbot-framing.log`. Stop this bounded art queue here.
