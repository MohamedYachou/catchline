> Superseded by [DASH082](DASH082.md): Mo approved the exact DASH1/DASH2 artwork and a real processing-before-main-hold pipeline. This document records the earlier intermediate implementation; its optional preparation-in-hold description is historical.

# Boat management — first working version

Mo's brief: make the fish-production chain understandable with numbers and bars,
show method-level income/output, and expose bottlenecks in green/orange/red.
Owner: Codex 2 (WSL CLI). Surface mode: Operate. Inherits the existing coastal
cream/navy art, Fredoka, sliced panels, safe-area Canvas and larger-text setting.

## Player path

At sea, choose **Fish flow** above the boat. **Fish flow** shows the
three work stages and shared storage; **Fishing** compares rods, nets and crab
traps. Switch between the last60seconds and last3minutes. The voyage continues
behind the screen. Close with X or Escape. Crew duties and Processing orders go
to the actual existing controls, with unsupported actions disabled on early boats.
The full overlay blocks boat actions and their keyboard shortcuts.

## What the screen means

- Catch aboard: actual successful rod landings, net hauls and trap recoveries.
  Fish still underwater in nets are not yet landed. The Fishing tab also shows
  real net state, waiting underwater kilograms, and trap readiness.
- Carry & store: successful deliveries into the hold, excluding trap direct
  delivery. Waiting kilograms include deck fish, net baskets, and fish currently
  being carried. Actual kg/min is separate from estimated working capacity.
- Prepare & keep: actual fish preparation completions. Eligible raw fish and
  prepared fish remain in the same shared hold. Preparation does not create
  storage space or a fictitious second carrying operation.
- Hold: actual cargo kilograms versus actual capacity, plus storedkg/min and
  approximate time to full at the current measured inflow. A whole fish may
  exceed the nominal capacity under the existing storage rule.

Method bars are teal and compare actual catch output on one shared scale. They
are not load indicators. Method coins/min estimates use raw catch value at landing,
before freshness, processing, market changes and contracts. They are not paid
income, profit or a promise about the eventual sale.

## Traffic-light rule

Green means incoming load is below80% of the capacity estimate. Orange means
80–100%; red means incoming load exceeds the estimate, a queue has no crew, or
storage blocks handling. Every color has a written state. Unknown capacity and
first15seconds are neutral **Measuring**, not green. A real blocked queue can
show red immediately. Hold colors use its actual fullness, with orange at80%.
A plain-language recommendation leads the screen and links to real decisions.

Carrying capacity is learned from at least3completed deliveries and5worker busy
seconds, including gather, walk and stow. The observed worker pace is multiplied
by potentially eligible deckhands. Duties, walking, captain help and shared jobs
make this an estimate; it is labeled shared crew pace, not guaranteed throughput.
Learning resets when crew, duties, hull or net layout changes. Processor capacity
uses eligible mean specimenkg, actual assigned worker speed and the existing
0.15+4.5+0.15second per-fish cycle. Shared chum jobs/table approach can lower
actual output. Rates and queues remain actual observations even when capacity
estimates are imperfect. This version observes the existing batch transport rules;
it does not implement the separately discussed kg-linked workload redesign.

## Technical behavior

FlowTelemetry is session-only, bounded to180seconds of events; voyage totals are
separate. Only fishing simulation time advances the window. Pause/capture freeze,
travel and harbour time do not dilute rates. During warmup, the denominator is
actual elapsed fishing time, with a1second minimum. New games and normal new
voyages reset it. Head-home automatic salvage is excluded from operating rates.
No new saved fields, RNG draws, crew cards, price rules or action timings.

Reports refresh twice per simulated second. Native retained UI shares the existing
Canvas and its vertical scroll. The landscape phone layout brings rate, queue,
status and bar into each compact stage; extra routing/hold detail remains scrollable.
No browser facsimile or Lighthouse result substitutes for the Unity frames.

## Verification

Verification results and final preview location are appended after the checks and
native review complete. Screens/logs live under docs/screens/management078.

## Review and scope limits

Native review used actual Windows player frames at1440×900 and844×390, including
Larger type, initial measuring, a real uncovered carrying job and a forced
full-hold scenario. The full-hold capture seeds cargo through actual accepted
storage calls; it is a UI-state fixture, not an economy/balance trace. Automated
callbacks verify control wiring; they are not a physical touch-device test.
The existing Unity Canvas has no screen-reader bridge; this task does not claim
VoiceOver/TalkBack support. Color-independent labels and the existing type scale
are present. Mobile hardware, user play acceptance and balance remain separate.

The initial design review led to one batch of layout/copy fixes and targeted
corrections for a remaining phone header/bar defect. Native Unity inspection,
source review and polish were performed in-thread. No independent subagent
critique command or browser/Lighthouse audit is claimed for this native screen.
