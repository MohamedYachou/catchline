using System;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        float catalogWidth;
        Transform catalog;
        int catalogItem;
        float catalogY;
        void InterfaceHarbour()
        {
            if (panelOpen && hudTab == HudTab.HarbourMaster) { InterfaceNauticalChart(); return; }
            float left = Mathf.Clamp(iw * .24f, 220, 280);
            coastalUi.Box("port/title", new Rect(18, 18, left - 34, 90), "chip-dark"); Block(new Rect(18, 18, left - 34, 90));
            coastalUi.Label("port/name", new Rect(34, 26, left - 66, 34), "Gull Harbour", 25, Palette.Cream);
            coastalUi.Label("port/voyage", new Rect(34, 65, left - 66, 24), $"Voyage {State.Voyage} · {State.HullDef.Name}", 15, Palette.Hex("A9D7D4"));
            IButton("port/pause", new Rect(18, 120, 54, 48), "II", () => paused = true, false);
            float footerY = ih - 156;
            coastalUi.Box("port/departure", new Rect(18, footerY, left - 34, 138)); Block(new Rect(18, footerY, left - 34, 138));
            coastalUi.Label("port/destination", new Rect(32, footerY + 7, left - 62, 32), GameData.Spots[SelectedSpot].Name, 19);
            coastalUi.Label("port/readiness", new Rect(32, footerY + 39, left - 62, 24), SailBlocker() ?? "Boat ready · supplies aboard", 14, SeaInk);
            IButton("port/sail", new Rect(30, footerY + 71, left - 58, 54), "Set sail", RequestDeparture, true, State.UnsoldCatch.Count == 0);
            if (!panelOpen)
            {
                InterfaceCoins();
                IButton("port/open", new Rect(iw - 238, 86, 220, 52), "Visit harbour shops", () => panelOpen = true);
                foreach (var (anchor, tab) in Shops)
                {
                    HudTab chosen = tab;
                    InterfaceBubble("building/" + tab, anchor.position, ShortTab(tab), ShopIcon(tab), () => OpenShop(chosen));
                }
                return;
            }
            var shell = new Rect(left, 18, iw - left - 18, ih - 36);
            coastalUi.Box("shop/shell", shell); Block(shell);
            float nav = compactInterface ? 126 : 142;
            coastalUi.Label("shop/brand", new Rect(left + 18, 32, nav - 24, 36), "Shops", 25);
            var tabs = (HudTab[])Enum.GetValues(typeof(HudTab));
            for (int i = 0; i < tabs.Length; i++)
            {
                HudTab tab = tabs[i]; float y = 91 + i * (compactInterface ? 59 : 72);
                coastalUi.Button("shop/tab/" + tab, new Rect(left + 12, y, nav - 16, compactInterface ? 56 : 64), "", () => OpenShop(tab), hudTab == tab ? "card-selected" : "button-tab-off-normal");
                coastalUi.Art("shop/tab/" + tab + "/icon", new Rect(left + 20, y + 12, 26, 28), ShopIcon(tab));
                coastalUi.Label("shop/tab/" + tab + "/name", new Rect(left + 51, y + 4, nav - 60, compactInterface ? 43 : 54), ShortTab(tab), 16, Palette.HullNavy);
            }
            float contentX = left + nav + 18, contentW = iw - contentX - 38;
            coastalUi.Art("shop/header", new Rect(contentX, 31, contentW - 176, compactInterface ? 64 : 88), ShopHeader(hudTab));
            coastalUi.Art("shop/coin", new Rect(iw - 186, 42, 26, 26), "icon-coin");
            coastalUi.Label("shop/balance", new Rect(iw - 151, 35, 73, 40), State.Coins.ToString("N0"), 23);
            IButton("shop/close", new Rect(iw - 74, 32, 38, 44), "X", () => panelOpen = false, false);
            float headerBottom = compactInterface ? 112 : 142;
            string caption = hudTab switch
            {
                HudTab.Market => State.UnsoldCatch.Count > 0 ? "Your catch, ready for the morning market." : "Fresh fish, fair prices. Every catch counts.",
                HudTab.Chandlery => "Good gear. Longer trips. A boat that grows with you.",
                HudTab.Supplies => "Stock the boat before you cast off.",
                HudTab.CrewOffice => "A helping hand for your next few voyages.",
                _ => "Find your next fishing ground and take a harbour contract."
            };
            coastalUi.Label("shop/intro", new Rect(contentX + 2, headerBottom - 14, contentW - 4, 35), caption, 17, SeaInk);
            float top = headerBottom + 34, height = ih - top - 36;
            int count = hudTab switch { HudTab.Supplies => 4 + GameData.Upgrades.Count(u => u.Shop == "Supplies") + (State.Hull > 0 ? 1 : 0) + (IsNetFisher ? 2 : 0), HudTab.Chandlery => 7, HudTab.CrewOffice => State.CrewCount + State.Board.Count + 1, _ => 14 };
            float estimatedHeight = hudTab == HudTab.Market ? 340 + GameData.Fish.Length * 88 : hudTab == HudTab.HarbourMaster ? 740 + State.Active.Count * 80 + State.Offers.Count * 100 : Mathf.Ceil(count / 2f) * 264 + (hudTab == HudTab.Supplies ? 120 + (IsNetFisher ? 100 : 0) : 0);
            catalog = coastalUi.Scroll("catalog/" + hudTab, new Rect(contentX, top, contentW, height), estimatedHeight);
            catalogWidth = contentW - 12; catalogItem = 0; catalogY = 0;
            switch (hudTab)
            {
                case HudTab.Market: InterfaceMarket(); break;
                case HudTab.HarbourMaster: InterfaceChart(); break;
                case HudTab.Chandlery: InterfaceGear(); break;
                case HudTab.Supplies: InterfaceSupplies(); break;
                case HudTab.CrewOffice: InterfaceCrew(); break;
            }
            // Fit scrolling to actual content, rather than a catalogue's estimated row count.
            var contentRect = (RectTransform)catalog;
            contentRect.sizeDelta = new Vector2(catalogWidth, Mathf.Max(height, catalogY + Mathf.Ceil(catalogItem / 2f) * 264));
        }
        void CatalogHeading(string id, string title, string detail, float height = 76)
        {
            coastalUi.Label(id + "/title", new Rect(4, catalogY, catalogWidth - 8, 34), title, 26, null, TextAnchor.MiddleLeft, catalog);
            coastalUi.Label(id + "/detail", new Rect(4, catalogY + 35, catalogWidth - 8, height - 36), detail, 16, SeaInk, TextAnchor.UpperLeft, catalog);
            catalogY += height;
        }
        void Product(string id, string name, string description, string icon, string action, bool enabled, Action onBuy, string reason = null)
        {
            float w = (catalogWidth - 16) / 2;
            float x = catalogItem % 2 * (w + 16), y = catalogY + catalogItem / 2 * 264;
            coastalUi.Box(id, new Rect(x, y, w, 248), "card-white", null, catalog);
            coastalUi.Art(id + "/art", new Rect(x + 16, y + 12, w - 32, 68), icon, catalog);
            coastalUi.Label(id + "/title", new Rect(x + 18, y + 83, w - 36, 30), name, 22, null, TextAnchor.MiddleLeft, catalog);
            coastalUi.Label(id + "/description", new Rect(x + 18, y + 115, w - 36, 64), reason ?? description, 15, SeaInk, TextAnchor.UpperLeft, catalog);
            coastalUi.Button(id + "/buy", new Rect(x + 14, y + 184, w - 28, 52), action, () => { onBuy(); audio?.Play(VoyageAudio.Cue.Purchase, .6f); },
                id == "module/second-net" ? "button-primary-pressed" : "button-primary-normal", enabled, catalog, 17);
            catalogItem++;
        }
        void FinishProducts() { catalogY += Mathf.Ceil(catalogItem / 2f) * 264; catalogItem = 0; }
        void InterfaceGear()
        {
            if (IsPrepFisher) Product("module/second-net", "Second net module",
                IsTier5 ? State.SecondNetActive ? "Fitted: two rods, two nets and two buoys. Switch at port to four rods and one net." : "Fitted: four rods, one net and two buoys. Switch at port to two rods and two nets." : State.SecondNetActive ? "Fitted: one rod and two independent nets. Switch off at port to restore three rods." : "Replace two rods with a second net. Buy once, then switch the module on or off at port.",
                "icon-net", State.SecondNetOwned ? State.SecondNetEnabled ? "Switch off / restore rods" : "Switch on / two nets" : "Buy / 2,000 coins",
                State.SecondNetOwned || State.Coins >= GameState.SecondNetModuleCost,
                () => { if (State.SecondNetOwned) ToggleSecondNetModule(); else BuySecondNetModule(); });
            if (State.Hull == 3) Product("refit/tier5", "Buoy fisher / Tier 5", "Six hired crew, two buoy stations, processing and engineering. Choose four rods + one net or two rods + two nets.", "icon-skiff", $"Refit / {GameState.Tier5Cost:N0} coins", State.CanRefitTier5, () => RefitTier5());
            if (SessionOnly) Product("trial/tier5", "Buoy fisher / Tier 5 trial", "Approved8.5x4.2m boat. Six crew plus captain; both equipment layouts are included.", "icon-skiff", IsTier5 ? "Trial boat aboard" : "Try Tier 5", !IsTier5, () => TrialTier5());
            foreach (var u in GameData.Upgrades.Where(u => u.Shop == "Chandlery")) InterfaceUpgrade(u);
            Product("refit", State.Hull > 0 ? State.HullDef.Name : "Skiff refit", State.Hull > 0 ? $"{State.CoolerCapacity:0.#} kg hold / {UsableRodCount} rods / {(SecondNetActive ? 2 : 1)} nets" : $"Bring home {GameData.SkiffFishGoal} fish in one trip. Best: {State.BestVoyageFish}.", "icon-skiff",
                State.Hull > 0 ? "Refitted" : $"Refit · {GameData.SkiffCost} coins", State.CanRefit, () => RefitSkiff(),
                State.Hull == 0 && State.BestVoyageFish >= GameData.SkiffFishGoal && State.Coins < GameData.SkiffCost ? CoinShortfall(GameData.SkiffCost) : null);
            if (State.Hull == 1) Product("refit/compact", "Compact fisher", "Tier3 ·100kg hold · three rods · stern net system. Your crew and owned upgrades transfer.", "icon-skiff",
                $"Refit · {GameState.CompactFisherCost:N0} coins", State.CanRefitCompact, () => RefitCompact(), State.CanRefitCompact ? null : CoinShortfall(GameState.CompactFisherCost));
            if (State.Hull == 2) Product("refit/prep", "Prep fisher", $"Deliver 100 kg in one voyage. Best: {State.BestVoyageKg:0.##} kg. 160 kg hold, four crew and prep table.", "icon-skiff",
                $"Refit / {GameState.PrepFisherCost:N0} coins", State.CanRefitPrep, () => RefitPrep());
            if (SessionOnly) Product("trial/netboat", "Compact fisher · trial", "Three crew · three rods · stern net. Trial includes fuel and a200coin crew budget. Prices are still being tuned.", "icon-skiff",
                State.Hull == 2 ? "Trial boat aboard" : "Try net boat", State.Hull != 2, () => TrialCompactFisher());
            if (SessionOnly) Product("trial/prepboat", "Prep fisher / Tier 4 trial", "Four crew berths, three rods and a stern net. Working two-person prep table, front storage and optional second net module.", "icon-skiff",
                IsPrepFisher ? "Trial boat aboard" : "Try prep boat", !IsPrepFisher, () => TrialPrepFisher());
        }
        void InterfaceUpgrade(UpgradeDef u)
        {
            if (!State.UpgradeAvailable(u.Id)) return;
            int cost = State.UpgradeCost(u.Id);
            bool owned = State.Has(u.Id), prerequisite = !u.Requires.HasValue || State.Has(u.Requires.Value);
            string reason = !owned && !prerequisite ? "Needs " + GameData.Upgrade(u.Requires.Value).Name : !owned && State.Coins < cost ? CoinShortfall(cost) : null;
            string icon = u.Id switch { UpgradeId.ThirdDeepLine => "icon-rod-carbon", UpgradeId.NetSystem => "icon-net", UpgradeId.LunchTin => "icon-fuel", UpgradeId.RodFibreglass => "icon-rod-fibreglass", UpgradeId.RodCarbon => "icon-rod-carbon", _ => "icon-" + u.Id.ToString().ToLowerInvariant() };
            Product("upgrade/" + u.Id, u.Name, State.UpgradeDescription(u.Id), icon, owned ? "Owned" : $"Buy · {cost:N0} coins", !owned && prerequisite && State.Coins >= cost,
                () => { if (State.TryBuy(u.Id)) { SyncUpgrades(); Toast("Bought: " + u.Name); SaveGame(); } }, reason);
        }
        void InterfaceSupplies()
        {
            if (IsNetFisher)
            {
                coastalUi.Label("supplies/net-loadout", new Rect(4, catalogY, catalogWidth - 8, 34), State.NetLoadoutLabel, 18, SeaInk, TextAnchor.MiddleLeft, catalog);
                coastalUi.Button("supplies/loadout/shallow", new Rect(0, catalogY + 38, catalogWidth * .48f, 48), $"Shallow · {GameData.ShallowNetSoakSeconds:0}s", () => SelectNetLoadout(NetKind.Shallow), State.SelectedNet == NetKind.Shallow ? "button-primary-normal" : "button-secondary-normal", true, catalog);
                coastalUi.Button("supplies/loadout/deep", new Rect(catalogWidth * .51f, catalogY + 38, catalogWidth * .48f, 48), $"Deep · {GameData.DeepNetSoakSeconds:0}s · 3 uses", () => SelectNetLoadout(NetKind.Deep), State.SelectedNet == NetKind.Deep ? "button-primary-normal" : "button-secondary-normal", State.DeepNetUses.Count > 0, catalog);
                catalogY += 100;
            }
            Product("supplies/worms", "Worms", $"{GameData.BaitPackSize} everyday hooks · {State.Bait} aboard", "icon-bait-worm", $"Buy · {GameData.BaitPackCost} coins", State.Coins >= GameData.BaitPackCost, () => { if (State.BuyBait()) SaveGame(); });
            Product("supplies/squid", "Squid bait", $"{GameData.SquidPackSize} hooks for larger fish · {State.Squid} aboard", "icon-squid", $"Buy · {GameData.SquidPackCost} coins", State.Coins >= GameData.SquidPackCost, () => { if (State.BuySquid()) SaveGame(); });
            Product("supplies/worms-bulk", "Worms · bulk box", $"{GameData.BaitBulkSize} hooks · better value for longer trips", "icon-bait-worm", $"Buy · {GameData.BaitBulkCost} coins", State.Coins >= GameData.BaitBulkCost, () => { if (State.BuyBait(true)) SaveGame(); });
            Product("supplies/squid-bulk", "Squid · bulk box", $"{GameData.SquidBulkSize} hooks · favour bigger specimens", "icon-squid", $"Buy · {GameData.SquidBulkCost} coins", State.Coins >= GameData.SquidBulkCost, () => { if (State.BuySquid(true)) SaveGame(); });
            int cost = State.FuelFillCost;
            foreach (var upgrade in GameData.Upgrades.Where(u => u.Shop == "Supplies")) InterfaceUpgrade(upgrade);
            if (State.Hull > 0) Product("supplies/fuel", "Outboard fuel", $"{State.FuelFraction:P0} aboard · {State.FuelCapacity:0} minute tank · return at10%", "icon-fuel", cost > 0 ? $"Fill · {cost} coins" : "Tank full", cost > 0 && State.Coins >= cost, () => { if (State.BuyFuel()) SaveGame(); });
            if (IsNetFisher)
            {
                bool rackFull = State.NetInventory >= GameData.NetInventoryCapacity;
                string stock = $"{State.NetInventory}/{GameData.NetInventoryCapacity} usable nets aboard.";
                string reason = rackFull ? stock + " Net rack full." : State.Coins < GameData.NetReplacementCost ? stock + " " + CoinShortfall(GameData.NetReplacementCost) + "." : null;
                Product("supplies/net", "Replacement net", $"{State.NetCapacityKg:0}kg capacity. " + stock + " Successful cycles reuse a net. A tear uses one.", "icon-net",
                    rackFull ? "Net rack full" : $"Buy net · {GameData.NetReplacementCost} coins", !rackFull && State.Coins >= GameData.NetReplacementCost,
                    () => { if (State.BuyNet()) { Toast("Replacement net aboard."); SaveGame(); } }, reason);
            }
            if (IsNetFisher)
            {
                Product("supplies/deep-net", "Deep net · 3 uses", $"{State.DeepNetUses.Count}/{GameData.DeepNetRackCapacity} aboard. {State.NetCapacityKg:0}kg capacity. Fewer, larger local fish. Failure spends one use.", "icon-net",
                    $"Buy · {GameData.DeepNetCost} coins", State.Coins >= GameData.DeepNetCost && State.DeepNetUses.Count < GameData.DeepNetRackCapacity,
                    () => { if (State.BuyDeepNet()) { Toast("Deep net aboard — choose it below before sailing."); SaveGame(); } });
            }
            FinishProducts();
            coastalUi.Label("supplies/free", new Rect(4, catalogY + 4, catalogWidth - 8, 50), "Free scraps are always aboard. No purchase needed.", 17, SeaInk, TextAnchor.MiddleLeft, catalog);
            coastalUi.Button("supplies/preference", new Rect(0, catalogY + 58, catalogWidth, 46), State.UseSquid ? "Squid first · On" : "Squid first · Off", () => { State.UseSquid = !State.UseSquid; SaveGame(); }, "button-secondary-normal", true, catalog);
            catalogY += 120;
        }
        void InterfaceCrew()
        {
            InterfaceRoster();
        }

        void InterfaceMarket()
        {
            State.UnseenSale = false;
            if (State.UnsoldCatch.Count > 0 || State.PendingXpKg > 0)
            {
                var quote = State.QuoteSale(State.UnsoldCatch, 0);
                CatalogHeading("market/haul", $"{State.UnsoldCatch.Sum(f => f.Kg):0.00} kg safely ashore", "Every fish earns coins. Matching catches also advance your contracts.", 85);
                coastalUi.Box("market/summary", new Rect(0, catalogY, catalogWidth, 90), "card-white", null, catalog);
                coastalUi.Art("market/crate", new Rect(12, catalogY + 9, 80, 70), "icon-fish", catalog);
                coastalUi.Label("market/value", new Rect(104, catalogY + 8, catalogWidth * .4f, 66), $"{quote.Coins + quote.ContractCoins} coins\nReady to collect", 22, null, TextAnchor.MiddleLeft, catalog);
                coastalUi.Button("market/sell", new Rect(catalogWidth - 180, catalogY + 20, 164, 48), "Sell haul", () => SellHaul(), "button-primary-normal", true, catalog);
                catalogY += 108;
            }
            else CatalogHeading("market/welcome", State.LastSale == null ? "Your first good day's fishing" : "Catch sold. Boat ready.", State.LastSale == null ? "Bring home three fish, sell them here, then choose your first improvement." : $"Last haul: {State.LastSale.FishSold} fish · {State.LastSale.Coins + State.LastSale.ContractCoins} coins earned.", 93);
            CatalogHeading("market/log", $"Fish log · {State.LogCount.Count(n => n > 0)}/{GameData.Fish.Length}", "Your records and today's market prices. Prices recover between voyages.", 82);
            for (int i = 0; i < GameData.Fish.Length; i++)
            {
                var f = GameData.Fish[i]; bool found = State.LogCount[(int)f.Species] > 0;
                coastalUi.Art("log/" + i + "/fish", new Rect(6, catalogY + 4, 114, 68), found ? FishPortrait(f.Species) : "fish-unknown", catalog);
                coastalUi.Label("log/" + i + "/name", new Rect(138, catalogY + 5, catalogWidth - 270, 29), found ? f.Name : "Undiscovered fish", 21, null, TextAnchor.MiddleLeft, catalog);
                coastalUi.Label("log/" + i + "/record", new Rect(138, catalogY + 36, catalogWidth - 270, 34), found ? $"{State.LogCount[(int)f.Species]} caught · best {State.LogBest[(int)f.Species]:0.00} kg" : "Explore the fishing grounds", 15, SeaInk, TextAnchor.MiddleLeft, catalog);
                coastalUi.Label("log/" + i + "/price", new Rect(catalogWidth - 122, catalogY + 10, 116, 56), $"{State.PricePerKg(f.Species):0.0} base/kg\n+ size bonus", 17, SeaInk, TextAnchor.MiddleRight, catalog);
                catalogY += 84;
            }
        }
        void InterfaceChart() => InterfaceNauticalChart();
    }
}
