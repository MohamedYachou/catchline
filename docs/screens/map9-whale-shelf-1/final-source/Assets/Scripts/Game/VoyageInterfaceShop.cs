using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEngine;

namespace Catchline.Game
{
    // Harbour hub and shop pages in the UI v2 system (docs/screens/ui-concept/chandlery.webp):
    // planks and rope, a header slab with the coin pill, a grid of item cards, the selected item in
    // a slab with the one primary Buy, and the five-tab bar at the bottom.
    public partial class VoyageGame
    {
        sealed class ShopItem
        {
            public string Id, Name, Description, Art, Fallback, Action, Reason;
            public int Price = -1;
            public bool Enabled, Owned;
            public Action Buy;
        }
        // The chart page still lays out a single scrolling catalogue.
        float catalogWidth, catalogY;
        Transform catalog;
        readonly List<ShopItem> shopItems = new();
        readonly Dictionary<HudTab, string> shopSelection = new();
        static readonly string[] TabIcons = { "v2-icon-market", "v2-icon-map", "v2-icon-crew", "v2-icon-gear", "v2-icon-supplies" };
        static string ShopTitle(HudTab t) => t switch { HudTab.Market => "Market", HudTab.HarbourMaster => "Chart", HudTab.CrewOffice => "Crew office", HudTab.Chandlery => "Chandlery", _ => "Supplies" };
        float TabBarHeight => compactInterface ? 64 : 96;

        // Shop products register here and are drawn together as one grid plus a selection slab.
        void Product(string id, string name, string description, string icon, string action, bool enabled, Action onBuy, string reason = null)
        {
            var price = Regex.Match(action, @"(\d[\d,]*)\s*coins");
            shopItems.Add(new ShopItem
            {
                Id = id, Name = name, Description = description, Art = id == "refit" ? HullArt() : ItemArt(id), Fallback = icon, Action = action, Enabled = enabled, Buy = onBuy,
                Reason = reason, Price = price.Success ? int.Parse(price.Groups[1].Value.Replace(",", "")) : -1,
                Owned = action == "Owned" || action == "Refitted" || action == "Trial boat aboard" || action == "Tank full"
            });
        }
        void FinishProducts() { }
        static string ItemArt(string id)
        {
            if (id.StartsWith("upgrade/")) return "v2-item-" + id.Substring(8).ToLowerInvariant();
            return id switch
            {
                "supplies/worms" or "supplies/worms-bulk" => "v2-item-worms", "supplies/squid" or "supplies/squid-bulk" => "v2-item-squid",
                "supplies/fuel" => "v2-item-fuel", "supplies/net" => "v2-item-net", "supplies/deep-net" => "v2-item-deep-net",
                "module/second-net" => "v2-item-netsystem", "refit" => "v2-item-skiff", _ => "v2-item-compact-fisher"
            };
        }
        // The boat on the refit card: its own illustration when one exists, else the nearest boat we have drawn (PS-15).
        string HullArt()
        {
            string own = "v2-item-hull" + State.Hull;
            return ArtLibrary.Get()?.UiTex(own) != null ? own : State.Hull >= 2 ? "v2-item-compact-fisher" : "v2-item-skiff";
        }
        // Card line: the first clause of the description, as short as the concept's "+50% hold space".
        static string Effect(string description)
        {
            int cut = description.Length;
            foreach (var mark in new[] { ". ", " ·", " /", " (", "; " }) { int i = description.IndexOf(mark, StringComparison.Ordinal); if (i > 8 && i < cut) cut = i; }
            return description.Substring(0, cut).TrimEnd('.', ' ');
        }

