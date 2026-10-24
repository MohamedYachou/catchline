# UI107 — tactile coastal UI mockups

Created 23 October 2026 by Codex 1 (Windows app) for Mo's supplied direction.

These are polished generated concept images, not implemented game screens. The
current game was inspected as the baseline. Native screenshots served as reference
inputs; image generation can redraw their pixels, including the boat and portraits.
Numbers describe illustrative screen states, not a fresh telemetry measurement.

## Pictures and exact generation prompts

| Screen | Picture | Prompt |
| --- | --- | --- |
| Voyage HUD | [01-voyage.png](01-voyage.png) | [01-voyage-prompt.txt](01-voyage-prompt.txt) |
| Operations | [02-operations.png](02-operations.png) | [02-operations-prompt.txt](02-operations-prompt.txt) |
| Crew | [03-crew.png](03-crew.png) | [03-crew-prompt.txt](03-crew-prompt.txt) |
| Shop | [04-shop.png](04-shop.png) | [04-shop-prompt.txt](04-shop-prompt.txt) |

Generated using the built-in image generation tool, one call per screen. The
Voyage image established the visual family; subsequent screens referenced the
preceding mockups for consistency. Each final image was visually inspected.

## Current-game reference inputs

- `docs/screens/deep104/layout1-boat-1440.png`: boat, camera, water, current
  crew rail, voyage resources and current actions.
- `docs/screens/deep104/layout1-tab1-1440.png`: four actual pipeline stages.
- `docs/screens/deep104/layout1-tab2-1440.png`: current crew tasks/bait controls.
- `Assets/Resources/FishReference/portrait-fisherman.png`: existing fisher identity.
- `docs/screens/polish-004/desktop/09-chandlery.png`: historical shop/harbour
  visual reference, not claimed to depict the latest shop implementation.
- Current shop categories and availability/prices were checked directly against
  `Assets/Scripts/Game/VoyageInterfaceShop.cs`, `GameData.cs`, and
  `GameStateProgression.cs`: Tier 5 big cooler 3000, ice box 2500, carbon rods 3500,
  third deep-line rig 3500. Shop balance 5000 is illustrative.

## Direction represented

- Warm cream slabs, navy bands/outlines, bevels, soft shadows and large readable
  illustrated icons; chunky display lettering and rounded body lettering.
- One orange primary per page: Head home, Assign crew, Save duties, Buy.
- Voyage keeps a recognizable central boat and right crew rail; supply/goal
  panels become one slab, interactions become speech bubbles, secondary actions
  become cream icon buttons.
- Operations uses four connected stages and visible fish queues (0/2/8/1).
  Processing is the red, labeled backlog. No cost panels, charts or efficiency
  rings. Details affordances indicate the intended full-page stage navigation;
  an opened stage-detail page is outside this four-image set.
- Crew shows Pim's bust, speciality badge, two tap-to-cycle duty slots and bait
  choices. Primary/Secondary, specialty and explicit Save behavior are proposals,
  not claims that current gameplay already supports this exact interaction.
- Shop is a full-page wood/rope board with illustrated equipment, price pills,
  one purchase action and five large bottom navigation tabs.

## Visual review and limits

All four images were reviewed for coherent materials/type, complete framing,
readable key labels, requested information hierarchy and single-primary-action
coverage. The Ops fish queues and bottleneck are visible, crew duty slots are
unambiguous, and all five shop tabs fit inside the frame.

The mockups use illustrated lettering approximating the requested display/body
font pairing; they are not proof of the precise installed Lilita One/Fredoka
fonts. Game code, art assets, DESIGN.md, builds, launchers and saves were not
modified. No runtime tests or physical touch acceptance are claimed. Dense
landscape-phone behavior still needs a dedicated layout pass if this direction
is selected for implementation. No commit or staging was performed.
