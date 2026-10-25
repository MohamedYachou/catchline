# TUTORIAL-ART-1 delivery

Codex 2 (WSL CLI). Artist construction A–D complete. Ten transparent PNGs are in this directory and copied byte-for-byte to `Assets/Art/UI/Tutorial/`. No import metadata or integration changes made.

| PNG | Canvas | Use |
| --- | --- | --- |
| mira-pose-wave | 512×640 | Hello, raised open glove |
| mira-pose-point | 512×640 | Arm points toward screen right |
| mira-pose-explain | 512×640 | Open palm |
| mira-pose-cheer | 512×640 | Raised fist, big smile |
| mira-pose-think | 512×640 | Finger at chin |
| mira-pose-map | 512×640 | Holds folded sea chart |
| tut-bubble | 256×160 | Cream speech panel, bottom-left tail |
| tut-pointer | 128×128 | Ivory glove points up-left |
| tut-arrow | 128×128 | Brass arrow points UP; rotate in UI as needed |
| tut-ring | 256×256 | Soft teal highlight, transparent centre |

## Integration notes

Bubble sprite border: **left48, bottom48, right48, top48 pixels**. Use sliced rendering. The tail is wholly inside the fixed lower-left48×48 corner; avoid shrinking below96px in either dimension. Recommended panel size at least256×160. Keep dialog text within an independently padded content rectangle;48px insets are a safe starting point. Centre fill is exact#F4EBDA. No text is baked in.

Poses share512×640 canvases and16px bottom placement margin. The generated masters were fit within480×608 without stretching; head heights naturally vary slightly by gesture. Use common bottom alignment for pose swaps, then check anchoring in the actual dialog. Portrait comparison normalizes approximate cap-to-chin height to160px for face review only; it does not alter delivered sprite proportions.

Ring has straight RGBA, no baked background or dark outline, and alpha0 at the centre and border. For additive rendering use an alpha-aware blend such as `SrcAlpha One`; ordinary alpha blending also preserves the soft teal ring. Runtime material brightness and button contrast need native review.

## Source and review evidence

Six reference-guided imagegen masters are preserved in `generated/{wave,point,explain,cheer,think,map}.png` at1122×1402. Approved reference: `Assets/Art/UI/Portraits/art108-mira.png`; wave established the shared half-body outfit reference for subsequent poses. The approved portrait was not changed. Four coach-mark sprites have editable native SVG sources beside the PNGs. No generation/export scripts were written to the project.

`review/sheet.png` was opened and inspected: unchanged approved portrait next to all six poses at approximately equal head size, followed by all four UI sprites on exact cream#F4EBDA and navy#1C3A5A. Consistent warm skin, dark curls, navy compass cap, ivory collar/gloves and binoculars; expressions and gestures read clearly. The screen-right point naturally turns her head. This is qualitative identity/style review rather than pixel-identical facial geometry.

`review/bubble-9slice.png` was opened and inspected: fixed48px borders stretched to400×200 and620×240 on both backgrounds. Tail and corner contours remain intact with continuous edges.

`delivery-checks.json` records all10 correct dimensions, RGBA modes, fully transparent outermost borders, source/Assets SHA256 equality, exact cream sample, ring centre alpha0 and opened evidence hashes. All checks pass. No Unity/batchmode/session/save access occurred. Native dialog sizing, pose switching, text layout and additive blending remain Claude/Mo integration checks.

No git/commit, scenes, scripts, metas, peer-owned folders or temporary backups. All reservations released at handoff; no remaining artist step or background work.
