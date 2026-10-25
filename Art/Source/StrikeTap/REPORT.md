# STRIKE-TAP-ART-1

Codex 2 (WSL CLI). A–C complete: editable SVG masters, two 256 × 256 RGBA PNGs, identical named copies in Assets/Art/UI/Crew, review evidence and technical receipt.

- A: fx-tap-burst.png; master svg/fx-tap-burst.svg.
- B: fx-tap-ripple.png; master svg/fx-tap-ripple.svg.
- Evidence: review/sheet.png, 1440 × 1000; review/goal-strike-panel.png, 690 × 330.

The brief explicitly gives the goal render priority when it disagrees with the prose. Art/Concepts/17-hud-fishing.png was opened and compared with its original compositor, Art/Source/build_ui_kit.py lines 89–95 and 205–209. The goal actually shows a **flat gold 12-point, horizontally broad burst**, without a white core or coral rim, and a **single circular mint ring**, without a second ring or teal edge. These delivered sprites preserve that reference. This is a deliberate, documented brief override; no speculative alternate sprites are supplied. TAP! lettering remains runtime text rather than baked into the new asset. No fish, bobber or panel pixels are baked into either sprite.

A uses #E6AD38. Its 24 alternating polygon vertices describe 12 tips, centred at (128,128), outer x radius114 and y radius82.08, valley x radius90 and y radius64.8. This exactly scales and recentres the original 128 × 96 kit geometry on a square transparent canvas; the wide silhouette is intentional. At square texture size256 the occupied width is228 and height164.16, so preserve square sprite aspect. To reproduce the goal's approximately136px visible burst width, draw the full canvas at approximately153px square. Code may scale/fade for strike feedback.

B uses #C1EEDE at0.8 opacity, a true circle centred at (128,128), radius108 and stroke8. This preserves the source ripple's dimensions, colour and opacity at twice its128px logical size. Its centre is entirely transparent. Preserve uniform scaling; do not apply the cast ring's water-plane oval aspect. A114px square draw gives the goal's approximately100px visible ring diameter. This is intentionally a pale ring on cream, matching the goal; it reads more strongly over the teal strike panel and navy review field. No stronger contrast or duplicate rings are claimed.

Both SVGs were exported at1024px with CairoSVG in the existing catchline-ui environment and reduced to256px with Lanczos. No image generation, new dependency, code file or Unity invocation was needed. Masters contain geometric primitives only, no text, bitmap embeddings or filters.

The required sheet includes actual32/64/200px versions of both final PNGs on cream #F4EBDA and navy #1C3A5A beside an unscaled crop of the goal's strike panel: source rectangle(615,726,1305,1056), top-left origin. The first opened sheet revealed clipped bottom size labels; its canvas was expanded and the final sheet reopened. Final static critique/audit/polish: burst silhouette reads at64px, ring is round with a clear centre, no artwork clipping; all size labels visible. Pale cream-background ripple at32px is intentionally subtle and explicitly shown. Only the evidence layout required correction; final sprite pixels did not change.

Independent final checks: exact256RGBA format, zero-alpha outer borders, one connected alpha component per sprite, opaque gold burst centre, zero-alpha140 ×140 ripple centre, square ring alpha bounds, exact source/Assets bytes, 24 burst vertices/12 tips and circular SVG geometry. Reference-shape coordinates were independently compared to original kit geometry. delivery-checks.json records measured bounds, metrics and SHA256 for masters, source PNGs, Assets copies, sheet, crop, goal and this report.

Static art delivery only. Import, animation and actual runtime HUD/player acceptance remain Claude/Mo scope. No .meta files, code files, git/commit, Unity, audio, saves, watchdogs, other-agent files, subagents or background processes. New-only construction required no temporary backup. All artist steps complete; no unresolved decision. Reservations released in comms.md.
