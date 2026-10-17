# Catchline playability plan — 2026-10-15

Mo chose the first voyage as the first priority. Keep active play, deliberate
pacing, hands as a bottleneck and player-chosen crew with meaningful captain
work after every berth is filled.

**Updated direction:** Mo tested the core loop and confirmed it works. Polish
the small slice to closely match the existing renders before adding content.
POLISH-002 prioritises fishing water/boat/HUD/catch presentation, a real menu,
coherent harbour shops and reusable visual components. PRODUCT.md / DESIGN.md
record this contract. The WSL artist is doing ART-010 in its existing CLI session:
matching-camera reference renders and rowboat detail, not new gameplay content.
Items 3–5 below are deferred until the visual foundation is accepted through play.

1. First voyage: real action-state guidance, a small optional three-fish goal,
   forgiving first catches, readable catch/weight/value feedback, safe stow
   feedback, selling and an attainable storage upgrade. Verify manual actions,
   early-strike recovery, selling, tutorial completion and save compatibility.
2. Play it with Mo: inspect actual desktop and landscape-phone HUD; use a
   session-only Windows preview so experiments do not replace the main save.
   Ask what felt slow, confusing or satisfying; tune from that feedback.
3. Make automation's benefit visible: second rod + deckhand, readable job
   states and pile-up pressure. Then revisit net pacing and the skiff.
4. Continue Claude C1–C4: contracts, rivals/weigh-off, daily reward, light sea
   events. Integrate remaining title/chart/UI artwork and sale/purchase feedback.
5. Integrate reviewed ART-009 deliveries, then tackle day-boat gameplay once
   the rowboat/skiff loop earns its complexity.

Do not mark the full night plan complete from this first-voyage slice. Preserve
its outstanding tasks. Native captures and test logs must distinguish actual
interactive play, scripted actions and scene-only renders.

## Urgent Mo override — 2026-10-15

The 2026-10-15 urgent slice introduced rowboat fishermen, fallback bait, explicit
port sale/save, freshness feedback and persistent Throw again / Leave interaction.
CREW026 fixes role availability in both Real and Test: enough temporary contracts
of each role remain on offer to fill the current hull, replenishing immediately
after a hire. Existing fees and 2/3/5-voyage expiry are unchanged.
