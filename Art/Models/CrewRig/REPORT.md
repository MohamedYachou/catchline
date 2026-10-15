# CrewRig — Task06

New asset; old `CrewBody` files, existing FBXs and pivots are unchanged. No Unity, Scripts or Scenes edits.

- Runtime export: `Assets/Art/Models/Crew/CrewRig.fbx`.
- Editable source: `Art/Models/CrewRig/CrewRig.blend`.
- Rebuild: Windows Blender5.2 headless, `Art/Source/build_crew_rig.py`.
- Validate source and FBX: Blender5.2 headless, `Art/Source/validate_crew_rig.py`; results in `validation.json`.
- Contact sheets: Python/Pillow `Art/Source/crew_contact_sheets.py`.
- Previews: `Previews/outfit-turnarounds.png`, `Previews/animation-contact-sheet.png`, `Previews/animation-contact-sheet-small.png`; individual rendered frames also retained.

Bare-scalp height **0.95m**, head0.38m (40%); round face, economical eyes/nose/smile, chestnut hair, mitten hands with thumbs, thick limbs, rubber boots. Hats extend above scalp. All variants share proportions and rig. Source X right, -Y forward, Z up; FBX converts to Unity Y up/+Z facing. Floor pivot is between boots at zero. The armature scale is1; source T-pose is the bind pose, previews use authored Idle.

## Mesh selection

Always enable `Body` (skin/face/hair, sleeves, boots/base garment). Enable exactly one skinned garment: `Outfit_Captain`, `Outfit_Deckhand`, `Outfit_Fisherman`, `Outfit_Veteran`. Garments include lower coverage and boots remain shared. Captain navy jacket has ivory lapels/gold buttons; deckhand yellow bib has straps/pocket; fisherman orange oilskins include a hood-down collar; veteran has raised cable-knit ribs and a silver beard.

Hats are separate rigid mesh children of the `HatMount` bone: `Hat_CaptainCap`, `Hat_Beanie`, `Hat_Hood`. Suggested combinations Captain/Cap, Deckhand/Beanie, Fisherman/Hood, Veteran/Beanie; enable one hat. Every variant is exported, so importing everything visibly stacked is expected until the consumer selects its variant. Source render visibility defaults to Deckhand/Beanie.

## Bones

20 total, no leaf/end bones:

```
CrewRig
└ Hips
  ├ Spine → Spine1 → Neck → Head → HatMount
  │         ├ LeftShoulder → LeftArm → LeftForeArm → LeftHand
  │         └ RightShoulder → RightArm → RightForeArm → RightHand
  ├ LeftUpLeg → LeftLeg → LeftFoot
  └ RightUpLeg → RightLeg → RightFoot
```

Shoulder branches attach to Spine1. All five skinned meshes target the same armature, with normalized explicit weights and two-bone elbow seam blending. Most chunky pieces use one-bone rigid weights; no finger or facial bones. Hats retain a rigid bone relationship. A Unity Generic rig can play these clips directly; Humanoid retargeting/mapping has not been tested. Hand bones provide external prop attachment sites. Carry holds an external fish; Bait/Cast/Wait/Strike/Reel expect an external rod. Props are deliberately absent from the crew FBX. Row lowers the hips 0.15m and folds the legs for a seat; set seat placement in the consumer.

## Actions and timing

24fps, sampled every frame, in place. Duration is (end-start)/24, including identical endpoint keys on loops. No horizontal root travel. Set Unity import loop settings explicitly from this table.

| Source action | Frames | Seconds | Loop |
| --- | --- | --- | --- |
| Idle | 1–49 | 2 | yes |
| Walk | 1–25 | 1 | yes |
| Carry | 1–25 | 1 | yes |
| Bait | 1–49 | 2 | yes |
| Cast | 1–33 | 1.333333 | no |
| Wait | 1–49 | 2 | yes |
| Strike | 1–19 | 0.75 | no |
| Reel | 1–25 | 1 | yes |
| Row | 1–49 | 2 | yes |
| Cheer | 1–49 | 2 | no |
| Stow | 1–49 | 2 | no |

FBX take names include the armature prefix `CrewRig|<Action>`. Blender reimport prefixes once more (`CrewRig|CrewRig|<Action>`). Match the suffix after the last `|`, or use the full imported clip name discovered by the consumer. Do not assume exact bare action names from an arbitrary FBX importer. Paths are below armature `CrewRig`, e.g. `CrewRig/Hips/Spine/Spine1/LeftShoulder/LeftArm`; meshes are siblings of Hips beneath the armature root. Integration may introduce another model root.

## Materials

New canonical sRGB: `M_HairChestnut` `#50392E`, `M_HairSilver` `#ADB6AF`. Add these to the game's material remap. All other exported materials reuse `M_Skin`, `M_HullNavy`, `M_RailIvory`, `M_OilskinYellow`, `M_SafetyOrange`, `M_Rubber`, `M_Steel`. Preview lighting/ground/materials are excluded from FBX. No bitmap textures or Unity material files.

## Validation and limits

Automated source checks: exact bone/mesh/action names;0.95m floor-to-scalp bounds; every skin vertex weighted with sum1; all garments use the same armature; rigid hats parented to HatMount;24fps; exact action frame ranges; meaningful movement; matching looping endpoint bone matrices. FBX reimport checks: one20-bone armature; all8 expected meshes; all11 actions with frame ranges preserved; all20 bones keyed, all imported curves retain one sample per frame and durations match the table; metre scale; normalized weights and skin armature relationships. `validation.json` records the actual imported names.

Outfit turnaround and animation renders were inspected from front/back/sides and the orthographic game camera. Contact sheet uses three distinct key frames per clip (start, one-third, two-thirds). Small sheet permits gameplay-scale review. The animations are intentionally broad, procedural authored first-pass clips; Unity scene lighting, exact equipment contact alignment, collision/foot IK, Humanoid mapping and runtime playback remain consumer integration checks. Tasks07/08 are not implemented by this batch.
