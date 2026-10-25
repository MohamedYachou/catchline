using System;
using System.Collections.Generic;
using System.Linq;

namespace Catchline.Game
{
    // Voyage-local rules. The simulation owns the clock and commits events only after successful work.
    // Nothing here reads saves, draws UI, mutates card progression, or advances on UI queries.
    public sealed class CrewAbilityEngine
    {
        public readonly struct Status
        {
            public readonly string CardId, AbilityId;
            public readonly bool Active;
            public readonly float LastFired, Until;
            public Status(string card, string ability, bool active, float last, float until)
            { CardId = card; AbilityId = ability; Active = active; LastFired = last; Until = until; }
        }
        sealed class CrewState
        {
            public int Landings, NightLandings, Sorts, Products, Hauls;
            public Species? PreviousSort;
            public bool SameAgain;
        }
        readonly GameState state;
        readonly Dictionary<string, CrewState> crew = new();
        readonly Dictionary<string, float> next = new(), until = new(), fired = new();
        readonly HashSet<string> armed = new();
        public float Time { get; private set; }
        public bool Night { get; private set; }
        public CrewAbilityEngine(GameState state) { this.state = state; }
        public CardState Card(string id) => id != null && state.Deployment.Contains(id) ? CardRoster.Find(state.Roster, id) : null;
        public bool Has(string id, int tier)
        {
            var c = Card(id);
            return c != null && CardProgression.HasAbility(c.Rarity, tier == 0 ? c.Def.Passive : tier == 1 ? c.Def.Auto : c.Def.Mythic);
        }
        CrewState For(string id)
        {
            if (!crew.TryGetValue(id, out var value)) crew[id] = value = new CrewState();
            return value;
        }
        static string Key(string id, int tier) => id + (tier == 0 ? ".passive" : tier == 1 ? ".auto" : ".mythic");
        void Fire(string key) { fired[key] = Time; }
        bool Window(string id, int tier) => Has(id, tier) && until.TryGetValue(Key(id, tier), out var end) && Time < end;
        public bool Armed(string id, int tier) => Has(id, tier) && armed.Contains(Key(id, tier));
        public bool Consume(string id, int tier)
        {
            if (!Has(id, tier) || !armed.Remove(Key(id, tier))) return false;
            Fire(Key(id, tier)); return true;
        }
        public void SweepDelivered()
        {
            if (Consume("ana", 2)) next[Key("ana", 2)] = Time + 60;
        }
        void Timer(string id, int tier, float period, float duration = 0, bool nightOnly = false)
        {
            if (!Has(id, tier)) return;
            string key = Key(id, tier);
            if (!next.TryGetValue(key, out float due)) next[key] = due = period;
            if (Time < due || nightOnly && !Night) return;
            next[key] = Time + period; // no backlog bursts, including after a night transition
            if (duration > 0) { until[key] = Time + duration; Fire(key); }
            else armed.Add(key); // one charge, never one charge per missed interval
        }
        public void Tick(float dt, bool night)
        {
            if (!(dt > 0) || float.IsInfinity(dt)) return;
            Time += dt; Night = night;
            Timer("mira", 1, 120, 20); Timer("mira", 2, 240, 30);
            Timer("tess", 2, 120); Timer("sam", 2, 120); Timer("rosa", 1, 180);
            Timer("ana", 2, 60); Timer("lise", 1, 120, 30, true);
            Timer("ines", 2, 180, 40, true); Timer("olaf", 1, 120, 30); Timer("pim", 2, 300);
        }
        public IReadOnlyList<Status> Query(string id)
        {
            var c = Card(id); if (c == null) return Array.Empty<Status>();
            var result = new List<Status>();
            foreach (var a in c.Def.Abilities)
            {
                if (!c.Has(a)) continue;
                bool timed = a == c.Def.Auto && (id == "mira" || id == "lise" || id == "ines" || id == "olaf")
                    || a == c.Def.Mythic && (id == "mira" || id == "ines");
                bool active = a == c.Def.Trait || a == c.Def.Passive || armed.Contains(a.Id)
                    || until.TryGetValue(a.Id, out var expiry) && Time < expiry;
                if (id == "kofi" && a == c.Def.Mythic) active = InstantNetSet(id);
                crew.TryGetValue(id, out var counters);
                if (id == "noor" && a == c.Def.Auto) active = counters?.SameAgain == true;
                if (id == "dirk" && a == c.Def.Mythic) active = ((counters?.Landings ?? 0) + 1) % 3 == 0;
                if (id == "lise" && a == c.Def.Mythic) active = Night && ((counters?.NightLandings ?? 0) + 1) % 4 == 0;
                if ((id == "ines" && (a == c.Def.Passive || a == c.Def.Mythic) || id == "lise") && !Night) active = false;
                // Conditional untimed abilities pulse at their commit; unlocked alone does not mean active.
                result.Add(new Status(id, a.Id, active, fired.TryGetValue(a.Id, out float last) ? last : -1,
                    timed && until.TryGetValue(a.Id, out float end) ? end : -1));
            }
            return result.AsReadOnly();
        }
        public float TeamWork => (Card("mira") != null ? Has("mira", 2) ? 1.08f : 1.05f : 1)
            * (Night && Has("ines", 0) ? 1.05f : 1) * (Night && Window("ines", 2) ? 1.15f : 1);
        public float Fuel => (Has("olaf", 0) ? .9f : 1) * (1 - TeamTool(ToolKind.OilCan));
        public float Travel => (Has("olaf", 2) ? 1.25f : 1) * (1 + TeamTool(ToolKind.Charts));
        public float Thinning => (Has("mira", 0) ? .85f : 1) * (1 - TeamTool(ToolKind.Compass));
        public float Tool(string id, params ToolKind[] kinds) => Math.Min(.5f, kinds.Sum(k => state.ToolBonus(id ?? GameState.CaptainToolOwner, k)));
        float TeamTool(ToolKind kind) => Math.Min(.5f, state.Deployment.Sum(id => state.ToolBonus(id, kind))
            + (ToolInfo.Class(kind) == CardRole.Engineer ? state.ToolBonus(GameState.CaptainToolOwner, kind) : 0));
        public float WinchRate(string id) => (1 + TeamTool(ToolKind.WinchHandle)) * (Window("olaf", 1) ? 1.25f : 1);
        public float BiteDuration(string id, bool line)
        {
            float factor = 1 / (1 + TeamTool(ToolKind.Binoculars) * .5f);
            if (Window("mira", 1)) factor *= .7f;
            if (Night && Window("lise", 1)) factor *= .75f;
            if (Night && Window("ines", 2)) factor *= .75f;
            if (Night && id == "lise" && Has(id, 0)) factor *= .8f;
            if (!line && id != "dirk" && Window("dirk", 1)) factor *= .8f;
            return Math.Max(.4f, factor);
        }
        public float Strike(string id) => (id == "dirk" && Has(id, 0) ? 1.15f : 1) * (1 + Tool(id, ToolKind.Rod));
        public float Reel(string id) => (id == "tess" && Has(id, 0) ? 1.15f : 1) * (1 + Tool(id, ToolKind.Rod, ToolKind.Reel));
        public float Walk(string id, bool carrying = false) => (id == "ana" && Has(id, 0) ? 1.1f : 1)
            * (1 + (carrying ? Tool(id, ToolKind.Boots, ToolKind.Gaff) : Tool(id, ToolKind.Boots)));
        public float Work(string id, string label)
        {
            float factor = id == null ? 1 : TeamWork;
            switch (label)
            {
                case "Sorting": case "Sorting fish":
                    factor *= 1 + Tool(id, ToolKind.Gloves);
                    if (id == "noor" && Has(id, 0)) factor *= 1.1f;
                    break;
                case "Processing": case "Making chum":
                    factor *= 1 + Tool(id, ToolKind.FilletKnife);
                    if (id == "mats" && Has(id, 0)) factor *= 1.1f;
                    break;
                case "Setting net":
                    factor *= 1 + Tool(id, ToolKind.NetNeedle);
                    if (id == "kofi" && Has(id, 0)) factor *= 1.15f;
                    break;
                case "Hauling net": case "Recovering buoy catch":
                    factor *= 1 + Math.Min(.5f, Tool(id, label == "Hauling net" ? ToolKind.NetNeedle : ToolKind.BaitKnife) + TeamTool(ToolKind.WinchHandle));
                    if (Window("olaf", 1)) factor *= 1.25f;
                    if (id == "rosa" && label == "Hauling net" && Has(id, 0)) factor *= 1.15f;
                    if (id == "pim" && label == "Recovering buoy catch" && Has(id, 0)) factor *= 1.25f;
                    break;
                case "Baiting deep line":
                    factor *= 1 + Tool(id, ToolKind.BaitKnife);
                    if (id == "pim" && Has(id, 0)) factor *= 1.25f;
                    break;
                case "Repairing": case "Engine work": factor *= 1 + Tool(id, ToolKind.Toolbelt); break;
            }
            return factor;
        }
        public float SortRate(string id, CaughtFish fish)
        {
            float rate = id == "noor" && Has(id, 1) && For(id).SameAgain ? 1.3f : 1;
            if (id == "tove" && Has(id, 0) && (fish.Species == Species.Crab || fish.Kg > 3)) rate *= 1.2f;
            return rate;
        }
        public void HandedOff() { if (Has("ana", 1)) Fire(Key("ana", 1)); }
        public void InstantSorted() { if (Has("noor", 2)) Fire(Key("noor", 2)); }
        public void Sorted(string id, CaughtFish fish)
        {
            if (id == null) return;
            var c = For(id); c.Sorts++;
            if (id == "noor" && Has(id, 1))
            {
                if (c.SameAgain) { c.SameAgain = false; Fire(Key(id, 1)); }
                else c.SameAgain = c.PreviousSort == fish.Species;
                c.PreviousSort = fish.Species;
            }
            if (id == "tove")
            {
                var def = GameData.Get(fish.Species);
                float value = 1 + fish.ValueBonus;
                if (Has(id, 1) && fish.Kg >= def.MinKg + .75f * (def.MaxKg - def.MinKg)) { value *= 1.1f; Fire(Key(id, 1)); }
                if (Has(id, 2) && c.Sorts % 10 == 0) { value *= 2; Fire(Key(id, 2)); }
                fish.ValueBonus = value - 1;
            }
        }
        public int ProductBatch(string id) => id == "mats" && Has(id, 2) && (For(id).Products + 1) % 3 == 0 ? 2 : 1;
        public void ProductDone(string id, int count)
        {
            if (id != "mats") return;
            For(id).Products++;
            if (Has(id, 1)) { state.Chum++; Fire(Key(id, 1)); }
            if (count > 1 && Has(id, 2)) Fire(Key(id, 2));
        }
        public bool SaveChum(string id) { bool saved = id == "pim" && Has(id, 1) && state.Rng.NextDouble() < .3; if (saved) Fire(Key(id, 1)); return saved; }
        public int ExtraGearCatch(string id) => id == "pim" && Consume(id, 2) ? 1 : 0;
        public bool IceActive => Window("ines", 1);
        public float FrozenSeconds(float start) => Has("ines", 1) && until.TryGetValue(Key("ines", 1), out float end)
            ? Math.Max(0, Math.Min(Time, end) - Math.Max(start, fired[Key("ines", 1)])) : 0;
        bool aboveHalf;
        public void HoldFill(float fill)
        {
            if (fill > .5f && !aboveHalf && Has("ines", 1)) { until[Key("ines", 1)] = Time + 180; Fire(Key("ines", 1)); }
            aboveHalf = fill > .5f;
        }
        public bool DoubleWeight => Window("mira", 2);
        public bool TrophyNext(string id) => id == "dirk" && Has(id, 2) && (For(id).Landings + 1) % 3 == 0;
        public bool PredatorNext(string id) => id == "lise" && Night && Has(id, 2) && (For(id).NightLandings + 1) % 4 == 0;
        public int RodLanded(string id, Species species)
        {
            if (id == null) return 1;
            var c = For(id); c.Landings++;
            if (Night) c.NightLandings++;
            if (id == "dirk")
            {
                if (Has(id, 1)) { until[Key(id, 1)] = Time + 15; Fire(Key(id, 1)); }
                if (Has(id, 2) && c.Landings % 3 == 0) Fire(Key(id, 2));
            }
            if (id == "lise" && Night && Has(id, 2) && c.NightLandings % 4 == 0) Fire(Key(id, 2));
            if (id != "tess" || !(species is Species.Herring or Species.Mackerel or Species.Whiting)) return 1;
            if (Consume(id, 2)) return 3;
            if (Has(id, 1) && state.Rng.NextDouble() < .2) { Fire(Key(id, 1)); return 2; }
            return 1;
        }
        public bool InstantNetSet(string id) => id == "kofi" && Has(id, 2) && armed.Contains("kofi.reset");
        public void NetSet(string id) { if (id == "kofi" && armed.Remove("kofi.reset")) Fire(Key(id, 2)); }
        public void NetHauled(string setter, string hauler, float fill, int rig)
        {
            if (setter == "kofi" && Has(setter, 1) && fill > .8f) { armed.Add("kofi.soak." + rig); Fire(Key(setter, 1)); }
            if (hauler == "kofi" && Has(hauler, 2) && ++For(hauler).Hauls % 3 == 0) armed.Add("kofi.reset");
        }
        public float NextSoak(int rig) => Has("kofi", 1) && armed.Remove("kofi.soak." + rig) ? .75f : 1;
    }
}
