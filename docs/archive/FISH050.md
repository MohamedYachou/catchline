# Four signature Big Common fish — FISH050

Mo approved yellowfin tuna, barracuda, mahi-mahi and monkfish on18October2026.
Each has an editable Blender source, authored FBX and transparent768×384portrait
rendered from that exact model. Existing25species, assets and saved IDs remain.

| Species | Saved ID | Class | Weight | Base coins/kg | Existing grounds |
|---|---|---|---|---|---|
| Yellowfin tuna |25|Big Common / green|3–10kg|14|Deep channel|
| Barracuda |26|Big Common / green|1.5–5kg|15|Kelp bank, Rocky point|
| Mahi-mahi |27|Big Common / green|2–7kg|16|Kelp bank, Rocky point|
| Monkfish |28|Big Common / green|1.5–6kg|16|Sandbar, Deep channel|

All four unlock with the Compact fisher (`Hull=2`). They stay Big Common at
every specimen size. Existing common fish still become Big Common at75%of
their maximum weight. Starter Harbour mouth catches are unchanged. Larger
specimen premiums, market/freshness/preparation, bait and contract rules apply
through the existing systems. Encounter weights and sizes are initial game
tuning rather than a claim about real species abundance or adult size limits.

Normal rods and deep nets can catch these species in their listed grounds.
Shallow nets retain the small-school species filter. Prep/chum class selectors
recognize the new catches as Big Common; the default Common-only chum choice
protects them. Existing saves expand their species arrays through the existing
migration and preserve old IDs/cargo/records.

## Art

Sources and export receipts: `Art/Models/Fish050/<Species>/`.
Runtime models: `Assets/gemini/Models/<Species>.fbx`.
Runtime portraits: `Assets/gemini/FishRenders/fish-<species>.png`.

- Tuna: navy/silver body, gold sickle fins,14yellow finlets, crescent tail.
- Barracuda: narrow body, projecting lower jaw,14fangs, separated dorsal fins.
- Mahi-mahi: square bull forehead, long dorsal sail, teal/gold body and blue spots.
- Monkfish: broad head/mouth,18teeth, raised eyes, lure, walking pectorals and tapering tail.

All use the existing named palette, natural black eyes, explicit Nose/TailEnd
heading markers and a separate Tail mesh. Monkfish lies belly-down; the other
three lie on their side through the existing deck model fitter.

Rebuild with the existing Blender5FBX compatibility setup:

```bash
PYTHONPATH=/tmp/catchline-fish043-env/lib/python3.14/site-packages \
  blender -b --python-use-system-env -t 4 --python Art/Source/build_fish050.py
/tmp/catchline-fish043-env/bin/python Art/Source/audit_fish050.py
```

The builder reuses Fish043 primitives/export validation without modifying the
existing generator. The environment supplies numpy for Blender's bundled FBX
addon and Pillow for the audit/contact sheet; no external model assets are used.

## Verification

Asset/source/FBX hashes, roundtrip geometry/materials, distinguishing features,
portrait alpha margins and installed copies passed. Review sheet:
`docs/screens/fish050/four-fish-contact.png`. Unity/game checks and the native desktop/landscape review also passed;
final delivery evidence is recorded below.

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File docs/tools/check.ps1 `
  -Name fish050 -Method Catchline.EditorTools.BigCommonFishChecks.ValidateAndBuild
```

This runs only in `Catchline-sim`. It checks IDs, tiers, model import/scale,
portraits, local normal-bait rolls, hull gating,25-slot save migration, prepared
cargo roundtrip, sales/records, prep eligibility and deep/shallow net membership.
It also runs FishContent, UI041, PREP047 and their adjacent regression suites
before building the save-isolated Tier033preview.


## Delivered and verified

- Full `fish050` isolated suite completed Unityexit0: FISH050, FishContent,
  UI041, PACE036, PREP035, TIER033, Compact Fisher, NET HAUL, MODULE042,
  BALANCE045, PREP047 and CREW046 passed.
- A capture-fixture-only adjustment uses the actual front-edge rod for clearer
  deck-model review. `fish050-visible` build-only completed Unityexit0 afterward;
  gameplay and assets did not change after the full regression.
- Final native player exited0 with TEST/no-save and capture-complete markers,
  no reported exceptions. Reviewed all8newcatchframes at1440×900and844×390,
  including actual deck mesh details and readable green catch cards. These
  are scripted native frames, not physical-phone or Mo play acceptance.
-233main/scratchsource/asset hashes match. The exact reviewed174-file build
  is installed at `Catchline-play/Tier033`; **Catchline - Tier 4 Test** retains
  its original `-prepboat-trial -native-display` shortcut arguments.
- Real-save contents match the pre-install fingerprint. Temporary source and
  installation backups were removed after verification. No commit or branch change.

Evidence: `docs/screens/fish050/asset-audit.json`, `check-summary.json`,
`source-verification.json`, `native-review.json`, `build-manifest.json`,
`installed-build.json`, `save-verification.json`, `rod-sample.csv`,
`four-fish-contact.png`, `native-four-1440.png`, `native-four-844.png`,
`native-deck-detail.png` and individual `catch-<Species>-<width>.png` frames.

The20,000normal-bait sample per ground produced0newfish at Harbour mouth,
1109at Kelp bank,907at Sandbar,1834at Rocky point and1944at Deep channel.
This verifies availability and relative frequency in the selected fixture;
long-term player economy/pacing remains open to normal play feedback.
