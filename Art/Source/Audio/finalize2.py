"""SOUND-2 receipt preflight; consumes manual review and independent verification."""
from pathlib import Path
import sys,json,hashlib,re,ast
sys.dont_write_bytecode=True
from verify2 import canonical,sha
R=Path(__file__).resolve().parents[3];O=R/'Art/Audio';D=Path(__file__).resolve().parent
def run(preflight=False):
 b=json.loads((D/'baseline2.json').read_text());m=json.loads((O/'metrics-sound2.json').read_text());v=json.loads((O/'verification-sound2.json').read_text());review=json.loads((O/'visual-review-sound2.json').read_text())
 assert m['result']==v['result']=='PASS' and v['aggregate_extension_present'] and v['files_verified']==20 and v['sheets_verified']==20
 assert len(review['sheets'])==20
 for a,s in zip(review['sheets'],m['sheets']):
  assert a['opened_individually'] and all(a[k]==s[k] for k in s) and sha(O/s['file'])==s['sha256']
 for r in m['files']:assert sha(O/r['file'])==r['sha256']
 for name,row in b['files'].items():
  if name not in b['aggregate_exceptions']:assert sha(R/name)==row['sha256'] and (R/name).stat().st_size==row['bytes'],name
 agg=json.loads((O/'metrics.json').read_text());assert agg.pop('sound2')==m and canonical(agg)==b['sound1_metrics_canonical_sha256']
 report=(O/'REPORT.md').read_bytes();assert hashlib.sha256(report[:b['sound1_report_prefix_bytes']]).hexdigest()==b['sound1_report_prefix_sha256']
 links=re.findall(r'\]\(([^)]+)\)',report.decode());assert links
 for dest in links:
  if dest=='delivery-receipt-sound2.json' and preflight:continue
  if dest=='delivery-receipt-sound2.json' and not (O/dest).exists():continue
  assert (O/dest).is_file(),dest
 for script in D.glob('*2.py'):ast.parse(script.read_text())
 for step,marker in [('build','BUILD'),('analyze','ANALYSIS'),('verify','VERIFY')]:
  log=(D/(step+'2.log')).read_text();assert 'SOUND2 '+marker+' PASS' in log and 'Traceback' not in log
 files={O/r['file'] for r in m['files']}|{O/r['file'] for r in m['sheets']}|{O/'metrics.json',O/'REPORT.md'}
 files|={p for p in O.glob('*-sound2.json') if p.name!='delivery-receipt-sound2.json'}
 files|={p for p in D.iterdir() if p.is_file() and p.name not in {Path(k).name for k in b['files'] if k.startswith('Art/Source/Audio/')}}
 assert not any('backup' in p.name or p.suffix=='.pyc' for p in files)
 receipt={'task':'SOUND-2','owner':'Codex 2 (WSL CLI)','status':'analysis-verified artist delivery; ear/native/mix acceptance external',
  'new_wavs':20,'individually_opened_sheets':20,'protected_unchanged_files':len(v['protected_unchanged_files']),
  'aggregate_exceptions':b['aggregate_exceptions'],'sound1_receipt':'unchanged; only two aggregate hashes superseded by this receipt',
  'report_links_checked':len(links),'files':[{'file':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(files)]}
 if not preflight:(O/'delivery-receipt-sound2.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print('SOUND2 FINAL',('PREFLIGHT' if preflight else 'RECEIPT'),'PASS',len(files),'files20reviewed sheets',len(links),'links',flush=True)
if __name__=='__main__':run('--preflight' in sys.argv)
