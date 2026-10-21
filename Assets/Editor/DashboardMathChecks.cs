using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Reflection;
using Catchline.Game;
using UnityEngine;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEditor.Build.Reporting;
namespace Catchline.EditorTools
{
    public static class DashboardMathChecks
    {
        const BindingFlags H=BindingFlags.Instance|BindingFlags.NonPublic;
        static void Check(bool ok,string why){if(!ok)throw new Exception("DASH087: "+why);}
        static object Call(VoyageGame g,string method,params object[] args)=>typeof(VoyageGame).GetMethod(method,H).Invoke(g,args);
        static void ProbabilityChecks()
        {
            var report=new List<string>{"hull,spot,bait,expected_value,observed_value,value_standard_error,expected_kg,observed_kg"};
            int cases=0;
            foreach(int hull in new[]{0,2,3,4})for(int spot=0;spot<GameData.Spots.Length;spot++)foreach(var bait in new[]{BaitPermission.Scraps,BaitPermission.Worms,BaitPermission.Squid,BaitPermission.Chum})
            {
                var state=new GameState(8700+cases){Hull=hull};var expected=CatchExpectation.Rod(state,spot,.55f,bait);
                double value=0,value2=0,kg=0,kg2=0;const int n=20000;var counts=new Dictionary<Species,int>();
                for(int sample=0;sample<n;sample++)
                {
                    var roll=state.RollFish(spot,.55f+(bait==BaitPermission.Squid?GameData.SquidPowerBonus:0),bait==BaitPermission.Scraps,bait==BaitPermission.Squid,bait==BaitPermission.Chum);
                    var actual=new CaughtFish{Species=roll.Item1,Kg=roll.Item2,StowedAt=0};int worth=state.ValueOf(actual,0);
                    value+=worth;value2+=worth*worth;kg+=roll.Item2;kg2+=roll.Item2*roll.Item2;
                    if(!counts.ContainsKey(roll.Item1))counts[roll.Item1]=0;counts[roll.Item1]++;
                }
                double mean=value/n,se=Math.Sqrt(Math.Max(0,value2/n-mean*mean)/n),meanKg=kg/n,kgse=Math.Sqrt(Math.Max(0,kg2/n-meanKg*meanKg)/n);
                Check(Math.Abs(mean-expected.Value)<=Math.Max(.04,6*se+expected.Value*.002),$"nominal rod value matches actual rolls {hull}/{spot}/{bait}");
                Check(Math.Abs(meanKg-expected.Kg)<=Math.Max(.002,6*kgse),"expected rod mass matches actual rolls");
                Check(Math.Abs(expected.Probabilities.Values.Sum()-1)<.0001,"species probability normalization");
                foreach(var e in expected.Probabilities){double p=e.Value;int observed=counts.TryGetValue(e.Key,out int c)?c:0;Check(Math.Abs(observed-n*p)<=6*Math.Sqrt(n*p*(1-p))+2,"species odds match actual game");}
                report.Add($"{hull},{spot},{bait},{expected.Value},{mean},{se},{expected.Kg},{meanKg}");cases++;
            }
            File.WriteAllLines("Logs/dash087/rod-statistics.csv",report);
            var waitState=new GameState(871);foreach(float richness in new[]{1f,.8f,.3f})foreach(int spot in new[]{0,GameData.Spots.Length-1})
            {
                waitState.Richness[spot]=richness;double sum=0;for(int i=0;i<30000;i++)sum+=waitState.RollBiteWait(spot,.55f);
                Check(Math.Abs(sum/30000-CatchExpectation.BiteWait(waitState,spot,.55f))<.05,"mean of capped wait distribution, not cap of its mean");
            }
            Debug.Log("[Catchline] DASH087 independent rod distributions: "+cases+" x20000 real rolls passed");
        }
        static void NetChecks()
        {
            int cases=0;
            foreach(int hull in new[]{1,2,3,4})for(int spot=0;spot<GameData.Spots.Length;spot++)foreach(bool deep in new[]{false,true})foreach(int seed in new[]{0,19,87087})
            {
                float target=hull>=3?30:20;var a=new System.Random(seed);var b=new System.Random(seed);
                var legacy=LegacyNet(hull,spot,deep,target,a);var current=CatchExpectation.RollNet(hull,spot,deep,target,b);
                Check(legacy.SequenceEqual(current)&&a.Next()==b.Next(),"exact pre-extraction net catch and RNG sequence");
                Check(current.Sum(f=>f.kg)<=target+.00001f&&current.All(f=>f.kg>0),"net hard mass bound");cases++;
            }
            Debug.Log("[Catchline] DASH087 "+cases+" seeded legacy net oracle comparisons passed");
        }
        static Rect Bounds(VoyageGame g,string id)
        {
            var t=g.GetComponentsInChildren<RectTransform>(true).FirstOrDefault(t=>t.name==id&&t.gameObject.activeInHierarchy);
            Check(t!=null,"rendered control "+id);return new Rect(t.anchoredPosition.x,-t.anchoredPosition.y,t.sizeDelta.x,t.sizeDelta.y);
        }
        static void AvailabilityAndLayout()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("DASH087 real gear / footer check").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();
            var rows=new List<string>{"hull,traps,rods_value,nets_value,crabs_value,share_rods,share_nets,share_crabs"};
            foreach(int hull in new[]{4,3,2,1,0})
            {
                g.NewGame();g.State.Hull=hull;g.State.Fuel=g.State.FuelCapacity;g.State.Bait=100;g.State.Squid=0;Call(g,"RebuildBoat",false);g.Showcase(0,0);typeof(VoyageGame).GetField("showTitle",H).SetValue(g,false);typeof(VoyageGame).GetField("paused",H).SetValue(g,false);g.UpdateManagementForecast();
                Check(g.FittedTrapCount==(hull==4?2:0),"actual fitted trap count across hull switches");
                Check(g.Forecast[1].ValuePerMinute==0&&g.Forecast[1].CostPerMinute==0,"no phantom net income without a net operator");
                Check(g.Forecast[2].ValuePerMinute==0&&g.ForecastShares[2]==0,"no crab income without fitted recovery operators");
                if(hull<4)Check(g.Forecast[2].InstalledCount==0&&g.Forecast[2].CycleValue==0&&g.Forecast[2].SpeciesCounts.Count==0,"absent traps have zero recovery value and mix, not just hidden UI");
                Check(g.ForecastShares.Sum()==100&&g.ForecastShares[0]==100,"only active rod method receives income share");
                var before=g.ForecastIncome;g.State.PrepOrders.ChumTarget=0;g.State.PrepOrders.PrepareClassMask=0;g.UpdateManagementForecast();Check(g.ForecastIncome==before,"no assumed processing premium in raw expected fish value");
                foreach(var size in new[]{new Vector2Int(1672,941),new Vector2Int(1440,900),new Vector2Int(844,390),new Vector2Int(1024,768)})
                {
                    g.PrepareInterface(size.x,size.y);var management=Bounds(g,"management/open");float height=(float)typeof(VoyageGame).GetField("ih",H).GetValue(g);float width=(float)typeof(VoyageGame).GetField("iw",H).GetValue(g);
                    Check(management.x>width/2&&management.y>=height-80&&management.yMax<=height,"management bottom right and inside safe area");
                    var home=Bounds(g,"home");Check(!home.Overlaps(management),"home and management do not overlap");
                    if(hull==4){var duties=Bounds(g,"tier5/operations");Check(duties.x>width/2&&duties.y>=height-80&&!duties.Overlaps(management)&&!duties.Overlaps(home),"former bottom-left duties now bottom right without overlap");}
                    if(hull>=2)
                    {
                        var guide=g.GetComponentsInChildren<RectTransform>().FirstOrDefault(t=>t.name=="guide"&&t.gameObject.activeInHierarchy);
                        if(guide!=null){var rect=new Rect(guide.anchoredPosition.x,-guide.anchoredPosition.y,guide.sizeDelta.x,guide.sizeDelta.y);Check(!rect.Overlaps(management),"fishing hint does not overlap management");}
                    }
                }
                rows.Add($"{hull},{g.FittedTrapCount},{g.Forecast[0].ValuePerMinute},{g.Forecast[1].ValuePerMinute},{g.Forecast[2].ValuePerMinute},{string.Join(",",g.ForecastShares)}");
            }
            g.StartTier5Trial();g.State.Chum=10;g.UpdateManagementForecast();
            Check(g.Forecast.All(f=>f.ValuePerMinute>0),"working staffed Tier5 methods can contribute");
            Check(g.Forecast[0].OperatorSecondsPerMinute+g.Forecast[2].OperatorSecondsPerMinute<=60*(g.State.Crew.Count(c=>c.Role==CrewRole.Fisherman)+1)+.001f,"rod and trap recovery share the fishing operator budget");
            Check(g.Forecast[1].Operators==1,"one Nets worker never runs both rigs at full rate");
            var netFisher=g.ExtraPeople.First(p=>p.Contract?.Role==CrewRole.Fisherman&&p.Contract.Allows(FisherTask.Nets));
            g.ToggleFisherTask(netFisher.Contract,FisherTask.Nets);g.UpdateManagementForecast();Check(g.Forecast[1].ValuePerMinute==0,"net tickbox invalidates forecast immediately");
            var models=(Transform[])typeof(VoyageGame).GetField("buoyModels",H).GetValue(g);foreach(var model in models)model.gameObject.SetActive(false);
            g.UpdateManagementForecast();Check(g.FittedTrapCount==0&&g.Forecast[2].ValuePerMinute==0&&g.ForecastShares[2]==0,"hull flag cannot invent missing/deactivated traps");
            foreach(var model in models)model.gameObject.SetActive(true);g.State.Tier5Broken[6]=g.State.Tier5Broken[7]=true;g.UpdateManagementForecast();Check(g.Forecast[2].ValuePerMinute>0,"legacy broken manual cages no longer penalize output");
            g.State.Tier5Broken[6]=g.State.Tier5Broken[7]=false;g.State.NetInventory=0;g.UpdateManagementForecast();Check(g.Forecast[1].ValuePerMinute==0,"no net stock contributes zero");
            g.Cooler.Add(new CaughtFish{Species=Species.Cod,Kg=g.State.CoolerCapacity});g.UpdateManagementForecast();
            Check(g.ForecastIncome==0&&g.ForecastShares.Sum()==0,"full hold does not promise future catch income");
            Check(g.ForecastVoyageMinutes<=g.State.FuelCapacity+1&&g.ForecastCost>1,"stalled/filled powered boat does not amortize crew over an impossible fill time");
            float fees=g.State.Crew.Sum(c=>c.Fee/(float)GameData.ContractVoyages(c.Grade));
            Check(Mathf.Abs(g.ForecastCost-1-fees/g.ForecastVoyageMinutes)<.001f,"estimated costs reconcile to fuel plus allocated actual voyage contract fees");
            float costBefore=g.ForecastCost;g.State.Fuel=2;g.UpdateManagementForecast();
            Check(g.ForecastCost>=costBefore,"costs refresh when fuel changes even if catch signature is cached");
            var rng=new System.Random(871);g.State.Rng=new System.Random(871);int coins=g.State.Coins,bait=g.State.Bait;float richness=g.State.Richness[g.ActiveSpot];
            typeof(VoyageGame).GetField("forecastSignature",H).SetValue(g,null);g.UpdateManagementForecast();
            Check(g.State.Rng.Next()==rng.Next()&&g.State.Coins==coins&&g.State.Bait==bait&&g.State.Richness[g.ActiveSpot]==richness,"forecast leaves actual RNG, money, bait and grounds untouched");
            foreach(var values in new[]{new[]{1f,1f,1f},new[]{176f,620f,106f},new[]{0f,10f,0f}}){var shares=CatchExpectation.Shares(values);Check(shares.Sum()==100&&shares.All(v=>v>=0&&v<=100),"display percentages sum to100");for(int i=0;i<values.Length;i++)if(values[i]==0)Check(shares[i]==0,"rounding cannot give absent methods income");}
            Check(CatchExpectation.Shares(0,0,0).Sum()==0,"no output is not represented as100% income");
            File.WriteAllLines("Logs/dash087/hull-availability.csv",rows);UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
        sealed class ControlledRecovery : System.Random {public override double NextDouble()=>.5;}
        static void CrabPipeline()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("DASH087 controlled actual crab pipeline").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();g.StartTier5Trial();
            foreach(var p in new[]{g.Captain,g.Hand}.Concat(g.ExtraPeople).Where(p=>p!=null))p.Stop();
            g.State.PrepOrders.ChumTarget=0;g.State.Rng=new ControlledRecovery();
            var timers=(float[])typeof(VoyageGame).GetField("buoyTimers",H).GetValue(g);timers[0]=g.BuoySoakSeconds;timers[1]=0;
            var fisher=g.ExtraPeople.First(p=>p.Contract.Role==CrewRole.Fisherman);
            void Finish(Person p){for(int n=0;n<5000&&!p.Idle;n++)p.Tick(.025f,g.WorkMult,Quaternion.identity);Check(p.Idle,"real job completes");}
            Check(g.TryBuoyWork(fisher),"real recovered trap job starts");Finish(fisher);
            var crab=g.OnDeck.Single(f=>f.Species==Species.Crab);float kg=crab.Kg;Call(g,"TickDeckFish",.5f);
            Check(g.BuoyHauls==1&&g.Flow.Sum(FlowTelemetry.Kind.Trap,60)==kg,"successful trap lands species and mass exactly once");
            g.CommandCarry(crab);Finish(g.Captain);
            Check(g.ProcessingInput.Count==1&&g.ProcessingInput[0].Species==Species.Crab&&g.Cooler.Count==0,"crab physically reaches table input");
            Check(g.TryPrepWork(g.Hand),"processor claims actual recovered crab");Finish(g.Hand);
            Check(g.ProcessingOutput.Single().Species==Species.Crab&&g.ProcessingOutput[0].Prepared,"processed crab retains identity outside hold");
            Check(g.TryCarryProcessed(g.Captain),"separate outbound carry starts");Finish(g.Captain);
            Check(g.Cooler.Single().Species==Species.Crab&&Mathf.Abs(g.HoldKg-kg)<.00001f&&g.ProcessingKg==0,"real recovered crab finishes in hold without duplication or lost mass");
            UnityEngine.Object.DestroyImmediate(g.gameObject);Debug.Log("[Catchline] DASH087 actual crab recovery-to-hold pipeline passed");
        }
        public static void Run()
        {
            Directory.CreateDirectory("Logs/dash087");ArtImport.BuildLibrary();ProbabilityChecks();NetChecks();AvailabilityAndLayout();CrabPipeline();DashboardChecks.Run();
            Debug.Log("[Catchline] DASH087 CHECKS PASSED");Debug.Log("[Catchline] Snapshot written to Logs/dash087");
        }
        public static void ValidateAndBuild(){Run();BuildBoth();}
        public static void BuildBoth()
        {
            foreach(bool test in new[]{true,false})
            {
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);var g=new GameObject(test?"DASH087 isolated check":"Catchline persistent game").AddComponent<VoyageGame>();g.SessionOnly=test;
                string scene="Assets/Scenes/Dash087"+(test?"Test":"Real")+".unity";EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(),scene);
                string output=Path.GetFullPath("Builds/Dash087/"+(test?"Test":"Real")+"/Catchline.exe");
                var result=BuildPipeline.BuildPlayer(new BuildPlayerOptions{scenes=new[]{scene},locationPathName=output,target=BuildTarget.StandaloneWindows64});Check(result.summary.result==BuildResult.Succeeded,"Windows "+(test?"Test":"Real")+" built");Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: "+output);
            }
            Debug.Log("[Catchline] Snapshot written to Logs/dash087");
        }
        // Independent frozen oracle: the pre-DASH087 production algorithm, retained only in tests.
        static List<(Species species,float kg)> LegacyNet(int hull,int spot,bool deep,float target,System.Random rng)
        {
            var netFish=new List<(Species species,float kg)>();
            bool large = deep;
            float mass = 0;
            var table = GameData.Spots[spot].Table;
            // Every added specimen has positive mass. The loop ends on remaining kg,
            // never a fish-count limit; a fish cannot cross the net's hard weight limit.
            while (true)
            {
                float remaining = target - mass;
                float total = 0;
                foreach (var entry in table)
                {
                    if (hull < GameData.MinimumHull(entry.species)) continue;
                    var d = GameData.Get(entry.species);
                    if (!large && !CatchExpectation.SmallSchool(entry.species)) continue;
                    float min = Mathf.Lerp(d.MinKg, d.MaxKg, large ? .65f : .05f);
                    if (min > remaining) continue;
                    total += entry.weight * (large ? .08f + 6f * d.Heaviness * d.Heaviness : 1);
                }
                if (total <= 0)
                {
                    if (large) { large = false; continue; }
                    break; // Residual smaller than any local school specimen stays empty.
                }
                float roll = (float)rng.NextDouble() * total;
                Species species = table[0].species;
                foreach (var entry in table)
                {
                    if (hull < GameData.MinimumHull(entry.species)) continue;
                    var d = GameData.Get(entry.species);
                    if (!large && !CatchExpectation.SmallSchool(entry.species)) continue;
                    float min = Mathf.Lerp(d.MinKg, d.MaxKg, large ? .65f : .05f);
                    if (min > remaining) continue;
                    species = entry.species;
                    roll -= entry.weight * (large ? .08f + 6f * d.Heaviness * d.Heaviness : 1);
                    if (roll <= 0) break;
                }
                var fish = GameData.Get(species);
                float low = Mathf.Lerp(fish.MinKg, fish.MaxKg, large ? .65f : .05f);
                float high = Mathf.Min(remaining, Mathf.Lerp(fish.MinKg, fish.MaxKg, large ? 1f : .25f));
                float kg = Mathf.Lerp(low, high, (float)rng.NextDouble());
                if (kg <= 0 || mass + kg > target + .00001f) break;
                netFish.Add((species, kg)); mass += kg;
            }
            return netFish;
        }

    }
}
