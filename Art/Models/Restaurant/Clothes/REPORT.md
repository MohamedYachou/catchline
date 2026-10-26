# Restaurant crew clothes — Codex 2 (WSL CLI)

Eight source/export pairs: one representative identity per live job, plus two kitchen support alternatives. This is the 3D part; the per-person 2D roster remains Codex1-owned. No runtime files changed.

| FBX + matching blend | Person | Live job / suggested use | Total triangles |
|---|---|---|---:|
| [Host_Mira.fbx](Host_Mira.fbx) | Mira | Reception | 13,086 |
| [Cook_Dirk.fbx](Cook_Dirk.fbx) | Dirk | Cook | 11,740 |
| [Server_Ana.fbx](Server_Ana.fbx) | Ana | Waiter | 13,804 |
| [Barista_Ines.fbx](Barista_Ines.fbx) | Ines | Barista | 13,227 |
| [Handyman_Olaf.fbx](Handyman_Olaf.fbx) | Olaf | Handyman | 14,212 |
| [Helper_Captain.fbx](Helper_Captain.fbx) | Captain | Helper | 11,511 |
| [PrepCook_Dirk.fbx](PrepCook_Dirk.fbx) | Dirk | Cook support, not a separate live enum | 11,888 |
| [Dishwasher_Olaf.fbx](Dishwasher_Olaf.fbx) | Olaf | Helper support, not a separate live enum | 14,012 |

## Integration

Use the full FBX when that representative person occupies the role. Each contains exactly four skinned meshes: unchanged face, unchanged expression, unchanged original hair, and the new `*_Outfit`. The outfit can be used as a sibling mesh on the identical CrewRig for other identities; preserve their own face/expression/hair and adapt the person-specific head crown and hand colours to that identity; the crown is part of the outfit mesh, not a universal hairstyle. Do not replace everyone with these six faces.

`Reception`, `Cook`, `Waiter`, `Barista`, `Handyman`, `Helper` are the current enum. Prep cook and dishwasher are wardrobe alternatives, not new runtime jobs; no bartender enum exists. Mira is the host; Dirk represents Cook; Ana Waiter; Ines Barista; Olaf Handyman; Captain Helper. Actual job mapping was read from RestaurantData.cs, RestaurantSim.cs and Cards.cs.

Metres, sole-level origin; Blender faces -Y/Z-up. FBX uses -Z forward/Y-up, scale units, no leaf bones. Armature is `CrewRig`, original 20 bones/rest/hierarchy and all 11 original clips at 24 fps. Guest-only additive Sit/Eat clips are not copied. No floor, camera, lights or presentation mesh is exported. Original image textures are embedded in FBX and packed in blend; local copies are in textures/. New cloth uses matte opaque material colours.

## Visual design and evidence

Mira follows the navy/ivory 2D option A with gold belt/pin, ivory neckline, dressed hair/barrette and earrings. Women wear smart ivory tops/navy skirts; men navy suits, contrasting lapels, ivory shirts and bow ties. Cooks wear ivory double-breasted coats and toques; prep/dish variants add teal aprons only for kitchen work. Existing compact CrewRig body proportions and original face/hair stay intact; this is not a literal reproduction of the taller illustrated 2D anatomy. Warm key/cool ambient lighting follows ui-service-desktop.png. Ana uses an ivory-top/navy-skirt variation rather than the teal illustrated dress; Ines uses an ivory blouse/navy waistcoat variation. Prep/dish comparisons show the same person’s standard 2D wardrobe for identity and palette, not a dedicated support-role drawing.

[All jobs at the elevated game view](renders/job-lineup.jpg). Each `renders/*-review.jpg` shows front, game camera, back and Walk; each `*-reference.jpg` compares with available same-person 2D or the desktop mockup. All views render from fresh FBX imports, not source-only geometry. Comparison references are recorded in comparison-manifest.json. All eight final four-view sheets, eight reference sheets and the lineup were opened; visual-review.json records those opens and file hashes. Visual review rejected separated waist primitives, flat crowns, a scalp gap below Ana’s bun and thigh/skirt penetration in Walk. Final exports use a continuous weighted coat, a wider skirt with walking clearance, textured scalp coverage and smooth swept hair locks; original identity geometry remains untouched.

## Checks and limits

validation.json records independent fresh FBX import checks against the original Assets/Art/Models/Crew/CrewRig.fbx: exact bone names/parents, rest matrices, Idle and Walk matrices sampled at five frames, all 11 clips present, normalized nonempty skin weights, exactly four meshes, and per-mesh world bounds below 1.5m. build-metrics.json records source identity geometry hashes, source provenance, triangles, rest bounds and byte-identical packaged texture hashes; validation.json confirms those images load after FBX reimport. Relative texture paths that failed after moving the source were corrected before delivery. Source face/expression/hair vertex and polygon signatures were asserted unchanged before export. Native Unity/avatar/material integration and collision-free blending across every runtime transition still need Claude’s game check. No native acceptance is claimed.

