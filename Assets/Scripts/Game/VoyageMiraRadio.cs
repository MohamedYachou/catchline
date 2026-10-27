using System;
using System.Collections.Generic;
using System.Linq;
using Catchline.Game.Restaurant;
using UnityEngine;

namespace Catchline.Game
{
    // Design 14.3-14.4 (Mo 10-27): Mira is the captain's assistant at sea. On the way out she takes the restaurant's
    // calls and puts each to the captain as a card (bookings with a haggle, the hotel's contract, Lotte's lemons, Old
    // Bram's repair, her own tips); the boat sails on and waits at the ground until every call is answered. Her
    // notebook (the pinned ticket) keeps tonight's list as the answers change it. On the way home the crew prep
    // tonight's portions on deck, the captain can lend a knife, and the boat comes in when the work is done.
    public partial class VoyageGame
    {
        public sealed class RadioOption { public string Label, Reply; public Func<bool> Can; public Action Apply; public Func<RadioCall> Then; public bool Enabled => Can?.Invoke() ?? true; }
        public sealed class RadioCall { public string Caller, Face, Line, Mood = "happy"; public readonly List<RadioOption> Options = new(); }
        // The people who ring the restaurant, back day after day.
        sealed class Regular { public string Name, Short, Face; public int Size; public Regular(string name, string shortName, string face, int size) { Name = name; Short = shortName; Face = face; Size = size; } }
        static readonly Regular[] Bookers =
        {
            new("Mr Peeters", "the Peeters", "v2-guest-ben", 4), new("Mrs Janssen", "the Janssens", "v2-guest-edda", 2),
            new("Vera and Kai", "Vera and Kai", "v2-guest-vera", 2), new("The rowing club", "the rowing club", "v2-guest-jonas", 6),
            new("Grandma Greta", "Greta's family", "v2-guest-greta", 4),
        };
        static readonly Regular Hotel = new("Mrs Haverkamp, Harbour Hotel", "the hotel", "v2-guest-marta", 0), Lotte = new("Lotte, greengrocer", "Lotte", "v2-guest-lena", 0),
            Bram = new("Old Bram, repairs", "Bram", "v2-guest-gus", 0), Henrik = new("Henrik, fishmonger", "Henrik", "v2-guest-henrik", 0);

        readonly List<RadioCall> radioQueue = new();
        readonly List<(float at, Func<RadioCall> call)> radioLater = new();
        readonly List<(string text, float at)> radioNotes = new();
        public RadioCall RadioOpen { get; private set; }
        public bool RadioAuto; // captures and checks answer with the first option
        float radioWait, radioOpenedAt, radioReplyUntil, radioStoveAt = -1, prepWork, prepDone, prepPop;
        string radioReply, radioReplyMood = "happy";
        int radioPriceBonus; bool radioRepairBooked, radioStoveRisk; Species? radioMarketSpecies;
        readonly HashSet<CaughtFish> radioReserved = new();

        bool RadioDay => dayForecast != null && (RestaurantPhase == DayPhase.Out || RestaurantPhase == DayPhase.Home);
        // Out: the boat waits at the ground while Mira still has someone on the line.
        bool RadioHolds => RestaurantPhase == DayPhase.Out && dayForecast != null && (RadioOpen != null || radioQueue.Count > 0 || radioLater.Count > 0);
        float PrepU => prepWork <= 0 ? 1 : Mathf.Clamp01(prepDone / prepWork);
        bool PrepHolds => RestaurantPhase == DayPhase.Home && PrepU < 1;
        // Home: the sail lasts as long as the work, so the boat eases off when the knives fall behind.
        float RadioPace => !PrepHolds ? 1f : Mathf.Clamp(PrepU / Mathf.Max(.05f, TravelProgress), .3f, 1f);
        int PrepWorkers => Mathf.Max(1, (State.TripDeployment.Count > 0 ? State.TripDeployment : State.Deployment).Count(id => id != "mira"));

        void Note(string text) => radioNotes.Add((text, SimTime));
        void RadioSay(string reply, string mood = "happy") { radioReply = reply; radioReplyMood = mood; radioReplyUntil = SimTime + 3.4f; }
        RadioCall Call(Regular who, string line, string mood = "happy") => new() { Caller = who?.Name, Face = who?.Face, Line = line, Mood = mood };
        RadioCall Mira(string line, string mood = "happy") => new() { Caller = "Mira", Line = line, Mood = mood };
        static RadioOption Opt(string label, Action apply = null, string reply = null, Func<bool> can = null, Func<RadioCall> then = null) => new() { Label = label, Apply = apply, Reply = reply, Can = can, Then = then };
        static int Round5(float v) => Mathf.Max(5, Mathf.RoundToInt(v / 5f) * 5);
        static string Plural(int n, string word) => n == 1 ? word : word + "s";

