using System;
using System.Collections.Generic;
using System.Linq;
using Catchline.Game.Restaurant;
using UnityEngine;
using SimStaff = Catchline.Game.Restaurant.RestaurantStaff;

namespace Catchline.Game
{
    // The restaurant day (docs/plans/RESTAURANT.md, Mo 10-26): Mira's plan before sailing, prep on arrival, the market
    // for the rest, the night's service, the closing card, then sleep. The screens are VoyageRestaurantUi.cs; this file
    // feeds them from the restaurant rules (Restaurant/*.cs) and moves the day along.
    public partial class VoyageGame
    {
        public enum DayPhase { Off, Plan, Out, Prep, Service, Closing }
        public DayPhase RestaurantPhase { get; private set; }
        // The new loop is on for every save; captures and old checks can switch it off.
        public bool RestaurantLoop = true;

        RestaurantState restaurantState;
        RestaurantLayout restaurantLayout;
        RestaurantForecast dayForecast;
        PrepPlan dayPrep;
        RestaurantSim night;
        int popularityBefore;
        int restaurantPopularity { get => State.RestaurantPopularity; set => State.RestaurantPopularity = value; }
        readonly Dictionary<string, float> staffLoad = new();

        RestaurantLayout Kitchen => restaurantLayout ??= new RestaurantLayout(restaurantState ??= RestaurantLayout.StartingKit());

        static readonly Dictionary<Dish, (string name, string art, string fallback)> DishLook = new()
        {
            [Dish.GrilledFish] = ("Grilled fish", "v2-dish-grilled-fish", "fish-mackerel"),
            [Dish.PanFish] = ("Fillets", "v2-dish-fillets", "fish-pollock"),
            [Dish.FishAndChips] = ("Fish & chips", "v2-dish-fish-and-chips", "icon-food"),
            [Dish.Soup] = ("Fish soup", "v2-dish-fish-soup", "icon-food"),
            [Dish.Platter] = ("Oven platter", "v2-dish-oven-platter", "icon-food"),
            [Dish.Crab] = ("Crab", "v2-dish-crab", "fish-crab"),
            [Dish.Calamari] = ("Calamari", "v2-dish-calamari", "icon-squid"),
            [Dish.Coffee] = ("Coffee", "v2-dish-coffee", "v2-icon-cup"),
        };
        static readonly Dictionary<PreparedForm, Dish> FormDish = new()
        {
            [PreparedForm.Whole] = Dish.GrilledFish, [PreparedForm.Fillet] = Dish.PanFish, [PreparedForm.Stock] = Dish.Soup,
            [PreparedForm.Platter] = Dish.Platter, [PreparedForm.Crab] = Dish.Crab, [PreparedForm.Squid] = Dish.Calamari,
        };
        // Guests write the reviews. Stand-in faces (deck portraits of people not on the night's staff) until the guest
        // portraits of RESTAURANT-MIRA-FISH-ART-1 D2 arrive.
        static readonly string[] GuestFaces = { "ana-deck", "bram-deck", "lise-deck", "olaf-deck", "tess-deck", "yusuf-deck" };
        static string FishArt(Species s) => "fish-" + s.ToString().ToLowerInvariant();
        static string FishName(Species s) => GameData.Get(s).Name.ToLowerInvariant();

        // ---- 1. Let's go: Mira's plan first ------------------------------------------------------------------------

