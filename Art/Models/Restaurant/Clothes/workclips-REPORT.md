# Restaurant work clips

Delivered in `CrewRig_Restaurant.blend` and `CrewRig_Restaurant.fbx`, with the accepted wardrobe and original animations retained.

| Clip | Seconds | Playback |
|---|---:|---|
| Cook | 2.0 | Loop |
| Chop | 1.0 | Loop |
| Pour | 2.0 | Loop |
| Wipe | 2.0 | Loop |
| Wash | 2.0 | Loop |
| Repair | 2.0 | Loop |
| Greet | 2.5 | Once |
| CarryPlate | 1.0 | Loop |
| TakeOrder | 2.0 | Loop |

All actions use 24 fps and fixed roots. CarryPlate borrows the original walk cycle and compensates the hands to keep the plate level. Greet bows, then opens an arm, then returns to rest. Repair lowers the hips and bends both legs while the right arm works.

`workclips-validation.json`: independent fresh FBX comparison against the accepted pre-edit rig passes the complete 20-bone hierarchy/rest matrices, every one of the 19 previous meshes (vertices, topology, material slots/assignments, skin weights and UVs), and the ranges and five sampled poses of all 11 previous actions. All eight loops have matching endpoints within 2e-5; every new clip has measurable motion. CarryPlate hand-height travel stays below 0.1 mm.

`workclips-contact.jpg` shows all nine actions in four phases; individual full-size strips are in `workclips-renders/`. Actually opened the complete contact and full-size Cook, Repair, Greet and CarryPlate strips. V4 perspective orientation and 58 mm lens are retained in translated actor closeups, with studio lighting. Review tools/counters/plate are not in the production FBX. Native Unity transitions, loop flags and prop attachments remain for integration. Set Loop Time on eight work loops and leave it off for Greet.

Blender/FBX coordinates retain the accepted rig convention and units. Attach tools to the hands and align work stations to the action pose; no new bones or sockets were introduced. No Assets/code/git edits.