        void InterfaceHarbour()
        {
            if (panelOpen && hudTab == HudTab.HarbourMaster) { InterfaceNauticalChart(); return; }
            if (!panelOpen) { HarbourHub(); return; }
            coastalUi.Planks("shop/planks"); Block(new Rect(0, 0, iw, ih));
            float headH = compactInterface ? 56 : 80;
            var header = new Rect(Edge, Edge, iw - Edge * 2, headH);
            float pill = compactInterface ? 170 : 240;
            coastalUi.PageHeader("shop/header", header, ShopTitle(hudTab), GameData.HarbourName, () => panelOpen = false, null, "shop/close", pill + 24);
            coastalUi.Icon("shop/header/emblem", Rect.zero, null);
            coastalUi.PricePill("shop/coins", new Rect(header.xMax - pill - 12, header.y + (headH - (compactInterface ? 44 : 60)) / 2, pill, compactInterface ? 44 : 60), State.Coins);
            ShopTabs(true);
            var content = new Rect(Edge, header.yMax + 12, iw - Edge * 2, ih - header.yMax - 12 - TabBarHeight - 24);
            shopItems.Clear();
            switch (hudTab)
            {
                case HudTab.Market: MarketPage(content); return;
                case HudTab.CrewOffice: CrewOfficePage(content); return;
                case HudTab.Chandlery: InterfaceGear(); break;
                case HudTab.Supplies: content = SuppliesOptions(content); InterfaceSupplies(); break;
            }
            ItemGrid(content);
        }

        void ShopTabs(bool open)
        {
            var tabs = (HudTab[])Enum.GetValues(typeof(HudTab));
            float x = open ? Edge : Edge + HarbourLeftWidth + 16;
            var bar = new Rect(x, ih - Edge - TabBarHeight, iw - x - Edge, TabBarHeight);
            Block(bar);
            coastalUi.TabBar("shop/tabs", bar, tabs.Select(ShortTab).ToArray(), TabIcons, open ? Array.IndexOf(tabs, hudTab) : -1,
                i => OpenShop(tabs[i]), tabs.Select(t => "shop/tab/" + t).ToArray());
        }

        void ItemGrid(Rect area)
        {
            if (shopItems.Count == 0) return;
            float selH = compactInterface ? 76 : 120, gap = 12;
            var gridRect = new Rect(area.x, area.y, area.width, area.height - selH - gap);
            int cols = compactInterface ? 5 : 4;
            float cw = (gridRect.width - 12 - gap * (cols - 1)) / cols, ch = compactInterface ? Mathf.Min(150, gridRect.height) : Mathf.Min(300, gridRect.height);
            int rows = Mathf.CeilToInt(shopItems.Count / (float)cols);
            var content = coastalUi.Scroll("shop/grid/" + hudTab, gridRect, rows * (ch + gap) + 12);
            if (!shopSelection.TryGetValue(hudTab, out var chosen) || shopItems.All(i => i.Id != chosen))
                chosen = (shopItems.FirstOrDefault(i => i.Enabled && !i.Owned) ?? shopItems[0]).Id;
            shopSelection[hudTab] = chosen;
            for (int n = 0; n < shopItems.Count; n++)
            {
                var item = shopItems[n];
                var r = new Rect(6 + n % cols * (cw + gap), 8 + n / cols * (ch + gap), cw, ch);
                ItemCard(item, r, item.Id == chosen, content);
            }
            var selected = shopItems.First(i => i.Id == chosen);
            SelectionSlab(selected, new Rect(area.x, area.yMax - selH, area.width, selH));
        }