        // Called where Let's go would sail; true when the plan card took over (its Got it sails).
        bool RestaurantPlanBeforeSail()
        {
            if (!RestaurantLoop || RestaurantPhase != DayPhase.Off) return false;
            var pool = Grounds.ForMap(SelectedSpot).SelectMany(g => g.Day).GroupBy(e => e.species)
                .Select(g => (g.Key, g.Sum(e => e.weight))).ToArray();
            try
            {
                dayForecast = new RestaurantForecast(State.Voyage * 7919 + SelectedSpot, restaurantPopularity, DateTime.Now.DayOfWeek, Weather.Fair, pool, Kitchen);
            }
            catch (ArgumentException) { return false; } // this ground's fish cannot be cooked yet: sail as before
            var v = RestaurantPlan;
            v.Day = DateTime.Now.DayOfWeek.ToString(); v.Hours = "18:00 – 23:00";
            v.GuestsLow = dayForecast.GuestRange.Min; v.GuestsHigh = dayForecast.GuestRange.Max;
            v.Dishes = dayForecast.DishRanges.GroupBy(k => k.Key.Item2)
                .Select(g => (dish: g.Key, lo: g.Sum(x => x.Value.Min), hi: g.Sum(x => x.Value.Max)))
                .OrderByDescending(x => x.hi).Take(2)
                .Select(x => new RestaurantDish { Name = Look(x.dish).name, Art = Look(x.dish).art, Fallback = Look(x.dish).fallback, Low = x.lo, High = x.hi })
                .Append(new RestaurantDish { Name = "Coffee", Art = "v2-dish-coffee", Fallback = "v2-icon-cup", Low = v.GuestsLow / 2, High = v.GuestsHigh / 2 + 2 })
                .ToList();
            v.BringBack = dayForecast.DishRanges.GroupBy(k => k.Key.Item1).OrderByDescending(g => g.Sum(x => x.Value.Max)).Take(2)
                .Select(g => new RestaurantFish { Name = FishName(g.Key), Art = FishArt(g.Key), Amount = g.Sum(x => x.Value.Max).ToString() }).ToList();
            var special = dayForecast.Guests.FirstOrDefault(g => g.Special);
            v.SpecialTitle = special != null ? "A birthday table for four" : "No special requests tonight"; v.SpecialReward = special != null ? "+120" : null; v.SpecialAccepted = special != null ? null : (bool?)true;
            specialGuest = special?.Id ?? -1;
            RestaurantPhase = DayPhase.Plan;
            RestaurantPreview = RestaurantScreen.Plan;
            return true;
        }
        int specialGuest = -1;
        static (string name, string art, string fallback) Look(Dish d) => DishLook.TryGetValue(d, out var l) ? l : (d.ToString(), "v2-icon-plate", "icon-food");

        // Got it on the plan card.
        void RestaurantPlanAccepted()
        {
            if (specialGuest >= 0 && RestaurantPlan.SpecialAccepted != null) dayForecast.SpecialRequest(specialGuest, RestaurantPlan.SpecialAccepted == true);
            RestaurantPreview = RestaurantScreen.None;
            RestaurantPhase = DayPhase.Out;
            SetSail();
        }

        // ---- 2. Home: prepare, then the market ---------------------------------------------------------------------

        // Called at the end of EnterHarbour; on a restaurant day the prep card replaces the plain Sell haul.
        void RestaurantArrived(bool arrived)
        {
            if (!arrived || RestaurantPhase != DayPhase.Out || dayForecast == null) return;
            dayForecast.Lock();
            if (State.UnsoldCatch.Count == 0) { StartNight(new List<PortionStock>()); return; }
            SuggestPrep();
            RestaurantPhase = DayPhase.Prep;
            RestaurantPreview = RestaurantScreen.Prep;
            panelOpen = false;
        }

