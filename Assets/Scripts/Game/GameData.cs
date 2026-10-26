using UnityEngine;

namespace Catchline.Game
{
    // Append only: numeric species IDs are stored in existing saves/contracts.
    public enum Species { Herring, Mackerel, Pollock, SeaBass, Conger, Plaice, Cod, Whiting, RedMullet, Turbot, GoldenPuffer, SpottedEagleRay, ApexReefShark, GoldTipShark, AbyssalGreatWhite, AbyssalLeviathan, BlueSpottedStingray, FlyingFish, Lionfish, GiantDevilManta, AtlanticSwordfish, OceanSunfish, ScallopedHammerhead, PelagicThresherShark, GiantSquid, YellowfinTuna, Barracuda, MahiMahi, Monkfish, Crab }
    public enum UpgradeId { BigCooler, IceBox, RodHolder, LunchTin, RodFibreglass, RodCarbon, NetSystem, ThirdDeepLine }
    public enum Grade { Hand, Experienced, Veteran }
    public enum CrewRole { Deckhand, Fisherman, Engineer, Navigator }
    public enum DeckhandWork { Fish, Nets, Prep }

    // Deck coordinates follow the game grid: X stern-to-bow (bow at -X), Y port-to-starboard.
    public class HullDef
    {
        public string Name, Model;
        public int Width, Height, Capacity, CrewCap;
        public float TravelMultiplier; // legacy chart score only; never controls runtime sailing
        public float SailSpeed = 10f; // metres/sec: the ONE trip-duration tuning value per hull
        public float TurnDegreesPerSecond = 120f;
        public float NavigationRadius => Height * CellSize * .5f + .5f;
        public float CellSize = 1f;
        public Vector2Int Hold, HoldAccess, Seat, Rest, NetAccess;
        public Vector2Int[] CrewRest;
        public Vector2Int[] Blocked, RodTiles;
        public Vector3[] RodBases;
        public Vector3 Center => new((Width - 1) * CellSize * 0.5f, 0f, (Height - 1) * CellSize * 0.5f);
    }

    public class FishDef
    {
        public Species Species;
        public string Name;
        public float MinKg, MaxKg;
        public float PricePerKg;
        public Color Color;
        public float Length;     // metres, for the model
        public float Heaviness;  // 0..1: how much longer casts favour this fish
        public float AvgValue => (MinKg + MaxKg) * 0.5f * PricePerKg * 1.25f;
    }

    public class SpotDef
    {
        public string Name, Blurb;
        public float RowSeconds;
        public float BiteWait = 1f; // multiplier on time to a bite
        public int ChartCost;       // 0 = known from the start
        public Vector2 MapPos;      // 0..1 on the harbour master's chart
        public Color Water;
        public (Species species, float weight)[] Table;
    }

