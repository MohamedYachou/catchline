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
            [Dish.PanFish] = ("Fillets", "v2-dish-pan-fish", "fish-pollock"),
            [Dish.FishAndChips] = ("Fish & chips", "v2-dish-fish-and-chips", "icon-food"),
            [Dish.Soup] = ("Fish soup", "v2-dish-fish-soup", "icon-food"),
            [Dish.Platter] = ("Oven platter", "v2-dish-platter", "icon-food"),
            [Dish.Crab] = ("Crab", "v2-dish-crab", "fish-crab"),
            [Dish.Calamari] = ("Calamari", "v2-dish-calamari", "icon-squid"),
            [Dish.Coffee] = ("Coffee", "v2-dish-coffee", "v2-icon-cup"),
            [Dish.Tea] = ("Tea", "v2-dish-tea", "v2-icon-cup"),
            [Dish.Lemonade] = ("Lemonade", "v2-dish-lemonade", "v2-icon-cup"),
            [Dish.Beer] = ("Beer", "v2-dish-beer", "v2-icon-cup"),
            [Dish.Fries] = ("Fries", "v2-dish-fries", "icon-food"),
            [Dish.Bread] = ("Bread", "v2-dish-bread", "icon-food"),
        };
        static readonly Dictionary<PreparedForm, Dish> FormDish = new()
        {
            [PreparedForm.Whole] = Dish.GrilledFish, [PreparedForm.Fillet] = Dish.PanFish, [PreparedForm.Stock] = Dish.Soup,
            [PreparedForm.Platter] = Dish.Platter, [PreparedForm.Crab] = Dish.Crab, [PreparedForm.Squid] = Dish.Calamari,
        };
        // Guests write the reviews. Stand-in faces (deck portraits of people not on the night's staff) until the guest
        // portraits of RESTAURANT-MIRA-FISH-ART-1 D2 arrive.
        static readonly string[] GuestFaces = { "guest-ada", "guest-ben", "guest-cora", "guest-dan", "guest-edda", "guest-finn", "guest-gus", "guest-hazel", "guest-ivo", "guest-jonas", "guest-kai", "guest-lena",
            "guest-marta", "guest-nils", "guest-pia", "guest-greta", "guest-henrik", "guest-zola", "guest-vera", "guest-anton" };
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
            if (special != null)
            {
                // Codex 1's reservation card: who booked (a guest face), how many, and the dish they ask for.
                var face = GuestFaces[special.Id % GuestFaces.Length];
                if (face == "guest-pia") face = "guest-marta"; // Pia is a child: her mother books the table
                v.ReservationFace = "v2-" + face; v.ReservationName = Cap(face.Substring(6));
                v.ReservationParty = dayForecast.Guests.Count(g => g.Group == special.Group);
                v.ReservationDish = Look(special.Dish).name; v.ReservationDishArt = Look(special.Dish).art;
                v.SpecialTitle = $"A table for {v.ReservationParty}";
            }
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
            toastUntil = 0; // the market's sale line belongs to the morning, not over the room (RESTAURANT-REVIEW-2)
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
            night = new RestaurantSim(State.Voyage * 104729, Kitchen, dayForecast, stock, staff) { Breakdowns = State.RestaurantNights.Count > 0, Events = State.RestaurantNights.Count > 0 }; // the tutorial night stays plain
            // The room in 3D behind the service HUD; the day loop ticks the rules, the world only draws them.
            restaurantWorld ??= gameObject.AddComponent<RestaurantWorld>();
            restaurantWorld.DriveSimulation = false;
            try { restaurantWorld.Begin(night); }
            catch (Exception e) { Debug.LogError("[Catchline] restaurant room failed: " + e.Message); }
            popularityBefore = restaurantPopularity;
            staffLoad.Clear(); miraSaid.Clear(); miraLines.Clear(); captainFix = captainTable = 0; miraCall = null; miraCallUntil = 0;
            coachLines.Clear(); coachLine = null; coachOff = State.RestaurantNights.Count > 0;
            nightStock = (night.Stock.Where(s => s.Form != PreparedForm.Stock).Sum(s => s.Count), night.Stock.Where(s => s.Form == PreparedForm.Stock).Sum(s => s.Count));
            RestaurantService.Rail = RestaurantRailMode.Scroll;
            RestaurantService.QuestionTitle = null;
            RestaurantService.Paused = false; RestaurantService.Speed = 1;
            RestaurantPhase = DayPhase.Service;
            RestaurantPreview = RestaurantScreen.Service;
            // The very first night opens on Mira's coaching card, the service paused behind it.
            if (State.RestaurantNights.Count == 0 && HasUi("rx-s13-background")) { RestaurantPreview = RestaurantScreen.FirstNight; RestaurantService.Paused = true; }
            miraSaid.Add("open"); miraLines.Enqueue("Doors open! Service starts at 18:00.");
            if (HasUi("rx-transition-evening-phone")) Transition("evening");
        }

        // Per frame while the night runs: tick the rules, then refresh the service screen's numbers.
        void RestaurantTick(float dt)
        {
            if (RestaurantPhase == DayPhase.Prep && RestaurantPrep.Margin != prepMargin && dayPrep != null) SuggestPrep();
            if (RestaurantPhase != DayPhase.Service || night == null) return;
            var v = RestaurantService;
            if (!v.Paused) { night.Tick(dt * Mathf.Max(1, v.Speed)); CaptainWork(dt * Mathf.Max(1, v.Speed)); }
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
            MiraCalls(fish, soup, broken);
            if (night.Finished) ShowClosing();
        }

        // The manager helps where it hurts (design section 6): tap a broken station and the captain goes to fix it;
        // tap a table and he works that table first (tap it again to let him help everywhere).
        int captainFix, captainTable;
        void ServiceTap()
        {
            var p = UnityEngine.InputSystem.Pointer.current;
            if (p == null || night == null || restaurantWorld == null) return;
            var at = p.position.ReadValue();
            if (restaurantWorld.TileAt(new Vector2(at.x / Screen.width, at.y / Screen.height), out var tile)) ServiceTapTile(tile);
        }

        bool ServiceTapTile(Vector2Int tile)
        {
            var hit = Kitchen.Active.FirstOrDefault(i => Kitchen.Cells(i).Contains(tile));
            if (hit == null || night.Finished) return false;
            var d = RestaurantData.Get(hit.Id);
            if (night.Broken.Contains(hit.Uid))
            {
                captainFix = hit.Uid; Toast($"Captain: on it, fixing the {d.Name.ToLower()}.");
                audio?.Play(VoyageAudio.Cue.Select, .4f); return true;
            }
            if (d.Seats == 0 || !night.Pin(hit.Uid)) return false;
            captainTable = captainTable == hit.Uid ? 0 : hit.Uid;
            restaurantWorld.Mark(captainTable == 0 ? null : hit);
            Toast(captainTable != 0 ? "Captain: I'll take this table first." : "Captain: back to helping everywhere.");
            audio?.Play(VoyageAudio.Cue.Select, .4f);
            return true;
        }

        void CaptainWork(float dt)
        {
            if (captainFix == 0) return;
            if (night.Broken.Contains(captainFix)) { night.CaptainHoldFix(captainFix, dt); if (night.Broken.Contains(captainFix)) return; }
            var item = Kitchen.Active.FirstOrDefault(i => i.Uid == captainFix);
            if (item != null) Toast($"Captain: the {RestaurantData.Get(item.Id).Name.ToLower()} works again.");
            captainFix = 0;
        }

        // Mira's calls during service (design section 9): each moment once a night, in her words.
        readonly HashSet<string> miraSaid = new();
        string miraCall; float miraCallUntil;
        // Codex 1's Mira expressions for each call: worried at trouble, excited at a party, proud at the last plates.
        readonly Dictionary<string, string> miraMood = new();
        static string MoodOf(string key) => key is "birthday" or "tour" ? "excited" : key is "queue" or "no-fish" or "no-soup" || key.StartsWith("broken-") ? "worried"
            : key == "door" ? "proud" : "happy";
        string MiraSprite(string line, string use)
        {
            string s = $"rx-mira-{(line != null && miraMood.TryGetValue(line, out var m) ? m : "happy")}-{use}";
            return HasUi(s) ? s : use == "call" ? "rx-s2-call-mira" : "rx-coach-mira";
        }
        void CloseServiceDoor()
        {
            if (night == null || night.DoorClosed) return;
            night.CloseDoor(); audio?.Play(VoyageAudio.Cue.Select, .45f);
        }
        (int fish, int soup) nightStock; // portions at the doors opening
        readonly Queue<string> coachLines = new(); string coachLine; bool coachPaused, coachOff;
        // Got it shows the next line or lets the night run again; Skip ends the coaching (never the service).
        void CoachNext(bool skip)
        {
            if (skip) { coachOff = true; coachLines.Clear(); }
            coachLine = null; RestaurantService.Paused = coachPaused;
            audio?.Play(VoyageAudio.Cue.Select, .4f);
        }
        readonly Queue<string> miraLines = new(); // one toast at a time, so quick moments at ×2 don't overwrite each other
        void MiraCalls(int fish, int soup, List<RestaurantItem> broken)
        {
            if (RestaurantPreview == RestaurantScreen.FirstNight) return;
            void Say(string key, string line)
            {
                if (miraSaid.Add(key)) { miraLines.Enqueue(line); miraMood[line] = MoodOf(key); Debug.Log($"[Catchline] MIRA {night.Hour:0.0}h {line}"); }
            }
            if (night.Groups.Any(g => g.TableUid != 0)) Say("seated", "First table seated. Here we go!");
            if (night.Groups.Any(g => g.Birthday && g.TableUid != 0)) Say("birthday", "A birthday at our table! Make it special.");
            if (night.Groups.Any(g => g.Count >= 6 && g.TableUid != 0)) Say("tour", "A tour group of six! All hands!");
            if (night.Groups.Any(g => g.Regular && g.TableUid != 0)) Say("regular", "Our regular is here. The usual!");
            if (night.Groups.Count(g => g.Phase == GroupPhase.Queue) >= 3) Say("queue", "The queue's growing, Captain!");
            if (fish == 0 && nightStock.fish > 0 && !night.DoorClosed) Say("no-fish", "We're out of fish!");
            if (soup == 0 && nightStock.soup > 0 && !night.DoorClosed) Say("no-soup", "Soup's all gone!");
            foreach (var b in broken) Say("broken-" + b.Uid, $"The {RestaurantData.Get(b.Id).Name.ToLower()} broke! Sending help.");
            if (night.DoorClosed) Say("door", "Doors closed. Last plates!");
            // The first night's coaching (Codex 1's coach card): the service waits while Mira explains the two controls.
            void Coach(string key, string line) { if (!coachOff && miraSaid.Add("coach-" + key)) coachLines.Enqueue(line); }
            if (night.Groups.Any(g => g.TableUid != 0 && g.Phase != GroupPhase.Seating)) Coach("pin", "Tap a table and I'll send the crew there first. Tap a broken station and you fix it yourself.");
            if (night.Hour >= 21 && !night.DoorClosed) Coach("door", "When the queue thins out, close the door up top. We finish the last plates, then count the till.");
            if (coachLine == null && coachLines.Count > 0 && HasUi("rx-coach-panel"))
            {
                coachLine = coachLines.Dequeue(); coachPaused = RestaurantService.Paused; RestaurantService.Paused = true;
                audio?.Play(VoyageAudio.Cue.CoachPop, .35f);
            }
            // Her lines go to the S2 call strip when Codex 1's sheet is in, else the toast.
            bool strip = HasUi("rx-s2-call-bubble");
            if (miraLines.Count > 0 && SimTime >= (strip ? miraCallUntil : toastUntil) - 1.2f)
            {
                var line = miraLines.Dequeue();
                if (strip) { miraCall = line; miraCallUntil = SimTime + 3.6f; } else Toast("Mira: " + line);
                audio?.Play(VoyageAudio.Cue.CoachPop, .25f);
            }
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
            var paid = night.Groups.Where(g => g.Paid).OrderByDescending(g => g.Stars).ThenByDescending(g => g.Why is "birthday" or "regular").ThenBy(g => g.Id).ToList();
            var speak = paid.Count <= 3 ? paid : new List<ServiceGroup> { paid[0], paid[paid.Count / 2], paid[^1] };
            // When the queue lost a lot of guests, one of them has the last word.
            var walked = night.Groups.FirstOrDefault(g => !g.Paid && g.Phase == GroupPhase.Gone);
            if (walked != null && r.Left * 3 >= r.Guests) { walked.Stars = 1; walked.Why = "queue"; if (speak.Count >= 3) speak[^1] = walked; else speak.Add(walked); }
            var quoted = new HashSet<string>();
            var faces = new HashSet<string>(); // three different people speak
            v.Reviews = speak.Select((g, i) => new RestaurantReview
            {
                Portrait = Enumerable.Range(0, GuestFaces.Length).Select(k => GuestFaces[(g.Id * 7 + i + k) % GuestFaces.Length]).First(faces.Add), Stars = Mathf.Clamp(g.Stars, 1, 5),
                Quote = Enumerable.Range(i, 3).Select(k => ReviewQuote(g, k)).FirstOrDefault(quoted.Add) ?? ReviewQuote(g, i),
            }).ToList();
            Debug.Log($"[Catchline] EVENTS birthday {night.Groups.Count(g => g.Birthday)} regular {night.Groups.Count(g => g.Regular)} happy regulars {r.HappyRegulars} tips {r.Tips} served {r.Served}/{r.Guests} pop +{r.PopularityGain:0.00}");
            Debug.Log("[Catchline] REVIEWS " + string.Join(" | ", speak.Select(g => $"{g.Stars}* {g.Why}")) + " :: " + string.Join(" | ", v.Reviews.Select(x => x.Quote)));
            v.MiraLine = r.Served >= r.Guests * .8f ? "Same time tomorrow?" : "Better tomorrow!";
            v.Title = r.Served >= r.Guests * .8f ? "A good night on the quay" : r.Served * 2 >= r.Guests ? "A busy night on the quay" : "A rough night on the quay";
            // Codex 1's S5 stamps: the best takings so far (from the second night on) and a night nobody walked out of.
            var before = State.RestaurantNights.Select(n => n.Split('|')).Where(p => p.Length >= 2 && int.TryParse(p[1], out _)).Select(p => int.Parse(p[1])).ToList();
            v.BestNight = before.Count > 0 && r.NetCoins > before.Max();
            v.FullHouse = r.Left == 0 && r.Guests >= 6 && r.Served >= r.Guests;
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

        // The reliable stove is a Bistro kitchen part (Codex 1's S8 "Needs Bistro" state); the others fit the Café.
        public static readonly (string id, string name, string effect, int cost, int stage)[] RestaurantUpgrades =
        {
            ("BigFridge", "Bigger fridge", "+15 portions", 600, 1), ("ReliableStove", "Reliable stove", "Fewer breakdowns", 450, 2),
            ("CosyLighting", "Cosy lighting", "More guest patience", 300, 1),
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
                "birthday" => Pick("Best birthday ever!", "What a birthday treat!"),
                "regular" => Pick("My usual. Perfect!", "Same table, same joy."),
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
            // Stored items come first and cost nothing to put back; then the shop.
            v.Items = Kitchen.State.Items.Where(i => i.Stored && areas.Contains(RestaurantData.Get(i.Id).Area)).Select(i => RestaurantData.Get(i.Id))
                .Zip(Kitchen.State.Items.Where(i => i.Stored && areas.Contains(RestaurantData.Get(i.Id).Area)), (d, i) => new RestaurantShopItem
                    { Id = d.Id, Name = ArrangeName(d), Art = "v2-item-rest-" + ArrangeArtKey(d.Id), Footprint = $"{d.Width}×{d.Height}", Price = 0, StoredUid = i.Uid })
                .Concat(RestaurantData.Items.Where(d => areas.Contains(d.Area) && d.Id != ItemId.Reception && d.Stage <= Kitchen.State.Stage)
                .Select(d => new RestaurantShopItem { Id = d.Id, Name = ArrangeName(d), Art = "v2-item-rest-" + ArrangeArtKey(d.Id), Footprint = $"{d.Width}×{d.Height}", Price = d.Price }))
                // ...and a taste of the next stage, locked under its name.
                .Concat(RestaurantData.Items.Where(d => areas.Contains(d.Area) && d.Id != ItemId.Reception && d.Stage == Kitchen.State.Stage + 1)
                .Select(d => new RestaurantShopItem { Id = d.Id, Name = ArrangeName(d), Art = "v2-item-rest-" + ArrangeArtKey(d.Id), Footprint = $"{d.Width}×{d.Height}", Price = d.Price,
                    Lock = RestaurantData.Stage(d.Stage).Name == "Cafe" ? "Café" : RestaurantData.Stage(d.Stage).Name, LockStage = d.Stage }))
                .ToList();
        }

        // A card picked from the drawer: its ghost starts on the free tile nearest the middle of the floor that takes it.
        void PickArrangeItem(RestaurantArrangeView v, int i)
        {
            CancelArrange(v);
            if (v.Items[i].Lock != null) { Toast($"Unlocks with the {v.Items[i].Lock} (stage {v.Items[i].LockStage})."); return; }
            var id = v.Items[i].Id; var st = Kitchen.Stage;
            v.Selected = i; v.PlaceId = id; v.Rotated = false;
            v.LiftUid = v.Items[i].StoredUid; v.FromStore = v.LiftUid != 0; // a stored item is put back with Move
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
            v.PlaceId = null; v.LiftUid = 0; v.Selected = -1; v.Placing = null; v.FromStore = false;
            restaurantWorld?.Ghost(null, default, false, false);
        }

        // Store keeps the lifted item for later (it waits in the drawer); Sell gives part of its price back.
        void StoreOrSellArrange(RestaurantArrangeView v, bool sell)
        {
            if (v.LiftUid == 0) return;
            var st = Kitchen.State; st.Coins = State.Coins;
            var before = (JsonUtility.ToJson(new ItemsOnly { Items = st.Items }), st.NextUid, State.Coins);
            var r = sell ? Kitchen.Sell(v.LiftUid) : Kitchen.Store(v.LiftUid);
            if (!r.Ok) { Toast(r.Message); return; }
            v.Undo.Add(before); State.Coins = st.Coins;
            StoreRestaurant(); SaveGame();
            audio?.Play(sell ? VoyageAudio.Cue.Purchase : VoyageAudio.Cue.Select, .5f);
            v.PlaceId = null; v.LiftUid = 0; v.Selected = -1; v.Placing = null;
            restaurantWorld.Show(Kitchen);
            SetArrangeCategory(v, v.Category);
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
            v.PlaceId = null; v.LiftUid = 0; v.Selected = -1; v.Placing = null; v.FromStore = false;
            restaurantWorld.Show(Kitchen);
            SetArrangeCategory(v, v.Category);
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

        string upgradeBought; float upgradeBoughtAt;
        bool BuyRestaurantUpgrade(string id)
        {
            var u = RestaurantUpgrades.First(x => x.id == id);
            if (Kitchen.HasUpgrade(id) || State.Coins < u.cost || Kitchen.State.Stage < u.stage) return false;
            State.Coins -= u.cost; Kitchen.State.Upgrades.Add(id);
            upgradeBought = id; upgradeBoughtAt = SimTime; // the S8 sparkle
            StoreRestaurant(); SaveGame();
            audio?.Play(VoyageAudio.Cue.Purchase, .6f);
            Toast($"{u.name}: {u.effect.ToLowerInvariant()}.");
            return true;
        }

        // The restaurant keeps its own calendar: night 0 is a Monday. Tomorrow's weather is rolled at bedtime and shown
        // on the sleep card, so the plan card and the forecast agree with it.
        static DayOfWeek RestaurantWeekday(int day) => (DayOfWeek)((day + 1) % 7);
        static string WeatherWords(Weather w) => w == Weather.Sun ? "Clear skies" : w == Weather.Rain ? "Rain" : "Some clouds";

        // One line per night for the dashboard: "day|net|dishes|drinks|tips|popularity|served|left|Dish=n;...".
        void RecordNight(NightResult r)
        {
            var sold = night.Groups.SelectMany(g => g.Tickets).Where(t => t.Phase == TicketPhase.Delivered)
                .GroupBy(t => t.Dish).Select(g => $"{g.Key}={g.Count()}");
            var crew = r.Walking.OrderByDescending(w => w.Metres).FirstOrDefault(w => w.Id != "mira" && w.Id != "captain")?.Id ?? "mira"; // the crew award, not the manager
            State.RestaurantNights.Add(string.Join("|", State.RestaurantDay, r.NetCoins, r.DishCoins, r.DrinkCoins, r.Tips, restaurantPopularity, r.Served, r.Left, string.Join(";", sold), crew));
            if (State.RestaurantNights.Count % 7 == 0) FillWeek();
            while (State.RestaurantNights.Count > 14) State.RestaurantNights.RemoveAt(0);
        }
        // The seventh night closes a week: S16 sums the last seven records (day|net|dishes|drinks|tips|popularity|served|left|sold|crew).
        bool weekDone;
        bool WeekDone() { bool d = weekDone && HasUi("rx-s16-background"); weekDone = false; return d; }
        void FillWeek()
        {
            var rec = State.RestaurantNights.Skip(State.RestaurantNights.Count - 7).Select(n => n.Split('|')).ToList();
            var all = State.RestaurantNights.Select(n => n.Split('|')).ToList();
            var v = RestaurantWeek;
            v.Nights = rec.Select(p => int.TryParse(p[1], out var c) ? c : 0).ToArray();
            v.Days = new string(rec.Select(p => "MTWTFSS"[(int.TryParse(p[0], out var d) ? d : 0) % 7]).ToArray());
            var dishes = rec.Where(p => p.Length > 8).SelectMany(p => p[8].Split(';')).Select(s => s.Split('=')).Where(s => s.Length == 2 && int.TryParse(s[1], out _))
                .GroupBy(s => s[0]).Select(g => (dish: g.Key, n: g.Sum(s => int.Parse(s[1])))).OrderByDescending(x => x.n).FirstOrDefault();
            if (dishes.dish != null && System.Enum.TryParse<Dish>(dishes.dish, out var best)) { v.Dish = Look(best).name; v.DishArt = Look(best).art; v.DishCount = dishes.n; }
            var crew = rec.Where(p => p.Length > 9 && p[9] != "captain").GroupBy(p => p[9]).OrderByDescending(g => g.Count()).FirstOrDefault()?.Key ?? "mira";
            v.CrewId = crew; v.Crew = Cap(crew); v.Quote = "Most steps on the floor this week.";
            int Pop(string[] p) => p.Length > 5 && float.TryParse(p[5], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out var x) ? Mathf.RoundToInt(x) : 0;
            v.PopularityTo = Pop(rec[^1]);
            v.PopularityFrom = all.Count > 7 ? Pop(all[all.Count - 8]) : Pop(rec[0]);
            weekDone = true;
            Debug.Log($"[Catchline] WEEK {string.Join(",", v.Nights)} best dish {v.Dish} x{v.DishCount} crew {v.Crew} pop {v.PopularityFrom}->{v.PopularityTo}");
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
            if (HasUi("rx-transition-morning-phone")) Transition("morning"); else Toast("A new morning in Gull Harbour.");
        }

        // ---- capture / test: walks the real day without sailing (VoyageUiV2Capture "day-*" steps) -----------------

        public bool StageRestaurantDay(string step)
        {
            bool ok = StageRestaurantDayStep(step);
            // The hand-off cards and Mira's queued calls run on real time, which captures freeze: settle them per step.
            if (step != "day-evening" && step != "day-morning") transitionCard = null;
            if (night != null && step.StartsWith("day-service")) { while (miraLines.Count > 0) miraCall = miraLines.Dequeue(); miraCallUntil = SimTime + 3.6f; }
            return ok;
        }

        bool StageRestaurantDayStep(string step)
        {
            switch (step)
            {
                case "day-evening": // the market closes: Evening falls over the quay before service
                    if (night == null) { RestaurantPrepared(); if (RestaurantPhase == DayPhase.Market) RestaurantMarketOpen(); }
                    return transitionCard == "evening";
                case "day-morning": // after sleep: Good morning over the harbour
                    if (night == null) return false;
                    RestaurantSleep();
                    return transitionCard == "morning";
                case "day-bistro": // buys stage 2 so the next night runs in the Bistro room
                    State.Coins += 100000; restaurantPopularity = 50;
                    bool bought = BuyRestaurantStage(); RestaurantPreview = RestaurantScreen.None;
                    foreach (var (id, _, _, _, _) in RestaurantUpgrades) BuyRestaurantUpgrade(id); // and the three S8 upgrades, shown in the room
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
                case "day-service-help": // the manager's taps: the stove breaks, a tap sends the captain; a table tap pins it
                    {
                        if (night == null) return false;
                        var stove = Kitchen.Active.First(i => i.Id == ItemId.Stove); night.Break(stove.Uid);
                        bool sent = ServiceTapTile(new Vector2Int(stove.X, stove.Y));
                        float t = 0; while (night.Broken.Contains(stove.Uid) && t < 120) { night.Tick(.25f); CaptainWork(.25f); t += .25f; }
                        var table = Kitchen.Active.First(i => RestaurantData.Get(i.Id).Seats > 0);
                        bool pinned = ServiceTapTile(new Vector2Int(table.X, table.Y));
                        Debug.Log($"[Catchline] HELP sent {sent}, stove fixed after {t:0.0}s ({!night.Broken.Contains(stove.Uid)}), table {table.Uid} pinned {pinned} ({captainTable})");
                        RestaurantTick(0f);
                        return sent && pinned && !night.Broken.Contains(stove.Uid);
                    }
                case "day-service-orders": // a table waiting for its food: order bubble, patience, task icons, Mira's call strip
                    {
                        if (night == null) { RestaurantPrepared(); if (RestaurantPhase == DayPhase.Market) RestaurantMarketOpen(); }
                        if (night == null) return false;
                        if (RestaurantPreview == RestaurantScreen.FirstNight) { RestaurantPreview = RestaurantScreen.Service; RestaurantService.Paused = false; }
                        while (!night.Finished && night.Hour < 22 && !night.Groups.Any(g => g.TableUid != 0 && g.Phase == GroupPhase.Kitchen)) night.Tick(.25f);
                        var waiting = night.Groups.FirstOrDefault(g => g.TableUid != 0 && g.Phase == GroupPhase.Kitchen);
                        if (waiting != null && !night.Groups.Any(g => g.Birthday)) waiting.Birthday = true; // the capture shows the event marker too
                        miraLines.Clear(); coachOff = true; coachLine = null; RestaurantTick(0f);
                        Debug.Log($"[Catchline] ORDERS at {night.Hour:0.00}h waiting {waiting?.Id} staff {string.Join(",", night.Staff.Select(x => x.Action))} call '{miraCall}'");
                        return waiting != null;
                    }
                case "day-service-coach": // the first night's coach card over the running service
                    {
                        if (night == null) { RestaurantPrepared(); if (RestaurantPhase == DayPhase.Market) RestaurantMarketOpen(); }
                        if (night == null) return false;
                        if (RestaurantPreview == RestaurantScreen.FirstNight) { RestaurantPreview = RestaurantScreen.Service; RestaurantService.Paused = false; }
                        coachOff = false;
                        while (!night.Finished && night.Hour < 22 && coachLine == null) { night.Tick(.25f); RestaurantTick(0f); }
                        Debug.Log($"[Catchline] COACH at {night.Hour:0.00}h '{coachLine}' paused {RestaurantService.Paused}");
                        return coachLine != null;
                    }
                case "day-service-closed": // door shut: the Closed board over the entrance, last plates going out
                    if (night == null) return false;
                    coachLine = null; coachOff = true; RestaurantService.Paused = false;
                    night.CloseDoor();
                    while (night.Hour < 22.2f && !night.Finished) night.Tick(.25f);
                    RestaurantTick(0f);
                    return RestaurantPhase == DayPhase.Service;
                case "day-service-paused": // the player holds the night: Codex 1's pause panel
                    if (night == null) return false;
                    coachOff = true; coachLine = null; RestaurantService.Paused = true;
                    return true;
                case "day-service-moods": // one table's patience running out (annoyed), the next about to walk (leaving)
                    {
                        if (night == null) return false;
                        coachOff = true; coachLine = null; RestaurantService.Paused = false;
                        var waiting = night.Groups.Where(g => g.TableUid != 0 && (g.Phase == GroupPhase.Kitchen || g.Phase == GroupPhase.Order)).ToList();
                        if (waiting.Count > 0) waiting[0].SeatedAt = night.Seconds - RestaurantTuning.TablePatience * .85f; // capture only: shows the warning states
                        if (waiting.Count > 1) waiting[1].SeatedAt = night.Seconds - RestaurantTuning.TablePatience * .95f;
                        RestaurantTick(0f);
                        Debug.Log($"[Catchline] MOODS waiting {waiting.Count} eating {night.Groups.Count(g => g.Phase == GroupPhase.Eating)}");
                        return waiting.Count > 0;
                    }
                case "day-service-late": // tables eating, plates on the tables
                    if (night == null) return false;
                    coachOff = true; coachLine = null; RestaurantService.Paused = false;
                    while (night.Hour < 21f && !night.Finished) night.Tick(.5f);
                    RestaurantTick(0f);
                    return RestaurantPhase == DayPhase.Service;
                case "day-closing":
                    if (night == null) return false;
                    while (!night.Finished) night.Tick(.5f);
                    RestaurantTick(0f);
                    return RestaurantPhase == DayPhase.Closing;
                case "day-week": // capture only: the real closing's record repeated into a week (varied takings), then S16 from it
                    {
                        if (State.RestaurantNights.Count == 0) return false;
                        var last = State.RestaurantNights[^1].Split('|');
                        for (int d = 1; State.RestaurantNights.Count % 7 != 0; d++)
                        {
                            var p = (string[])last.Clone(); p[0] = (int.Parse(last[0]) + d).ToString(); p[1] = (int.Parse(last[1]) * (4 + d % 3 + d) / 5).ToString();
                            State.RestaurantNights.Add(string.Join("|", p));
                        }
                        FillWeek();
                        RestaurantPreview = WeekDone() ? RestaurantScreen.Week : RestaurantScreen.None;
                        return RestaurantPreview == RestaurantScreen.Week;
                    }
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
                case "day-arrange-lift": // lift the bought table: store / sell show beside rotate
                    {
                        var t = Kitchen.Active.Last(i => i.Id == ItemId.Table2);
                        ArrangeTapTile(RestaurantArrange, new Vector2Int(t.X, t.Y));
                        return RestaurantArrange.LiftUid == t.Uid;
                    }
                case "day-arrange-store":
                    {
                        int had = Kitchen.Active.Count();
                        StoreOrSellArrange(RestaurantArrange, false);
                        SetArrangeCategory(RestaurantArrange, 1);
                        Debug.Log($"[Catchline] ARRANGE stored: active {had}->{Kitchen.Active.Count()}, drawer first {RestaurantArrange.Items[0].Name} free {RestaurantArrange.Items[0].Price == 0}");
                        return Kitchen.Active.Count() == had - 1 && RestaurantArrange.Items[0].StoredUid != 0;
                    }
                case "day-arrange-poor": // the guests drawer when the wallet is short: the stored table, then a card it can't pay for
                    State.Coins = 90; SetArrangeCategory(RestaurantArrange, 1); RestaurantArrange.Scroll = 0;
                    return RestaurantArrange.Items.Any(i => i.StoredUid == 0 && i.Price > State.Coins);
                case "day-dash-stored": // after day-arrange-store: the dashboard's Arrange tab counts the piece waiting in the store
                    CloseRestaurantArrange(); OpenRestaurantDashboard();
                    return Kitchen.State.Items.Any(i => i.Stored);
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