        void SuggestPrep()
        {
            var caught = State.UnsoldCatch.Select(f => new RestaurantCatch { Species = f.Species, Kg = f.Kg }).ToList();
            var margin = (PrepMargin)Mathf.Clamp(RestaurantPrep.Margin, 0, 2);
            dayPrep = RestaurantPortions.Suggest(caught, dayForecast, Kitchen, margin);
            var v = RestaurantPrep;
            v.Catch = State.UnsoldCatch.GroupBy(f => f.Species).OrderByDescending(g => g.Sum(f => f.Kg)).Take(2)
                .Select(g => new RestaurantFish { Name = GameData.Get(g.Key).Name, Art = FishArt(g.Key), Amount = g.Count() > 1 ? g.Count().ToString() : $"{g.Sum(f => f.Kg):0.#} kg" }).ToList();
            var ranges = dayForecast.DishRanges;
            v.Rows = dayPrep.Stock.GroupBy(s => s.Form).Take(3).Select(g =>
            {
                var dish = FormDish.TryGetValue(g.Key, out var d) ? d : Dish.Soup;
                var r = ranges.Where(k => k.Key.Item2 == dish).ToArray();
                return new RestaurantPrepRow { Name = Look(dish).name, Art = Look(dish).art, Fallback = Look(dish).fallback, Portions = g.Sum(s => s.Count),
                    ForecastLow = r.Sum(x => x.Value.Min), ForecastHigh = r.Sum(x => x.Value.Max) };
            }).ToList();
            v.FridgeCapacity = Mathf.Max(1, dayPrep.Capacity); v.Fridge = v.RestaurantPortions;
            v.MarketFish = dayPrep.Market.Count; v.MarketCoins = dayPrep.MarketCoins;
            prepMargin = v.Margin;
        }
        int prepMargin = -1;

        // Prepare on the prep card: the portions go to the fridge, the rest of the catch to the market.
        void RestaurantPrepared()
        {
            var stock = new List<PortionStock>();
            foreach (var row in RestaurantPrep.Rows)
            {
                var form = FormDish.FirstOrDefault(f => Look(f.Value).name == row.Name).Key;
                var source = dayPrep.Stock.Where(s => s.Form == form).ToList();
                int planned = source.Sum(s => s.Count), want = Mathf.Min(row.Portions, Mathf.Max(planned, row.Portions));
                foreach (var s in source)
                {
                    int n = planned > 0 ? Mathf.RoundToInt(want * (float)s.Count / planned) : 0;
                    if (n > 0) { var c = s.Copy(); c.Count = n; stock.Add(c); }
                }
            }
            // Market: whatever the plan did not cook leaves the boat now (cheap), as the design says.
            var marketKg = dayPrep.Market.GroupBy(m => m.Species).ToDictionary(g => g.Key, g => g.Sum(m => m.Kg));
            var keep = new List<CaughtFish>();
            var sell = new List<CaughtFish>();
            foreach (var f in State.UnsoldCatch)
            {
                if (marketKg.TryGetValue(f.Species, out var kg) && kg >= f.Kg * .5f) { sell.Add(f); marketKg[f.Species] = kg - f.Kg; }
                else keep.Add(f);
            }
            State.UnsoldCatch.Clear();
            State.UnsoldCatch.AddRange(sell);
            if (sell.Count > 0) SellHaul(); else { State.TripDeployment.Clear(); State.EndVoyage(new SaleReport()); }
            StartNight(stock);
        }

        // ---- 3. The night -----------------------------------------------------------------------------------------

        void StartNight(List<PortionStock> stock)
        {
            var staff = new List<SimStaff>
            {
                new SimStaff { Id = "mira", Job = Job.Reception, NativeJob = Job.Reception, Rarity = CardRarity.Gold, Tile = Kitchen.Door, Position = Kitchen.Door },
            };
            foreach (var id in State.TripDeployment.Count > 0 ? State.TripDeployment : State.Deployment)
            {
                var card = State.Roster.FirstOrDefault(c => c.Id == id);
                if (card == null || card.Def == null || card.Id == "mira") continue;
                var job = RestaurantData.NativeJob(card.Def.Role);
                var start = job == Job.Cook ? Kitchen.PassKitchen : Kitchen.Door;
                staff.Add(SimStaff.FromCard(card, job, start));
            }
            // The captain walks around helping (design section 6). Until the rules have a helper role (RESTAURANT-PLAY-1 A),
            // the captain covers whichever of cooking and serving nobody else does; the kitchen half stays off the rail.
            if (!staff.Any(s => s.Job == Job.Waiter)) staff.Add(new SimStaff { Id = "captain", Job = Job.Waiter, NativeJob = Job.Waiter, Tile = Kitchen.Door, Position = Kitchen.Door });
            if (!staff.Any(s => s.Job == Job.Cook)) staff.Add(new SimStaff { Id = "captain-kitchen", Job = Job.Cook, NativeJob = Job.Cook, Tile = Kitchen.PassKitchen, Position = Kitchen.PassKitchen });
            night = new RestaurantSim(State.Voyage * 104729, Kitchen, dayForecast, stock, staff);
            popularityBefore = restaurantPopularity;
            staffLoad.Clear();
            RestaurantService.Rail = RestaurantRailMode.Scroll;
            RestaurantService.QuestionTitle = null;
            RestaurantService.Paused = false; RestaurantService.Speed = 1;
            RestaurantPhase = DayPhase.Service;
            RestaurantPreview = RestaurantScreen.Service;
            Toast("Mira opens the doors. Service starts at 18:00.");
        }