    public class UpgradeDef
    {
        public UpgradeId Id;
        public string Name, Desc;
        public int Cost;
        public UpgradeId? Requires;
        public string Shop = "Chandlery";
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
            new() { Species = Species.Mackerel, Name = "Mackerel", MinKg = 0.3f, MaxKg = 0.7f, PricePerKg = 13f, Color = Palette.Hex("3F8C8A"), Length = 0.34f, Heaviness = 0.2f },
            new() { Species = Species.Pollock, Name = "Pollock", MinKg = 0.8f, MaxKg = 2.5f, PricePerKg = 15f, Color = Palette.Hex("8C7A4E"), Length = 0.48f, Heaviness = 0.5f },
            new() { Species = Species.SeaBass, Name = "Sea bass", MinKg = 1.0f, MaxKg = 3.0f, PricePerKg = 19f, Color = Palette.Hex("A9B4B8"), Length = 0.5f, Heaviness = 0.7f },
            new() { Species = Species.Conger, Name = "Conger eel", MinKg = 3f, MaxKg = 8f, PricePerKg = 18f, Color = Palette.Hex("4A4E52"), Length = 0.8f, Heaviness = 1f },
            new() { Species = Species.Plaice, Name = "Plaice", MinKg = 0.4f, MaxKg = 1.4f, PricePerKg = 16f, Color = Palette.Hex("B59A6A"), Length = 0.36f, Heaviness = 0.35f },
            new() { Species = Species.Cod, Name = "Cod", MinKg = 2f, MaxKg = 7f, PricePerKg = 17f, Color = Palette.Hex("8E9A6C"), Length = 0.7f, Heaviness = 0.85f },
            new() { Species = Species.Whiting, Name = "Whiting", MinKg = 0.4f, MaxKg = 1.3f, PricePerKg = 14f, Color = Palette.Hex("BAC9C6"), Length = 0.38f, Heaviness = 0.4f },
            new() { Species = Species.RedMullet, Name = "Red mullet", MinKg = 0.6f, MaxKg = 1.6f, PricePerKg = 18f, Color = Palette.Hex("C77D65"), Length = 0.34f, Heaviness = 0.45f },
            new() { Species = Species.Turbot, Name = "Turbot", MinKg = 1.5f, MaxKg = 5f, PricePerKg = 22f, Color = Palette.Hex("8C7A4E"), Length = 0.58f, Heaviness = 0.9f },
            new() { Species = Species.GoldenPuffer, Name = "Crown pufferfish", MinKg = .2f, MaxKg = .6f, PricePerKg = 400, Color = Palette.Hex("E6B746"), Length = .32f, Heaviness = .4f },
            new() { Species = Species.SpottedEagleRay, Name = "Spotted eagle ray", MinKg = 4, MaxKg = 12, PricePerKg = 24, Color = Palette.Hex("467D9D"), Length = .8f, Heaviness = .85f },
            new() { Species = Species.ApexReefShark, Name = "Sun-gilded reef shark", MinKg = 8, MaxKg = 20, PricePerKg = 24, Color = Palette.Hex("BDA66A"), Length = 1.0f, Heaviness = .95f },
            new() { Species = Species.GoldTipShark, Name = "Gold-tip shark", MinKg = 12, MaxKg = 30, PricePerKg = 26, Color = Palette.Hex("9D8954"), Length = 1.1f, Heaviness = 1f },
            new() { Species = Species.AbyssalGreatWhite, Name = "Scarred great white shark", MinKg = 20, MaxKg = 45, PricePerKg = 25, Color = Palette.Hex("5F7382"), Length = 1.25f, Heaviness = 1f },
            new() { Species = Species.AbyssalLeviathan, Name = "Abyssal killer whale", MinKg = 40, MaxKg = 85, PricePerKg = 24, Color = Palette.Hex("424B59"), Length = 1.45f, Heaviness = 1f },
            new() { Species = Species.BlueSpottedStingray, Name = "Blue-spotted stingray", MinKg = 1, MaxKg = 5, PricePerKg = 34, Color = Palette.Hex("D1AF76"), Length = .65f, Heaviness = .65f },
            new() { Species = Species.FlyingFish, Name = "Flying fish", MinKg = .2f, MaxKg = .8f, PricePerKg = 38, Color = Palette.Hex("2A6685"), Length = .4f, Heaviness = .3f },
            new() { Species = Species.Lionfish, Name = "Lionfish", MinKg = .3f, MaxKg = 1.5f, PricePerKg = 45, Color = Palette.Hex("E36A35"), Length = .42f, Heaviness = .45f },
            new() { Species = Species.GiantDevilManta, Name = "Giant devil manta", MinKg = 12, MaxKg = 40, PricePerKg = 25, Color = Palette.Hex("28343B"), Length = 1.3f, Heaviness = 1f },
            new() { Species = Species.AtlanticSwordfish, Name = "Atlantic swordfish", MinKg = 10, MaxKg = 30, PricePerKg = 28, Color = Palette.Hex("2A6685"), Length = 1.15f, Heaviness = .95f },
            new() { Species = Species.OceanSunfish, Name = "Ocean sunfish", MinKg = 8, MaxKg = 25, PricePerKg = 24, Color = Palette.Hex("8FA6AC"), Length = .85f, Heaviness = .9f },
            new() { Species = Species.ScallopedHammerhead, Name = "Scalloped hammerhead", MinKg = 12, MaxKg = 35, PricePerKg = 26, Color = Palette.Hex("696F64"), Length = 1.15f, Heaviness = 1f },
            new() { Species = Species.PelagicThresherShark, Name = "Pelagic thresher shark", MinKg = 10, MaxKg = 30, PricePerKg = 27, Color = Palette.Hex("2A6685"), Length = 1.1f, Heaviness = 1f },
            new() { Species = Species.GiantSquid, Name = "Giant Architeuthis squid", MinKg = 20, MaxKg = 65, PricePerKg = 30, Color = Palette.Hex("A9433C"), Length = 1.2f, Heaviness = 1f },
            // FISH050: signature Big Common species, fixed class at every specimen size.
            new() { Species = Species.YellowfinTuna, Name = "Yellowfin tuna", MinKg = 3f, MaxKg = 10f, PricePerKg = 14f, Color = Palette.Hex("173F57"), Length = .82f, Heaviness = .8f },
            new() { Species = Species.Barracuda, Name = "Barracuda", MinKg = 1.5f, MaxKg = 5f, PricePerKg = 15f, Color = Palette.Hex("696F64"), Length = .88f, Heaviness = .65f },
            new() { Species = Species.MahiMahi, Name = "Mahi-mahi", MinKg = 2f, MaxKg = 7f, PricePerKg = 16f, Color = Palette.Hex("168F9F"), Length = .78f, Heaviness = .75f },
            new() { Species = Species.Monkfish, Name = "Monkfish", MinKg = 1.5f, MaxKg = 6f, PricePerKg = 16f, Color = Palette.Hex("696F64"), Length = .68f, Heaviness = .7f },
            new() { Species = Species.Crab, Name = "Edible crab", MinKg = .5f, MaxKg = 1.8f, PricePerKg = 28f, Color = Palette.Hex("E36A35"), Length = .28f, Heaviness = .35f },
        };

