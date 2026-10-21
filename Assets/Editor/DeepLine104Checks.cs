using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class DeepLine104Checks
    {
        static void Check(bool ok, string why) { if (!ok) throw new Exception("DEEP104: " + why); }
        static void Advance(VoyageGame game, float seconds)
        {
            for (int i = 0; i < Mathf.CeilToInt(seconds / .05f); i++) game.Tick(.05f);
        }
        static void Clock()
        {
            var cycle = new DeepLineCycle();
            Check(!cycle.Deploy(BaitPermission.None), "no deployment without bait");
            Check(cycle.Deploy(BaitPermission.Chum) && !cycle.Deploy(BaitPermission.Chum), "one deployment only");
            Check(!cycle.Tick(1) && cycle.Phase == DeepLinePhase.Soaking && cycle.Remaining == 60, "drop then sixty seconds");
            Check(!cycle.Tick(0) && cycle.Remaining == 60 && !cycle.Tick(float.NaN), "paused or invalid time cannot advance");
            Check(!cycle.Tick(59) && cycle.Phase == DeepLinePhase.Soaking, "not early");
            Check(!cycle.Tick(1) && cycle.Phase == DeepLinePhase.Raising, "automatic raise at minute");
            Check(cycle.Tick(2) && !cycle.Tick(10000) && !cycle.Deploy(BaitPermission.Chum), "return exactly once, collection backpressure");
            cycle.Collected(); Check(cycle.Deploy(BaitPermission.Chum) && cycle.Tick(1000), "large tick and next cycle");
            cycle.Reset(); Check(cycle.Phase == DeepLinePhase.Empty && cycle.Bait == BaitPermission.None, "trip reset");
            Check(DeepLineRules.CatchCount(0) + DeepLineRules.CatchCount(1) == 2, "one fish per standard rod");
            foreach (FisherWork work in Enum.GetValues(typeof(FisherWork)))
                Check(DeepLineRules.AllowsRods(work) || DeepLineRules.AllowsCrabs(work) || DeepLineRules.AllowsDeepLines(work), "each policy has work");
            Check(!DeepLineRules.AllowsCrabs(FisherWork.RodsOnly) && !DeepLineRules.AllowsDeepLines(FisherWork.RodsOnly)
                && !DeepLineRules.AllowsRods(FisherWork.CrabsOnly) && !DeepLineRules.AllowsDeepLines(FisherWork.CrabsOnly)
                && !DeepLineRules.AllowsRods(FisherWork.DeepLinesOnly) && !DeepLineRules.AllowsCrabs(FisherWork.DeepLinesOnly), "exclusive policies");
        }
        const System.Reflection.BindingFlags H=System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic;
        static object Call(VoyageGame g,string n,params object[] args)=>typeof(VoyageGame).GetMethod(n,H).Invoke(g,args);
        static void Work(Person p){for(int n=0;n<6000&&!p.Idle;n++)p.Tick(.025f,1,Quaternion.identity);Check(p.Idle,"real job completes");}
        static void RolesAndNets()
        {
            var g=new GameObject("DEEP104 D-F acceptance").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();g.StartTier5Trial();
            Check(g.State.CrewCount==6 && !g.State.Crew.Any(c=>c.Role==CrewRole.Engineer) && !g.State.Board.Any(c=>c.Role==CrewRole.Engineer),"six berths, no Tier5 Engineer hiring/default");
            var legacy=new CrewMember{Name="Preserved Engineer",Role=CrewRole.Engineer,VoyagesLeft=4,Grade=Grade.Experienced};
            g.State.ExtraCrew.Add(legacy);g.State.EnsureCrewRoleOffers();
            Check(g.State.CrewCount==6 && g.State.InactiveEngineers.Contains(legacy)&&legacy.VoyagesLeft==4,"paid legacy Engineer retained inactive and berth released");
            g.State.Save("Logs/deep104/migration.json");var loaded=GameState.Load("Logs/deep104/migration.json");Check(loaded.InactiveEngineers.Single().Name==legacy.Name && loaded.InactiveEngineers[0].VoyagesLeft==4,"inactive Engineer survives save without contract loss");
            var fishers=g.ExtraPeople.Where(p=>p.Contract.Role==CrewRole.Fisherman).ToArray();
            foreach(var p in fishers){p.Stop();p.Contract.HasFisherTasks=true;p.Contract.AllowedTasks=FisherTask.Nets;}
            g.State.PrepOrders.ChumTarget=0;
            g.State.Tier5Broken[4]=true;g.State.Tier5Condition[4]=0;
            Check(g.TryNetWork(fishers[0]),"fisher operates manual net despite legacy broken flag");fishers[0].Stop();Check(g.Net==VoyageGame.NetState.Stowed,"cancel releases operator claim");
            Check(g.TryNetWork(fishers[0]),"retry fisher set");Work(fishers[0]);Call(g,"TickNet",GameData.ShallowNetSoakSeconds);
            Check(g.TryNetWork(fishers[0]),"fisher hauls ready net");Work(fishers[0]);
            Check(g.NetBasketCount>0&&!g.NetUnloadActive,"fisher lands basket, collection is a separate hand job");
            Check(!g.TryNetWork(g.Hand),"Tier5 hand cannot operate net");
            foreach(var f in g.OnDeck)f.Age=1;
            var carrier=g.ExtraPeople.First(p=>p.Contract.Role==CrewRole.Deckhand);carrier.Stop();Call(g,"BeginNetUnload",carrier);
            for(int n=0;n<6000&&g.NetUnloadActive;n++){Call(g,"TickNetUnload",.025f);carrier.Tick(.025f,1,Quaternion.identity);}
            Check(g.NetBasketCount==0&&g.ProcessingInput.Count>0,"ordinary hand collects entire basket into processing");
            Check(g.TryPrepWork(g.Hand),"processor accepts basket specimen");Work(g.Hand);
            Check(g.ProcessingOutput.Count>0&&g.TryCarryProcessed(carrier),"processed basket fish waits for separate outbound carry");Work(carrier);Check(g.Cooler.Any(f=>f.Prepared),"net specimen reaches hold prepared");
            foreach(var p in g.ExtraPeople)p.Stop();
            var selected=fishers[0].Contract;selected.AllowedTasks=FisherTask.Rods|FisherTask.Nets;
            g.OpenManagement();
            foreach(var size in new[]{new Vector2Int(1440,900),new Vector2Int(844,390)})
            {
                g.PrepareInterface(size.x,size.y);Check(g.InvokeInterface("management/tab/crew"),"Crew third tab");g.PrepareInterface(size.x,size.y);
                int index=g.State.Crew.ToList().IndexOf(selected);Check(g.InvokeInterface("management/crew/select/"+index),"select actual fisher");g.PrepareInterface(size.x,size.y);
                var before=selected.FishingTasks;Check(g.InvokeInterface("management/crew/task/DeepLines")&&selected.FishingTasks==(before^FisherTask.DeepLines),"independent task tickbox");
                g.PrepareInterface(size.x,size.y);var bait=selected.BaitPolicy;Check(g.InvokeInterface("management/crew/bait/Squid")&&selected.BaitPolicy==(bait^BaitPermission.Squid),"real bait tickbox");
            }
            g.State.Save("Logs/deep104/tasks.json");loaded=GameState.Load("Logs/deep104/tasks.json");Check(loaded.Crew.Single(c=>c.Name==selected.Name).FishingTasks==selected.FishingTasks,"task combinations survive saves");
            g.State.Chum=10; foreach(var p in fishers)p.Contract.AllowedTasks=FisherTask.DeepLines;
            g.UpdateManagementForecast();Check(g.Forecast.Length==4&&g.Forecast[1].ValuePerMinute==0&&g.Forecast[2].ValuePerMinute==0&&g.Forecast[3].ValuePerMinute>0,"exclusive deep tasks forecast deep only plus captain rod");
            Check(g.Forecast.Sum(f=>f.OperatorSecondsPerMinute)<=60*(fishers.Length+1)+.01f,"shared finite fisher/captain budget");
            foreach(var p in fishers)p.Contract.AllowedTasks=FisherTask.None;
            g.UpdateManagementForecast();Check(g.Forecast[3].ValuePerMinute==0,"all tasks off means no fisher deep forecast");
            g.CloseManagement();g.HeadHome();Advance(g,80);Call(g,"ResetNet");Check(g.ConfigureTier5NetTeam(),"net layout team setup");g.Showcase(0,0);
            Check(!g.DeepLinesActive&&g.Rods.Count==2,"net layout excludes deep rigs and optional rods");
            var netters=g.ExtraPeople.Where(p=>p.Contract.Role==CrewRole.Fisherman&&p.Contract.Allows(FisherTask.Nets)).ToArray();foreach(var p in netters)p.Stop();
            Check(g.TryNetWork(netters[0])&&g.TryNetWork(netters[1]),"two independent fisher net claims");Work(netters[0]);Work(netters[1]);
            Check(g.Net==VoyageGame.NetState.Soaking&&g.SecondNet==VoyageGame.NetState.Soaking,"two fisher operated nets soak independently");
            Call(g,"TickNet",GameData.ShallowNetSoakSeconds);Call(g,"TickSecondNet",GameData.ShallowNetSoakSeconds);
            Check(g.TryNetWork(netters[0]),"first fisher haul");Work(netters[0]);Check(g.TryNetWork(netters[1]),"second haul allowed with first basket pending");Work(netters[1]);
            Check(g.OnDeck.Where(f=>f.FromNetBasket).Select(f=>f.Tile).Distinct().Count()==2,"both independent real baskets retained");
            g.HeadHome();Advance(g,80);Check(g.CurrentMode==VoyageGame.Mode.Harbour,"return salvages two baskets");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
        static void Distribution()
        {
            var report=new System.Collections.Generic.List<string>{"spot,bait,class,expected,observed,mean_kg,mean_value"};
            for(int spot=0;spot<GameData.Spots.Length;spot++)foreach(var bait in new[]{BaitPermission.Chum})
            {
                var state=new GameState(10400+spot){Hull=4};var options=DeepLineRules.Options(state,spot,bait);var mix=DeepLineRules.Expectation(state,spot,bait);
                Check(Mathf.Abs(options.Sum(o=>o.Probability)-1)<.0001f,"local deep probabilities normalize");
                int[] counts=new int[6];double kg=0,value=0,value2=0;const int samples=12000;
                for(int n=0;n<samples;n++)
                {
                    var f=DeepLineRules.Roll(state,spot,bait);Check(GameData.Spots[spot].Table.Any(e=>e.species==f.species),"deep never invents nonlocal species");
                    counts[(int)CatchPresentation.Tier(f.species,f.kg)]++;kg+=f.kg;float worth=CatchExpectation.NominalValue(f.species,f.kg);value+=worth;value2+=worth*worth;
                }
                double mean=value/samples,se=Math.Sqrt(Math.Max(0,value2/samples-mean*mean)/samples);
                Check(Math.Abs(mean-mix.Value)<Math.Max(.1,7*se),"deep expected value matches independent real catches");
                for(int tier=0;tier<6;tier++)
                {
                    float expected=options.Where(o=>(int)o.Tier==tier).Sum(o=>o.Probability);
                    Check(Math.Abs(counts[tier]-samples*expected)<7*Math.Sqrt(samples*expected*(1-expected))+2,"deep class odds match real catches");
                    if(spot==4)Check(Mathf.Abs(expected-DeepLineRules.ClassWeights[tier])<.0001f,"full deep sea exact Mo class mix");
                    report.Add($"{spot},{bait},{tier},{expected},{counts[tier]/(float)samples},{kg/samples},{mean}");
                }
            }
            File.WriteAllLines("Logs/deep104/deep-distribution.csv",report);
        }
        static void UpgradeAndChum()
        {
            var g=new GameObject("DEEP104 third rig and existing chum table").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();g.StartTier5Trial();
            g.HeadHome();Advance(g,80);g.State.Coins=3500;
            Check(g.State.TryBuy(UpgradeId.ThirdDeepLine)&&g.State.Coins==0&&!g.State.TryBuy(UpgradeId.ThirdDeepLine),"3500 upgrade charges exactly once");g.SyncUpgrades();
            Check(g.FittedDeepLineCount==3,"actual third rig fitted after purchase");var tile=g.DeepLineWorkerTile(2);
            Debug.Log("[Catchline] DEEP104 THIRD RIG worker="+tile+" local="+g.Grid.GetLocal(tile));
            var tips=(Vector3[])typeof(VoyageGame).GetField("deepLineTips",H).GetValue(g);
            Debug.Log("[Catchline] DEEP104 TIPS "+string.Join(";",tips.Select(v=>v.ToString())));
            for(int rig=0;rig<3;rig++)Check(tips[rig].y>2,"actual deep tip above water, rig "+rig+" "+tips[rig]);
            Check(!g.Grid.IsBlocked(tile),"third worker clear of cage/normal rod/rig meshes");
            foreach(var to in g.BuoyWorkerTiles.Concat(g.PrepWorkerTiles).Concat(g.State.HullDef.CrewRest).Concat(g.Rods.Select(r=>r.Tile)).Append(g.State.HullDef.Seat).Append(g.State.HullDef.HoldAccess))
                Check(g.Grid.FindPath(tile,to)!=null,"third rig connected to all crew destinations "+to);
            Check(g.Boat.GetComponentsInChildren<Transform>().Any(t=>t.name=="DeepLineRig_3"),"third real imported rig geometry exists");
            g.State.Save("Logs/deep104/third-rig.json");var saved=GameState.Load("Logs/deep104/third-rig.json");Check(saved.Has(UpgradeId.ThirdDeepLine),"third upgrade survives save/load");
            var early=new GameState(3){Hull=3,Coins=99999};Check(!early.TryBuy(UpgradeId.ThirdDeepLine)&&early.Coins==99999,"third rig offered only on Tier5");
            var member=g.State.Crew.First(c=>c.Role==CrewRole.Fisherman);member.HasFisherTasks=true;member.AllowedTasks=FisherTask.DeepLines;member.HasBaitPolicy=true;member.AllowedBait=BaitPermission.Chum;
            g.State.Deckhand=null;g.State.ExtraCrew.RemoveAll(c=>c!=member);g.SyncCrew();g.State.Bait=100;g.State.Chum=100;g.Showcase(0,0);
            Advance(g,20);Check(g.State.Chum==97&&Enumerable.Range(0,3).All(i=>g.DeepLineStatus(i)==DeepLinePhase.Soaking),"one real fisher baits all three, one portion each");
            float before=g.DeepLineRemaining(2);g.Tick(0);Check(g.DeepLineRemaining(2)==before,"actual third line pauses");
            Advance(g,65);Check(g.DeepLineHauls==3&&g.OnDeck.Count(f=>f.DeepLineRig>=0)==3,"three independent rigs land one specimen each");
            Advance(g,90);Check(g.State.Chum==97&&g.OnDeck.Count(f=>f.DeepLineRig>=0)==3,"upgraded backlog remains bounded without carriers");
            g.HeadHome();Advance(g,80);Check(g.ToggleSecondNetModule()&&g.FittedDeepLineCount==0&&!g.Boat.GetComponentsInChildren<Transform>().Any(t=>t.name=="DeepLineRig_3"),"side net excludes all three rig meshes and jobs");
            Check(g.ToggleSecondNetModule()&&g.FittedDeepLineCount==3,"saved third restored when swapping back");
            g.StartTier5Trial();foreach(var p in g.ExtraPeople)p.Stop();
            g.State.PrepOrders.HasClassFilters=true;g.State.PrepOrders.ChumClassMask=63;g.State.PrepOrders.PrepareClassMask=0;g.State.PrepOrders.ChumTarget=10;g.State.Chum=0;
            var station=g.Boat.GetComponentsInChildren<Transform>(true).First(t=>t.name=="PrepStation");Check(station.gameObject.activeInHierarchy&&g.PrepWorkerTiles.Length==2,"original working station preserved");
            var samplesFish=new[]{new CaughtFish{Species=Species.Herring,Kg=.2f},new CaughtFish{Species=Species.Herring,Kg=.3f},new CaughtFish{Species=Species.SeaBass,Kg=1f}};
            int expectedStock=0;
            for(int i=0;i<3;i++){g.DeliverCatch(samplesFish[i]);Check(g.TryPrepWork(g.Hand),"existing Tier5 station accepts permitted chum input");Work(g.Hand);expectedStock+=i+1;Check(g.State.Chum==expectedStock&&!g.ProcessingInput.Contains(samplesFish[i]),"white/green/blue full chum yield");}
            var chumFisher=g.ExtraPeople.First(p=>p.Contract.Role==CrewRole.Fisherman);chumFisher.Contract.HasFisherTasks=true;chumFisher.Contract.AllowedTasks=FisherTask.DeepLines;
            chumFisher.Contract.HasBaitPolicy=true;chumFisher.Contract.AllowedBait=BaitPermission.Worms;
            Check(!g.TryDeepLineWork(chumFisher),"worms cannot replace required self-made chum");
            chumFisher.Contract.AllowedBait=BaitPermission.Chum;
            Check(g.TryDeepLineWork(chumFisher),"station-produced chum starts actual rig baiting");Work(chumFisher);
            Check(g.State.Chum==5&&g.DeepLineStatus(0)==DeepLinePhase.Dropping,"actual table-to-deep-line supply chain consumes one produced portion");
            foreach(var fish in new[]{new CaughtFish{Species=Species.SeaBass,Kg=3},new CaughtFish{Species=Species.ApexReefShark,Kg=10},new CaughtFish{Species=Species.GiantSquid,Kg=20}})g.DeliverCatch(fish);
            Check(!g.TryPrepWork(g.Hand)&&g.ProcessingInput.Count==3&&g.State.Chum==5,"purple/gold/red cannot be chummed even with legacy all-class mask");
            g.State.Chum=9;var blue=new CaughtFish{Species=Species.SeaBass,Kg=1};g.DeliverCatch(blue);
            Check(g.TryPrepWork(g.Hand),"blue chum reserved near target");g.Hand.Stop();Check(g.State.Chum==9&&g.ProcessingInput.Contains(blue),"cancel keeps fish and stock intact");
            Check(g.TryPrepWork(g.Hand),"retry chum");Work(g.Hand);Check(g.State.Chum==12,"whole blue fish yields full three portions across target");
            g.State.Save("Logs/deep104/chum-orders.json");saved=GameState.Load("Logs/deep104/chum-orders.json");Check(saved.Chum==0&&saved.PrepOrders.ChumTarget==10&&saved.PrepOrders.ChumClasses==7,"chum settings persist, per-voyage stock does not");
            g.State.PrepOrders.PrepareClassMask=63;g.State.PrepOrders.ChumTarget=0;Check(g.TryPrepWork(g.Hand),"same station still prepares protected fish");Work(g.Hand);
            Check(g.ProcessingOutput.Any(f=>f.Prepared&&f.PreparedBonus==1.5f),"Tier5 station retains actual 150percent preparation");
            g.HeadHome();Advance(g,80);Check(g.State.Chum==0,"chum discarded on return");UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
        public static void Expanded()
        {
            Run();Distribution();UpgradeAndChum();
            Debug.Log("[Catchline] DEEP104 EXPANSION PASSED");Debug.Log("[Catchline] Snapshot written to Logs/deep104");
        }
        public static void Regression()
        {
            Expanded(); DashboardMathChecks.Run(); SecondNetModuleChecks.RunCore();
            Debug.Log("[Catchline] DEEP104 REGRESSION PASSED");
            Debug.Log("[Catchline] Snapshot written to Logs/deep104");
        }
        public static void BuildBoth()
        {
            ArtImport.BuildLibrary();
            foreach(bool test in new[]{true,false})
            {
                EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
                var g=new GameObject(test?"DEEP104 isolated Test":"Catchline persistent Real").AddComponent<VoyageGame>();g.SessionOnly=test;
                string scene="Assets/Scenes/Deep104"+(test?"Test":"Real")+".unity";EditorSceneManager.SaveScene(UnityEngine.SceneManagement.SceneManager.GetActiveScene(),scene);
                string output=Path.GetFullPath("Builds/Deep104/"+(test?"Test":"Real")+"/Catchline.exe");
                var r=UnityEditor.BuildPipeline.BuildPlayer(new UnityEditor.BuildPlayerOptions{scenes=new[]{scene},locationPathName=output,target=UnityEditor.BuildTarget.StandaloneWindows64});
                Check(r.summary.result==UnityEditor.Build.Reporting.BuildResult.Succeeded,"Windows build "+test);
                Debug.Log("[Catchline] PLAYABLE PREVIEW BUILT: "+output);
            }
            Debug.Log("[Catchline] Snapshot written to Logs/deep104");
        }
        public static void Run()
        {
            Directory.CreateDirectory("Logs/deep104"); Clock(); ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("DEEP104 isolated check").AddComponent<VoyageGame>();
            g.SessionOnly = true; g.Build(); Check(g.StartTier5Trial(), "isolated Tier5 start");
            Check(g.DeepLinesActive && g.State.HullDef.Model == "Tier5DeepLines103", "new fitted model and actual deep-line anchors");
            for (int rig = 0; rig < 2; rig++)
            {
                var tile = g.DeepLineWorkerTile(rig);
                Debug.Log("[Catchline] DEEP104 worker " + rig + " tile " + tile + " blocked=" + g.Grid.IsBlocked(tile));
                Check(!g.Grid.IsBlocked(tile) && g.Grid.FindPath(g.State.HullDef.Seat, tile) != null, "real worker access " + rig);
            }
            var fisher = g.State.Crew.First(c => c.Role == CrewRole.Fisherman);
            g.State.Deckhand = null; g.State.ExtraCrew.RemoveAll(c => c != fisher); g.SyncCrew();
            var person = g.ExtraPeople.Single(p => p.Contract == fisher);
            g.SetFisherWork(fisher, FisherWork.DeepLinesOnly);
            fisher.HasBaitPolicy = true; fisher.AllowedBait = BaitPermission.Chum;
            g.State.Squid = 0; g.State.Chum = 100; g.State.Bait = 100;
            Check(g.TryDeepLineWork(person), "actual worker claims deep job");
            person.Stop(); Check(g.State.Chum == 100 && g.DeepLineStatus(0) == DeepLinePhase.Empty, "cancel walk before commit charges nothing");
            Advance(g, 20); Check(g.State.Chum == 98 && Enumerable.Range(0, 2).All(i => g.DeepLineStatus(i) == DeepLinePhase.Soaking), "one fisher baits both then free while soaking");
            Advance(g, 65);
            Check(g.DeepLineHauls == 2 && g.OnDeck.Count(f => f.DeepLineRig >= 0) == 2, "automatic return, independent real specimens");
            Check(g.OnDeck.Where(f => f.DeepLineRig >= 0).All(f => f.Kg > 0 && f.ClaimedBy == null), "real unclaimed cargo");
            float landedKg = g.OnDeck.Where(f => f.DeepLineRig >= 0).Sum(f => f.Kg);
            Advance(g, 90);
            Check(g.DeepLineHauls == 2 && g.State.Chum == 98 && g.OnDeck.Count(f => f.DeepLineRig >= 0) == 2, "no carrier retains backlog and blocks rebait, no deck expiry");
            Check(Mathf.Abs(g.Flow.LandedKg - landedKg) < .001f && g.Flow.LostKg == 0, "per specimen landed mass, no silent loss");
            g.State.Save("Logs/deep104/policy-save.json"); var loaded = GameState.Load("Logs/deep104/policy-save.json");
            Check(loaded.Crew.Single().FishingWork == FisherWork.DeepLinesOnly, "fisher policy save roundtrip");
            var legacy = JsonUtility.FromJson<CrewMember>("{\"Name\":\"Old fisher\",\"Role\":1}");
            Check(legacy.FishingWork == FisherWork.CrabAndDeepFirst, "old-save mixed policy default");
            fisher.AllowedBait = BaitPermission.None;
            g.State.EnsureCrewRoleOffers(); Check(g.State.Hire(g.State.Board.First(c => c.Role == CrewRole.Deckhand)), "add real collection hand");
            g.SyncCrew(); Advance(g, 90);
            Check(!g.OnDeck.Any(f => f.DeepLineRig >= 0) && g.ProcessingInput.Count > 0, "ordinary deckhand pickup delivers deep catch to processing");
            // The new hand can independently bait ordinary unowned rods; inspect deep jobs,
            // not global bait stock, when checking the fisher's now-empty permission policy.
            Check(g.DeepLineHauls == 2 && Enumerable.Range(0, 2).All(i => g.DeepLineStatus(i) == DeepLinePhase.Empty)
                && !g.TryDeepLineWork(person), "no allowed bait means no new deep deployment");
            g.HeadHome(); Advance(g, 80); Check(g.CurrentMode == VoyageGame.Mode.Harbour, "returns safely");
            Check(g.ToggleSecondNetModule() && !g.DeepLinesActive && g.Rods.Count == 2, "side-net layout excludes entire deep module");
            g.Showcase(0, 0); Advance(g, 70);
            Check(!g.TryDeepLineWork(g.ExtraPeople.Single(p => p.Contract == fisher)), "absent module cannot take work");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            RolesAndNets();
            Debug.Log("[Catchline] DEEP104 CHECKS PASSED");
            Debug.Log("[Catchline] Snapshot written to Logs/deep104");
        }
    }
}
