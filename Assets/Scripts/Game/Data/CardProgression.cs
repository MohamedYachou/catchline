using System;

namespace Catchline.Game
{
    // Pure card maths for crew cards v2 (docs/plans/CREW-CARDS-V2.md sections 1-4). No scene or Unity dependencies.
    public static class CardProgression
    {
        public const int MaxLevel = 30, MaxStars = 5, MaxToolSlots = 3;
        public const float ToolBonusCap = 0.5f;

        // Indexed by (int)CardRarity: White, Green, Blue, Purple, Gold, Mythic.
        static readonly int[] Caps = { 5, 10, 15, 20, 30, 30 };
        static readonly int[] RankUpBlueprints = { 1, 1, 2, 3, 4, 0 };
        static readonly float[] RarityBase = { 1.00f, 1.08f, 1.16f, 1.26f, 1.36f, 1.50f };
        static readonly int[] OffSkills = { 45, 50, 55, 62, 70, 80 };
        static readonly float[] StrikeBase = { 0.78f, 0.80f, 0.82f, 0.85f, 0.88f, 0.90f };
        static readonly float[] ToolBonuses = { 0.03f, 0.05f, 0.07f, 0.10f, 0.13f, 0.17f };
        static readonly float[] RarityWage = { 1.0f, 1.2f, 1.45f, 1.75f, 2.1f, 2.5f };

        // Wage inputs (section 2.3), indexed by tier 1..5.
        static readonly int[] TierBase = { 0, 8, 15, 30, 60, 120 };

        static int R(CardRarity rarity) => rarity < CardRarity.White ? 0 : rarity > CardRarity.Mythic ? 5 : (int)rarity;

        // Player-facing name: gold is called Legendary in the game.
        public static string RarityName(CardRarity rarity) => rarity == CardRarity.Gold ? "Legendary" : rarity.ToString();

        public static int ClampLevel(int level) => level < 1 ? 1 : level > MaxLevel ? MaxLevel : level;

        public static int LevelCap(CardRarity rarity) => Caps[R(rarity)];

        // Tokens and coins to go from `level` to level + 1.
        public static int TokensForLevel(int level) => (int)Math.Round(Math.Pow(ClampLevel(level), 1.6), MidpointRounding.AwayFromZero) + 1;
        public static int CoinsForLevel(int level) => (int)Math.Round(15.0 * Math.Pow(ClampLevel(level), 1.5), MidpointRounding.AwayFromZero);

        // Blueprints to move from `rarity` to the next one; 0 at Mythic (stars take over).
        public static int BlueprintsToRankUp(CardRarity rarity) => RankUpBlueprints[R(rarity)];
        public static bool CanRankUp(CardRarity rarity) => rarity < CardRarity.Mythic;

        // Blueprints for the next star of a Mythic card holding `stars` (2, 3, 4, 5, 6); 0 once at MaxStars.
        public static int BlueprintsForStar(int stars) => stars < 0 ? 2 : stars >= MaxStars ? 0 : stars + 2;

        // Blueprints from `rarity` with `stars` to the very top (Mythic, five stars).
        public static int BlueprintsToTop(CardRarity rarity, int stars)
        {
            int total = 0;
            for (var r = rarity; r < CardRarity.Mythic; r++) total += BlueprintsToRankUp(r);
            for (int s = rarity == CardRarity.Mythic ? stars : 0; s < MaxStars; s++) total += BlueprintsForStar(s);
            return total;
        }

        public static int ToolSlots(CardRarity rarity) => rarity >= CardRarity.Gold ? 3 : rarity >= CardRarity.Blue ? 2 : 1;
        public static float ToolBonus(CardRarity toolRarity) => ToolBonuses[R(toolRarity)];

        // 1 + 0.012 x (level - 1)
        public static float LevelMult(int level) => 1f + 0.012f * (ClampLevel(level) - 1);

        // Work speed: rarity base x level x stars (tools and abilities multiply on top, per job).
        public static float WorkMult(CardRarity rarity, int level, int stars) =>
            RarityBase[R(rarity)] * LevelMult(level) * (1f + 0.03f * Math.Max(0, Math.Min(MaxStars, stars)));
        public static float WorkMult(CardState card) => card == null ? 1f : WorkMult(card.Rarity, card.Level, card.Stars);

        // Haul tokens (section 2): tier x crew aboard x hold fill, +15% for a full hold, rounded down.
        public const float FullHoldFill = 0.95f, FullHaulBonus = 0.15f;
        public static int HaulTokens(int tier, int crew, float fill)
        {
            if (tier <= 0 || crew <= 0 || !(fill > 0f)) return 0;
            if (fill > 1f) fill = 1f;
            double tokens = tier * crew * (double)fill * (fill >= FullHoldFill ? 1.0 + FullHaulBonus : 1.0);
            return (int)Math.Floor(tokens + 1e-6);
        }

        // Abilities switch on at their unlock rarity; a trait is on from the card's start.
        public static bool HasAbility(CardRarity rarity, AbilityDef ability) => ability != null && rarity >= ability.Unlock;

        // Wage per voyage: tierBase[T] * rarityMult * (1 + 0.01 * (level - 1)), rounded to whole coins.
        public static int Wage(int tier, CardRarity rarity, int level)
        {
            int t = tier < 1 ? 1 : tier > 5 ? 5 : tier;
            double w = TierBase[t] * (double)RarityWage[R(rarity)] * (1.0 + 0.01 * (ClampLevel(level) - 1));
            return (int)Math.Round(w, MidpointRounding.AwayFromZero);
        }

        // Non-speciality skill by rarity.
        public static int OffSkill(CardRarity rarity) => OffSkills[R(rarity)];

        // Fisher strike chance by rarity, +0.25 percentage points per level above 1, cap 97%.
        public static float StrikeChance(CardRarity rarity, int level)
        {
            float c = StrikeBase[R(rarity)] + 0.0025f * (ClampLevel(level) - 1);
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
