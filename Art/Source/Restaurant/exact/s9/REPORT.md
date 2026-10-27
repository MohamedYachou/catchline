# S9 Crew priorities - source-art handoff

Reference: ../../concepts/ui-9-crew-priorities.png (844 x 390). Six visible rows plus more-crew scroll and Save; repeat the row for the owned restaurant roster. Mira/Dirk/Ana/Sam/Ines/Olaf demonstrate Host/Cook/Waiter/Waiter/Barista/Handyman. Jobs are fixed by the card under the current plan, so job fields show locks; numbered task chips express reorderable priorities. This screen does not introduce free job reassignment. Rows and chips are static art; runtime scrolling/dragging/saving are Claude's work.

24 sprites, 89 placements, 56 measured text entries, 10 sliced sprites. Original painting 1846 x 852. The painting reinterprets faces; the delivered six bust sprites instead use the actual accepted clothes/2d originals (Mira D interim host). manifest.json records the original bust source and hash. Crew not visible in this example uses the same row template with its own accepted bust. No new roster or outfit acceptance is implied.

Import the v2-s9-* PNGs with manifest.json, layout.json, text-styles.json and slices.json. Layout uses an 844 x 390 top-left canvas and a distinct use for every repeated placement. Text is live; the coin emboss remains painted. Slice borders are left, bottom, right, top in exported pixels. Foreground pieces have tight alpha bounds; background is opaque. Exports are three times the largest measured placement, mechanically resampled; native 3x detail is not claimed.

Provenance includes the original generated painting, prompts, isolation sheets and reference crops. Isolated/recreated clean pieces differ in painted detail from the mockup; pixel-identical cutting is not claimed. Review sheets show actual reference crops above exports. reconstruction-compare.jpg is an offline sprite/text composition, not a Unity capture. Font sizing uses the supplied Fredoka Bold fitted to measured text regions; painted lettering is not proven identical.

Verified: bounds, unique uses/text IDs, RGBA/tight bounds/3x sizes, hashes, no cross-screen filename collisions, slice border validity, and opened export contacts/measurement overlays/reconstruction/slice stress pages. Native integration, interaction, final economy and lead/Mo acceptance remain with Claude. No Assets, production code, Git, saves or watchdog edits. No commit. Source-art scope only.

S9 correction: two Hauler labels replaced with Waiter; only two bounded generated text patches composited, every pixel outside those regions unchanged. Clean sprites remain text-free.
