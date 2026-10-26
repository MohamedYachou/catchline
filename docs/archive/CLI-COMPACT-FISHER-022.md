# ART-022 — approved-size motor fisher, finished 3D delivery

Codex2 /2026-10-16. Art commit **a709cf0** (local, not pushed). Mo approved the V1 image and authorized finishing the boat.
Hull remains5.4×2.8m; four-person layout/open helm roof/three rods/small stern net
are retained. This completes the model/export handoff; gameplay integration is
still separate. Stable asset basename `CompactFisherV1`, manifest revision2.

![Finished boat](screens/art022/Finished-review.png)

Real opening/recessed hold under the independent lid, helm gauges/switches/handles,
windshield wiper, canopy braces/running lights, navy hull band, engine fittings and
separate net frame/drum/crank complete the working-boat details.29parts/10,164tri.
No new material slots/textures, no boat growth, no enlarged cabin. Crew figures,
studio floor/lights/cameras appear only in the review blend, not exported geometry.

## Actual delivery

Main `Assets/Art/Models/Boats/CompactFisherV1.fbx` updated in place with existing
GUID dfcce90858484e95bad7f132ff98f3f3 intact; matching new `.placements.json` stores
effective Y-up stations/sockets/access points, source hinge/spin axes and dimensions.
Existing Rowboat/Skiff/meta remain unchanged. Main runtime source/save/settings
are untouched. V1 had already imported/registered natively via Codex1's HUD008
checks; that does not validate this new revision's import/playability.

Art checkout sources/evidence: `Art/Source/finish_compact_fisher22.py`,
`Art/Models/CompactFisher22/` (editable source/review blend, FBX, manifest,
validation, renders, logs, receipt/report). Approved ART021 sources remain intact.

Checked saved source/actual FBX roundtrip, pivot landmarks and protected V1
geometry/bounds. Five hold-aperture rays reach tub floor;90degree source-X lid
opening clears it in source and FBX. Static.28m body clearance connects four
stations/rod/net/hold approaches; finite vertices and triangle areas checked.
Inspected neutral studio desktop/phone/top/stern/open-hold/scale renders. These
do not verify live Unity shadows, crew movement, HUD, net animations or hardwareFPS.
Independent slices of actual source/FBX geometry at.20/.55/.95m body heights also
connect the four stations and all job approaches (1,771samples,.28m body radius).

## First unfinished step — Codex1 runtime integration

1. Native import sanity:29meshes/10,164tri, metre scale, canonical materials, Y-up
   root orientation, current GUID. Avoid applying FBX−90degree root conversion twice.
2. Wire this accepted model to the intended tier. **Do not drop it into the old
   Skiff5×3grid or resize crew to hide the mismatch.** Establish grid/route mapping
   against the conservative2.2×4.2m deck and manifest; preserve saves/rowboat behaviour.
3. Hide optional `RodVisual_1/2/3` before spawning functional rods; use actual
   sockets/approaches. Avoid the old duplicate winch/net-kit spawn. New net parts:
   static `SternNetRoller`, rotating `NetDrum` and `NetCrank`, `NetMountFittings`,
   `SternNet_Stowed`. Engine fittings are separate and stay visible with net hidden.
4. Lid hinge source(−.65,.35,.02); source-local+X90degree opens. Drum/crank spin
   about source X at manifest pivots; propeller pivot/axis is separately supplied.
   There are no baked animation clips. Test open-hatch occupancy/routes and carrying.
5. Test four actual crew passing, all three rod stations, helm/hold/net reach,
   deck backlog/full hold, departure/docking and landscape phone framing. Inspect
   roof occlusion; roof fading is a runtime presentation decision, not baked art.
6. Keep net economics/wear/yield as [TODO](../TODO.md) proposals until a scoped
   gameplay pass. This delivery does not introduce a net-operator role or force
   role combinations. Record actual native outcomes in canonical comms.md.

No additional art queue started; resume from runtime fitting or specific Mo feedback.
