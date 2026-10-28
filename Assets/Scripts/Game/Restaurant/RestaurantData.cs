using System;
using System.Collections.Generic;
using System.Linq;

namespace Catchline.Game.Restaurant
{
    // Save IDs: append only. No production scene or GameState dependency.
    public enum ItemId { PrepCounter, Stove, SoupKettle, Grill, Fryer, Oven, Steamer, Fridge, Sink,
        CoffeeMachine, DrinksFridge, BarCounter, Table2, Table4, Booth6, TerraceTable, Reception,
        Trophy, Net, Lamp, Plant, Chart, Jukebox }
    public enum Area { Kitchen, Guests, Bar, Decor, Wall }
    public enum PreparedForm { Whole, Fillet, Stock, Platter, Crab, Squid }
    public enum Dish { GrilledFish, PanFish, FishAndChips, Soup, Platter, Crab, Calamari, Coffee, Tea, Lemonade, Beer, Fries, Bread, IceCream }
    public enum Job { Reception, Cook, Waiter, Barista, Handyman, Helper }
    public enum Weather { Fair, Sun, Rain }
    public enum PrepMargin { Tight, TenPercent, TwentyPercent }

    // All first-pass economic/timing/probability tuning is here. Values not specified in the plan are
    // deliberately provisional; reports expose them, and the live game's prices are untouched.
    public static class RestaurantTuning
    {
        // Service v2 (Mo 10-28, "no point in waiting 2 minutes for something to happen"): a night is about three
        // minutes of play. Everything a guest does takes seconds; walk-ins stream in all night on top of the bookings.
        public const float TickSeconds = .25f, NightSeconds = 240, DoorCloseSeconds = 180;
        public const float OffRole = .7f, Monday = .8f, BusyDay = 1.3f, Rain = .85f;
        public const float FilletKg = .4f, WholeMaxKg = .8f, StockBowlsPerKg = 4, PlatterMinKg = 4, SquidKg = .3f;
        public const float OffcutFraction = .2f, MarketMultiplier = .5f, DishMultiplier = 3, SellBack = .5f;
        public const float WalkInMax = .1f, MiraGrowthMax = .2f, DrinkChance = .8f, CoffeeChance = .3f, SpecialChance = .06f;
        public const float ForecastUncertainty = .12f, DoorPatience = 25, TablePatience = 45, DrinkPatience = 8;
        public const float SeatSeconds = .6f, OrderSeconds = 1, ServeSeconds = .6f, ClearSeconds = .8f, PlateSeconds = .6f;
        public const float EatSeconds = 12, DrinkSeconds = 1, CoffeeSeconds = 1.5f, SubstituteDelay = 2, RepairSeconds = 5;
        public const float ColdSeconds = 14, ColdPrice = .8f, PaymentSeconds = .8f, CoffeeWait = 8;
        public const float BreakdownPerSecond = .003f, TipRate = .12f, SpecialMultiplier = 2, AmbiencePatience = .5f;
        public const int FridgePortions = 15, KettleBatch = 8, BaseGuests = 8, GuestsPerPopularity = 1; // bookings; walk-ins fill the rest of the room (service v2)
        // Staff walk faster in the small room than on deck; the captain (the player's hands) beats any hire.
        public const float WalkBoost = 1.8f, CaptainBoost = 1.5f, LoadSeconds = .4f;
        // Walk-ins: a group every WalkInEvery seconds on average (faster as the night's stars climb), never while
        // WalkInQueue groups already wait at the door. ComboTip is paid per plate when one trip serves two tables.
        // A booked table waits BookingPatience times longer at the door than a walk-in, and Mira seats bookings first.
        public const float BookingPatience = 1.6f;
        // Harbour moment: the evening ferry moors and FerryGroups groups of passengers come up together; they tip FerryTip times more.
        public const int FerryGroups = 4; public const float FerryTip = 1.25f, FerryStay = 45f, FerryPatience = 2f; // nowhere else to eat: they wait
        public const float WalkInEvery = 6f, WalkInFishChance = .45f; public const int WalkInQueue = 3, CarryPlates = 2, ComboTip = 3;
        // Upsell bubbles: a few seconds into their meal a table may wave for another round; a tap within UpsellSeconds sells
        // it on the spot (per guest, at the staple price), no trip needed. Something to do while the kitchen works.
        public const float UpsellChance = .6f, UpsellAfter = 3f, UpsellSeconds = 5f;
        // Gulls: one lands on a table that is eating about every GullEvery seconds; tap it away within GullSeconds or it
        // steals from the plate (that table loses a star).
        public const float GullEvery = 20f, GullSeconds = 5f;
        // Hands-on plating: with nobody cooking but the captain, a fish dish waits on its station when done. A tap within
        // PerfectSeconds plates it perfect (PerfectTip); left BurnSeconds it burns (the portion is lost, the dish recooks).
        public const float PerfectSeconds = 2.5f, BurnSeconds = 7f; public const int PerfectTip = 4;
        public static readonly int[] ItemPrices = { 80,140,100,160,220,360,260,120,180,100,100,220,80,160,300,120,0,80,50,60,40,60,250 };
        public static readonly int[] StagePrices = { 0,0,1200,3500,8000 }, StagePopularity = { 0,0,3,5,8 };
        // Loaded and left: the station cooks by itself for this long while the cook does something else.
        public static float CookSeconds(Dish d) => d == Dish.Soup ? 4 : d == Dish.Platter ? 9 : d == Dish.Crab ? 6 : d == Dish.Bread ? 1.5f : d == Dish.Fries ? 3 : 4;
        public static int StaplePrice(Dish d) => d == Dish.IceCream ? 6 : d == Dish.Beer ? 5 : d == Dish.Coffee || d == Dish.Tea ? 4 : 3;
        public const int StapleCost = 1;
        public const float PopularityPerGuest = .01f, PopularityPerSpecial = .05f, PopularityPerRegular = .5f, BirthdayChance = .35f, RegularChance = .4f, TourChance = .3f;
    }

