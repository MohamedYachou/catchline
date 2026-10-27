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

## Restaurant, early 10-27 (Claude 2)
- **HUD v3 concepts for the rest of the game.** Codex 1 painted the fishing view and the harbour in the restaurant's
  look: Art/Source/Restaurant/concepts/ui-v3-17-hud-fishing.png and ui-v3-18-hud-harbour.png. Nothing is cut or wired.
  Yes means Codex cuts them 1:1 and Claude moves the fishing/harbour HUD over. *Default: wait for your yes.*
- **Reliable stove needs the Bistro.** Codex's S8 art has a "Needs Bistro" state, so the stove upgrade now opens at stage 2
  (fridge and lighting stay at the Cafe). Breakdowns start on night 2; until the Bistro, the captain fixes stations by
  tapping them. *Default: keep.*
- **Pause menu.** The third button of Codex's pause panel said "Back to the harbour"; the night can't be left halfway, so
  it opens Upgrades instead (Back returns to the night). *Default: Upgrades.*
- **Week report (S16).** Shows after every 7th night, before Sleep. "Crew of the week" is whoever walked the most that
  week (the captain doesn't count). *Default: keep.*
- **First-night coaching.** Besides the S13 card, Mira pauses the first night twice with the new coach card (tap a table
  / close the door). Skip ends it. *Default: keep.*
- **Hiring for the restaurant (S17).** Codex painted a hiring board (concepts/ui-17-hire.png): three candidates a day, a
  nightly wage, Hire. Today the restaurant staff are your fishing crew in restaurant clothes, so hiring would be a second
  way to get people. Should restaurant staff be hired separately (wage per night), or stay the crew cards? *Default: crew
  cards only; the board stays unwired.*

## Restaurant, morning 10-27 (Claude 2)
- **Market partial sales (S7).** Codex cut "Sold out", "Fresh today" and kg +/- buttons. Today the whole catch goes to the
  buyer or the kitchen per fish (Sell / Keep). Do you want to sell part of a fish by kg, and fish that carries over to the
  next day (so "Fresh today" means something)? *Default: keep whole-fish Sell / Keep; the pieces stay unwired.*
- **Pause dims the room.** The pause panel doesn't dim the room behind it yet: the screenshot tool drops full-screen dim
  layers, so it can't be checked without your screen. *Default: leave until it can be checked in a normal play window.*
- **Closing Mira.** The closing mockup paints Mira in her captain's coat; in the restaurant she is the host. Codex 1 is
  repainting that cut in the host outfit (queued). *Default: host outfit.*
- **Night sea.** Codex 2's new seamless sea came out near-black against the painting's mid-blue, so the old water stays
  until the repaint (queued).
