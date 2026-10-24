# FISH-SILHOUETTE-1

Codex 1 (Windows app), 2026-10-24. Reusable rendering foundation; no fishing gameplay is connected.

`FishShadow` instantiates the actual ArtLibrary species prefab, retains its meshes/fins, and fits its upright nose-to-tail length to game-world metres. Length uses `GameData.Length * cbrt(clamp(kg, MinKg, MaxKg) / midpointKg)`. This is a consistent mass-scaling convention using existing game data, rather than an externally validated biological length model.

The preview row, left to right, is Herring 0.2 kg (0.2558 m), Mackerel 0.6 kg (0.3613 m), Cod 6 kg (0.7704 m), and ApexReefShark 14 kg (1.0000 m).

| View | Depth 0.2 | Depth 0.7 |
| --- | --- | --- |
| Normal boat, 1440 x 900 | [Image](boat-depth-0.2-1440.png) | [Image](boat-depth-0.7-1440.png) |
| Normal boat, 844 x 390 | [Image](boat-depth-0.2-844.png) | [Image](boat-depth-0.7-844.png) |
| Low close-up, 1440 x 900 | [Image](close-depth-0.2-1440.png) | [Image](close-depth-0.7-1440.png) |
| Low close-up, 844 x 390 | [Image](close-depth-0.2-844.png) | [Image](close-depth-0.7-844.png) |

All eight final images were opened individually. The normal view uses the existing anchored rowboat camera after its arrival easing settles (orthographic size 3.2011); the close-up uses a low camera and orthographic size 1.65. Fish remain at the same physical scale in both. Herring and mackerel are necessarily small at normal landscape zoom, especially at depth 0.7; a minigame camera must account for that when presenting readable nibble/fake cues. These are scratch Editor camera renders over the existing PTS water, without the runtime HUD. They do not establish installed-player, touch, or gameplay acceptance.

## Integration

Files: `Assets/Scripts/Game/Minigame/FishShadow.cs`, `Assets/Scripts/Game/Minigame/Resources/FishShadow.shader`, and `Assets/Editor/FishShadowChecks.cs` (plus metadata).

```csharp
var fish = new GameObject("Approaching fish").AddComponent<FishShadow>();
fish.transform.position = waterSurfacePosition; // root is the surface anchor
fish.Initialize(Species.Cod, 6f);
fish.Depth = .2f;       // 0..1, also submerges the child visual
fish.Visibility = 1f;  // 0..1; zero hides renderers
fish.SwimTo(targetSurfacePosition, .4f); // world position, metres/second
fish.Dart(Vector3.right); // horizontal 0.32-second burst, then resume destination
```

Root +Z is the nose. Use an unscaled hierarchy to preserve world-metre dimensions. Depth clearance keeps the model submerged; depth adds up to 1.25 m below its shallow position. Automatic motion runs only during play. Editor previews can call `Advance(seconds)` explicitly, and Depth/Visibility update in edit mode. Destroying or reinitializing the component disposes its owned visual/material without mutating source meshes/materials.

PTS water writes depth. The late transparent fish shader therefore compares against the **opaque camera depth texture**, allowing water to transmit the silhouette while boats/rocks occlude it. The URP camera must request depth and the renderer must copy depth **After Opaques**, as the current PC/Mobile renderer assets do. No pipeline or Sea assets were changed. This pass composites a tinted silhouette and soft Fresnel rim; it does not simulate optical refraction. Mesh details and fins share the transparent material, so their overlapping surfaces can retain internal detail.

The shader lives under Resources so runtime loading retains it in builds. It applies a tail-weighted vertex wave in common fish coordinates across all prefab parts, with corrected bend normals and expanded CPU culling bounds.

## Verification

[editor-check.log](editor-check.log) ends with API checks PASS, render checks PASS, and Unity exit code 0. The checks verify source-mesh identity, metre length, increasing weight/length, mass clamping, upright nose heading, Depth/Visibility/enable lifecycle, movement speed/arrival, dart duration, reinitialization cleanup, invalid mass, visible compositing over PTS water, fainter deep renders, rendered GPU bending with stationary roots (mean pixel difference 0.1299277), and complete opaque-blocker occlusion.

Run only in `C:/Users/momoy/Projects/Catchline-lead-sim`:

```text
Unity.exe -batchmode -quit -projectPath C:/Users/momoy/Projects/Catchline-lead-sim -executeMethod Catchline.EditorTools.FishShadowChecks.Capture -logFile C:/Users/momoy/Projects/Catchline/docs/screens/fish-silhouette-1/editor-check.log
```

The scratch-only menu `Catchline/Fish Shadow/Preview (scratch only)` creates a fresh save-isolated rowboat preview. The capture/check code rejects other project-directory names. [verification.json](verification.json) records final source equivalence and artifact hashes. No main-project Unity launch, save changes, art edits, installation, commit, or subagents were used for this assignment. Lead-owned `Minigame/BiteModel.cs` was preserved.