        void ItemCard(ShopItem item, Rect r, bool selected, Transform parent)
        {
            string id = item.Id;
            if (selected) coastalUi.Sliced(id + "/glow", new Rect(r.x - 4, r.y - 4, r.width + 8, r.height + 8), "v2-card-selected", parent);
            else coastalUi.Sliced(id + "/glow", Rect.zero, null, parent);
            var card = coastalUi.Card(id, r, Skin.Card.Ink, parent, compactInterface ? null : item.Name);
            coastalUi.HitArea(id + "/select", new Rect(0, 0, r.width, r.height), () => { shopSelection[hudTab] = id; audio?.Play(VoyageAudio.Cue.Select, .3f); }, card);
            coastalUi.Icon(id + "/tick", selected ? new Rect(r.width - 30, -10, 40, 40) : Rect.zero, "v2-badge-tick", card);
            bool locked = !item.Enabled && !item.Owned && item.Reason != null;
            float top = compactInterface ? 6 : Skin.HeaderBand + 8, priceH = compactInterface ? 34 : 48;
            float artH = r.height - top - priceH - (compactInterface ? 34 : 70) - (locked && !compactInterface ? 34 : 0);
            coastalUi.Icon(id + "/art", new Rect(12, top, r.width - 24, artH), item.Art, card, locked ? new Color(1, 1, 1, .6f) : (Color?)null, item.Fallback);
            float y = top + artH + 4;
            coastalUi.Text(id + "/effect", new Rect(10, y, r.width - 20, compactInterface ? 26 : 30), compactInterface ? item.Name : Effect(item.Description),
                compactInterface ? Skin.Type.Small : Skin.Type.Body, Skin.Ink, TextAnchor.MiddleCenter, card);
            y += compactInterface ? 26 : 32;
            if (locked && !compactInterface) { coastalUi.LockChip(id + "/lock", new Rect(10, y, r.width - 20, 30), Effect(item.Reason), card); y += 34; }
            else coastalUi.Sliced(id + "/lock", Rect.zero, null, card);
            var pr = new Rect(10, r.height - priceH - 10, r.width - 20, priceH);
            if (item.Owned) { coastalUi.Light(id + "/owned", pr, Skin.Status.Steady, card); coastalUi.SetText(id + "/owned/word", item.Action == "Tank full" ? "Full" : "Owned"); coastalUi.Sliced(id + "/price", Rect.zero, null, card); }
            else if (item.Price >= 0) { coastalUi.Sliced(id + "/owned", Rect.zero, null, card); coastalUi.PricePill(id + "/price", pr, item.Price, State.Coins >= item.Price, card); }
            else { coastalUi.Sliced(id + "/owned", Rect.zero, null, card); coastalUi.Sliced(id + "/price", pr, "v2-pill-cream", card); coastalUi.Text(id + "/price/label", new Rect(0, 0, pr.width, pr.height), item.Action, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, coastalUi.ElementRect(id + "/price")); }
            // Each product keeps its stable "<id>/buy" control: an invisible press of the same action.
            coastalUi.HiddenButton(id + "/buy", item.Enabled ? () => { item.Buy(); audio?.Play(VoyageAudio.Cue.Purchase, .6f); } : null, card);
        }

        void SelectionSlab(ShopItem item, Rect r)
        {
            var slab = coastalUi.Slab("shop/selection", r, null, true);
            float artW = compactInterface ? 80 : 150;
            coastalUi.Icon("shop/selection/art", new Rect(14, 8, artW, r.height - 16), item.Art, slab, null, item.Fallback);
            coastalUi.Sliced("shop/selection/rule", new Rect(artW + 24, 14, 2, r.height - 28), "v2-rule", slab);
            float bw = compactInterface ? 220 : 340, x = artW + 40, w = r.width - x - bw - 32;
            // A phone slab is short: the name takes a slimmer top band so the description gets two full lines.
            float split = compactInterface ? .36f : .45f;
            coastalUi.Text("shop/selection/name", new Rect(x, compactInterface ? 2 : 6, w, r.height * split), item.Name, compactInterface ? Skin.Type.Heading : Skin.Type.Display, Skin.Ink, TextAnchor.LowerLeft, slab);
            string line = item.Reason ?? item.Description;
            coastalUi.Text("shop/selection/line", compactInterface ? new Rect(x, r.height * split + 2, w, r.height * (1 - split) - 6) : new Rect(x, r.height * .45f + 8, w, r.height * .5f - 12), line, compactInterface ? Skin.Type.Small : Skin.Type.Body,
                item.Reason != null && !item.Enabled ? Skin.Bad : Skin.Teal, TextAnchor.UpperLeft, slab);
            float bh = compactInterface ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight + 8;
            string label = item.Owned ? item.Action : item.Price >= 0 ? $"{Verb(item.Action)} · {item.Price:N0}" : item.Action;
            coastalUi.Primary("shop/buy", new Rect(r.width - bw - 18, (r.height - bh) / 2 - 2, bw, bh), label,
                () => { item.Buy(); audio?.Play(VoyageAudio.Cue.Purchase, .6f); }, item.Price >= 0 ? "v2-icon-coin" : null, item.Enabled, slab);
        }
        static string Verb(string action) { int dot = action.IndexOfAny(new[] { '·', '/' }); return dot > 0 ? action.Substring(0, dot).Trim() : "Buy"; }

