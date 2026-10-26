# Crew polish — Codex 2 (WSL CLI), 16 October 2026

Mo requested correct character facing, no progress bars above sailors, a walking
and lookout routine for idle deckhands, and worker HUD imagery closer to fish.png.

The crew rail now uses the actual captain, deckhand and fisher portrait pixels
from `docs/reference-hud024/fish-original.png`. Each original 57×60 fragment keeps
its cream backing and is displayed at the existing reference coordinates.
`docs/tools/extract_crew016.py` reproduces these crops; their bounds and hashes
are in `docs/screens/crew016/portraits.json`. Veterans retain their actual role's
portrait; no unsupported professions or experience values were added.

Idle deckhands take slower walks around the current hull's walkable grid, pause
for 3.8–5.6 seconds facing the water, and continue along the deck. A gentle
downward head glance and scan uses the existing crew rig. The scheduler keeps
checking for work during patrol, so a catch, empty hook or available assigned
net job interrupts immediately. Idle routines neither reserve work stations nor
consume the fish/economy random stream. Real jobs retain their existing timing.

The overhead progress geometry is removed. Rigged sailors also no longer receive
the extra high-frequency whole-body bob on top of their authored animation.
Heading turns are eased by a bounded turn rate; bait/cast/watch/reel face the
rod's actual side, pickups face the fish, deliveries face the hold and net work
faces the stern equipment. Automatically carried net batches use the carrying
walk pose, with that state cleared on unload or cancellation.

Verification uses `Catchline-sim`, never main-project Unity batchmode:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File docs/tools/check.ps1 -Name crew016-final -Method Catchline.EditorTools.CrewPolishChecks.ValidateAndBuildPreview
```

This runs the existing first-voyage/skiff/crew/sale/water/menu/HUD/compact/net
regressions, net tap/tear/economy checks, focused all-hull patrol/action checks,
native world plus Canvas captures, and a separate Windows build. The focused
fixture checks walk/look/resume, unblocked routes, immediate job interruption,
real pickup/delivery/bait/net facing, paused transforms, no root jitter, no
overhead progress geometry, RNG isolation and imported reference portraits.

Native captures cover 1440×900 desktop, 1672×941 reference dimensions and
844×390 landscape phone. The game targets landscape; browser tests and
Lighthouse do not apply. Existing small phone typography and world-action
bubbles covering some sailors remain broader HUD limitations. Static captures
and scripted checks do not establish physical input feel or Mo's acceptance.

Preview output: `Catchline-sim/Builds/Crew016/Catchline.exe`. Start with
`-netboat-trial -native-display` to use the existing isolated 200-coin compact
boat fixture with two fishers and a deckhand. The current running player is
left in place; no foreground launch/restart is part of this polish pass.

No commit, staging or reset. Existing unrelated project work is preserved.

Final result: `check-crew016-final.log` completed with exit 0, including every
listed regression and the separate Crew016 build. Desktop and landscape-phone
captures were inspected. Native reference-resolution portrait comparisons show
zero RGB difference for all three portrait regions; this claim applies to those
regions, not the whole HUD. The built player reached its isolated trial startup
and remained alive with no runtime exception or unreadable-mesh error during
the bounded headless smoke check; the diagnostic process was then stopped.
Evidence and narrow limits are recorded in `docs/screens/crew016/verification.txt`.
