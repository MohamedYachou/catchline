using System;

namespace Catchline.Game
{
    // Pure card maths from docs/CARDS-AND-SPEEDS.md sections 1-3. No scene or Unity dependencies.
    public static class CardProgression
    {
        public const int MaxLevel = 30;

        // Cumulative kg to reach each level (index = level - 1), copied verbatim from section 2.2.
        // The doc's formula round(40 * (L-1)^1.5) gives 4128 (L23) and 5926 (L29); the printed table says
        // 4127 and 5927. The printed table is the source of truth here; XpFormula keeps the raw formula.
        static readonly int[] XpTable =
        {
            0, 40, 113, 208, 320, 447, 588, 741, 905, 1080,
            1265, 1459, 1663, 1875, 2095, 2324, 2560, 2804, 3055, 3313,
            3578, 3849, 4127, 4412, 4703, 5000, 5303, 5612, 5927, 6247,
        };

        // Wage inputs (section 2.3), indexed by tier 1..5.
        static readonly int[] TierBase = { 0, 8, 15, 30, 60, 120 };
        static readonly float[] RarityWage = { 1.0f, 1.6f, 2.5f };

        public static int ClampLevel(int level) => level < 1 ? 1 : level > MaxLevel ? MaxLevel : level;

        // Cumulative kg needed to reach `level`.
        public static int XpForLevel(int level) => XpTable[ClampLevel(level) - 1];

        // The raw formula from the spec, kept for reference and cross-checking.
        public static int XpFormula(int level)
        {
            int l = ClampLevel(level);
            return (int)Math.Round(40.0 * Math.Pow(l - 1, 1.5), MidpointRounding.AwayFromZero);
        }

        public static int LevelForXp(float xp)
        {
            int level = 1;
            for (int l = 2; l <= MaxLevel; l++)
            {
                if (xp >= XpTable[l - 1]) level = l;
                else break;
            }
            return level;
        }

        // 1 + 0.015 * (level - 1)
        public static float LevelMult(int level) => 1f + 0.015f * (ClampLevel(level) - 1);

        // Wage per voyage: tierBase[T] * rarityMult * (1 + 0.01 * (level - 1)), rounded to whole coins.
        public static int Wage(int tier, CardRarity rarity, int level)
        {
            int t = tier < 1 ? 1 : tier > 5 ? 5 : tier;
            double w = TierBase[t] * (double)RarityWage[(int)rarity] * (1.0 + 0.01 * (ClampLevel(level) - 1));
            return (int)Math.Round(w, MidpointRounding.AwayFromZero);
        }

        // Role wildcards needed to move from `rarity` to the next one; 0 when already Gold.
        public static int UpgradeWildcards(CardRarity rarity) => rarity == CardRarity.Blue ? 10 : rarity == CardRarity.Purple ? 25 : 0;

        // Coins to move from `rarity` to the next one for a card unlocked at `tier`; 0 when already Gold.
        public static int UpgradeCoins(CardRarity rarity, int tier)
        {
            int t = tier < 1 ? 1 : tier > 5 ? 5 : tier;
            return rarity == CardRarity.Blue ? 300 * t : rarity == CardRarity.Purple ? 1000 * t : 0;
        }

        public static bool CanUpgrade(CardRarity rarity) => rarity != CardRarity.Gold;

        // Non-speciality skill by rarity: 50 / 65 / 80.
        public static int OffSkill(CardRarity rarity) => rarity == CardRarity.Blue ? 50 : rarity == CardRarity.Purple ? 65 : 80;

        // Fisher strike chance: 80 / 85 / 90% by rarity, +0.25 percentage points per level above 1, cap 97%.
        public static float StrikeChance(CardRarity rarity, int level)
        {
            float baseChance = rarity == CardRarity.Blue ? 0.80f : rarity == CardRarity.Purple ? 0.85f : 0.90f;
            float c = baseChance + 0.0025f * (ClampLevel(level) - 1);
            return c > 0.97f ? 0.97f : c;
        }

        // Skill (0..100) for `job` (a Speciality value naming the work family) per the section 3 matrix.
        // 0 means the role cannot do that job.
        public static int Skill(CardRole role, Speciality speciality, CardRarity rarity, Speciality job)
        {
            switch (role)
            {
                case CardRole.Fisher:
                    if (!IsGear(job)) return 0;
                    return job == speciality ? 100 : OffSkill(rarity);
                case CardRole.Deckhand:
                    if (!IsDeckWork(job)) return 0;
                    return job == speciality ? 100 : OffSkill(rarity);
                case CardRole.Navigator:
                    return job == Speciality.Navigation ? 100 : 0;
                case CardRole.Engineer:
                    if (job == Speciality.Power) return 100;
                    return job == Speciality.Haul ? 50 : 0;
                default:
                    return 0;
            }
        }

        public static int Skill(CardDef def, CardRarity rarity, Speciality job) => Skill(def.Role, def.Speciality, rarity, job);

        // The captain: skill 100 at every deck job, level 1 forever, no wage.
        public static int CaptainSkill(Speciality job) => IsGear(job) || IsDeckWork(job) ? 100 : 0;

        // Section 1: duration = base / (skill/100) / levelMult. Infinity when the person cannot do the job.
        public static float Duration(float baseSeconds, int skill, int level)
        {
            if (skill <= 0) return float.PositiveInfinity;
            return baseSeconds / (skill / 100f) / LevelMult(level);
        }

        // Section 1: walk = 2.2 m/s * (haulSkill/100) * levelMult.
        public static float WalkSpeed(int haulSkill, int level) => 2.2f * (haulSkill / 100f) * LevelMult(level);

        static bool IsGear(Speciality s) => s == Speciality.Rods || s == Speciality.Nets || s == Speciality.CagesLines || s == Speciality.Jigs;
        static bool IsDeckWork(Speciality s) => s == Speciality.Haul || s == Speciality.Sort || s == Speciality.Table;
    }
}
