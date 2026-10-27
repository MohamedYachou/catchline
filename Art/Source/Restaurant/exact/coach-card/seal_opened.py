"""Seal the review files actually opened by Codex 1 after the final render."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;A=P.parent.parent;R=A.parents[2]
paths=['concepts/ui-coach-phone.png','concepts/ui-coach-desktop.png','concepts/ui-arrange-card-states.png','concepts/ui-closed-sign.png','exact/coach-card/slice-proof.jpg','exact/coach-card/contact-sheet.jpg','exact/s1-card-states/contact-sheet.jpg','exact/closed-sign/contact-sheet.jpg']
out=dict(reviewer='Codex 1 (Windows app)',method='Actually opened with view_image; final logical-size contexts and cut/slice proofs',actuallyOpened=[dict(file=str((A/p).relative_to(R)),sha256=hashlib.sha256((A/p).read_bytes()).hexdigest()) for p in paths],critique=['Coach preserves host identity, accepted cream/navy panel and orange primary action; 110-character sample fits3 lines, Got it/Skip separated.','Stored/Bistro/disabled-price states readable in original drawer; painted table examples retain proportions. Wallet and item price are illustrative reference values, not an affordability simulation.','Closed board moved to entrance gate after first review obscured host face. Label separate and readable at actual size.','Speech panel tail survives both nine-sliced widths; no visual/native acceptance claim.'])
(P/'visual-review.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print('Sealed',len(paths),'actually opened final review files')
