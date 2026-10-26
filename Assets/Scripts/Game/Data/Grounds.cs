using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public enum RichnessBand { Rich, Thinning, Poor }

    // MASTER-PLAN M4 / MAP-PLAN 7.2. Three grounds per map (ids match each map's navigation.json), each with a day
    // pool and a night pool. Richness is stored per ground per species in one flat array (GameState.GroundRich),
    // indexed by Grounds.Slot. The old per-map tables are split across the grounds so no species is lost.
    public sealed class GroundDef
    {
        public string Id, Name, Kind;
        public (Species species, float weight)[] Day;
        (Species species, float weight)[] night;
        public (Species species, float weight)[] Night => night ??= Day.Select(e => (e.species, e.weight * Grounds.NightFactor(e.species))).ToArray();
        public (Species species, float weight)[] Pool(bool isNight) => isNight ? Night : Day;
    }

    // What the navigator tells the player about the ground they are on.
    public sealed class GroundReport
    {
        public string GroundId, GroundName;
        public readonly List<(Species species, float richness, RichnessBand band)> Species = new();
        public float Score;
        public RichnessBand Overall;
        public string BetterGroundId, BetterGroundName;
        public bool ShouldMove => BetterGroundId != null;
        public string Line;
    }

    public static class Grounds
    {
        public const float RodDrain = .02f, NetDrainPerKg = .004f, Floor = .3f, Start = 1f, RecoveryPerVoyage = .35f;
        public const float RichBand = .8f, PoorBand = .5f, MoveMargin = .3f;

        static GroundDef G(string id, string name, string kind, params (Species, float)[] day) => new GroundDef { Id = id, Name = name, Kind = kind, Day = day };

        // Indexed like GameData.Spots.
        static readonly GroundDef[][] ByMap =
        {
            new[] {
                G("quay-shallows", "Quay shallows", "shallows", (Species.Herring, 70f), (Species.Whiting, 25f), (Species.Mackerel, 8f)),
                G("channel", "Channel", "channel", (Species.Herring, 30f), (Species.Mackerel, 45f), (Species.Whiting, 8f)),
                G("mouth-flats", "Mouth flats", "flats", (Species.Mackerel, 60f), (Species.Herring, 20f), (Species.Whiting, 15f)) },
            new[] {
                G("kelp-shallows", "Kelp shallows", "shallows", (Species.Herring, 25f), (Species.Mackerel, 55f), (Species.Whiting, 20f), (Species.GoldenPuffer, 1.2f), (Species.Lionfish, .6f)),
                G("kelp-edge", "Kelp edge", "edge", (Species.Mackerel, 40f), (Species.Pollock, 30f), (Species.SeaBass, 15f), (Species.Whiting, 8f), (Species.Herring, 5f)),
                G("open", "Open", "open", (Species.Pollock, 30f), (Species.Mackerel, 15f), (Species.SeaBass, 12f), (Species.Barracuda, 8f), (Species.MahiMahi, 6f), (Species.FlyingFish, 2.4f)) },
            new[] {
                G("the-bar", "The bar", "bar", (Species.Plaice, 55f), (Species.RedMullet, 30f), (Species.Mackerel, 10f), (Species.GoldenPuffer, 1f), (Species.BlueSpottedStingray, 1f)),
                G("gully", "Gully", "gully", (Species.SeaBass, 30f), (Species.Plaice, 25f), (Species.Turbot, 14f), (Species.Monkfish, 7f), (Species.Lionfish, .9f), (Species.SpottedEagleRay, .7f)),
                G("open", "Open", "open", (Species.Mackerel, 25f), (Species.SeaBass, 15f), (Species.RedMullet, 15f), (Species.Turbot, 4f), (Species.FlyingFish, 1.2f), (Species.SpottedEagleRay, .6f)) },
            new[] {
                G("reef", "Reef", "reef", (Species.Pollock, 40f), (Species.SeaBass, 30f), (Species.RedMullet, 20f), (Species.Conger, 10f), (Species.SpottedEagleRay, .8f), (Species.ApexReefShark, .25f), (Species.GoldTipShark, .1f)),
                G("drop-off", "Drop-off", "drop-off", (Species.Conger, 30f), (Species.Pollock, 25f), (Species.SeaBass, 25f), (Species.GiantDevilManta, .16f), (Species.AtlanticSwordfish, .1f), (Species.ScallopedHammerhead, .08f), (Species.PelagicThresherShark, .08f)),
                G("open", "Open", "open", (Species.Mackerel, 25f), (Species.Pollock, 15f), (Species.Barracuda, 12f), (Species.MahiMahi, 8f), (Species.AtlanticSwordfish, .1f), (Species.PelagicThresherShark, .06f)) },
            new[] {
                G("drop-off", "Drop-off", "drop-off", (Species.Cod, 55f), (Species.Conger, 35f), (Species.Pollock, 20f), (Species.Turbot, 15f), (Species.Monkfish, 8f), (Species.SpottedEagleRay, .4f)),
                G("trench", "Trench", "trench", (Species.Cod, 35f), (Species.Conger, 25f), (Species.Monkfish, 5f), (Species.Turbot, 5f), (Species.ApexReefShark, .2f), (Species.GoldTipShark, .15f), (Species.AbyssalGreatWhite, .08f), (Species.AbyssalLeviathan, .03f), (Species.GiantSquid, .03f)),
                G("open", "Open", "open", (Species.Pollock, 30f), (Species.Cod, 15f), (Species.YellowfinTuna, 12f), (Species.OceanSunfish, .3f), (Species.AtlanticSwordfish, .2f), (Species.GiantDevilManta, .15f), (Species.ScallopedHammerhead, .1f), (Species.PelagicThresherShark, .1f)) },
            // Seal skerries (MAP6-SKERRIES-1). Appended last so saved richness slots of the first five maps keep their index.
            new[] {
                G("seal-rocks", "Seal rocks", "rocks", (Species.Crab, 45f), (Species.Conger, 35f), (Species.Pollock, 15f), (Species.SeaBass, 10f)),
                G("kelp-gully", "Kelp gully", "gully", (Species.Pollock, 45f), (Species.Cod, 35f), (Species.Conger, 10f), (Species.SeaBass, 8f)),
                G("outer-reef", "Outer reef", "reef", (Species.Monkfish, 30f), (Species.Cod, 35f), (Species.Pollock, 15f), (Species.Turbot, 4f), (Species.ApexReefShark, .2f)) },
            // Wreck bank (MAP7). Append to preserve all existing saved richness slots.
            new[] {
                G("the-wreck", "The wreck", "wreck", (Species.Conger, 40f), (Species.Cod, 30f), (Species.Pollock, 25f), (Species.Turbot, 2f)),
                G("herring-bank", "Herring bank", "bank", (Species.Herring, 50f), (Species.Mackerel, 30f), (Species.Whiting, 20f)),
                G("sand-edge", "Sand edge", "sand", (Species.Plaice, 50f), (Species.Turbot, 12f), (Species.Whiting, 25f), (Species.SpottedEagleRay, 1f)) },
            // Lighthouse rock (MAP8). Preserve all prior map richness slots.
            new[] {
                G("the-pinnacle", "The pinnacle", "pinnacle", (Species.Pollock, 40f), (Species.SeaBass, 30f), (Species.Conger, 20f), (Species.GoldTipShark, 1f)),
                G("tide-race", "Tide race", "race", (Species.Mackerel, 45f), (Species.SeaBass, 35f), (Species.YellowfinTuna, 3f)),
                G("deep-ledge", "Deep ledge", "ledge", (Species.Cod, 35f), (Species.Monkfish, 30f), (Species.Turbot, 10f), (Species.AtlanticSwordfish, 1f)) },
            // Whale shelf (MAP9): append without moving saved richness slots.
            new[] {
                G("herring-shoals", "Herring shoals", "shoals", (Species.Herring, 50f), (Species.Mackerel, 35f), (Species.Whiting, 12f), (Species.FlyingFish, 2f)),
                G("shelf-edge", "Shelf edge", "shelf", (Species.Cod, 30f), (Species.Pollock, 30f), (Species.Conger, 20f), (Species.Turbot, 10f), (Species.AbyssalGreatWhite, 1f)),
                G("whale-road", "Whale road", "whales", (Species.Mackerel, 35f), (Species.SeaBass, 25f), (Species.Pollock, 20f), (Species.SpottedEagleRay, 3f)) },
            // Seal cliffs (MAP10): append without moving saved richness slots.
            new[] {
                G("arch-pool", "Arch pool", "arch", (Species.Pollock, 40f), (Species.RedMullet, 30f), (Species.Conger, 15f), (Species.Crab, 2f)),
                G("seal-cove", "Seal cove", "cove", (Species.Mackerel, 40f), (Species.Herring, 30f), (Species.SeaBass, 20f), (Species.RedMullet, 3f)),
                G("stack-race", "Stack race", "stack", (Species.Cod, 35f), (Species.Pollock, 30f), (Species.Conger, 15f), (Species.Turbot, 1f)) },
            // Kelp forest (MAP11): append without moving prior saved richness slots.
            new[] {
                G("kelp-edge", "Kelp edge", "kelp", (Species.RedMullet, 40f), (Species.Pollock, 30f), (Species.SeaBass, 20f), (Species.Crab, 2f)),
                G("sand-clearing", "Sand clearing", "sand", (Species.Plaice, 40f), (Species.Whiting, 30f), (Species.RedMullet, 20f), (Species.Turbot, 3f)),
                G("post-line", "Post line", "posts", (Species.Mackerel, 45f), (Species.Herring, 30f), (Species.Conger, 15f), (Species.Turbot, 2f)) },
        };

        static readonly int[][] offsets;
        public static readonly int SlotCount;

        static Grounds()
        {
            offsets = new int[ByMap.Length][];
            int n = 0;
            for (int m = 0; m < ByMap.Length; m++)
            {
                offsets[m] = new int[ByMap[m].Length];
                for (int g = 0; g < ByMap[m].Length; g++) { offsets[m][g] = n; n += ByMap[m][g].Day.Length; }
            }
            SlotCount = n;
        }

        // Night: small shoaling fish thin out, heavy predators come up (scaled by the species heaviness).
        public static float NightFactor(Species s) => Mathf.Lerp(.6f, 1.5f, GameData.Get(s).Heaviness);

        public static GroundDef[] ForMap(int spot) => spot >= 0 && spot < ByMap.Length ? ByMap[spot] : Array.Empty<GroundDef>();
        public static int IndexOf(int spot, string groundId) => Array.FindIndex(ForMap(spot), g => g.Id == groundId);
        public static GroundDef Get(int spot, int ground) => ground >= 0 && ground < ForMap(spot).Length ? ByMap[spot][ground] : null;
        public static float[] NewRichness() { var a = new float[SlotCount]; for (int i = 0; i < a.Length; i++) a[i] = Start; return a; }

        // Flat index of a species' richness at a ground, or -1 when the ground does not hold it.
        public static int Slot(int spot, int ground, Species s)
        {
            var def = Get(spot, ground);
            if (def == null) return -1;
            int k = Array.FindIndex(def.Day, e => e.species == s);
            return k < 0 ? -1 : offsets[spot][ground] + k;
        }
        public static float Richness(float[] rich, int spot, int ground, Species s)
        {
            int slot = Slot(spot, ground, s);
            return slot < 0 || rich == null || slot >= rich.Length ? Start : rich[slot];
        }

        public static void Drain(float[] rich, int spot, int ground, Species s, float amount)
        {
            int slot = Slot(spot, ground, s);
            if (slot >= 0) rich[slot] = Mathf.Max(Floor, rich[slot] - amount);
        }
        public static void Recover(float[] rich)
        {
            for (int i = 0; i < rich.Length; i++) rich[i] = Mathf.Min(Start, rich[i] + RecoveryPerVoyage);
        }

        public static RichnessBand BandOf(float richness) => richness >= RichBand ? RichnessBand.Rich : richness < PoorBand ? RichnessBand.Poor : RichnessBand.Thinning;

        // Weighted mean richness of a ground's day pool over the species the player targets (all when null).
        public static float Score(float[] rich, int spot, int ground, Func<Species, bool> targeted = null)
        {
            var def = Get(spot, ground);
            if (def == null) return Start;
            float sum = 0, total = 0;
            foreach (var e in def.Day)
            {
                if (targeted != null && !targeted(e.species)) continue;
                sum += e.weight * Richness(rich, spot, ground, e.species); total += e.weight;
            }
            return total <= 0 ? Start : sum / total;
        }

        public static GroundReport Report(float[] rich, int spot, int ground, Func<Species, bool> targeted = null)
        {
            var def = Get(spot, ground);
            var report = new GroundReport { GroundId = def?.Id, GroundName = def?.Name };
            if (def == null) return report;
            foreach (var e in def.Day)
            {
                if (targeted != null && !targeted(e.species)) continue;
                float r = Richness(rich, spot, ground, e.species);
                report.Species.Add((e.species, r, BandOf(r)));
            }
            report.Score = Score(rich, spot, ground, targeted);
            report.Overall = BandOf(report.Score);
            float best = report.Score + MoveMargin - .0001f; int pick = -1;
            for (int g = 0; g < ForMap(spot).Length; g++)
            {
                if (g == ground) continue;
                float s = Score(rich, spot, g, targeted);
                if (s >= best) { best = s; pick = g; }
            }
            if (pick >= 0) { report.BetterGroundId = ByMap[spot][pick].Id; report.BetterGroundName = ByMap[spot][pick].Name; }
            // Name the heaviest-weighted species that is not rich.
            Species? worst = null; float worstWeight = -1; RichnessBand worstBand = RichnessBand.Rich;
            foreach (var s in report.Species)
            {
                if (s.band == RichnessBand.Rich) continue;
                float w = def.Day.First(d => d.species == s.species).weight;
                if (w > worstWeight) { worstWeight = w; worst = s.species; worstBand = s.band; }
            }
            report.Line = worst.HasValue
                ? $"{GameData.Get(worst.Value).Name} {(worstBand == RichnessBand.Poor ? "poor" : "thinning")} here." + (report.ShouldMove ? $" {report.BetterGroundName} is richer." : "")
                : "Rich water here.";
            return report;
        }

        // MASTER-PLAN M4: warning lead time for events = 8 s + 0.5 s per level.
        public static float EventWarningSeconds(int level) => 8f + .5f * Mathf.Max(0, level);

        // Visible cues, driven only by the richness bands (MAP-PLAN 7.2).
        public static int GullCount(float groundScore, int variant)
        {
            var band = BandOf(groundScore);
            int v = Mathf.Abs(variant);
            return band == RichnessBand.Rich ? 3 + v % 4 : band == RichnessBand.Thinning ? 1 + v % 2 : 0;
        }
        public static Color RingTint(float groundScore) => BandOf(groundScore) switch
        {
            RichnessBand.Rich => new Color(1f, .72f, .28f, .85f),
            RichnessBand.Thinning => new Color(.92f, .94f, .9f, .75f),
            _ => new Color(.52f, .56f, .58f, .7f),
        };
    }
}
