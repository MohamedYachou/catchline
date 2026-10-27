"""Append SOUND-4 evidence, then bind new-only artist delivery hashes."""
from pathlib import Path
import sys,json,hashlib,datetime
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parents[4];O=R/'Art/Audio/Real';A=R/'Art/Audio'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
edits=json.loads((O/'sound4-edits.json').read_text());metrics=json.loads((O/'sound4-metrics.json').read_text())
review=json.loads((O/'sound4-review.json').read_text())
assert len(review['sheets'])==5
for r in review['sheets']:assert sha(R/r['file'])==r['sha256']
report=A/'REPORT.md';old=report.read_bytes()
assert b'## SOUND-4 ' not in old,'Refuse duplicate report append'
parts=['\n\n---\n\n## SOUND-4 — recorded CC0 tutorial, refit and harbour cues\n',
'Codex 2 (WSL CLI). **15 recording-based candidates technically verified; auditory acceptance remains incomplete.** Three variants each of CoachPop, RefitFanfare, TabTap, CoinBuy and PageTurn. Source ownership was limited to Art/Audio; no Assets, code outside Art/Audio, metas, Unity, saves, watchdog or git changes. Existing deliveries preserved.\n',
'The brief calls SOUND2 a real-recording pipeline, but the preceding SOUND-2 report explicitly describes original synthesis. This delivery uses the real SOUND-3/CREW-FX source/scan pipeline and SOUND-2 measurement primitives. Every contributing source is explicitly CC0; no BY/BY-SA/NC source, synthesized excitation, generated sound or pitch shifting is used.\n',
'All outputs are uncompressed mono RIFF WAV, signed16-bit PCM at44100Hz. Source files are decoded only after clean Defender receipt and original SHA256 checks; extracted members match the scanned ZIP byte for byte. New bell preview scanned before decode: exit0, found no threats. Prior retained originals reuse matching clean scan receipts; no redundant download or scan was claimed.\n',
'Processing: trim/crop and downmix/resample,45Hz high-pass/per-cut low-pass,12ms source fades,9ms final fades, DC correction, gain-only transient control, real-source layering and loudness normalization. Targets: CoachPop -32, RefitFanfare -27, TabTap -38, CoinBuy -24 and PageTurn -29LUFS, with ±0.2LU variants. Short-cue loudness uses zero padding to400ms solely for measurement, following SOUND2; these padded values are not whole-game mix acceptance. Peak estimate uses4x polyphase interpolation, not a certified true-peak meter.\n',
'### Per-file evidence\n\n| Output | Recorded source(s), all CC0 | Duration,s | LUFS | 4x peak,dBTP | Review | Listening |\n|---|---|---:|---:|---:|---|---|']
byfile={r['file']:r for r in metrics['files']}
for e in edits['files']:
    m=byfile[e['file']];sources={r['source_page']:r['author'] for r in e['layers']}
    links=' + '.join(f'[{a}]({url})' for url,a in sources.items())
    parts.append(f"| [{Path(e['file']).stem}](Real/{e['file']}) | {links} | {m['duration_seconds']:.3f} | {m['integrated_lufs']:.2f} | {m['true_peak_4x_dbtp']:.2f} | [wave/spectrum](review/SOUND4-{m['family']}.png) | NOT HEARD; pending |")
parts += ['\n### Source licence and scan ledger\n\n| Recording/archive | Author / licence | Source / download | Scan evidence |\n|---|---|---|---|']
indexes=json.loads((O/'sources/index.json').read_text())+json.loads((O/'sources/crewfx/index.json').read_text())+json.loads((O/'sources/sound4/index.json').read_text())
used={l['original'] for e in edits['files'] for l in e['layers']}
for row in indexes:
    if row['local'] not in used:continue
    assert row['license']=='CC0-1.0' and row['clean'] and row['scan_returncode']==0 and sha(R/row['local'])==row['sha256']
    if 'sources/sound4/' in row['local']:receipt='Real/sources/sound4/ShipBell.scan.json'
    elif 'sources/crewfx/' in row['local']:receipt='Real/sources/crewfx/ShipHornClean.scan.json'
    else:receipt=f"Real/sources/{row['source_page'].rsplit('/',1)[1]}--{row['original_filename']}.scan.json"
    assert (A/receipt).exists(),receipt
    parts.append(f"| [{Path(row['local']).name}]({Path(row['local']).relative_to('Art/Audio').as_posix()}) | {row['author']} / [CC0-1.0]({row['license_url']}) | [source]({row['source_page']}) / [download]({row['download_url']}) | exit0, found no threats; [full receipt]({receipt}) |")