        // ---- the day starts: the notebook and the calls for the way out -----------------------------------------
        void RadioBeginDay()
        {
            radioQueue.Clear(); radioLater.Clear(); radioNotes.Clear(); radioReserved.Clear(); RadioOpen = null; radioReply = null;
            radioPriceBonus = 0; radioRepairBooked = radioStoveRisk = false; radioMarketSpecies = null; radioStoveAt = -1; prepWork = prepDone = 0;
            radioWait = 2.5f;
            var r = new System.Random(State.Voyage * 7349 + State.RestaurantDay * 31);
            Note($"{dayForecast.GuestRange.Min}-{dayForecast.GuestRange.Max} guests");
            foreach (var g in dayForecast.DishRanges.GroupBy(k => k.Key.Item1).OrderByDescending(g => g.Sum(x => x.Value.Max)).Take(2))
                Note($"{Cap(FishName(g.Key))}: {g.Sum(x => x.Value.Max)} plates");
            if (State.RestaurantNights.Count == 0)
            {
                var intro = Mira("This is me on the radio! When the restaurant phones while we sail, I'll ask you here. Tonight is easy: our first guests.");
                intro.Options.Add(Opt("Let's do it", null, "Then let's catch them something good!"));
                radioQueue.Add(intro);
                return;
            }
            radioQueue.Add(Booking(r));
            var extra = new List<Func<RadioCall>> { () => HotelContract(r), () => LotteDeal(r) };
            if (Kitchen.Active.Any(i => i.Id == ItemId.Stove)) extra.Add(() => BramRepair());
            foreach (var make in extra.OrderBy(_ => r.Next()).Take(2)) { var c = make(); if (c != null) radioQueue.Add(c); }
            var tip = MiraTip(); if (tip != null) radioQueue.Add(tip);
        }

        (Species species, float weight)[] RadioPool => Grounds.ForMap(ActiveSpot).SelectMany(g => g.Day).GroupBy(e => e.species).Select(g => (g.Key, g.Sum(e => e.weight))).OrderByDescending(p => p.Item2).ToArray();

        RadioCall Booking(System.Random r)
        {
            int seats = Kitchen.Active.Select(i => RestaurantData.Get(i.Id).Seats).DefaultIfEmpty(2).Max();
            var who = Bookers.Where(b => b.Size <= seats).OrderBy(_ => r.Next()).First();
            var pool = RadioPool.Take(3).ToArray(); var species = pool[r.Next(pool.Length)].species;
            string time = new[] { "19:30", "20:00", "20:30", "21:00" }[r.Next(4)], fish = FishName(species);
            int size = Mathf.Min(who.Size, seats), deposit = size * 10;
            bool Book() { if (dayForecast.Book(size, species) == 0) return false; Note($"{Cap(who.Short)} x{size}, {time}, {fish}"); return true; }
            var c = Call(who, $"{who.Name} would like a table for {size} at {time}. They'd love the {fish}.");
            c.Options.Add(Opt("Book them", () => Book(), $"Booked! {size} {fish} plates on the list."));
            c.Options.Add(Opt("Ask a deposit", then: () =>
            {
                float yes = Mathf.Clamp(.45f + restaurantPopularity * .04f, .45f, .85f), roll = (float)r.NextDouble();
                if (roll < yes && Book())
                {
                    State.Coins += deposit; audio?.Play(VoyageAudio.Cue.Coins, .5f);
                    var ok = Mira($"Good news! {Cap(who.Short)} paid a {deposit}-coin deposit. They're booked.", "excited"); ok.Options.Add(Opt("Brilliant")); return ok;
                }
                if (roll < yes + .25f && Book()) { var half = Mira($"{Cap(who.Short)} say a deposit's a bit much, but they're coming anyway. Booked."); half.Options.Add(Opt("Fair enough")); return half; }
                var lost = Mira($"Oh dear. {Cap(who.Short)} booked at the Anchor instead.", "worried"); lost.Options.Add(Opt("Their loss")); return lost;
            }, reply: "I'll ask them for a deposit. One moment..."));
            c.Options.Add(Opt("Not tonight", null, "I'll tell them we're full. Shame!"));
            return c;
        }