        Rect SuppliesOptions(Rect area)
        {
            float h = compactInterface ? 56 : 68;
            var slab = coastalUi.Slab("supplies/options", new Rect(area.x, area.y, area.width, h), null, false);
            float x = 16;
            if (IsNetFisher)
            {
                coastalUi.Text("supplies/net-loadout", new Rect(x, 0, 120, h), "Net", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, slab);
                coastalUi.PageSwitch("supplies/loadout", new Rect(x + 60, (h - 48) / 2, compactInterface ? 300 : 380, 48),
                    new[] { $"Shallow · {GameData.ShallowNetSoakSeconds:0}s", $"Deep · {State.DeepNetUses.Count} left" }, State.SelectedNet == NetKind.Deep ? 1 : 0,
                    i => SelectNetLoadout(i == 0 ? NetKind.Shallow : NetKind.Deep), new[] { "supplies/loadout/shallow", "supplies/loadout/deep" }, slab, new[] { true, State.DeepNetUses.Count > 0 });
                x += (compactInterface ? 300 : 380) + 84;
            }
            coastalUi.Text("supplies/free", new Rect(x, 0, area.width - x - 260, h), "Free scraps are always aboard.", Skin.Type.Body, Skin.Teal, TextAnchor.MiddleLeft, slab);
            coastalUi.Secondary("supplies/preference", new Rect(area.width - 250, (h - 48) / 2, 234, 48), State.UseSquid ? "Squid first · on" : "Squid first · off",
                () => { State.UseSquid = !State.UseSquid; SaveGame(); }, "v2-icon-squid", true, slab);
            return new Rect(area.x, area.y + h + 12, area.width, area.height - h - 12);
        }

        void MarketPage(Rect area)
        {
            State.UnseenSale = false;
            float topH = compactInterface ? 76 : 120, gap = 12;
            var top = coastalUi.Slab("market/summary", new Rect(area.x, area.y, area.width, topH), null, true);
            float bw = compactInterface ? 220 : 340, bh = compactInterface ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight + 8;
            coastalUi.Icon("market/crate", new Rect(16, 8, topH * 1.3f, topH - 16), "v2-icon-market", top);
            float x = topH * 1.3f + 30, w = area.width - x - bw - 40;
            if (State.UnsoldCatch.Count > 0)
            {
                var quote = State.QuoteSale(State.UnsoldCatch, 0);
                coastalUi.Text("market/haul", new Rect(x, 6, w, topH * .5f), $"{State.UnsoldCatch.Sum(f => f.Kg):0.0} kg ashore · {State.UnsoldCatch.Count} fish", compactInterface ? Skin.Type.Heading : Skin.Type.Display, Skin.Ink, TextAnchor.LowerLeft, top);
                coastalUi.Text("market/value", new Rect(x, topH * .5f + 6, w, topH * .4f), $"Worth {quote.Coins + quote.ContractCoins:N0} coins today, contracts included.", Skin.Type.Body, Skin.Teal, TextAnchor.UpperLeft, top);
                coastalUi.Primary("market/sell", new Rect(area.width - bw - 18, (topH - bh) / 2 - 2, bw, bh), "Sell haul", () => { SellHaul(); audio?.Play(VoyageAudio.Cue.Purchase, .6f); }, "v2-icon-coin", true, top);
            }
            else
            {
                coastalUi.Text("market/haul", new Rect(x, 6, area.width - x - 24, topH * .5f), State.LastSale == null ? "Your first good day's fishing" : "Catch sold. Boat ready.", compactInterface ? Skin.Type.Heading : Skin.Type.Display, Skin.Ink, TextAnchor.LowerLeft, top);
                coastalUi.Text("market/value", new Rect(x, topH * .5f + 6, area.width - x - 24, topH * .4f), State.LastSale == null ? "Bring fish home and sell them here." : $"Last haul: {State.LastSale.FishSold} fish · {State.LastSale.Coins + State.LastSale.ContractCoins:N0} coins.", Skin.Type.Body, Skin.Teal, TextAnchor.UpperLeft, top);
            }
            // Fish log: a card per species with today's price.
            var log = new Rect(area.x, area.y + topH + gap, area.width, area.height - topH - gap);
            int cols = compactInterface ? 6 : 5; float cw = (log.width - 12 - gap * (cols - 1)) / cols, ch = compactInterface ? 120 : 190;
            var content = coastalUi.Scroll("market/log", log, Mathf.Ceil(GameData.Fish.Length / (float)cols) * (ch + gap) + 12);
            for (int i = 0; i < GameData.Fish.Length; i++)
            {
                var f = GameData.Fish[i]; bool found = State.LogCount[(int)f.Species] > 0;
                var r = new Rect(6 + i % cols * (cw + gap), 8 + i / cols * (ch + gap), cw, ch);
                var card = coastalUi.Card("log/" + i, r, Skin.Card.Soft, content);
                coastalUi.Icon("log/" + i + "/fish", new Rect(10, 8, r.width - 20, ch * .42f), found ? FishPortrait(f.Species) : "fish-unknown", card, found ? (Color?)null : new Color(1, 1, 1, .5f), found ? FishPortrait(f.Species) : "fish-unknown");
                coastalUi.Text("log/" + i + "/name", new Rect(8, ch * .46f, r.width - 16, 28), found ? f.Name : "Undiscovered", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter, card);
                // A phone card has room for one line under the name: the market needs the price there, not the record.
                bool priceLine = compactInterface && found;
                coastalUi.Text("log/" + i + "/record", new Rect(8, ch * .46f + 28, r.width - 16, 22), priceLine ? $"{State.PricePerKg(f.Species):0.0} / kg" : found ? $"{State.LogCount[(int)f.Species]} caught · best {State.LogBest[(int)f.Species]:0.0} kg" : "Explore the grounds", priceLine ? Skin.Type.Heading : Skin.Type.Caption, priceLine ? Skin.Teal : Skin.InkSoft, TextAnchor.MiddleCenter, card);
                if (!compactInterface) coastalUi.Text("log/" + i + "/price", new Rect(8, ch - 40, r.width - 16, 30), $"{State.PricePerKg(f.Species):0.0} / kg", Skin.Type.Heading, Skin.Teal, TextAnchor.MiddleCenter, card);
            }
        }

