# Six additional restaurant guests

New source/export pairs: Guest_Gus, Guest_Hazel, Guest_Ivo, Guest_Jonas, Guest_Kai, Guest_Lena. Older accepted guest files are untouched. One independently skinned mesh and the same original 20-bone hierarchy per FBX. Table contact/sitting motion follows the accepted guest rig convention; actors retain original ~1 m proportions.

| Name | Read | Triangles |
|---|---|---:|
| Guest_Gus | older man | 1868 |
| Guest_Hazel | older woman | 1926 |
| Guest_Ivo | teenager | 1910 |
| Guest_Jonas | fisherman in cap | 1940 |
| Guest_Kai | smart dinner man | 1632 |
| Guest_Lena | smart dinner woman | 1880 |

Gus/Hazel: silver-haired older couple with glasses/moustache and berry cardigan/pearls. Ivo: ochre hoodie, dark hair, blue trousers and white sneakers. Jonas: olive cap, striped fisherman shirt and moustache. Kai/Lena: aubergine suit with bowtie/pocket square and burgundy dress/gold belt/earrings/updo. Their distinctive hair, clothes, skin and accessories retain real material colours.

**Every used material name begins Guest_<Name>_, never M_.** No M_SeaTeal/M_HullNavy/M_Skin/M_HairChestnut or other crew-remap key survives. Material sRGB colour intent and linear RGBA are in build-metrics-extra.json and validation-extra.json. Import should respect these materials directly; runtime tint logic for the older guests must not override these new assets with an unrelated default palette.

validation-extra.json fresh-import checks: one mesh, exact 20 bones/rest/hierarchy (<1e-5), normalized weights, world bounds under 1.5 m, original Idle/Walk poses, Sit/Eat clips, eating right-hand travel 0.12146 m. audit-extra-clips.json additionally checks **all 11 original clip ranges and five sampled poses per clip, all six guests, zero matrix delta**. Sit/Eat are the accepted additive seated cycles, not replacements for original actions.

All six extra-<Name>-poses.jpg sheets actually opened: Idle12, Sit1, side Sit1, Eat25 from independently imported FBXs. V4 saved camera orientation/58 mm lens translated close to each actor; side proof rotates yaw 90 degrees. Not exact full-room/native Unity captures. The source helper reuses only the accepted pose_action function, not the earlier build queue.

Author delivery complete. Runtime seating height/actual table placement and blend acceptance belong to lead after import. No Assets/code/git edits, no subagents.

Additional exact V4 framing proof (shared with formal host): ../Clothes/formal-game-{1440,844}.png and formal-game-cameras.json. Both saved camera positions/rotations/lens/resolutions used, neutral studio floor/lighting. All six guests bound to Idle in the corrected proof; both final images actually opened.
