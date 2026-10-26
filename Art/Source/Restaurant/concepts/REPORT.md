# RESTAURANT-CONCEPT-1 — concept review

Codex 2 (WSL CLI), 2026-10-26. **Concept delivery; Mo’s exterior choice is pending.** Start with [contact.png](contact.png), then [look-options.png](look-options.png). All output files are source concepts, not game assets or an implemented UI.

Built-in image generation produced the artwork; `layout.py` frames/resizes it, crops the isolated kit cells and adds clean Fredoka labels. It does not repaint scenes. Exact submitted prompts, including initial passes and targeted corrections, follow below and also live in [generation-prompts.json](generation-prompts.json). [generation-receipts.json](generation-receipts.json) preserves tool save receipts. Selected sources and earlier authoring iterations are in `generated/`; final review PNGs are at this directory’s top level. No API/CLI image fallback was used.

## What Mo chooses

1. Exterior01 whitewashed stone/blue shutters,02 teal timber/red roof, or03 brick/green awning. Progression uses01 until selected.
2. Whether the navy-enamel/ivory/honey furniture and warm-window/blue-dusk balance feels like the existing harbour. These are material/mood choices; stage progression and restaurant jobs come from the brief.
3. How much maritime decoration to keep at phone scale. Prefer big trophy/net/lantern silhouettes over the generated tiny masonry/plant details.

## New plan takes precedence when building

The brief initially requested8x5 and14x7 rooms. During this delivery Claude adopted the scale study: **52° orthographic, yaw0, five tiles deep, low cutaway walls, sideways expansion and a front-to-back pass between left kitchen/right guests**. The14x7 sheet remains the requested mood/furniture study and says so on the image. Do not trace its depth, full-height back wall, diagonal/horizontal pass or UI background into runtime. The small image was corrected toward the same frontal camera, but generative pictures do not certify identical projection or metre counts.

See [current restaurant plan](../../../../docs/plans/RESTAURANT.md), especially sections5/10, and the separate [scale study](../../../../docs/screens/restaurant-scale-1/README.md). Codex1 owns native scale evidence; this delivery makes no runtime/touch acceptance claim. Latest diary also records Codex1’s subsequent5-deep native study. No further room redesign or3D production was assigned here.

## Sheet review

Eight review PNGs are2400x1350 (seven A-D sheets and contact). Five phone PNGs are844x390; desktop Service is1440x900. Every final image was individually opened. Filename → exact prompt keys → choice → observed/style limits:

### [look-options.png](look-options.png)

Prompt: `look`.

Whitewashed stone/blue shutters; teal timber/red roof; harbour brick/green awning. Mo chooses 01/02/03; 01 is provisional.

Review: Matching miniature corner buildings, water-facing terrace and harbour palette. Material texture and props are richer than runtime; roof/window details are not mesh specifications.

### [exterior-stages.png](exterior-stages.png)

Prompt: `stages → stages_fix`.

Choose how strongly the inherited family building changes from closed house to full-frontage seafood house. Uses look01 provisionally.

Review: Five comparable views: closed, café, bistro, joined-house restaurant, string-lit seafood house. Window contents are illustrative, not an exact countable floorplan; silhouettes are comparable rather than registered CAD cameras.

### [exterior-night.png](exterior-night.png)

Prompt: `night → night_fix`.

Choose warm amber occupancy against blue dusk, keeping stage3 expansion.

Review: Joined neighbouring frontage, guests and queue present. Detail/noisy stonework should be simplified for actual harbour distance; the terrace railing is atmosphere rather than a walkability solution.

### [interior-1.png](interior-1.png)

Prompt: `interior1 → interior1_fix → interior1_camera`.

Review the first café’s sparse warmth, navy/ivory appliances, reception and cats.

Review: Two tables/two chairs each; separate fridge, soup kettle, stove, prep and coffee. Camera corrected to a front-down view. Faint grid is not an exact8x5 surveyed layout; horizontal pass explores the original brief, not the newer front-to-back runtime divider.

### [interior-4.png](interior-4.png)

Prompt: `interior4 → interior4_fix`.

Review the full furniture family, booth/trophy wall and kitchen/guest contrast.

Review: Five small indoor tables + booth + terrace table = seven table groups. Grill/fryer/oven/sink-rack/bar visible. Brief14x7 mood study clearly labelled; current plan14x5/low walls takes precedence for implementation. Rendered Mira corrected toward accepted identity; miniature faces remain approximations.

### [kit-sheet.png](kit-sheet.png)

Prompt: `kit`.

Choose the navy enamel/ivory/honey furniture family and distinct silhouette per job.

Review: All23 requested placeables plus one ship-clothes scale figure. Labels give proposed1x1/2x1 sizes and wall slots, with table4 corrected2x1. Plinths/chairs are illustrative: not measured collision or aisle footprints. Wall-net display has freestanding support in the concept; runtime can mount the net directly.

