# SOUND-1 — original coastal foley and ambience

Codex 2 (WSL CLI),2026-10-25. **Artist pack complete by analysis.** No listening or native gameplay acceptance claimed; Claude owns copying/importing the files and ear-proxy review.

63mono cue WAVs (21families ×3variants) and3stereo30s ambience loops. Original offline numpy/scipy synthesis only: filtered noise, damped modal resonances, granular water, pressure/pitch envelopes and deterministic variation. No downloaded audio, recordings, external samples, TTS, network access or Unity synthesis render was used. Pillow draws the analysis PNGs only. These are physically inspired approximations, not recordings.

## File and integration contract

- All files: RIFF WAVE,44,100Hz,signed16-bit little-endian PCM, uncompressed. SFX mono; ambience stereo. Case-sensitive family names exactly match VoyageAudio.Cue. No normalization metadata or runtime DSP is required.
- Copy SFX to `Assets/Resources/Audio/SFX/<Cue>_<n>.wav` for n=0,1,2; ambience to `Assets/Resources/Audio/Ambience/<Name>.wav`. No files under Assets were authored in this assignment. Existing code-synthesized fallbacks remain the integrator’s choice.
- One-shot cues have7ms cosine endpoint tapers and exact zero first/last PCM samples. Three deterministic variants differ in seed/modal frequencies/noise and duration; choose one per event. Loop the ambience only.
- Ambience has exactly1,323,000frames per channel (30s), periodic whole-cycle noise plus wrapped events; an8ms smooth join on either side keeps a live bed with equal endpoint values and zero join slope. Do not add an end fade or a gap. Preserve the exact sample count when importing/looping.
- UI Select/Click/Purchase are86–134ms and~−32LUFS on the explicitly padded measurement, compared with~−24LUFS normal foley. Gull/SealBark/Bell/Horn target−27LUFS; ambience−28LUFS. Peak headroom may reduce sparse low impacts slightly.
- Winch variants are380/390/400ms with three damped pawl contacts and rope friction. Offline variant-cycled overlap at8and12Hz has unity-gain sum peaks below−4.85dBFS; at0.65gain below−8.59dBFS. This is a bounded two-second synthetic stress case, not a guarantee for every mixer combination. Start at current game gains and judge by ear before changing balance.

## Recipes and opened contact sheets

Each SFX sheet contains all three files, each with waveform and absolute-level log-frequency spectrogram (80Hz–16kHz,−100to−15dBFS). Loop sheets show left/right plus a±20ms mono seam preview. Seam row LUFS/peak metadata belongs to the full parent loop; its40ms duration identifies the zoom. All24sheets were individually opened.

| Family / sheet | Duration range,s | Measured LUFS range | Recipe |
|---|---:|---:|---|
| [Cast](review/Cast.png) | 0.590–0.610 | -24.20–-23.80 | Air/line band noise sweeping through a smooth arm envelope, soft spool tick and outgoing line hiss. |
| [Splash](review/Splash.png) | 0.710–0.730 | -24.20–-23.80 | Filtered broadband water impact, low displaced-water body and irregular falling bubble grains. |
| [Bite](review/Bite.png) | 0.290–0.310 | -24.20–-23.80 | Two small wood/float knocks above a narrow water plip, short line tension rub. |
| [Reel](review/Reel.png) | 0.940–0.960 | -24.20–-23.80 | Jittered ratchet teeth, quiet low spool modes and an amplitude-shaped rope/friction bed. |
| [Land](review/Land.png) | 0.540–0.560 | -24.20–-23.80 | Wet low board impact with secondary wooden settling and small water grains. |
| [Stow](review/Stow.png) | 0.470–0.490 | -24.20–-23.80 | Crate-body wood modes, sliding rubber friction and one delayed damped contact. |
| [Moor](review/Moor.png) | 0.640–0.660 | -27.06–-26.11 | Low timber contact, rope stick-slip and a second quieter hull settling knock. |
| [Sale](review/Sale.png) | 0.710–0.730 | -24.20–-23.80 | Paper/receipt rustle followed by an irregular restrained coin stack; no musical progression. |
| [Select](review/Select.png) | 0.101–0.109 | -32.20–-31.80 | Quiet damped wooden switch touch with low filtered friction, under150ms. |
| [Purchase](review/Purchase.png) | 0.126–0.134 | -32.20–-31.80 | Short paper rustle and one muffled coin contact, under150ms. |
| [Gull](review/Gull.png) | 1.240–1.260 | -27.20–-26.80 | Three nasal pitch-curved harmonic calls with breath band noise and rough amplitude modulation. |
| [Bell](review/Bell.png) | 2.590–2.610 | -27.20–-26.80 | Soft clapper contact and five inharmonic buoy-bell modes with unequal decays. |
| [Creak](review/Creak.png) | 0.640–0.660 | -24.20–-23.80 | Pressure-shaped rope/wood stick-slip with wandering pulse rate and low body resonance. |
| [Horn](review/Horn.png) | 2.690–2.710 | -27.20–-26.80 | Slowly swelled low reed/hull harmonics with slight drift and filtered breath. |
| [Click](review/Click.png) | 0.086–0.094 | -32.20–-31.80 | Quiet plastic latch pair, short inharmonic body and damped friction, under150ms. |
| [Winch](review/Winch.png) | 0.380–0.400 | -24.20–-23.80 | Short rope pull with three irregular damped hauler pawl contacts; tail dies before450ms. |
| [CrabClack](review/CrabClack.png) | 0.330–0.350 | -24.20–-23.80 | Three staggered dry claw contacts exciting short plastic tray modes. |
| [SealBark](review/SealBark.png) | 0.840–0.860 | -27.20–-26.80 | Two low rough harmonic barks with descending pitch and a throaty filtered-noise layer. |
| [NetSlap](review/NetSlap.png) | 0.670–0.690 | -24.41–-23.80 | Broad wet-net noise impact, low timber modes, scattered water droplets and rope settling. |
| [Gut](review/Gut.png) | 0.420–0.440 | -24.20–-23.80 | Short pressure-shaped wet knife friction with subdued low water grains; no tonal reward. |
| [Coins](review/Coins.png) | 0.790–0.810 | -24.20–-23.80 | Irregular small coin pile with differing inharmonic modes and a low wooden supporting tray. |

