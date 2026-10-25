using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEngine;
using UnityEditor.SceneManagement;

namespace Catchline.EditorTools
{
    public static class CrewCardsAbilityChecks
    {
        static int assertions;
        static void Check(bool ok, string message)
        { assertions++; if (!ok) throw new Exception("Crew abilities: " + message); }
        static bool Near(float a, float b) => Mathf.Abs(a - b) < .0001f;
        static GameState State(params string[] ids)
        {
            var s = new GameState(42) { Hull = 5, Chum = 20 };
            s.Roster.Clear(); s.Deployment.Clear();
            foreach (string id in ids) { s.Roster.Add(new CardState(id) { Rarity = CardRarity.Mythic }); s.Deployment.Add(id); }
            return s;
        }
        static CaughtFish Fish(Species species = Species.Cod, float kg = 5) => new() { Species = species, Kg = kg };
        sealed class Actor : IDeckActor
        {
            public Vector2Int Tile { get; set; }
            Action next;
            public int Acts;
            public float Seconds;
            public bool WalkTo(Vector2Int tile, Action arrive, Action cancel) { next = () => { Tile = tile; arrive(); }; return true; }
            public void Act(string label, float seconds, Action done, Action cancel) { Seconds = seconds; Acts++; next = done; }
            public void Stop() { next = null; }
            public void Step() { var action = next; next = null; action?.Invoke(); }
        }
        public static void Run()
        {
            assertions = 0;
            M2DataChecks.Run();
            MiraAndTools(); Rods(); Nets(); Deck(); RouteAndBatch(); ProductsAndIce(); NightAndTravel(); Sources(); LiveNetHooks();
            var args = Environment.GetCommandLineArgs(); int index = Array.IndexOf(args, "-snapshotPath");
            string path = index >= 0 ? Path.ChangeExtension(args[index + 1], ".json") : Path.Combine(Application.temporaryCachePath, "crew-abilities.json");
            File.WriteAllText(path, "{\"suite\":\"crew-abilities\",\"assertions\":" + assertions + ",\"passed\":true}");
            Debug.Log("[Catchline] CREW CARDS ABILITY CHECKS PASSED: " + assertions);
            Debug.Log("[Catchline] Snapshot written to " + path);
        }
        public static void Regression()
        {
            Run();
            M2Checks.Run();
            Debug.Log(BiteModelChecks.Run());
            Debug.Log(CageModelChecks.Run());
            Debug.Log("[Catchline] CREW ABILITY INTEGRATION REGRESSION PASSED");
        }
        static void MiraAndTools()
        {
            var s = State("mira", "noor"); var e = new CrewAbilityEngine(s);
            Check(Near(e.TeamWork, 1.08f) && Near(e.Thinning, .85f), "Mira trait and chart reader");
            e.Tick(119, false); Check(Near(e.BiteDuration(null, false), 1), "shoal call not early");
            e.Tick(1, false); Check(Near(e.BiteDuration(null, false), .7f) && Near(e.BiteDuration(null, true), .7f), "shoal call rods and lines");
            e.Tick(20, false); Check(Near(e.BiteDuration(null, false), 1), "shoal call expires");
            e.Tick(100, false); Check(e.DoubleWeight, "mate eye starts at 240");
            e.Tick(30, false); Check(!e.DoubleWeight, "mate eye expires");
            var report = e.Query("mira"); Check(report.Count == 4 && report.Single(a => a.AbilityId == "mira.mythic").LastFired == 240, "query exposes last fire without advancing clock");
            s.Deployment.Remove("mira"); Check(Near(e.TeamWork, 1) && Near(e.Thinning, 1), "undeployed perks gated");
            var card = CardRoster.Find(s.Roster, "noor"); card.Rarity = CardRarity.White;
            Check(Near(e.Work("noor", "Sorting"), 1), "White passive locked");
            card.Rarity = CardRarity.Mythic;
            for (int i = 0; i < 3; i++) { var t = s.AddTool(ToolKind.Gloves, CardRarity.Mythic); Check(s.EquipTool("noor", i, t.Uid), "equip gloves"); }
            Check(Near(e.Tool("noor", ToolKind.Gloves), .5f) && Near(e.Work("noor", "Sorting"), 1.65f), "tools capped, quick sort once");
        }
        static void Rods()
        {
            var s = State("dirk", "tess"); var e = new CrewAbilityEngine(s);
            Check(Near(e.Strike("dirk"), 1.15f) && Near(e.Strike(null), 1), "steady strike owner only");
            Check(Near(e.Reel("tess"), 1.15f) && Near(e.Reel("dirk"), 1), "quick reel owner only");
            e.RodLanded("dirk", Species.Cod);
            Check(Near(e.BiteDuration("tess", false), .8f) && Near(e.BiteDuration("dirk", false), 1) && Near(e.BiteDuration(null, true), 1), "Rod line excludes own rod and lines");
            e.RodLanded("dirk", Species.Cod); Check(e.TrophyNext("dirk"), "third successful landing trophy prepared");
            e.RodLanded("dirk", Species.Cod); Check(!e.TrophyNext("dirk"), "trophy counter commits once");
            e.Tick(15, false); Check(Near(e.BiteDuration(null, false), 1), "Rod line expires");
            int doubles = 0; for (int i = 0; i < 500; i++) if (e.RodLanded("tess", Species.Herring) == 2) doubles++;
            Check(doubles > 60 && doubles < 140, "Feathers deterministic broad probability bound");
            e.Tick(105, false); Check(e.Armed("tess", 2), "Tess timer armed");
            Check(e.RodLanded("tess", Species.Cod) == 1 && e.Armed("tess", 2), "nonshoal retains token");
            Check(e.RodLanded("tess", Species.Whiting) == 3 && !e.Armed("tess", 2), "Mythic replaces Purple extra");
        }
        static void Nets()
        {
            var e = new CrewAbilityEngine(State("kofi", "rosa"));
            Check(Near(e.Work("kofi", "Setting net"), 1.15f) && Near(e.Work("rosa", "Hauling net"), 1.15f), "net passive rates");
            e.NetHauled("kofi", "rosa", .81f, 1);
            Check(Near(e.NextSoak(0), 1) && Near(e.NextSoak(1), .75f) && Near(e.NextSoak(1), 1), "setter credit and rig specific one-shot soak");
            for (int i = 0; i < 3; i++) e.NetHauled(null, "kofi", .1f, 0);
            Check(e.InstantNetSet("kofi"), "third Kofi haul instant reset");
            e.NetHauled(null, "kofi", .1f, 1);
            Check(e.InstantNetSet("kofi") && e.Query("kofi").Single(a => a.AbilityId == "kofi.mythic").Active, "queued reset survives another haul and query reports it");
            e.NetSet("kofi"); Check(!e.InstantNetSet("kofi"), "reset consumes only on successful set");
            e.Tick(180, false); Check(e.Consume("rosa", 1) && !e.Consume("rosa", 1), "Rosa fuller batch single charge");
        }
        static void RouteAndBatch()
        {
            var deck = DeckGraph.Load(GameData.Hulls[2]); var sched = new DeckScheduler(deck);
            var actor = new Actor { Tile = deck.Access(deck.Hold) };
            var ana = new Worker { Card = new CardState("ana") { Rarity = CardRarity.Mythic }, Actor = actor, Role = CrewRole.Deckhand, HandCount = 3, Primary = Duty.Table, Secondary = Duty.Table };
            sched.Workers.Add(ana);
            var sources = deck.Stations.Where(s => s.IsGear && s.Out != null).Select(s => s.Out).Distinct().Take(2).ToArray();
            Check(sources.Length == 2, "route fixture has separate sources");
            foreach (var source in sources) for (int i = 0; i < 3; i++) sched.Land(source.Owner, Fish(Species.Herring, .5f));
            int deliveries = 0; bool ready = true;
            sched.SweepReady = _ => ready; sched.OnSweepDelivered = _ => { deliveries++; ready = false; };
            sched.Tick(); Check(ana.Current?.Kind == JobKind.Haul && ana.Current.Fish.Count <= 3 && sched.OnDeck == 6, "sweep overrides duties with real bounded carry job");
            sched.Cancel(ana.Current); Check(deliveries == 0 && sched.Balanced && sources.Sum(s => s.UnclaimedCount) == 6, "cancelled sweep spends no charge and releases all fish");
            for (int i = 0; i < 30; i++) { sched.Tick(); actor.Step(); }
            Check(deliveries == 1 && sources.Sum(s => s.Count) == 0 && deck.OfKind(StationKind.SortTable).Sum(s => s.In.Count) == 6 && sched.Balanced, "sweep visits both sources, routes snapshot and spends once");

            deck = DeckGraph.Load(GameData.Hulls[3]); sched = new DeckScheduler(deck);
            var table = deck.OfKind(StationKind.ProcessTable).First();
            actor = new Actor { Tile = deck.Access(table) };
            var mats = new Worker { Card = new CardState("mats") { Rarity = CardRarity.Mythic }, Actor = actor, Role = CrewRole.Deckhand, Primary = Duty.Table, Secondary = Duty.Table };
            sched.Workers.Add(mats);
            for (int i = 0; i < 2; i++) { table.In.Put(Fish(), false); sched.Landed++; }
            int batches = 0; sched.ProductBatch = _ => 2; sched.OnProductDone = _ => batches++;
            sched.Tick(); Check(mats.Current?.Fish.Count == 2 && table.Out.Free <= 6, "double product claims two real inputs and output capacity");
            sched.Cancel(mats.Current);
            Check(batches == 0 && table.In.UnclaimedCount == 2 && table.Out.Count == 0 && sched.Balanced, "cancelled product has no outputs or offcuts");
            sched.Tick(); actor.Step();
            Check(batches == 1 && table.In.Count == 0 && table.Out.Count == 2 && sched.Balanced, "double product commits atomically once");

            var bonus = new DeliverySortBonus(); var sort = deck.OfKind(StationKind.SortTable).First();
            var old = new Job { At = sort }; var next = new Job { At = sort };
            Check(Near(bonus.Begin(old), 1), "no delivery bonus initially");
            bonus.Offer(sort); bonus.Complete(old);
            Check(Near(bonus.Begin(next), 1.2f), "delivery during running sort survives completion");
            bonus.Cancel(next); Check(Near(bonus.Begin(next), 1.2f), "cancelled sort retains bonus");
            bonus.Offer(sort); bonus.Complete(next);
            var third = new Job { At = sort };
            Check(Near(bonus.Begin(third), 1.2f), "new delivery while boosted sort runs is next charge");
            bonus.Complete(third); Check(Near(bonus.Begin(new Job { At = sort }), 1), "completed boosted sort consumes only its charge");
        }
        static void Deck()
        {
            var deck = DeckGraph.Load(GameData.Hulls[2]); var sched = new DeckScheduler(deck);
            var actor = new Actor { Tile = deck.Access(deck.Hold) };
            var sam = new Worker { Name = "Sam", Card = new CardState("sam") { Rarity = CardRarity.Purple }, Role = CrewRole.Deckhand, Actor = actor, HandCount = 4 };
            sched.Workers.Add(sam);
            var source = deck.OfKind(StationKind.Net).First();
            for (int i = 0; i < 3; i++) sched.Land(source, Fish(Species.Cod, 4));
            sched.Tick(); Check(sam.Current?.Fish.Count == 2, "Sam carries two heavy fish");
            sched.Cancel(sam.Current); Check(sched.Balanced && sam.Hands.Count == 0 && source.Out.UnclaimedCount == 3, "cancel releases claims/reservations");
            sched.WholeLoad = (_, _) => true;
            sched.Tick(); Check(sam.Current?.Fish.Count == 3 && sam.Current.WholeLoad, "whole net load bypasses hand kg only");
            for (int i = 0; i < 8; i++) actor.Step(); Check(sched.Balanced, "whole load delivery identity balanced");
            var sort = deck.OfKind(StationKind.SortTable).First();
            sched.Workers.Clear(); var noor = new Worker { Card = new CardState("noor") { Rarity = CardRarity.Mythic }, Role = CrewRole.Deckhand, Actor = actor, Primary = Duty.Sort };
            sched.Workers.Add(noor); int sorted = 0; sched.OnSorted = (_, _) => sorted++;
            sched.BenchRate = _ => float.PositiveInfinity;
            sched.Tick(); for (int i = 0; i < 3; i++) actor.Step();
            Check(sorted == 1 && sched.Balanced, "instant sort commits normal routing without zero-duration deadlock");
            var e = new CrewAbilityEngine(State("noor", "tove", "ana", "sam"));
            e.Sorted("noor", Fish()); e.Sorted("noor", Fish()); Check(Near(e.SortRate("noor", Fish()), 1.3f), "Same again next sort armed");
            e.Sorted("noor", Fish(Species.Herring)); Check(Near(e.SortRate("noor", Fish()), 1), "Same again consumed at completion");
            var def = GameData.Get(Species.Cod); var fish = Fish(Species.Cod, def.MaxKg);
            for (int i = 0; i < 9; i++) e.Sorted("tove", Fish()); e.Sorted("tove", fish);
            Check(Near(fish.ValueBonus, 1.2f) && Near(e.SortRate("tove", Fish(Species.Crab, .5f)), 1.2f), "Tove grader times tenth sale and crab sort");
            Check(Near(e.Walk("ana"), 1.1f), "Ana walking");
            e.Tick(120, false); Check(e.Armed("ana", 2) && e.Armed("sam", 2), "Ana and Sam charges");
            e.SweepDelivered(); Check(!e.Armed("ana", 2), "Ana consumed on delivery");
            e.Tick(59, false); Check(!e.Armed("ana", 2), "Ana cooldown from delivery");
            e.Tick(1, false); Check(e.Armed("ana", 2), "Ana cooldown elapsed");
        }
        static void ProductsAndIce()
        {
            var s = State("mats", "ines", "pim"); var e = new CrewAbilityEngine(s);
            Check(Near(e.Work("mats", "Processing"), 1.1f), "quick knife");
            e.ProductDone("mats", 1); e.ProductDone("mats", 1);
            Check(s.Chum == 22 && e.ProductBatch("mats") == 2, "Offcuts and third batch");
            e.ProductDone("mats", 2); Check(s.Chum == 23 && e.ProductBatch("mats") == 1, "one chum per completed batch");
            e.HoldFill(.5f); Check(!e.IceActive, "half full strict edge");
            e.HoldFill(.51f); Check(e.IceActive, "crossing half freezes catch");
            e.Tick(180, false); Check(!e.IceActive, "Ice watch expires");
            Check(Near(e.FrozenSeconds(179), 1) && Near(e.FrozenSeconds(180), 0), "Ice watch integrates only active part at expiry");
            Check(Near(e.Work("pim", "Baiting deep line"), 1.25f) && Near(e.Work("pim", "Recovering buoy catch"), 1.25f), "Pim two live jobs");
            int saved = 0; for (int i = 0; i < 500; i++) if (e.SaveChum("pim")) saved++;
            Check(saved > 105 && saved < 200 && !e.SaveChum("mats"), "Pim saver gated and probability");
            e.Tick(120, false); Check(e.ExtraGearCatch("pim") == 1 && e.ExtraGearCatch("pim") == 0, "Pim next line or pot only once");
        }
        static void NightAndTravel()
        {
            var state = State("lise", "ines", "olaf"); var e = new CrewAbilityEngine(state);
            e.Tick(1, false); Check(Near(e.TeamWork, 1) && Near(e.BiteDuration("lise", false), 1), "night effects absent by day");
            e.Tick(179, true);
            Check(Near(e.TeamWork, 1.05f * 1.15f) && Near(e.BiteDuration("lise", false), .8f * .75f * .75f), "night own/team modifiers multiply");
            for (int i = 0; i < 3; i++) e.RodLanded("lise", Species.Cod);
            Check(e.PredatorNext("lise"), "fourth night predator");
            Check(Near(e.Fuel, .9f) && Near(e.Travel, 1.25f) && Near(e.Work(null, "Hauling net"), 1.25f), "Olaf fuel/travel/winch include captain");
            e.Tick(1, false); Check(Near(e.TeamWork, 1) && !e.PredatorNext("lise"), "night windows immediately gated");
            e.RodLanded("lise", Species.Cod); e.Tick(1, true);
            Check(e.PredatorNext("lise"), "day catch does not advance night-only counter");
            var winch = state.AddTool(ToolKind.WinchHandle, CardRarity.Mythic);
            Check(state.EquipTool("olaf", 0, winch.Uid) && Near(e.WinchRate(null), 1.17f * 1.25f), "engineer winch reaches captain pot pull");
            Check(Near(e.Work("lise", "Hauling net"), e.TeamWork * 1.17f * 1.25f), "engineer winch reaches fisher net work once");
            var oil = state.AddTool(ToolKind.OilCan, CardRarity.Mythic);
            Check(state.EquipTool(GameState.CaptainToolOwner, 0, oil.Uid) && Near(e.Fuel, .9f * .83f), "captain engineer tool affects global fuel");
            var plain = new CageModel(new System.Random(42)); var boosted = new CageModel(new System.Random(42));
            plain.Tap(); boosted.Tap(e.WinchRate(null));
            Check(boosted.Lift > plain.Lift && boosted.Phase == plain.Phase, "winch improves cage lift per input without speeding hazard clocks");
        }
        static void Sources()
        {
            var cycle = new DeepLineCycle(); Check(cycle.Deploy(BaitPermission.Chum), "paid line deploy");
            cycle.Tick(1, .5f); Check(cycle.Phase == DeepLinePhase.Soaking && Near(cycle.Remaining, 60), "dropping not bite-speeded");
            cycle.Tick(30, .5f); Check(cycle.Phase == DeepLinePhase.Raising && Near(cycle.Remaining, 2), "only line soak sped");
            Check(!cycle.Tick(1, .5f) && cycle.Tick(1, .5f), "raising unchanged");
            float sum = 0, heavier = 0;
            for (int i = 0; i < 200; i++)
            {
                var normal = new GameState(i) { Hull = 5 }; var boosted = new GameState(i) { Hull = 5 };
                var a = DeepLineRules.Roll(normal, 0, BaitPermission.Chum); var b = DeepLineRules.Roll(boosted, 0, BaitPermission.Chum, true);
                Check(a.species == b.species && b.kg >= a.kg && DeepLineRules.Options(boosted, 0, BaitPermission.Chum).Any(o => o.Species == b.species && b.kg >= o.Min && b.kg <= o.Max), "double draw keeps selected species/tier and improves legal weight");
                sum += a.kg; heavier += b.kg;
            }
            Check(heavier > sum * 1.01f, "double draw measurably improves matched source weights");
            var net = CatchExpectation.RollNet(5, 0, false, 30, new System.Random(42), heavier: true);
            Check(net.Sum(f => f.kg) <= 30.0001f && net.All(f => f.kg >= GameData.Get(f.species).MinKg && f.kg <= Mathf.Lerp(GameData.Get(f.species).MinKg, GameData.Get(f.species).MaxKg, .25f)), "double draw preserves net bait bounds and cap");
            var cage = new CageModel(new System.Random(42), true);
            Check(cage.Crabs.All(f => f.Kg >= GameData.Get(Species.Crab).MinKg && f.Kg <= GameData.Get(Species.Crab).MaxKg), "cage roll legal");
        }
        static void LiveNetHooks()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Crew abilities isolated hook checks").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build();
            try
            {
                g.State.Hull = 3; g.State.EnsureCards();
                foreach (var card in g.State.Roster) card.Rarity = CardRarity.Mythic;
                g.State.Deployment.Clear(); g.State.Deployment.AddRange(new[] { "mira", "noor", "rosa" });
                const System.Reflection.BindingFlags flags = System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic;
                object Call(string name, params object[] args) => typeof(VoyageGame).GetMethod(name, flags).Invoke(g, args);
                Call("RebuildBoat", false);
                typeof(VoyageGame).GetProperty("Abilities").SetValue(g, new CrewAbilityEngine(g.State));
                Call("SetupDeckGraph");
                var station = g.DeckGraph.OfKind(StationKind.Net).First();
                var rosa = new Person("Rosa", false, Vector3.zero) { Contract = new CrewMember { CardId = "rosa" } };
                for (int i = 0; i < 7; i++) Call("LandAbilityNet", station, Species.Cod, 4f, rosa, i);
                Check(g.Cooler.Count == 6 && g.Scheduler.Stowed == 6 && g.Scheduler.OnDeck == 1 && g.Scheduler.Balanced, "Rosa first six reach real hold, seventh remains on deck");
                Call("LandAbilityNet", station, Species.Cod, 4f, null, 0);
                var marked = station.Out.Fish.Last(); var sort = g.DeckGraph.OfKind(StationKind.SortTable).First();
                var job = new Job { At = sort, Kind = JobKind.Sort, Worker = new Worker { Card = CardRoster.Find(g.State.Roster, "noor") } };
                job.Fish.Add(marked);
                Check(float.IsPositiveInfinity(g.Scheduler.BenchRate(job)), "Noor net fish reaches zero-work hook");
                job.Worker = new Worker { Card = new CardState("sam") { Rarity = CardRarity.Mythic } };
                Check(!float.IsPositiveInfinity(g.Scheduler.BenchRate(job)), "another sorter cannot spend Noor instant ability");
                job.Worker = new Worker { Card = CardRoster.Find(g.State.Roster, "noor") };
                g.Scheduler.OnSorted(job, marked);
                Check(!float.IsPositiveInfinity(g.Scheduler.BenchRate(job)) && g.Abilities.Query("noor").Single(s => s.AbilityId == "noor.mythic").LastFired == 0, "instant-sort completion consumes marker and pulses read-only query");
                float free = g.State.CoolerCapacity - g.HoldKg;
                if (free > 0) g.Cooler.Add(Fish(Species.Cod, free));
                int held = g.Cooler.Count;
                Call("LandAbilityNet", station, Species.Cod, 4f, rosa, 0);
                Check(g.Cooler.Count == held && g.Scheduler.OnDeck == 3 && g.Scheduler.Balanced, "Rosa full hold falls back to normal deck without loss or overflow");
            }
            finally { UnityEngine.Object.DestroyImmediate(g.gameObject); }
        }
    }
}
