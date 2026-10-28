# RESTAURANT-PIER-1

Codex 1 (Windows app), 2026-10-28. Asset-only delivery for Mira's restaurant at the edge of a Gull Harbour pier.

The production asset contains four alternative timber decks with submerged pilings, a short connection to a continuous stone quay, nine gabled harbour houses, seven lamp posts, three moored boats, crates, barrels, bollards, rope coils, hanging tyre fenders and festoon lights. The room and its furniture are the original, unchanged resource FBXs.

**24,870 triangles in the entire FBX**, including all four alternative piers. Budget is 25,000. No code, room asset, Crew asset or Git operation is part of this delivery. Unity has not been run for verification or integration.

## Files and reproduction

- Production: `Assets/Resources/Restaurant/RestaurantPier.fbx` and `.meta`.
- Optional seven-point light recipe: `Assets/Resources/Restaurant/RestaurantPier-lighting.json` and `.meta`.
- Editable production-only source: [RestaurantPier.blend](RestaurantPier.blend), with the two original atlas images packed. It contains all alternatives; show only one `Pier_S*` group at a time.
- Deterministic authoring, export and render script: [build.py](build.py).
- Independent FBX roundtrip audit: [audit.py](audit.py), results [audit.json](audit.json).
- Read-only source measurements and preservation hashes: [room-inspection.json](room-inspection.json).
- Final counts and exact geometry bounds: [phase3-metrics.json](phase3-metrics.json).
- Render camera records: [phase3-cameras.json](phase3-cameras.json).
- Sealed delivery hashes and render-size checks: [delivery-check.json](delivery-check.json).