        // UI041 append-only IDs: rarity controls presentation; these values are first-pass tuning.
        public static int MinimumHull(Species s) => s switch
        {
            Species.Crab => 4,
            Species.YellowfinTuna or Species.Barracuda or Species.MahiMahi or Species.Monkfish => 2,
            Species.GoldenPuffer or Species.SpottedEagleRay or Species.BlueSpottedStingray or Species.FlyingFish or Species.Lionfish => 2,
            Species.ApexReefShark or Species.GoldTipShark or Species.AbyssalGreatWhite or Species.AbyssalLeviathan or Species.GiantDevilManta or Species.AtlanticSwordfish or Species.OceanSunfish or Species.ScallopedHammerhead or Species.PelagicThresherShark or Species.GiantSquid => 3,
            _ => 0
        };

        public static FishDef Get(Species s) => Fish[(int)s];

        public static readonly SpotDef[] Spots =
        {
            new()
            {
                Name = "Harbour mouth", Blurb = "Quick bites from small schools. Squid draws whiting below them.", RowSeconds = 5f, BiteWait = 0.85f, Water = Palette.Hex("1E9AA8"),
                MapPos = new Vector2(0.3f, 0.55f),
                Table = new[] { (Species.Herring, 54f), (Species.Mackerel, 36f), (Species.Whiting, 10f) },
            },
            new()
            {
                Name = "Kelp bank", Blurb = "Mackerel schools in the kelp, pollock below.", RowSeconds = 9f, BiteWait = 1f, Water = Palette.Hex("2A8C80"),
                MapPos = new Vector2(0.42f, 0.25f),
                Table = new[] { (Species.Herring, 10f), (Species.Mackerel, 40f), (Species.Pollock, 28f), (Species.SeaBass, 10f), (Species.Whiting, 12f), (Species.GoldenPuffer, .6f), (Species.FlyingFish, .8f), (Species.Lionfish, .3f), (Species.Barracuda, 3f), (Species.MahiMahi, 2f) },
            },
            new()
            {
                Name = "Sandbar", Blurb = "Warm, shallow and sandy. Flatfish lie on the bottom.", RowSeconds = 11f, BiteWait = 1.05f, Water = Palette.Hex("3FB3B0"),
                ChartCost = 120, MapPos = new Vector2(0.5f, 0.78f),
                Table = new[] { (Species.Mackerel, 15f), (Species.Plaice, 35f), (Species.SeaBass, 20f), (Species.RedMullet, 22f), (Species.Turbot, 8f), (Species.GoldenPuffer, .4f), (Species.SpottedEagleRay, .35f), (Species.BlueSpottedStingray, .4f), (Species.FlyingFish, .4f), (Species.Lionfish, .3f), (Species.Monkfish, 4f) },
            },
            new()
            {
                Name = "Rocky point", Blurb = "A long row. Big fish hide between the rocks.", RowSeconds = 14f, BiteWait = 1.3f, Water = Palette.Hex("1A7591"),
                ChartCost = 220, MapPos = new Vector2(0.7f, 0.18f),
                Table = new[] { (Species.Mackerel, 12f), (Species.Pollock, 35f), (Species.SeaBass, 28f), (Species.Conger, 15f), (Species.RedMullet, 10f), (Species.SpottedEagleRay, .5f), (Species.ApexReefShark, .12f), (Species.GoldTipShark, .06f), (Species.GiantDevilManta, .08f), (Species.AtlanticSwordfish, .08f), (Species.ScallopedHammerhead, .04f), (Species.PelagicThresherShark, .04f), (Species.Barracuda, 6f), (Species.MahiMahi, 4f) },
            },
            new()
            {
                Name = "Deep channel", Blurb = "Open water past the point. Cod and big eels, slow bites. Check your fuel.", RowSeconds = 20f, BiteWait = 1.5f, Water = Palette.Hex("15587A"),
                ChartCost = 500, MapPos = new Vector2(0.88f, 0.55f),
                Table = new[] { (Species.Pollock, 25f), (Species.Cod, 40f), (Species.Conger, 25f), (Species.Turbot, 10f), (Species.SpottedEagleRay, .3f), (Species.ApexReefShark, .12f), (Species.GoldTipShark, .08f), (Species.AbyssalGreatWhite, .04f), (Species.AbyssalLeviathan, .015f), (Species.GiantDevilManta, .08f), (Species.AtlanticSwordfish, .12f), (Species.OceanSunfish, .15f), (Species.ScallopedHammerhead, .06f), (Species.PelagicThresherShark, .06f), (Species.GiantSquid, .012f), (Species.YellowfinTuna, 6f), (Species.Monkfish, 5f) },
            },
            new()
            {
                Name = "Seal skerries", Blurb = "Granite skerries and a seal colony. Crabs on the rocks, big fish on the reef. Bring fuel.", RowSeconds = 24f, BiteWait = 1.35f, Water = Palette.Hex("1C6E7E"),
                ChartCost = 2500, MapPos = new Vector2(.88f, .12f),
                Table = new[] { (Species.Crab, 20f), (Species.Conger, 20f), (Species.Pollock, 20f), (Species.Cod, 25f), (Species.Monkfish, 14f), (Species.Turbot, 1f) },
            },
            new()
            {
                Name = "Wreck bank", Blurb = "An old steamer on the sandbank. Congers in the wreck, herring on the bank, flatfish at the edge.", RowSeconds = 26f, BiteWait = 1.3f, Water = Palette.Hex("2E8C8A"),
                ChartCost = 4000, MapPos = new Vector2(.72f, .06f),
                Table = new[] { (Species.Conger, 40f), (Species.Cod, 30f), (Species.Pollock, 25f), (Species.Turbot, 2f), (Species.Herring, 50f), (Species.Mackerel, 30f), (Species.Whiting, 45f), (Species.Plaice, 50f), (Species.SpottedEagleRay, 1f) },
            },
            new()
            {
                Name = "Lighthouse rock", Blurb = "A lighthouse on a lone rock. Bass in the tide race, cod and monkfish down the ledge.", RowSeconds = 30f, BiteWait = 1.4f, Water = Palette.Hex("1F5F8C"),
                ChartCost = 6000, MapPos = new Vector2(.85f, .08f),
                Table = new[] { (Species.Pollock, 40f), (Species.SeaBass, 65f), (Species.Conger, 20f), (Species.GoldTipShark, 1f), (Species.Mackerel, 45f), (Species.YellowfinTuna, 3f), (Species.Cod, 35f), (Species.Monkfish, 30f), (Species.Turbot, 10f), (Species.AtlanticSwordfish, 1f) },
            },
            new()
            {
                Name = "Whale shelf", Blurb = "Out where the shelf drops away. Herring shoals, cod on the edge, whales passing through.", RowSeconds = 34f, BiteWait = 1.5f, Water = Palette.Hex("2A7F96"),
                ChartCost = 8500, MapPos = new Vector2(.88f, .04f),
                Table = new[] { (Species.Herring, 50f), (Species.Mackerel, 70f), (Species.Whiting, 12f), (Species.FlyingFish, 2f), (Species.Cod, 30f), (Species.Pollock, 50f), (Species.Conger, 20f), (Species.Turbot, 10f), (Species.AbyssalGreatWhite, 1f), (Species.SeaBass, 25f), (Species.SpottedEagleRay, 3f) },
            },
            new()
            {
                Name = "Seal cliffs", Blurb = "Cliffs, a sea arch and seals on the stones. Wrasse in the pool, cod in the race.", RowSeconds = 36f, BiteWait = 1.5f, Water = Palette.Hex("2A7F96"),
                ChartCost = 11000, MapPos = new Vector2(.08f, .88f),
                Table = new[] { (Species.Pollock, 70f), (Species.RedMullet, 33f), (Species.Conger, 30f), (Species.Crab, 2f), (Species.Mackerel, 40f), (Species.Herring, 30f), (Species.SeaBass, 20f), (Species.Cod, 35f), (Species.Turbot, 1f) },
            },
        };

