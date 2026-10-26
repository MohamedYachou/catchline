# MIRA-TALK-ART-1 — delivery

Owner: Codex 2 (WSL CLI). Source art complete; cropping, amplitude calibration and native integration belong to Claude. No Unity/runtime acceptance claimed.

## Integration files

Use the 18 top-level `<pose>-mouth-mid.png`, `<pose>-mouth-open.png`, and `<pose>-blink.png` files. Each is 1122 × 1402 RGBA at the accepted generated source framing. Apply the existing pose crop identically to the source and all three variants. Accepted originals and six game crops are unchanged (12 SHA-256 checks).

The accepted source supplies the closed/rest state. Wave, explain and cheer already have open smiling mouths in their accepted source: “closed” is the brief’s rest-state label, not a sealed-lips claim. Their mid frames have a smaller aperture than the original smile; mid/open are visually distinct. Do not replace the accepted rest art.

The `generated/` directory contains raw imagegen authoring intermediates only; integrate the top-level composites. Prompts/provenance are in [generation-prompts.json](generation-prompts.json). Feature-local masks retain the original pixels elsewhere and retain the source alpha everywhere.

## Face boxes and exact changed-pixel counts

Coordinates are source pixels from the top-left, `[left, top, right, bottom)`, exclusive right/bottom. Each box encloses all changes for that pose; mouth or eyelid edits occupy smaller regions.

| Pose | Face box | Mid pixels | Open pixels | Blink pixels | Review |
| --- | --- | ---: | ---: | ---: | --- |
| wave | [425, 365, 685, 590] | 11,965 | 11,893 | 19,522 | [sheet](wave-contact-sheet.png) |
| point | [390, 375, 610, 570] | 9,153 | 9,048 | 15,983 | [sheet](point-contact-sheet.png) |
| explain | [450, 365, 690, 590] | 11,882 | 12,163 | 18,355 | [sheet](explain-contact-sheet.png) |
| cheer | [412, 360, 645, 592] | 13,710 | 13,965 | 18,066 | [sheet](cheer-contact-sheet.png) |
| think | [410, 365, 645, 570] | 8,014 | 8,216 | 19,152 | [sheet](think-contact-sheet.png) |
| map | [399, 355, 638, 559] | 10,223 | 11,132 | 17,303 | [sheet](map-contact-sheet.png) |

Every sheet presents source/rest, mid, open and blink side by side, with a 3× nearest-neighbour face zoom below. All 18 final frames, six sheets and 18 binary diff masks were individually opened. Mouth contours and closed eyelids were checked for seams; no head, hat, hair or body movement is introduced. Blink mouths remain identical to their source. See [opened-images.json](opened-images.json) for the 42 reviewed output hashes.

## Suggested amplitude mapping

These are starting values, not measurements from the af_heart recordings. Use a 20 ms RMS window and normalize against the voiced line’s 95th-percentile RMS, with a nonzero denominator floor and values clamped to 0–1. Ignore leading/trailing silence when deriving the reference.

| Normalized loudness | Frame |
| --- | --- |
| Below 0.12 | Accepted source/rest (“closed”) |
| 0.12 to below 0.38 | Mouth mid |
| 0.38 and above | Mouth open |

For hysteresis, return to rest below 0.09 and return from open to mid below 0.31. Start with 20–30 ms attack, 60–90 ms release, a 60 ms minimum state hold and at most about 12 visual updates per second. Return to rest after the release interval at audio end. Claude should adjust these values against the actual recordings and game portrait size; amplitude swapping does not provide phoneme matching.

Blink for about 100–130 ms every 3–6 seconds, preferably during a quiet gap because these complete blink frames retain the rest mouth. Independent blinking during speech would require runtime eye-region composition with the current mouth state. No extra combined sprites are supplied.

## Verification and limits

- [talk-validation.json](talk-validation.json): all 18 frames PASS, zero changed pixels outside each face box, unchanged alpha and opposite facial features; exact counts, bounds and SHA-256 hashes per frame.
- [diff-masks/](diff-masks/): white means an actual changed RGBA pixel; black means identical to the source.
- [independent-audit.json](independent-audit.json): separate Pillow per-channel comparison without importing the compositor; exact binary-mask equality, bounds/count equality, unchanged source hashes and all 42 reviewed-output hashes PASS.
- [source-hashes.json](source-hashes.json): six accepted generated portraits and six accepted game crops protected.

Repeat the independent read-only comparison with:

```sh
/home/mo/.venvs/catchline-ui/bin/python Art/Source/Tutorial/talk/audit.py
```

`compose.py --final` rebuilds the composites and primary evidence from the raw authoring variants; it is not needed for integration. Do not regenerate files after native review without renewing the opened-image hashes and audit.

No git, Unity, Assets, .meta, .cs, player-save or watchdog operations. No temporary backups were required for this new, isolated output directory. No subagents. All assigned source-art steps complete; native crop, voice synchronization, listening and in-game acceptance remain lead scope.
