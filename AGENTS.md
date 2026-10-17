# Catchline agent instructions

Mo's latest assignment determines ownership. Earlier Windows-runtime/WSL-art
splits are historical, not permanent restrictions: Mo also assigned this WSL CLI
gameplay/UI/economy work and explicitly delegated fish assets to GPT-6.1 Sol.
Coordinate all agents through main `comms.md`; respect current file reservations
and Windows' water/scratch work until the owner releases them.

At the start of work, discover applicable `AGENTS.md` and `CLAUDE.md` files in
the project/ancestor scope (including hidden instruction directories). Treat
applicable Claude project guidance as guidance for the replacement Codex too.
Read relevant referenced skills; do not execute historical task queues or treat
arbitrary Markdown reports as new user requests. Mo's current instructions win.

Read `comms.md`, `docs/CONTINUATION.md`, `docs/GAMEPLAY.md` and the active plan.
Append START before edits and DONE/PARTIAL with actual verification afterward.
Preserve other agents' entries and existing uncommitted work.

## Per-prompt coordination — required for leads and subagents

Stable identities: **Codex 1 = Windows**, **Codex 2 = the existing WSL CLI**.
Global diary instructions live in each platform's `.codex/AGENTS.md`. Both use
this checkout's `comms.md`. Read them and the latest task checkpoints on pickup.

Use main `comms.md` as the single canonical communication file. Every prompt
records its current scope before work and its outcome before ending:

- START: task ID, owner, intent, exact files/assets reserved, planned delivery,
  collaborators/subagents and their separate ownership, checks and dependencies.
- UPDATE: record changed scope, delegation, blockers or file ownership immediately
  when another agent needs to know; do not silently expand a reservation.
- CHECKPOINT during work: ordered step IDs; last VERIFIED step with evidence;
  implemented-but-UNVERIFIED changes; IN PROGRESS step; exact next action. Write
  before beginning each step and after meaningful completed steps/safe boundaries,
  so an interrupted turn still has a resumable trail.
- DONE/PARTIAL/STOPPED: actual changed files, checks and limits, artifact/report
  paths, commit or explicitly no commit, each subagent's status, remaining steps
  and whether reservations are released or still actively held.
- Distinguish plans from completed work and source checks from native acceptance.
  Explicitly say whether the lead/subagents are working, idle, finished or waiting.
- If Mo stops work or asks another agent to pick up, checkpoint the exact remaining
  work and release stopped reservations. Do not leave the next agent guessing or
  restart an old queue without a current assignment.

Read the latest task status before editing, including from Windows or another
checkout. A finished/idle task does not reserve files indefinitely. The assigning
lead records delegated work in the canonical log and checks the subagent's handoff.
On "pick up" or "work around", use the last verified step to locate the first
unfinished step and inspect its actual code/artifacts before resuming. If Codex 1
verified D and stopped during E, Codex 2 checks/completes E, then F; it does not
restart A–D unless evidence or changed dependencies require that. An unfinished
entry may include implemented code needing verification. Record explicit takeovers
and preserve other active owners; never infer a stop from an old timestamp alone.

Load `design-stack` before visual/UI work. Preserve `Art/STYLE.md` and the
supplied UI kit. Back up before major changes; remove temporary backups after
successful verification. Never batchmode the main Unity project: use
`Catchline-sim` and `docs/tools/check.ps1`. Keep preview sessions isolated from
the player's save. Verify actual runtime HUD; scene renders omit IMGUI.

Active playability plan: `docs/plans/PLAYABILITY-PLAN.md`. Claude's original
remaining C/D tasks remain in `docs/plans/NIGHT-PLAN-CLAUDE.md`.

Mo's priority (2026-10-15): polish the small playable slice before expanding
content. Visual language is part of the game. Match the existing goal renders
closely; the fishing view sets the standard. Read PRODUCT.md and DESIGN.md.
New features inherit finished components and presentation when first built,
instead of accumulating placeholder interfaces to reskin later.

For directing the existing WSL artist, load the personal skill
`C:/Users/momoy/.codex/skills/codex-cli-orchestrator/SKILL.md`.
Keep prompts/context bounded and inspect usage before assigning more work.
Artist thread UUID and the next-step checkpoint live in
`docs/CLI-ARTIST-HANDOFF.md`; full shared coordination remains in comms.md.