        public static readonly UpgradeDef[] Upgrades =
        {
            new() { Id = UpgradeId.RodHolder, Name = "Rod holder", Cost = 250, Desc = "A second rod. A rod nobody is holding hooks a biting fish by itself 35% of the time; otherwise the fish usually keeps nibbling." },
            new() { Id = UpgradeId.BigCooler, Name = "Big cooler", Cost = 60, Desc = "Rowboat: 20 to 35 kg. Powered boats: 50% more hold weight." },
            new() { Id = UpgradeId.IceBox, Name = "Ice box", Cost = 250, Desc = "Fish keep full value. Without ice they lose up to 40% the longer they sit." },
            new() { Id = UpgradeId.LunchTin, Name = "Extra fuel tank", Cost = 100, Desc = "Double fuel capacity: 20 minutes instead of 10.", Shop = "Supplies" },
            // Retired from the market (crew cards v2): the captain's rod tool picks the rods now (GameState.RodTier).
            new() { Id = UpgradeId.RodFibreglass, Name = "Fibreglass rods", Cost = 180, Shop = "Retired", Desc = "Longer strike window (1.15 s) and 25% faster reeling." },
            new() { Id = UpgradeId.RodCarbon, Name = "Carbon rods", Cost = 450, Shop = "Retired", Requires = UpgradeId.RodFibreglass, Desc = "Strike window 1.4 s, 50% faster reeling, and an unattended rod hooks the fish itself 45% of the time." },
            new() { Id = UpgradeId.NetSystem, Name = "Heavy net system", Cost = 5000, Desc = "Increase the capacity of both shallow and deep nets." },
            new() { Id = UpgradeId.ThirdDeepLine, Name = "Third deep-line rig", Cost = 3500, Desc = "Tier 5: fit a third deep-line rod between the crab cage and normal rod. One self-made chum per rig; one fish after a 60-second soak. Used in the rod / deep-line layout." },
        };

