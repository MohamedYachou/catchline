using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace Catchline.EditorTools
{
    public static class Balance045Checks
    {
        const BindingFlags H=BindingFlags.Instance|BindingFlags.NonPublic;
        static void Check(bool ok,string why){if(!ok)throw new Exception("BALANCE045: "+why);}
        static object Call(VoyageGame g,string n,params object[] a)=>typeof(VoyageGame).GetMethod(n,H).Invoke(g,a);
        static void Work(Person p){for(int i=0;i<10000&&!p.Idle;i++)p.Tick(.02f, Quaternion.identity);Check(p.Idle,"action finishes");}
        static CaughtFish Add(VoyageGame g,Species s,float kg,float age=0){var f=new CaughtFish{Species=s,Kg=kg,StowedAt=g.SimTime-age};g.DeliverCatch(f);return f;}
        static void Empty(VoyageGame g){Call(g,"ClearPrepWork");g.Cooler.Clear();Call(g,"ClearProcessingPipeline",false);g.State.Chum=0;}
        public static void Run()
        {
            Directory.CreateDirectory("Logs/balance045"); ArtImport.BuildLibrary();
            var state=new GameState(45);state.Hull=1;
            Check(state.CoolerCapacity==40,"Skiff40kg");state.Owned.Add(UpgradeId.BigCooler);Check(state.CoolerCapacity==60,"Skiff60kg upgrade");
            state.Hull=2;state.Coins=9500;state.BestVoyageKg=99.99f;
            Check(!state.RefitPrep()&&state.Coins==9500,"100kg goal enforced before fee");state.BestVoyageKg=100;state.Coins=9499;
            Check(!state.RefitPrep(),"fee enforced");state.Coins=9500;Check(state.RefitPrep()&&state.Coins==0&&state.Hull==3,"real9500paid refit");
            Check(state.CoolerCapacity==240&&state.NetCapacityKg==30&&state.HullDef.CrewCap==4,"Prep240upgrade/30net/4berths");
            state.Owned.Add(UpgradeId.NetSystem);Check(state.NetCapacityKg==44,"Prep44heavy net");
            state.Save("Logs/balance045/progression.json");var load=GameState.Load("Logs/balance045/progression.json");Check(load.Hull==3&&load.BestVoyageKg==100,"record persists");
            var fisher=new CrewMember{Role=CrewRole.Fisherman};state.Chum=2;state.Bait=3;state.Squid=4;
            Check(state.SelectBait(fisher)==BaitPermission.Chum,"legacy crew all bait");
            fisher.HasBaitPolicy=true;fisher.AllowedBait=BaitPermission.Worms;
            Check(state.TakeBait(fisher,out var squid,out var chum,out var scraps)&&!squid&&!chum&&!scraps&&state.Bait==2&&state.Chum==2&&state.Squid==4,"restricted bait preserves other stock");
            state.Bait=0;Check(!state.TakeBait(fisher,out _,out _,out _),"no silently forbidden scraps");
            fisher.AllowedBait=BaitPermission.Scraps;Check(state.TakeBait(fisher,out _,out _,out scraps)&&scraps,"allowed free scraps");
            fisher.AllowedBait=BaitPermission.None;Check(!state.CanTakeBait(fisher),"all-off waits");
            state.Deckhand=fisher;state.Save("Logs/balance045/bait.json");load=GameState.Load("Logs/balance045/bait.json");Check(load.Deckhand.HasBaitPolicy&&load.Deckhand.BaitPolicy==BaitPermission.None,"explicit zero persists");
            var settings=JsonUtility.FromJson<PrepOrderSettings>("{\"ChumMaxKg\":2,\"ChumMaxValue\":10}");Check(settings.ChumMaxValue==35,"old cap migrates from obsolete field");
            Check(PrepOrderSettings.ChumYield(Species.Herring,.2f)==1&&PrepOrderSettings.ChumYield(Species.Herring,.3f)==2&&PrepOrderSettings.ChumYield(Species.SeaBass,1f)==3&&PrepOrderSettings.ChumYield(Species.SeaBass,3f)==0,"class-based chum yield and protected purple");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("BALANCE045 isolated").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();Check(g.StartPrepBoatTrial(),"trial");
            var hands=new[]{g.Hand}.Concat(g.ExtraPeople).Where(p=>p.Contract.Role==CrewRole.Deckhand).ToArray();
            foreach(var h in hands){h.Stop();g.SetDeckhandWork(h.Contract,DeckhandWork.Prep);}
            Empty(g);g.State.PrepOrders.HasClassFilters=true;g.State.PrepOrders.ChumClassMask=63;var pollock=Add(g,Species.Pollock,1.4f);
            Check(g.TryPrepWork(hands[0])&&g.ChumBeingMade==1,"white Pollock reserves one chum");Work(hands[0]);Check(g.State.Chum==1&&!g.Cooler.Contains(pollock),"white Pollock makes one chum");
            g.State.Chum=9;Add(g,Species.Pollock,1.4f);Add(g,Species.Pollock,1.4f);
            Check(g.TryPrepWork(hands[0])&&g.TryPrepWork(hands[1])&&g.ChumBeingMade==1,"concurrent scaled reservations bounded at target");Work(hands[0]);Work(hands[1]);Check(g.State.Chum==10,"no target overshoot");
            // M0: the table no longer prepares fish. Unchummed fish are sorted (oldest first) at full value.
            Empty(g);g.State.PrepOrders.ChumTarget=0;
            var fresh=Add(g,Species.Cod,7);var old=Add(g,Species.Herring,.2f,240);
            Check(g.TryPrepWork(hands[0]),"oldest reservation");Work(hands[0]);Check(g.ProcessingOutput.Contains(old)&&g.ProcessingInput.Contains(fresh),"oldest sorted first despite list order");
            Empty(g);var purple=Add(g,Species.Conger,7);float kg=purple.Kg;int value=g.State.ValueOf(purple,g.SimTime);
            Check(g.TryPrepWork(hands[0]),"sort reservation");Work(hands[0]);Check(g.ProcessingOutput.Contains(purple)&&purple.Kg==kg&&g.State.Chum==0&&g.State.ValueOf(purple,g.SimTime)==value,"sorting keeps cargo and value, no premium or by-product");
            // Main-hold fullness does not consume the distinct input reservations.
            Empty(g);Add(g,Species.Cod,5);Add(g,Species.Cod,5);var filler=new CaughtFish{Species=Species.Cod,Kg=g.State.CoolerCapacity-15,StowedAt=g.SimTime};g.TryStore(filler);
            foreach(var h in hands)Check(g.TryPrepWork(h),"hand reserves full-hold fish");
            foreach(var h in hands)Work(h);Check(g.ProcessingOutput.Count==2 && g.ProcessingInput.Count==0,"all workers sort distinct fish to output");
            g.TryStore(new CaughtFish{Species=Species.Cod,Kg=15,StowedAt=g.SimTime});
            var fullFisher=g.ExtraPeople.First(p=>p.Contract.Role==CrewRole.Fisherman);fullFisher.Stop();
            var fullRod=g.Rods[0];fullRod.Fisher=fullFisher;fullRod.State=RodState.Ready;fullFisher.Place(fullRod.Tile);
            Call(g,"FisherThink",fullFisher);Check(fullFisher.Idle&&fullRod.State==RodState.Ready,"full hold stops new automated fishing");
            g.HeadHome();for(int i=0;i<1800&&g.CurrentMode!=VoyageGame.Mode.Harbour;i++)g.Tick(.05f);
            Check(g.State.BestVoyageKg>=160,"real docking records actual delivered kg before sale");g.State.UnsoldCatch.Clear();g.Showcase(0,0);
            // Rod bait consumed by a deckhand honors assigned fisher policy.
            Empty(g);var owner=g.ExtraPeople.First(p=>p.Contract.Role==CrewRole.Fisherman);var rod=g.Rods[0];rod.Fisher=owner;
            owner.Contract.HasBaitPolicy=true;owner.Contract.AllowedBait=BaitPermission.Worms;g.State.Chum=5;g.State.Bait=5;g.State.Squid=5;rod.State=RodState.Unbaited;
            Call(g,"Bait",hands[0],rod);Work(hands[0]);Check(rod.State==RodState.Ready&&!rod.Chum&&!rod.Squid&&!rod.Scraps&&g.State.Chum==5&&g.State.Bait==4,"deckhand honors rod owner's bait");
            g.Showcase(-1,0);
            typeof(VoyageGame).GetField("hudTab",H).SetValue(g,VoyageGame.HudTab.CrewOffice);
            typeof(VoyageGame).GetField("panelOpen",H).SetValue(g,true);
            g.PrepareInterface(844,390);
            Check(g.InvokeInterface("employee/"+owner.Contract.Name+"/buy") || g.InvokeInterface("crew/count/Fisherman/settings/0"),"actual per-fisher Bait entry opens modal");
            g.PrepareInterface(844,390);
            Check(g.InvokeInterface("crew/bait/Chum")&&(owner.Contract.BaitPolicy&BaitPermission.Chum)!=0,"real bait toggle");Check(g.InvokeInterface("crew/bait/close"),"close bait modal");
            // Net soak fallback, then preemption with actual fish claim cancellation.
            g.Showcase(0,0);Empty(g);foreach(var h in hands){h.Stop();g.SetDeckhandWork(h.Contract,DeckhandWork.Fish);}g.SetDeckhandWork(hands[0].Contract,DeckhandWork.Nets);
            Check(g.TryNetWork(hands[0]),"net sets");Work(hands[0]);Check(g.Net==VoyageGame.NetState.Soaking,"net soaking");
            g.LandFish(g.Rods[0],Species.Herring,.2f);var deck=g.OnDeck.Last();deck.Age=1;
            Call(g,"HandThink",hands[0]);Check(deck.ClaimedBy==hands[0],"Nets hand picks rod fish during soak");
            Call(g,"TickNet",GameData.ShallowNetSoakSeconds);Call(g,"PreemptNetFallback");Check(deck.ClaimedBy==null&&hands[0].Idle,"ready net cancels uncollected pickup and releases claim");
            Call(g,"HandThink",hands[0]);Check(g.Net==VoyageGame.NetState.Hauling,"ready net takes priority");
            g.HeadHome();
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            SecondNetModuleChecks.RunCore();
            Debug.Log("[Catchline] BALANCE045 CHECKS PASSED");Debug.Log("[Catchline] Snapshot written to Logs/balance045");
        }
        public static void ValidateAndBuild(){Run();PrepFisherChecks.BuildPreview();}
        public static void BuildPreview(){PrepFisherChecks.BuildPreview();}
        public static void ValidateIntegrated(){Run();CrewCounterChecks.ValidateAndBuild();}
    }
}
