using System;
using System.Collections.Generic;
using System.Linq;

namespace Catchline.Game.Restaurant
{
    [Serializable] public sealed class PortionStock
    {
        public Species Species; public PreparedForm Form; public int Count; public bool CaptainCut, Special;
        public PortionStock Copy()=>(PortionStock)MemberwiseClone();
    }
    [Serializable] public sealed class RestaurantCatch
    {
        public Species Species; public float Kg; public bool CaptainCut, Special;
    }
    public sealed class PrepPlan
    {
        public readonly List<PortionStock> Stock=new List<PortionStock>();
        public readonly List<RestaurantCatch> Market=new List<RestaurantCatch>();
        public readonly Dictionary<PreparedForm,string> Unavailable=new Dictionary<PreparedForm,string>();
        public int Capacity, MarketCoins;
        public int Portions=>Stock.Sum(s=>s.Count);
    }
    public static class RestaurantPortions
    {
        public static int Yield(Species species,float kg,PreparedForm form,bool cleanCut=false)
        {
            if(!(kg>0)||float.IsInfinity(kg))return 0;
            if(form==PreparedForm.Stock)return (int)Math.Floor(kg*RestaurantTuning.StockBowlsPerKg+.00001f);
            if(species==Species.Crab)return form==PreparedForm.Crab?1:0;
            if(species==Species.GiantSquid)return form==PreparedForm.Squid?(int)Math.Floor(kg/RestaurantTuning.SquidKg+.00001f):0;
            switch(form){
                case PreparedForm.Whole:return kg<=RestaurantTuning.WholeMaxKg && species!=Species.Herring?1:0;
                case PreparedForm.Fillet:return kg>RestaurantTuning.WholeMaxKg?(int)Math.Floor(kg/RestaurantTuning.FilletKg+.00001f)+(cleanCut?1:0):0;
                case PreparedForm.Platter:return kg>=RestaurantTuning.PlatterMinKg?1:0;
                default:return 0;
            }
        }
        public static int HerringPortions(int fish)=>Math.Max(0,fish)/2;
        public static float OffcutsKg(float filletedKg)=>Math.Max(0,filletedKg)*RestaurantTuning.OffcutFraction;
        public static bool CanPrepare(RestaurantLayout kitchen,PreparedForm form) => RestaurantData.Dishes.Any(d=>!d.Staple&&d.Form==form&&kitchen.CanCook(d.Id));
        public static PrepPlan Suggest(IEnumerable<RestaurantCatch> catchList,RestaurantForecast forecast,RestaurantLayout layout,PrepMargin margin=PrepMargin.TenPercent)
        {
            var plan=new PrepPlan{Capacity=layout.FridgeCapacity};
            foreach(PreparedForm form in Enum.GetValues(typeof(PreparedForm)))if(!CanPrepare(layout,form)){
                var d=RestaurantData.Dishes.First(x=>!x.Staple&&x.Form==form);plan.Unavailable[form]="Needs a "+RestaurantData.Get(d.Appliance).Name.ToLowerInvariant();}
            float mult=margin==PrepMargin.TwentyPercent?1.2f:margin==PrepMargin.TenPercent?1.1f:1;
            var need=new Dictionary<(Species,PreparedForm),int>();
            foreach(var g in forecast.Guests.Where(g=>g.Dish!=Dish.Platter).GroupBy(g=>(g.Species,RestaurantData.Get(g.Dish).Form)))need[g.Key]=(int)Math.Ceiling(g.Count()*mult);
            foreach(var group in forecast.Guests.Where(g=>g.Dish==Dish.Platter).GroupBy(g=>g.Group)){
                var key=(group.First().Species,PreparedForm.Platter);need[key]=need.TryGetValue(key,out int n)?n+1:1;}
            // One indivisible fish per step. If its entire yield cannot fit, it stays whole for the market.
            var remaining=catchList.ToList();float offcuts=0;
            foreach(var fish in remaining.ToArray()){
                var candidates=new[]{PreparedForm.Platter,PreparedForm.Whole,PreparedForm.Fillet,PreparedForm.Crab,PreparedForm.Squid};
                foreach(var form in candidates){var key=(fish.Species,form);if(!need.TryGetValue(key,out int want)||want<=0||!CanPrepare(layout,form))continue;
                    int yield=Yield(fish.Species,fish.Kg,form,fish.CaptainCut);if(yield<=0||plan.Portions+yield>plan.Capacity)continue;
                    Add(plan.Stock,fish.Species,form,yield,fish.CaptainCut,fish.Special||fish.Kg>=RestaurantTuning.PlatterMinKg);need[key]=Math.Max(0,want-yield);remaining.Remove(fish);
                    if(form==PreparedForm.Fillet)offcuts+=OffcutsKg(fish.Kg);break;
                }
            }
            var h=remaining.Where(f=>f.Species==Species.Herring&&f.Kg<=RestaurantTuning.WholeMaxKg).ToList();
            int hNeed=need.TryGetValue((Species.Herring,PreparedForm.Whole),out int hn)?hn:0;
            if(CanPrepare(layout,PreparedForm.Whole))for(int i=0;i+1<h.Count&&hNeed>0&&plan.Portions<plan.Capacity;i+=2){Add(plan.Stock,Species.Herring,PreparedForm.Whole,1);remaining.Remove(h[i]);remaining.Remove(h[i+1]);hNeed--;}
            int soupNeed=need.Where(p=>p.Key.Item2==PreparedForm.Stock).Sum(p=>p.Value);
            if(CanPrepare(layout,PreparedForm.Stock)){
                int bowls=Math.Min(Math.Min(soupNeed,Yield(Species.Herring,offcuts,PreparedForm.Stock)),plan.Capacity-plan.Portions);
                if(bowls>0){Add(plan.Stock,Species.Herring,PreparedForm.Stock,bowls);soupNeed-=bowls;}
                foreach(var fish in remaining.ToArray()){
                    if(soupNeed<=0)break;int n=Yield(fish.Species,fish.Kg,PreparedForm.Stock);
                    if(n<=0||plan.Portions+n>plan.Capacity)continue;
                    Add(plan.Stock,fish.Species,PreparedForm.Stock,n);remaining.Remove(fish);soupNeed-=n;
                }
            }
            plan.Market.AddRange(remaining);
            plan.MarketCoins=(int)Math.Round(plan.Market.Sum(f=>GameData.Get(f.Species).PricePerKg*f.Kg*RestaurantTuning.MarketMultiplier));
            return plan;
        }
        public static void Add(List<PortionStock> stock,Species species,PreparedForm form,int count,bool cut=false,bool special=false)
        {
            if(count<=0)return;var s=stock.FirstOrDefault(x=>x.Species==species&&x.Form==form&&x.CaptainCut==cut&&x.Special==special);
            if(s==null)stock.Add(new PortionStock{Species=species,Form=form,Count=count,CaptainCut=cut,Special=special});else s.Count+=count;
        }
        // Transfers leftovers exactly once; calling again returns zero.
        public static int FeedCats(List<PortionStock> stock){int cats=stock.Sum(s=>s.Count);stock.Clear();return cats;}
    }
}