        // Per frame while the night runs: tick the rules, then refresh the service screen's numbers.
        void RestaurantTick(float dt)
        {
            if (RestaurantPhase == DayPhase.Prep && RestaurantPrep.Margin != prepMargin && dayPrep != null) SuggestPrep();
            if (RestaurantPhase != DayPhase.Service || night == null) return;
            var v = RestaurantService;
            if (!v.Paused) night.Tick(dt * Mathf.Max(1, v.Speed));
            v.Hour = night.Hour; v.Open = 18; v.Close = 23;
            v.Coins = State.Coins + night.Result.Coins;
            v.Popularity = restaurantPopularity;
            int fish = night.Stock.Where(s => s.Form != PreparedForm.Stock).Sum(s => s.Count), soup = night.Stock.Where(s => s.Form == PreparedForm.Stock).Sum(s => s.Count);
            int coffees = night.Groups.Sum(g => g.Tickets.Count(t => t.Dish == Dish.Coffee && t.Phase == TicketPhase.Delivered));
            v.Stock[0].Count = fish; v.Stock[0].Max = Mathf.Max(v.Stock[0].Max, fish); v.Stock[0].Alert = fish <= 2;
            v.Stock[1].Count = soup; v.Stock[1].Max = Mathf.Max(v.Stock[1].Max, soup);
            v.Stock[2].Count = Mathf.Max(0, 40 - coffees); v.Stock[2].Max = 40;
            var broken = night.Broken.Select(uid => Kitchen.Active.FirstOrDefault(i => i.Uid == uid)).Where(i => i != null).ToList();
            v.Alert = broken.Count > 0 ? $"{RestaurantData.Get(broken[0].Id).Name}\nneeds repair" : null;
            v.Crew = night.Staff.Where(s => !s.Id.EndsWith("-kitchen")).Select(s =>
            {
                staffLoad.TryGetValue(s.Id, out var load);
                load = Mathf.MoveTowards(load, s.Busy ? 1f : 0f, dt * Mathf.Max(1, v.Speed) / 20f);
                staffLoad[s.Id] = load;
                return new RestaurantStaff_View(s, load);
            }).Select(x => x.View).ToList();
            if (night.Finished) ShowClosing();
        }

        // A small adapter so the HUD's staff card (VoyageGame.RestaurantStaff) reads from the rules' staff member.
        readonly struct RestaurantStaff_View
        {
            public readonly VoyageGame.RestaurantStaff View;
            public RestaurantStaff_View(SimStaff s, float load)
            {
                var (job, icon, fallback) = s.Job switch
                {
                    Job.Cook => ("Cook", "v2-icon-pan", "icon-food"),
                    Job.Waiter => ("Serve", "v2-icon-cloche", "v2-icon-haul"),
                    Job.Handyman => ("Fix", "v2-icon-wrench", "v2-icon-engine"),
                    Job.Barista => ("Coffee", "v2-icon-cup", "v2-icon-clock"),
                    _ => ("Host", "v2-icon-bell", "v2-icon-anchor"),
                };
                if (s.Id == "captain") (job, icon, fallback) = ("Help", "v2-icon-crew", "icon-crew");
                View = new VoyageGame.RestaurantStaff { Portrait = s.Id, Job = job, Icon = icon, Fallback = fallback, Busy = Mathf.Clamp01(.15f + load * .85f) };
            }
        }

