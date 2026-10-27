from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent;ROOT=next(p for p in P.parents if (p/'Assets').exists());A=P.parent.parent
files=[A/'concepts/ui-17-hire.png',P/'contact-sheet.jpg',P/'slice-proof.jpg',A/'clothes/guests/contact-sheet-extra.jpg',A/'clothes/guests/extra/reference-comparison.jpg']
result=dict(opened={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},notes='Final views opened with view_image: hiring844x390, actual1x pieces, slice proof, all8 new guest192/64/32 contact and accepted-v-new64/32 reference comparison. Corrected contact ordering before these opens. Source art QA only; native acceptance pending.')
(P/'visual-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
