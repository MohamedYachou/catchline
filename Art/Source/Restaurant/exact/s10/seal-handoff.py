from pathlib import Path
import json, hashlib

root = Path(__file__).resolve().parents[2]
details = {
10: ('Service markers', 'ui-10-service-markers.png', 32,44,29,5,
'''Thirteen dish/order balloons: grilled fish, pan fish, fish and chips, soup, platter, crab, calamari, coffee, tea, lemonade, beer, fries and bread. Three transparent patience states (calm/warning/angry), tip coin +12, review star +1, six staff tasks (seat/cook/serve/clear/wash/repair), the soup substitution question with both buttons, and a composite broken-appliance warning card. Rings are static state art; animation and attachment to room actors remain integration work. Repeated label fields have separate layout uses. The broken-appliance stove/triangle/paper is one composite sprite.

New isolated fish/chips, soup and platter art replaced cuts contaminated by the proposal header. Two detached neighbour fragments were removed from pan-fish/crab during cutting. Final contact sheets were reopened after correction.'''),
11: ('Stage up: Cafe to Bistro', 'ui-11-stage-up.png',11,11,10,5,
'''New painted Bistro sign, awning and terrace vignette, stage path, terrace reward, and three benefits: more dining room, a bigger kitchen and quayside tables. No currency bonus or speculative upgrade price is asserted. The painted physical BISTRO sign is decorative lettering; interface headings and benefits are live text. This illustration is a concept, not a capture of the 3D room.'''),
12: ('Sleep / night to morning', 'ui-12-sleep.png',14,14,8,6,
'''New moonlit harbour vignette, tonight net, popularity change, tomorrow weather, booking hint and Sleep button. The +564 / +4 figures and Saturday clear-skies booking hint are illustrative mockup values; they do not change the economy or claim an actual forecast. The forecast sprite is the accepted sun icon.''')
}
for n, (title, concept, sprites, placements, texts, slices, content) in details.items():
    folder=root/'exact'/f's{n}'
    report=f'''# S{n}: {title}

Source-art delivery by Codex 1 (Windows app). Ready for Claude import/review; no native Unity acceptance claimed.

{content}

## Import contract

- Official mockup: `../../concepts/{concept}` (844 x 390).
- {sprites} unique `v2-s{n}-*` tight RGBA PNGs, {placements} placements, {texts} measured live text entries, {slices} sliced sprites.
- `layout.json`: top-left mockup pixels; repeated instances have explicit `use` names. `text-styles.json`: unique IDs, measured rectangles and fitted Fredoka sizes.
- `slices.json`: left, bottom, right, top in exported pixels. Exports are 3x their largest mockup placement; 3x resampling is not a claim of newly generated native detail.
- `manifest.json` records source crops, export sizes and hashes. Use its sprite filenames; no cross-screen name collisions were found.
- `spec.json` plus local `handoff.py` reproduce the cuts/composition. Original paintings and isolated sources remain in `provenance/`.

## Verification and limits

Independent audit passed tight alpha bounds, RGBA/3x sizes, unique names/IDs, text fitting, hashes, and pixel equality between the official mockup and downsampled offline reconstruction. Contact sheets were opened individually; measured placement/text overlays, slice stress proofs and reconstruction were opened in `measure-slice-proof.jpg`. `visual-review.json` seals the actual reviewed image hashes. Slice borders protect decorative corners in the supplied stress proof.

The final mockup is an authored composition of new ImageGen paintings, accepted restaurant kit pieces and live text. It is not a pixel-identical extraction of the earlier generated proposal. Manifest pixelExactClaimFalse/native3xDetailClaimFalse describe that provenance; the final authored mockup does match its reconstruction. Unity import, shader/alpha rendering, responsive placement, interaction, animation and lead/Mo acceptance remain unverified.

No Assets, production C# or Git changes. No commit. Reservations released after diary DONE.
'''
    (folder/'REPORT.md').write_text(report,encoding='utf-8')
    proofs=sorted(folder.glob('review-*.jpg'))+[folder/'measure-slice-proof.jpg',folder/'reconstruction-compare.jpg',root/'concepts'/concept]
    ledger={'screen':n,'reviewer':'Codex 1 (Windows app)','method':'Individual contact-sheet opens; measurement/slice/reconstruction montage opens; official 844x390 concept opens. No native runtime claim.', 'approvedForSourceHandoff':True,'nativeAcceptance':False,'opened':[{ 'file':str(p.relative_to(root)), 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in proofs]}
    (folder/'visual-review.json').write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
    audit=json.loads((folder/'audit.json').read_text(encoding='utf-8'))
    audit['visualReview']='visual-review.json: actual reviewed image hashes'
    (folder/'audit.json').write_text(json.dumps(audit,indent=2)+'\n',encoding='utf-8')

(root/'exact'/'s10'/'S10-S12-HANDOFF.md').write_text('''# Restaurant source-art handoff

Completed current assignment; ready for Claude import and review.

- S9: [Waiter correction](../s9/waiter-fix.json), two label regions only; outside pixels preserved. [Review](../s9/waiter-review.json).
- [Jo and Mei waiter outfits](../../clothes/2d/jo-mei-REPORT.md): each sheet/front/bust/compare, identity references and visual ledger.
- [S10 service markers](REPORT.md): 32 sprites / 44 placements / 29 text entries.
- [S11 Bistro celebration](../s11/REPORT.md): 11 sprites / 11 placements / 10 text entries.
- [S12 Sleep](../s12/REPORT.md): 14 sprites / 14 placements / 8 text entries.

All three official 844x390 mockups are in `../../concepts/`. Their exact packages include manifest, layout, measured text styles, slices, reference crops, contact sheets, reconstruction and independent audit. Total: 57 sprites, 69 placements, 47 text entries, 16 sliced sprites. Unique names, tight alpha, text fitting and reconstruction checks pass. The visual ledgers distinguish source-art verification from Unity acceptance.

No Assets, production C# or Git edits; no commit. Claude owns import/runtime/acceptance. No remaining authored steps; Codex 1 is idle and releases all current assignment paths.
''',encoding='utf-8')

for n in details:
    folder=root/'exact'/f's{n}'
    ledger=json.loads((folder/'visual-review.json').read_text())
    for item in ledger['opened']:
        assert hashlib.sha256((root/item['file']).read_bytes()).hexdigest()==item['sha256']
    assert json.loads((folder/'independent-audit.json').read_text())['pass_']
print('Handoff sealed: reports, 3 visual ledgers and independent checks PASS.')