        // ---- 4. Closing and sleep ----------------------------------------------------------------------------------

        void ShowClosing()
        {
            var r = night.Result;
            restaurantPopularity = Mathf.Max(0, popularityBefore + Mathf.RoundToInt(r.PopularityGain));
            var v = RestaurantClosing;
            v.Served = r.Served; v.Left = r.Left; v.Dishes = r.DishCoins; v.Drinks = r.DrinkCoins; v.Tips = r.Tips;
            v.CatPortions = r.Cats; v.CatValue = r.Cats * 2;
            v.Stars = Mathf.Clamp(Mathf.RoundToInt(r.Stars), 0, 5);
            v.PopularityFrom = popularityBefore; v.PopularityTo = restaurantPopularity;
            v.PopularityBefore = Mathf.Clamp01(popularityBefore / 50f); v.Popularity = Mathf.Clamp01(restaurantPopularity / 50f);
            var best = r.Walking.OrderByDescending(w => w.Metres).FirstOrDefault(w => w.Id != "mira");
            v.CrewOfTheNight = best != null ? Cap(best.Id) : "Mira"; v.CrewPortrait = best?.Id ?? "mira";
            string[] good = { "Fish worth the wait.", "Cosy, even in the rain.", "We'll be back!" }, mid = { "More coffee, please!", "A bit slow tonight.", "Nice view, cold plate." };
            v.Reviews = night.Groups.Where(g => g.Paid).Take(3).Select((g, i) => new RestaurantReview
            {
                Portrait = GuestFaces[(g.Id + i) % GuestFaces.Length], Stars = Mathf.Clamp(g.Stars, 1, 5),
                Quote = g.Stars >= 4 ? good[i % good.Length] : mid[i % mid.Length],
            }).ToList();
            v.MiraLine = r.Served >= r.Guests * .8f ? "Same time tomorrow?" : "We'll do better tomorrow.";
            RestaurantPhase = DayPhase.Closing;
            RestaurantPreview = RestaurantScreen.Closing;
        }
        static string Cap(string id) => string.IsNullOrEmpty(id) ? id : char.ToUpperInvariant(id[0]) + id.Substring(1);

        // Sleep on the closing card: bank the night, feed the cats, start a new morning in the harbour.
        void RestaurantSleep()
        {
            if (night != null) State.Coins += Mathf.Max(0, night.Result.NetCoins);
            night = null; dayForecast = null; dayPrep = null;
            RestaurantPhase = DayPhase.Off;
            RestaurantPreview = RestaurantScreen.None;
            harbourEvening = false;
            SaveGame();
            Toast("A new morning in Gull Harbour.");
        }

        // ---- capture / test: walks the real day without sailing (VoyageUiV2Capture "day-*" steps) -----------------

