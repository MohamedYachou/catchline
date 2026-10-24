# ART108 reproducible source tools

Run from the Catchline project root. Blender5.2 scripts use background mode only; do not open or batchmode the main Unity project. All builders write only ART108's new source/export paths. Existing hulls, rig and map sources are read-only inputs. The art checkout's original map .blends are required to rebuild derived maps.

- build_stations.py:33 shared kit assets, per-asset .blend/sourceFBX/runtimeFBX/readback receipt. Optional names after -- rebuild a subset.
- render_kit.py: render selected/all kit sources for isolated object review.
- layout_stations.py: all5 hull station JSONs, review overlays, BFS clearance receipts and top/gameplay plates. Names after -- select hulls.
- build_maps.py -- <Map> build: expanded model, grounds/paths/lighting, independent FBX readback. -- <Map> review:3day+3night+top, review-only water/lights.
- build_navigator.py: shared-rig navigator,3clips and readback evidence.
- build_cards.py: raster-backed portrait SVG compositions at240/96/56; vector-native frames at480x640.
- build_effects.py: editable light-pool and rain-streak SVGs plus PNGs.
- build_textures.py: generated-art SVG mirror/repeat compositions, exact edge checks, runtime textures and review plate.
- package_imagery.py: self-contained SVGs/PNG sizes/alpha checks/manifests and group review plates. Reuses unchanged SVG exports; retains originals and exact generation prompts. Textures handled separately. Effects/texture manifests merged into the UI delivery list.
- audit_imagery.py:87manifest files,40events,33portrait variants,4frames and Navigator parity; records retained backup inventory.
- review_events.py: actual64px cream/navy review plates grouped by approved batch.
- audit_delivery.py: verifies5 hull hashes,5 source map hashes,33 kit export hashes,38 unique runtime names, rename targets and unchanged original shared rig.

Python raster composition uses Pillow and resvg-py. Current resvg-py package is installed under C:/Users/momoy/.codex/tmp/art108-python; install that dependency or adjust the local package path on another workstation. No external-image links occur in SVG sources. Transparent output comes from built-in image generation or native SVG alpha; source pixels are not repainted by packaging scripts.

Exact event prompts and batch grouping are imagery/event-specs.json. Runtime logical filenames are art108-<id>.png. Source-generated images are retained inside this project; none depend on Codex's generated-images storage to ship. Code session must define remaining20 event IDs and special-product table before further content. No C# edits are authorized by ART-PLAN.

Reports: Art/ART-PLAN-PROGRESS.md, Art/Models/{StationsV1,Maps,NavigatorV1,CardsV1}/REPORT.md, imagery/REPORT.md. These distinguish source validation from pending native acceptance. Temporary namespace backup deletion was blocked by automatic approval review and is retained; namespace-backup-receipt.json records its original bytes.
