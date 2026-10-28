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
            return new RestaurantSim(seed, l, forecast, stock, staff) { CaptainHandsOn = true, CaptainAuto = auto, Breakdowns = false, GullPace = 1 };
        }

        // What a quick player taps when the captain is free: two tables with plates waiting (a combo), else a station
        // for the oldest waiting dish, else a table to clear, else a free table for the first group at the door.
        static void Tap(RestaurantSim sim)
        {
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
            $"{name}: {r.Guests} guests ({r.WalkIns} walk-ins), served {r.Served}, left {r.Left}, {r.Stars:0.0} stars, {r.Coins} coins, {r.Combos} combos, {r.Upsells} upsells, gulls {r.GullsShooed} shooed {r.GullSteals} fed, {r.Seconds:0} s";

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
            foreach (var (name, sim) in new[] { ("idle", idle), ("tapper", tapper), ("auto", auto) }) Debug.Log("[Catchline] SERVICE V2 " + Line(name, sim.Result));

            var t = tapper.Result;
            Check(tapper.Layout.Active.Count(i => RestaurantData.Get(i.Id).Seats > 0) == 4, "the cafe opens with four tables (ten seats)");
            Check(tapper.Finished && t.Seconds <= 300, $"the night is about three minutes ({t.Seconds:0} s)");
            Check(t.WalkIns >= 10 && t.Guests >= 25, $"walk-ins all night ({t.WalkIns} of {t.Guests})");
            Check(t.Served >= t.Guests * .6f, $"a quick player serves most of the room ({t.Served} of {t.Guests})");
            Check(t.Combos >= 1, "two tables in one trip pays a combo");
            Check(t.Upsells >= 5 && idle.Result.Upsells == 0, $"tables wave for another round and a tap sells it ({t.Upsells})");
            Check(t.GullsShooed >= 3 && t.GullSteals == 0 && auto.Result.GullSteals >= 1, $"gulls land on tables; a tap shoos them, ignored they steal ({t.GullsShooed} shooed, auto fed {auto.Result.GullSteals})");
            Check(idle.Result.Served < t.Served / 2, $"without taps the room goes hungry ({idle.Result.Served} vs {t.Served})");
            Check(auto.Result.Served >= t.Served / 2, $"the auto captain keeps bots and captures playable ({auto.Result.Served})");
            Debug.Log("[Catchline] SERVICE V2 CHECKS PASSED");
        }
    }
}
