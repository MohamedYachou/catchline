# V4 north-wall paint repair

Stage1V4.blend and Stage1V4.fbx redelivered; all239 exported node names unchanged,152488triangles unchanged. Geometry, transforms and secondary UV coordinates match the accepted source. No layout pieces renamed; EXPORT_* naming preserved for the lead's hide-by-name flow.

Changed50meshes only:48RearMasonry_* to atlas stonecool, RearCoping to navy, HighKitchenShelf to wooddark. Added neutral LocalAO=.85 to these formerly plain-material meshes, assigned the existing V4 atlas shader, and named their primary UV layer UV0 to match that shader. Each face samples one inset cell. Original atlas textures unchanged. Source colour/UV repairs avoid the game's former bright striped sampling.

validation.json fresh-import check passes239meshes, original bounds/topology/triangles and secondary UVs. backwall-changes.json records source geometry/transform/UV1 signatures and current export hash. backwall-final-audit confirms texture files resolve in Stage1V4/textures; FBX relative base path is textures/Restaurant_BaseColor.png.

Opened before/after1440x900+844x390 saved V4 camera renders. Final proof shows quieter slate wall, navy top coping and dark shelf beneath warm lanterns. backwall-review.jpg combines before/after plus upper-wall crops. Proof inherits accepted LookProof populated scene and light rig; the runtime r41 appearance is the lead's import check, not claimed here. Existing LookProof.blend is untouched.

Source editable with Blender5.2.1. Backwall helpers regenerate source/audit/proof; backwall-fix.py uses a temporary pre-change backup when present and otherwise repeats the paint repair on the production source; the temporary backup is removed after verification per standing instruction. Production source/export and saved before renders remain. No Assets/code/git changes.
