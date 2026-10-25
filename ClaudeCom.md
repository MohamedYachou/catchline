# ClaudeCom — Claude W (Windows desktop app) ↔ Claude L (WSL)

Rules (Mo, 2026-10-25):
1. Claude-to-Claude talk happens only here. Codex orders and START/DONE logs for Codex stay in comms.md, because Codex reads that.
2. Keep your own section current: one Goal, the Next steps in order, the files you hold. When a step is done, delete it (git history keeps it). When the goal is done, replace it with the next goal.
3. Heartbeats are automatic: the hook in .claude/settings.json refreshes yours while you work, shows you the other's new Chat lines, and warns when the other has been silent 25 min with an open goal.
4. Takeover: when warned, set the other's State to out, move its Goal and Next steps into your section, write "TAKEOVER" in Chat and continue from its first Next step. Check the actual files first, since the step may be half done.
5. Both online: split work by files. Claim a file under Holding before editing it, and never edit a file the other holds. Ask in Chat: `python docs/tools/claudecom.py say "..."` (or python3 in WSL).
6. Keep this file under ~60 lines. Chat keeps the last 12 lines by itself.

## Claude W (Windows desktop app)
Heartbeat: 2026-10-25 23:06 +0100
State: working
Goal: Night plan. Tutorial flow (tier 0 alone → skiff → welcome chest with Mira → recruit), then sound polish, keeping Codex 1 and 2 busy.
Next:
- Tutorial: new VoyageTutorial.cs (coach overlay with Mira poses from Assets/Art/UI/Tutorial, bubble, ring, pointer), step saved in GameState/SaveV2, targets marked where buttons are drawn (port/sail, shop tabs, refit, crew office, Recruit tab).
- Capture the tutorial (LeadShots), run the regression in Catchline-lead-sim, commit.
- Codex 1 is on docs/briefs/HARBOUR-SOUND-2.txt; Codex 2 is on docs/briefs/TUTORIAL-ART-1.txt (wave and point done, then explain/cheer/think/map, bubble, pointer, arrow, ring). Review each delivery, make .meta files, give the next brief via Art/Source/UIv2/CONTINUE-CODEX*.txt.
- Morning: report to Mo with docs/QUESTIONS.md.
Holding: Assets/Scripts/Game/VoyageTutorial.cs (new), CrewUi/**, VoyageAudio.cs until Codex 1 starts HARBOUR-SOUND-2

## Claude L (WSL)
Heartbeat: -
State: not started
Goal: -
Next: -
Holding: -

## Chat (newest last, last 12 kept)
- 10-25 23:06 W: Channel set up. On start, read this file, CLAUDE.md and the latest comms.md lines, then ask here before taking anything in my Holding list.
