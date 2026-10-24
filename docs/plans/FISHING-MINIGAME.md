# Rod minigame: full-screen rod view (decided 2026-10-24)

Mo picked full screen after trying the crude prototype: "whenever you go it throws a rod and you get in full
screen, but we need enough animations, a rod, it needs to look good and fluent, not just being forcefully
transported in fullscreen of just water and a fish, there has to be a rod".

## The beat, start to finish

1. **Cast (about 1.2 s, one continuous camera move, no cut).** The player taps the rod's Fish bubble. The captain
   baits as now, then casts. As the cast animation starts, the camera swoops from the boat view to over the
   captain's shoulder. It follows the bobber's arc out and settles into the rod view. The deck HUD fades out over
   the same 0.4 s.
2. **Rod view (waiting).**
   - Framing: the rod comes in from the lower right, held in the captain's gloved hands, with the reel visible.
     The line runs from the tip to the bobber 6–8 m out. The horizon sits high and the water fills the screen.
   - The rod sways with the swell, and the line sags and lifts with the bobber.
   - The fish is seen under the surface as the FishShadow silhouette of its real 3D model, sized by kg. It
     approaches, circles, nibbles and fakes.
   - The only UI left is pause and a small "Reel in" button that leaves the rod.
3. **Reading the fish.** All of it is diegetic: no banners, no "PULL" text, no timing bar.
   | What the fish does | What you see and hear |
   |---|---|
   | Nibble | Two or three shallow ticks, small ripple rings, the rod tip barely twitches, soft tick sounds. |
   | Fake | One deep dip that holds a moment and pops back up with a bounce, while the fish backs off with a bubble puff. The rod bends, then relaxes. |
   | Take | The bobber goes fully under and **stays** under, and the line runs sideways. The rod bends hard and stays bent, and the line zings. |
4. **Strike.** Tap or click anywhere, or press Space. The rod yanks up and the line snaps taut.
   - **Hooked:** the rod bends deep, the reel spins and the fish thrashes at the surface for 1–2.5 s, scaled by
     kg. It is lifted out on the line toward the camera, hangs for a beat as the real 3D model, then the camera
     pulls back to the boat (1 s) and the catch card shows as now.
   - **Too early** (nibble or fake): the bobber pops up, the fish darts off and the line goes slack. The bait is
     gone, as the current rule says. The camera pulls back to the boat.
   - **Too late:** the bobber bobs back up, and the fish shakes off and swims away. The bait is gone. The camera
     pulls back.
5. **Tips.** With Tips on, the first two casts of a save show one quiet line at the bottom: "Wait until the bobber
   stays under, then strike." It is never shown again after that.

## Difficulty by fish (BiteModel, `Assets/Scripts/Game/Minigame/BiteModel.cs`)

- `BiteModel.DifficultyFor(species, kg)` is 70% species heaviness and 30% where the kg sits in that species'
  range. A minimum herring is about 0.05; a big cod is above 0.8.
- **Small fish:** comes straight in, nibbles 1–2 times, never fakes, and gives a 0.9 s take window.
- **Big fish:** inspects longer, nibbles 2–4 times, fakes about twice with deep dips (up to 0.88 under), and gives
  a take window down to 0.42 s.
- The model outputs these signals, and the view only reads them: `Dip`, `Drift`, `RodPull`, `FishPos`,
  `FishHeading`, `FishDepth` and `Dart`.
- `Assets/Editor/BiteModelChecks.cs` proves it:
  - A patient striker (0.3 s reaction) hooks every fish.
  - A greedy striker never hooks a big cod.
  - Herring never fakes.
  - An ignored take ends the bite.

## Scope

- **v1:** only the captain's own rod goes into the rod view. Crew fishers keep the current automatic logic.
- **Fight phase:** not in v1. The hooked fight is a short automatic reel scaled by kg. A real fight (tension
  through rod bend and line creak, no bar) is planned for tier 2 and later, after Mo plays v1.
- **Net minigame:** next, in the same diegetic spirit. The net is real in the water at the stern and fish shapes
  fill its bag. The floats sink and the winch rope creaks as it gets heavier, and an overfilled net can tear.

## Work split

- **Claude:** this design, BiteModel and its check, and review.
- **Codex 1:** FISH-SILHOUETTE-1 (the underwater fish), then FISH-VIEW-1 (camera, rod view, wiring, transitions).
- **Codex 2:** FISH-ROD-ART-1 (the first-person rod, reel and gloved hands, with animation), after SEA-SCENE-1.
