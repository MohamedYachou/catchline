# ClaudeCom — Claude 1 (W, Windows app) ↔ Claude 2 (L, WSL)

Rules (Mo, 2026-10-25):
1. Claude-to-Claude talk happens only here. Codex orders and START/DONE logs for Codex stay in comms.md, because Codex reads that.
2. Goals and the done list live in CLAUDE.md. Here keep only a one-line Goal (what you are doing right now) so the takeover check knows you are busy.
3. Usage: keep a Usage line (5-hour and weekly percent used). Claude L's status line writes it by itself; Claude W reads it from the app (get_usage) and writes it with `claudecom.py usage`. When yours passes ~90% of the 5-hour or weekly window, hand your Next steps over in Chat before you stop.
4. Heartbeats are automatic: the hook in .claude/settings.json refreshes yours while you work, shows you the other's new Chat lines, and warns when the other has been silent 25 min with an open goal.
5. Takeover: when warned, set the other's State to out, move its Goal and Next steps into your section, write "TAKEOVER" in Chat and continue from its first Next step. Check the actual files first, since the step may be half done.
6. Both online: split work by files. Claim a file under Holding before editing it, and never edit a file the other holds. Ask in Chat: `python docs/tools/claudecom.py say "..."` (or python3 in WSL).
7. Keep this file under ~60 lines. Chat keeps the last 12 lines by itself.

## Claude W (Windows desktop app)
Heartbeat: 2026-10-26 00:14 +0100
State: working
Usage: 5h 63% resets 04:00 · week 90% resets Wed 07:00 (at 00:14)
Goal: Review Codex deliveries (FIRST-CATCH-ART-1, SOUND-WIRE-4), then polish

## Claude L (WSL)
Heartbeat: 2026-10-26 00:10 +0100
State: working
Usage: 5h 9% resets Mon 04:10 · week 1% resets Wed 00:00 (at 00:13)
Goal: -

## Chat (newest last, last 12 kept)
- 10-25 23:06 W: Channel set up. On start, read this file, CLAUDE.md and the latest comms.md lines, then ask here before taking anything in my Holding list.
- 10-26 00:08 W: Night-shift check 00:07: Codex 2 IDLE after UI-POLISH-ART-1 (13 new PNGs in Assets/Art/UI/Crew need review/metas + next brief); Codex 1 still on TUTORIAL-CHECK-1. Claude L, both are yours to direct.
- 10-26 00:14 W: W at 90% weekly, pausing. Committed 9c99409. Codex 1 on CAST-SPLASH-1, Codex 2 on CAST-SPLASH-ART-1 (briefs in docs/briefs). If you start: review those, make metas, commit; my goals in CLAUDE.md.
