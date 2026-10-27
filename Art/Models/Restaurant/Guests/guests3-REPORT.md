# RESTAURANT-GUESTS-3

Eight additive guests match the review faces09–16 in hair, skin, clothing colours and distinguishing accessories. Existing guest names and files are preserved.

| Face | FBX | Appearance | Triangles |
|---|---|---|---:|
| v2-guest-09.png | `Guest_Marta.fbx` | auburn bob, sage cardigan and cream blouse | 2,144 |
| v2-guest-10.png | `Guest_Nils.fbx` | dark hair and full beard, rust shirt | 1,810 |
| v2-guest-11.png | `Guest_Pia.fbx` | smaller child, auburn pigtails with bows, coral top | 2,290 |
| v2-guest-12.png | `Guest_Greta.fbx` | silver hair, cream sunhat, glasses and camera | 2,118 |
| v2-guest-13.png | `Guest_Henrik.fbx` | silver beard, navy cap and ochre jumper | 2,064 |
| v2-guest-14.png | `Guest_Zola.fbx` | dark skin, rounded black curls, coral jacket and gold studs | 3,920 |
| v2-guest-15.png | `Guest_Vera.fbx` | silver chignon, dark teal top, cream scarf and pearls | 1,962 |
| v2-guest-16.png | `Guest_Anton.fbx` | silver swept hair and moustache, navy blazer and burgundy ascot | 1,664 |

The rig is the current Clothes/CrewRig_Restaurant contract: 20 bones with unchanged rest matrices and all 20 current animation clips, plus the accepted guest Sit and Eat actions (22 total, 24 fps). Keeping every current clip takes precedence over reducing the count to 20. Pia uses a smaller fitted mesh while retaining the same skeleton. All meshes are skinned with normalized weights.

Materials contain the actual colours, with unique `Guest_<Name>_*` names. No crew-remapped M_SeaTeal/M_HullNavy/M_Skin/M_HairChestnut names are reused. UV0 and flat atlas-style colour blocks follow the accepted guest convention; no new bitmap atlas or transparent material. Foot contact and metre bounds were checked on independent FBX imports. Export uses Stage1V4's unit/axis/linear-colour settings with FBX_SCALE_UNITS.

`guests3-validation.json` records independent import results: all bone rest transforms and five samples of every current clip match exactly; ranges, weights, UV0, bounds, material names and all prior guest hashes pass. `guests3-metrics.json` contains source colours and source/export hashes. The preserved-file baseline remains in `guests3-preserved.json`.

Opened all eight `Guest_*-guests3-poses.jpg` sheets (original face beside fresh-import Idle/Sit/Eat), the exact `guests3-front-lineup-844x390.png`, and `renders-guests3/guests3-v4-angle-844x390.png`. The latter uses V4 camera orientation in an orthographic studio to compare the full cast; it is not a native service-room capture. The root-animation lineup overlap was corrected using review-only parent offsets before the final image. Nils/Henrik received chin beard volumes after the first visual pass. Distinguishing colours, silhouettes, hats and accessories read in the phone-size lineup.

Rebuild: Windows Blender5.2 through `run.py guests3-build guests3-validate guests3-lineup`, then Pillow contact assembly with `guests3-package.py`. The builder imports the current crew rig and the accepted guest Sit/Eat function without modifying either source.

No Assets, code, metas, git or prior guest changes. Source delivery only; Unity import, actor scale, material assignment and native service-camera acceptance remain with Claude. No temporary backups were needed for additive assets.
