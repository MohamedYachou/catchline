using System;
using System.Collections.Generic;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Restaurant;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Service v2 (Mo 10-28): a night is about three minutes, walk-ins come all night, and the captain does only what
    // the player taps. Three headless nights on the starting kit with Mira and the captain:
    //   idle    – nobody taps: the kitchen never cooks, so the night must go badly (the player matters);
    //   tapper  – a bot that plays only through Command(), as a player's taps would;
    //   auto    – the captain helping by himself (bots and captures).
    public static class ServiceV2Checks
    {
        static void Check(bool pass, string label) { if (!pass) throw new Exception("Service v2 check failed: " + label); }

        static RestaurantSim Night(bool auto, int seed = 42)
        {
            var l = new RestaurantLayout(RestaurantLayout.WithServiceTables(RestaurantLayout.StartingKit()));
            var forecast = new RestaurantForecast(seed, 1, DayOfWeek.Friday, Weather.Fair, new[] { (Species.Pollock, 60f), (Species.Cod, 30f), (Species.Mackerel, 10f) }, l);
            forecast.Lock();
            var stock = new List<PortionStock> { new() { Species = Species.Pollock, Form = PreparedForm.Fillet, Count = 10 }, new() { Species = Species.Herring, Form = PreparedForm.Stock, Count = 5 } };
            var staff = new List<RestaurantStaff> { new() { Id = "mira", Job = Job.Reception, NativeJob = Job.Reception, Rarity = CardRarity.Gold, Tile = l.Door }, RestaurantStaff.Captain(l.Door) };
            return new RestaurantSim(seed, l, forecast, stock, staff) { CaptainHandsOn = true, CaptainAuto = auto, Breakdowns = false, GullPace = 1, FerryAt = 100 };
        }

        // What a quick player taps when the captain is free: two tables with plates waiting (a combo), else a station
        // for the oldest waiting dish, else a table to clear, else a free table for the first group at the door.
        static void Tap(RestaurantSim sim, bool plate = true)
        {
            // A done dish glows on its station: a quick player taps it about a second later (perfect), a forgetful one never does.
            if (plate) foreach (var c in sim.OnStations.Where(c => c.since >= 1).ToList()) sim.PlateNow(c.uid);
            // Upsell bubbles sell on the tap, no trip: a quick player takes every one.
            foreach (var g in sim.Groups.Where(g => g.Phase == GroupPhase.Eating && sim.Seconds < g.UpsellUntil).ToList()) sim.TakeUpsell(g.TableUid);
            if (sim.GullTable != 0 && sim.Seconds - sim.GullLandedAt >= 1) sim.ShooGull(sim.GullTable); // a second to notice it
            var captain = sim.Staff.First(s => s.Id == "captain");
            if (captain.Busy || sim.CaptainOrders.Count > 0) return;
            var ready = sim.Groups.Where(g => g.Phase == GroupPhase.Kitchen && g.Tickets.Any(t => t.Phase == TicketPhase.Ready)).Take(2).ToList();
            if (ready.Count > 0) { foreach (var g in ready) sim.Command(g.TableUid); return; }
            var thirsty = sim.Groups.FirstOrDefault(g => (g.Phase == GroupPhase.Drinks || g.Phase == GroupPhase.Coffee) && !g.Reserved);
            if (thirsty != null) { sim.Command(thirsty.TableUid); return; }
            var waiting = sim.Groups.Where(g => g.Phase == GroupPhase.Kitchen).SelectMany(g => g.Tickets).FirstOrDefault(t => t.Phase == TicketPhase.Waiting);
            if (waiting != null)
            {
                var station = sim.Layout.Active.FirstOrDefault(i => i.Id == RestaurantData.Get(waiting.Dish).Appliance);
                if (station != null && sim.Command(station.Uid)) return;
            }
            var clear = sim.Groups.FirstOrDefault(g => g.Phase == GroupPhase.Clearing && !g.Reserved);
            if (clear != null) { sim.Command(clear.TableUid); return; }
            var door = sim.Groups.FirstOrDefault(g => g.Phase == GroupPhase.Queue && !g.Reserved);
            if (door == null) return;
            var table = sim.Layout.Active.FirstOrDefault(i => RestaurantData.Get(i.Id).Seats >= door.Count && i.Id != ItemId.BarCounter
                && !sim.Groups.Any(g => g.TableUid == i.Uid && g.Phase != GroupPhase.Gone && g.Phase != GroupPhase.NotArrived && g.Phase != GroupPhase.Queue));
            if (table != null) sim.Command(table.Uid);
        }

        static string Line(string name, NightResult r) =>
            $"{name}: {r.Guests} guests ({r.WalkIns} walk-ins), served {r.Served}, left {r.Left}, {r.Stars:0.0} stars, {r.Coins} coins, {r.Combos} combos, {r.Upsells} upsells, gulls {r.GullsShooed} shooed {r.GullSteals} fed, {r.Perfects} perfect {r.Burnt} burnt, {r.Seconds:0} s";

        public static void Run()
        {
            var idle = Night(false); idle.RunToClose(400);
            var tapper = Night(false);
            var busy = new Dictionary<string, float>();
            while (!tapper.Finished && tapper.Seconds < 400)
            {
                Tap(tapper); tapper.Tick(.25f);
                foreach (var s in tapper.Staff) { string k = s.Id + ":" + s.Action; busy[k] = busy.TryGetValue(k, out var v) ? v + .25f : .25f; }
            }
            Debug.Log("[Catchline] SERVICE V2 time " + string.Join(", ", busy.OrderByDescending(x => x.Value).Select(x => $"{x.Key} {x.Value:0}s")));
            Debug.Log("[Catchline] SERVICE V2 tables " + string.Join(", ", tapper.Layout.Active.Where(i => RestaurantData.Get(i.Id).Seats > 0).Select(i => i.Id + "x" + RestaurantData.Get(i.Id).Seats))
                + " · groups " + string.Join(" ", tapper.Groups.Select(g => $"{g.Count}{(g.Id >= 1000000 ? "w" : "b")}:{g.Why ?? g.Phase.ToString()}")));
            var auto = Night(true); auto.RunToClose(400);
            var forgetful = Night(false);
            while (!forgetful.Finished && forgetful.Seconds < 400) { Tap(forgetful, false); forgetful.Tick(.25f); }
            // Night cards: every gadget, both dishes and the critic's table, played by the same quick player; and a rainy night.
            var carded = Night(false);
            carded.ColdBonus = 2; carded.CarryBonus = 1; carded.DoorBonus = 1.4f; carded.GullPace *= .5f; carded.CookBonus = .75f; carded.PriceBonus += 2; carded.IceCream = true; carded.CriticAt = 80;
            carded.Staff.First(s => s.Id == "captain").Boost *= 1.2f;
            while (!carded.Finished && carded.Seconds < 400) { Tap(carded); carded.Tick(.25f); }
            var rain = Night(false); rain.WalkInPace *= .6f; rain.GullPace = 0; rain.TipBonus *= 1.3f;
            while (!rain.Finished && rain.Seconds < 400) { Tap(rain); rain.Tick(.25f); }
            // Late in a run (the walk-in ramp at its +60%): the same player with the kept gadgets, and without them.
            RestaurantSim Late(bool gadgets)
            {
                var late = Night(false); late.WalkInPace = VoyageGame.WalkInRamp(11);
                if (gadgets) { late.ColdBonus = 2; late.CarryBonus = 1; late.DoorBonus = 1.4f; late.GullPace *= .5f; late.CookBonus = .75f; late.Staff.First(s => s.Id == "captain").Boost *= 1.2f; }
                while (!late.Finished && late.Seconds < 400) { Tap(late); late.Tick(.25f); }
                return late;
            }
            var lateKit = Late(true); var lateBare = Late(false);
            foreach (var (name, sim) in new[] { ("idle", idle), ("tapper", tapper), ("auto", auto), ("forgetful", forgetful), ("carded", carded), ("rain", rain), ("late+gadgets", lateKit), ("late bare", lateBare) }) Debug.Log("[Catchline] SERVICE V2 " + Line(name, sim.Result));

            var t = tapper.Result;
            Check(tapper.Layout.Active.Count(i => RestaurantData.Get(i.Id).Seats > 0) == 4, "the cafe opens with four tables (ten seats)");
            Check(tapper.Finished && t.Seconds <= 300, $"the night is about three minutes ({t.Seconds:0} s)");
            Check(t.WalkIns >= 10 && t.Guests >= 25, $"walk-ins all night ({t.WalkIns} of {t.Guests})");
            Check(t.Served >= t.Guests * .6f, $"a quick player serves most of the room ({t.Served} of {t.Guests})");
            Check(t.Combos >= 1, "two tables in one trip pays a combo");
            Check(Mathf.RoundToInt(t.PopularityGain) >= 1 && idle.Result.PopularityGain < 0, $"a good night grows popularity, a hungry room loses it ({t.PopularityGain:0.0} vs {idle.Result.PopularityGain:0.0})");
            Check(t.Upsells >= 5 && idle.Result.Upsells == 0, $"tables wave for another round and a tap sells it ({t.Upsells})");
            Check(t.GullsShooed >= 3 && t.GullSteals == 0 && auto.Result.GullSteals >= 1, $"gulls land on tables; a tap shoos them, ignored they steal ({t.GullsShooed} shooed, auto fed {auto.Result.GullSteals})");
            Check(tapper.FerryArrivedAt >= 100 && tapper.FerryGuests >= 8 && tapper.Groups.Count(g => g.Ferry && g.Paid) >= 2, $"the ferry moors mid-night and its passengers eat ({tapper.FerryGuests} off the ferry, {tapper.Groups.Count(g => g.Ferry && g.Paid)} tables paid)");
            Check(t.Perfects >= 5 && t.Burnt == 0, $"a done dish tapped in time plates perfect ({t.Perfects} perfect, {t.Burnt} burnt)");
            Check(forgetful.Result.Burnt >= 3 && forgetful.Result.Coins < t.Coins * .85f, $"left on the stove, fish burns and the night pays less ({forgetful.Result.Burnt} burnt, {forgetful.Result.Coins} vs {t.Coins} coins)");
            Check(tapper.Groups.Where(g => g.Id < 1000000).All(g => g.Why != "queue" && g.TableUid != 0), "every booking gets a table before walk-ins");
            Check(auto.Result.Burnt == 0, "the auto captain plates by itself (bots and captures never burn)");
            Check(idle.Result.Served < t.Served / 2, $"without taps the room goes hungry ({idle.Result.Served} vs {t.Served})");
            Check(auto.Result.Served >= t.Served / 2, $"the auto captain keeps bots and captures playable ({auto.Result.Served})");
            var critic = carded.Groups.FirstOrDefault(g => g.Critic);
            Check(critic != null && critic.Paid && carded.CriticStars >= 1, $"the critic's table: one guest dines and writes it up ({carded.CriticStars} stars)");
            int iceCreams = carded.Groups.Count(g => g.Upsell == Dish.IceCream && g.UpsellCoins > 0); // sold on the tap, no ticket
            Check(iceCreams >= 1, $"the ice cream card sells as another round ({iceCreams})");
            Check(carded.Result.Coins > t.Coins, $"kept cards make the same night pay more ({carded.Result.Coins} vs {t.Coins} coins)");
            Check(rain.Result.GullsShooed + rain.Result.GullSteals == 0 && rain.Result.WalkIns < t.WalkIns, $"a rainy night: fewer walk-ins, no gulls ({rain.Result.WalkIns} vs {t.WalkIns})");
            Check(NightCards.All.Length == 12 && NightCards.All.All(c => !string.IsNullOrEmpty(c.Effect) && c.Effect.Length <= 52), "twelve night cards, each effect fits the card's body");
            Check(lateKit.Result.Guests >= t.Guests + 4 && lateKit.Result.Served >= lateKit.Result.Guests * .55f, $"late in a run the harbour is busier and a kept kit keeps up ({lateKit.Result.Served} of {lateKit.Result.Guests} vs {t.Guests} early)");
            Check(lateBare.Result.Coins < lateKit.Result.Coins, $"the kept gadgets pay in the late rush ({lateBare.Result.Coins} vs {lateKit.Result.Coins} coins)");
            Debug.Log("[Catchline] SERVICE V2 CHECKS PASSED");
        }
    }
}
