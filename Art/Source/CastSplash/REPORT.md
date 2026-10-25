# CAST-SPLASH-ART-1

Codex 2 (WSL CLI). A–C complete: two sprites, editable SVG masters and the opened review sheet.

| Item | Source PNG and identical Assets/Art/UI/Crew copy | Canvas |
|---|---|---|
| A | fx-cast-ring.png | 256 × 256 RGBA |
| B | fx-cast-drops.png | 256 × 256 RGBA |

Masters: svg/fx-cast-ring.svg and svg/fx-cast-drops.svg. Rasterized using the existing catchline-ui CairoSVG/Pillow environment at1024px, then Lanczos downsampled to256px. No generator script file created. These are geometric extensions of the existing fx-splash/fx-glow family, inspected before construction.

A is one continuous, slightly uneven oval water ring: near-white #F9FCF3 core4.5 source pixels, soft sea-teal #168F9F shoulder9px at80%opacity. Its centre is fully transparent. The oval already contains water-plane perspective; preserve the square image aspect when displaying it, without adding a second perspective squash. Centre the image at the landing point. Code owns scale and fade; no motion blur, background, shadow, extra rings or animation is baked in.

B contains exactly seven separate near-white droplets with3.6px sea-teal rims and mint #A3E2DA inner accents. Their positions and rotations form a fan thrown upward/outward from the bottom-centre region. Transparent lower space is intentional; display using the full square rather than trimming to alpha bounds. It is one pop sprite, not a sprite sheet.

review/sheet.png is1440 ×900 and shows both sprites at actual40,96 and200px on cream #F4EBDA and navy #1C3A5A. Opened and inspected twice. First critique found the40px cream edges faint; strengthened shoulders to the house sea teal and regenerated/reopened the sheet. Final inspection: ring contour remains thin and continuous at40px, clear oval/empty centre at200px; droplets remain separate and fan direction reads on both surfaces. Review labels are outside exported sprites. The requested near-white remains the dominant large-size surface; teal supplies contrast on cream. No material issue remains in static art review.

Independent final checks pass for both exact sizes/RGBA, zero-alpha outer borders, source/Assets byte equality, SHA256 readback, valid SVGs without text/filter elements; alpha>127 has one connected ring and seven droplet components. The central ring rectangle x65..189/y105..159 is fully clear. Measurements and hashes are in delivery-checks.json.

This is static asset evidence. Unity import, runtime positioning/scaling/fade and actual gameplay acceptance remain Codex1/Claude/Mo scope, not verified here. Claude makes .meta files. No Unity, code files, git/commit, metas, saves, watchdogs, peer-file edits, subagents, background jobs or temporary backups. New-only assets; no major-change backup needed. Finished reservations released in comms.md.
