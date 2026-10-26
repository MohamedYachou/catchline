# Existing-slice polish — 16 October 2026

Owner: Windows Codex. Scope: existing fishing maps, Unity water, harbour travel,
fishing HUD and quiet tactile coastal sound. No gameplay/content expansion.
Read PRODUCT.md, DESIGN.md, TOMORROW.md and the latest comms entries.

## Implementation

- Harbour manoeuvres: slide clear sideways, turn to the selected ground's bearing,
  travel, then settle into the fishing frame. Return follows the opposite bearing,
  aligns parallel and slides into the berth. Rotations pivot about the hull centre.
  Smooth camera framing retains the wide quay during casting off and docking.
- Live water now uses the actual PTS/Boat Attack HLSL through the bounded
  `Catchline/PTS Water` adaptation. See PTS-WATER-NOW.md for WATER-005 and current
  evidence. Foam is forced off; rounded Gerstner displacement, blue slope lighting,
  restrained glints and original PTS absorption/refraction replace the previous
  coastal look. Clock-driven animation freezes with game pause. Main pipeline
  settings and packages remain unchanged. Latest acceptance is hidden camera
  rendering and native integration checks, not current player/HUD review.
- Fishing HUD: compact cream resource instruments and separate hold/haul/freshness
  panel, cream portrait crew strips, smaller cream-framed bite/cast panels,
  live captain/crew activity, and readable reward/carry controls. Landscape-phone
  layout uses 480 logical vertical pixels. Interactive actions get larger touch
  areas; fixed HUD honours Unity's safe area.
- Original procedural coastal sound bed and tactile cast/splash/bite/reel,
  landing/stow/mooring/sale foley. Sound slider persists in ordinary play;
  preview sound preferences stay in memory. Crew fishing remains quiet.

## Artist and preservation

Existing Ubuntu artist: 01a13eac-e066-72e2-b226-f7f85c5cf5d4. ART-011 closeout
796c485 includes retained actual Unity handedness checks and working-quay renders.
ART-012 assignment and review are in ART-012-BRIEF.md and ART-012-REVIEW.md.
Windows adds runtime hooks for GullKelpBank, GullSandbar, GullRockyPoint and
GullDeepChannel; artist owns their saved Blender sources/FBX/placement contracts.
Do not import unfinished drafts. ART-009 day boat is outside this slice.

Main had extensive dirty work before this pass, including urgent crew/sale fixes.
Keep it. PC_RPAsset.asset baseline SHA256:
08A9C221B335A0DBCA1B6967B7DE5C42B957C5F0D5E43DA9EDB36CA8FCE5966B.
URPProjectSettings.asset baseline SHA256:
C317FE22B9488785C0611F0642429922E5D324430D929BFFB41648130F30C218.
Real-save pre-review SHA256:
FF6C05B75F05FD2C864A60D24C7B806747F4714EECF8599B0DCF1EF70B618AC5.

## Verification in progress

Scratch FirstVoyageChecks.Regression passed in check-polish004-final.log, including
new CoastalPolishChecks for all five outbound/return bearings, quay clearance,
arrival state and imported positive-X harbour landmarks. Player build and first
desktop/844x390 capture batch passed; scripted full loop, crew cast/leave and
sale/settings screenshots are under docs/screens/polish-004. Early captures
precede the final optical/map corrections and are not the final reveal.

Early static-stage native sample: 60.3 fps mean at both1440x900 and844x390 on
RTX4080Laptop, worst19.1/20.2ms. Vsync-capped desktop sample, not mobile hardware
performance proof. Runtime reported one audio listener,48kHz output and playing
coastal ambience. Manual native mouse review opened title/harbour, departed and
cast; scripted checks exercise strike/catch/carry/stow/full/return/sale/upgrade.

Final maps, native captures, regression, save/settings hashes and preview location
will be recorded after the artist delivery is integrated. No Mo visual acceptance
is implied by either source checks or these captures.
