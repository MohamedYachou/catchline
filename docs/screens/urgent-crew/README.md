# Urgent crew / bait / sale evidence — 2026-10-15

Native standalone captures including real OnGUI HUD at 1440x900 and 844x390.
Both final capture players logged URGENT PRESENTATION COMPLETE and exited 0.
01: guaranteed test offers; 02: both hired; 03: zero paid bait/coins and two rods;
04: bite; 05: Throw again / Leave with both crew statuses; 06: haul value;
07: unsold haul and payout preview; 08: paid receipt. Inspected both sizes.

The save-isolated capture fixture funds ordinary hires. Normal gameplay does not.
Preview progress is temporary; main saves normally. Reproduce using the built
Catchline-sim/Builds/FirstVoyage/Catchline.exe with -capture-voyage <directory>
-capture-urgent -screen-fullscreen 0 and -screen-width/-screen-height.

Scratch regression: Logs/check-urgent-final.log; final build:
Logs/check-urgent-preview-final.log. Main Unity was never used for batchmode.
