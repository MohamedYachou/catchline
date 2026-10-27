"""Append current delivery without changing historical SOUND-3 evidence."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[4];O=R/'Art/Audio/Real'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
E=json.loads((O/'crewfx-edits.json').read_text());M=json.loads((O/'crewfx-metrics.json').read_text());I=json.loads((O/'sources/index.json').read_text())+json.loads((O/'sources/crewfx/index.json').read_text());bylocal={r['local']:r for r in I}
assert len(E['files'])==26 and len(M['files'])==26
old=json.loads((O/'edits.json').read_text())['files'];assert len(old)==71
for e in old:assert sha(O/e['file'])==e['sha256'],e['file']
for e,m in zip(E['files'],M['files']):assert e['file']==m['file'] and e['sha256']==m['sha256']==sha(O/e['file'])
used={l['original'] for e in E['files'] for l in e['layers']}
for local in used:
 r=bylocal[local];assert r['clean'] and r['scan_returncode']==0 and sha(R/local)==r['sha256']
# Actual view_image inspections, recorded only after opening the final sheets.
review={'owner':'Codex 2 (WSL CLI)','method':'Opened with view_image; visual signal inspection only. No listening/native mix.','files':M['sheets'],'observations':{'Gull':'Repeated short calls and two longer harmonic passages; real field background remains.','Puffin':'Low harmonic calls plus continuous field background; fades cut an ongoing field recording, listening needed.','Foghorn':'Three separate short/long signal cycles; long inter-cycle silences omitted.','Horn':'Blümlisalp take avoids Albatros overload; low horn band and fading tail.','SealBark':'Single bounded call; species is unspecified.','ChestCrateOpen':'Final0.8s versions include wood creak beneath box/wood contacts; narrow creak transients retained.','ChestHeavyOpen':'Distinct squeak lengths; third movement substantially shorter.','TokenPour':'Revised three layered edits have multiple recorded contacts; same montage rotated, audible repetition not evaluated.','CardFlip':'115–135ms with tapered endpoints.','RewardChime':'Distinct real bell strikes; third includes secondary contacts, not a synthesized melody.'}}
(O/'review/crewfx-opened.json').write_text(json.dumps(review,indent=2)+'\n')
lic=['\n## CREW-FX-ART-1 addendum — 26 new outputs\n', 'Historical SOUND-3 rows above are unchanged. This addendum fills the five skipped families and adds chest cues. All six new originals passed Defender before decoding; five are used. The overloaded Albatros horn is retained only as a rejected source. Four previously scanned CC0 originals/archives also contribute. Exact cuts/placements and source hashes: [crewfx-edits.json](crewfx-edits.json).\n', '**Puffin derivative licence:** `SFX/Puffin_0.wav`, `Puffin_1.wav`, `Puffin_2.wav` are edited adaptations of Lawrence Shove’s Atlantic Puffin recording, copyright The British Library Board, and are distributed under [CC BY-SA4.0](https://creativecommons.org/licenses/by-sa/4.0/). Retain attribution, source link, licence and changes notice when distributing these clips. Changes: excerpts, mono/resample, bandpass, fades, DC correction and normalisation; no pitch change. This notice concerns the edited audio clips. Foghorn clips retain CC BY4; seal clip CC BY3. Public-domain/CC0 inputs and our additional Foley arrangement edits are released without added restrictions.\n', '| Output | Source / original | Author | Licence | Scan receipt |\n|---|---|---|---|---|\n']
for e in E['files']:
 seen=set()
 for l in e['layers']:
  key=l['source'];
  if key in seen:continue
  seen.add(key);r=bylocal[l['original']]
  if '/crewfx/' in r['local']:receipt='sources/crewfx/'+r['slug']+'.scan.json'
  else:receipt='sources/'+r['source_page'].rsplit('/',1)[-1]+'--'+r['original_filename']+'.scan.json'
  assert (O/receipt).exists(),receipt
  lic.append(f"| [{e['file']}]({e['file']}) | [source]({r['source_page']}) · `{Path(l['source']).name}` | {r['author']} | [{r['license']}]({r['license_url']}) | [exit0/no threats]({receipt}) |\n")
p=O/'LICENSES.md';assert '## CREW-FX-ART-1 addendum' not in p.read_text();
with p.open('a') as f:f.write(''.join(lic))
report='''
## CREW-FX-ART-1 — Group B delivery addendum

Codex 2 (WSL CLI). 26 new mono44.1kHz/16-bit PCM WAVs, technical checks passed; **listening and native mixing/acceptance remain with Claude/Mo**. The earlier SOUND-3 skip table is historical: all five families now have at least one real recording. Original71 SOUND-3 WAV hashes are unchanged. No Assets edits or Unity launch.

| Family / filenames in SFX/ | Count | Recording / Foley and limits | Duration |
|---|---|---|---|
| Gull_0..2 | 3 | Real herring gull, avphillips/PDSounds; distinct passages, Long Island | 2.95–3.33s |
| Puffin_0..2 | 3 | Real Atlantic puffin, Lawrence Shove/BL, Skokholm1965; field background retained; CC BY-SA4 adaptations | 2.3–3.3s |
| SealBark_0 | 1 | Mike Koenig zoo seal call; one take, species unspecified, not a verified grey seal | 0.62s |
| Horn_0 | 1 | Nachtbold’s steamboat Blümlisalp horn; one take; small fishing-boat suitability unverified | 1.896s |
| Foghorn_0..2 | 3 | Work With Sounds/Torsten Nilsson, Gislövsläge compressed-air horn; three separate short/long cycles | 9.3–9.4s |
| ChestCrateOpen_0..2 | 3 | Real wooden-box opening + tree/wood creak + distinct wood contacts. Same box take reused | 0.8s |
| ChestHeavyOpen_0..2 | 3 | Key/lock, distinct recorded door movements and wood; heavy-chest Foley. Third movement much shorter | 0.515–2.682s |
| TokenPour_0..2 | 3 | Three actual coin-handling passages layered at rotated placements; edited pour Foley, same montage reused | 2.07–2.11s |
| CardFlip_0..2 | 3 | Distinct recorded stick/hanger swishes + paper movement | 0.115–0.135s |
| RewardChime_0..2 | 3 | Three distinct household-bell recordings; single dings with source contacts, no generated melody | 0.428–1.232s |

Six new originals/pages/Defender receipts are retained in `sources/crewfx/`; **Albatros ship horn is rejected for severe source overload and contributes to no output**. Five newly downloaded originals plus four existing clean originals/archives contribute. Archive members are compared byte-for-byte with the scanned ZIP before decode. No login workaround, AI animal, oscillator/noise, pitch shifting or synthetic replacement. Foghorn is a full paired maritime signal rather than a short UI beep.

Processing matches SOUND-3: crop/downmix/resample,45Hz high-pass, per-cue low-pass,12ms source fades plus final9ms fades, DC correction, gain-only transient control, real-source layering and loudness mastering. Animal/horns/bells target -27LUFS, chest/coins -24, card flip -32. High-crest-factor impacts use transient gain control; listen for pumping or dulling. A filename variant is an edit, not proof of three independent takes. Seal and usable horn have one genuine take each; no duplicate variants fabricated. Puffin cuts retain field noise and fade an ongoing recording; listening must judge isolation. No subjective sound approval claimed.

Independent PCM decode:26/26 correct format, target deviation<1LU, each family spread<2LU, sample and4x estimated truepeak<=-3dBFS, DC<0.0007, zero faded endpoints; card flips<150ms. [crewfx-metrics.json](crewfx-metrics.json) has per-file numbers. All ten final family waveform/spectrogram sheets were opened; final crate/coin sheets reopened after refinement. [review/crewfx-opened.json](review/crewfx-opened.json) records observations. The source overview was also opened; this visual review cannot establish auditory suitability.

Open [review/crewfx-listening.html](review/crewfx-listening.html) locally for individual playback controls. Claude: audition source background and cuts, compare the three bell tones, choose chest timing for0.5–2.7s heavy takes, and mix contextually before native acceptance. Horn, seal and all other assets are candidates for integration, not tested game playback. Licence rows and ready-to-copy attribution are in [LICENSES.md](LICENSES.md) and [CREW-FX-CREDITS.txt](CREW-FX-CREDITS.txt); retain Puffin’s BY-SA4 adaptation licence.

Reproduction: run `python -B tools/acquire_crewfx.py`, then `python -B tools/build_crewfx.py`, then `python -B tools/check_crewfx.py` from this directory using the Catchline audio Python environment. The build refuses an existing `crewfx-edits.json`; explicitly remove only that own manifest before an intentional rebuild. Existing SOUND-3 originals must remain at their recorded paths. The doc tool appends once and refuses duplicate addenda. New manifests are separate from the accepted SOUND-3 manifests.
'''
p=O/'REPORT.md';assert '## CREW-FX-ART-1 — Group B delivery addendum' not in p.read_text()
with p.open('a') as f:f.write(report)
credits='''CREW-FX-ART-1 recorded audio credits
Changes to all clips: crop, mono44.1k resample, filtering, fades, DC correction and loudness processing; some physical Foley layered. No pitch change or generated sound.

Atlantic Puffin (Fratercula arctica), W1CDR0001416 BD3: recorded Lawrence Shove, copyright The British Library Board. Skokholm, Wales,1965.
Source: https://commons.wikimedia.org/wiki/File:Atlantic_Puffin_(Fratercula_arctica)_(W1CDR0001416_BD3).ogg
Puffin_0.wav, Puffin_1.wav, Puffin_2.wav are edited adaptations released under Creative Commons Attribution-ShareAlike4.0:
https://creativecommons.org/licenses/by-sa/4.0/

WWS Foghorn: Work With Sounds / Torsten Nilsson. Gislövsläge harbour.
Source: https://commons.wikimedia.org/wiki/File:WWS_Foghorn.ogg
Foghorn_0..2.wav edited under CC BY4.0: https://creativecommons.org/licenses/by/4.0/

Seal Call Zoo: Mike Koenig.
Source: https://soundbible.com/142-Seal-Call-Zoo.html
SealBark_0.wav edited under CC BY3.0: https://creativecommons.org/licenses/by/3.0/

Gull1: avphillips/PDSounds, public-domain author dedication.
https://commons.wikimedia.org/wiki/File:Gull_1.ogg
Blümlisalp Horn: Nachtbold, CC0.
https://commons.wikimedia.org/wiki/File:Bl%C3%BCmlisalp_Horn.ogg

CC0 physical Foley:
rubberduck: 100 CC0 SFX (wooden box, wood contacts, key/lock, door movement, paper, household bells).
https://opengameart.org/content/100-cc0-sfx
Department64, cleaned by AntumDeluge: Tree Creaking.
https://opengameart.org/content/tree-creaking
syncopika: Coin Sounds.
https://opengameart.org/content/coin-sounds
artisticdude: Swishes Sound Pack (camcorder-recorded sticks/hanger).
https://opengameart.org/content/swishes-sound-pack
CC0 licence: https://creativecommons.org/publicdomain/zero/1.0/
Additional creative arrangement edits by Codex2 for Catchline from CC0/public-domain material carry no added restrictions. Full per-output source/receipt/hash ledger: LICENSES.md and crewfx-edits.json.
'''
(O/'CREW-FX-CREDITS.txt').write_text(credits)
receipt={'task':'CREW-FX-ART-1','owner':'Codex 2 (WSL CLI)','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'new_outputs':26,'prior_sound3_unchanged_sha256':71,'used_clean_originals':len(used),'technical_checks':'PASS','listening':'NOT PERFORMED','native_mix_acceptance':'PENDING CLAUDE/MO','new_output_hashes':{e['file']:e['sha256'] for e in E['files']},'evidence_hashes':{str(p.relative_to(O)):sha(p) for p in [O/'crewfx-edits.json',O/'crewfx-metrics.json',O/'review/crewfx-opened.json',O/'CREW-FX-CREDITS.txt']}}
(O/'crewfx-verification.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('DOCUMENTED',len(E['files']),'prior preserved',len(old),'used originals',len(used))
