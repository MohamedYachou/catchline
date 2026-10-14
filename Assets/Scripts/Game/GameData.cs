using UnityEngine;

namespace Catchline.Game
{
    public enum Species { Herring, Mackerel, Pollock, SeaBass, Conger }
    public enum UpgradeId { BigCooler, IceBox, RodHolder, LunchTin }
    public enum Grade { Hand, Experienced, Veteran }

    public class FishDef
    {
        public Species Species;
        public string Name;
        public float MinKg, MaxKg;
        public float PricePerKg;
        public Color Color;
        public float Length;     // metres, for the model
        public float Heaviness;  // 0..1: how much longer casts favour this fish
        public float AvgValue => (MinKg + MaxKg) * 0.5f * PricePerKg;
    }

    public class SpotDef
    {
        public string Name, Blurb;
        public float RowSeconds;
        public float BiteWait = 1f; // multiplier on time to a bite
        public Color Water;
        public (Species species, float weight)[] Table;
    }

    public class UpgradeDef
    {
        public UpgradeId Id;
        public string Name, Desc;
        public int Cost;
    }

    public static class Palette
    {
        public static readonly Color DeckWood = Hex("C58B50");
        public static readonly Color DeckWoodDark = Hex("B07A44");
        public static readonly Color HullNavy = Hex("173F57");
        public static readonly Color Rail = Hex("F3F0DC");
        public static readonly Color Accent = Hex("E36A35");
        public static readonly Color Sea = Hex("168F9F");
        public static readonly Color Oilskin = Hex("E6AD38");
        public static readonly Color Steel = Hex("8FA6AC");
        public static readonly Color Rubber = Hex("28343B");
        public static readonly Color Cream = Hex("F4EFE3");
        public static readonly Color Skin = Hex("F2C6A0");
        public static readonly Color Good = Hex("3E9A5B");
        public static readonly Color Bad = Hex("C8443A");

        public static Color Hex(string h)
        {
            ColorUtility.TryParseHtmlString("#" + h, out var c);
            return c;
        }
    }

    // All tuning numbers for build 1 live here.
    public static class GameData
    {
        public const string HarbourName = "Gull Harbour";

        public static readonly FishDef[] Fish =
        {
            new() { Species = Species.Herring, Name = "Herring", MinKg = 0.12f, MaxKg = 0.3f, PricePerKg = 12f, Color = Palette.Hex("9DB8C9"), Length = 0.26f, Heaviness = 0f },
            new() { Species = Species.Mackerel, Name = "Mackerel", MinKg = 0.3f, MaxKg = 0.7f, PricePerKg = 10f, Color = Palette.Hex("3F8C8A"), Length = 0.34f, Heaviness = 0.2f },
            new() { Species = Species.Pollock, Name = "Pollock", MinKg = 0.8f, MaxKg = 2.5f, PricePerKg = 6f, Color = Palette.Hex("8C7A4E"), Length = 0.48f, Heaviness = 0.5f },
            new() { Species = Species.SeaBass, Name = "Sea bass", MinKg = 1.0f, MaxKg = 3.0f, PricePerKg = 9f, Color = Palette.Hex("A9B4B8"), Length = 0.5f, Heaviness = 0.7f },
            new() { Species = Species.Conger, Name = "Conger eel", MinKg = 3f, MaxKg = 8f, PricePerKg = 4f, Color = Palette.Hex("4A4E52"), Length = 0.8f, Heaviness = 1f },
        };

        public static FishDef Get(Species s) => Fish[(int)s];

