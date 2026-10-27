# S10: Service markers

Source-art delivery by Codex 1 (Windows app). Ready for Claude import/review; no native Unity acceptance claimed.

Thirteen dish/order balloons: grilled fish, pan fish, fish and chips, soup, platter, crab, calamari, coffee, tea, lemonade, beer, fries and bread. Three transparent patience states (calm/warning/angry), tip coin +12, review star +1, six staff tasks (seat/cook/serve/clear/wash/repair), the soup substitution question with both buttons, and a composite broken-appliance warning card. Rings are static state art; animation and attachment to room actors remain integration work. Repeated label fields have separate layout uses. The broken-appliance stove/triangle/paper is one composite sprite.

New isolated fish/chips, soup and platter art replaced cuts contaminated by the proposal header. Two detached neighbour fragments were removed from pan-fish/crab during cutting. Final contact sheets were reopened after correction.

## Import contract

- Official mockup: `../../concepts/ui-10-service-markers.png` (844 x 390).
- 32 unique `v2-s10-*` tight RGBA PNGs, 44 placements, 29 measured live text entries, 5 sliced sprites.
- `layout.json`: top-left mockup pixels; repeated instances have explicit `use` names. `text-styles.json`: unique IDs, measured rectangles and fitted Fredoka sizes.
- `slices.json`: left, bottom, right, top in exported pixels. Exports are 3x their largest mockup placement; 3x resampling is not a claim of newly generated native detail.
- `manifest.json` records source crops, export sizes and hashes. Use its sprite filenames; no cross-screen name collisions were found.
- `spec.json` plus local `handoff.py` reproduce the cuts/composition. Original paintings and isolated sources remain in `provenance/`.

## Verification and limits

Independent audit passed tight alpha bounds, RGBA/3x sizes, unique names/IDs, text fitting, hashes, and pixel equality between the official mockup and downsampled offline reconstruction. Contact sheets were opened individually; measured placement/text overlays, slice stress proofs and reconstruction were opened in `measure-slice-proof.jpg`. `visual-review.json` seals the actual reviewed image hashes. Slice borders protect decorative corners in the supplied stress proof.

The final mockup is an authored composition of new ImageGen paintings, accepted restaurant kit pieces and live text. It is not a pixel-identical extraction of the earlier generated proposal. Manifest pixelExactClaimFalse/native3xDetailClaimFalse describe that provenance; the final authored mockup does match its reconstruction. Unity import, shader/alpha rendering, responsive placement, interaction, animation and lead/Mo acceptance remain unverified.

No Assets, production C# or Git changes. No commit. Reservations released after diary DONE.