        RadioCall HotelContract(System.Random r)
        {
            if (State.Active.Count >= GameData.MaxActiveContracts) return null;
            var species = RadioPool[0].species; var def = GameData.Get(species);
            float kg = (def.MinKg + def.MaxKg) * .5f;
            int n = Mathf.Clamp(Mathf.RoundToInt(State.CoolerCapacity * .2f / Mathf.Max(.1f, kg)), 3, 10);
            int value = State.ValueOf(new CaughtFish { Species = species, Kg = kg, StowedAt = SimTime }, SimTime), reward = Round5(n * value * 1.6f);
            string fish = FishName(species);
            void Take(int pay) { if (State.TakeContract(new Contract { Species = species, Count = n, VoyagesLeft = 2, Reward = pay })) Note($"Hotel: {n} {fish} (+{pay})"); }
            var c = Call(Hotel, $"The Harbour Hotel needs {n} {fish} by tonight. {reward} coins when we dock, on top of the market price.", "excited");
            c.Options.Add(Opt("Deal", () => Take(reward), $"Deal! Keep {n} {fish} aside for Mrs Haverkamp."));
            c.Options.Add(Opt("Ask for more", then: () =>
            {
                int more = Round5(reward * 1.2f);
                if (r.NextDouble() < .5) { Take(more); var ok = Mira($"She went up to {more}! {n} {fish} for the hotel.", "excited"); ok.Options.Add(Opt("Nice")); return ok; }
                var no = Call(Hotel, $"Mrs Haverkamp says {reward} is fair. Take it or leave it.");
                no.Options.Add(Opt("Take it", () => Take(reward), "Done. The hotel's on the list."));
                no.Options.Add(Opt("Leave it", null, "Another time, then."));
                return no;
            }, reply: "I'll try her for more..."));
            c.Options.Add(Opt("Not today", null, "I'll tell her the hold's spoken for."));
            return c;
        }

        RadioCall LotteDeal(System.Random r)
        {
            int bonus = 2, cost = Round5(bonus * dayForecast.Guests.Count * .5f), cheap = Round5(cost * .7f);
            void Buy(int pay) { State.Coins -= pay; radioPriceBonus += bonus; Note($"Lemons and dill: plates +{bonus}"); }
            var c = Call(Lotte, $"Lotte has lemons and dill going cheap. Every fish plate +{bonus} coins tonight, for {cost} coins?");
            c.Options.Add(Opt($"Buy, {cost}", () => Buy(cost), "Lovely. The plates will smell wonderful.", () => State.Coins >= cost));
            c.Options.Add(Opt("Haggle", then: () =>
            {
                if (r.NextDouble() < .6 && State.Coins >= cheap) { Buy(cheap); var ok = Mira($"Lotte gave in: {cheap} coins. The lemons are ours!", "excited"); ok.Options.Add(Opt("Ha!")); return ok; }
                var no = Call(Lotte, $"Lotte won't budge. {cost} or nothing, she says.");
                no.Options.Add(Opt($"Buy, {cost}", () => Buy(cost), "Bought. Worth it.", () => State.Coins >= cost));
                no.Options.Add(Opt("Leave it", null, "Plain plates tonight, then."));
                return no;
            }, reply: "Let me talk to her..."));
            c.Options.Add(Opt("No thanks", null, "Plain plates it is."));
            return c;
        }

        RadioCall BramRepair()
        {
            const int cost = 35;
            var c = Call(Bram, $"Old Bram says our stove has been clicking. He can fix it before service for {cost} coins. Or do we risk it?", "worried");
            c.Options.Add(Opt($"Send Bram, {cost}", () => { State.Coins -= cost; radioRepairBooked = true; Note("Bram fixes the stove"); }, "Bram's on his way. Nothing breaks tonight.", () => State.Coins >= cost));
            c.Options.Add(Opt("Risk it", () => radioStoveRisk = true, "Fingers crossed, Captain.", null));
            return c;
        }

