# Clear prep orders and stable net crews — PREP047

Mo's 17 October feedback supersedes BALANCE045's weight/value filter controls.

The prep table now has two clearly separated sections:

- **Chum settings**, on the left: turn selected fish into bait, choose how much
  chum to keep ready, and see current/being-made stock. Those fish leave the hold.
- **Fish preparation**, on the right: choose fish to prepare and process oldest
  or most valuable first. Fish stay in the hold, earn the existing25% premium and
  stop spoiling at their existing quality. No freshness restoration was added.

Each **Fish to chum** / **Fish to prepare** button opens an independent dropdown.
Tap any class to include/exclude it; multiple classes may be selected. Both lists
use Common (white), Big common (green), Rare (blue), Big rare (purple), Legendary
(gold), Big legendary (red), in that order. All-off pauses that type of work.
These selections drive actual worker and captain eligibility and are saved.
Existing class assignments, species IDs and saved enum values stay intact; the
red internal `Mythical` enum now displays the requested Big legendary name.

Legacy saves migrate to Common-only chum and all-class preparation. Obsolete
weight/value fields remain load-compatible but no longer gate either operation.
The established weight-scaled chum yield, target reservations, work pace, two-hand
limit, one-time purple/gold/red by-product and full-hold captain game remain.
Priority still selects which kind of work to do first when both are available.
Worker assignments belong in **Crew duties**, with no worker controls in the table.

**Prep table / chum** now sits on the right below Head home and Crew duties.
The bottom-left catch list remains clear.

Net repair:

- Net2 drops and settles its catch at a basket beside its own access point,
  instead of using net1's pickup tile and basket.
- Net catches use one gather/carry/stow cycle per basket. Other hands cannot
  claim individual fish from that batch. Each fish still respects exact cargo
  capacity, including the existing one-whole-fish overflow rule.
- Nets deckhands keep distinct rig assignments through setting, soaking,
  hauling and unloading. Ready work at the other rig cannot cause switching.
  Changing duties or crew releases ownership. During soak they retain the
  previously approved rod/bait fallback, preempted only by their own ready net.
- Crew duties identifies each assigned net; the unloading caption appears on
  the actual net being unloaded.

Verification receipts and native desktop1440x900/landscape844x390 images are in
`docs/screens/prep047/`. Final check/build/install status is in `comms.md`.
These are scripted native captures and actual behavior checks, not physical
phone touch or Mo's play acceptance. No real save is used by the fixtures.

## Codex 3 completion — 2026-10-17

The prep order and active prep-worker count now appear in **Crew duties**. The
prep table keeps only fish-processing choices and the prepared-fish count.
The Codex 3 follow-up also caps rod bite waits at 15 seconds, including when a
fishing ground is depleted; shorter waits and the first-trip tutorial remain
unchanged. `docs/screens/prep047/codex3-source-verification.json` records that
all six changed source/check files matched the tested scratch project for that
release. The `prep047-codex3-fast-bites` build was installed at
`C:/Users/momoy/Projects/Catchline-play/Tier033`; its 174-file hash receipt is
`docs/screens/prep047/installed-build.json`. The existing Tier 4 Test shortcut
still targets that install with its original arguments. Desktop and landscape
captures were regenerated and inspected. Physical touch and Mo's in-game
acceptance remain unclaimed.

## Codex 3 net stat update — 2026-10-17

The follow-up doubles shallow/deep soak time to40/60 seconds and net weight
capacity across hull tiers: 20kg through Hull2 and30kg on Hull3, increased by
Heavy Net System to30/44kg. Both net rigs use the same settings. Net output,
hauling, crew behavior and prices are unchanged. `netstats-codex3-final` passes
the focused net/progression checks and is installed at the same Tier 4 Test path;
the refreshed 174-file install receipt is `docs/screens/prep047/installed-build.json`.