| Loop / sheet | LUFS | Stereo correlation | Recipe |
|---|---:|---:|---|
| [HarbourDay](review/HarbourDay.png) | -28.00 | 0.603 | Periodic low lapping bed, wet piling laps, distant filtered gull calls and rope creak; broad stereo. |
| [OpenSea](review/OpenSea.png) | -28.00 | 0.600 | Periodic slow swell and soft high wind, irregular low hull slaps and small water scatter. |
| [Skerries](review/Skerries.png) | -28.00 | 0.603 | Periodic surf wash against rocks, filtered distant seal pairs and a darker low water body. |

## Decoded-file checks

[metrics.json](metrics.json) contains every file’s duration/frame count,format, sample peak,4×polyphase estimated true peak, integrated LUFS,padding, RMS, DC offset, PCM endpoints andSHA256. For loops it also records per-channel seam value/slope steps, interior-difference p99 and seam RMS. [verification.json](verification.json) independently reads every WAV using the standard wave decoder, checks exactly the66expected filenames/hashes/formats/endpoints and24PNGhashes, and records the environment and known-tone meter check. [synthesis inventory](synthesis.json), [opened-sheet receipt](visual-review.json), [delivery receipt](delivery-receipt.json).

LUFS uses BS.1770 K-weighting with400msblocks/100msstride,−70LUFSabsolute gating and−10LUrelative gating. For cues shorter400ms, zeros extend the measurement to one400msblock; `measurement_zero_padding_seconds` records the amount. This makes those short-clip numbers padded energy measurements, not a claimed native-duration integrated reading. The meter matches a1kHz−20dBFSpeak sine at~−23.00LUFSmono and~−19.99LUFSstereo. The4×polyphase true-peak estimate is not a certified hardware meter.

Results:
- Highest decoded sample peak: **-3.406dBFS**; highest4×estimated true peak: **-3.400dBTP**, both below−3.
- Largest within-family loudness spread: **0.945LU** (limit2LU).
- Largest absolute decoded DC offset: **0.0000398FS** (limit0.0007).
- Every one-shot has zero endpoints and adjacent endpoint samples within3PCMsteps. All loops have exactly zero value and slope discontinuity at the join in both channels; no fade-to-silence.

| Loop | Seam value step,L/R | Seam slope step,L/R | ±20ms RMS/whole,L/R |
|---|---|---|---|
| HarbourDay | [0.0, 0.0] | [0.0, 0.0] | 0.922, 0.808 |
| OpenSea | [0.0, 0.0] | [0.0, 0.0] | 0.825, 0.998 |
| Skerries | [0.0, 0.0] | [0.0, 0.0] | 1.285, 1.445 |

## Per-file readings

All levels below are from decoding the actual delivered PCM16WAVs. Full DC/channel/seam details are in metrics.json.

