from pathlib import Path
import json,hashlib
from PIL import Image
W=Path(__file__).resolve().parent;O=W.parent;R=W.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=json.loads((W/'roster.json').read_text());audits=[json.loads((W/f'{r["name"]}-audit.json').read_text()) for r in rows];assert all(a['passAll'] for a in audits)
for a in audits:assert a['sha256']==sha(O/f'{a["name"]}.fbx')
manifest=json.loads((O/'crew-manifest.json').read_text());assert len(manifest)==14 and len({r['name'] for r in manifest})==14
fields=('name','gender','hair','skinHex','hairHex','eyeHex','suitHex','note')
for row in rows:assert {k:row[k] for k in fields}==next(r for r in manifest if r['name']==row['name'])
# Other roster entries are preserved exactly against their delivered palette.
for row in json.loads((O/'female-palette.json').read_text()):assert {k:row[k] for k in fields}==next(r for r in manifest if r['name']==row['name'])
female_seal=json.loads((O/'female-delivery-audit.json').read_text())
for path,h in female_seal['hashes'].items():assert sha(O/path)==h,('Other roster changed',path)
base=json.loads((W/'source-hashes.json').read_text());changed=[p for p,h in base.items() if sha(R/p)!=h];assert not changed
proofs=[O/f'crew-contact-2{s}.jpg' for s in ['', '-grid','-844']]+[W/f'{r["name"]}-{kind}.png' for r in rows for kind in ['head','proof']]+[W/'crew-grid.png'];sizes={}
for p in proofs:
 with Image.open(p) as im:im.load();sizes[str(p.relative_to(O))]=list(im.size)
assert sizes['crew-contact-2-844.jpg'][0]==844
bounds=json.loads((W/'grid-bounds.json').read_text());assert len(bounds)==6 and all(min(b)>=0 and max(b)<=1 for b in bounds.values())
report=O/'REPORT.md';section=(W/'report-section.md').read_text();assert '## Codex 2 (WSL CLI) — CREW-QUATERNIUS-2' not in report.read_text()
with report.open('a') as f:f.write(section)
removed=[]
for p in W.glob('*.blend1'):removed.append(p.name);p.unlink()
seal={'owner':'Codex 2 (WSL CLI)','status':'Phase 1 source delivery PASS; Unity retarget/runtime and Mo acceptance remain unverified','crew':[r['name'] for r in rows],'auditPASS':True,'triangles':sum(a['triangles'] for a in audits),'sourcePreservation':{'checked':len(base),'changed':changed},'otherManifestRowsPreserved':8,'manifestRows':len(manifest),'matrixTolerance':1e-4,'maxRestMatrixError':max(a['maxRestMatrixError'] for a in audits),'maxBindMatrixError':max(a['maxBindMatrixError'] for a in audits),'maxBodyVertexErrorMetres':max(a['maxBodyVertexError'] for a in audits),'maxBodyUvError':max(a['maxBodyUvError'] for a in audits),'gridBounds01':bounds,'proofDimensions':sizes,'visuallyReviewed':'Six head proofs beside portraits; six fresh-FBX full-body game-camera proofs; six-row contact, corrected all-six grid and 844 overview opened. Attachments align, names match, no clipping.','sha256':{str(p.relative_to(O)):sha(p) for p in proofs+[O/f'{r["name"]}.fbx' for r in rows]},'temporaryBackupsRemoved':removed,'noCommit':True,'subagents':[]}
(W/'delivery-audit.json').write_text(json.dumps(seal,indent=2)+'\n');print(json.dumps({k:seal[k] for k in ['auditPASS','crew','triangles','sourcePreservation','manifestRows','temporaryBackupsRemoved']}))
