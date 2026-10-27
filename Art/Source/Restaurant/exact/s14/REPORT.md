# S14 harbour restaurant entry

Concept: ../../concepts/ui-14-harbour-entry.png. Original18-hud-harbour.png is1920x1080 (16:9); its canvas is deliberately preserved. All placement and text rects are in those own pixels, not844x390. Anchor the entry group below the left harbour-summary card and scale it uniformly with the HUD.

Three text-free tight RGBA3x sprites: cream v2-s14-button, painted v2-s14-restaurant-icon, orange v2-s14-badge. Separate live labels: Mira's and Service tonight. Hide the badge when no service is scheduled. Entry visible after restaurant introduction; this painting does not decide unlock logic.

Manifest gives hashes/sizes/provenance/slices L/B/R/T source pixels. Layout includes original background reference; don't import the full HUD painting as a runtime background. The frame and badge reuse accepted v2 bitmap art; the facade is new built-in ImageGen art. Mechanical trim and3x export are not a native3x-detail claim for reused bitmaps. Full generated facade and prompts retained in provenance.

Opened context-review,cuts-review,text-layout-review. Audit PASS3tightRGBA3x/2live-text rects; every pixel outside entry[x36,y276,w440,h146] matches original HUD. Art/mockup delivery only; runtime import/hitboxes/responsiveness/localization/lead acceptance remain Claude. No Assets/code/git.