Run from the checkout with Blender 5.2:

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b -t 8 --python Art/Source/RestaurantPier/build.py -- --phase 3 --samples 32
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b -t 4 --python Art/Source/RestaurantPier/audit.py
```

`--phase 1` rebuilds/renders the initial S1+quay check; `--phase 2 --stage 2 3 4` checks the extensions. `--skip-render` only authors/exports, and exports occur only in phase 3. The script writes only this source folder and the permitted production FBX/JSON paths. No Unity invocation.

## Origin, axes and stage alignment

Metres. The asset root and every group are at identity. Spawn `RestaurantPier` at local position zero, identity rotation, scale one under the same room root at `HarbourQuayOrigin`. The current code's world origin is `(18, .31, 9)`; no world offset is baked into the model.

Blender is X right, Y inland, Z up. It follows the existing room FBX export convention (`-Z` forward, `Y` up). For the game's imported handedness, Blender `(x,y,z)` corresponds to room-local Unity `(-x,z,-y)`. The measurements below are the literal Blender deck footprints, followed by their Unity counterparts. Structural beam/cap overhangs are included separately in the machine-readable bounds.

| Group | Room resource | Main deck Blender X | Main deck Blender Y | Main deck Unity X | Main deck Unity Z | Tris |
|---|---|---|---|---|---|---:|
| `Pier_S1` | `Stage1V4` | -5.25 .. 5.53 | -5.05 .. 3.60 | -5.53 .. 5.25 | -3.60 .. 5.05 | 2,068 |
| `Pier_S2` | `Stage2Bistro` | -5.25 .. 9.68 | -5.05 .. 3.60 | -9.68 .. 5.25 | -3.60 .. 5.05 | 2,236 |
| `Pier_S3` | `Stage3Restaurant` | -5.25 .. 11.68 | -5.05 .. 3.60 | -11.68 .. 5.25 | -3.60 .. 5.05 | 2,320 |
| `Pier_S4` | `Stage4Seafood` | -5.25 .. 13.68 | -5.05 .. 3.60 | -13.68 .. 5.25 | -3.60 .. 5.05 | 2,404 |

Every stage also includes the same rear-left approach, Blender X `[-6.40,-4.95]`, Y `[2.85,4.55]`; Unity X `[4.95,6.40]`, Z `[-4.55,-2.85]`. Its top is exactly zero and it overlaps both the main platform and quay coping. This location preserves the visible way in despite the current expanded-stage camera's right-edge crop.

Main and approach planks top at **Unity Y=0** (Blender Z=0), thickness .17 m. Support beams are below the deck; piling bottoms are -1.80 m, passing through the unchanged sea level -0.57 m. Exposed perimeter piling caps reach .21 m and the approach guide ropes .68 m, all outside the room floor rectangle. No new furniture or structure is placed inside the room.

Actual source room measurements took precedence over nominal layout dimensions, as logged in `comms.md`:

- S1's inherited `EXPORT_RoomShell` includes the existing terrace/jetty/foundation: X `[-4.860,4.805]`, Y `[-4.735,3.210]`, bottom Z=-.905. The new deck wraps that structure. Its existing foundation remains unchanged beneath the new deck.
- S2–S4 `EXPORT_GridFloor` spans X `[-4,9]`, `[-4,11]`, `[-4,13]`, Y `[-2.5,2.5]`, top Z=.04. The support deck sits .04 m below that floor top.
- Quay land begins at Blender Y=4.30 (Unity Z=-4.30). Coping projects slightly seaward. Solid land continues to Blender Y=37.50 behind the houses, with X `[-22,26]`. The backdrop is a shore, rather than another floating platform.

Enable `Quay`, `Boats`, `Clutter`, and **exactly one** `Pier_S1` .. `Pier_S4`. Do not display all four deck variants simultaneously. No room, water quad, camera or light object is exported in the FBX.

## Hierarchy and triangle counts

`RestaurantPier` has the seven group children below. Mesh children remain separate and named.

| Group | Mesh children | Triangles |
|---|---|---:|
| `Pier_S1` | `Deck_Planks_Beams_Pilings_S1` | 2,068 |
| `Pier_S2` | `Deck_Planks_Beams_Pilings_S2` | 2,236 |
| `Pier_S3` | `Deck_Planks_Beams_Pilings_S3` | 2,320 |
| `Pier_S4` | `Deck_Planks_Beams_Pilings_S4` | 2,404 |
| `Quay` | `Quay_Stonework_And_Coping` | 3,516 |
| `Quay` | `House_00_Gable_Windows` .. `House_08_Gable_Windows` | 584 each; 5,256 total |
| `Quay` | `Quay_Lamp_Posts` | 1,764 |
| `Boats` | `Boat_Rowboat` / `Boat_Rowboat_Mooring` | 452 / 26 |
| `Boats` | `Boat_Moored_Fisher` / `Boat_Moored_Fisher_Mooring` | 528 / 26 |
| `Boats` | `Boat_Harbour_Launch` / `Boat_Harbour_Launch_Mooring` | 528 / 26 |
| `Clutter` | `Harbour_Crates_Barrels_Bollards_Rope` | 2,148 |
| `Clutter` | `Quay_Hanging_Tyre_Fenders` | 612 |
| `Clutter` | `Quay_Festoon_Lights` | 960 |
| **All alternatives and shared meshes** | **24 mesh objects, 8 empty transforms** | **24,870** |

Shared geometry is 15,842 triangles. With one pier enabled the visible environment is 17,910 / 18,078 / 18,162 / 18,246 triangles for S1–S4, excluding the existing room.

## Material and lights

Every new mesh uses one slot, `Restaurant_Atlas_URP_V4`. The FBX meta remaps it to the existing `RestaurantAtlas.mat` GUID `93ede68a78343aa4bbc6d4deed7baeec`, which uses **Catchline/RestaurantAtlas** and the original `Resources/RestaurantAtlas/Restaurant_BaseColor` and `Restaurant_Surface` textures. No replacement material or texture is introduced.

Each face's UVs remain inside its atlas cell with an inset; `Color` corner attributes tint the shared atlas. Houses/boats use reduced pigment values, navy roofs/hulls, muted stone and restrained warm window/lantern cells. Broad timber planks, chamfered corners, octagonal piles and faceted rounded hulls maintain the room's chunky proportions.

The lighting JSON uses the same top-level `lights` array / `name`, `type`, `position_unity_m`, `blender_power` fields as the room recipes, with extra Blender positions, colour, radius and range documentation. Its positions **already include the FBX X mirror**: use them directly, without another X flip. Seven quay lamps use 20 W Blender reference power, warm RGB `(1,.60,.22)`, radius .30 m and suggested range 3 m. Window/festoon emission is in the atlas surface mask. The FBX contains no Blender lights.

## Render evidence and limits

Final evidence uses the unchanged room FBXs, one appropriate deck, all shared groups, and sea at -.57. Cycles/OptiX, 32 samples, denoising, AgX. The Blender material reproduces atlas base colour, vertex pigment, surface roughness/metal and the shader's 2.8 glow multiplier. Existing `LocalAO` room colours are preserved in the review binding. Blue dusk and a review-only warm area bounce approximate the game's ambient/practical lighting; these are **Blender art reviews, not an exact URP/post-processing match or native runtime acceptance**. The supplemental views have a deliberately wider lens and are identified separately.

| Stage | Exact live-camera desktop | Exact live-camera phone | Supplementary full surroundings |
|---|---|---|---|
| 1 | [1440×900](renders/stage1-1440x900.png) | [844×390](renders/stage1-844x390.png) | [Wide overview](renders/overview-stage1.png) |
| 2 | [1440×900](renders/stage2-1440x900.png) | [844×390](renders/stage2-844x390.png) | [Wide overview](renders/overview-stage2.png) |
| 3 | [1440×900](renders/stage3-1440x900.png) | [844×390](renders/stage3-844x390.png) | [Wide overview](renders/overview-stage3.png) |
| 4 | [1440×900](renders/stage4-1440x900.png) | [844×390](renders/stage4-844x390.png) | [Wide overview](renders/overview-stage4.png) |

**Existing framing limitation:** the exact game camera cannot show the complete backdrop and centre every expanded room at once. S1's phone lens crops most house facades and the original back-wall top. Stages 2–4's current camera clips the far-right terrace/deck edge and is offset from the expanded room centre. No new pier geometry causes that crop or blocks the interior. The rear-left bridge, quay edge and moored boats still establish the connection. Complete silhouettes, houses, all boats and continuous shore can be checked in the wider views. Full centred-room acceptance under the exact live lens remains outside this asset-only scope.

The exact camera conversion is Unity `(38,178,0)` to Blender `(52,0,+2)` degrees after the FBX X reflection. S1 uses Blender position `(.598,-17.088,13.359)`. S2–S4 use the current `StageRecipe` positions from their 1440 camera rows, with `FrameCamera`'s distance-scaled half-width, per-resolution FOV and lens shift. Their older source JSON's Blender yaw **-2** would aim differently; silently using that would hide the live framing issue. No camera/code change was made. Both discrepancies were logged as QUESTION lines and work continued from the files.

## Verification status

- Independent exported-FBX reimport: passed at 24,870 triangles; bounds/triangle counts match the authored meshes, required hierarchy present, one atlas material, finite UVs in `[0,1]`, vertex colours present.
- Raised pier geometry is outside the floor rectangles; deck remains at/below floor level. Pilings and all three hulls cross sea level. Objects use identity group transforms and metre scale.
- All four room FBX SHA256 hashes match the initial read-only inspection. Their preserved hashes are in `audit.json`.
- All eight final exact-camera renders and four supplemental overviews were personally opened and inspected. File hashes, image sizes and per-image framing notes are recorded in [visual-review.json](visual-review.json). The first-item pair and six extension renders were also opened before progressing to the next ordered item.
- Production asset is ready for the code owner to load and select by stage. No `.cs` edits, source room edits, Crew edits, Git commands or Unity execution. Runtime spawning, stage selection, optional lamp loading and native player framing acceptance have not been performed.
