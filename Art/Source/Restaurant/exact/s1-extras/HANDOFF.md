# Restaurant art pickup 04:15 - Codex 1

Finished art-only scope. Claude imports/wires/reviews; no Assets, production code, git or watchdog edits. S12 weather was already accepted/imported and was not reopened.

| Package | Delivery | Integration notes |
| --- | --- | --- |
| exact/s15 | 16 sprites: blank order bubble, patience track/fill, tip/question/broken pops, nine task icons, four-frame steam strip | Manifest/layout/text/slices + REPORT. Radial centre is transparent. Steam is four 192px cells, fixed padding needed for animation. Demo concepts/ui-15-markers.png is 844x390. |
| clothes/busts | 14 tight job busts, contact + identity/size proof | Ana corrected to plain navy waistcoat; Mira D remains host. Preserve aspect in 256 logical box, anchor bottom centre. Bram/Yusuf plain waiter suits remain provisional. Read manifest job/identity authority. |
| exact/s9/text-styles.json | Uniform 48 row styles; size fields only | Names 18px, job/tasks 14px, ranks 13px. Rank 14 with existing stroke exceeds fixed 10px rect. Rects and every other field retained. Evidence in text-size-review/. |
| exact/s1-extras | Store/Sell bubble buttons, red invalid placement | Same source dimensions as accepted rotate/placement sprites. Separate live labels; no slicing. New measured layout demonstrates lifted controls and red footprint beside valid footprint. Runtime uses actual ghost. |
| exact/s6 + arrange-entry | Unique Arrange background and chair sprites, appended manifest entries | Background byte-identical to accepted idle tab. Same slice borders. Separate live label. Daytime replacement of existing Service tab slot demonstrated; Claude decides navigation/visibility. |

Run independent verification from project root:

    uv run --with pillow python Art/Source/Restaurant/exact/s1-extras/delivery-audit.py

PASS: 35 exported sprites, 48 uniform S9 rows, all 35 accepted S6 manifest entries/sprite hashes preserved, 11 actually-opened proof hashes current, unique public names, tight static RGBA, transparent ring centres, steam frame geometry, identity-source hashes and new label fits. The steam strip intentionally preserves frame-cell padding. S1 exports retain accepted source density (at least 3x demonstrated logical rectangles), other measured static additions are 3x; resampling does not claim native 3x painted detail.

Actual context/contact/radial/steam/bust-size/S9-text/slice proofs were opened. Source paintings/prompts and audit scripts are retained as evidence; baseline-manifest is preservation evidence, not a restoration backup. Accepted S1/S6 concepts and layouts remain untouched. Native import, animation/radial behaviour, touch and Mo's visual acceptance remain unverified. No commit. All owned paths released; Codex 1 idle.
