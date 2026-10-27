"""Write the integration report from final audited delivery metrics."""
import json
from pathlib import Path

D = Path(__file__).resolve().parent
O = D.parents[1] / 'Models/Townsfolk'
b = json.loads((O / 'metrics/build.json').read_text())
a = json.loads((O / 'metrics/audit.json').read_text())
names = ['Town_OldWoman', 'Town_Kid', 'Town_Fisherman', 'Town_Shopkeeper', 'Town_Walker']
descriptions = [
    'Woman; teal headscarf, silver fringe, long navy coat and open woven shopping basket on right forearm',
    'Girl; navy/ivory striped jumper, teal cap, navy trousers; mesh fitted at 0.75 adult neutral height',
    "Man; yellow oilskins, sou\u2019wester, rubber boots and chestnut moustache",
    'Woman; ivory apron with back ties, rolled cuffs exposing forearms and chestnut bun',
    'Woman; teal knitted jumper with ivory diamonds/bands, chestnut hair and crew red-orange beanie',
]
rows = '\n'.join(f'| `{n}` | {b["people"][n]["triangles"]} | {b["people"][n]["bounds"][1][2]:.5f} m | {d} |' for n,d in zip(names,descriptions))
actions = '\n'.join(f'| `{n}` | {v["range"][0]:g}\u2013{v["range"][1]:g} | {(v["range"][1]-v["range"][0])/24:g} s |' for n,v in a['actions'].items())
palette = '\n'.join(f'| `{n}` | `{c}` |' for n,c in b['palette'].items())
evidence = []
for n in names:
    studio = ', '.join(f'[{v}](renders/{n}/{v}.png)' for v in ['front','back','left','right','three-quarter'])
    walk = ', '.join(f'[{i/4:g} s](renders/{n}/Walk-{i}.png)' for i in range(5))
    evidence.append(f'| `{n}` | {studio} | {walk} |')

