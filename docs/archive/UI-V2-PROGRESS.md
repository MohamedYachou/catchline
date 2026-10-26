# UI v2 progress

One line per screen against [UI-SYSTEM.md](UI-SYSTEM.md) and the concepts in `screens/ui-concept/`.
Native captures (TEST / no-save player, 1440x900 and 844x390) and concept comparisons live in
`screens/ui-v2/`; produce them with `docs/tools/uiv2-capture.ps1 -Screens <list>`.

| Screen | Status |
|---|---|
| Kit | Skin.cs tokens and components; 62 SVG sprites (build_ui_v2.py) and 99 generated illustrations, icons and portraits cut by cut_ui_v2.py; Lilita One added. |
| Voyage HUD | Done: status, ground slab with stat tiles, stow tag, crew rail (status words, bar only on a timed job), primary Head home, Crew / Ops tiles, de-overlapped speech bubbles, guide toast in the open water. Phone rail shows portraits only. |
| Operations | Done: four stage cards (number, status word, fish queue, Details), one recommendation with one primary, main hold slab, crew rail. Income tab, cost charts and efficiency ring retired. |
| Crew | Done: portrait, name, role, grade badge; fishers toggle gear and allowed bait, deckhands cycle a primary duty. Secondary duty is read-only until the game has one (TODO(BLUEPRINT)); grade stands in for the concept's speciality. |
| Harbour hub + shops | Done: hub slab, Market, Chandlery (item grid + selection slab), Supplies, Crew Office card roster with an empty state for the rowboat. |
| Chart | Done: illustration and pins kept; floating header, v2 pin cards, ground detail slab, contracts panel. |
| Departure | Done: "Ready to leave?" slab with fuel tile, bait rows, crew cards, nets line and Let's go. Travel is a v2 slab with a progress bar. |
| Sale result | Done: toast plus the v2 Market summary. |
| Title / pause | Done: title, reset modal, pause, settings (page switches), head-home confirmation. IMGUI menus removed. |
| Catch card | Done: catch card and net receipt as v2 slabs in the open water; Gemini card art retired. |
| Old modes removed | Done 2026-10-24: old capture harnesses, probes, trial launch flags and per-feature build scripts removed; one build (`Catchline/Build Game`) and two shortcuts (`docs/tools/install-shortcuts.ps1`). Legacy Box / Button / Bar calls draw the v2 kit. |