### [service-moment.png](service-moment.png)

Prompt: `service`.

Review whether the five restaurant jobs read through ship clothes and station positions.

Review: Fishers stove/grill, deckhand plates, hardhat engineer at smoking fryer, navigator coffee, Mira/queue and fish/coffee orders visible. Kitchen worktops/hands visible; waist-high pass can hide legs. No chef/waiter outfits. Crowd spacing and all foot routes unverified.

### [ui-1-arrange.png](ui-1-arrange.png)

Prompt: `ui-1-arrange → ui_arrange_fix → ui_arrange_grid`.

Review category drawer, shop cards and local placement confirmation.

Review: One green1x1 ghost under two-chair table; big rotate/cancel/check; clean table4 glyph/label2x1. Room is a mood background, not latest5-deep camera fit.44px targets, finger offset, undo, pathfinding, invalid-state copy and pan require interactive validation; drawer does not prove exact84px implementation.

### [ui-2-service.png](ui-2-service.png)

Prompt: `ui-2-service → ui_service_fix`.

Review phone hierarchy: clock/arrival curve, stocks, staff and Mira event.

Review: Four ship-clothes role portraits, repair cue and order bubbles. Reception is the in-world desk/event rather than a fifth phone rail slot; actual staff rail should allow Reception. Speed controls and some tabs are visibly smaller than44px; expand hit areas in implementation.

### [ui-3-mira-plan.png](ui-3-mira-plan.png)

Prompt: `ui-3-mira-plan`.

Review Mira-led forecast ranges, catch list and special request acceptance.

Review: Accepted Mira portrait language, dishes/ranges, fish/kg catch list and two special actions. Numbers illustrative; catch yields must be calculated from simulation. Plan card should be composited on the outbound voyage, not treated as a new location.

### [ui-4-prep.png](ui-4-prep.png)

Prompt: `ui-4-prep → ui_prep_fix → ui_prep_fillets`.

Review two-column catch/portions, forecast ticks and margin/captain’s-cut choice.

Review: Coffee removed from catch prep;10 grilled +8 soup +12 fillets =30 portions; fridge30/30 and market2fish cleaned. Controls deliberately enlarged. Fish art depicts finished dishes as category icons; boat prepares raw forms only. Forecast numerical range/market coin value and unavailable-recipe reason still need real data and native layout.

### [ui-5-closing.png](ui-5-closing.png)

Prompt: `ui-5-closing`.

Review tally, reviews, popularity, cats, crew of night and Sleep.

Review: 420 dishes +96 drinks +48 tips =564. Unsupported generated reward-unlock text replaced with neutral harbour reputation copy. Names, values and reviews are examples, not economy or crew decisions.

### [ui-service-desktop.png](ui-service-desktop.png)

Prompt: `ui-service-desktop → ui_desktop_fix`.

Review desktop spacing: stock left, event right, wider room, five-role rail.

Review: Distinct cook/serve/fix/coffee/reception portraits, rounded title, no chef outfits. Tiny world Mira cap still varies from accepted navy compass cap; reuse accepted Mira asset in production. Crew/world positions and view fit are concept art only.

### [contact.png](contact.png)

Prompt: `layout.py; seven A–D finals`.

Compare exterior01/02/03 and small-room warmth/full-room bustle in one glance.

Review: A-D only as brief requests; UI screens are separate full-size PNGs. Contact thumbnails are for selection; inspect full sheets for detail.

## Consistency and implementation limits

World concepts follow chunky bevelled miniatures, navy/ivory/honey/teal with amber evening light and no global outlines. UI deliberately uses the existing cream physical slabs, navy outlines/planks, orange primary buttons and rounded Fredoka-like lettering. Actual typeset sheet labels use the repository Fredoka font read-only; image-generated UI letters approximate it and must become real UI text. Do not ship raster mockup labels as the interactive interface.

Prompts requested existing ship clothes. Early accidental chef/officer substitutions were corrected in the selected service passes. Accepted ship rigs/portraits and Mira’s accepted navy compass cap remain authoritative; miniature generated faces/caps are not replacements. The kit’s role-scale sailor is reference only.

Kitchen tops and hands are visually readable. That does not prove visible feet or collision-free paths. Later production should use low walls and a front-to-back pass; test door-to-table/pass-to-appliance access, crew congestion, hidden kitchen floor, roof removal and tiny phone bubbles. The pictures provide no projected-tile measurements or44px hit-target certification. Stock numbers, prices, crew names, ratings and forecast counts are illustrative, independent examples between screens; they are not one saved day. Prep and closing local arithmetic was cleaned for readability, but only the simulation should determine yields/economy.

