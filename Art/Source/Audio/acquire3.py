"""SOUND-3: direct CC0 recordings; Defender before any decode/extraction.
Downloaded material is data only. Only this locally authored script is executed.
"""
from pathlib import Path, PurePosixPath
import requests, re, html, json, hashlib, subprocess, zipfile, datetime
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT/'Art/Audio/Real'
SOURCES = [
 ('100-cc0-sfx','rubberduck',r'\.zip$'),
 ('water-splash-and-sand-footsteps','Peludo',r'splash[12]_0\.wav$'),
 ('swishes-sound-pack','artisticdude',r'\.zip$'),
 ('bicycle-sounds','AntumDeluge',r'\.zip$'),
 ('water-waves','transitking',r'\.flac$'),
 ('beach-ocean-waves','jasinski',r'\.flac$'),
 ('sea-and-river-wave-sounds','RandomMind',r'\.mp3$'),
 ('202-more-sound-effects','OwlishMedia',r'\.zip$'),
 ('baby-animals-sounds-pack','Technopeasant (compilation; individual recordists in pack credits)',r'\.zip$'),
 ('cut-peel-a-pumpkin','TinyWorlds',r'cut_pumpkin_0[123]\.ogg$'),
 ('coin-sounds','syncopika',r'\.wav$'),
 ('equipment-clicks-ii','LFA',r'\.wav$'),
 ('tree-creaking','Department64; cleaned by AntumDeluge',r'\.flac$'),
 ('bell-dingschimes','PWL',r'bell_ding[123]\.wav$'),
]
AUDIO={'.wav','.ogg','.flac','.mp3','.aif','.aiff'}
FORBIDDEN={'.exe','.dll','.js','.bat','.ps1','.com','.cmd','.msi','.vbs','.scr','.sh','.py'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def main():
 (OUT/'sources').mkdir(parents=True,exist_ok=True)
 index=[]
 for slug,author,pattern in SOURCES:
  url='https://opengameart.org/content/'+slug
  page=requests.get(url,timeout=45);page.raise_for_status()
  # Save documentary text outside the audio-only download quarantine.
  text=page.text
  assert re.search(r'field-name-field-art-licenses.*?creativecommons.org/publicdomain/zero/1.0',text,re.S),slug
  (OUT/'sources'/f'{slug}.html').write_text(text)
  links=[]
  for u,label in re.findall(r'href="([^"]+)"[^>]*>(.*?)</a>',text,re.S):
   u=html.unescape(u)
   if '/sites/default/files/' in u and re.search(pattern,u) and u not in links:links.append(u)
  assert links,slug
  directory=ROOT/'Art/Audio/Downloads'/('oga-'+slug)
  directory.mkdir(parents=True,exist_ok=True)
  for u in links:
   name=html.unescape(u.rsplit('/',1)[1]);p=directory/name
   scanfile=OUT/'sources'/f'{slug}--{name}.scan.json'
   if p.exists() and scanfile.exists():
    receipt=json.loads(scanfile.read_text())
    if receipt.get('sha256')==sha(p) and receipt.get('clean'):index.append(receipt);continue
   if not p.exists():
    r=requests.get(u,timeout=90);r.raise_for_status();p.write_bytes(r.content)
   win=subprocess.check_output(['wslpath','-w',str(p)],text=True).strip()
   command=['/mnt/c/Program Files/Windows Defender/MpCmdRun.exe','-Scan','-ScanType','3','-File',win,'-DisableRemediation']
   scan=subprocess.run(command,text=True,capture_output=True,timeout=60)
   clean=scan.returncode==0 and 'found no threats' in scan.stdout.lower()
   receipt={'source_page':url,'download_url':u,'author':author,'license':'CC0-1.0','license_url':'https://creativecommons.org/publicdomain/zero/1.0/',
    'original_filename':name,'local':str(p.relative_to(ROOT)),'sha256':sha(p),'bytes':p.stat().st_size,
    'scan_command':command,'scan_returncode':scan.returncode,'scan_stdout':scan.stdout,'scan_stderr':scan.stderr,
    'clean':clean,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
   dump(scanfile,receipt)
   assert clean,receipt
   if p.suffix.lower()=='.zip':
    with zipfile.ZipFile(p) as z:
     infos=z.infolist()
     for item in infos:
      q=PurePosixPath(item.filename.replace('\\','/'))
      assert not q.is_absolute() and '..' not in q.parts and ':' not in str(q),q
      assert q.suffix.lower() not in FORBIDDEN,q
      assert item.file_size<200_000_000 and (item.external_attr>>16)&0o170000 !=0o120000,q
     receipt['archive_members']=[i.filename for i in infos]
     # zipfile only; approved audio/text licences. Never execute anything.
     for item in infos:
      if item.is_dir():continue
      q=PurePosixPath(item.filename)
      if '__MACOSX' in q.parts or q.name.startswith('._'):continue
      if q.suffix.lower() not in AUDIO|{'.txt','.md','.pdf'}:continue
      target=directory/'extracted'/str(q);target.parent.mkdir(parents=True,exist_ok=True)
      target.write_bytes(z.read(item))
    dump(scanfile,receipt)
   index.append(receipt)
   print(slug,name,'CLEAN',p.stat().st_size,flush=True)
   dump(OUT/'sources/index.json',index)
 dump(OUT/'sources/index.json',index)
 print('VERIFIED',len(index),'downloads')
if __name__=='__main__':main()