    // Night cards (Mo 10-28, our take on PlateUp's): after each night the player keeps one of three. Gadgets and dishes stay
    // for good; a night card shapes only the next night. Effects are read in VoyageRestaurantDay.ApplyNightCards.
    public enum NightCardKind { Gadget, Night, Dish }
    public sealed class NightCardDef { public string Id, Name, Effect; public NightCardKind Kind; }
    public static class NightCards
    {
        static NightCardDef C(string id, string name, NightCardKind kind, string effect) => new NightCardDef { Id = id, Name = name, Kind = kind, Effect = effect };
        public static readonly NightCardDef[] All = {
            C("warming-lamp", "Warming lamp", NightCardKind.Gadget, "Plates at the pass stay hot twice as long."),
            C("plate-rack", "Plate rack", NightCardKind.Gadget, "The captain carries three plates a trip."),
            C("service-bell", "Service bell", NightCardKind.Gadget, "Guests wait at the door 40% longer."),
            C("gull-net", "Gull net", NightCardKind.Gadget, "Half as many gulls land on your tables."),
            C("quick-shoes", "Quick shoes", NightCardKind.Gadget, "The captain works and walks 20% faster."),
            C("second-pan", "Second pan", NightCardKind.Gadget, "Fish cooks 25% faster."),
            C("ferry", "Ferry night", NightCardKind.Night, "The ferry brings six groups. Tips +20%."),
            C("critic", "Critic's table", NightCardKind.Night, "A critic dines. Five stars and the harbour hears."),
            C("festival", "Harbour festival", NightCardKind.Night, "More walk-ins and tips +20%, but more gulls too."),
            C("rain", "Rainy night", NightCardKind.Night, "Fewer walk-ins, no gulls, tips +30%."),
            C("catch", "Catch of the day", NightCardKind.Dish, "Every fish plate pays 2 coins more."),
            C("ice-cream", "Ice cream", NightCardKind.Dish, "Tables wave for ice cream too: 6 coins a bowl."),
        };
        public static NightCardDef Get(string id) => Array.Find(All, c => c.Id == id);
    }