Physical kit bases are presentation plinths, not model geometry to export. Footprints are proposed design labels: appliances1x1; sink/pass/bar/table4/booth2x1; trophy/net/chart wall slots. The plan includes an additional steamer beyond the brief’s23-item kit; it was not silently added to the requested art scope.

## Evidence and reproduction

- [dimensions-and-hashes.json](dimensions-and-hashes.json): all14 final PNG dimensions/modes/SHA256 values.
- [opened-images.json](opened-images.json): human visual observations tied to those exact final hashes.
- [independent-audit.json](independent-audit.json): independent decode/dimension/hash/prompt-source checks.
- [delivery-receipt.json](delivery-receipt.json): file receipt for this source delivery.
- `layout.py`: repeatable framing/clean labels, using the existing `/home/mo/.venvs/catchline-ui/bin/python` Pillow environment. `write_report.py` regenerates this report/prompt appendix.

No Unity, git/commit, Assets writes, .meta/.cs, player save or watchdog operations. New source-art files only; no major original replacement, persistent backup or temporary backup. No subagents or outstanding image generation jobs. Art scope released after DONE in canonical comms.md; no further queue resumed.

## Exact submitted prompt history

The keys below are the literal tool submissions, retained for provenance rather than rewritten after the result. `ui-service-desktop` accidentally began with the literal `undefined`; its image references and explicit desktop spec still produced the selected composition, followed by the recorded identity/title correction. Clean final labels/totals are specified in `layout.py`, not misrepresented as imagegen output.

### `look`

Create a premium game concept art sheet, landscape 16:9, three equally wide side-by-side panels, cream background, NO text or letters (clean labels will be added afterwards). Same fixed orthographic 3/4 camera and same corner harbour restaurant building footprint in each panel: at the end of a short quay house row with terrace facing turquoise water, warm lanterns at blue dusk. Catchline miniature chunky bevelled 3D toy diorama style, broad clean colour blocks, no outlines, no noisy textures, no depth of field; navy #173F57, honey timber #C58B50, ivory #F3F0DC, teal #168F9F, orange #E36A35. Reference image 1 sets harbour shape/material language. Panel LEFT: whitewashed stone walls, blue shutters, navy slate pitched roof, little seafood restaurant sign silhouette, lanterns, three terrace tables. Panel CENTER: painted pale teal timber clapboard, warm terracotta red pitched roof, three terrace tables. Panel RIGHT: warm brick harbour house, green fabric awning, three terrace tables. All feel like cosy inherited family restaurants, small two-storey vernacular buildings, no skyscrapers; comparable scale, water terraces and same view; leave top 10% and bottom 9% empty cream for typeset headings.

### `kit`

Create a landscape16:9 game furniture concept kit contact sheet for Catchline cosy harbour restaurant. STRICT grid SIX columns by FOUR rows of equal-sized cells, generous cream gutters, on #F4EFE3 background. Every cell contains ONE complete isolated chunky bevelled miniature 3D object or furniture set at the SAME orthographic front-three-quarter camera50degrees down, same warm left lighting, soft contact shadows. No black outlines, no tiny texture detail, no text or letters. Navy paint #173F57, ivory #F3F0DC, honey timber #C58B50, muted steel #8FA6AC, teal #168F9F, restrained orange. Every item stands on a faint square1x1 tile or a double2x1 rectangular tile, tile visible, leave BOTTOM22% of EACH CELL blank cream for clean labels added later. No larger environmental scene. EXACT ITEMS left to right: ROW1 prep counter with chopping board1x1; stove with four broad burners1x1; grill with broad black ridges1x1; fryer with two square baskets1x1; round soup kettle on a squat base1x1; oven with front window1x1. ROW2 tall fridge1x1; sink with dish rack2x1; low pass counter with open hatch frame2x1; coffee machine with prominent cup1x1; glass drinks fridge1x1; bar counter with two stools2x1. ROW3 round table for two with two chairs1x1; square table for four with four chairs2x1; booth for six with two facing benches2x1; terrace table with blue parasol2x1; curved Mira reception desk1x1; trophy fish mount on small wall display1x1. ROW4 sparse net with big floats on wall display1x1; warm lantern on short post1x1; pot plant with big olive leaves1x1; framed nautical chart on display1x1; curved navy and orange jukebox1x1; ONE orange-beanie sailor in yellow ship overalls for size reference1x1. Kitchen machines have distinct silhouettes. Honour exactly6columns4rows. Reference image1 material style, image2 sailor proportions.

### `interior1`