        // Mira's tips cost nothing: the assistant part of her job.
        RadioCall MiraTip()
        {
            int guests = dayForecast.Guests.Count, crew = PrepWorkers;
            var big = RadioPool.Select(p => GameData.Get(p.species)).OrderByDescending(d => d.MaxKg).First();
            int plates = dayForecast.DishRanges.Sum(k => k.Value.Max);
            string line = guests > (crew + 1) * 6
                ? $"{guests} guests and {crew} {Plural(crew, "crew")} tonight. It'll be busy! One more pair of hands next time makes nights like this easy."
                : big.MaxKg >= RestaurantTuning.PlatterMinKg
                ? $"{big.Name} out here can top {big.MaxKg:0} kg. One big one feeds a whole table, so keep an eye out."
                : $"Tonight's list is about {Mathf.CeilToInt(plates * RestaurantTuning.FilletKg)} kg of fish and the hold takes {State.CoolerCapacity:0}. Whatever else we catch, the market buys.";
            var c = Mira(line); c.Options.Add(Opt("Thanks, Mira", null, "Any time, Captain.")); return c;
        }

        // ---- leaving the ground: lock the list, start the prep on deck, the calls for the way home -----------------
        void RadioHeadHome()
        {
            if (RestaurantPhase != DayPhase.Out || dayForecast == null) return;
            radioQueue.Clear(); radioLater.Clear(); RadioOpen = null;
            dayForecast.Lock();
            RestaurantPhase = DayPhase.Home;
            SuggestPrep(Cooler); prepDone = 0; prepWork = PrepSeconds(); radioWait = 1.6f;
            var margin = Mira("We're heading home and the crew are on the knives. How much extra shall we prep for tonight?");
            void Set(int m) { RestaurantPrep.Margin = m; SuggestPrep(Cooler); prepWork = PrepSeconds(); }
            margin.Options.Add(Opt("Tight", () => Set(0), "Tight it is. Less for the cats."));
            margin.Options.Add(Opt("+10%", () => Set(1), "Ten percent. Nice and safe."));
            margin.Options.Add(Opt("+20%", () => Set(2), "Plenty for walk-ins!"));
            radioQueue.Add(margin);
            var spare = dayPrep?.Market.GroupBy(m => m.Species).OrderByDescending(g => g.Sum(m => m.Kg)).FirstOrDefault();
            if (spare != null)
            {
                string fish = FishName(spare.Key); int n = spare.Count();
                var deal = Call(Henrik, $"Henrik the fishmonger will take our spare {fish} at +30% if I promise them to him now. {n} {Plural(n, "fish")}.", "excited");
                deal.Options.Add(Opt("Promise him", () => { radioMarketSpecies = spare.Key; Note($"Henrik: spare {fish} +30%"); }, "Promised! Henrik's waiting at the quay."));
                deal.Options.Add(Opt("Keep them free", null, "Fine. They might go in the soup."));
                radioQueue.Add(deal);
            }
        }

        float PrepSeconds()
        {
            if (dayPrep == null) return 0;
            return dayPrep.Stock.Sum(s => s.Count * (s.Form switch { PreparedForm.Fillet => 3.5f, PreparedForm.Whole => 2.5f, PreparedForm.Stock => .8f, PreparedForm.Platter => 8f, _ => 3f }));
        }

        // Fish promised on a contract skip the prep: they go to the buyer with the market sale.
        List<CaughtFish> ContractFish(IEnumerable<CaughtFish> fish)
        {
            var need = State.Active.GroupBy(c => c.Species).ToDictionary(g => g.Key, g => g.Sum(c => Mathf.Max(0, c.Count - c.Delivered)));
            var held = new List<CaughtFish>();
            foreach (var f in fish) if (need.TryGetValue(f.Species, out int n) && n > 0) { held.Add(f); need[f.Species] = n - 1; }
            return held;
        }

        // ---- per tick while sailing -------------------------------------------------------------------------------
        void TickRadio(float dt)
        {
            if (!RadioDay) return;
            for (int i = radioLater.Count - 1; i >= 0; i--)
                if (SimTime >= radioLater[i].at) { var c = radioLater[i].call(); radioLater.RemoveAt(i); if (c != null) radioQueue.Insert(0, c); }
            if (RadioOpen == null)
            {
                radioWait -= dt;
                if (radioWait <= 0 && radioQueue.Count > 0) { RadioOpen = radioQueue[0]; radioQueue.RemoveAt(0); radioOpenedAt = SimTime; audio?.Play(VoyageAudio.Cue.Bell, .45f); }
            }
            else if ((AutoPlay || RadioAuto) && SimTime - radioOpenedAt > .6f) AnswerRadio(0);
            if (PrepHolds) prepDone = Mathf.Min(prepWork, prepDone + dt * PrepWorkers * (TripFast ? 3f : 1f));
        }