report = f'''# TOWNSFOLK-1 artist delivery

Five townsfolk use the original crew skeleton and its unchanged source actions. Four are women/girl and one is a man. Each person is one sibling skinned mesh with all wardrobe, face and carried details included; show one sibling at a time in the game. Optional Dog omitted to prioritize the required five.

Production files: [Townsfolk.blend](Townsfolk.blend), [Townsfolk.fbx](Townsfolk.fbx). Review fixture only: [same-scale lineup Blender scene](Townsfolk-lineup-review.blend). Do not import the review scene as the character asset.

## People and budgets

| Mesh | Triangles (maximum 2,500 each) | Rest mesh top above foot origin | Appearance |
| --- | ---: | ---: | --- |
{rows}

All objects and armatures have scale `(1,1,1)`. Adult bare heads use the crew's 0.95 m nominal top; headwear raises the measured bounds. Blender coordinates are metres, +Z up, -Y facing, foot origin at zero. The child bare head is 0.7125 m in Walk-neutral, with cap to 0.72975 m. The lineup uses the original crew captain at the same object scale, with no child rig scaling.

The child mesh is reduced to 0.75 of its adult counterpart in original Walk frame 1, then inverse-skinned into the unchanged adult rest skeleton. This keeps sleeves attached when the original adult animation rotates its joints. Its compensated rest armspan is wider than an adult's; judge child scale in the posed lineup, rather than measuring the T-pose width. Bones, joint pivots, bind armature, action keys and object scale remain unchanged.

## Integration contract

Keep `CrewRig` as the armature/root and retain every bone and its path. The five `Town_*` meshes are direct siblings parented to that armature, each with the original 20 named vertex groups and an Armature modifier targeting `CrewRig`. Do not create per-person rigs, rename bones, scale the child's bones, or insert a transform between `CrewRig` and its bones. Original source rest matrices and hierarchy compare exactly. Actual FBX rest matrices compare exactly to the shipped original FBX; Blender's reconstructed bone display tails are not used as a substitute for matrix parity.

For Unity integration, use the existing crew Legacy import and animation-root conventions, keep the imported hierarchy intact, remap the existing `M_*` materials by name and select one visible skinned renderer. Reuse existing crew Walk, Idle, Carry, Wait and other clips unchanged. A scene parent above the complete asset can position the character. The export uses `-Z` forward, `Y` up, metre unit scale, no added leaf bones, no animation simplification and all eleven source actions baked. No Unity import or runtime code is included in this artist-only delivery.

The original source's 24 fps action ranges are:

| Original action | Frames | Duration |
| --- | --- | ---: |
{actions}

Use the existing crew clip loop flags and movement speeds. The sampled Walk is the original 1-second action, frames `1,7,13,19,25` (0, 0.25, 0.5, 0.75, 1 seconds); endpoint is the original repeated pose. Translation along the quay, stops, animation selection and ground alignment belong to the runtime integrator.

The basket is attached to the old woman's right forearm and moves with it; it is part of her single mesh. Outfit and accessory shapes are deliberately chunky. Hair/scarf shells and apron edges use opaque materials with two-sided rendering in the Blender evidence; retain appropriate shared-material culling for visible cloth/hat undersides during native review. No transparency, image textures or downloaded assets are required.

## Shared palette

| Material name | sRGB base color |
| --- | --- |
{palette}

Only `M_Oilskin #E8B43A` and `M_Basket #B98F5E` are new materials. The requested red beanie uses the crew's existing `M_SafetyOrange #E36A35`, a warm red-orange, to preserve the explicit shared-palette restriction. No separate pure-red material was introduced. `M_OilskinYellow` is an existing crew color used for related trim. Existing skin, hair and cloth names and colors are retained.

## Evidence and checks

The independent [audit](metrics/audit.json) passes five mesh budgets, finite nonzero face areas, shared material colors/names, identity scales, all 20 bone names/parents/rest matrices, all vertices weighted with normalized weights, and the actual reimported FBX surfaces. Original source animation curve hashes are identical for all eleven actions. Every integer-frame world-bone pose (421 frames across all actions) matches the original source exactly and the shipped original FBX within {a['original_fbx_pose_max_error']:.9g}; the acceptance tolerance is 0.000002. Raw serialized FBX curve hashes differ because of Euler/handle representation, so export proof uses evaluated bone poses rather than claiming byte-identical FBX curves.

Actual FBX rest mesh surface error is at most {a['rest_surface']['max_vertex_error_metres']:.9g} m. At the five Walk samples, all five exported deformed meshes match source surfaces within {max(v['max_vertex_error_metres'] for v in a['walk_deformed_surface'].values()):.9g} m (audit tolerance 0.000020 m). Ordered face topology, counts and materials also match. All five people move under the original action.

All 51 final PNGs were individually opened by Codex 2 (WSL CLI): five true studio views and five original Walk samples per person, plus one lineup. Studio and Walk images are 640x600; lineup is 1800x660. They use an isolated Blender studio and orthographic cameras fitted to complete geometry with at least 2.5% normalized frame margin. Studio views use original Walk frame 1, with front/back and left/right cameras horizontal. Walk samples share one camera and fitting volume per person. Ground/studio/cameras are excluded from production files.

| Person | Five final studio views | Five final Walk samples |
| --- | --- | --- |
{chr(10).join(evidence)}

[Final lineup: OldWoman, Kid, Fisherman, Shopkeeper, Walker, original CrewRig captain](renders/Lineup/all-five-with-crew.png). All six use scale 1; the child's size is in its mesh.

[Render manifest](renders/manifest.json) records views, frame/time and crop bounds. [Visual review](visual-review.json) binds individually opened images to their SHA256, dimensions, assessment and production model hashes. [Build metrics](metrics/build.json), [original reference probe](metrics/reference.json) and [unchanged read-only dependency hashes](metrics/dependencies.json) record provenance. The [final delivery receipt](delivery-receipt.json) binds all delivered model/source/evidence files by size and SHA256.

Reproduction scripts: [build](../../Source/Townsfolk/build.py), [audit](../../Source/Townsfolk/audit.py), [render](../../Source/Townsfolk/render.py), [runner](../../Source/Townsfolk/run.py), [review recorder](../../Source/Townsfolk/review.py), [report writer](../../Source/Townsfolk/document.py), [finalizer](../../Source/Townsfolk/finalize.py). Successful logs: [build log](../../Source/Townsfolk/build.log), [audit log](../../Source/Townsfolk/audit.log), ''' + ', '.join(f'[{n} render](../../Source/Townsfolk/render-{n}.log)' for n in names) + '''.

Run `python3 Art/Source/Townsfolk/run.py build,audit` from the project root to rebuild/check; run `python3 Art/Source/Townsfolk/run.py render Town_Name` for each of the five names in separate bounded passes. Each pass regenerates the lineup; review and hash-bind the lineup after the final pass. Rebuilding invalidates prior review hashes; only record images after opening the new output. Run `python3 Art/Source/Townsfolk/finalize.py --preflight` before the final receipt.

These are source/export and isolated Blender visual checks. Native Unity material culling, Legacy playback, exact imported root paths, quay ground clearance and runtime appearance remain Claude's integration acceptance. All-action bone parity does not claim every costume collision was visually reviewed for all actions; the required five Walk samples per person were visually reviewed. No Unity launch, Assets write, git operation, player-save change or watchdog file was made for this delivery.
'''
(O / 'REPORT.md').write_text(report)
print('TOWNSFOLK REPORT WRITTEN', len(report), 'characters')