        void CatalogHeading(string id, string title, string detail, float height = 76)
        {
            coastalUi.Label(id + "/title", new Rect(4, catalogY, catalogWidth - 8, 34), title, 26, null, TextAnchor.MiddleLeft, catalog);
            coastalUi.Label(id + "/detail", new Rect(4, catalogY + 35, catalogWidth - 8, height - 36), detail, 16, SeaInk, TextAnchor.UpperLeft, catalog);
            catalogY += height;
        }
        void InterfaceGear()
        {
            if (IsPrepFisher) Product("module/second-net", "Second net module",
                IsTier5 ? State.SecondNetActive ? "Fitted: two rods, two nets and two buoys. Switch at port to four rods and one net." : "Fitted: four rods, one net and two buoys. Switch at port to two rods and two nets." : State.SecondNetActive ? "Fitted: one rod and two independent nets. Switch off at port to restore three rods." : "Replace two rods with a second net. Buy once, then switch the module on or off at port.",
                "icon-net", State.SecondNetOwned ? State.SecondNetEnabled ? "Switch off · restore rods" : "Switch on / two nets" : "Buy / 2,000 coins",
                State.SecondNetOwned || State.Coins >= GameState.SecondNetModuleCost,
                () => { if (State.SecondNetOwned) ToggleSecondNetModule(); else BuySecondNetModule(); });
            if (State.Hull == 3) Product("refit/tier5", "Buoy fisher · Tier 5", "Six hired crew, two buoy stations, processing and engineering. Choose four rods + one net or two rods + two nets.", "icon-skiff", $"Refit / {GameState.Tier5Cost:N0} coins", State.CanRefitTier5, () => RefitTier5());
            foreach (var u in GameData.Upgrades.Where(u => u.Shop == "Chandlery")) InterfaceUpgrade(u);
            Product("refit", State.Hull > 0 ? State.HullDef.Name : "Skiff refit", State.Hull > 0 ? $"{State.CoolerCapacity:0.#} kg hold / {UsableRodCount} rods / {(SecondNetActive ? 2 : 1)} nets" : $"Bring home {GameData.SkiffFishGoal} fish in one trip. Best: {State.BestVoyageFish}.", "icon-skiff",
                State.Hull > 0 ? "Refitted" : $"Refit · {GameData.SkiffCost} coins", State.CanRefit, () => RefitSkiff(),
                State.Hull == 0 && State.BestVoyageFish >= GameData.SkiffFishGoal && State.Coins < GameData.SkiffCost ? CoinShortfall(GameData.SkiffCost) : null);
            if (State.Hull == 1) Product("refit/compact", "Compact fisher", "Tier 3 · 100 kg hold · three rods · stern net system. Your crew and owned upgrades transfer.", "icon-skiff",
                $"Refit · {GameState.CompactFisherCost:N0} coins", State.CanRefitCompact, () => RefitCompact(), State.CanRefitCompact ? null : CoinShortfall(GameState.CompactFisherCost));
            if (State.Hull == 2) Product("refit/prep", "Prep fisher", $"Deliver 100 kg in one voyage. Best: {State.BestVoyageKg:0.##} kg. 160 kg hold, four crew and prep table.", "icon-skiff",
                $"Refit / {GameState.PrepFisherCost:N0} coins", State.CanRefitPrep, () => RefitPrep());
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
            Product("supplies/worms", "Worms", $"{GameData.BaitPackSize} everyday hooks · {State.Bait} aboard", "icon-bait-worm", $"Buy · {GameData.BaitPackCost} coins", State.Coins >= GameData.BaitPackCost, () => { if (State.BuyBait()) SaveGame(); });
            Product("supplies/squid", "Squid bait", $"{GameData.SquidPackSize} hooks for larger fish · {State.Squid} aboard", "icon-squid", $"Buy · {GameData.SquidPackCost} coins", State.Coins >= GameData.SquidPackCost, () => { if (State.BuySquid()) SaveGame(); });
            Product("supplies/worms-bulk", "Worms · bulk box", $"{GameData.BaitBulkSize} hooks · better value for longer trips", "icon-bait-worm", $"Buy · {GameData.BaitBulkCost} coins", State.Coins >= GameData.BaitBulkCost, () => { if (State.BuyBait(true)) SaveGame(); });
            Product("supplies/squid-bulk", "Squid · bulk box", $"{GameData.SquidBulkSize} hooks · favour bigger specimens", "icon-squid", $"Buy · {GameData.SquidBulkCost} coins", State.Coins >= GameData.SquidBulkCost, () => { if (State.BuySquid(true)) SaveGame(); });
            int cost = State.FuelFillCost;
            foreach (var upgrade in GameData.Upgrades.Where(u => u.Shop == "Supplies")) InterfaceUpgrade(upgrade);
            if (State.Hull > 0) Product("supplies/fuel", "Outboard fuel", $"{State.FuelFraction:P0} aboard · {State.FuelCapacity:0} minute tank · return at 10%", "icon-fuel", cost > 0 ? $"Fill · {cost} coins" : "Tank full", cost > 0 && State.Coins >= cost, () => { if (State.BuyFuel()) SaveGame(); });
            if (IsNetFisher)
            {
                bool rackFull = State.NetInventory >= GameData.NetInventoryCapacity;
                string stock = $"{State.NetInventory}/{GameData.NetInventoryCapacity} usable nets aboard.";
                string reason = rackFull ? stock + " Net rack full." : State.Coins < GameData.NetReplacementCost ? stock + " " + CoinShortfall(GameData.NetReplacementCost) + "." : null;
                Product("supplies/net", "Replacement net", $"{State.NetCapacityKg:0}kg capacity. " + stock + " Successful cycles reuse a net. A tear uses one.", "icon-net",
                    rackFull ? "Net rack full" : $"Buy net · {GameData.NetReplacementCost} coins", !rackFull && State.Coins >= GameData.NetReplacementCost,
                    () => { if (State.BuyNet()) { Toast("Replacement net aboard."); SaveGame(); } }, reason);
            }
            InterfaceCrabPotProduct();
            if (IsNetFisher && State.TornNets > 0)
            {
                bool full = State.NetInventory >= GameData.NetInventoryCapacity;
                Product("supplies/mend", State.TornNets > 1 ? $"Mend a torn net · {State.TornNets} torn" : "Mend the torn net",
                    "Lace new twine over the hole and it goes back on the rack. Free, if your stitching holds.", "icon-net",
                    "Mend · free", !full, () => BeginMend(), full ? "Net rack full." : null);
            }
            if (IsNetFisher)
            {
                Product("supplies/deep-net", "Deep net · 3 uses", $"{State.DeepNetUses.Count}/{GameData.DeepNetRackCapacity} aboard. {State.NetCapacityKg:0}kg capacity. Fewer, larger local fish. Failure spends one use.", "icon-net",
                    $"Buy · {GameData.DeepNetCost} coins", State.Coins >= GameData.DeepNetCost && State.DeepNetUses.Count < GameData.DeepNetRackCapacity,
                    () => { if (State.BuyDeepNet()) { Toast("Deep net aboard — choose it below before sailing."); SaveGame(); } });
            }
        }
        void CrewOfficePage(Rect area)
        {
            var report = State.ReadRoster();
            float headH = compactInterface ? 52 : 64;
            var help = coastalUi.Slab("crew/heading", new Rect(area.x, area.y, area.width, headH), null, false);
            coastalUi.Text("crew/heading/title", new Rect(16, 0, area.width * .5f, headH), $"Crew · {report.Deployed}/{report.Berths} berths", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, help);
            coastalUi.Text("crew/heading/wages", new Rect(area.width * .5f, 0, area.width * .5f - 16, headH), $"Wages next departure: {report.Wages:N0} coins",
                Skin.Type.Body, Skin.Teal, TextAnchor.MiddleRight, help);
            var list = new Rect(area.x, area.y + headH + 12, area.width, area.height - headH - 12);
            if (report.Cards.Length == 0)
            {
                // The rowboat has no berths: say where crew comes from instead of an empty page.
                var empty = coastalUi.Slab("crew/empty", new Rect(list.x + list.width * .15f, list.y + 12, list.width * .7f, Mathf.Min(list.height - 24, compactInterface ? 150 : 200)), null, true);
                float ew = list.width * .7f, eh = Mathf.Min(list.height - 24, compactInterface ? 150 : 200), p = eh - 40;
                coastalUi.Portrait("crew/empty/portrait", new Rect(24, 20, p, p), "captain", empty);
                coastalUi.Text("crew/empty/title", new Rect(p + 48, 16, ew - p - 72, eh * .4f), "Just you and the oars", Skin.Type.Heading, Skin.Ink, TextAnchor.LowerLeft, empty);
                coastalUi.Text("crew/empty/body", new Rect(p + 48, eh * .4f + 22, ew - p - 72, eh * .6f - 40), "The rowboat has no berths. Refit to a skiff at the Chandlery and your first crew cards come aboard.", Skin.Type.Body, Skin.Teal, TextAnchor.UpperLeft, empty);
                return;
            }
            int cols = 3; float gap = 12, cw = (list.width - 12 - gap * (cols - 1)) / cols, ch = compactInterface ? 170 : 208;
            var content = coastalUi.Scroll("crew/roster", list, Mathf.Ceil(report.Cards.Length / (float)cols) * (ch + gap) + 12);
            for (int n = 0; n < report.Cards.Length; n++)
            {
                var row = report.Cards[n]; string id = "crew/roster/" + row.Id;
                var r = new Rect(6 + n % cols * (cw + gap), 8 + n / cols * (ch + gap), cw, ch);
                var card = coastalUi.Card(id, r, row.Deployed ? Skin.Card.Selected : Skin.Card.Soft, content);
                float p = compactInterface ? 56 : 72, x = p + 24, tw = cw - x - 12;
                coastalUi.Portrait(id + "/portrait", new Rect(12, 12, p, p), row.Name, card);
                coastalUi.Text(id + "/name", new Rect(x, 8, tw, 30), row.Name, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, card);
                coastalUi.Text(id + "/role", new Rect(x, 38, tw, 22), $"{row.Role} · {row.Rarity} · Lv {row.Level}", Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, card);
                coastalUi.Text(id + "/wage", new Rect(x, 60, tw, 22), $"{row.Wage} coins per voyage · {row.Xp:0} kg", Skin.Type.Caption, Skin.InkSoft, TextAnchor.MiddleLeft, card);
                float by = ch - (compactInterface ? 44 : 52) - 10, bh = compactInterface ? 44 : 52, half = (cw - 36) / 2;
                coastalUi.Text(id + "/ability", new Rect(12, p + 18, cw - 24, by - p - 22), row.Ability, Skin.Type.Small, Skin.Teal, TextAnchor.UpperLeft, card);
                string cardId = row.Id;
                bool canDeploy = row.Role != "Navigator" && (row.Deployed || report.Deployed < report.Berths);
                coastalUi.Secondary(id + "/deploy", new Rect(12, by, half, bh), row.Deployed ? "Stand down" : "Deploy", () => { DeployCard(cardId, !row.Deployed); MenuSound(); }, null, canDeploy, card);
                var owned = CardRoster.Find(State.Roster, row.Id);
                int wild = CardProgression.UpgradeWildcards(row.Rarity), coins = CardProgression.UpgradeCoins(row.Rarity, owned.Def.TierGranted);
                bool gold = row.Rarity == CardRarity.Gold;
                bool can = !gold && State.Wildcards[(int)owned.Def.Role] >= wild && State.Coins >= coins;
                coastalUi.CardButton(id + "/upgrade", new Rect(24 + half, by, half, bh), gold ? "Gold" : $"Upgrade · {coins:N0}", () => { if (UpgradeCard(cardId)) audio?.Play(VoyageAudio.Cue.Purchase, .6f); }, null, can, card);
            }
        }