Landscape16:9 high quality Catchline game art concept, chunky miniature 3D dollhouse, broad bevels, clean navy #173F57, ivory #F3F0DC, honey wood #C58B50, teal #168F9F accents, no outlines, no photoreal texture/no blur. Orthographic camera exactly from front looking down50degrees, front wall and roof completely removed, low cutaway side walls so everything is visible, kitchen back/left tiled floor, dining front/right honey plank floor; waist-high pass counter with an open serving hatch separating kitchen from guests, never obstruct appliances. Faint one-metre square floor tile grid, no tiny props. Quay entrance front-right, small Mira reception desk beside it, open back-left kitchen door to alley with two waiting cats. Warm window/lantern light balanced blue dusk outside. Cream margin top8% and bottom6%, NO text anywhere. Reference harbour and crew proportions. STAGE1 humble reopened family cafe, EXACTLY8tiles wide by5deep. ONLY two round dining tables with two chairs each, small stove, round soup kettle, prep counter, tall ivory fridge, chunky coffee machine; all readable separately. One navy-clothed ship crew member for scale, yellow oilskin overalls, no chef outfit. Sparse charming clean navigable cafe, generous clear aisles, blue shutters and whitewashed stone.

### `interior4`

Landscape16:9 high quality Catchline game art concept, chunky miniature 3D dollhouse, broad bevels, clean navy #173F57, ivory #F3F0DC, honey wood #C58B50, teal #168F9F accents, no outlines, no photoreal texture/no blur. Orthographic camera exactly from front looking down50degrees, front wall and roof completely removed, low cutaway side walls so everything is visible, kitchen back/left tiled floor, dining front/right honey plank floor; waist-high pass counter with an open serving hatch separating kitchen from guests, never obstruct appliances. Faint one-metre square floor tile grid, no tiny props. Quay entrance front-right, small Mira reception desk beside it, open back-left kitchen door to alley with two waiting cats. Warm window/lantern light balanced blue dusk outside. Cream margin top8% and bottom6%, NO text anywhere. Reference harbour and crew proportions. STAGE4 thriving seafood house, EXACTLY14tiles wide by7deep plus front waterside terrace strip. Larger kitchen with separate recognisable stove, grill, fryer, oven, sink/dish rack, prep counter, fridge and pass. Right side navy bar with three stools and coffee machine. Six indoor dining tables plus one back-right six-seat upholstered booth, and one terrace table with parasol, maximum eight tables total. Mounted trophy fish wall, little chart and maritime floats. One open central service aisle and clear routes to all tables. Whitewashed stone and blue shutters, same furniture language as tiny cafe; no people except Mira at reception for scale.

### `stages`

Premium Catchline harbour restaurant evolution concept sheet, landscape16:9, FIVE equal side-by-side panels on cream, NO TEXT. Reference image1 is look-options, use ONLY LEFT whitewashed stone/blue shutter/navy roof building as target, image2 harbour material style. SAME orthographic camera position, scale, quay corner and water side in every panel. Progressive stages0to4 LEFT TO RIGHT:0 closed family house, all shutters closed, faded hanging sign blank, crates stacked, no guests or terrace tables;1 reopened tiny cafe, open doorway showing exactly two two-seat tables INSIDE, outside bench and one chalkboard, NO terrace tables;2 bistro, navy fabric awning and exactly THREE terrace tables;3 full restaurant knocked through next adjacent matching house, widened ground floor windows and door frontage, bigger blank fish-shaped sign, warm lanterns and terrace tables;4 celebrated seafood house, entire doubled frontage open, string lights over terrace and prominent trophy fish OVER THE DOOR. Whitewashed stone/blue shutters across all stages, honey wood quay, navy iron, teal water, soft blue dusk/warm lighting. Chunky miniature3D, broad bevels and clean planes, no outlines, no photoreal noise. Building fully framed each panel; leave top10% and bottom12% empty for titles. Growth legible across the full row.

### `night`

Catchline game concept, landscape16:9, ONE orthographic3/4 view of stage3 family seafood RESTAURANT at NIGHT, cosy warm gold windows and lanterns against luminous navy blue dusk and calm turquoise harbour water. Use LEFT building of reference1 only: whitewashed stone, blue shutters, navy slate roofs; restaurant is knocked through into adjacent second whitewashed house, continuous doubled groundfloor frontage. Quay corner, terrace side facing water, THREE outdoor dining tables with seated guests in everyday harbour clothes, Mira smiling at entrance greeting two new guests, several more queue on quay clear of walking path. Ship clothes on staff: navy shirts/oilskins/work boots, no waiter costumes. Short string lights only as secondary accents, bigger navy blank sign with fish symbol above entrance, sturdy stone/wood quay and a few pots. Miniature chunky rounded bevelled3D, clean navy/ivory/honey timber/teal/orange colour blocks, no outlines/no blur/no bloom/no noisy textures. Night still bright enough to distinguish the house and guests. Leave top8% and bottom6% unlettered space. NO text or letters.

### `service`

