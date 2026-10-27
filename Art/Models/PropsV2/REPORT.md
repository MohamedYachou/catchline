# PropsV2 — A5 gear and A6 events art

All 14 named items delivered: 12 clean mesh sources/FBXs and 2 editable SVG/RGBA effects.
Preview: [overview.png](overview.png). Exact runtime paths, pivots, bounds and
read-only provenance: [delivery-index.json](delivery-index.json).

| Plan | Item | Revision | Triangles / parts, or pixels | Audit checks |
|---|---|---|---|---|
| A5 | [JigRig](JigRig/REPORT.md) | r01 | 2,116 / 34 | 321 |
| A5 | [SpareRig](SpareRig/REPORT.md) | r03 | 1,714 / 12 | 124 |
| A5 | [LanternOilCan](LanternOilCan/REPORT.md) | r03 | 914 / 12 | 124 |
| A5 | [DeckLightPool](DeckLightPool/REPORT.md) | r01 | 256 × 256 RGBA | 11 |
| A6 | [JellyfishClump](JellyfishClump/REPORT.md) | r02 | 4,168 / 38 | 358 |
| A6 | [FlyingFishEvent](FlyingFishEvent/REPORT.md) | r01 | 908 / 2 | 33 |
| A6 | [GullSwoop](GullSwoop/REPORT.md) | r01 | 632 / 3 | 42 |
| A6 | [SealHead](SealHead/REPORT.md) | r01 | 776 / 9 | 96 |
| A6 | [DolphinFin](DolphinFin/REPORT.md) | r01 | 132 / 2 | 33 |
| A6 | [InspectorLaunch](InspectorLaunch/REPORT.md) | r01 | 644 / 9 | 96 |
| A6 | [RivalBoat](RivalBoat/REPORT.md) | r01 | 1,790 / 10 | 105 |
| A6 | [SquallOverlay](SquallOverlay/REPORT.md) | r01 | 1024 × 512 RGBA | 9 |
| A6 | [OffalPile](OffalPile/REPORT.md) | r01 | 840 / 7 | 79 |
| A6 | [TableEel](TableEel/REPORT.md) | r01 | 948 / 4 | 52 |

Total: 15,582 triangles / 142 mesh parts;
1483 Blender validation checks passed. Final integrity pass:
315 SHA256 comparisons and 108 unique PNG decodes, including
77 individual angle/context renders, 28 current/revision sheets,
2 source effects and this overview. Per-item reports distinguish new work and
existing-kit derivatives. Original StationsV1/Art108 sources are read-only and hash checked.

Mesh validation opens the saved clean source and independently imports the actual
runtime FBX. Every world-space vertex is matched in both directions; every mesh
part origin, count, material assignment/colour, bounds and metre scale is checked.
Maximum vertex error: 5.52750736e-07 m; maximum part-origin error:
2.23517418e-07 m (tolerance 0.0001 m).
Effect checks cover PNG/SVG hashes, runtime equality, dimensions, finite RGBA,
transparent corners and restrained opacity; pool monotonic fade / rain sparsity.
Final image openings are recorded per item in canonical `comms.md`; a numerical
pass is not a visual or native acceptance claim.

## Placement and integration

Sources use Z up and -Y front; FBXs export Y up and -Z forward, in metres.
JigRig origin is the rail-clamp contact. SpareRig, LanternOilCan, JellyfishClump,
OffalPile and TableEel use centred floor/contact origins. FlyingFishEvent and
GullSwoop retain airborne pose origins. SealHead, DolphinFin and InspectorLaunch
use local waterline zero. RivalBoat preserves its inherited deck-centre root and
all part pivots; suggested water plane is source Z=-0.32 m. Consult each manifest
before positioning; do not apply blanket floor recentering.

DeckLightPool is a 256-square warm transparent pool, suggested diameter 1 m.
SquallOverlay is a 1024×512 sparse rain sprite. Bind alpha/emission and lamp
behaviour in native integration. Review lights, cameras, floors and teal water
surfaces are excluded from delivered mesh sources/exports. Assets contain static
poses; event travel/animation is runtime work.

Native Unity import, lighting/material binding, live placement and event behaviour
remain untested. No Unity scenes, game C#, git operations, or Mo acceptance claim.
Runtime copies are new files under `Assets/Art/Models/PropsV2/`; existing kit files
and GUIDs were not replaced. Claude owns commits and integration.

Recheck receipts and regenerate this index/overview with:
`uv run --with pillow python Art/Models/PropsV2/audit_delivery.py`.
Independent Blender reproducer: `Art/Source/validate_props_v2.py -- --name <Item>`
via Blender background mode. Source/tool snapshots and audit/build logs live in
each item's current `iterations/<revision>/` folder. Older drafts remain history.