        void InterfaceChart() => InterfaceNauticalChart();

        float HarbourLeftWidth => compactInterface ? 250 : 320;
        void HarbourHub()
        {
            // World stays visible: harbour slab and Set sail on the left, coins top right, tabs along the bottom.
            float w = HarbourLeftWidth;
            var r = new Rect(Edge, Edge, w, compactInterface ? 128 : 168);
            var slab = coastalUi.Slab("port/title", r, ""); Block(r);
            coastalUi.Icon("port/title/icon", new Rect(12, 9, 30, 30), "v2-icon-anchor", slab, Skin.Cream);
            coastalUi.Text("port/name", new Rect(48, 4, w - 60, Skin.HeaderBand), GameData.HarbourName.ToUpperInvariant(), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, slab);
            coastalUi.Text("port/voyage", new Rect(16, Skin.HeaderBand + 10, w - 32, 26), $"Voyage {State.Voyage} · {State.HullDef.Name}", Skin.Type.Small, Skin.InkSoft, TextAnchor.MiddleLeft, slab);
            coastalUi.Text("port/destination", new Rect(16, Skin.HeaderBand + 38, w - 32, 34), GameData.Spots[SelectedSpot].Name, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, slab);
            if (!compactInterface) coastalUi.Text("port/readiness", new Rect(16, Skin.HeaderBand + 74, w - 32, 40), SailBlocker() ?? "Boat ready · supplies aboard", Skin.Type.Body, Skin.Teal, TextAnchor.UpperLeft, slab);
            float bh = compactInterface ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight + 8;
            var sail = new Rect(Edge, ih - Edge - Mathf.Max(bh, TabBarHeight), w, bh);
            coastalUi.Primary("port/sail", sail, "Set sail", () => { RequestDeparture(); audio?.Play(VoyageAudio.Cue.Select, .45f); }, "v2-icon-anchor", State.UnsoldCatch.Count == 0); Block(sail);
            float pill = compactInterface ? 170 : 220;
            coastalUi.PricePill("port/coins", new Rect(iw - Edge - pill - 64, Edge, pill, compactInterface ? 48 : 60), State.Coins); Block(new Rect(iw - Edge - pill - 64, Edge, pill, 60));
            var pause = new Rect(iw - Edge - 56, Edge, 56, compactInterface ? 48 : 60);
            coastalUi.IconButton("port/pause", pause, "v2-icon-menu", null, () => paused = true, null, "icon-menu"); Block(pause);
            ShopTabs(false);
            coastalUi.BubbleTop = Edge + 72; coastalUi.BubbleLeft = Edge + w + 12; coastalUi.BubbleBottom = sail.y;
            foreach (var (anchor, tab) in Shops)
            {
                HudTab chosen = tab;
                // A building hidden behind the port slab or the bottom row gets no bubble: clamped into the open water
                // it would point at nothing, and the tab bar already opens that shop.
                var v = Cam.WorldToViewportPoint(anchor.position);
                float bx = v.x * iw, by = (1 - v.y) * ih;
                if (v.z <= 0 || bx < coastalUi.BubbleLeft - 8 || bx > iw - 8 || by > sail.y) continue;
                InterfaceBubble("building/" + tab, anchor.position, ShortTab(tab), TabIcons[(int)tab], () => OpenShop(chosen));
            }
        }
    }
}
