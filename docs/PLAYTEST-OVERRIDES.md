# Test and playtest setup — Mo, 2026-10-16

**Current storage/net implementation (WEIGHT020, 2026-10-16):** cargo uses kg,
not fish slots; rowboat4/6kg, skiff18/27kg, compact24/36kg (base/upgraded).
Shallow nets cost30coins and soak20s; deep nets cost100coins/3uses and soak30s.
One final whole fish can exceed cargo capacity. Net yields use local mass budgets.
These supersede historical count/yield/replacement numbers below. Full rules and
native evidence: [WEIGHT020.md](WEIGHT020.md).

The new isolated `Builds/Weight020/Catchline.exe -deep-net-trial` fixture starts
the compact fisher with200coins, two fishers/one deckhand, two deep nets of3uses
each and deep selected. This never reads/writes the real player save. Normal
progression gives no free deep nets; buy and choose them in Supplies at harbour.

CREW026 fixes role availability in both Real and Test. The role guarantee is no
longer a one-candidate-per-role testing override: the board always has enough
deckhand and fisherman contracts to fill every berth on the current hull.

Hiring a worker removes that individual offer, then immediately adds another
candidate of the same role. Board rolls, refits and old-save loads also preserve
the role choices. Fees and 2/3/5-voyage contract expiry are unchanged, as is each
hull's crew cap. Real and Test use the same rules; the Test session does not
touch player saves.

For the current test slice the starter rowboat accepts two hired employees plus
the captain. A fisherman unlocks the existing second rod socket and claims that
rod, leaving the first rod for the captain. A deckhand carries and baits. The
captain stays at the rod after a catch with a prominent Throw again / Leave
choice; Throw starts the next cast without reselecting a world bubble.

The board can vary names and grades, but both roles remain hireable even after a
same-role hire. The rowboat still has two employee berths and powered tier3 boats
have three. The CREW026 Test shortcut starts at tier3 with an empty roster,
1000 session-only coins and the Crew Office open so any three contracts can be
chosen; normal fees and contract terms still apply.

Unlimited poor scraps, explicit port selling, saved unsold haul and freshness
feedback remain normal gameplay. Harbour storage freezes the remaining sale value.
Sell before sailing again; harbour contracts advance once at sale or arrival.

Verification: `FirstVoyageChecks.Regression` includes `UrgentCrewChecks.Run`:
real fisherman/deckhand simulation without captain input, two-crew limit, test
board across seeds and old saves, scraps bounds, persistent cast interaction,
unsold-haul save/reload, quote/sale equality, no duplicate sale and freshness.
Native preview captures support `-capture-voyage <directory> -capture-urgent`.
The capture fixture funds its own save-isolated hire actions; normal play does not.

## Compact fisher mechanics trial — NET-010 (2026-10-16)

The **session-only preview** offers “Compact fisher · trial” at the Chandlery.
It switches to additive saved hull ID2, provides at least200trial coins,20fuel
and full food, and leaves the crew mix to the player. Hire any three crew at
the Crew Office. This deliberately avoids asserting a final boat price or
changing the tier0/1/2 economy. Normal saves do not receive trial funds/boats.
Existing Rowboat0/Skiff1 saves retain their IDs and behaviour.

The compact fisher has three rods and a small stationary net. NET015 supersedes
the old timed setting/hold-to-winch model. Setting is three timed screen taps in
the green zone, followed by a20second soak yielding3–5local schooling fish.
Hauling uses short taps: build tension near the red threshold for best progress;
slack line loses progress, near-red loses least, and red loses progress rapidly.
Two mistakes across setting/hauling tear one net and lose the unlanded catch.
No captain random failure. Holding the screen does not repeat pulls.
Nets-duty deckhands set in2working seconds and haul in5; one completed recovery
roll has80% safety/20% tear risk. Cancelling does not reroll a ready catch.
A successful haul automatically gathers/carries/stows the entire batch, with no
per-fish clicks. Capacity is checked per fish; overflow remains in the basket.
Captain/deckhands may overlap and deliver concurrently. No hold-access lock.
A clean cycle reuses the fitted net. Three usable nets start aboard (one fitted
plus two reserves); rack cap4total. Supplies sells replacements for80coins.
This is provisional economy tuning. Legacy saves get default stock; a saved zero
stays zero. Nets and net minigames currently apply to the compact fisher only.

Each deckhand has an explicit saved duty, adjustable at sea under Crew duties:
Fish handles rod catches/bait; Nets handles setting/hauling/basket. A soak
releases its worker, who watches for the next net task rather than taking
rod work. The captain covers unassigned logistics and can leave a waiting
rod to set/haul, but must finish a cast/reel or action first.

Compact-only novice handling starts at1.4s pickup/3s stow, plus real walking.
This is provisional bottleneck tuning; older boats keep their timings. Crew
speed grades apply. The captain uses the same handling rules. The early
production boat ladder/prices/tutorial remain separate pending work.

NET015 laptop launch: `-netboat-trial -native-display` opts into a direct
at-sea compact fisher with two fishers/one hand prepaid, exactly200coins left,
60bait, full food and fuel. Borderless resolution uses the physical monitor
(Mo's laptop2560×1440), render scale1. SessionOnly is required for the fixture;
normal save files stay untouched. Updated feedback preview builds separately
under `Catchline-sim/Builds/Net015`, preserving any running earlier player.