        public static readonly SpotDef[] Spots =
        {
            new()
            {
                Name = "Harbour mouth", Blurb = "Close by. Small fish, quick bites.", RowSeconds = 5f, BiteWait = 0.85f, Water = Palette.Hex("1E9AA8"),
                Table = new[] { (Species.Herring, 60f), (Species.Mackerel, 40f) },
            },
            new()
            {
                Name = "Kelp bank", Blurb = "Mackerel schools in the kelp, pollock below.", RowSeconds = 9f, BiteWait = 1f, Water = Palette.Hex("2A8C80"),
                Table = new[] { (Species.Herring, 15f), (Species.Mackerel, 50f), (Species.Pollock, 28f), (Species.SeaBass, 7f) },
            },
            new()
            {
                Name = "Rocky point", Blurb = "A long row. Big fish hide between the rocks.", RowSeconds = 14f, BiteWait = 1.3f, Water = Palette.Hex("1A7591"),
                Table = new[] { (Species.Mackerel, 20f), (Species.Pollock, 42f), (Species.SeaBass, 28f), (Species.Conger, 10f) },
            },
        };

        public static readonly UpgradeDef[] Upgrades =
        {
            new() { Id = UpgradeId.RodHolder, Name = "Rod holder", Cost = 250, Desc = "A second rod. A rod nobody is holding hooks a biting fish by itself 35% of the time; otherwise the fish usually keeps nibbling." },
            new() { Id = UpgradeId.BigCooler, Name = "Big cooler", Cost = 200, Desc = "Holds 16 fish instead of 10, so you stay out longer." },
            new() { Id = UpgradeId.IceBox, Name = "Ice box", Cost = 250, Desc = "Fish keep full value. Without ice they lose up to 40% the longer they sit." },
            new() { Id = UpgradeId.LunchTin, Name = "Lunch tin", Cost = 100, Desc = "Carry 12 minutes of food instead of 6." },
        };

        public static UpgradeDef Upgrade(UpgradeId id)
        {
            foreach (var u in Upgrades)
                if (u.Id == id) return u;
            return null;
        }

        // Rod cycle (seconds)
        public const float BaitTime = 1.2f;
        public const float CastTime = 0.45f;
        public const float FlightTime = 0.6f;
        public const float BiteWindow = 0.9f;
        public const float SelfHookChance = 0.35f;
        public const float PickupTime = 0.5f;
        public const float StowTime = 0.4f;
        public const float DeckFishLifetime = 25f;
        public const float WalkSpeed = 2.2f;
        public const float HungrySpeed = 0.7f;

        // Economy
        public const int StartCoins = 40;
        public const int StartBait = 15;
        public const int BaitPackSize = 10, BaitPackCost = 10;
        public const int FoodCostPerMinute = 2;
        public const float RichnessPerCatch = 0.035f;
        public const float RichnessRecovery = 0.2f;
        public const float MarketDropPerFish = 0.97f;
        public const float MarketRecovery = 0.35f;
        public const float FreshnessLossPerMinute = 0.07f, MinFreshness = 0.6f;
        public const int MaxActiveContracts = 2;

        // Hull goal (refit itself arrives in build 2)
        public const int SkiffFishGoal = 16, SkiffCost = 1500;

        // Crew contracts: experienced costs 2x for 1.5x the voyages, veterans are rare.
        public static float Speed(Grade g) => g switch { Grade.Hand => 1f, Grade.Experienced => 1.5f, _ => 2f };
        public static int ContractVoyages(Grade g) => g switch { Grade.Hand => 2, Grade.Experienced => 3, _ => 5 };
        public static int Fee(Grade g) => g switch { Grade.Hand => 30, Grade.Experienced => 60, _ => 150 };
        public static string GradeName(Grade g) => g switch { Grade.Hand => "Deckhand", Grade.Experienced => "Experienced", _ => "Veteran" };

        public static readonly string[] Names =
        {
            "Sam", "Jo", "Ana", "Bram", "Kofi", "Lise", "Mats", "Noor", "Pim", "Rosa", "Tess", "Yusuf", "Ines", "Dirk", "Mei", "Olaf",
        };

        public static readonly Color[] Suits =
        {
            Palette.Oilskin, Palette.Hex("4E8F5A"), Palette.Hex("7A5AA0"), Palette.Hex("3F6FB0"), Palette.Hex("B85A3C"),
        };
    }
}