## Exported bounds (fresh FBX import)

| Asset / mesh | Min XYZ (m) | Max XYZ (m) |
|---|---|---|
| Host_Mira / Mira_EyesExpression | -0.102, -0.155, 0.662 | 0.102, -0.116, 0.841 |
| Host_Mira / Mira_Face | -0.198, -0.161, 0.516 | 0.199, 0.155, 0.950 |
| Host_Mira / Host_Mira_Outfit | -0.466, -0.190, 0.000 | 0.466, 0.203, 0.986 |
| Host_Mira / Mira_HairSculpt | -0.211, -0.159, 0.581 | 0.226, 0.324, 0.939 |
| Cook_Dirk / Dirk_Expression | -0.122, -0.153, 0.676 | 0.122, -0.107, 0.842 |
| Cook_Dirk / Cook_Dirk_Outfit | -0.466, -0.141, 0.000 | 0.466, 0.151, 1.095 |
| Cook_Dirk / Dirk_Hair | -0.199, -0.169, 0.627 | 0.199, 0.179, 0.943 |
| Cook_Dirk / Dirk_Face | -0.200, -0.176, 0.505 | 0.200, 0.155, 0.950 |
| Server_Ana / Ana_Face | -0.200, -0.162, 0.505 | 0.200, 0.155, 0.950 |
| Server_Ana / Server_Ana_Outfit | -0.466, -0.190, 0.000 | 0.466, 0.190, 0.960 |
| Server_Ana / Ana_Expression | -0.098, -0.156, 0.672 | 0.098, -0.117, 0.843 |
| Server_Ana / Ana_Hair | -0.209, -0.156, 0.654 | 0.209, 0.287, 1.078 |
| Barista_Ines / Ines_Hair | -0.211, -0.156, 0.312 | 0.211, 0.180, 0.939 |
| Barista_Ines / Barista_Ines_Outfit | -0.466, -0.190, 0.000 | 0.466, 0.190, 0.986 |
| Barista_Ines / Ines_Face | -0.200, -0.166, 0.505 | 0.200, 0.155, 0.950 |
| Barista_Ines / Ines_Expression | -0.104, -0.163, 0.672 | 0.104, -0.114, 0.844 |
| Handyman_Olaf / Olaf_Face | -0.200, -0.176, 0.505 | 0.200, 0.155, 0.950 |
| Handyman_Olaf / Olaf_Expression | -0.122, -0.153, 0.676 | 0.122, -0.107, 0.842 |
| Handyman_Olaf / Handyman_Olaf_Outfit | -0.466, -0.138, 0.000 | 0.466, 0.168, 0.986 |
| Handyman_Olaf / Olaf_Hair | -0.199, -0.177, 0.570 | 0.199, 0.179, 0.943 |
| Helper_Captain / Helper_Captain_Outfit | -0.466, -0.138, 0.000 | 0.466, 0.168, 0.986 |
| Helper_Captain / Captain_Face | -0.200, -0.166, 0.505 | 0.200, 0.155, 0.950 |
| Helper_Captain / Captain_Expression | -0.088, -0.153, 0.676 | 0.088, -0.119, 0.842 |
| Helper_Captain / Captain_Hair | -0.199, -0.168, 0.671 | 0.199, 0.181, 0.943 |
| PrepCook_Dirk / Dirk_Hair | -0.199, -0.169, 0.627 | 0.199, 0.179, 0.943 |
| PrepCook_Dirk / Dirk_Face | -0.200, -0.176, 0.505 | 0.200, 0.155, 0.950 |
| PrepCook_Dirk / Dirk_Expression | -0.122, -0.153, 0.676 | 0.122, -0.107, 0.842 |
| PrepCook_Dirk / PrepCook_Dirk_Outfit | -0.466, -0.141, 0.000 | 0.466, 0.151, 1.095 |
| Dishwasher_Olaf / Olaf_Face | -0.200, -0.176, 0.505 | 0.200, 0.155, 0.950 |
| Dishwasher_Olaf / Olaf_Hair | -0.199, -0.177, 0.570 | 0.199, 0.179, 0.943 |
| Dishwasher_Olaf / Dishwasher_Olaf_Outfit | -0.466, -0.135, 0.000 | 0.466, 0.155, 0.996 |
| Dishwasher_Olaf / Olaf_Expression | -0.122, -0.153, 0.676 | 0.122, -0.107, 0.842 |

No Assets/code/.meta/save/watchdog edits. No commit. Source builders and validation scripts are scoped to this folder.