Create a polished 16:9 landscape concept illustration for Catchline, a cosy chunky low-poly miniature harbour restaurant at busy evening service. Reference1 defines the stage4 dollhouse construction; make a slightly smaller stage3 version with NO roof or front wall, fixed front camera 50degrees down. Back/LEFT cool grey tiled kitchen, navy waist-high pass with ivory top, front/RIGHT honey wood dining floor. All stations/crew heads and hands visible. Warm lanterns, blue dusk quay outside, turquoise water.
Ship clothes ONLY, never chef hats, aprons, waiter uniforms. Reference2 crew: two fishers in navy knit caps and teal oilskins cook at SEPARATE stove and grill in backleft; a deckhand orange beanie/yellow oilskins carries two white fish plates at central pass; engineer yellow hardhat/grey oilskins kneels using wrench at smoking navy fryer, a small soft grey plume; navigator navy cap/teal coat operates a coffee machine at right bar. Mira at open front-right reception door greets a group: match reference3 exactly curly brown bob, navy cap small gold compass badge, navy coat cream collar/cuffs, cream jumper, binoculars. Keep every role spatially distinct. 5 tables/booth with guests, simple cream order bubbles above two tables with a single fish-dish silhouette and a coffee-cup silhouette, no text. 3 guests queue outside on quay; alley backdoor with 2 cats. Quiet grid1m, broad clear aisles. Saturated navy, ivory, orange accents, warm wood, solid faceted forms with soft bevel edges, ambient occlusion, NOT outlines or photorealism. No headers, no labels, no written text; room should fill frame with small clean border.

### `stages_fix`

Precise concept revision of reference1 five-stage restaurant progression sheet. Keep five same-camera orthographic harbour miniatures side by side on cream. Keep style, blue shutters/navy roofs, pier, water, little boat, camera, stage0 closed, stage1 cafe with bench/chalkboard, stage2 bistro with EXACTLY3terrace tables and navy awning. Critical change: in stage3 (fourth panel) and stage4 (last panel), the restaurant MUST visibly EXPAND into the neighbouring house on the RIGHT. Make a WIDER two-house combined frontage: second house on right is knocked through, with its own pitched roof and a large matching restaurant window and door in that right house. Two visible roof gables, broad groundfloor spanning bothhouses, expanded terrace. Stage3 has bigger fish sign and lanterns; stage4 spans FULLdoublefrontage with overhead stringlights, trophy fish above door and4terrace tables. Maintain exact same camera and same distance in all5panels, so stage3/4 occupy significantly more horizontal space than stage0-2 without shrinking. Leave adequate gutters between panels. No text, no panel labels, no outlines. Reference2 accepted harbour material style.

### `night_fix`

Precise building-continuity edit to reference1 night restaurant illustration. Keep ALL warm night ambience, guests, doorway welcome, terrace tables, boat, water, samecamera. Restaurant is STAGE3: it has expanded into next house on RIGHT, as FOURTH miniature in reference2. Enlarge that right annex into a proper two-storey neighbouring house joined at groundfloor, its own navy pitched roof and chimney, blue shutters upstairs and broad warm dining windows at streetlevel. Same ivory stone. Widen terrace to fit joinedhouse. Still cosy harbour footprint, two attached roof volumes, NOT mansion. Keep fish sign and navy awning, no stage4huge trophy or festoon strings (only walllanterns). Material palette/lighting unchanged. No written text or outline.

### `ui-1-arrange`

Design a finished UI CONCEPT MOCKUP for Catchline cosy harbour restaurant game. LANDSCAPE PHONE screen aspect 844:390 (2.164:1), no device frame, no letterbox. Match reference1 existing Catchline UI exactly: navy plank header #1E4D7B, physical warm cream slabs with dark navy 3px outlines, slight bevel/highlight and offset drop shadow, brass coins, single warm orange primary, rounded Fredoka typography. No modern thin sans font, no glass, no purple. Large legible concise English labels, generous44px target zones at output844width. Tiny miniature world uses reference2 warm low-poly restaurant, reference3 Mira identity curly brown hair navy compass cap navy coat cream collar. Distinct ship-clothes crew portraits, no chef uniforms. Coherent polished phone-first hierarchy. All numbers are illustrative concept data, not a shipped screenshot. DAYTIME ARRANGE SCREEN. Top narrow navy strip: back arrow, "Arrange", brass coin "2,450", Undo arrow. Main large dollhouse floorplan restaurant daylight occupying middle area, warm wood guest zone foreground/right, grey tile kitchen backleft, low navy pass. Overlay faint clear grid. Selected table ghost in green tile at foreground with rotate icon, green check, red cancel alongside. A clear unblocked route door-to-table. At right unobtrusive tag "Table for 2 · 1×1". Bottom84px cream drawer with categories Kitchen Guests (selected orange) Bar Decor Expand, and three product cards visible: "Table for 2" "120" "1×1", "Table for 4" "220" "1×1", "Booth" "380" "2×1". Draw small matching furniture pictures. Keep all cards and text inside frame.