        public static UpgradeDef Upgrade(UpgradeId id)
        {
            foreach (var u in Upgrades)
                if (u.Id == id) return u;
            return null;
        }

        // Rod cycle (seconds)
        // Base durations at skill 100, level 1 (CARDS-AND-SPEEDS section 4). WorkSpeed.Duration applies the one work-speed formula.
        public const float BaitTime = 1.0f;
        public const float CastTime = 0.5f;
        public const float FlightTime = 0.6f;
        public const float BiteWindow = 0.9f;
        public const float MaxBiteWait = 15f;
        public const float ShallowNetSoakSeconds = 40f;
        public const float DeepNetSoakSeconds = 60f;
        public const float SelfHookChance = 0.35f;
        public const float PickupTime = 0.5f;
        public const float StowTime = 0.6f;
        public const float NetGatherTime = 0.5f;
        public const float NetSetTime = 2f;
        public const float TableHandleTime = 0.2f, TableSortTime = 1.5f, ChumUnitTime = 3f;
        public const float DeckFishLifetime = 25f;
        public const float WalkSpeed = 2.2f;

        // Economy
        public const int StartCoins = 40;
        public const int NetReplacementCost = 30, NetInventoryCapacity = 4;
        public const int DeepNetCost = 100, DeepNetUses = 3, DeepNetRackCapacity = 3;
        public const int StartBait = 15;
        public const int BaitPackSize = 10, BaitPackCost = 10;
        public const int SquidPackSize = 5, SquidPackCost = 15; // squid draws bigger fish
        public const int BaitBulkSize = 30, BaitBulkCost = 24;
        public const int SquidBulkSize = 15, SquidBulkCost = 36;
        public const float SquidPowerBonus = 0.4f;
        public const int FoodCostPerMinute = 1;
        public const float RichnessPerCatch = 0.035f;
        public const float RichnessRecovery = 0.2f;
        public const float FreshnessGraceSeconds = 60f;
        public const float FreshnessLossPerMinute = 0.07f, MinFreshness = 0.6f;
        public const int MaxActiveContracts = 2;

