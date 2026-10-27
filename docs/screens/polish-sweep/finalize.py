"""Bind reviewed sweep evidence and compare capture source snapshots with current main."""
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[2]
REPORT = PROJECT / 'docs/reports/POLISH-SWEEP-1.md'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(name, data):
    (ROOT / name).write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')

if __name__ == '__main__':
    snapshots = []
    for section in (1, 6, 9):
        run = json.loads((ROOT / f'section-{section}/native-run.json').read_text(encoding='utf-8-sig'))
        differences = []
        for row in run['sourceHashes']:
            p = PROJECT / row['path'].replace('\\', '/')
            current = digest(p) if p.exists() else None
            if current is None or current.upper() != row['sha256'].upper():
                differences.append({'path': row['path'], 'compiledSha256': row['sha256'], 'currentSha256': current,
                                    'scratchFixtureOnly': p.name == 'PolishSweepRuntime.cs'})
        snapshots.append({'section': section, 'launchedUtc': run['launchedUtc'], 'assemblySha256': run['assemblySha256'],
                          'comparedSources': len(run['sourceHashes']), 'differentFromCurrentMain': differences})
    write('source-age-final.json', {'checkedUtc': datetime.now(timezone.utc).isoformat(), 'snapshots': snapshots,
                                  'limit': 'Read-only comparison at this instant; Claude may continue changing production source.'})
    samples = []
    for section in (9, 10, 11):
        with (ROOT / f'section-{section}/effective-hit-samples.csv').open() as f:
            samples.extend(dict(section=section, **r) for r in csv.DictReader(f))
    exceptions = [r for r in samples if int(r['nominalGridHits']) != 81]
    write('effective-hit-summary.json', {'sampledControls': len(samples), 'full81of81': len(samples) - len(exceptions),
        'samplesPerControl': 81, 'gridSpanPixels': 43, 'gridPoints': '9x9; pixel centers spanning -21.5..21.5 from union center',
        'reportedDpi': sorted(set(r['dpi'] for r in samples)), 'exceptions': exceptions,
        'limit': 'No dispatched input; union-center sampling does not prove a largest usable square. Partial scroll cards, nonrectangular unions and covered controls require interpretation; no device safe-area/high-DPI/manual touch proof.'})
    # Run the independent image/link/native-exit audit before binding its output.
    exec(compile((ROOT / 'audit.py').read_text(), str(ROOT / 'audit.py'), 'exec'),
         {'__file__': str(ROOT / 'audit.py'), 'PENDING_OUTPUTS': {'phone-artwork-under44.csv', 'evidence-check.json', 'delivery-receipt.json', 'receipt-readback.json'}})
    excluded = {'delivery-receipt.json', 'receipt-readback.json'}
    paths = [p for p in ROOT.rglob('*') if p.is_file() and p.name not in excluded and '__pycache__' not in p.parts]
    paths += [REPORT, PROJECT / 'Assets/Editor/PolishSweepCapture.cs', PROJECT / 'Assets/Editor/PolishSweepCapture.cs.meta']
    write('delivery-receipt.json', {'createdUtc': datetime.now(timezone.utc).isoformat(), 'reviewedPngCount': 204,
        'scope': 'Capture fixture and evidence only; production source/save/installed-player unchanged by this task.',
        'files': [{'path': p.relative_to(PROJECT).as_posix(), 'bytes': p.stat().st_size, 'sha256': digest(p)} for p in sorted(paths)]})
    print('FINAL RECEIPT', len(paths), 'files')