| WAV | Duration,s | Sample peak,dBFS | Est.true peak,dBTP | LUFS | Measurement zero pad,s |
|---|---:|---:|---:|---:|---:|
| [SFX/Cast_0.wav](SFX/Cast_0.wav) | 0.590 | -12.27 | -12.09 | -24.20 | 0.000 |
| [SFX/Cast_1.wav](SFX/Cast_1.wav) | 0.600 | -11.82 | -11.68 | -24.00 | 0.000 |
| [SFX/Cast_2.wav](SFX/Cast_2.wav) | 0.610 | -12.82 | -12.82 | -23.80 | 0.000 |
| [SFX/Splash_0.wav](SFX/Splash_0.wav) | 0.710 | -6.45 | -6.44 | -24.20 | 0.000 |
| [SFX/Splash_1.wav](SFX/Splash_1.wav) | 0.720 | -5.66 | -5.66 | -24.00 | 0.000 |
| [SFX/Splash_2.wav](SFX/Splash_2.wav) | 0.730 | -5.73 | -5.68 | -23.80 | 0.000 |
| [SFX/Bite_0.wav](SFX/Bite_0.wav) | 0.290 | -8.06 | -8.00 | -24.20 | 0.110 |
| [SFX/Bite_1.wav](SFX/Bite_1.wav) | 0.300 | -6.55 | -6.53 | -24.00 | 0.100 |
| [SFX/Bite_2.wav](SFX/Bite_2.wav) | 0.310 | -7.00 | -6.98 | -23.80 | 0.090 |
| [SFX/Reel_0.wav](SFX/Reel_0.wav) | 0.940 | -8.90 | -8.90 | -24.20 | 0.000 |
| [SFX/Reel_1.wav](SFX/Reel_1.wav) | 0.950 | -9.79 | -9.73 | -24.00 | 0.000 |
| [SFX/Reel_2.wav](SFX/Reel_2.wav) | 0.960 | -10.01 | -9.90 | -23.80 | 0.000 |
| [SFX/Land_0.wav](SFX/Land_0.wav) | 0.540 | -3.78 | -3.77 | -24.20 | 0.000 |
| [SFX/Land_1.wav](SFX/Land_1.wav) | 0.550 | -5.04 | -5.03 | -24.00 | 0.000 |
| [SFX/Land_2.wav](SFX/Land_2.wav) | 0.560 | -3.67 | -3.66 | -23.80 | 0.000 |
| [SFX/Stow_0.wav](SFX/Stow_0.wav) | 0.470 | -6.48 | -6.45 | -24.20 | 0.000 |
| [SFX/Stow_1.wav](SFX/Stow_1.wav) | 0.480 | -4.99 | -4.99 | -24.00 | 0.000 |
| [SFX/Stow_2.wav](SFX/Stow_2.wav) | 0.490 | -4.93 | -4.92 | -23.80 | 0.000 |
| [SFX/Moor_0.wav](SFX/Moor_0.wav) | 0.640 | -3.41 | -3.40 | -27.06 | 0.000 |
| [SFX/Moor_1.wav](SFX/Moor_1.wav) | 0.650 | -3.43 | -3.40 | -26.11 | 0.000 |
| [SFX/Moor_2.wav](SFX/Moor_2.wav) | 0.660 | -3.41 | -3.40 | -26.52 | 0.000 |
| [SFX/Sale_0.wav](SFX/Sale_0.wav) | 0.710 | -13.83 | -13.79 | -24.20 | 0.000 |
| [SFX/Sale_1.wav](SFX/Sale_1.wav) | 0.720 | -13.19 | -13.11 | -24.00 | 0.000 |
| [SFX/Sale_2.wav](SFX/Sale_2.wav) | 0.730 | -11.36 | -11.31 | -23.80 | 0.000 |
| [SFX/Select_0.wav](SFX/Select_0.wav) | 0.101 | -13.50 | -13.44 | -32.20 | 0.299 |
| [SFX/Select_1.wav](SFX/Select_1.wav) | 0.105 | -13.61 | -13.59 | -32.00 | 0.295 |
| [SFX/Select_2.wav](SFX/Select_2.wav) | 0.109 | -13.41 | -13.39 | -31.80 | 0.291 |
| [SFX/Purchase_0.wav](SFX/Purchase_0.wav) | 0.126 | -11.67 | -11.61 | -32.20 | 0.274 |
| [SFX/Purchase_1.wav](SFX/Purchase_1.wav) | 0.130 | -10.64 | -10.64 | -32.00 | 0.270 |
| [SFX/Purchase_2.wav](SFX/Purchase_2.wav) | 0.134 | -12.19 | -12.04 | -31.80 | 0.266 |
| [SFX/Gull_0.wav](SFX/Gull_0.wav) | 1.240 | -14.27 | -14.25 | -27.20 | 0.000 |
| [SFX/Gull_1.wav](SFX/Gull_1.wav) | 1.250 | -13.48 | -13.44 | -27.00 | 0.000 |
| [SFX/Gull_2.wav](SFX/Gull_2.wav) | 1.260 | -13.60 | -13.59 | -26.80 | 0.000 |
| [SFX/Bell_0.wav](SFX/Bell_0.wav) | 2.590 | -11.35 | -11.34 | -27.20 | 0.000 |
| [SFX/Bell_1.wav](SFX/Bell_1.wav) | 2.600 | -10.65 | -10.65 | -27.00 | 0.000 |
| [SFX/Bell_2.wav](SFX/Bell_2.wav) | 2.610 | -9.59 | -9.57 | -26.80 | 0.000 |
| [SFX/Creak_0.wav](SFX/Creak_0.wav) | 0.640 | -6.66 | -6.65 | -24.20 | 0.000 |
| [SFX/Creak_1.wav](SFX/Creak_1.wav) | 0.650 | -5.91 | -5.84 | -24.00 | 0.000 |
| [SFX/Creak_2.wav](SFX/Creak_2.wav) | 0.660 | -5.93 | -5.84 | -23.80 | 0.000 |
| [SFX/Horn_0.wav](SFX/Horn_0.wav) | 2.690 | -20.17 | -20.16 | -27.20 | 0.000 |
| [SFX/Horn_1.wav](SFX/Horn_1.wav) | 2.700 | -19.81 | -19.81 | -27.00 | 0.000 |
| [SFX/Horn_2.wav](SFX/Horn_2.wav) | 2.710 | -19.72 | -19.71 | -26.80 | 0.000 |
| [SFX/Click_0.wav](SFX/Click_0.wav) | 0.086 | -11.75 | -11.74 | -32.20 | 0.314 |
| [SFX/Click_1.wav](SFX/Click_1.wav) | 0.090 | -13.50 | -13.49 | -32.00 | 0.310 |
| [SFX/Click_2.wav](SFX/Click_2.wav) | 0.094 | -12.47 | -12.46 | -31.80 | 0.306 |
| [SFX/Winch_0.wav](SFX/Winch_0.wav) | 0.380 | -8.66 | -8.66 | -24.20 | 0.020 |
| [SFX/Winch_1.wav](SFX/Winch_1.wav) | 0.390 | -8.35 | -8.33 | -24.00 | 0.010 |
| [SFX/Winch_2.wav](SFX/Winch_2.wav) | 0.400 | -6.98 | -6.98 | -23.80 | 0.000 |
| [SFX/CrabClack_0.wav](SFX/CrabClack_0.wav) | 0.330 | -6.91 | -6.91 | -24.20 | 0.070 |
| [SFX/CrabClack_1.wav](SFX/CrabClack_1.wav) | 0.340 | -6.31 | -6.28 | -24.00 | 0.060 |
| [SFX/CrabClack_2.wav](SFX/CrabClack_2.wav) | 0.350 | -6.51 | -6.42 | -23.80 | 0.050 |
| [SFX/SealBark_0.wav](SFX/SealBark_0.wav) | 0.840 | -10.39 | -10.38 | -27.20 | 0.000 |
| [SFX/SealBark_1.wav](SFX/SealBark_1.wav) | 0.850 | -9.74 | -9.73 | -27.00 | 0.000 |
| [SFX/SealBark_2.wav](SFX/SealBark_2.wav) | 0.860 | -10.17 | -10.16 | -26.80 | 0.000 |
| [SFX/NetSlap_0.wav](SFX/NetSlap_0.wav) | 0.670 | -3.41 | -3.40 | -24.41 | 0.000 |
| [SFX/NetSlap_1.wav](SFX/NetSlap_1.wav) | 0.680 | -5.72 | -5.71 | -24.00 | 0.000 |
| [SFX/NetSlap_2.wav](SFX/NetSlap_2.wav) | 0.690 | -4.38 | -4.38 | -23.80 | 0.000 |
| [SFX/Gut_0.wav](SFX/Gut_0.wav) | 0.420 | -11.74 | -11.68 | -24.20 | 0.000 |
| [SFX/Gut_1.wav](SFX/Gut_1.wav) | 0.430 | -11.56 | -11.50 | -24.00 | 0.000 |
| [SFX/Gut_2.wav](SFX/Gut_2.wav) | 0.440 | -11.80 | -11.79 | -23.80 | 0.000 |
| [SFX/Coins_0.wav](SFX/Coins_0.wav) | 0.790 | -12.41 | -12.41 | -24.20 | 0.000 |
| [SFX/Coins_1.wav](SFX/Coins_1.wav) | 0.800 | -11.68 | -11.67 | -24.00 | 0.000 |
| [SFX/Coins_2.wav](SFX/Coins_2.wav) | 0.810 | -11.65 | -11.53 | -23.80 | 0.000 |
| [Ambience/HarbourDay.wav](Ambience/HarbourDay.wav) | 30.000 | -14.26 | -14.21 | -28.00 | 0.000 |
| [Ambience/OpenSea.wav](Ambience/OpenSea.wav) | 30.000 | -13.84 | -13.83 | -28.00 | 0.000 |
| [Ambience/Skerries.wav](Ambience/Skerries.wav) | 30.000 | -13.43 | -13.42 | -28.00 | 0.000 |

## Reproduction and remaining acceptance

Scripts: [dsp.py](../Source/Audio/dsp.py), [build.py](../Source/Audio/build.py), [analyze.py](../Source/Audio/analyze.py), [verify.py](../Source/Audio/verify.py), [run.py](../Source/Audio/run.py), [finalize.py](../Source/Audio/finalize.py). From project root, using an existing Python environment with numpy/scipy (and Pillow for plots):

```sh
/home/mo/.venvs/catchline-ui/bin/python Art/Source/Audio/run.py build analyze verify
```