parts += ['\nSource limitations: Sojan’s **Ship Bell Single Ring** is a publicly offered HQ MP3 preview (44.1k mono decoded), not the login-gated original WAV. It is openly linked by the source page; no authentication workaround. Lossy encoding remains in the input. Nachtbold’s **Blümlisalp Horn** is a real steamboat, shortened to a faded toot for the celebration; the full natural recording remains in the accepted prior pack. Three refit variants reuse the same bell and horn takes with different lengths/timing. Other families use three distinct recorded wood/paper takes or distinct coin-montage passages; variant names do not imply new recording sessions.\n',
'### Review and limits\n',
'**What I heard: no claim — I could not listen in this session.** Available tools expose images and technical audio decoding, with no audio perception capability. All fifteen file rows therefore explicitly remain NOT HEARD. The requested per-file listening check, believable material/timbre, gentle/cartoon-free character, coin distinction by ear and native mix acceptance remain pending with Claude/Mo. [Playback controls for all fifteen cues](Real/sound4-listening.html) are ready. This is a technical delivery, not full SOUND-4 DONE acceptance.\n']
for name,text in review['observations'].items():parts.append(f'- **{name}, visual inspection only:** {text}')
parts += ['\nIndependent verification:15/15 format, duration, peak<=-3dBFS, DC<0.0007FS, zero endpoints and adjacent samples<=3PCMsteps, target deviation<1LU, variant loudness spread0.4LU and distinct SHA256 PASS. TabTap is at least3LU quieter and has lower sample peak than every Click in both existing recorded and synthetic packs. [Metrics and comparison evidence](Real/sound4-metrics.json).\n',
'Preservation:711 pre-existing audio files were checked byte for byte before this append. The original REPORT prefix remains unchanged; its historical SOUND2 receipt report hash is superseded only by this additive report update. The SOUND4 receipt binds new candidates/evidence; historical receipts are retained unchanged.\n',
'### Reproduction and pickup\n',
'Use `/home/mo/.venvs/catchline-ui/bin/python -B Art/Audio/Real/tools/acquire_sound4.py`, then `build_sound4.py`, then `check_sound4.py` (same interpreter and tools directory, from project root). Acquisition reuses a matching clean retained receipt. Build refuses existing SOUND4 manifest or cue files; an intentional revision must remove only its own manifest/cues before rebuilding. Checker can be repeated without touching WAVs and validates the preserved REPORT prefix. [Exact source cuts/layers](Real/sound4-edits.json), [opened-sheet observations/hashes](Real/sound4-review.json), [receipt](delivery-receipt-sound4.json). Source files outside Art/Audio are imported read-only for DSP/meter helpers.\n',
'Next: listen to every named variant, record actual heard observations, refine any source crop/timbre needed, remeasure/reopen affected evidence, then integrate and judge mixer behaviour. No remaining construction or technical-verification step is known; listening is the unmet brief requirement.\n']
with report.open('ab') as f:f.write(('\n'.join(parts)+'\n').encode())
assert report.read_bytes().startswith(old)
paths=[O/e['file'] for e in edits['files']]+[R/r['file'] for r in metrics['sheets']]
paths += list((O/'sources/sound4').glob('*'))+list((O/'tools').glob('*sound4.py'))+list(O.glob('sound4-*'))+[report]
paths=sorted({p for p in paths if p.is_file()})
receipt={'task':'SOUND-4','owner':'Codex 2 (WSL CLI)','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'TECHNICAL DELIVERY VERIFIED; PARTIAL against brief: listening not performed','new_wavs':15,'opened_review_sheets':5,'recording_licenses':'CC0-1.0 only','preserved_files':711,'report_original_prefix_bytes':len(old),'report_original_prefix_sha256':hashlib.sha256(old).hexdigest(),'auditory_review':'NOT PERFORMED; all15 pending. See REPORT and playback HTML.','native_integration':'outside artist scope; not performed','files':[{'file':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in paths]}
(A/'delivery-receipt-sound4.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('APPENDED REPORT; RECEIPT',len(paths),'files; auditory review explicitly pending')
