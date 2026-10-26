# Catchline continuation report — 2026-10-15

Codex recovered both night plans and took over gameplay/design. A GPT-6.1 Sol medium subagent completed the interrupted 2D/3D asset queue.

## Playable changes

- Skiff refit at the Chandlery: return with 16 fish, pay 1,500 coins. New hull, 5×3 deck, 40-fish hold, three rods, outboard and fuel. Returning fuel is reserved at launch; the first tank is included.
- Up to three hired crew: deckhands carry/bait; fishermen cast and strike autonomously with 55/70/85% accuracy by grade. Everyone remains on expiring contracts. Old saves still load.
- Gill net: Set net, rod-fish during its 60–90 s soak, then Haul net. Captain cranks the winch, producing a deck pile; crew carrying capacity becomes the bottleneck.
- Rigged captain/crew replace capsules with role outfits/hats and 11 clips. Big coolers and improved rods now show their purchased variants. Harbour/sea polish includes residents, moored boats, landmarks and the hill backdrop.

## Assets recovered and delivered

The queue falsely marked failed usage-limit exits done; this is repaired. Task 05's 39 additions validated (83 total UI textures); task 06 supplies the crew; task 07 adds 31 world/upgrade models; task 08 supplies the day boat, nine stations and seven textures for later tiers. Blender sources, FBX exports, previews, reports and validation are retained. Day-boat gameplay and water material integration remain future work.

## Test it

1. Open **Catchline > Play Voyage** in the existing Unity project.
2. Return with 16 fish in one voyage and buy the skiff refit at the Chandlery.
3. Buy food/fuel at Supplies; hire fishermen and deckhands when available.
4. At sea, watch a fisherman work his rod. With the captain free, tap **Set net**; after soaking, tap **Haul net**. Carry the pile before fish flop away.
5. Return to harbour to sell/save, reload, and check hull/crew/fuel persist.

Automated checks run only on `Catchline-sim`. `docs/tools/check.ps1` accepts `-Method Catchline.EditorTools.SkiffChecks.Run` (refit/save/rig/fuel/upgrade checks), `-Method Catchline.EditorTools.SkiffChecks.Automation` (roles/net/backlog/contracts), or its default 30-voyage sim. All passed in Unity 6000.3.25f1.

Latest seed 7 run: skiff at voyage 28; trips 28–30 earned 86/133/73 **gross** coins/min, with 40 fish each and durations 6.0/6.0/5.3 min. Late rowboat trips were around 30–54 gross/min. Two fish flopped away in the first net/crew trip. These are one seed's observations, not a guarantee across all crew boards.

## Remaining work

Claude's C section (contract variety, rivals, daily gift, sea events) and D1–D5 (precise HUD/title/feedback/portraits/chart integration) remain. UI05 is imported but those layouts are not yet wired. More balance seeds and longer-voyage pacing need tuning. There is no blocking product decision needed to continue.

Screenshots in `docs/screens/` cover harbour, five seas, skiff, net and desktop/phone landscape framing. These are scene renders; Unity's IMGUI overlays and interactive shop/title flows still need native play review. The existing unrelated render-pipeline setting edits were left unstaged.

Continue at Claude plan **C1**. Detailed state and paths: `docs/CONTINUATION.md`; the asset queue05–08 is complete.
