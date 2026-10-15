# Task 06: rigged crew with animations

The current CrewBody reads thin and off-model. Make the crew from concept 15:
- chibi proportions: the head about 40% of total height
- round friendly face with simple eyes
- mitten hands, chunky boots
- total height 0.95 m

Blender sources, FBX exports, previews, REPORT. No Unity, no Scripts or Scenes. Keep the old CrewBody files untouched; this is a new asset.

1. **`Assets/Art/Models/Crew/CrewRig.fbx`:** one shared armature with Mixamo-style bone names:
   - `Hips`, `Spine`, `Spine1`, `Neck`, `Head`
   - `LeftShoulder`, `LeftArm`, `LeftForeArm`, `LeftHand` and the right side
   - `LeftUpLeg`, `LeftLeg`, `LeftFoot` and the right side
   - a `HatMount` bone or empty on the head at the hat seat
   - Skinned body mesh `Body` with clean weights, palette `M_*` materials only. Skin uses `M_Skin`; add more skin and hair tones as new `M_` names (list them).
2. **Outfits** as separate skinned meshes on the same armature, toggled by the game, named `Outfit_Captain` (navy jacket), `Outfit_Deckhand` (yellow oilskins), `Outfit_Fisherman` (orange oilskin with hood down) and `Outfit_Veteran` (navy cable-knit sweater, beard).
3. **Hats** as separate rigid meshes parented to `HatMount`: `Hat_CaptainCap`, `Hat_Beanie`, `Hat_Hood`.
4. **Animation clips** (actions) baked into the same FBX, looping where it makes sense, 24 fps:
   - `Idle` (breathing, slight sway)
   - `Walk`
   - `Carry` (walk with arms holding a fish in front)
   - `Bait` (hands at the rod butt)
   - `Cast` (one-shot overhead cast)
   - `Wait` (holding a rod, slight bob)
   - `Strike` (one-shot jerk back)
   - `Reel` (cranking)
   - `Row` (seated rowing)
   - `Cheer` (one-shot)
   - `Stow` (bend down and drop into the cooler)

   Clips must read clearly from the game camera at about 1 m tall on a 1600x900 screen: exaggerate.
5. **Previews:**
   - a turnaround of each outfit
   - a contact sheet with 3 key frames per clip, from the game angle
6. **REPORT:** bone list, clip list with frame ranges and loop flags, mesh and hat names, and new M_ names. Push.