### `ui-2-service`

Design a finished UI CONCEPT MOCKUP for Catchline cosy harbour restaurant game. LANDSCAPE PHONE screen aspect 844:390 (2.164:1), no device frame, no letterbox. Match reference1 existing Catchline UI exactly: navy plank header #1E4D7B, physical warm cream slabs with dark navy 3px outlines, slight bevel/highlight and offset drop shadow, brass coins, single warm orange primary, rounded Fredoka typography. No modern thin sans font, no glass, no purple. Large legible concise English labels, generous44px target zones at output844width. Tiny miniature world uses reference2 warm low-poly restaurant, reference3 Mira identity curly brown hair navy compass cap navy coat cream collar. Distinct ship-clothes crew portraits, no chef uniforms. Coherent polished phone-first hierarchy. All numbers are illustrative concept data, not a shipped screenshot. EVENING SERVICE SCREEN. Narrow navy top HUD "18:40" evening arrival curve with now marker, coin "320", star "42", Pause and1×2× speeds (1×selected). Large busy dollhouse warm interior mostly visible, kitchen upperleft behind pass and guests right, separate crew ship clothes. Small order bubble fish plate above table and coffee above another with patience arc. Small left cream stock cards "Fish 8" "Soup 5" "Coffee 12", Fish warning orange. Compact right event card with Mira portrait, "A late table?" and two buttons "Seat them" orange, "Not tonight" cream. Bottom cream portrait rail4crew: "Cook", "Serve", "Fix", "Coffee" role symbols pan/tray/wrench/cup with simple busy progress rings. Restaurant remains clearly visible; quiet transparent-free UI.

### `ui-3-mira-plan`

Design a finished UI CONCEPT MOCKUP for Catchline cosy harbour restaurant game. LANDSCAPE PHONE screen aspect 844:390 (2.164:1), no device frame, no letterbox. Match reference1 existing Catchline UI exactly: navy plank header #1E4D7B, physical warm cream slabs with dark navy 3px outlines, slight bevel/highlight and offset drop shadow, brass coins, single warm orange primary, rounded Fredoka typography. No modern thin sans font, no glass, no purple. Large legible concise English labels, generous44px target zones at output844width. Tiny miniature world uses reference2 warm low-poly restaurant, reference3 Mira identity curly brown hair navy compass cap navy coat cream collar. Distinct ship-clothes crew portraits, no chef uniforms. Coherent polished phone-first hierarchy. All numbers are illustrative concept data, not a shipped screenshot. TONIGHT PLANNING SCREEN, cream paperboard on navy plank background, no room behind needed. Top back and "Tonight at Mira’s". Left large approved Mira portrait, curly brown bob navy compass cap navy coat cream collar, friendly gesture (reference3). Right main cream board "FRIDAY · 18:00–23:00", "18–22 guests + walk-ins". Dish pictures/icons in row: "Grilled fish 8–10", "Fish soup 6–8", "Coffee 10–14". Below smaller catch list "Bring back: 8 mackerel · 3 kg pollock". Small separate special request cream card "A birthday table for four" with "Accept" and "Not tonight" choices. Bottomright big orange "Got it" primary. Clean readable at844x390.

### `ui-4-prep`

Design a finished UI CONCEPT MOCKUP for Catchline cosy harbour restaurant game. LANDSCAPE PHONE screen aspect 844:390 (2.164:1), no device frame, no letterbox. Match reference1 existing Catchline UI exactly: navy plank header #1E4D7B, physical warm cream slabs with dark navy 3px outlines, slight bevel/highlight and offset drop shadow, brass coins, single warm orange primary, rounded Fredoka typography. No modern thin sans font, no glass, no purple. Large legible concise English labels, generous44px target zones at output844width. Tiny miniature world uses reference2 warm low-poly restaurant, reference3 Mira identity curly brown hair navy compass cap navy coat cream collar. Distinct ship-clothes crew portraits, no chef uniforms. Coherent polished phone-first hierarchy. All numbers are illustrative concept data, not a shipped screenshot. PREPARE STOCK SCREEN, cream board on navy planks. Top back "Prepare for tonight", fridge capacity icon "18 / 24". Left card "Today’s catch" with fish pictures "Mackerel 12", "Pollock 5 kg". Right larger "Portions" card three rows with simple dish icons, name and minus/count/plus large controls: "Grilled fish 10", "Fish soup 8", "Coffee 12", small forecast tick below portions. Margin buttons "Tight" "+10%" orange selected "+20%". Footer figures "Restaurant: 18 portions" and "Market: 4 fish"; small "Captain’s cut" checkbox. Bottomright big orange "Prepare" primary. No clutter, no microtext. Art chunky like reference.