    public sealed class ItemDef
    {
        public ItemId Id; public string Name; public Area Area; public int Width, Height = 1, Price, Stage = 1, Seats;
        public Dish[] Cooks = Array.Empty<Dish>();
    }
    public sealed class StageDef
    {
        public int Stage, Width, KitchenWidth, Depth = 5, TerraceWidth; public string Name;
        public int TotalWidth => Width + TerraceWidth;
        public int Price => RestaurantTuning.StagePrices[Stage];
        public int Popularity => RestaurantTuning.StagePopularity[Stage];
    }
    public sealed class DishDef
    {
        public Dish Id; public PreparedForm Form; public ItemId Appliance; public bool Staple;
    }
    public static class RestaurantData
    {
        static ItemDef I(ItemId id, string name, Area area, int width = 1, int seats = 0, int stage = 1, params Dish[] dishes) =>
            new ItemDef { Id=id, Name=name, Area=area, Width=width, Seats=seats, Stage=stage,
                Price=RestaurantTuning.ItemPrices[(int)id], Cooks=dishes };
        public static readonly ItemDef[] Items = {
            I(ItemId.PrepCounter,"Prep counter",Area.Kitchen), I(ItemId.Stove,"Stove",Area.Kitchen,1,0,1,Dish.PanFish),
            I(ItemId.SoupKettle,"Soup kettle",Area.Kitchen,1,0,1,Dish.Soup), I(ItemId.Grill,"Grill",Area.Kitchen,1,0,1,Dish.GrilledFish),
            I(ItemId.Fryer,"Fryer",Area.Kitchen,1,0,1,Dish.FishAndChips,Dish.Calamari,Dish.Fries),
            I(ItemId.Oven,"Oven",Area.Kitchen,1,0,2,Dish.Platter), I(ItemId.Steamer,"Steamer pot",Area.Kitchen,1,0,2,Dish.Crab),
            I(ItemId.Fridge,"Fridge",Area.Kitchen), I(ItemId.Sink,"Sink and dish rack (R4)",Area.Kitchen,2,0,4),
            I(ItemId.CoffeeMachine,"Coffee machine",Area.Bar,1,0,1,Dish.Coffee,Dish.Tea),
            I(ItemId.DrinksFridge,"Drinks fridge",Area.Bar,1,0,1,Dish.Lemonade,Dish.Beer),
            I(ItemId.BarCounter,"Bar counter",Area.Bar,2,2), I(ItemId.Table2,"Table for two",Area.Guests,1,2),
            I(ItemId.Table4,"Table for four",Area.Guests,2,4), I(ItemId.Booth6,"Booth for six",Area.Guests,2,6,3),
            I(ItemId.TerraceTable,"Terrace table",Area.Guests,1,2,2), I(ItemId.Reception,"Reception desk",Area.Guests),
            I(ItemId.Trophy,"Trophy mount",Area.Wall), I(ItemId.Net,"Net with floats",Area.Wall),
            I(ItemId.Lamp,"Lamp",Area.Wall), I(ItemId.Plant,"Plant",Area.Decor), I(ItemId.Chart,"Framed chart",Area.Wall),
            I(ItemId.Jukebox,"Jukebox",Area.Decor) };
        public static readonly StageDef[] Stages = {
            new StageDef { Stage=1,Name="Cafe",Width=8,KitchenWidth=3 },
            new StageDef { Stage=2,Name="Bistro",Width=10,KitchenWidth=4,TerraceWidth=3 },
            new StageDef { Stage=3,Name="Restaurant",Width=12,KitchenWidth=4,TerraceWidth=3 },
            new StageDef { Stage=4,Name="Seafood house",Width=14,KitchenWidth=5,TerraceWidth=3 } };
        public static readonly DishDef[] Dishes = {
            D(Dish.GrilledFish,PreparedForm.Whole,ItemId.Grill), D(Dish.PanFish,PreparedForm.Fillet,ItemId.Stove),
            D(Dish.FishAndChips,PreparedForm.Fillet,ItemId.Fryer), D(Dish.Soup,PreparedForm.Stock,ItemId.SoupKettle),
            D(Dish.Platter,PreparedForm.Platter,ItemId.Oven), D(Dish.Crab,PreparedForm.Crab,ItemId.Steamer),
            D(Dish.Calamari,PreparedForm.Squid,ItemId.Fryer), D(Dish.Coffee,PreparedForm.Stock,ItemId.CoffeeMachine,true),
            D(Dish.Tea,PreparedForm.Stock,ItemId.CoffeeMachine,true), D(Dish.Lemonade,PreparedForm.Stock,ItemId.DrinksFridge,true),
            D(Dish.Beer,PreparedForm.Stock,ItemId.DrinksFridge,true), D(Dish.Fries,PreparedForm.Stock,ItemId.Fryer,true),
            D(Dish.Bread,PreparedForm.Stock,ItemId.PrepCounter,true), D(Dish.IceCream,PreparedForm.Stock,ItemId.PrepCounter,true) };
        static DishDef D(Dish d, PreparedForm f, ItemId a, bool staple=false) => new DishDef { Id=d,Form=f,Appliance=a,Staple=staple };
        public static ItemDef Get(ItemId id) => Items[(int)id];
        public static DishDef Get(Dish d) => Dishes[(int)d];
        public static StageDef Stage(int stage) => Stages[Math.Max(1,Math.Min(4,stage))-1];
        public static Job NativeJob(CardRole role) => role == CardRole.Fisher ? Job.Cook : role == CardRole.Deckhand ? Job.Waiter : role == CardRole.Engineer ? Job.Handyman : Job.Barista;
        public static float PortionPrice(Species species, Dish dish)
        {
            if(Get(dish).Staple) return RestaurantTuning.StaplePrice(dish);
            float kg = dish == Dish.GrilledFish ? (GameData.Get(species).MinKg+Math.Min(.8f,GameData.Get(species).MaxKg))*.5f :
                dish == Dish.Soup ? 1/RestaurantTuning.StockBowlsPerKg : dish == Dish.Crab ? 1 : dish == Dish.Calamari ? RestaurantTuning.SquidKg : dish == Dish.Platter ? RestaurantTuning.PlatterMinKg : RestaurantTuning.FilletKg;
            return GameData.Get(species).PricePerKg * kg * RestaurantTuning.DishMultiplier;
        }
    }
}
