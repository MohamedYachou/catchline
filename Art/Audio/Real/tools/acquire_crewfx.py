"""CREW-FX real source acquisition; scan originals before decoding."""
from pathlib import Path
import requests, re, html, json, hashlib, subprocess, datetime
requests = requests.Session()
requests.headers.update({'User-Agent':'CatchlineAssetResearch/1.0 (recording attribution)'})
R=Path(__file__).resolve().parents[4]; O=R/'Art/Audio/Real/sources/crewfx'
S=[
('Gull','Gull 1.ogg','avphillips','Public-domain author dedication','https://commons.wikimedia.org/wiki/Template:PD-author'),
('Puffin','Atlantic Puffin (Fratercula arctica) (W1CDR0001416 BD3).ogg','Lawrence Shove; copyright The British Library Board','CC-BY-SA-4.0','https://creativecommons.org/licenses/by-sa/4.0/'),
('ShipHornClean','Blümlisalp Horn.ogg','Nachtbold','CC0-1.0','https://creativecommons.org/publicdomain/zero/1.0/'),
('ShipHorn','Cruise ship Albatros ship horn.ogg','Tvabutzku1234','CC0-1.0','https://creativecommons.org/publicdomain/zero/1.0/'),
('Foghorn','WWS Foghorn.ogg','Work With Sounds / Torsten Nilsson','CC-BY-4.0','https://creativecommons.org/licenses/by/4.0/'),
('SealBark',None,'Mike Koenig','CC-BY-3.0','https://creativecommons.org/licenses/by/3.0/')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for slug,title,author,lic,licurl in S:
 page='https://commons.wikimedia.org/wiki/File%3A'+title.replace(' ','_') if title else 'https://soundbible.com/142-Seal-Call-Zoo.html'
 h=requests.get(page,timeout=40);h.raise_for_status();(O/(slug+'.html')).write_text(h.text)
 if title:
  match=re.search(r'class="fullMedia".*?href="([^"]+)"',h.text,re.S);assert match,slug
  url=html.unescape(match[1]);url='https:'+url if url.startswith('//') else url
  ext='.ogg'
 else:url='https://soundbible.com/grab.php?id=142&type=wav';ext='.wav'
 p=O/(slug+ext);rp=O/(slug+'.scan.json')
 if p.exists() and rp.exists():
  old=json.loads(rp.read_text())
  if old.get('clean') and old['sha256']==sha(p):rows.append(old);print('cached',slug,flush=True);continue
 d=requests.get(url,timeout=60);d.raise_for_status();p.write_bytes(d.content)
 command=['/mnt/c/Program Files/Windows Defender/MpCmdRun.exe','-Scan','-ScanType','3','-File',subprocess.check_output(['wslpath','-w',str(p)],text=True).strip(),'-DisableRemediation']
 scan=subprocess.run(command,text=True,capture_output=True,timeout=60)
 clean=scan.returncode==0 and 'found no threats' in scan.stdout.lower()
 row={'slug':slug,'source_page':page,'download_url':url,'resolved_download':d.url,'author':author,'license':lic,'license_url':licurl,'local':str(p.relative_to(R)),'sha256':sha(p),'bytes':p.stat().st_size,'scan_command':command,'scan_returncode':scan.returncode,'scan_stdout':scan.stdout,'scan_stderr':scan.stderr,'clean':clean,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 rp.write_text(json.dumps(row,indent=2)+'\n');assert clean,row
 rows.append(row);print('SCANNED',slug,p.stat().st_size,lic,flush=True)
(O/'index.json').write_text(json.dumps(rows,indent=2)+'\n')