This regenerates the pack and analysis. Individually open all final sheets before running finalize.py again; it binds that review to hashes. Seeds are stable in dsp.py. Package versions are recorded in verification.json; no dependency installation was performed.

Claude’s remaining acceptance: copy/import uncompressed source WAVs as appropriate, wire Skerries ambience when the runtime supports that location, listen through ear-proxy review for timbre, repetition, scene balance and loop joins, and check fast taps in the real mixer. Current read-only VoyageAudio.cs already discovers SFXvariants0–4and HarbourDay/OpenSea beds; Skerries is supplied for the lead’s integration. No Unity/Assets/runtime/save/watchdog or git changes were made.

---

## SOUND-2 — harbour dusk, Lighthouse Rock and new activity sounds

Codex 2 (WSL CLI),2026-10-25. **Artist delivery complete by analysis:**18mono cues (6families ×3variants),2stereo30s loops. All20final per-file waveform/spectrogram sheets individually opened; no listening or Unity/native acceptance claimed. Claude owns copy/import, timbre, repetition and final mixer judgement.

### Contract and integration

All files are uncompressed RIFF WAVE,44,100Hz,signed16-bit little-endian PCM. Cue file names are `<Cue>_0.wav` through `_2.wav`; choose one per event. DogBark=.250s,Meow=.400s,Stitch=.200s,PotDrop=.800s; Puffin=.660/.720/.780s,Foghorn=2.900/3.000/3.100s. No downloaded audio, recordings, external samples, TTS or network generation: original deterministic numpy/scipy synthesis using unchanged SOUND-1 primitives. Pillow is for evidence images only. These are physically inspired approximations.

Copy the18new cues to `Assets/Resources/Audio/SFX/` and the two beds to `Assets/Resources/Audio/Ambience/` when integrating; this task wrote no Assets or runtime files. Explicitly route new families and dusk/spot beds as appropriate. Treat Foghorn as a rare separate quiet cue; it is absent from LighthouseRock. Both loops are exactly1,323,000frames/channel: enable looping without extra silence, preserve sample counts and judge compression/import joins in the real player. One-shots have7ms tapers and zero first/last PCM samples.

Dusk is2LU quieter than delivered HarbourDay (-30versus-28LUFS), with darker water/wind filters, two far gulls and exactly one church bell onset at20.1s (6.1s decay). No crickets. LighthouseRock has broader rock surf/open wind and five faint puffin calls; one surf wash wraps through the30s seam. Both retain live audio at the join. The8ms smooth endpoint bridge on each side gives identical endpoint values and zero slope steps; native perception of that short bridge remains part of ear acceptance.

### Recipes

| Family | Duration,s | Measured LUFS | Recipe |
|---|---:|---:|---|
| Puffin | 0.660–0.780 | -28.20–-27.80 | One low purring growl-call: rough low harmonic throat, fluttering pressure, narrow breath and soft terminal exhale. |
| Foghorn | 2.900–3.100 | -32.20–-31.80 | One distant low diaphone-inspired blast: 52Hz pulsed pressure, a soft falling release, dark delayed reflections and diffuse tail; quiet. |
| DogBark | 0.250–0.250 | -27.20–-26.80 | One friendly small-dog bark: fast rounded onset, descending rough glottal pulse, broad mouth resonances and short breath decay. |
| Meow | 0.400–0.400 | -27.20–-26.80 | Short ginger-cat meow: softly swept glottal harmonics, moving nasal/mouth resonances, breath and a tapered closing vowel. |
| Stitch | 0.200–0.200 | -29.20–-28.80 | Twine pull through a net mesh: smooth pressure-shaped fibre noise, irregular stick-slip grains and a soft final knot touch. |
| PotDrop | 0.800–0.800 | -25.20–-24.80 | One pot over the rail: low wooden thump, rope friction, delayed displaced-water splash and small buoy/bubble settling. |
| HarbourDusk | 30.000 stereo | -30.00 | Warmer, quieter periodic piling laps than HarbourDay, sparse distant gulls and rope, one low church bell stroke at20.1s; no crickets. |
| LighthouseRock | 30.000 stereo | -28.00 | Slow open swell, broken surf washes against rock, soft wind and a distant scattered puffin colony; no foghorn. |

### Actual decoded readings and individually opened sheets

Each linked sheet belongs to its single delivered file. SFX rows show one waveform and absolute-level log-frequency spectrogram; loop sheets show both channels plus a±20ms seam zoom. Spectrogram range80Hz–16kHz,−100to−15dBFS; Foghorn’s~50Hz fundamental is below that plot range, independently confirmed in the decoded spectral check. Seam-row LUFS/peak is the full parent loop;40ms labels its zoom.