        public bool AnswerRadio(int index)
        {
            var call = RadioOpen; if (call == null || index < 0 || index >= call.Options.Count || !call.Options[index].Enabled) return false;
            var o = call.Options[index]; RadioOpen = null;
            o.Apply?.Invoke();
            if (o.Reply != null) RadioSay(o.Reply, call.Mood);
            if (o.Then != null) radioLater.Add((SimTime + 2.6f, o.Then));
            radioWait = 1.8f; audio?.Play(VoyageAudio.Cue.Select, .4f);
            return true;
        }

        // The captain lends a knife: each tap guts a fish's worth of work.
        void PrepHelp() { if (!PrepHolds) return; prepDone = Mathf.Min(prepWork, prepDone + 1.2f); prepPop = SimTime; audio?.Play(VoyageAudio.Cue.Gut, .35f); }

        // ---- the night reads the answers ---------------------------------------------------------------------------
        void RadioNight(RestaurantSim sim)
        {
            sim.PriceBonus = radioPriceBonus;
            if (radioRepairBooked) sim.Breakdowns = false;
            radioStoveAt = radioStoveRisk && new System.Random(State.Voyage).NextDouble() < .65 ? 150f : -1; // about 19:15
            radioQueue.Clear(); radioLater.Clear(); RadioOpen = null; radioReply = null;
        }
        void RadioNightTick()
        {
            if (radioStoveAt < 0 || night == null || night.Seconds < radioStoveAt) return;
            radioStoveAt = -1; var stove = Kitchen.Active.FirstOrDefault(i => i.Id == ItemId.Stove); if (stove != null) night.Break(stove.Uid);
        }
        void RadioMarketBonus()
        {
            if (radioMarketSpecies == null) return;
            foreach (var f in State.UnsoldCatch) if (f.Species == radioMarketSpecies) f.ValueBonus += .3f;
            radioMarketSpecies = null;
        }

