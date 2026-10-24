# Mira — fable build

Side-by-side test entry per `docs/MIRA-3D-BRIEF.md`. Built headless with the bpy 5.2.3
module (same Blender generation as the CrewRig source); rendered with Cycles CPU.

## Files

- `Mira.blend` — editable source: the unchanged `CrewRig` armature and all 11 actions, the
  skinned `Mira` mesh, the rigid `Mira_Cap`, preview camera and lights. The three reference
  crew meshes from CrewRig.blend are kept hidden for the size comparison only.
- `Mira.fbx` — export with the CrewRig FBX settings (−Z forward, Y up, metres, all actions
  baked). Contains armature `CrewRig`, meshes `Mira` and `Mira_Cap`, 11 takes.
- `Mira_Face.png` 1024², `Mira_Gloss.png` 512² (roughness mask), `Mira_Hair.png` 512².
- `Mira-review.png` — front / three-quarter / side / back, face beside `mira-portrait.jpg`,
  current deckhand beside Mira at the same camera, Walk frame 7 and Idle frame 25.
- `stats.json` — counts and the FBX round-trip check.
- Builder: `Art/Source/build_mira_fable.py` (`--quick --samples 16` for a 35 s loop).

## Numbers

| | |
|---|---|
| Triangles | **18,018** (body 15,942 + cap 2,076) of the 20,000 budget |
| Textures | 1024² + 512² + 512² = 1.5 Mpx, under the 2048² (4.2 Mpx) budget |
| Bare-scalp height | 0.95 m (skin head top); hair puff reaches 1.00 m, cap 1.03 m |
| Head | 0.38 m, 40 % of height; floor pivot between the boots |
| Render | 165 s for the nine review frames at 48 samples, CPU |

## Rig reuse

The armature is appended from `CrewRig.blend` untouched: 20 bones, same names and
hierarchy, bind pose unchanged, 24 fps actions Idle/Walk/Carry/Bait/Cast/Wait/Strike/Reel/
Row/Cheer/Stow with their original frame ranges. `Mira` is skinned with explicit normalized
weights per part (head/hair/ears to `Head`, neck to `Neck`, torso blended Hips→Spine→Spine1
by height, two-bone elbow blend as the base crew, hands/feet to their bones). `Mira_Cap` is a
rigid child of `HatMount`, the same convention as `Hat_*`. The Walk and Idle frames on the
sheet are those actions played unmodified.

FBX round trip (re-imported into an empty scene): 1 armature, 20 bones, `Head` at 0.60 m,
meshes `Mira` + `Mira_Cap`, 11 actions, every vertex weighted to sum 1, cap parented to
`HatMount`.

## Materials

Palette (flat): `M_HullNavy`, `M_RailIvory`, `M_BandIvory`, `M_Skin`, `M_Rubber`, `M_Steel`.
New flat materials with their hex: `M_HairMira #5A3620` (fallback colour for the textured
hair), `M_CoatNavy #1E4A78`, `M_BootNavy #12304A`, `M_Brass #D9A441` (metallic .9),
`M_LensBlue #2E8FE0`, `M_Leather #6B4A2B`, `M_SweaterCream #F2E7CF`.
Textured: `Mira_Face` (base colour + roughness from `Mira_Gloss`), `Mira_Hair`.

## What matches

Big dark glossy eyes with two highlights and a winged liner, thick brows, small nose, closed
smile lifted to one side, warm tanned skin with blush. Dark chocolate wavy hair: fringe under
the visor, loose curls framing both sides to the collar, high ponytail springing from behind
the cap and cascading down the back. Navy officer cap with cream band, brass compass-rose
badge and gold side button. Double-breasted pea coat with lapels, six brass buttons and the
cream cable-knit collar; navy trousers; navy rubber boots; gold hoops; binoculars with blue
lenses on a leather strap. Same height and silhouette as the current crew.

## What does not match yet (honest)

- The hair is sculpted strands; the portrait's painted curls are finer and more varied.
  From the back the ponytail reads as thick ropes rather than a flowing mass.
- The face is a painted texture on a rounded head: no modelled eyelids, lips or cheek
  volume, so at close-up it is "her" from the front but flatter than the drawing in profile.
- The ink outline and cel shading of the 2D art are not reproduced; the render is lit, not
  drawn. A toon shader in Unity would close part of that gap.
- The lapels are simplified flaps; the coat has no seams or pockets.
- Cycles only in this environment, so previews are lit with the CrewRig preview rig, not the
  game's lighting; colours will shift slightly in Unity.
- Not verified in Unity: import, material remap for the new names, clip playback.
