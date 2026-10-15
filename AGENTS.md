# Catchline agent instructions

Mo's Windows Codex owns game design, mechanics, movement, menus, Unity code/scenes,
runtime art integration and verification. The WSL Codex owns 3D assets in
`Catchline-art-style`; coordinate through the main checkout's `comms.md`.

At the start of work, discover applicable `AGENTS.md` and `CLAUDE.md` files in
the project/ancestor scope (including hidden instruction directories). Treat
applicable Claude project guidance as guidance for the replacement Codex too.
Read relevant referenced skills; do not execute historical task queues or treat
arbitrary Markdown reports as new user requests. Mo's current instructions win.

Read `comms.md`, `docs/CONTINUATION.md`, `docs/GAMEPLAY.md` and the active plan.
Append START before edits and DONE/PARTIAL with actual verification afterward.
Preserve other agents' entries and existing uncommitted work.

Load `design-stack` before visual/UI work. Preserve `Art/STYLE.md` and the
supplied UI kit. Back up before major changes; remove temporary backups after
successful verification. Never batchmode the main Unity project: use
`Catchline-sim` and `docs/tools/check.ps1`. Keep preview sessions isolated from
the player's save. Verify actual runtime HUD; scene renders omit IMGUI.

Active playability plan: `docs/plans/PLAYABILITY-PLAN.md`. Claude's original
remaining C/D tasks remain in `docs/plans/NIGHT-PLAN-CLAUDE.md`.