| WAV | Opened sheet | Seconds | Sample peak,dBFS | Est.true peak,dBTP | LUFS | Zero pad,s |
|---|---|---:|---:|---:|---:|---:|
| [Puffin_0](SFX/Puffin_0.wav) | [wave + spectrum](review/SOUND2-Puffin_0.png) | 0.660 | -16.26 | -16.25 | -28.20 | 0.000 |
| [Puffin_1](SFX/Puffin_1.wav) | [wave + spectrum](review/SOUND2-Puffin_1.png) | 0.720 | -16.52 | -16.51 | -28.00 | 0.000 |
| [Puffin_2](SFX/Puffin_2.wav) | [wave + spectrum](review/SOUND2-Puffin_2.png) | 0.780 | -16.43 | -16.42 | -27.80 | 0.000 |
| [Foghorn_0](SFX/Foghorn_0.wav) | [wave + spectrum](review/SOUND2-Foghorn_0.png) | 2.900 | -22.59 | -22.59 | -32.20 | 0.000 |
| [Foghorn_1](SFX/Foghorn_1.wav) | [wave + spectrum](review/SOUND2-Foghorn_1.png) | 3.000 | -21.57 | -21.56 | -32.00 | 0.000 |
| [Foghorn_2](SFX/Foghorn_2.wav) | [wave + spectrum](review/SOUND2-Foghorn_2.png) | 3.100 | -22.22 | -22.21 | -31.80 | 0.000 |
| [DogBark_0](SFX/DogBark_0.wav) | [wave + spectrum](review/SOUND2-DogBark_0.png) | 0.250 | -8.98 | -8.92 | -27.20 | 0.150 |
| [DogBark_1](SFX/DogBark_1.wav) | [wave + spectrum](review/SOUND2-DogBark_1.png) | 0.250 | -8.19 | -8.18 | -27.00 | 0.150 |
| [DogBark_2](SFX/DogBark_2.wav) | [wave + spectrum](review/SOUND2-DogBark_2.png) | 0.250 | -6.60 | -6.56 | -26.80 | 0.150 |
| [Meow_0](SFX/Meow_0.wav) | [wave + spectrum](review/SOUND2-Meow_0.png) | 0.400 | -16.86 | -16.86 | -27.20 | 0.000 |
| [Meow_1](SFX/Meow_1.wav) | [wave + spectrum](review/SOUND2-Meow_1.png) | 0.400 | -16.82 | -16.82 | -27.00 | 0.000 |
| [Meow_2](SFX/Meow_2.wav) | [wave + spectrum](review/SOUND2-Meow_2.png) | 0.400 | -16.81 | -16.80 | -26.80 | 0.000 |
| [Stitch_0](SFX/Stitch_0.wav) | [wave + spectrum](review/SOUND2-Stitch_0.png) | 0.200 | -13.39 | -13.28 | -29.20 | 0.200 |
| [Stitch_1](SFX/Stitch_1.wav) | [wave + spectrum](review/SOUND2-Stitch_1.png) | 0.200 | -14.00 | -13.84 | -29.00 | 0.200 |
| [Stitch_2](SFX/Stitch_2.wav) | [wave + spectrum](review/SOUND2-Stitch_2.png) | 0.200 | -13.63 | -13.58 | -28.80 | 0.200 |
| [PotDrop_0](SFX/PotDrop_0.wav) | [wave + spectrum](review/SOUND2-PotDrop_0.png) | 0.800 | -8.59 | -8.58 | -25.20 | 0.000 |
| [PotDrop_1](SFX/PotDrop_1.wav) | [wave + spectrum](review/SOUND2-PotDrop_1.png) | 0.800 | -8.60 | -8.57 | -25.00 | 0.000 |
| [PotDrop_2](SFX/PotDrop_2.wav) | [wave + spectrum](review/SOUND2-PotDrop_2.png) | 0.800 | -8.93 | -8.87 | -24.80 | 0.000 |
| [HarbourDusk](Ambience/HarbourDusk.wav) | [wave + spectrum](review/SOUND2-HarbourDusk.png) | 30.000 | -16.18 | -16.17 | -30.00 | 0.000 |
| [LighthouseRock](Ambience/LighthouseRock.wav) | [wave + spectrum](review/SOUND2-LighthouseRock.png) | 30.000 | -14.63 | -14.62 | -28.00 | 0.000 |

[SOUND-2 metrics](metrics-sound2.json) records each file’s duration,format,frames,LUFS/padding,sample+4×estimated true peak,DC,RMS,endpoints,stereo correlation,seam value/slope and SHA256. The same data is added under `sound2` in [aggregate metrics](metrics.json); all original SOUND-1 keys/66rows retain their original semantic contents. [Synthesis inventory/event schedule](synthesis-sound2.json), [independent verification](verification-sound2.json), [actual individual review record](visual-review-sound2.json), [final receipt](delivery-receipt-sound2.json).

LUFS uses the unchanged SOUND-1 BS.1770 K-weighting/gated400ms meter. DogBark and Stitch are zero-padded to400ms solely for measurement (150/200ms padding); these are padded energy readings. Known1kHz−20dBFSpeak test remains~−23mono/~−20stereo LUFS. Estimated true peak uses4×polyphase interpolation and is not a certified meter.

Results:

- Highest sample peak **-6.601dBFS**; highest4×estimate **-6.556dBTP**, below−3.
- Maximum cue-family loudness spread **0.400LU**, below2; three unique PCM hashes per family.
- Maximum absolute DC **0.00002501FS**, below0.0007; all one-shot endpoints0 and adjacent samples within3PCMsteps.
- Independent exact86WAV inventory:66unchanged SOUND-1 +20SOUND-2.103original nonaggregate files retain exact size/SHA256. Original report’s15215-byte prefix unchanged. Both metadata exceptions are additive, as expressly requested by the brief.

| Loop | Seam value,L/R | Seam slope,L/R | Join/whole RMS,L/R | Stereo correlation |
|---|---|---|---|---:|
| HarbourDusk | [0.0, 0.0] | [0.0, 0.0] | 1.033, 1.050 | 0.690 |
| LighthouseRock | [0.0, 0.0] | [0.0, 0.0] | 0.907, 0.944 | 0.685 |

Stitch cyclic variant overlap at8/12/16Hz over2s has worst unity-gain peak -11.58dBFS; at0.65gain -15.32dBFS. This is a bounded stress case; still cap/review event rate and sum with music/water in the real mixer.

### Reproduction and receipt scope

New-only scripts: [dsp2.py](../Source/Audio/dsp2.py), [build2.py](../Source/Audio/build2.py), [analyze2.py](../Source/Audio/analyze2.py), [verify2.py](../Source/Audio/verify2.py), [run2.py](../Source/Audio/run2.py), [document2.py](../Source/Audio/document2.py), [finalize2.py](../Source/Audio/finalize2.py). [Protected original baseline](../Source/Audio/baseline2.json). Existing environment used; no installation.

```sh
/home/mo/.venvs/catchline-ui/bin/python -B Art/Source/Audio/run2.py build analyze verify
```

The historical SOUND-1 reproduction command above is superseded for this expanded directory: do not rerun its build/analyze/finalize scripts over the current pack; its exact66-file verifier is a historical inventory. New-only tooling reads unchanged old DSP/meter/plot primitives but writes only the20new WAVs and SOUND-2 evidence. If anything changes, open every affected final sheet again and explicitly replace its manual review record before document2.py/finalize2.py. The document script refuses stale review hashes.

The original SOUND-1 receipt is preserved byte for byte. Its hashes for the two expanded aggregates (REPORT.md/metrics.json) are historical; the new SOUND-2 receipt supersedes those two only and binds new files, review hashes and the protected baseline proof. All other original receipt members remain unchanged. Artist completion is analytical; remaining lead acceptance is listening for believable vocal timbre, far bell/horn distance, repetition, loop-bridge perception and final gameplay/rapid-stitch balance. No git/commit,Unity,Assets,save or watchdog changes were made.


---

## SOUND-4 — recorded CC0 tutorial, refit and harbour cues

Codex 2 (WSL CLI). **15 recording-based candidates technically verified; auditory acceptance remains incomplete.** Three variants each of CoachPop, RefitFanfare, TabTap, CoinBuy and PageTurn. Source ownership was limited to Art/Audio; no Assets, code outside Art/Audio, metas, Unity, saves, watchdog or git changes. Existing deliveries preserved.

