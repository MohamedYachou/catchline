# Outer coast chart art

Codex 2 (WSL CLI) — OUTER-COAST-CHART-ART-1, 2026-10-26.

Delivery: `Assets/Resources/Charts/outer-coast.png`, 1672 × 941 RGB PNG. New painterly chart inherits Gull coast's high three-quarter miniature islands, faceted warm granite, white surf, turquoise shallows, deeper blue sea and soft cloud corners. No labels, pins or UI are baked into the delivered painting.

`review.png` places the unchanged Gull reference beside the annotated Outer chart, each at full original size below a 64 px evidence heading. `annotated.png` is the separate full-size Outer evidence. Circles mark the seven exact brief coordinates; yellow outlines mark the top/bottom quiet bands and approximate card areas. These annotations are evidence only.

| Ground | Normalized pin | Visual check |
|---|---|---|
| Kelp forest | .216, .278 | Point within green kelp bay beside compact rocky shore |
| Seal skerries | .400, .240 | Point at low seal-bearing granite skerries |
| Lighthouse rock | .660, .240 | Point on the lone island below white/red tower |
| Whale shelf | .060, .400 | Point on whale-tail shelf at left turquoise/deep-water edge |
| Seal cliffs | .240, .620 | Point at cliff formation with sea arch and resting seals |
| Wreck bank | .720, .560 | Point on sandbank just below rusty steamer hull |
| Home harbour | .483, .711 | Point at quay in smaller harbour town |

Landmark formation anchors, rather than the centre of every tower or arch opening, are aligned to the pin tips. The top and bottom areas remain predominantly sea/cloud, with broad deep-water lanes between landmarks. Card outlines are approximate asset-space evidence; actual UI layout and native import need lead acceptance.

## Source and reproduction

Generated with the built-in imagegen tool; the tool does not expose a reproducible model version or seed. `prompt-v1.txt` preserves the exact first prompt, with `gull-coast.png` supplied as style reference. `master-v1.png` is the first original generation. `prompt-v2.txt` preserves the targeted correction prompt, using the first master as edit reference. `master-v2.png` is the second geographic correction. `prompt-v3.txt` and selected `master-v3.png` retain the final local correction lowering the kelp-bay rock below the protected top band. All three iterations are retained as requested source history, not temporary backups.

Original tool outputs:
- v1: `/home/mo/.codex/generated_images/01a176ff-eb59-7962-ada0-e9d959032caf/exec-953a0236-47f2-4671-82c0-6539476f84a1.png`
- v2: `/home/mo/.codex/generated_images/01a176ff-eb59-7962-ada0-e9d959032caf/exec-a1a21f95-dd31-4736-9223-64ae804850f6.png`

Final local edit tool output: `/home/mo/.codex/generated_images/01a176ff-eb59-7962-ada0-e9d959032caf/exec-707bc831-93a1-4e70-a3d4-1e50aee2935e.png`.

Project-local master copies are the durable source. Export converts to RGB at delivery size and embeds all three prompts and provenance; no painting was added by the export script. Rebuild export/evidence with:

```sh
/home/mo/.venvs/catchline-ui/bin/python Art/Source/Charts/outer-coast/review_chart.py Art/Source/Charts/outer-coast/master-v3.png
```

`validation.json` records output/reference/review hashes, dimensions and exact point coordinates. `receipt.json` records the handoff files. The Gull reference hash matches the captured pre-work hash; reference and code were not edited. No git, Unity launch, player-save operation or meta creation was performed by this task. Native game acceptance is not claimed.

This is an ordinary extension of the incumbent art world. PRODUCT.md, DESIGN.md and existing design tokens stay authoritative and unchanged. No durable system change was introduced.

## Final review

Fresh finish review requested one material fix (the kelp rock entering the top quiet band). The local v3 correction resolved it; targeted reviewer verdict: **ship**, limited to that finding combined with the initial full asset review. Fresh read-only documenter confirmed source/report consistency and no required design-system change. Native acceptance remains untested.

Final output also passed the Impeccable embedded-prompt scan after adding its expected PNG text encoding with the exact v3 prompt. The pre-existing Gull reference was flagged by that scanner and deliberately left untouched under the brief. Reproduction should run `impeccable embed-prompt` on the exported PNG with the exact text of `prompt-v3.txt` after the export command above. This adds metadata only; reviewed image pixels stay unchanged.
