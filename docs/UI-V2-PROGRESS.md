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
| Harbour hub + shops | Not started. |
| Chart | Not started. |
| Departure | Not started. |
| Sale result | Not started. |
| Title / pause | Not started. |
| Catch card | Not started. |
| Old skins removed | Not started; legacy Box / Button / Bar calls already draw the v2 kit. |
