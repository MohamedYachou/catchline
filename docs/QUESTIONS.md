# Questions for Mo

Written overnight on 2026-10-25. Each question has a default, which is what the game does now. Answer only the ones
you want changed.

1. **Starting rarity by tier.** Crew from higher tiers join at a higher rarity: tier 1 White, tier 2 Green, tier 3
   Blue, tier 4 Purple, tier 5 Legendary. Together with the +5% work per tier, this is the power creep. You wrote
   "at least the base white card each tier". Should every new crew member start White instead? That would leave the
   tier multiplier as the only creep, and the top-tier crew would join with no abilities.
   *Default: keep the rising starting rarity.*

2. **Crew chest price.** Three sea chests' worth: 2,100 coins at tier 1, up to 5,700 at tier 5. A crew member's full
   offer of 10 chests costs 21,000 to 57,000 coins.
   *Default: keep these prices until the pacing simulation says otherwise.*

3. **Tier 3 has no boat.** The jig boat isn't built yet, so Tess, Ana and Lise join from the prep fisher (tier 4).
   *Default: leave it that way until the jig boat exists.*

4. **The welcome chest's 20 tokens and one tool.** Enough to show what tokens and tools are for in the tutorial.
   *Default: keep.*

## Pacing (from Codex 1's rerun, docs/plans/CARDS-PACING.md)
- A player who buys a 700-coin sea chest every time they can afford one never saves for the Compact (4,000). Median Mythic is still day 33, but on the Skiff. Options: leave it (players will save on their own), raise the sea chest price (6,000 gives a full hull path and Mythic day 34), or have the hull refit nudge appear when savings stall. My pick: leave prices, add a "saving for Compact" goal in the harbour UI later.

## Sound
- **Listen to the five SOUND-4 cues** (coach pop, refit fanfare, tab tap, coin buy, page turn): open
  Art/Audio/Real/sound4-listening.html. No agent can hear; they are wired in on the technical check only.
  Also: Horn_1/2 and SealBark_1/2 in Assets/Resources/Audio are not from the real pack. *Default: keep them.*

## HUD (Claude 2, 10-26 night)
- **D1 "match 17-hud-fishing / 18-hud-harbour precisely"** is from the 10-15 night plan. The live HUD has since moved
  to the UI v2 kit (cream panels, crew rail, Display type; see docs/screens/overnight/hud-*.png), which goes beyond those
  flat concepts. Matching them now would undo accepted work. The part of D1 still open, the TAP burst and press
  ripple in the strike panel, is STRIKE-TAP-1 (Codex 1, finishing tonight).
  *Default: count D1 done once STRIKE-TAP-1 is accepted. Say if you want new HUD mockups instead, and for which screens.*
- **Boats:** the Rowboat and Skiff are refined in game (7cafc46; captures intro-8.0s, refit-skiff-1.6). Codex 2 now
  does the Compact, Prep and Tier-5 trim the same way, plus new refit-card pictures.
