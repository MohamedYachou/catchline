# NET-015 replacement-net economy handoff

Codex 1 (Windows app) / net_systems. New default is3 usable nets total, comprising the fitted net plus two reserves. Successful net cycles reuse stock. Root owns all tear/cycle/minigame behavior and decides when to subtract one; this economy delegate never consumes nets.

## Delivery and contract

Changed only the assigned `GameData.cs`, `GameState.cs`, `VoyageInterfaceShop.cs`; new `Assets/Editor/NetEconomyChecks.cs`, this note and diary. No Unity/scratch/foreground/build/commit. All preexisting dirty work preserved. Exact pre-edit backups in `%TEMP%/Catchline-NET015-economy-backup` contain those three existing sources; root should remove that dedicated directory after verified integration.

`GameData.NetReplacementCost=80`, `GameData.NetInventoryCapacity=4`. `GameState.NetInventory=3` is the total usable count including any fitted net. `BuyNet()` validates stock0..3 and coins>=80, spends exactly80 and adds one; otherwise false without mutation. Like existing BuyBait, it embeds no harbour/current-mode/hull check. The UI exposes it only on compact-fisher Supplies at harbour. Root should use `NetInventory>0` to permit a cycle and subtract one only for a validated tear. Successful cycles leave stock alone. Zero stock does not block ordinary rod fishing.

SaveData keeps Version1. New saves write `HasNetInventory=true` plus `NetInventory`; load clamps explicit stock0..4. Legacy saves without the presence flag get default3; an explicitly saved exhausted0 remains0 through repeated save/load. No coin/hull migration. This separate presence bit avoids relying on Unity JsonUtility constructor/default-field behavior for absent fields.

Supplies product id `supplies/net` and purchase button `supplies/net/buy`. Existing Product family/icon-net, stock count,80coin price, rack-full/funds reasons; action saves only after successful BuyNet. Product estimate now counts actual base/upgrade/fuel/net items and includes the120logical footer. Omitting that footer from the estimate would clamp scroll too early during retained updates, despite final content sizing, so both were updated together.

## Authored verification

`Catchline.EditorTools.NetEconomyChecks.Run`: new default3; exact80purchase; insufficient/full rack no spend; zero-stock recovery; repeated purchases stop at4; invalid runtime stock/negativefunds rejection; domain independence from hull; all0..4save roundtrips; malformed negative/over-cap saved values clamped; old Version1 default3 and exhausted migrated0 retained; actual native Supplies control funds/cap/success; exact catalogue footer extent; shop purchase unavailable after switching to sea UI.

Source whitespace checks clean. Checks authored but not executed: no C# compilation/native UI/runtime or visual acceptance claimed. Root must mirror source and run hidden scratch checks alongside its updated captain-timing/worker80%/3–5fish tests. Provisional80price,4capacity and3trial/default stock require play feedback rather than a final economy claim.

## Separate delegated fixture adaptation

After economy delivery, lead separately assigned only `NetChoiceChecks.cs` and `CompactFisherChecks.cs` to match the new captain timing games. These now call root `NetHaulChecks.FinishCaptainSet(game)` after captain walking, expect3–5fish and assert active setting-game cancellation via root `NetGameSetting`. Soak test uses NetRemaining immediately after the final successful tap to avoid falsely assuming no simulation time elapsed on that completion tick. Safe-worker allocation fixture resets Rng to Random(0) immediately before actual haul; firstroll.726 is checked within(.2,.8), preserving the success-path fixture while root tests the independent20%tear branch. Root must supply helper/property and confirm its actual safe RNG condition. No runtime source changed by this adaptation.

Exact pre-adaptation fixture backups at `%TEMP%/Catchline-NET015-fixture-backup`; root removes after successful hidden regression. Other tests and root NetHaulChecks rewrite remain untouched. Source-only whitespace checks clean; no Unity execution by delegate.
