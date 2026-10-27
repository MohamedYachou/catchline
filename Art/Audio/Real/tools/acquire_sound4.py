"""Acquire publicly offered CC0 bell preview; scan before decoding."""
from pathlib import Path
import sys, re, json, hashlib, subprocess, datetime
sys.dont_write_bytecode = True
import requests
R = Path(__file__).resolve().parents[4]
O = R/'Art/Audio/Real/sources/sound4'
O.mkdir(parents=True, exist_ok=True)
page = 'https://freesound.org/people/Sojan/sounds/353233/'
h = requests.get(page, timeout=40); h.raise_for_status()
assert 'creativecommons.org/publicdomain/zero/1.0/' in h.text
(O/'ShipBell.html').write_text(h.text)
url = re.search(r'data-static-file-url="([^"]+-hq.mp3)"', h.text)[1]
p = O/'ShipBell-preview.mp3'; receipt = O/'ShipBell.scan.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if receipt.exists():
    row = json.loads(receipt.read_text())
    assert row['clean'] and sha(p) == row['sha256']
else:
    d = requests.get(url, timeout=45); d.raise_for_status(); p.write_bytes(d.content)
    command = ['/mnt/c/Program Files/Windows Defender/MpCmdRun.exe','-Scan','-ScanType','3','-File',subprocess.check_output(['wslpath','-w',str(p)],text=True).strip(),'-DisableRemediation']
    s = subprocess.run(command, capture_output=True, text=True, timeout=60)
    row = dict(source_page=page,download_url=url,author='Sojan',license='CC0-1.0',license_url='https://creativecommons.org/publicdomain/zero/1.0/',local=str(p.relative_to(R)),sha256=sha(p),bytes=p.stat().st_size,scan_command=command,scan_returncode=s.returncode,scan_stdout=s.stdout,scan_stderr=s.stderr,clean=s.returncode==0 and 'found no threats' in s.stdout.lower(),utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),limitation='Publicly offered HQ MP3 preview, not login-gated original WAV. No authentication bypass. Lossy source retained.')
    receipt.write_text(json.dumps(row,indent=2)+'\n')
assert row['clean'], row
(O/'index.json').write_text(json.dumps([row],indent=2)+'\n')
print('CC0 ship bell public preview; Defender CLEAN',row['bytes'])