### `ui-5-closing`

Design a finished UI CONCEPT MOCKUP for Catchline cosy harbour restaurant game. LANDSCAPE PHONE screen aspect 844:390 (2.164:1), no device frame, no letterbox. Match reference1 existing Catchline UI exactly: navy plank header #1E4D7B, physical warm cream slabs with dark navy 3px outlines, slight bevel/highlight and offset drop shadow, brass coins, single warm orange primary, rounded Fredoka typography. No modern thin sans font, no glass, no purple. Large legible concise English labels, generous44px target zones at output844width. Tiny miniature world uses reference2 warm low-poly restaurant, reference3 Mira identity curly brown hair navy compass cap navy coat cream collar. Distinct ship-clothes crew portraits, no chef uniforms. Coherent polished phone-first hierarchy. All numbers are illustrative concept data, not a shipped screenshot. CLOSING REPORT SCREEN cream board navy planks. Top title "A good night on the quay" and small moon. Left numbers "22 served · 2 left", "Dishes 420", "Drinks 96", "Tips 48", bold coin "Tonight +564". Middle three short review cards with 5star/4star/4star and one brief line each: "Fish worth the wait." "Cosy, even in the rain." "More coffee, please!" Right popularity star progress "42 → 46". Bottomleft two cats beside leftovers icon "3 portions for the alley cats · value 18", small crew portrait orange beanie "Crew of the night · Jo". Mira portrait small and speech "Same time tomorrow?" Bottomright orange "Sleep" button. Clear readable hierarchy, fit844x390.

### `ui-service-desktop`

undefinedDESKTOP service HUD1440:900 aspect1.6:1, not phone. Main view a busy evening stage3 dollhouse restaurant at front50degree down, kitchen tiled backleft and serving pass, dining wood right/front, guests and shipclothes crew, warm lanterns. Top navy header with backarrow, "Mira’s · Evening service", arrivalcurve labelled18:00/20:00/23:00 now18:40, coin320, popularity42, Pause1×2×. Left cream stockcolumn "Tonight’s stock" Fish8 Soup5 Coffee12 and compact kitchen alert "Fryer needs repair" wrench. Right cream eventcolumn Mira portrait with "A late table?" "A party of four has arrived." orange "Seat them" cream "Not tonight". Room is central largest visual, orderbubbles fish/coffee and subtle patience arcs. Bottom cream crewrail shipclothes portraits roles "Cook" "Serve" "Fix" "Coffee" "Reception" with pan/tray/wrench/cup/desk symbols and progressrings. Spacious breathing room, no microtext, no other UI panels. This is desktop adaptation of phone service with more visible world, not oversized mobile screen.

### `ui_service_fix`

Precise identity and role correction to this Catchline service HUD mockup. Preserve exact composition, all legible English words, stocks/counts, orange/cream/navy UI and large room. Ship-clothes crew MUST have4different silhouettes, never uniform chef/waiter/naval costumes. In bottom crewrail: Cook portrait = man NAVY KNIT beanie TEAL oilskins; Serve portrait = orange knit beanie YELLOW oilskins deckhand; Fix portrait = yellow HARDHAT GREY oilskins engineer; Coffee portrait = navy knit cap TEAL coat navigator, no white officer cap. Keep corresponding pan/tray/wrench/cup symbols and clear labels. In kitchenworld the cook wears navy beanie+tealoveralls; platecarrier orangebeanie+yellowoveralls, no whitecap/navyuniform. Add yellowhardhat greyoveralls engineer kneeling at broken fryer beside a small ORANGE WRENCH warning badge. Mira alone retains navy compass peaked cap, curlybob and navycoat creamcollar at reception/event portrait. Absolutely no chef hats/aprons. Do not change any text or layout. This is an image edit, not a new differently arranged UI.

### `ui_desktop_fix`

Precise edit of reference1 desktop restaurant UI. KEEP exact layout, legible words/numbers, same scene, stock/event cards and4:2.5aspect. Correct ALL crew identities to reference2 ship-clothes, absolutely NO chef hat, NO aprons or waiter uniforms. Bottom rail5distinct portraits: Cook navy KNIT beanie TEAL oilskins (NOT whitechefhat); Serve orange beanie YELLOW oilskins deckhand (NOT Mira); Fix YELLOW HARDHAT and GREY oilskins (NOT orangebeanie); Coffee navy knitcap TEAL coat; Reception alone Mira curlybob navycompasscap navycoatcreamcollar. In world scene replace whitechefhat with navyknitcap and tealoveralls. All platecarriers orangebeanie yellowoilskins; have yellowhardhatgreyengineer at fryer. Mira alone at entrance keeps compasscap. Replace top title's thin serif with rounded Fredoka-like chunky letterforms, same wording "Mira’s · Evening service". Preserve everything else.

