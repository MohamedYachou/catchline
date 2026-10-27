# RESTAURANT-SEA-1B

Both accepted sea1-night-water tiles now have pixel-equal opposing edges in X and Y, including corners. Resolution, opaque RGB format, painted navy/blue ripples and sparse warm glints stay the same.

The reproducible recipe starts from the accepted candidate4 painting, Lanczos-resizes, then symmetrically blends opposing boundary differences into a 32px / 64px edge band with cubic smoothstep falloff. The remaining interior is bit-identical. No new painting or generated content. sea1-package.py now calls sea1b-package.py so rebuilding cannot restore the previous unequal edges. Numerical change statistics are in sea1b-texture-audit.json.

Proofs: native 4x4 PNGs at4096/8192 pixels, compact 4x4 JPGs, and nearest-neighbour 4x seam-intersection crops at both resolutions. Fresh independent reads verify edge equality and every repeated tile in all16 cells. Fine local ripple shapes still repeat with the source painting; exact boundary equality does not claim a new nonrepeating procedural ocean.

The additive sea1b-V4-check.blend and desktop/phone renders use the current RoomLook3 scene unchanged, the same V4 cameras and the same material recipe as SEA-1. Historical sea1 audits/proofs refer to the previous tile bytes; sea1b-final-audit.json supersedes their tile hashes. Original candidate4 provenance is unchanged.

No Assets/code/git edits. Native Unity sampling/material/runtime appearance remains lead-owned. Temporary repair backups removed after verification.
