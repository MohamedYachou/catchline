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
        public enum DayPhase { Off, Plan, Out, Prep, Market, Service, Closing }
        public DayPhase RestaurantPhase { get; private set; }
        // The new loop is on for every save; captures and old checks can switch it off.
        public bool RestaurantLoop = true;

        RestaurantState restaurantState;
        RestaurantLayout restaurantLayout;
        RestaurantForecast dayForecast;
        PrepPlan dayPrep;
        RestaurantSim night;
        int popularityBefore;
        RestaurantWorld restaurantWorld;
        // Mo 10-26: the restaurant opens once the Skiff is bought (Mira joins); the rowboat days stay the fishing tutorial.
        bool RestaurantOpen => RestaurantLoop && (State.Hull >= 1 || restaurantForced);
        bool restaurantForced;
        int restaurantPopularity { get => State.RestaurantPopularity; set => State.RestaurantPopularity = value; }
        readonly Dictionary<string, float> staffLoad = new();

        RestaurantLayout Kitchen => restaurantLayout ??= new RestaurantLayout(restaurantState ??= LoadRestaurant());
        RestaurantState LoadRestaurant()
        {
            if (!string.IsNullOrEmpty(State.RestaurantLayout)) try { return RestaurantState.FromJson(State.RestaurantLayout); } catch (Exception e) { Debug.LogWarning("[Catchline] restaurant layout unreadable, starting kit: " + e.Message); }
            return RestaurantLayout.StartingKit();
        }
        void StoreRestaurant() { if (restaurantState != null) State.RestaurantLayout = JsonUtility.ToJson(restaurantState); }

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
        static readonly string[] GuestFaces = { "guest-ada", "guest-ben", "guest-cora", "guest-dan", "guest-edda", "guest-finn", "guest-gus", "guest-hazel", "guest-ivo", "guest-jonas", "guest-kai", "guest-lena" };
        static string FishArt(Species s) => "fish-" + s.ToString().ToLowerInvariant();
        static string FishName(Species s) => GameData.Get(s).Name.ToLowerInvariant();

        // ---- 1. Let's go: Mira's plan first ------------------------------------------------------------------------

        // Called where Let's go would sail; true when the plan card took over (its Got it sails).
        bool RestaurantPlanBeforeSail()
        {
            if (!RestaurantOpen || RestaurantPhase != DayPhase.Off) return false;
            var pool = Grounds.ForMap(SelectedSpot).SelectMany(g => g.Day).GroupBy(e => e.species)
                .Select(g => (g.Key, g.Sum(e => e.weight))).ToArray();
            try
            {
                dayForecast = new RestaurantForecast(State.Voyage * 7919 + SelectedSpot, restaurantPopularity, RestaurantWeekday(State.RestaurantDay), (Weather)State.RestaurantWeather, pool, Kitchen,
                    State.RestaurantNights.Count == 0 ? FirstNightGuests : 0);
            }
            catch (ArgumentException) { return false; } // this ground's fish cannot be cooked yet: sail as before
            var v = RestaurantPlan;
            v.Day = RestaurantWeekday(State.RestaurantDay).ToString(); v.Hours = "18:00 – 23:00";
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
            v.SpecialTitle = special != null ? "A birthday table for four" : "No special\nrequests tonight"; v.SpecialReward = special != null ? "+120" : null; v.SpecialAccepted = special != null ? null : (bool?)true;
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
            if (sell.Count == 0) { State.TripDeployment.Clear(); State.EndVoyage(new SaleReport()); StartNight(stock); return; }
            // S7: the morning market card decides what the buyer gets; Keep turns a fish into extra soup for tonight.
            marketStock = stock;
            var m = RestaurantMarket;
            m.Rows = sell.GroupBy(f => f.Species).Select(g => new RestaurantMarketRow
            {
                Species = g.Key, Name = GameData.Get(g.Key).Name, Art = FishArt(g.Key), Kg = g.Sum(f => f.Kg),
                Value = g.Sum(f => State.ValueOf(f, SimTime)),
            }).OrderByDescending(r => r.Value).ToList();
            m.Wallet = State.Coins; m.Room = Mathf.Max(0, dayPrep.Capacity - stock.Sum(x => x.Count));
            string[] moods = { "keen", "steady", "picky" };
            m.Mood = moods[State.RestaurantDay % moods.Length];
            m.Demand = m.Mood == "keen" ? "Good demand today." : m.Mood == "steady" ? "Fair prices today." : "Only the best fish today.";
            RestaurantPhase = DayPhase.Market;
            RestaurantPreview = RestaurantScreen.Market;
        }
        List<PortionStock> marketStock;

        // Kept rows become soup portions while the fridge has room; the rest sells at the market, then the doors open.
        void RestaurantMarketOpen()
        {
            var m = RestaurantMarket; int room = m.Room;
            var sold = new List<CaughtFish>();
            foreach (var f in State.UnsoldCatch)
            {
                var row = m.Rows.FirstOrDefault(r => r.Species == f.Species);
                int bowls = RestaurantPortions.Yield(f.Species, f.Kg, PreparedForm.Stock);
                if (row != null && row.Keep && Kitchen.CanCook(Dish.Soup) && bowls > 0 && bowls <= room)
                { RestaurantPortions.Add(marketStock, f.Species, PreparedForm.Stock, bowls); room -= bowls; }
                else sold.Add(f);
            }
            State.UnsoldCatch.Clear();
            State.UnsoldCatch.AddRange(sold);
            if (sold.Count > 0) SellHaul(); else { State.TripDeployment.Clear(); State.EndVoyage(new SaleReport()); }
            StartNight(marketStock);
        }

        // S9: each crew member's work order, as saved on the priorities screen or their job's default.
        Work[] PriorityOf(string id, Job job)
        {
            var saved = State.RestaurantPriorities.FirstOrDefault(p => p.StartsWith(id + "="));
            if (saved != null)
                try { var w = saved.Substring(id.Length + 1).Split(',').Select(x => (Work)Enum.Parse(typeof(Work), x)).ToArray(); if (w.Length == 3) return w; }
                catch (ArgumentException) { }
            return SimStaff.DefaultOrder(job);
        }

        void SavePriority(string id, Work[] order)
        {
            State.RestaurantPriorities.RemoveAll(p => p.StartsWith(id + "="));
            State.RestaurantPriorities.Add(id + "=" + string.Join(",", order));
        }

        // Tonight's crew as the night will field them: Mira at reception, then the deployed cards in their fixed jobs.
        List<(string id, Job job)> TonightsCrew()
        {
            var crew = new List<(string, Job)> { ("mira", Job.Reception) };
            foreach (var id in State.TripDeployment.Count > 0 ? State.TripDeployment : State.Deployment)
            {
                var card = State.Roster.FirstOrDefault(c => c.Id == id);
                if (card == null || card.Def == null || card.Id == "mira") continue;
                crew.Add((card.Id, SimStaff.FromCard(card, Job.Cook, Kitchen.Door).Job));
            }
            return crew;
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
                var s = SimStaff.FromCard(card, Job.Cook, Kitchen.Door);
                if (s.Job == Job.Cook) { s.Tile = Kitchen.PassKitchen; s.Position = s.Tile; }
                staff.Add(s);
            }
            if (!Environment.GetCommandLineArgs().Contains("-no-priorities")) foreach (var s in staff) s.Order = PriorityOf(s.Id, s.Job); // A/B checks
            // The captain walks around helping wherever the queue is longest (design section 6).
            staff.Add(SimStaff.Captain(Kitchen.Door));
            night = new RestaurantSim(State.Voyage * 104729, Kitchen, dayForecast, stock, staff) { Breakdowns = true };
            // The room in 3D behind the service HUD; the day loop ticks the rules, the world only draws them.
            restaurantWorld ??= gameObject.AddComponent<RestaurantWorld>();
            restaurantWorld.DriveSimulation = false;
            try { restaurantWorld.Begin(night); }
            catch (Exception e) { Debug.LogError("[Catchline] restaurant room failed: " + e.Message); }
            popularityBefore = restaurantPopularity;
            staffLoad.Clear();
            RestaurantService.Rail = RestaurantRailMode.Scroll;
            RestaurantService.QuestionTitle = null;
            RestaurantService.Paused = false; RestaurantService.Speed = 1;
            RestaurantPhase = DayPhase.Service;
            RestaurantPreview = RestaurantScreen.Service;
            // The very first night opens on Mira's coaching card, the service paused behind it.
            if (State.RestaurantNights.Count == 0 && HasUi("rx-s13-background")) { RestaurantPreview = RestaurantScreen.FirstNight; RestaurantService.Paused = true; }
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
            if (restaurantWorld != null && restaurantWorld.Sim == night) restaurantWorld.Refresh(dt * (v.Paused ? 0 : Mathf.Max(1, v.Speed)));
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
            // Three tables speak: the best, the worst and one between, each about what really happened at it.
            var paid = night.Groups.Where(g => g.Paid).OrderByDescending(g => g.Stars).ThenBy(g => g.Id).ToList();
            var speak = paid.Count <= 3 ? paid : new List<ServiceGroup> { paid[0], paid[paid.Count / 2], paid[^1] };
            // When the queue lost a lot of guests, one of them has the last word.
            var walked = night.Groups.FirstOrDefault(g => !g.Paid && g.Phase == GroupPhase.Gone);
            if (walked != null && r.Left * 3 >= r.Guests) { walked.Stars = 1; walked.Why = "queue"; if (speak.Count >= 3) speak[^1] = walked; else speak.Add(walked); }
            v.Reviews = speak.Select((g, i) => new RestaurantReview
            {
                Portrait = GuestFaces[(g.Id + i) % GuestFaces.Length], Stars = Mathf.Clamp(g.Stars, 1, 5),
                Quote = ReviewQuote(g, i),
            }).ToList();
            Debug.Log("[Catchline] REVIEWS " + string.Join(" | ", speak.Select(g => $"{g.Stars}* {g.Why}")) + " :: " + string.Join(" | ", v.Reviews.Select(x => x.Quote)));
            v.MiraLine = r.Served >= r.Guests * .8f ? "Same time tomorrow?" : "Better tomorrow!";
            v.Title = r.Served >= r.Guests * .8f ? "A good night on the quay" : r.Served * 2 >= r.Guests ? "A busy night on the quay" : "A rough night on the quay";
            RecordNight(r);
            var sleep = RestaurantSleepCard;
            sleep.Net = r.NetCoins; sleep.Popularity = restaurantPopularity - popularityBefore;
            // Tomorrow: fair most days, some sun (terrace walk-ins), some rain (fewer guests, no terrace).
            double roll = new System.Random(State.RestaurantDay * 31 + 7).NextDouble();
            var weather = roll < .25 ? Weather.Sun : roll < .45 ? Weather.Rain : Weather.Fair;
            sleep.TomorrowWeather = (int)weather;
            sleep.Tomorrow = $"{RestaurantWeekday(State.RestaurantDay + 1)} · {WeatherWords(weather)}";
            var nextDay = RestaurantWeekday(State.RestaurantDay + 1);
            sleep.Booking = weather == Weather.Rain ? "A quiet night indoors" : nextDay is DayOfWeek.Friday or DayOfWeek.Saturday ? "Expect a full house"
                : weather == Weather.Sun && Kitchen.Stage.TerraceWidth > 0 ? "Expect a lively terrace" : nextDay == DayOfWeek.Monday ? "A slow Monday" : "A steady night ahead";
            RestaurantPhase = DayPhase.Closing;
            RestaurantPreview = RestaurantScreen.Closing;
        }

        // ---- S6 dashboard, S8 upgrades, S11 stage-up ----------------------------------------------------------------

        public static readonly (string id, string name, string effect, int cost)[] RestaurantUpgrades =
        {
            ("BigFridge", "Bigger fridge", "+15 portions", 600), ("ReliableStove", "Reliable stove", "Fewer breakdowns", 450),
            ("CosyLighting", "Cosy lighting", "More guest patience", 300),
        };
        static readonly string[] StagePitch = { "", "", "More tables and a terrace", "A proper dining room and a bar", "Booths, a fish counter, the big terrace" };
        static readonly (string reward, string[] unlocks)[] StageUnlocks =
        {
            default, default, ("Terrace unlocked!", new[] { "More dining room", "A bigger kitchen", "Quayside tables" }),
            ("Bar unlocked!", new[] { "Booths for six", "A bar with stools", "A bigger terrace" }),
            ("Fish counter unlocked!", new[] { "The biggest kitchen", "A fish counter", "Room for the whole harbour" }),
        };

        // The week so far from the saved nights (RecordNight's format).
        void FillDashboard()
        {
            var v = RestaurantDashboard;
            int week = State.RestaurantDay / 7;
            var nights = State.RestaurantNights.Select(n => n.Split('|')).Where(p => p.Length >= 9).ToList();
            List<string[]> In(int w) => nights.Where(p => int.Parse(p[0]) / 7 == w).ToList();
            var now = In(week); var last = In(week - 1);
            v.Week = week + 1;
            v.DayIncome = new int[7];
            foreach (var p in now) v.DayIncome[int.Parse(p[0]) % 7] = Mathf.Max(0, int.Parse(p[1]));
            v.Income = now.Sum(p => int.Parse(p[1]));
            int before = last.Sum(p => int.Parse(p[1]));
            v.IncomeChange = before > 0 ? $"{(v.Income >= before ? "+" : "")}{Mathf.RoundToInt((v.Income - before) * 100f / before)}% last week" : now.Count > 0 ? $"{now.Count} night{(now.Count == 1 ? "" : "s")} this week" : "First week";
            v.Dishes = now.Sum(p => int.Parse(p[2])); v.Drinks = now.Sum(p => int.Parse(p[3])); v.Tips = now.Sum(p => int.Parse(p[4]));
            v.Popularity = restaurantPopularity;
            v.DayPopularity = Enumerable.Repeat(-1, 7).ToArray();
            foreach (var p in now) v.DayPopularity[int.Parse(p[0]) % 7] = int.Parse(p[5]);
            int startPop = now.Count > 0 ? int.Parse(now[0][5]) : restaurantPopularity;
            v.PopularityChange = restaurantPopularity - startPop + (now.Count > 0 ? 0 : 0);
            v.Menu = now.SelectMany(p => p[8].Split(';')).Where(x => x.Contains("=")).Select(x => x.Split('='))
                .GroupBy(x => x[0]).Select(g => (dish: (Dish)Enum.Parse(typeof(Dish), g.Key), sold: g.Sum(x => int.Parse(x[1]))))
                .OrderByDescending(x => x.sold).Take(3).ToList();
            FillStageCard(v.Stage);
        }

        void FillStageCard(RestaurantStageCard c)
        {
            int next = Kitchen.State.Stage + 1;
            c.Current = Kitchen.State.Stage; c.Next = next;
            if (next > 4) { c.Name = null; return; }
            var def = RestaurantData.Stage(next);
            c.Name = def.Name == "Cafe" ? "Café" : def.Name; c.Pitch = StagePitch[next];
            c.Stars = def.Popularity; c.StarsMet = restaurantPopularity >= def.Popularity;
            c.Cost = def.Price; c.Have = State.Coins;
        }

        // Buys the next stage through the layout's own rules, with the game's wallet and popularity.
        bool BuyRestaurantStage()
        {
            var st = Kitchen.State; st.Coins = State.Coins; st.Popularity = restaurantPopularity;
            int next = st.Stage + 1;
            var r = Kitchen.Expand(next);
            if (!r.Ok) { Toast(RestaurantLayout.Sentence(r.Reason)); return false; }
            State.Coins = st.Coins;
            var unlock = StageUnlocks[next];
            var v = RestaurantStageUp;
            v.From = RestaurantData.Stage(next - 1).Name; v.To = RestaurantData.Stage(next).Name; v.Stage = next;
            v.Reward = unlock.reward; v.Unlocks = unlock.unlocks;
            StoreRestaurant(); SaveGame();
            RestaurantPreview = RestaurantScreen.StageUp;
            audio?.Play(VoyageAudio.Cue.Purchase, .7f);
            return true;
        }

        // A short line from a table about its night (the closing card's review strip fits about 24 characters).
        string ReviewQuote(ServiceGroup g, int i)
        {
            var dish = g.Tickets.Where(t => t.Dish != Dish.Coffee).Select(t => t.Dish).FirstOrDefault();
            string name = DishLook.TryGetValue(dish, out var look) ? look.name.ToLower() : "fish";
            string Pick(params string[] lines) => lines[(g.Id + i) % lines.Length];
            return g.Why switch
            {
                "gave-up" => Pick("We waited, then left.", "Never got our food."),
                "queue" => Pick("Queue was too long.", "No table for us."),
                "missing" => Pick("Half our order came.", "Still hungry, sadly."),
                "cold" => Pick($"Cold {name}. Shame.", "Lovely view, cold plate."),
                "swap" => Pick("Not what we ordered.", "Nice, but not our pick."),
                "slow" => Pick("A bit slow tonight.", "Worth it, but slow."),
                "special" => Pick("That special! Wow.", "Ask for the special!"),
                "captain" => Pick("The captain's catch!", "Fresh off the boat!"),
                _ => Pick($"Best {name} in town!", "Fish worth the trip.", "We'll be back!"),
            };
        }

        // ---- S1 arrange by day: the player's own room in 3D behind the drawer, empty of crew and guests ----

        // The reopening night is a short tutorial service (design section 9: four guests).
        const int FirstNightGuests = 4;

        bool ArrangeLive => RestaurantPreview == RestaurantScreen.Arrange && restaurantWorld != null && restaurantWorld.RoomRoot != null && restaurantWorld.Sim == null;
        RestaurantScreen arrangeBack;

        public void OpenRestaurantArrange()
        {
            if (RestaurantPhase == DayPhase.Service) return;
            restaurantWorld ??= gameObject.AddComponent<RestaurantWorld>();
            restaurantWorld.DriveSimulation = false;
            try { restaurantWorld.Show(Kitchen); }
            catch (Exception e) { Debug.LogError("[Catchline] arrange room failed: " + e.Message); }
            arrangeBack = RestaurantPreview;
            var v = RestaurantArrange; v.Undo.Clear(); v.PlaceId = null; v.LiftUid = 0; v.Placing = null;
            RestaurantPreview = RestaurantScreen.Arrange;
            SetArrangeCategory(v, 1);
        }

        void CloseRestaurantArrange()
        {
            if (!ArrangeLive) { RestaurantPreview = RestaurantScreen.None; return; }
            CancelArrange(RestaurantArrange);
            restaurantWorld.End();
            if (arrangeBack == RestaurantScreen.Dashboard) OpenRestaurantDashboard(); else RestaurantPreview = arrangeBack;
        }

        static string ArrangeArtKey(ItemId id) => id switch
        {
            ItemId.Table2 => "table2", ItemId.Table4 => "table4", ItemId.Booth6 => "booth",
            _ => string.Concat(id.ToString().Select((c, i) => i > 0 && char.IsUpper(c) ? "-" + char.ToLower(c) : char.ToLower(c).ToString())),
        };
        static string ArrangeName(ItemDef d) => d.Id switch
        {
            ItemId.Table2 => "Table for 2", ItemId.Table4 => "Table for 4", ItemId.Booth6 => "Booth", ItemId.Sink => "Sink",
            _ => d.Name,
        };

        void SetArrangeCategory(RestaurantArrangeView v, int c)
        {
            // Expand is the stage card (S8), not something to place.
            if (c == 4) { CloseRestaurantArrange(); OpenRestaurantUpgrades(); return; }
            CancelArrange(v);
            v.Category = c; v.Scroll = 0;
            var areas = c == 0 ? new[] { Area.Kitchen } : c == 1 ? new[] { Area.Guests } : c == 2 ? new[] { Area.Bar } : new[] { Area.Decor, Area.Wall };
            v.Items = RestaurantData.Items.Where(d => areas.Contains(d.Area) && d.Id != ItemId.Reception && d.Stage <= Kitchen.State.Stage)
                .Select(d => new RestaurantShopItem { Id = d.Id, Name = ArrangeName(d), Art = "v2-item-rest-" + ArrangeArtKey(d.Id), Footprint = $"{d.Width}×{d.Height}", Price = d.Price })
                .ToList();
        }

        // A card picked from the drawer: its ghost starts on the free tile nearest the middle of the floor that takes it.
        void PickArrangeItem(RestaurantArrangeView v, int i)
        {
            CancelArrange(v);
            var id = v.Items[i].Id; var st = Kitchen.Stage;
            v.Selected = i; v.PlaceId = id; v.Rotated = false;
            var mid = RestaurantData.Get(id).Area == Area.Kitchen ? new Vector2(st.KitchenWidth / 2f, 2) : new Vector2((st.KitchenWidth + st.Width) / 2f, 2);
            Vector2Int best = Vector2Int.RoundToInt(mid); float near = float.MaxValue;
            for (int y = 0; y < st.Depth; y++)
                for (int x = 0; x < st.TotalWidth; x++)
                    if ((new Vector2(x, y) - mid).sqrMagnitude < near && Kitchen.CheckPlacement(id, x, y).Ok) { near = (new Vector2(x, y) - mid).sqrMagnitude; best = new Vector2Int(x, y); }
            v.Tile = best;
            RefitArrange(v);
        }

        void RefitArrange(RestaurantArrangeView v)
        {
            if (v.PlaceId == null) { restaurantWorld?.Ghost(null, default, false, false); return; }
            var d = RestaurantData.Get(v.PlaceId.Value);
            var r = Kitchen.CheckPlacement(v.PlaceId.Value, v.Tile.x, v.Tile.y, v.Rotated, v.LiftUid);
            v.Fits = r.Ok; v.Reason = r.Ok ? null : r.Message;
            v.Placing = $"{ArrangeName(d)} · {d.Width}×{d.Height}";
            restaurantWorld?.Ghost(v.PlaceId, v.Tile, v.Rotated, v.Fits);
        }

        // A tap on the room moves the ghost there, or lifts the placed item under the finger.
        void ArrangeTap(RestaurantArrangeView v)
        {
            var p = UnityEngine.InputSystem.Pointer.current;
            if (p == null || restaurantWorld == null) return;
            var at = p.position.ReadValue();
            if (!restaurantWorld.TileAt(new Vector2(at.x / Screen.width, at.y / Screen.height), out var tile)) return;
            ArrangeTapTile(v, tile);
        }

        void ArrangeTapTile(RestaurantArrangeView v, Vector2Int tile)
        {
            if (v.PlaceId != null)
            {
                var d = RestaurantData.Get(v.PlaceId.Value);
                v.Tile = new Vector2Int(tile.x - ((v.Rotated ? d.Height : d.Width) - 1) / 2, tile.y);
                RefitArrange(v); return;
            }
            var hit = Kitchen.Active.FirstOrDefault(i => Kitchen.Cells(i).Contains(tile));
            if (hit == null) return;
            v.LiftUid = hit.Uid; v.PlaceId = hit.Id; v.Tile = new Vector2Int(hit.X, hit.Y); v.Rotated = hit.Rotated; v.Selected = -1;
            restaurantWorld.Hide(hit.Uid, true);
            RefitArrange(v);
        }

        void CancelArrange(RestaurantArrangeView v)
        {
            if (v.LiftUid != 0) restaurantWorld?.Hide(v.LiftUid, false);
            v.PlaceId = null; v.LiftUid = 0; v.Selected = -1; v.Placing = null;
            restaurantWorld?.Ghost(null, default, false, false);
        }

        // ✓ pays for a new item or puts a lifted one down, through the layout's own rules; Undo steps back one.
        void ConfirmArrange(RestaurantArrangeView v)
        {
            if (v.PlaceId == null) return;
            if (!v.Fits) { Toast(v.Reason); return; }
            var st = Kitchen.State; st.Coins = State.Coins;
            var before = (JsonUtility.ToJson(new ItemsOnly { Items = st.Items }), st.NextUid, State.Coins);
            bool moving = v.LiftUid != 0;
            var r = moving ? Kitchen.Move(v.LiftUid, v.Tile.x, v.Tile.y, v.Rotated) : Kitchen.Buy(v.PlaceId.Value, v.Tile.x, v.Tile.y, v.Rotated);
            if (!r.Ok) { Toast(r.Message); return; }
            v.Undo.Add(before); State.Coins = st.Coins;
            StoreRestaurant(); SaveGame();
            audio?.Play(moving ? VoyageAudio.Cue.Select : VoyageAudio.Cue.Purchase, .6f);
            v.PlaceId = null; v.LiftUid = 0; v.Selected = -1; v.Placing = null;
            restaurantWorld.Show(Kitchen);
        }
        [Serializable] class ItemsOnly { public List<RestaurantItem> Items; }

        void UndoArrange(RestaurantArrangeView v)
        {
            if (!ArrangeLive) return;
            CancelArrange(v);
            if (v.Undo.Count == 0) return;
            var (items, nextUid, coins) = v.Undo[^1]; v.Undo.RemoveAt(v.Undo.Count - 1);
            Kitchen.State.Items = JsonUtility.FromJson<ItemsOnly>(items).Items; Kitchen.State.NextUid = nextUid; State.Coins = coins;
            StoreRestaurant(); SaveGame();
            restaurantWorld.Show(Kitchen);
        }

        bool BuyRestaurantUpgrade(string id)
        {
            var u = RestaurantUpgrades.First(x => x.id == id);
            if (Kitchen.HasUpgrade(id) || State.Coins < u.cost) return false;
            State.Coins -= u.cost; Kitchen.State.Upgrades.Add(id);
            StoreRestaurant(); SaveGame();
            audio?.Play(VoyageAudio.Cue.Purchase, .6f);
            Toast($"{u.name}: {u.effect.ToLowerInvariant()}.");
            return true;
        }

        // The restaurant keeps its own calendar: night 0 is a Monday. Tomorrow's weather is rolled at bedtime and shown
        // on the sleep card, so the plan card and the forecast agree with it.
        static DayOfWeek RestaurantWeekday(int day) => (DayOfWeek)((day + 1) % 7);
        static string WeatherWords(Weather w) => w == Weather.Sun ? "Sunshine" : w == Weather.Rain ? "Rain" : "Clear skies";

        // One line per night for the dashboard: "day|net|dishes|drinks|tips|popularity|served|left|Dish=n;...".
        void RecordNight(NightResult r)
        {
            var sold = night.Groups.SelectMany(g => g.Tickets).Where(t => t.Phase == TicketPhase.Delivered)
                .GroupBy(t => t.Dish).Select(g => $"{g.Key}={g.Count()}");
            State.RestaurantNights.Add(string.Join("|", State.RestaurantDay, r.NetCoins, r.DishCoins, r.DrinkCoins, r.Tips, restaurantPopularity, r.Served, r.Left, string.Join(";", sold)));
            while (State.RestaurantNights.Count > 14) State.RestaurantNights.RemoveAt(0);
        }
        static string Cap(string id) => string.IsNullOrEmpty(id) ? id : char.ToUpperInvariant(id[0]) + id.Substring(1);

        // Sleep on the closing card: bank the night, feed the cats, start a new morning in the harbour.
        void RestaurantSleep()
        {
            if (night != null) State.Coins += Mathf.Max(0, night.Result.NetCoins);
            if (night != null) { State.RestaurantDay++; State.RestaurantWeather = RestaurantSleepCard.TomorrowWeather; }
            if (restaurantWorld != null) restaurantWorld.End();
            night = null; dayForecast = null; dayPrep = null;
            RestaurantPhase = DayPhase.Off;
            RestaurantPreview = RestaurantScreen.None;
            harbourEvening = false;
            StoreRestaurant();
            SaveGame();
            Toast("A new morning in Gull Harbour.");
        }

        // ---- capture / test: walks the real day without sailing (VoyageUiV2Capture "day-*" steps) -----------------

        public bool StageRestaurantDay(string step)
        {
            switch (step)
            {
                case "day-bistro": // buys stage 2 so the next night runs in the Bistro room
                    State.Coins += 100000; restaurantPopularity = 50;
                    bool bought = BuyRestaurantStage(); RestaurantPreview = RestaurantScreen.None;
                    foreach (var (id, _, _, _) in RestaurantUpgrades) BuyRestaurantUpgrade(id); // and the three S8 upgrades, shown in the room
                    Debug.Log($"[Catchline] DAY bistro bought {bought}, stage {Kitchen.State.Stage}");
                    return bought;
                case "day-exterior": case "day-exterior2": // Mira's house on the quay at its current stage
                    RestaurantPhase = DayPhase.Off; RestaurantPreview = RestaurantScreen.None; restaurantForced = true; panelOpen = false;
                    harbourLook = (new Vector3(19f, 0, 2.5f), 8.5f); snapCamera = true; SyncHarbourScenery();
                    return true;
                case "day-harbour": // the harbour hub with Mira's entry (S14)
                    RestaurantPhase = DayPhase.Off; RestaurantPreview = RestaurantScreen.None; restaurantForced = true; panelOpen = false;
                    return true;
                case "day-plan":
                    RestaurantPhase = DayPhase.Off; SelectedSpot = 0; restaurantForced = true;
                    return RestaurantPlanBeforeSail();
                case "day-prep":
                    if (RestaurantPhase == DayPhase.Plan) { RestaurantPreview = RestaurantScreen.None; RestaurantPhase = DayPhase.Out; }
                    State.UnsoldCatch.Clear();
                    var rng = new System.Random(5);
                    foreach (var s in new[] { Species.Mackerel, Species.Mackerel, Species.Mackerel, Species.Pollock, Species.Pollock, Species.Herring, Species.Cod })
                        for (int i = 0; i < 2; i++) State.UnsoldCatch.Add(new CaughtFish { Species = s, Kg = GameData.Get(s).MinKg + (float)rng.NextDouble() * (GameData.Get(s).MaxKg - GameData.Get(s).MinKg) * .5f });
                    RestaurantArrived(true);
                    return RestaurantPhase == DayPhase.Prep;
                case "day-market":
                    if (RestaurantPhase == DayPhase.Prep) RestaurantPrepared();
                    return RestaurantPhase == DayPhase.Market;
                case "day-service":
                    if (RestaurantPhase == DayPhase.Prep) RestaurantPrepared();
                    if (RestaurantPhase == DayPhase.Market) RestaurantMarketOpen();
                    if (night == null) return false;
                    if (RestaurantPreview == RestaurantScreen.FirstNight) { RestaurantPreview = RestaurantScreen.Service; RestaurantService.Paused = false; } // seen in restaurant-firstnight
                    while (night.Hour < 19.6f && !night.Finished) night.Tick(.5f);
                    RestaurantTick(0f);
                    return RestaurantPhase == DayPhase.Service;
                case "day-service-late": // tables eating, plates on the tables
                    if (night == null) return false;
                    while (night.Hour < 21f && !night.Finished) night.Tick(.5f);
                    RestaurantTick(0f);
                    return RestaurantPhase == DayPhase.Service;
                case "day-closing":
                    if (night == null) return false;
                    while (!night.Finished) night.Tick(.5f);
                    RestaurantTick(0f);
                    return RestaurantPhase == DayPhase.Closing;
                case "day-dashboard": OpenRestaurantDashboard(); return true;
                case "day-upgrades": OpenRestaurantUpgrades(); return true;
                // Arrange by day over the real room: a table for two picked from the drawer, its ghost on the floor;
                // day-arrange-buy confirms it, day-arrange-bad drags it into the kitchen (red, with the reason).
                case "day-arrange":
                    OpenRestaurantArrange();
                    if (!ArrangeLive) return false;
                    PickArrangeItem(RestaurantArrange, 0);
                    Debug.Log($"[Catchline] ARRANGE {RestaurantArrange.Placing} at {RestaurantArrange.Tile} fits={RestaurantArrange.Fits} items={Kitchen.Active.Count()}");
                    return RestaurantArrange.Fits;
                case "day-arrange-bad":
                    ArrangeTapTile(RestaurantArrange, new Vector2Int(1, 2));
                    Debug.Log($"[Catchline] ARRANGE bad: {RestaurantArrange.Reason}");
                    return !RestaurantArrange.Fits;
                case "day-arrange-kitchen": // the kitchen drawer scrolled one card along
                    SetArrangeCategory(RestaurantArrange, 0); RestaurantArrange.Scroll = 157;
                    return RestaurantArrange.Items.Count > 3;
                case "day-arrange-buy":
                    {
                        State.Coins = Math.Max(State.Coins, 500); // a fresh save has 40
                        int had = Kitchen.Active.Count(), coins = State.Coins;
                        PickArrangeItem(RestaurantArrange, 0); ConfirmArrange(RestaurantArrange);
                        Debug.Log($"[Catchline] ARRANGE bought: items {had}->{Kitchen.Active.Count()}, coins {coins}->{State.Coins}");
                        return Kitchen.Active.Count() == had + 1;
                    }
                case "day-sleep":
                    if (RestaurantPhase != DayPhase.Closing) return false;
                    RestaurantPreview = RestaurantScreen.Sleep;
                    return true;
                // A fresh save played through its first day: the real departure, trip, catch (the bot fishes), arrival,
                // prep, a live night, closing and sleep. Each step logs what it found for the check log.
                case "new-harbour":
                    NewGame(); EndIntro(); showTitle = false; State.Tutorial = (int)TutStep.Hello; RestaurantPhase = DayPhase.Off;
                    restaurantForced = true; // the real game opens the restaurant with the Skiff; the check walks it on the rowboat
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
                    Debug.Log($"[Catchline] NEWGAME caught {Cooler.Count} fish, mode {CurrentMode}, deck {OnDeck.Count}, tutorial {Tutorial}, bait {State.HasAnyBait}, cast {AwaitingCast}, captain {(Captain.Idle ? "idle" : Captain.BusyLabel)} carrying {Captain.Carrying != null}, minigame {MinigameRod != null}, manning {Manning != null}, rods {string.Join(",", Rods.Select(r => r.State + (r.Unlocked ? "" : "(locked)") + (CanCommandRod(r) ? "*" : "") + $" reading {r.Reading?.Phase} result {r.ReadingResult} castAge {r.CastAge:0}"))}, strikeRod {botStrikeRod != null}, landed {Stats.Landed} spooked {Stats.Spooked} missed {Stats.Missed} lost {Stats.Lost}, unsold {State.UnsoldCatch.Count}, graph {UsesDeckGraph}, baskets {(DeckGraph == null ? "-" : string.Join(",", DeckGraph.Baskets.Select(b => b.Id + ":" + b.Fish.Count)))}, loose {Scheduler?.Loose.Count}, hold {HoldKg:0.0}/{State.CoolerCapacity}");
                    return CurrentMode == Mode.Fishing && Cooler.Count > 0;
                case "new-prep":
                    HeadHome();
                    for (int n = 0; n < 40000 && RestaurantPhase == DayPhase.Out; n++) Tick(.05f);
                    Debug.Log($"[Catchline] NEWGAME home: phase {RestaurantPhase}, {State.UnsoldCatch.Count} fish, rows {string.Join("/", RestaurantPrep.Rows.Select(r => r.Name + " " + r.Portions))}, market {RestaurantPrep.MarketFish}");
                    return RestaurantPhase == DayPhase.Prep;
                case "new-service":
                    RestaurantPrepared();
                    if (RestaurantPhase == DayPhase.Market) RestaurantMarketOpen();
                    Debug.Log($"[Catchline] NEWGAME first night card {RestaurantPreview == RestaurantScreen.FirstNight}, paused {RestaurantService.Paused}");
                    if (RestaurantPreview == RestaurantScreen.FirstNight) { RestaurantPreview = RestaurantScreen.Service; RestaurantService.Paused = false; } // the player taps the card
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
