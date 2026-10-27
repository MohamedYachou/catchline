"""Seal manually reviewed MAP11 evidence; run only after the native review."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[3]
FIX = ROOT / 'docs/screens/map11-kelp-forest-1/fix'
LIFE = ROOT / 'docs/screens/kelp-life-1'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    evidence = json.loads((FIX / 'evidence-verification.json').read_text())
    assert evidence['nativeExit'] == 0 and evidence['liveMotion']
    observations = {
        'chart': 'Kelp forest card and 36,000 price readable; retained lead chart artwork.',
        'sail-out': 'Normal sailing camera and route remain legible; open water retains its wave read.',
        'sand-clearing': 'Warm sand clearing visible beside boat against teal bed; faceted perimeter and deeper anchor pocket visible.',
        'kelp-edge': 'Warm clearing, teal surround and rooted kelp visible. Normal raft anchor largely occluded by left HUD.',
        'post-line': 'Sand and teal read around boat; posts, kelp and existing gulls visible. No post relocation.',
        'life-kelp-motion': 'Rooted cluster pose changes subtly; quantitative four-cluster movement recorded in native log.',
        'life-otter': 'Supplementary camera: adults and pup readable on desktop; phone raft remains small and partly action-label occluded. Not ordinary-camera acceptance.',
    }
    reviewed = []
    for item in evidence['nativeImages']:
        path = FIX / item['path']
        assert sha(path) == item['sha256']
        stage = path.stem.rsplit('-', 1)[0]
        reviewed.append(dict(path=path.name, sha256=sha(path), individuallyOpened=True,
                             observation=observations[stage]))
    for item in evidence['images']:
        path = FIX / item['comparison']
        reviewed.append(dict(path=path.name, sha256=sha(path), individuallyOpened=True,
                             observation='Rejected deep-blue baseline compared with final shallow sand/teal native frame; original pixels retained.'))
    assert len(reviewed) == 22
    source = ROOT / 'Art/Models/KelpLife/OtterRaft.fbx'
    imported = ROOT / 'Assets/Art/Models/Environment/GullKelpForest/OtterRaft.fbx'
    assert sha(source) == sha(imported)
    receipt = dict(owner='Codex 1 (Windows app)', task='MAP11-FIX-AND-LIFE-1',
                   review='Manual individual native image inspection; lead/player acceptance separate.',
                   reviewed=reviewed, otterSourceSha256=sha(source), otterImportSha256=sha(imported),
                   otterRevision='KELP-RIBBON-FIX: fifteen slender dark-olive ribbons; unchanged adults/pup.',
                   limits=['Phone raft remains small/partly covered by action labels in supplementary evidence.',
                           'Ordinary Kelp edge camera largely hides raft behind left HUD.',
                           'No installed-player, touch or player approval of animation timing.'])
    (FIX / 'visual-review.json').write_text(json.dumps(receipt, indent=2) + '\n')
    p = FIX / 'README.md'
    text = p.read_text(encoding='utf-8-sig')
    text = text.replace('No navigation or terrain changed afterward.', 'Navigation and terrain geometry remain identical afterward; the material-only audit proves that equality.')
    text = text.replace('This preceded the final optical-constant and evidence-camera changes;', 'This preceded the final optical-constant, evidence-camera and delivered raft-ribbon changes;')
    text = text.replace('Native visual review is recorded after individual frame inspection below.', '''## Individual native review

Codex 1 opened all 14 final native frames and all eight comparison pairs individually; [hashed review record](visual-review.json). Sand clearing, Kelp edge and Post line now show warm sand clearings against a teal surrounding bed at both sizes, with rooted kelp and a deeper anchor pocket. The clearing boundary remains visibly faceted. Sailing retains open-water waves; chart price and labels remain readable. The live-motion pair shows subtle pose change, backed by measured movement of all four clusters.

The final imported raft includes Codex 2's delivered KELP-RIBBON-FIX: fifteen slender dark-olive ribbons. Source and import hashes are identical, and the runtime binding preserves its two olive colours. Desktop supplementary evidence shows adults and pup. At phone size the raft is small and partly covered by action labels; at the ordinary Kelp edge camera it is largely behind the left HUD. This is a recorded visibility limitation, not a claim of full ordinary-camera raft acceptance.

Final launch provenance: {matched}/{total} runtime/import inputs matched main at launch. The exact mismatches and both source hashes, if any, are in evidence-verification.json; all MAP11-owned files matched. Concurrent lead edits are preserved, not silently folded into capture provenance.'''.format(matched=evidence['matchedLaunchInputs'], total=evidence['totalLaunchInputs']))
    p.write_text(text, encoding='utf-8')
    p = LIFE / 'README.md'
    text = p.read_text(encoding='utf-8-sig').replace('Individual native visual inspection is recorded with the final MAP11 review.',
        'All eight life images were individually opened. Rooted kelp and post gulls are visible at both sizes. The final raft uses the delivered narrow dark-olive ribbon revision. Adults and pup read on desktop; the phone supplementary raft is small and partly action-label occluded. The ordinary-camera left-HUD limitation remains. See the [hashed individual review](../map11-kelp-forest-1/fix/visual-review.json).')
    p.write_text(text, encoding='utf-8')
    p = ROOT / 'Art/Models/Maps/GullKelpForest/REPORT.md'
    text = p.read_text(encoding='utf-8-sig').replace('on unchanged navigation/terrain.', 'on unchanged navigation/terrain geometry.')
    text += '\nFinal continuation imports the delivered KELP-RIBBON-FIX raft byte-for-byte, retaining its dark-olive colours. All 14 native frames and eight comparison pairs were individually opened; warm localized sand and rooted kelp read at both sizes. Ordinary-camera raft HUD occlusion and small/partly label-covered phone supplementary raft remain explicit review limits. See fix/visual-review.json for final image and imported-raft hashes.\n'
    p.write_text(text, encoding='utf-8')
    checked = 0
    for p in (FIX / 'README.md', LIFE / 'README.md', ROOT / 'Art/Models/Maps/GullKelpForest/REPORT.md'):
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if '://' in target or target.startswith('#'):
                continue
            assert (p.parent / target.split('#')[0]).exists(), (p, target)
            checked += 1
    (FIX / 'documentation-check.json').write_text(json.dumps(dict(localLinks=checked, allExist=True), indent=2) + '\n')
    print(f'MAP11 seal PASS: 22 individually reviewed images, exact revised raft import, {checked} documentation links')

if __name__ == '__main__':
    main()
