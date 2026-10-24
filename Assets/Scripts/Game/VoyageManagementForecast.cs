using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace Catchline.Game
{
    public sealed class MethodForecast
    {
        public string Name, Availability;
        public int InstalledCount, Operators;
        public float FishPerMinute, KgPerMinute, ValuePerMinute, CostPerMinute, CycleFish, CycleValue, CycleSeconds, OperatorSecondsPerMinute, SupplyCostPerMinute;
        public readonly Dictionary<Species,float> SpeciesCounts=new();
        public readonly Dictionary<CatchTier,float> ClassOdds=new();
        public float Margin=>ValuePerMinute>0?(ValuePerMinute-CostPerMinute)/ValuePerMinute:0;
    }
    public partial class VoyageGame
    {
        public MethodForecast[] Forecast {get;private set;}=Array.Empty<MethodForecast>();
        string forecastSignature;
        public float ForecastIncome=>Forecast.Sum(f=>f.ValuePerMinute);
        public float[] DashboardCosts {get;private set;}=new float[4];
        public float ForecastCost=>DashboardCosts.Sum();
        public float ForecastVoyageMinutes {get;private set;}
        public int FittedTrapCount=>IsTier5?Enumerable.Range(0,Mathf.Min(buoyTiles.Length,buoyModels.Length)).Count(i=>buoyModels[i]!=null&&buoyModels[i].gameObject.activeInHierarchy):0;
        public int FittedNetCount=>State.Hull>0&&netFloats!=null?1+(SecondNetActive&&secondNetFloats!=null?1:0):0;
        public int FittedRodCount=>Rods.Count(r=>r.Unlocked&&r.Root!=null&&r.Root.gameObject.activeInHierarchy);
        public int[] ForecastShares=>CatchExpectation.Shares(Forecast.Select(f=>f.ValuePerMinute).ToArray());
        static float NominalValue(Species species,float kg)=>CatchExpectation.NominalValue(species,kg);
        float ForecastWalk(Vector2Int from,Vector2Int to,float speed)
        {
            var path=Grid.FindPath(from,to);if(path==null)return float.PositiveInfinity;
            float distance=0;var prev=from;foreach(var tile in path){distance+=Vector3.Distance(Grid.GetLocal(prev),Grid.GetLocal(tile));prev=tile;}
            return distance/Mathf.Max(.01f,GameData.WalkSpeed*speed);
        }
        int ForecastCaptainNet=>Captain==netWorker?0:Captain==secondNetWorker?1:netUnloader==Captain?NetUnloadRig:-1;
        bool ForecastCaptainTrap=>buoyWorkers.Contains(Captain);
        bool ForecastRodWorking(Rod rod)=>true;
        public void UpdateManagementForecast()
        {
            var people=People.ToArray();
            string signature=$"{State.Hull}/{ActiveSpot}/{HoldFull}/{FittedRodCount}/{FittedNetCount}/{FittedTrapCount}/{FittedDeepLineCount}/{State.SelectedNet}/{State.ActiveNetStock}/{State.ReelSpeed}/{State.NetCapacityKg}/{State.Richness[ActiveSpot]}/{ForecastCaptainNet}/{ForecastCaptainTrap}/{CaptainHaulingIn}/{CaptainHaulingOut}/{State.SelectBait(null)}/{State.PrepOrders.ChumTarget}/{State.PrepOrders.ChumFirst}/{State.PrepOrders.ChumClasses}/{State.Chum}/"+
                string.Join(",",people.Where(p=>p.Contract!=null).Select(p=>$"{p.Name}:{p.Contract.Role}:{p.Contract.WorkPreference}:{p.Contract.FishingTasks}:{p.Speed}:{State.SelectBait(p.Contract)}"));
            if(signature==forecastSignature&&Forecast.Length==4){UpdateForecastCosts();return;}forecastSignature=signature;
            var rods=new MethodForecast{Name="Rods",InstalledCount=FittedRodCount,Availability=FittedRodCount>0?"No rod operator":"No rods fitted",CycleFish=FittedRodCount>0?100:0};
            var nets=new MethodForecast{Name="Nets",InstalledCount=FittedNetCount,Availability=FittedNetCount>0?State.ActiveNetStock>0?"Enable Nets for a fisher":"No net stock":"No nets fitted"};
            var crabs=new MethodForecast{Name="Crab cages",InstalledCount=FittedTrapCount,Availability=FittedTrapCount>0?"No recovery operator":"No cages fitted",CycleFish=FittedTrapCount>0?1:0};
            var deep=new MethodForecast{Name="Deep lines",InstalledCount=FittedDeepLineCount,Availability=DeepLinesActive?"Enable Deep lines":"Not fitted in this layout"};
            Forecast=new[]{rods,nets,crabs,deep};
            var fishers=people.Where(p=>p.Contract?.Role==CrewRole.Fisherman).ToArray();
            var budget=people.ToDictionary(p=>p,p=>60f);
            bool Permits(Person p,FisherTask task)=>!IsTier5||p.Contract.Allows(task);
            bool HasCarrier=people.Any(p=>p.Contract?.Role==CrewRole.Deckhand)||CaptainHaulingIn;
            float Take(Person p,float rate,float work) { float actual=Mathf.Min(rate,budget[p]/Mathf.Max(.001f,work));budget[p]=Mathf.Max(0,budget[p]-actual*work);return actual; }
            float BaitCost(BaitPermission b)=>b==BaitPermission.Squid?GameData.SquidPackCost/(float)GameData.SquidPackSize:b==BaitPermission.Worms?GameData.BaitPackCost/(float)GameData.BaitPackSize:0;
            void AddMix(MethodForecast f,CatchExpectation.RodMix mix,float rate)
            {
                f.FishPerMinute+=rate;f.KgPerMinute+=rate*mix.Kg;f.ValuePerMinute+=rate*mix.Value;
                foreach(var e in mix.Probabilities){if(!f.SpeciesCounts.ContainsKey(e.Key))f.SpeciesCounts[e.Key]=0;f.SpeciesCounts[e.Key]+=e.Value*rate;}
            }
            var netOps=new Dictionary<int,Person>();
            foreach(var p in people.Where(p=>NetOperator(p.Contract)&&(IsTier5||p.Contract.WorkPreference==DeckhandWork.Nets)))
            {
                int rig=netAssignments.TryGetValue(p.Contract,out int known)&&known<nets.InstalledCount&&!netOps.ContainsKey(known)?known:Enumerable.Range(0,nets.InstalledCount).Where(i=>!netOps.ContainsKey(i)).DefaultIfEmpty(-1).First();
                if(rig>=0)netOps[rig]=p;
            }
            if(ForecastCaptainNet>=0&&!netOps.ContainsKey(ForecastCaptainNet))netOps[ForecastCaptainNet]=Captain;
            if(nets.InstalledCount>0&&State.ActiveNetStock>0)
            {
                var rng=new System.Random(87087);float kg=0,value=0,fish=0;
                for(int sample=0;sample<256;sample++)foreach(var f in CatchExpectation.RollNet(State.Hull,ActiveSpot,DeepNetSelected,NetWeightRange(ActiveSpot,DeepNetSelected).y,rng,State.FishTable(ActiveSpot)))
                {kg+=f.kg/256;value+=NominalValue(f.species,f.kg)/256f;fish+=1f/256;if(!nets.SpeciesCounts.ContainsKey(f.species))nets.SpeciesCounts[f.species]=0;nets.SpeciesCounts[f.species]+=1f/256;}
                nets.CycleFish=fish;nets.CycleValue=value;
                foreach(var op in netOps.OrderBy(v=>v.Key).Take(State.ActiveNetStock))
                {
                    var p=op.Value;var tile=op.Key==0?NetAccess:SecondNetAccess;
                    float work=WorkSpeed.Duration(GameData.NetSetTime+GameData.NetHaulTime,p)+2*ForecastWalk(p.Tile,tile,p.Speed);
                    float handling=WorkSpeed.Duration(GameData.NetGatherTime+GameData.StowTime,p)+2*ForecastWalk(tile,InboundAccess,p.Speed);
                    float chance=IsTier5||p==Captain?1:.8f;
                    float cycle=(DeepNetSelected?GameData.DeepNetSoakSeconds:GameData.ShallowNetSoakSeconds)+work+chance*handling;
                    if(float.IsInfinity(cycle))continue;
                    float attempts=Take(p,60/cycle,work+(!IsTier5?chance*handling:0));
                    if(IsTier5&&p!=Captain&&!HasCarrier)attempts=0;
                    float rate=attempts*chance;nets.Operators++;nets.FishPerMinute+=fish*rate;nets.KgPerMinute+=kg*rate;nets.ValuePerMinute+=value*rate;nets.OperatorSecondsPerMinute+=attempts*(work+(!IsTier5?chance*handling:0));
                    nets.CostPerMinute+=attempts*(DeepNetSelected?GameData.DeepNetCost/(float)GameData.DeepNetUses:(1-chance)*GameData.NetReplacementCost);
                }
                nets.CycleSeconds=nets.FishPerMinute>0?fish*60*nets.Operators/nets.FishPerMinute:0;
                if(nets.Operators>0)nets.Availability=nets.FishPerMinute>0?"Estimated · collection included":"Needs catch collection";
            }
            var crabOps=fishers.Where(p=>Permits(p,FisherTask.Crabs)).ToList();if(ForecastCaptainTrap)crabOps.Add(Captain);
            if(crabs.InstalledCount>0)
            {
                crabs.SpeciesCounts[Species.Crab]=1;
                crabs.CycleValue=Enumerable.Range(0,512).Average(n=>(float)NominalValue(Species.Crab,Mathf.Lerp(.5f,1.8f,(n+.5f)/512)));
                for(int rig=0;rig<FittedTrapCount;rig++)
                {
                    var p=crabOps.OrderByDescending(p=>budget[p]).FirstOrDefault();if(p==null)break;
                    float work=WorkSpeed.Duration(2f,p)+2*ForecastWalk(p.Tile,buoyTiles[rig],p.Speed);if(float.IsInfinity(work))continue;
                    float rate=Take(p,60/(BuoySoakSeconds+work),work);crabs.FishPerMinute+=rate;crabs.OperatorSecondsPerMinute+=rate*work;
                }
                crabs.Operators=crabOps.Count;crabs.KgPerMinute=crabs.FishPerMinute*1.15f;crabs.ValuePerMinute=crabs.FishPerMinute*crabs.CycleValue;
                crabs.CycleSeconds=crabs.FishPerMinute>0?60*FittedTrapCount/crabs.FishPerMinute:0;
                if(crabs.Operators>0)crabs.Availability="Estimated recovery value";
            }
            var deepOps=fishers.Where(p=>Permits(p,FisherTask.DeepLines)&&State.SelectDeepLineBait(p.Contract)!=BaitPermission.None).ToArray();
            if(DeepLinesActive)
            {
                deep.Operators=deepOps.Length;
                for(int rig=0;rig<FittedDeepLineCount;rig++)
                {
                    var p=deepOps.OrderByDescending(p=>budget[p]).FirstOrDefault();if(p==null)break;
                    var bait=State.SelectDeepLineBait(p.Contract);var mix=DeepLineRules.Expectation(State,ActiveSpot,bait);
                    float work=WorkSpeed.Duration(DeepLineRules.BaitSeconds,p)+2*ForecastWalk(p.Tile,deepLineTiles[rig],p.Speed);
                    float collection=people.Where(h=>h.Contract?.Role==CrewRole.Deckhand).Select(h=>2*ForecastWalk(deepLineTiles[rig],InboundAccess,h.Speed)+WorkSpeed.Duration(GameData.PickupTime+GameData.StowTime,h)).DefaultIfEmpty(0).Min();
                    float count=DeepLineRules.CatchCount(rig),cycle=work+DeepLineRules.DropSeconds+DeepLineRules.SoakSeconds+DeepLineRules.RaiseSeconds+count*collection;
                    if(float.IsInfinity(cycle))continue;
                    float attempts=HasCarrier?Take(p,60/cycle,work):0;AddMix(deep,mix,count*attempts);
                    foreach(var option in DeepLineRules.Options(State,ActiveSpot,bait))
                    {if(!deep.ClassOdds.ContainsKey(option.Tier))deep.ClassOdds[option.Tier]=0;deep.ClassOdds[option.Tier]+=option.Probability*count*attempts;}
                    deep.OperatorSecondsPerMinute+=attempts*work;deep.CostPerMinute+=attempts*BaitCost(bait);
                }
                deep.CycleFish=FittedDeepLineCount;deep.CycleValue=deep.FishPerMinute>0?FittedDeepLineCount*deep.ValuePerMinute/deep.FishPerMinute:0;
                deep.CycleSeconds=deep.FishPerMinute>0?60*FittedDeepLineCount/deep.FishPerMinute:0;
                deep.Availability=!HasCarrier?"Needs catch collection":deepOps.Length==0?"Needs self-made chum / operator":FittedDeepLineCount+" rods · 1 fish each";
            }
            var seats=Rods.Where(r=>r.Unlocked&&r.Root!=null&&r.Root.gameObject.activeInHierarchy).ToList();var used=new HashSet<Rod>();
            var assignments=new List<(Person person,Rod rod)>();
            foreach(var p in fishers.Where(p=>Permits(p,FisherTask.Rods)))
            {var r=seats.FirstOrDefault(r=>r.Fisher==p&&!used.Contains(r))??seats.LastOrDefault(r=>!used.Contains(r)&&r!=Manning);if(r!=null){used.Add(r);assignments.Add((p,r));}}
            if(ForecastCaptainNet<0&&!ForecastCaptainTrap&&!CaptainHaulingIn&&!CaptainHaulingOut)
            {var r=Manning!=null&&!used.Contains(Manning)?Manning:seats.FirstOrDefault(r=>!used.Contains(r));if(r!=null)assignments.Add((Captain,r));}
            foreach(var a in assignments)
            {
                var p=a.person;var bait=State.SelectBait(p.Contract);if(bait==BaitPermission.None)continue;
                var mix=CatchExpectation.Rod(State,ActiveSpot,.55f,bait);float chance=p==Captain||IsTier5?1:CardStrikeChance(p.Contract);
                float cycle=WorkSpeed.Duration(GameData.BaitTime+GameData.CastTime,p)+GameData.FlightTime+CatchExpectation.BiteWait(State,ActiveSpot,.55f,LearningFishing)+chance*mix.ReelSeconds/(p.Speed*State.ReelSpeed)+(1-chance)*StrikeWindow;
                if(p==Captain&&!HasCarrier)cycle+=2*ForecastWalk(a.rod.Tile,InboundAccess,p.Speed)+WorkSpeed.Duration(GameData.PickupTime+GameData.StowTime,p);
                if(float.IsInfinity(cycle))continue;float attempts=Take(p,60/cycle,cycle);AddMix(rods,mix,attempts*chance);rods.Operators++;rods.OperatorSecondsPerMinute+=attempts*cycle;rods.CostPerMinute+=attempts*BaitCost(bait);
            }
            foreach(var f in new[]{rods,deep})foreach(var key in f.SpeciesCounts.Keys.ToArray())f.SpeciesCounts[key]/=Mathf.Max(.00001f,f.FishPerMinute);
            foreach(var tier in deep.ClassOdds.Keys.ToArray())deep.ClassOdds[tier]/=Mathf.Max(.00001f,deep.FishPerMinute);
            rods.CycleValue=rods.FishPerMinute>0?100*rods.ValuePerMinute/rods.FishPerMinute:0;rods.CycleSeconds=rods.FishPerMinute>0?6000/rods.FishPerMinute:0;
            if(rods.Operators>0)rods.Availability="Expected raw catch value";
            if(HoldFull)foreach(var f in Forecast){f.FishPerMinute=f.KgPerMinute=f.ValuePerMinute=f.CostPerMinute=f.OperatorSecondsPerMinute=0;f.Availability="Hold full · return to sell";}
            foreach(var f in Forecast)f.SupplyCostPerMinute=f.CostPerMinute;
            UpdateForecastCosts();
        }
        void UpdateForecastCosts()
        {
            float kgRate=Forecast.Sum(f=>f.KgPerMinute),fishRate=Forecast.Sum(f=>f.FishPerMinute);
            float storageRate=kgRate;
            if(IsPrepFisher)
            {
                float prepRate=TableFishCapacity*(1-EstimatedChumShare);
                storageRate=Mathf.Min(kgRate*(1-EstimatedChumShare),prepRate*(fishRate>0?kgRate/fishRate:0));
            }
            float fill=storageRate>0?Mathf.Max(0,State.CoolerCapacity-HoldKg)/storageRate:float.PositiveInfinity;
            float remaining=State.Hull>0?Mathf.Min(fill,Mathf.Max(0,State.Fuel-.1f*State.FuelCapacity)):float.IsInfinity(fill)?0:fill;
            float travel=2*GameData.Spots[ActiveSpot].RowSeconds*State.HullDef.TravelMultiplier/(State.Hull>0?1:WorkSpeed.Rate(Captain))/60;
            ForecastVoyageMinutes=Mathf.Max(1,(float)Flow.Clock/60+remaining+travel);
            foreach(var f in Forecast)f.CostPerMinute=f.SupplyCostPerMinute;
            DashboardCosts=new float[4];DashboardCosts[0]=Forecast.Sum(f=>f.SupplyCostPerMinute)+(State.Hull>0?1:0);
            foreach(var crew in State.Crew)
            {
                float fee=crew.Fee/(float)GameData.ContractVoyages(crew.Grade)/ForecastVoyageMinutes;
                if(crew.Role==CrewRole.Deckhand){if(crew.WorkPreference==DeckhandWork.Prep)DashboardCosts[2]+=fee;else{DashboardCosts[1]+=fee*.5f;DashboardCosts[3]+=fee*.5f;}}
                else DashboardCosts[0]+=fee;
            }
            float indirect=Mathf.Max(0,ForecastCost-Forecast.Sum(f=>f.SupplyCostPerMinute));
            foreach(var f in Forecast)f.CostPerMinute+=indirect*f.ValuePerMinute/Mathf.Max(.00001f,ForecastIncome);
        }
    }
}
