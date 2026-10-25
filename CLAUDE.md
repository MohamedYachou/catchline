@AGENTS.md

# Two Claude sessions: goals and done list

Mo runs two Claude accounts here: **Claude 1** (Windows desktop app, "W" in ClaudeCom.md) and **Claude 2** (WSL CLI on
/mnt/c/Users/momoy/Projects/Catchline, "L"). This file holds each one's current goals and what is done; keep it true
and short. Delete a goal's line when it is done and add it (one line, commit id) under Done; prune Done to the last ~10.
Live status (heartbeat, plan usage, chat between the two) is in ClaudeCom.md. When one runs out, the other takes over
its goals here, in order, after checking the actual files. Codex orders and logs stay in comms.md.

@ClaudeCom.md

## Claude 1 (Windows) — goals, in order
1. Tutorial follow-ups: capture the at-sea step (FirstCast) and the Sell step; play SOUND-4 CoachPop when Mira appears
   (VoyageTutorial.cs plays Cue.CardFlip until then).
2. UI and animation polish of the crew office and harbour screens (design-stack skill first).
Holding: VoyageTutorial.cs, CrewUi/**, CoastalCanvas*.cs, Skin*.cs, LeadShots.cs, VoyageInterface.cs, VoyageMenus.cs.

## Claude 2 (WSL) — goals, in order
1. Direct the two Codex agents (skill codex-director): Codex 1 is on docs/briefs/HARBOUR-SOUND-2.txt, Codex 2 on
   docs/briefs/SOUND-4.txt. Review each delivery against its brief, make .meta files for new Assets files, commit only
   accepted files, write the next brief, append it to Art/Source/UIv2/CONTINUE-CODEX1.txt / CONTINUE-CODEX2.txt.
   Keep both always busy (Mo's order); their watchdogs relaunch about every 10 minutes and read those files.
2. Sound: wire Codex 2's SOUND-4 recordings (VoyageAudio.cs cue pattern from commit 7c2593b) once HARBOUR-SOUND-2 lands.
   Mo's own picks may come from the Sound picks artifact https://claude.ai/artifact/BZn1HJnhiexxQdSfSHLBoC.
3. Pending integrations: HARBOUR-LIFE-2, the MAP9 D5 chart/water handoff (Codex 1's uncommitted MAP9 hunks in
   Grounds.cs, SeaNav.cs, VoyageScenery.cs, GameData.cs grounds are its own; do not commit them as yours).
4. Morning report to Mo: what was done overnight, plus docs/QUESTIONS.md.
Holding: VoyageAudio.cs (after Codex 1 finishes), Assets/Resources/Audio/**, docs/briefs/**.

## Done (latest first)
- 2d5b0b3 first-run tutorial: Mira coach marks (VoyageTutorial.cs, CoastalCanvas.TryFind, captures docs/screens/overnight/tut-*)
- cd7259a / 70d3b29 ClaudeCom channel, usage line, WSL setup (shared instructions, memory, skills)
- b21fb21 card pacing sim rerun after crew tiers (Codex 1, accepted)
- 48671cf deck berths 2/4/6/8 per boat (Codex 1, accepted)
- 7c2593b real crew office sounds (card flip, chest open/heavy, reward chime, token pour)
- f920e4a crew tiers: crew join through blueprints and crew chests, welcome chest with Mira, crew art set
