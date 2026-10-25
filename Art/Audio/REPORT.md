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
