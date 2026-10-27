# Questions for Mo

Started overnight on 2026-10-25, trimmed by Claude 2 on 10-26. Each question has a default, which is what the game does now. Answer only the ones
you want changed.

1. **Starting rarity by tier.** Crew from higher tiers join at a higher rarity: tier 1 White, tier 2 Green, tier 3
   Blue, tier 4 Purple, tier 5 Legendary. Together with the +5% work per tier, this is the power creep. You wrote
   "at least the base white card each tier". Should every new crew member start White instead? That would leave the
   tier multiplier as the only creep, and the top-tier crew would join with no abilities.
   *Default: keep the rising starting rarity.*

2. **Crew chest price.** Three sea chests' worth: 2,100 coins at tier 1, up to 5,700 at tier 5. A crew member's full
   offer of 10 chests costs 21,000 to 57,000 coins.
   *Default: keep these prices until the pacing simulation says otherwise.*

3. **Tier 3 boat (Jig boat).** Its art is accepted (10-26); Claude wires it in next, between the Compact and the
   Prep fisher, so Tess, Ana and Lise will join from it. Existing saves on a Prep or Buoy fisher move up one hull
   number, so nobody loses a boat. *Default: refit price halfway between the Compact's and the Prep's.*

4. **The welcome chest's 20 tokens and one tool.** Enough to show what tokens and tools are for in the tutorial.
   *Default: keep.*

## Pacing (from Codex 1's rerun, docs/plans/CARDS-PACING.md)
- A player who buys a 700-coin sea chest every time they can afford one never saves for the Compact (4,000). Median Mythic is still day 33, but on the Skiff. Options: leave it (players will save on their own), raise the sea chest price (6,000 gives a full hull path and Mythic day 34), or have the hull refit nudge appear when savings stall. My pick: leave prices; the harbour savings-goal tile is now in (4095521).

## Sound
- **Listen to the five SOUND-4 cues** (coach pop, refit fanfare, tab tap, coin buy, page turn): open
  Art/Audio/Real/sound4-listening.html. No agent can hear; they are wired in on the technical check only.
  Also: Horn_1/2 and SealBark_1/2 in Assets/Resources/Audio are not from the real pack. *Default: keep them.*

## New (Claude 2, 10-26)
- **Gold-fish minigame.** You're thinking it over. Claude's proposal: a line-tension fight (hold to reel, ease off when
  the line goes red, 3–4 runs). Until it exists, gold and red fish stay off. *Default: no gold/red fish yet.*
- **Chart 3.** Every further ground goes on a third chart (Kelp forest is the last on the Outer coast). Which coast,
  how many grounds, and which boat opens it (the tier 6 boat?). *Default: no map 12 until you decide.*

## Restaurant, night of 10-26 → 10-27 (Claude 2)
- **Mira's look.** Four busts: rc-bust-mira-a/b/c/d in Assets/Art/UI. D (navy host jacket, scarf) is in the game for
  now, on the rail, S5 and S9. *Default: D.*
- **Terrace side.** Your plan (RESTAURANT.md) puts the 3×5 terrace on the quay side of the room. Codex 2 built the
  Bistro/Restaurant/Seafood rooms with the terrace in front, over the water (it looks like ui-8), which doesn't fit the
  game's grid. Codex 2 is refitting them to your plan. Say if you'd rather have the front terrace; then the grid changes
  instead. *Default: your plan, terrace on the side.*
- **Crew priorities (S9).** Tap a task, then tap another in the same row to swap them. This works the same on phone and
  desktop; the mockup said "drag". *Default: tap-to-swap.*
- **Mira's house on the quay.** It stands at the east end (x 13–27 at its widest) and the crane moved west. The Seafood
  house's terrace will come close to the moored boats there. *Default: check when stage 4 is reachable.*
- **First night.** Mira's 4-panel coaching card shows once before the first service, which waits until it's tapped.
  *Default: keep.*