        public bool StageRestaurantDay(string step)
        {
            switch (step)
            {
                case "day-plan":
                    RestaurantPhase = DayPhase.Off; SelectedSpot = 0;
                    return RestaurantPlanBeforeSail();
                case "day-prep":
                    if (RestaurantPhase == DayPhase.Plan) { RestaurantPreview = RestaurantScreen.None; RestaurantPhase = DayPhase.Out; }
                    State.UnsoldCatch.Clear();
                    var rng = new System.Random(5);
                    foreach (var s in new[] { Species.Mackerel, Species.Mackerel, Species.Mackerel, Species.Pollock, Species.Pollock, Species.Herring, Species.Cod })
                        for (int i = 0; i < 2; i++) State.UnsoldCatch.Add(new CaughtFish { Species = s, Kg = GameData.Get(s).MinKg + (float)rng.NextDouble() * (GameData.Get(s).MaxKg - GameData.Get(s).MinKg) * .5f });
                    RestaurantArrived(true);
                    return RestaurantPhase == DayPhase.Prep;
                case "day-service":
                    if (RestaurantPhase == DayPhase.Prep) RestaurantPrepared();
                    if (night == null) return false;
                    while (night.Hour < 19.6f && !night.Finished) night.Tick(.5f);
                    RestaurantTick(0f);
                    return RestaurantPhase == DayPhase.Service;
                case "day-closing":
                    if (night == null) return false;
                    while (!night.Finished) night.Tick(.5f);
                    RestaurantTick(0f);
                    return RestaurantPhase == DayPhase.Closing;
                // A fresh save played through its first day: the real departure, trip, catch (the bot fishes), arrival,
                // prep, a live night, closing and sleep. Each step logs what it found for the check log.
                case "new-harbour":
                    NewGame(); EndIntro(); showTitle = false; State.Tutorial = (int)TutStep.Hello; RestaurantPhase = DayPhase.Off;
                    return CurrentMode == Mode.Harbour && State.Coins >= 0;
                case "new-plan":
                    departureReady = true;
                    if (!ConfirmDeparture()) { Debug.LogError("[Catchline] NEWGAME departure blocked: " + SailBlocker()); return false; }
                    Debug.Log($"[Catchline] NEWGAME plan {RestaurantPlan.GuestsLow}-{RestaurantPlan.GuestsHigh} guests, dishes {string.Join("/", RestaurantPlan.Dishes.Select(d => d.Name))}");
                    return RestaurantPhase == DayPhase.Plan && RestaurantPreview == RestaurantScreen.Plan;
                case "new-fishing":
                    RestaurantPlanAccepted();
                    for (int n = 0; n < 40000 && !(CurrentMode == Mode.Fishing && AtFishingGround); n++) Tick(.05f);
                    AutoPlay = true;
                    for (int n = 0; n < 40000 && Cooler.Count < 8 && !HoldFull; n++) Tick(.05f);
                    AutoPlay = false;
                    Debug.Log($"[Catchline] NEWGAME caught {Cooler.Count} fish, mode {CurrentMode}");
                    return CurrentMode == Mode.Fishing && Cooler.Count > 0;
                case "new-prep":
                    HeadHome();
                    for (int n = 0; n < 40000 && RestaurantPhase == DayPhase.Out; n++) Tick(.05f);
                    Debug.Log($"[Catchline] NEWGAME home: phase {RestaurantPhase}, {State.UnsoldCatch.Count} fish, rows {string.Join("/", RestaurantPrep.Rows.Select(r => r.Name + " " + r.Portions))}, market {RestaurantPrep.MarketFish}");
                    return RestaurantPhase == DayPhase.Prep;
                case "new-service":
                    RestaurantPrepared();
                    for (int n = 0; n < 4000 && night != null && night.Hour < 20f; n++) RestaurantTick(.25f);
                    Debug.Log($"[Catchline] NEWGAME service {night?.Hour:0.00}h, served {night?.Result.Served}, coins {RestaurantService.Coins}");
                    return RestaurantPhase == DayPhase.Service;
                case "new-closing":
                    for (int n = 0; n < 40000 && RestaurantPhase == DayPhase.Service; n++) RestaurantTick(.25f);
                    Debug.Log($"[Catchline] NEWGAME closing: served {RestaurantClosing.Served}, left {RestaurantClosing.Left}, net {night?.Result.NetCoins}, popularity {RestaurantClosing.PopularityFrom}->{RestaurantClosing.PopularityTo}");
                    return RestaurantPhase == DayPhase.Closing;
                case "new-morning":
                    int before = State.Coins;
                    RestaurantSleep();
                    Debug.Log($"[Catchline] NEWGAME morning: coins {before}->{State.Coins}, phase {RestaurantPhase}, tutorial {Tutorial}");
                    return RestaurantPhase == DayPhase.Off && CurrentMode == Mode.Harbour;
            }
            return false;
        }
    }
}
