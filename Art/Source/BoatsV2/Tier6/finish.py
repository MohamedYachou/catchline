"""Seal the chosen concept sheet, prompts and concept-only handoff."""
from pathlib import Path
import hashlib,json
from PIL import Image
S=Path(__file__).resolve().parent;R=S.parents[3];O=R/'Art/Models/BoatsV2/Tier6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=S/'concepts.png'
with Image.open(p) as im:
    size=list(im.size);mode=im.mode;assert size==[1536,1024] and mode in ('RGB','RGBA');im.verify()
assert not list(O.glob('*.fbx')) and not list(O.glob('*.blend'))
files=[p,S/'prompt.txt',S/'scale-revision-prompt.txt',S/'layout-revision-prompt.txt',S/'concepts-first.png',Path(__file__),O/'REPORT.md']
receipt={'task':'TIER6-BOAT-CONCEPT-1','owner':'Codex 2 (WSL CLI)','status':'Concept delivery; STOP for Mo choice before3D','generator':'Built-in imagegen;3calls:initial,scale correction,final two-column layout','image':{'file':p.relative_to(R).as_posix(),'dimensions':size,'mode':mode,'sha256':sha(p),'opened':True},'visual_review':{'views':'A/B/C each side plus elevated rear-three-quarter; all6 opened on final sheet','comparisons':'Prep6.8m and Buoy8.5m painted side summaries, bow-aligned beside concepts; metre labels authoritative, painted widths approximate','style':'Navy/ivory/timber, lifted sheer and clinker strakes, enclosed forward cabins and open walkable aft deck','recommendation':'A Northstar9.4m:clearest compact offshore upgrade with generous open aft deck','limits':'Concept only, no engineering/navigation/mesh/crew-path proof; no Tier6model/FBX/Unity changes'},'files':{q.relative_to(R).as_posix():sha(q) for q in files}}
(S/'concept-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
for file,digest in receipt['files'].items():assert sha(R/file)==digest
print('TIER6 CONCEPT PASS',size,mode,len(files),'sealed hashes; no3D')
