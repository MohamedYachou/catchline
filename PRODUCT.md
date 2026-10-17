# Catchline

<!-- impeccable:product-schema 1 -->

## Platform

adaptive

Unity native game with a custom illustrated coastal interface, shipped for
Windows and landscape mobile. Native Canvas/input/render checks apply here;
browser styling and Lighthouse are not applicable.

## Product Purpose

An active fishing automation game: start with a small rowboat, catch and carry
fish by hand, sell in Gull Harbour, and gradually build a working boat with
temporary crew and equipment. The hands-on fishing should remain satisfying.

## Capabilities and Constraints

The rowboat/skiff voyage loop already works. Preserve gameplay, save compatibility,
deck footprints, asset pivots and roles. Windows Codex owns runtime implementation;
the existing WSL Codex owns models and reference renders in the art worktree.

## Brand Commitments

Mo confirmed on 2026-10-15: closely match the existing goal renders, with the
fishing view (water, boat, HUD and catch feedback) setting the polish standard.
References: Art/STYLE.md, Art/Concepts/17-hud-fishing.png,
18-hud-harbour.png, 20-title-screen-1280.png and the Day 3/Day 28 references.

## Product Principles

- Finish a small playable slice to a premium visual and interaction standard.
- Visual language is part of the fun, not a cosmetic phase after feature growth.
- Every new feature inherits the finished standard when it is implemented.
- Keep play deliberate and active; automation frees the captain for bigger jobs.
- Use actual game captures and player feedback to judge the result.

## Evidence on Hand

Existing models, rigged crew, Fredoka font, complete supplied UI artwork and water
textures. The first-voyage loop and skiff regressions pass. Mo tested the core and
confirmed it works; the previous presentation lacked the desired polish.

## Open Decisions

Mo chose quiet, tactile coastal sounds on 2026-10-16: sea/harbour ambience,
wood/rope, cast/splash/reel and gentle catch/sale feedback. Minimum mobile
hardware and final mobile accessibility sizing remain unconfirmed. Mo authorizes a bounded fish-content/economy/bait/audio and catch-portrait pass on
2026-10-16, followed by distinct fish model polish. No monetization work.

## Player review — 2026-10-15

POLISH-002 is rejected as a visual target. Passing functional checks does not
mean the presentation is accepted. UI, water and world remain far from Mo's
references. The next pass must make a substantial visual improvement before
content expansion. Mo authorizes reuse from Plunder the Seas and suitable online
assets. Existing WSL artist now owns a complete authored first-location diorama
(ART-011), with Windows owning live water, faithful UI and runtime integration.

## Current Mo content direction — 2026-10-16

Mo asks for more fish in the existing locations, better rewards for big catches,
stronger value from squid, additional bait purchase options, quiet sound effects
and UI polish. Fish must have distinct authored models and matching polished
catch portraits. Keep the current voyage loop and unlimited free scraps. Native
review stays background-only; Windows owns water and scratch integration.