        public static readonly HullDef[] Hulls =
        {
            // Crew roles are flexible; every hull keeps enough offers for each available berth.
            new() { Name = "Rowboat", Model = "Rowboat", SailSpeed = 10f, Width = 3, Height = 2, Capacity = 20, CrewCap = 0,
                TravelMultiplier = 1f, Hold = new(1, 1), HoldAccess = new(1, 0), Seat = new(1, 0), Rest = new(0, 1),
                Blocked = new[] { new Vector2Int(1, 1) }, RodTiles = new[] { new Vector2Int(0, 0), new Vector2Int(2, 0) },
                RodBases = new[] { new Vector3(0f, .44f, -.615f), new Vector3(2f, .44f, -.615f) } },
            new() { Name = "Skiff", Model = "Skiff", SailSpeed = 10f, Width = 5, Height = 3, Capacity = 40, CrewCap = 2,
                TravelMultiplier = .5f, Hold = new(1, 1), HoldAccess = new(1, 0), Seat = new(3, 0), Rest = new(0, 1),
                CrewRest = new[] { new Vector2Int(0, 1), new Vector2Int(3, 1) },
                Blocked = new[] { new Vector2Int(1, 1), new Vector2Int(2, 1), new Vector2Int(4, 2), new Vector2Int(4, 1) },
                RodTiles = new[] { new Vector2Int(0, 0), new Vector2Int(2, 0), new Vector2Int(4, 0) },
                RodBases = new[] { new Vector3(.25f, .45f, -.68f), new Vector3(2f, .45f, -.68f), new Vector3(3.75f, .45f, -.68f) } },
            // Additive saved ID. Tier/economy labels can change without migrating old boats.
            new() { Name = "Compact fisher", Model = "CompactFisherV1", SailSpeed = 10f, Width = 43, Height = 23, CellSize = .1f,
                Capacity = 100, CrewCap = 4, TravelMultiplier = .5f,
                // Unity FBX import reflects source X; these are verified native socket/deck coordinates.
                Hold = new(29, 17), HoldAccess = new(29, 11), Seat = new(13, 12), Rest = new(30, 2), NetAccess = new(39, 6),
                CrewRest = new[] { new Vector2Int(30, 2), new Vector2Int(9, 20), new Vector2Int(23, 11), new Vector2Int(6, 2) },
                Blocked = System.Array.Empty<Vector2Int>(),
                RodTiles = new[] { new Vector2Int(21, 18), new Vector2Int(21, 3), new Vector2Int(38, 18) },
                RodBases = new[] { new Vector3(2f, .47f, 2.38f), new Vector3(2f, .47f, -.18f), new Vector3(3.75f, .47f, 2.33f) } },
            // Tier4 approved BOAT032 hull. Existing saved IDs0-2 stay unchanged.
            // First integration retains tier3 cargo/net capacity; economy unlock is still untuned.
            new() { Name = "Prep fisher", Model = "PrepFisherV1", SailSpeed = 10f, Width = 57, Height = 29, CellSize = .1f,
                Capacity = 160, CrewCap = 6, TravelMultiplier = .5f,
                Hold = new(29, 14), HoldAccess = new(29, 24), Seat = new(15, 15), Rest = new(10, 26), NetAccess = new(53, 4),
                CrewRest = new[] { new Vector2Int(10, 26), new Vector2Int(37, 26), new Vector2Int(23, 11), new Vector2Int(45, 2), new Vector2Int(22, 4), new Vector2Int(15, 21) },
                Blocked = System.Array.Empty<Vector2Int>(),
                RodTiles = new[] { new Vector2Int(28, 24), new Vector2Int(28, 4), new Vector2Int(50, 24) },
                RodBases = new[] { new Vector3(2.8f, .47f, 3f), new Vector3(2.8f, .47f, -.2f), new Vector3(5.0037f, .47f, 2.9375f) } },
            // Tier5 approved8.5x4.2m model. Two optional rods exchange for a secondnet.
            new() { Name = "Buoy fisher", Model = "Tier5DeepLines103", SailSpeed = 10f, Width = 73, Height = 35, CellSize = .1f,
                Capacity = 240, CrewCap = 8, TravelMultiplier = .5f,
                Hold = new(61,17), HoldAccess = new(61,30), Seat = new(20,17), Rest = new(39,28), NetAccess = new(65,27),
                CrewRest = new[] { new Vector2Int(39,28), new Vector2Int(70,16), new Vector2Int(30,7), new Vector2Int(63,32), new Vector2Int(60,2), new Vector2Int(19,24), new Vector2Int(30,24), new Vector2Int(12,25) },
                Blocked = System.Array.Empty<Vector2Int>(),
                RodTiles = new[] { new Vector2Int(33,31), new Vector2Int(33,3), new Vector2Int(47,3), new Vector2Int(62,3) },
                RodBases = new[] { new Vector3(3.25f,.47f,3.6f), new Vector3(3.25f,.47f,-.2f), new Vector3(4.7f,.47f,-.2f), new Vector3(6.15f,.47f,-.2f) } },
        };

        // Legacy pack constants retained for fixtures. Timed tanks use GameState.FuelFillCost.
        public const int FuelPackSize = 10, FuelPackCost = 10;
        public static int TripFuel(int spot) => Mathf.CeilToInt(Spots[spot].RowSeconds / 5f);

        // Hull goal
        public const int SkiffFishGoal = 16, SkiffCost = 1500;

        // Crew contracts: experienced costs 2x for 1.5x the voyages; veterans are rare.
        public static int ContractVoyages(Grade g) => g switch { Grade.Hand => 2, Grade.Experienced => 3, _ => 5 };
        public static int Fee(Grade g) => g switch { Grade.Hand => 30, Grade.Experienced => 60, _ => 150 };
        public static float StrikeChance(Grade g) => g switch { Grade.Hand => .80f, Grade.Experienced => .85f, _ => .90f };
        public const float NetSoakMin = 60f, NetSoakMax = 90f, NetHaulTime = 5f;
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
