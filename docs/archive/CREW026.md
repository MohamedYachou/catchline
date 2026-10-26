# CREW026 — Always-available contract hiring

Mo's clarified request: keep contract hiring temporary, but do not let a worker
type disappear from the Crew Office after the available candidate is hired.

## Rules

- Real and Test maintain the same role availability.
- The Crew Office always offers enough deckhand contracts and fisherman
  contracts to fill the current hull's full crew capacity. Hiring one candidate
  immediately replenishes that role with another candidate; board rolls, refits
  and loading older saves restore the full choices too.
- Tier3 supports three fishermen, three deckhands or any mix. The rowboat keeps
  its two existing hired berths; the captain remains additional.
- Hiring is still a temporary contract. Hands last2 voyages, experienced crew3
  and veterans5. Existing grade fees and the fisherman's2x fee remain unchanged;
  expired crew leave normally and must be hired again.
- Full crew does not remove the captain's own work.

## Test setup

The `Catchline - Tier 3 Test` desktop shortcut starts at the Crew Office with an
empty compact-fisher roster and1000 session-only coins. That allows three
veteran fishermen (900 coins) as well as cheaper mixes. Normal contract fees and
durations apply. The test has full fuel and the existing bait/net supplies; it
never reads or writes the Real save.

The previous at-sea setup remains available by launching the Test player with
`-deep-net-trial -native-display`. The Real shortcut continues normal title/load
and persistent saves; no test currency or crew is added to Real progression.

## Verification

`UrgentCrewChecks.Run` covers each hull and30 board seeds, all-fisher/
all-deckhand/mixed compositions, replacement offers after each hire, contract
timers through save/load and expiry, and actual Test Crew Office purchase
controls at desktop and phone sizes. `ProgressionLaunchChecks.ValidateAndBuild`
runs the integrated regression, water check, and separate Real/Test Windows
builds on `Catchline-sim`. The guarded Real standalone probe checks both role
lists under a temporary `net023-probe-*` save root; it does not target the
player's save.

Delivered builds and shortcuts are versioned under
`Catchline-play/Crew026/{Real,Test}`. Shortcut readback and installed-file hashes
are recorded in `Catchline-sim/Logs/crew026/shortcuts.json`; the full verification
and correction history is in `comms.md`.