### `ui_arrange_fix`

Targeted correction of reference1 Catchline Arrange mockup. Preserve exact layout, style, readable texts/prices, drawer/header. SELECTED furniture must be a small round TABLE FOR TWO with EXACTLY TWO chairs, one each side, NOT four chairs. Its single green valid placement footprint is exactly ONE grid square with NO internal cross or subdivisions; consistent labelled1×1. Rotate/cancel/check buttons above selected ghost need visibly larger cream/red/green circles, each diameter100pixels on this1844pixel-wide source (44px on844width), separated by12pixels. Keep validdoor-to-table path clear. Else unchanged.

### `ui_prep_fix`

Revise this Catchline Prepare UI with exact same navy/cream/orange physical UI style and all existing labels/numbers. Mobile readability improvement: REMOVE the large Mira portrait at left (her portrait is already on planning screen); use space for two clean main columns, Today’s catch LEFT35%width and Portions RIGHT65%width. Main top and bottom bars unchanged. Make ALL minus/plus controls at least100×100sourcepixels on1844width (44px on844phone).3rows Grilledfish10/Fishsoup8/Coffee12, each large minus andplus, and UNDER EACH count a short thin forecast bar with a distinct gold vertical forecast tick. Preserve grilledfish/mackerel/soup/coffee artwork. Margin buttons Tight/+10%selected/+20%, fridge18/24, footerRestaurant18portions/Market4fish/Captaincut checkbox, bigorangePrepare. Side-by-side column layout, no large character blocking space, no addedtext.

### `interior1_fix`

Precise revision of reference1 small Stage1 interior. Keep samecamera, room, allmaterials, two tables with2chairs EACH, pass hatch, quayside door/reception, twoalleycats. There MUST be a SEPARATE soup-kettle station, not a pot sharing the stove. Add the standalone dark navy domed soup kettle on a low square navy heated pedestal from reference2 (row1fifth object), between tallfridge and stove. Shift fridgeleft/stoveright slightly to fit, without altering room footprint, keep stove/prep/coffee clear. Remove littlepot fromstove; stove burners visible. Fixed front-down50degree landscape dollhouse, faint1mgrid, no roof/frontwall. Only requestedchange, no new furniture or text.

### `interior4_fix`

Precise ONE-character identity correction to reference1 full Stage4 interior. Preserve every room/appliance/table/chair/material/camera exactly. Reception character at bottomright desk must be MIRA from reference2: curly brown bob, navy peakedcap with small GOLD COMPASS badge (no whitecap), navycoat with ivorycollar/cuffs, creamjumper, binoculars. Same chunky miniature scale as existingcharacter, standing behinddesk, friendlysmallwave. No other people added, no layoutchanges, no written text.

### `interior1_camera`

Use case: precise-object-edit. Image 1 edit target: small restaurant interior. Image 2 camera reference only: large restaurant. Keep ALL image1 furniture, two tables with exactly two chairs each, separate soup kettle BETWEEN fridge and stove, stove without pot, prep counter, coffee, low pass/hatch, cats, desk and quay. Correct only camera: front-centered yaw ZERO, about 52 degrees down, matching image2's frontal camera. Back wall must run horizontally, no left-to-right yaw. Small approximately 8x5 room stays small. Remove the unnecessary officer character from middle so floor grid reads. Keep chunky miniature ivory/blue/honey style, warm light, no outlines, no text. Do not copy large room furniture into small room.

### `ui_arrange_grid`

Use case: precise-object-edit. Edit target the supplied Arrange screenshot. Keep ALL layout, art, text, camera, controls and colors exactly. ONLY correct the green placement footprint: it must be ONE contiguous 1x1 tile underneath the round table and two chairs, with one luminous green perimeter and NO internal grid lines. The table purchase card correctly says 1x1. Tiny footprint glyphs under Table for2/Table for4 should be a single outlined square; Booth 2x1 should be exactly two adjacent outlined squares. Do not add subdivisions. Preserve everything else, including all exact words, prices, controls and two chairs.

### `ui_prep_fillets`

Use case: precise-object-edit. Edit target supplied Prepare for tonight phone UI. Keep exact composition, all controls, typography, colors, catch panel, totals and large buttons. ONLY correct third portion row: coffee is an always-available staple and is not prepped from the catch. Replace coffee cup illustration with a pan-fried white fish fillet on a small cream plate with lemon, and replace its text 'Coffee' with 'Fillets'. Keep row number 12, minus/plus buttons and gold forecast tick. No other changes. Preserve 844:390 landscape composition.