The brief calls SOUND2 a real-recording pipeline, but the preceding SOUND-2 report explicitly describes original synthesis. This delivery uses the real SOUND-3/CREW-FX source/scan pipeline and SOUND-2 measurement primitives. Every contributing source is explicitly CC0; no BY/BY-SA/NC source, synthesized excitation, generated sound or pitch shifting is used.

All outputs are uncompressed mono RIFF WAV, signed16-bit PCM at44100Hz. Source files are decoded only after clean Defender receipt and original SHA256 checks; extracted members match the scanned ZIP byte for byte. New bell preview scanned before decode: exit0, found no threats. Prior retained originals reuse matching clean scan receipts; no redundant download or scan was claimed.

Processing: trim/crop and downmix/resample,45Hz high-pass/per-cut low-pass,12ms source fades,9ms final fades, DC correction, gain-only transient control, real-source layering and loudness normalization. Targets: CoachPop -32, RefitFanfare -27, TabTap -38, CoinBuy -24 and PageTurn -29LUFS, with ±0.2LU variants. Short-cue loudness uses zero padding to400ms solely for measurement, following SOUND2; these padded values are not whole-game mix acceptance. Peak estimate uses4x polyphase interpolation, not a certified true-peak meter.

### Per-file evidence

| Output | Recorded source(s), all CC0 | Duration,s | LUFS | 4x peak,dBTP | Review | Listening |
|---|---|---:|---:|---:|---|---|
| [CoachPop_0](Real/SFX/CoachPop_0.wav) | [rubberduck](https://opengameart.org/content/100-cc0-sfx) | 0.170 | -32.20 | -15.37 | [wave/spectrum](review/SOUND4-CoachPop.png) | NOT HEARD; pending |
| [CoachPop_1](Real/SFX/CoachPop_1.wav) | [rubberduck](https://opengameart.org/content/100-cc0-sfx) | 0.180 | -32.00 | -14.68 | [wave/spectrum](review/SOUND4-CoachPop.png) | NOT HEARD; pending |
| [CoachPop_2](Real/SFX/CoachPop_2.wav) | [rubberduck](https://opengameart.org/content/100-cc0-sfx) | 0.190 | -31.80 | -11.01 | [wave/spectrum](review/SOUND4-CoachPop.png) | NOT HEARD; pending |
| [RefitFanfare_0](Real/SFX/RefitFanfare_0.wav) | [Sojan](https://freesound.org/people/Sojan/sounds/353233/) + [Nachtbold](https://commons.wikimedia.org/wiki/File%3ABlümlisalp_Horn.ogg) | 2.180 | -27.20 | -10.18 | [wave/spectrum](review/SOUND4-RefitFanfare.png) | NOT HEARD; pending |
| [RefitFanfare_1](Real/SFX/RefitFanfare_1.wav) | [Sojan](https://freesound.org/people/Sojan/sounds/353233/) + [Nachtbold](https://commons.wikimedia.org/wiki/File%3ABlümlisalp_Horn.ogg) | 2.285 | -27.00 | -8.70 | [wave/spectrum](review/SOUND4-RefitFanfare.png) | NOT HEARD; pending |
| [RefitFanfare_2](Real/SFX/RefitFanfare_2.wav) | [Sojan](https://freesound.org/people/Sojan/sounds/353233/) + [Nachtbold](https://commons.wikimedia.org/wiki/File%3ABlümlisalp_Horn.ogg) | 2.390 | -26.80 | -10.09 | [wave/spectrum](review/SOUND4-RefitFanfare.png) | NOT HEARD; pending |
| [TabTap_0](Real/SFX/TabTap_0.wav) | [rubberduck](https://opengameart.org/content/100-cc0-sfx) | 0.075 | -38.20 | -18.97 | [wave/spectrum](review/SOUND4-TabTap.png) | NOT HEARD; pending |
| [TabTap_1](Real/SFX/TabTap_1.wav) | [rubberduck](https://opengameart.org/content/100-cc0-sfx) | 0.084 | -38.00 | -20.54 | [wave/spectrum](review/SOUND4-TabTap.png) | NOT HEARD; pending |
| [TabTap_2](Real/SFX/TabTap_2.wav) | [rubberduck](https://opengameart.org/content/100-cc0-sfx) | 0.093 | -37.80 | -16.39 | [wave/spectrum](review/SOUND4-TabTap.png) | NOT HEARD; pending |
| [CoinBuy_0](Real/SFX/CoinBuy_0.wav) | [syncopika](https://opengameart.org/content/coin-sounds) | 0.440 | -24.20 | -3.60 | [wave/spectrum](review/SOUND4-CoinBuy.png) | NOT HEARD; pending |
| [CoinBuy_1](Real/SFX/CoinBuy_1.wav) | [syncopika](https://opengameart.org/content/coin-sounds) | 0.455 | -24.00 | -7.08 | [wave/spectrum](review/SOUND4-CoinBuy.png) | NOT HEARD; pending |
| [CoinBuy_2](Real/SFX/CoinBuy_2.wav) | [syncopika](https://opengameart.org/content/coin-sounds) | 0.470 | -23.80 | -3.79 | [wave/spectrum](review/SOUND4-CoinBuy.png) | NOT HEARD; pending |
| [PageTurn_0](Real/SFX/PageTurn_0.wav) | [rubberduck](https://opengameart.org/content/100-cc0-sfx) | 0.421 | -29.20 | -9.31 | [wave/spectrum](review/SOUND4-PageTurn.png) | NOT HEARD; pending |
| [PageTurn_1](Real/SFX/PageTurn_1.wav) | [rubberduck](https://opengameart.org/content/100-cc0-sfx) | 0.548 | -29.00 | -11.80 | [wave/spectrum](review/SOUND4-PageTurn.png) | NOT HEARD; pending |
| [PageTurn_2](Real/SFX/PageTurn_2.wav) | [rubberduck](https://opengameart.org/content/100-cc0-sfx) | 0.537 | -28.80 | -13.93 | [wave/spectrum](review/SOUND4-PageTurn.png) | NOT HEARD; pending |

### Source licence and scan ledger

| Recording/archive | Author / licence | Source / download | Scan evidence |
|---|---|---|---|
| [100-CC0-SFX_0.zip](Downloads/oga-100-cc0-sfx/100-CC0-SFX_0.zip) | rubberduck / [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | [source](https://opengameart.org/content/100-cc0-sfx) / [download](https://opengameart.org/sites/default/files/100-CC0-SFX_0.zip) | exit0, found no threats; [full receipt](Real/sources/100-cc0-sfx--100-CC0-SFX_0.zip.scan.json) |
| [coinsounds011015.wav](Downloads/oga-coin-sounds/coinsounds011015.wav) | syncopika / [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | [source](https://opengameart.org/content/coin-sounds) / [download](https://opengameart.org/sites/default/files/coinsounds011015.wav) | exit0, found no threats; [full receipt](Real/sources/coin-sounds--coinsounds011015.wav.scan.json) |
| [ShipHornClean.ogg](Real/sources/crewfx/ShipHornClean.ogg) | Nachtbold / [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | [source](https://commons.wikimedia.org/wiki/File%3ABlümlisalp_Horn.ogg) / [download](https://upload.wikimedia.org/wikipedia/commons/2/28/Bl%C3%BCmlisalp_Horn.ogg?utm_source=commons.wikimedia.org&utm_campaign=index&utm_content=original) | exit0, found no threats; [full receipt](Real/sources/crewfx/ShipHornClean.scan.json) |
| [ShipBell-preview.mp3](Real/sources/sound4/ShipBell-preview.mp3) | Sojan / [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) | [source](https://freesound.org/people/Sojan/sounds/353233/) / [download](https://cdn.freesound.org/previews/353/353233_5477651-hq.mp3) | exit0, found no threats; [full receipt](Real/sources/sound4/ShipBell.scan.json) |

Source limitations: Sojan’s **Ship Bell Single Ring** is a publicly offered HQ MP3 preview (44.1k mono decoded), not the login-gated original WAV. It is openly linked by the source page; no authentication workaround. Lossy encoding remains in the input. Nachtbold’s **Blümlisalp Horn** is a real steamboat, shortened to a faded toot for the celebration; the full natural recording remains in the accepted prior pack. Three refit variants reuse the same bell and horn takes with different lengths/timing. Other families use three distinct recorded wood/paper takes or distinct coin-montage passages; variant names do not imply new recording sessions.

### Review and limits

**What I heard: no claim — I could not listen in this session.** Available tools expose images and technical audio decoding, with no audio perception capability. All fifteen file rows therefore explicitly remain NOT HEARD. The requested per-file listening check, believable material/timbre, gentle/cartoon-free character, coin distinction by ear and native mix acceptance remain pending with Claude/Mo. [Playback controls for all fifteen cues](Real/sound4-listening.html) are ready. This is a technical delivery, not full SOUND-4 DONE acceptance.

- **CoachPop, visual inspection only:** Compact low/mid-heavy wood onset, paper component visible, decaying tail and faded endpoints; three distinct shapes. Gentleness and non-cartoon character need audition.
- **RefitFanfare, visual inspection only:** Two distinct bell attack columns at0 and about0.4s; lower sustained horn band starts around1.1s and fades under bell tail. Same source strike reused; bell/horn scale and cropped horn release need audition.
- **TabTap, visual inspection only:** Small low-frequency contacts at a lower measured level/peak than all existing Click variants. All three shorter than0.1s. Apparent quietness and repeated-tab comfort need audition.
- **CoinBuy, visual inspection only:** Two separated groups of metal transients, with a brief inter-event gap and second drop/rattle; all below0.5s. Variants0/2 approach the allowed peak ceiling but remain below-3dBTP; ear comparison with Coins remains pending.
- **PageTurn, visual inspection only:** Three different broadband paper movements with event lengths0.42–0.55s, no flat digital clipping; first is more impulsive, third quieter in peak. Actual unfold/chart timbre and source background need audition.

Independent verification:15/15 format, duration, peak<=-3dBFS, DC<0.0007FS, zero endpoints and adjacent samples<=3PCMsteps, target deviation<1LU, variant loudness spread0.4LU and distinct SHA256 PASS. TabTap is at least3LU quieter and has lower sample peak than every Click in both existing recorded and synthetic packs. [Metrics and comparison evidence](Real/sound4-metrics.json).

Preservation:711 pre-existing audio files were checked byte for byte before this append. The original REPORT prefix remains unchanged; its historical SOUND2 receipt report hash is superseded only by this additive report update. The SOUND4 receipt binds new candidates/evidence; historical receipts are retained unchanged.

### Reproduction and pickup

Use `/home/mo/.venvs/catchline-ui/bin/python -B Art/Audio/Real/tools/acquire_sound4.py`, then `build_sound4.py`, then `check_sound4.py` (same interpreter and tools directory, from project root). Acquisition reuses a matching clean retained receipt. Build refuses existing SOUND4 manifest or cue files; an intentional revision must remove only its own manifest/cues before rebuilding. Checker can be repeated without touching WAVs and validates the preserved REPORT prefix. [Exact source cuts/layers](Real/sound4-edits.json), [opened-sheet observations/hashes](Real/sound4-review.json), [receipt](delivery-receipt-sound4.json). Source files outside Art/Audio are imported read-only for DSP/meter helpers.

Next: listen to every named variant, record actual heard observations, refine any source crop/timbre needed, remeasure/reopen affected evidence, then integrate and judge mixer behaviour. No remaining construction or technical-verification step is known; listening is the unmet brief requirement.



## SOUND-5 — first catch, sale and savings (Codex 2, technical delivery)

15 recording-based CC0 one-shots: three variants each of FishLeap, NewSpecies, StampThud, CoinLand and GoalReady. **NOT HEARD.** Listening and native mix acceptance belong to Mo. Technical delivery is complete; waveform inspection is not listening. No Assets, scripts, metas, Unity or game wiring changed.

[Playback and 14-coin repeat diagnostic](Real/sound5-listening.html) · [Independent measurements](Real/sound5-metrics.json) · [Edit/source ledger](Real/sound5-edits.json) · [Delivery receipt](delivery-receipt-sound5.json).

### Per-file sources and measured levels

All exports are mono 44,100 Hz, 16-bit PCM WAV. Loudness uses BS.1770 K-weighted/gated 400ms windows with zero padding for shorter files; short-event LUFS is a comparison convention, not a listening verdict. Peaks use 4x polyphase true-peak estimation, not a certified meter.

| File | Duration (s) | LUFS | Estimated dBTP | Recorded source URL(s), all CC0 |
|---|---:|---:|---:|---|
| [FishLeap_0.wav](Real/SFX/FishLeap_0.wav) | 0.580 | -25.20 | -8.33 | [1](https://opengameart.org/content/100-cc0-sfx) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [FishLeap_1.wav](Real/SFX/FishLeap_1.wav) | 0.635 | -25.00 | -4.97 | [1](https://opengameart.org/content/100-cc0-sfx) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [FishLeap_2.wav](Real/SFX/FishLeap_2.wav) | 0.690 | -24.80 | -3.79 | [1](https://opengameart.org/content/water-splash-and-sand-footsteps) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [NewSpecies_0.wav](Real/SFX/NewSpecies_0.wav) | 1.410 | -29.00 | -16.42 | [1](https://versilian-studios.com/vcsl/) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [NewSpecies_1.wav](Real/SFX/NewSpecies_1.wav) | 1.480 | -28.90 | -15.34 | [1](https://versilian-studios.com/vcsl/) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [NewSpecies_2.wav](Real/SFX/NewSpecies_2.wav) | 1.550 | -28.80 | -14.14 | [1](https://versilian-studios.com/vcsl/) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [StampThud_0.wav](Real/SFX/StampThud_0.wav) | 0.184 | -32.00 | -8.14 | [1](https://freesound.org/people/kermite607/sounds/362624/) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [StampThud_1.wav](Real/SFX/StampThud_1.wav) | 0.205 | -31.90 | -8.10 | [1](https://freesound.org/people/kermite607/sounds/362624/) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [StampThud_2.wav](Real/SFX/StampThud_2.wav) | 0.222 | -31.80 | -7.89 | [1](https://freesound.org/people/kermite607/sounds/362624/) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [CoinLand_0.wav](Real/SFX/CoinLand_0.wav) | 0.145 | -36.00 | -13.77 | [1](https://opengameart.org/content/coin-sounds) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [CoinLand_1.wav](Real/SFX/CoinLand_1.wav) | 0.160 | -35.90 | -8.50 | [1](https://opengameart.org/content/coin-sounds) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [CoinLand_2.wav](Real/SFX/CoinLand_2.wav) | 0.175 | -35.80 | -9.33 | [1](https://opengameart.org/content/coin-sounds) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [GoalReady_0.wav](Real/SFX/GoalReady_0.wav) | 0.830 | -32.00 | -20.24 | [1](https://versilian-studios.com/vcsl/) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [GoalReady_1.wav](Real/SFX/GoalReady_1.wav) | 0.885 | -31.90 | -20.09 | [1](https://versilian-studios.com/vcsl/) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| [GoalReady_2.wav](Real/SFX/GoalReady_2.wav) | 0.930 | -31.80 | -19.50 | [1](https://versilian-studios.com/vcsl/) — [CC0-1.0](https://creativecommons.org/publicdomain/zero/1.0/) |

### Recording provenance and honest variant limits

- **FishLeap:** Actual water splash with a quieter offset water slap for the fish-flip accent; water Foley, no animal/synthesized excitation.
- **NewSpecies:** Three rising real soft glockenspiel strikes G4-C5-G5 (VCSL CC0); original recorded pitches, timing/gain/fade variants reuse same three strikes; no synthesis.
- **StampThud:** Actual rubber stamp hitting paper, kermite607 CC0; three crop/EQ/fade edits of ONE recorded strike from public HQ MP3 preview (not three takes).
- **CoinLand:** Single isolated metal coin contact from syncopika recorded coin collection; cropped before subsequent contact, short damped tail, soft target for repeated landings. No jar material claimed.
- **GoalReady:** Two real soft glockenspiel strikes G4-C5; original recorded pitches, short overlapping decays; same two VCSL CC0 strikes reused with timing/fade/gain variation. Quieter than RefitFanfare.

FishLeap uses splash_01 and splash_02 from the existing 100-CC0-SFX archive and splash1_0 from Water Splash and Sand Footsteps; water Foley supplies the wet flip accent, with no real fish recording claimed. CoinLand uses three separate dominant contacts at source peaks recorded in the edit ledger; short bounce/contact detail may remain. No literal glass jar material is claimed. Audition whether these read as a small landing onto a pile in context.

VCSL glockenspiel soft G4, C5 and G5 lossless WAVs were acquired from the commit-pinned official GitHub repository. [Official VCSL page](https://versilian-studios.com/vcsl/) and [repository README](Real/sources/sound5/VCSL-README.md) state CC0. Retained page/tree, source bytes, SHA256 and Defender scan receipts are in [new source index](Real/sources/sound5/index.json). No pitch shifting or synthesized instrument/excitation was used.

StampThud is [kermite607’s rubber-stamp-on-paper recording](https://freesound.org/people/kermite607/sounds/362624/), CC0. Only the publicly offered HQ MP3 preview was available without login; the lossy preview is retained and explicitly identified. Three edits reuse ONE take, with slightly different crop/EQ/fade/gain. It is not three distinct recorded stamps.

All four new audio downloads passed Windows Defender before any decode. Existing recordings were reused only after clean receipt/hash verification, and archive-member byte equality where applicable. New index stores exact download URLs, pinned commit for glock samples, scan commands/output/status and SHA256. Per-layer source/original hashes, source pages, authors, CC0 links, crops, timing, gains, filters and fades are in sound5-edits.json.

### Technical and review evidence

- All15 independently decoded: requested durations, mono44100 PCM16, sample/estimated true peaks <= -3 dB, DC < .0007, zero endpoints and adjacent endpoint samples <=3 PCM units. Targets met within1LU; actual within-family spread <=.4LU.
- GoalReady is at least4.60LU below RefitFanfare; CoinLand at least11.60LU below CoinBuy. Distinct output hashes are edit variants, not proof of different recordings.
- [14-contact diagnostic](Real/review/SOUND5-CoinLand-14-hit-preview.wav) rotates CoinLand variants at80ms spacing, unity gain, no normalization; measured estimated peak -8.56dBTP. Diagnostic timing is not a claim about runtime scheduling, comfort or auditory acceptance.
- Five waveform/log-spectrum PNGs were opened: broadband water transients, staged three/two glock attacks with fading tails, short dominant stamp impact and brief coin contacts. Plots cannot establish realism, warmth or fatigue.

- [SOUND5-FishLeap.png](review/SOUND5-FishLeap.png)
- [SOUND5-NewSpecies.png](review/SOUND5-NewSpecies.png)
- [SOUND5-StampThud.png](review/SOUND5-StampThud.png)
- [SOUND5-CoinLand.png](review/SOUND5-CoinLand.png)
- [SOUND5-GoalReady.png](review/SOUND5-GoalReady.png)

All745 pre-existing Art/Audio files matched the pre-task baseline before this append; REPORT.md retains its original byte prefix. No prior audio delivery was rebuilt. Source construction is complete. Mo’s outstanding listening check: wet-flip clarity, bell warmth, stamp material, coin fatigue across14 repeats, and goal cue balance in game. **NOT HEARD.**
