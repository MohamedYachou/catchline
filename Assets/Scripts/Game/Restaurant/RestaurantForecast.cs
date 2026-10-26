using System;
using System.Collections.Generic;
using System.Linq;

namespace Catchline.Game.Restaurant
{
    [Serializable] public sealed class GuestOrder
    {
        public int Id, Group; public Species Species; public Dish Dish; public bool Drink, Coffee, Special, Accepted;
        public Dish DrinkDish = Dish.Coffee;
        public GuestOrder Copy() => (GuestOrder)MemberwiseClone();
    }
    public readonly struct ForecastRange
    {
        public readonly int Min, Max;
        public ForecastRange(int min,int max){Min=min;Max=max;}
        public bool Contains(int value)=>value>=Min&&value<=Max;
        public override string ToString()=>Min+"-"+Max;
    }
    public sealed class RestaurantForecast
    {
        readonly Random random; readonly RestaurantLayout kitchen;
        readonly (Species species,float weight)[] pool;
        readonly List<GuestOrder> guests=new List<GuestOrder>();
        int nextId, nextGroup, calls, added;
        public readonly int Seed, BaseCount;
        public readonly Weather Weather;
        public bool Locked {get;private set;}
        public int Calls=>calls;
        public int WalkIns {get;private set;}
        // Copies prevent a UI from mutating a locked departure plan accidentally.
        public IReadOnlyList<GuestOrder> Guests=>guests.Select(g=>g.Copy()).ToArray();
        public ForecastRange GuestRange => Range(guests.Count);
        public Dictionary<(Species,Dish),ForecastRange> DishRanges => guests.GroupBy(g=>(g.Species,g.Dish)).ToDictionary(g=>g.Key,g=>Range(g.Count()));
        public RestaurantForecast(int seed,int popularity,DayOfWeek weekday,Weather weather,
            IEnumerable<(Species species,float weight)> groundPool,RestaurantLayout layout)
        {
            Seed=seed;random=new Random(seed);kitchen=layout;Weather=weather;
            pool=groundPool.Where(p=>p.weight>0 && !float.IsNaN(p.weight) && !float.IsInfinity(p.weight) && Options(p.species).Count>0).ToArray();
            if(pool.Length==0)throw new ArgumentException("This kitchen cannot cook anything from this ground");
            float day=weekday==DayOfWeek.Monday?RestaurantTuning.Monday:weekday==DayOfWeek.Friday||weekday==DayOfWeek.Saturday?RestaurantTuning.BusyDay:1;
            float sky=weather==Weather.Rain?RestaurantTuning.Rain:weather==Weather.Sun&&layout.Stage.TerraceWidth>0?1+RestaurantTuning.WalkInMax:1;
            BaseCount=Math.Max(1,(int)Math.Round((RestaurantTuning.BaseGuests+Math.Max(0,popularity)*RestaurantTuning.GuestsPerPopularity)*day*sky*(.9+random.NextDouble()*.2)));
            AddGuests(BaseCount,weekday==DayOfWeek.Sunday);
        }
        ForecastRange Range(int n){int slack=Math.Max(1,(int)Math.Ceiling(n*RestaurantTuning.ForecastUncertainty));return new ForecastRange(Math.Max(0,n-slack),n+slack);}
        List<Dish> Options(Species s)
        {
            var f=GameData.Get(s);var ds=new List<Dish>();
            if(s==Species.Crab){if(kitchen.CanCook(Dish.Crab))ds.Add(Dish.Crab);}
            else if(s==Species.GiantSquid){if(kitchen.CanCook(Dish.Calamari))ds.Add(Dish.Calamari);}
            else {
                if(f.MinKg<=RestaurantTuning.WholeMaxKg&&kitchen.CanCook(Dish.GrilledFish))ds.Add(Dish.GrilledFish);
                if(f.MaxKg>RestaurantTuning.WholeMaxKg){if(kitchen.CanCook(Dish.PanFish))ds.Add(Dish.PanFish);if(kitchen.CanCook(Dish.FishAndChips))ds.Add(Dish.FishAndChips);}
                if(f.MaxKg>=RestaurantTuning.PlatterMinKg&&kitchen.CanCook(Dish.Platter))ds.Add(Dish.Platter);
            }
            if(kitchen.CanCook(Dish.Soup))ds.Add(Dish.Soup);return ds;
        }
        Species RollSpecies()
        {
            double roll=random.NextDouble()*pool.Sum(p=>(double)p.weight);
            foreach(var p in pool){roll-=p.weight;if(roll<=0)return p.species;}return pool[pool.Length-1].species;
        }
        void AddGuests(int count,bool families=false)
        {
            int seats=Math.Max(1,kitchen.Active.Max(i=>RestaurantData.Get(i.Id).Seats));
            while(count>0){int group=++nextGroup;int n=Math.Min(count,families?Math.Min(4,seats):random.Next(1,Math.Min(4,seats)+1));
                // One oven platter is shared by a whole table; grouping it here avoids multiple platter orders.
                Species species=RollSpecies();var options=Options(species);Dish common=options[random.Next(options.Count)];
                for(int i=0;i<n;i++){
                    Species s=common==Dish.Platter?species:RollSpecies();var ds=Options(s).Where(x=>x!=Dish.Platter).ToList();
                    // A separately rolled species may support only a table platter. Keep individual orders cookable.
                    if(common!=Dish.Platter&&ds.Count==0){s=species;ds=Options(s).Where(x=>x!=Dish.Platter).ToList();}
                    Dish d=common==Dish.Platter?common:ds[random.Next(ds.Count)];
                    bool special=d!=Dish.Soup && GameData.Get(s).MaxKg>=RestaurantTuning.PlatterMinKg && random.NextDouble()<RestaurantTuning.SpecialChance;
                    var drinks=new List<Dish>();if(kitchen.Has(ItemId.CoffeeMachine)){drinks.Add(Dish.Coffee);drinks.Add(Dish.Tea);}if(kitchen.Has(ItemId.DrinksFridge)){drinks.Add(Dish.Lemonade);drinks.Add(Dish.Beer);}
                    guests.Add(new GuestOrder{Id=++nextId,Group=group,Species=s,Dish=d,Special=special,
                        Drink=drinks.Count>0&&random.NextDouble()<RestaurantTuning.DrinkChance,DrinkDish=drinks.Count==0?Dish.Coffee:drinks[random.Next(drinks.Count)],
                        Coffee=kitchen.Has(ItemId.CoffeeMachine)&&random.NextDouble()<RestaurantTuning.CoffeeChance});
                }count-=n;
            }
        }
        public bool MiraChange(int delta)
        {
            if(Locked||calls>=2)return false;
            if(delta>0 && added+delta>(int)Math.Floor(BaseCount*RestaurantTuning.MiraGrowthMax))return false;
            if(delta<0 && guests.Count+delta<1)return false;
            calls++;
            if(delta>0){added+=delta;AddGuests(delta);}else if(delta<0)guests.RemoveRange(guests.Count+delta,-delta);
            return true;
        }
        public bool SpecialRequest(int guestId,bool accept)
        {
            if(Locked)return false;var g=guests.FirstOrDefault(x=>x.Id==guestId&&x.Special);if(g==null)return false;g.Accepted=accept;return true;
        }
        public void Lock()
        {
            if(Locked)return;WalkIns=random.Next(0,(int)Math.Floor(guests.Count*RestaurantTuning.WalkInMax)+1);AddGuests(WalkIns);Locked=true;
        }
    }
}
