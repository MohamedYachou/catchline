# Mira 3D — side-by-side test brief

Two builders get this exact brief (cloud Fable and Codex Sol 6.1). Mo picks the better
Mira and that builder makes the rest of the crew. Lead: Claude (local).

## Goal

Mira, the navigator ("the explorer"), as a rigged 3D crew member who looks like her 2D
design. **Face and hair should be as close to a copy of the picture as 3D allows.** The
body only needs the prescribed clothes. Her **size on deck stays the same** as today's crew,
but she must be **far more detailed**, so she still looks great when the camera zooms right in.

## References (plain git files, no LFS needed)

`docs/screens/crew-styles/mira-ref/`

- `mira-portrait.jpg`: face, hair, cap and coat. The main target.
- `mira-fullbody.jpg`: body proportions and full outfit.
- `current-3d-crew-size.jpg`: today's 3D crew. Same height, proportions and readable silhouette.
- `in-game-voyage-1440.jpg`: how small the crew are on deck at normal zoom.

Full-size sheets: `docs/screens/crew-styles/*.png` (Git LFS).

## Must keep

- **Rig:** use the existing `CrewRig` skeleton unchanged: 20 bones, same names and hierarchy
  (`Art/Models/CrewRig/REPORT.md`; source `Art/Models/CrewRig/CrewRig.blend`, export
  `Assets/Art/Models/Crew/CrewRig.fbx`, both Git LFS). Skin Mira to it so the existing
  Idle / Walk / Carry / Cast / … actions play on her without changes.
- **Scale and axes:** bare-scalp height 0.95 m, head about 40% of height, chibi proportions
  as in the reference; floor pivot between the boots; Blender X right, −Y forward, Z up;
  FBX settings as CrewRig.
- **Materials:** flat parts reuse the game's palette names (`M_HullNavy`, `M_RailIvory`,
  `M_Skin`, `M_Rubber`, `M_Steel`, …; add new ones like `M_HairMira` with their hex). Face
  and hair detail may use textures: name those materials `Mira_Face`, `Mira_Hair` and ship
  the PNGs next to the FBX. Up to 2048² of texture in total.
- **Budget:** a hero-quality mobile character, up to 20k triangles including hair and props.

## Look

- **Face:** the portrait's face. Big dark glossy eyes with a white highlight and a small
  winged liner, defined brows, small rounded nose, confident closed-mouth smile, warm
  sun-tanned skin, soft blush. Sculpted or textured. The eyes and smile make it her.
- **Hair:** dark chocolate-brown, wavy, volumous. Loose waves framing both sides of the face
  from under the cap, and a high ponytail falling in big curls down the back. Built as
  sculpted game geometry (cards or chunky strands are fine), not particles.
- **Cap:** navy officer cap, cream band, brass compass-rose badge on the front, gold side
  button, dark visor.
- **Clothes:** navy double-breasted pea coat with lapels and brass buttons; cream cable-knit
  sweater showing at the collar; navy trousers; navy rubber boots.
- **Props:** small gold hoop earrings; dark binoculars with blue lenses on a brown leather
  strap around the neck. Hands in the crew style.

## Deliver

To `Art/Models/CrewV2/Mira-<builder>/` (`Mira-fable` or `Mira-sol`):

1. `Mira.blend` and `Mira.fbx` (+ texture PNGs).
2. `Mira-review.png`, one sheet with:
   - full body front, three-quarter, side and back;
   - face close-up beside `mira-portrait.jpg`;
   - Mira next to the current crew at the same scale;
   - one Walk frame and one Idle frame from the existing CrewRig actions.
3. `REPORT.md`: triangle count, texture sizes, how the rig was reused, and an honest list of
   what does not yet match the picture.

Do not change any other file and do not touch Unity scenes or scripts. Integration into the
game is a separate step after Mo chooses.