        // ---- drawing: the notebook (pinned ticket), the call card and Mira's reply -------------------------------
        void InterfaceRadio()
        {
            if (!RadioDay) return;
            bool home = RestaurantPhase == DayPhase.Home;
            float nw = compactInterface ? 168 : 228, nh = nw * 672f / 495f;
            var note = new Rect(iw - Edge - nw, Edge + (compactInterface ? 56 : 80), nw, nh); Block(note);
            coastalUi.Icon("radio/note", note, "rx-ticket");
            coastalUi.Text("radio/note/title", new Rect(note.x + nw * .14f, note.y + nh * .07f, nw * .72f, nh * .16f), home ? "Prep for tonight" : "Tonight", Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleCenter);
            float row = compactInterface ? 20 : 26, y = note.y + nh * .32f, x = note.x + nw * .13f, w = nw * .74f;
            if (!home)
            {
                int max = Mathf.FloorToInt(nh * .58f / row), from = Mathf.Max(0, radioNotes.Count - max);
                for (int i = from; i < radioNotes.Count; i++, y += row)
                {
                    var (text, at) = radioNotes[i];
                    int shown = Mathf.Clamp(Mathf.FloorToInt((SimTime - at) * 45f), 0, text.Length); // Mira's pen writes it in
                    coastalUi.Text($"radio/note/{i - from}", new Rect(x, y, w, row), text.Substring(0, shown), Skin.Type.Caption, Skin.Ink);
                }
            }
            else if (RestaurantPrep.Rows.Count > 0)
            {
                foreach (var (r, i) in RestaurantPrep.Rows.Select((r, i) => (r, i)).Take(4))
                {
                    int done = Mathf.FloorToInt(r.Portions * PrepU);
                    coastalUi.Text($"radio/prep/{i}", new Rect(x, y, w, row), $"{r.Name}  {done}/{r.Portions}", Skin.Type.Caption, Skin.Ink);
                    coastalUi.ProgressBar($"radio/prep/{i}/bar", new Rect(x, y + row - 5, w, 6), (float)done / Mathf.Max(1, r.Portions), Skin.Bar.Teal);
                    y += row + 8;
                }
                coastalUi.Text("radio/prep/crew", new Rect(x, note.yMax - nh * .14f, w, row), PrepHolds ? $"{PrepWorkers} {Plural(PrepWorkers, "crew")} on the knives" : "All prepped!", Skin.Type.Caption, Skin.Teal);
                if (PrepHolds)
                {
                    var help = new Rect(note.x, note.yMax + 8, nw, compactInterface ? 40 : 48);
                    coastalUi.Primary("radio/prep/help", help, "Lend a knife", PrepHelp, "v2-icon-fish"); Block(help);
                    float pop = SimTime - prepPop; if (pop < .25f) coastalUi.Pose("radio/prep/help", 0, 1 + .08f * Ease.Pulse(pop / .25f));
                }
            }

            float area = iw - nw - Edge * 3, W = Mathf.Min(compactInterface ? 560 : 640, area), H = compactInterface ? 156 : 176, cx = Edge + (area - W) / 2;
            var call = RadioOpen;
            if (call != null)
            {
                float t = SimTime - radioOpenedAt, slide = 1 - Ease.OutBack(t / .4f);
                var card = new Rect(cx, ih - Edge - H + slide * (H + Edge + 30), W, H); Block(card);
                var slab = coastalUi.Slab("radio/card", card, null, true);
                float ph = H - 16, pw = ph * 114f / 153f, tx = pw + 22, tw = W - tx - 14;
                coastalUi.Icon("radio/card/mira", new Rect(10, 8, pw, ph), MiraFace(call.Mood), slab, null, "rx-coach-mira");
                coastalUi.Icon("radio/card/radio", new Rect(pw - 18, 2, 34, 34), "v2-icon-radio", slab, null, "v2-icon-bell");
                if (t < 1.4f) coastalUi.Pose("radio/card/radio", Mathf.Sin(t * 38f) * 16f * (1 - t / 1.4f));
                bool caller = call.Face != null;
                if (caller) coastalUi.Icon("radio/card/face", new Rect(tx, 8, 30, 30), call.Face, slab);
                coastalUi.Text("radio/card/who", new Rect(caller ? tx + 36 : tx, 8, tw - 36, 30), call.Caller ?? "Mira", Skin.Type.Small, Skin.Teal, TextAnchor.MiddleLeft, slab);
                float bh = compactInterface ? 38 : 46;
                coastalUi.Text("radio/card/line", new Rect(tx, 40, tw, H - 40 - bh - 16), call.Line, compactInterface ? Skin.Type.Small : Skin.Type.Body, Skin.Ink, TextAnchor.UpperLeft, slab);
                int n = call.Options.Count; float bw = (tw - (n - 1) * 8) / n;
                for (int i = 0; i < n; i++)
                {
                    int k = i; var o = call.Options[i]; var b = new Rect(tx + i * (bw + 8), H - bh - 10, bw, bh);
                    if (i == 0) coastalUi.Primary($"radio/card/o{i}", b, o.Label, () => AnswerRadio(k), null, o.Enabled, slab);
                    else coastalUi.Secondary($"radio/card/o{i}", b, o.Label, () => AnswerRadio(k), null, o.Enabled, slab);
                }
            }
            else if (radioReply != null && SimTime < radioReplyUntil)
            {
                float t = SimTime - (radioReplyUntil - 3.4f), rh = compactInterface ? 56 : 64;
                var strip = new Rect(cx + W * .08f, ih - Edge - rh, W * .84f, rh);
                var slab = coastalUi.Slab("radio/reply", strip, null, false);
                coastalUi.Pose("radio/reply", 0, .9f + .1f * Ease.OutBack(t / .3f));
                float s = rh - 10;
                coastalUi.Icon("radio/reply/mira", new Rect(8, 5, s * 114f / 153f, s), MiraFace(radioReplyMood), slab, null, "rx-coach-mira");
                coastalUi.Text("radio/reply/t", new Rect(s * .8f + 18, 4, strip.width - s * .8f - 28, rh - 8), radioReply, Skin.Type.Small, Skin.Ink, TextAnchor.MiddleLeft, slab);
            }
            else if (RadioHolds && CurrentMode == Mode.SailingOut && TravelProgress > .98f)
                coastalUi.Toast("radio/wait", "Mira's on the radio. Anchoring once the call's done.", "v2-icon-radio", Edge, HudGapLeft, HudGapRight);
        }
        static string MiraFace(string mood) => HasUi($"rx-mira-{mood}-call") ? $"rx-mira-{mood}-call" : "rx-mira-happy-call";
    }
}
