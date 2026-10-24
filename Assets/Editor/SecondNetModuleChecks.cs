using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class SecondNetModuleChecks
    {
        const BindingFlags H=BindingFlags.Instance|BindingFlags.NonPublic;
        static void Check(bool ok,string why){if(!ok)throw new Exception("MODULE042: "+why);}
        static object Call(VoyageGame g,string n,params object[] a)=>typeof(VoyageGame).GetMethod(n,H).Invoke(g,a);
        static void Work(Person p){for(int i=0;i<3000&&!p.Idle;i++)p.Tick(.02f, Quaternion.identity);Check(p.Idle,"crew action completes");}
        sealed class FailedHaul : System.Random { public override double NextDouble()=>.9; }
        public static void RunCore()
        {
            Directory.CreateDirectory("Logs/module042");ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("MODULE042 isolated check").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();
            Check(g.StartPrepBoatTrial(),"trial starts");g.Showcase(-1,0);
            g.State.Coins=1999;Check(!g.BuySecondNetModule()&&g.State.Coins==1999&&!g.State.SecondNetOwned,"cannot buy without2000");
            g.State.Coins=2000;Check(g.BuySecondNetModule()&&g.State.Coins==0,"purchase costs exactly2000");
            Check(g.SecondNetActive&&g.UsableRodCount==1&&g.Rods.Count==1&&g.Rods[0].Tile==g.State.HullDef.RodTiles[2],"two real rods removed, stern rod stays");
            Check(!g.BuySecondNetModule()&&g.State.Coins==0,"cannot charge twice");
            Check(g.ToggleSecondNetModule()&&g.Rods.Count==3&&!g.SecondNetActive&&g.State.Coins==0,"off restores rods at no charge");
            Check(g.ToggleSecondNetModule()&&g.Rods.Count==1&&g.State.Coins==0,"on again free");
            g.State.Save("Logs/module042/on.json");var loaded=GameState.Load("Logs/module042/on.json");
            Check(loaded.SecondNetActive&&loaded.SecondNetOwned,"owned/enabled survives save");
            g.ToggleSecondNetModule();g.State.Save("Logs/module042/off.json");loaded=GameState.Load("Logs/module042/off.json");
            Check(loaded.SecondNetOwned&&!loaded.SecondNetEnabled,"owned/off survives save");g.ToggleSecondNetModule();
            var temporary=g.State.ExtraCrew.First(c=>c.Role==CrewRole.Deckhand);temporary.Role=CrewRole.Fisherman;
            g.RequestDeparture();Check(g.ExcessFishermen==2&&!g.ConfirmDeparture(),"three fishermen / one rod warns about two idle crew");temporary.Role=CrewRole.Deckhand;
            g.RequestDeparture();g.PrepareInterface(844,390);Check(g.InvokeInterface("depart/go")&&g.CurrentMode==VoyageGame.Mode.Harbour,"finalgo intercepted for two fishers/one rod");
            g.PrepareInterface(844,390);Check(g.ExcessFishermen==1&&g.InvokeInterface("depart/crew-warning/back")&&g.CurrentMode==VoyageGame.Mode.Harbour,"back keeps harbour/crew unchanged");
            g.RequestDeparture();g.PrepareInterface(844,390);g.InvokeInterface("depart/go");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("depart/crew-warning/proceed")&&g.CurrentMode==VoyageGame.Mode.SailingOut,"explicit sailanyway proceeds");
            Check(!g.ToggleSecondNetModule(),"cannot switch gear underway");
            g.Showcase(0,0);
            var hands=new[]{g.Hand}.Concat(g.ExtraPeople).Where(p=>p.Contract.Role==CrewRole.Deckhand).ToArray();
            foreach(var h in hands){h.Stop();g.SetDeckhandWork(h.Contract,DeckhandWork.Nets);}
            g.State.NetInventory=3;
            Check(g.TryNetWork(hands[0]),"first hand sets primary");
            Check(g.TryNetWork(hands[1]),"second hand sets independent module");
            Work(hands[0]);Work(hands[1]);
            Check(g.Net==VoyageGame.NetState.Soaking&&g.SecondNet==VoyageGame.NetState.Soaking,"two simultaneous soaks");
            Check(!g.ToggleSecondNetModule(),"at-sea toggle cannot discard deployed net");
            Call(g,"TickNet",GameData.ShallowNetSoakSeconds);Call(g,"TickSecondNet",7f);
            Check(g.Net==VoyageGame.NetState.Ready&&g.SecondNet==VoyageGame.NetState.Soaking&&Math.Abs(g.SecondNetRemaining-(GameData.ShallowNetSoakSeconds-7f))<.01,"timers independent");
            float primary=g.NetCatchKg;Call(g,"TickSecondNet",GameData.ShallowNetSoakSeconds-7f);
            Check(g.SecondNet==VoyageGame.NetState.Ready&&g.SecondNetCatchKg>0&&g.SecondNetCatchKg<=g.State.NetCapacityKg+.001&&g.NetCatchKg==primary,"secondary rolls own weight while retaining exact primary catch");
            g.State.Rng=new System.Random(0);
            Check(g.TryNetWork(hands[0]),"primary starts haul");Work(hands[0]);
            Check(g.Net==VoyageGame.NetState.Stowed&&g.SecondNet==VoyageGame.NetState.Ready&&g.SecondNetCatchKg>0,"primary reset never discards secondary");
            // Finish first unloading batch before starting the other haul.
            for(int i=0;i<5000&&g.NetUnloadActive;i++){Call(g,"TickNetUnload",.02f);hands[0].Tick(.02f, Quaternion.identity);Call(g,"TickDeckFish",.02f);}
            Check(g.NetBasketCount==0&&g.ProcessingInput.Count>0,"first haul safely delivered to processing input");
            g.State.Rng=new System.Random(0);
            Check(g.TryNetWork(hands[1]),"other hand hauls secondary");Work(hands[1]);
            Check(g.SecondNet==VoyageGame.NetState.Stowed&&g.NetBasketCount>0,"second real catch delivered to basket");
            g.HeadHome();Check(g.AllNetsStowed,"return clears both rigs");
            for(int i=0;i<1800&&g.CurrentMode!=VoyageGame.Mode.Harbour;i++)g.Tick(.05f);
            g.State.UnsoldCatch.Clear();g.ToggleSecondNetModule();
            g.RequestDeparture();Check(g.ExcessFishermen==0&&g.ConfirmDeparture(),"three rods / two fishers no warning");
            // Scarce equipment cannot be deployed twice simultaneously.
            g.Showcase(-1,0);g.ToggleSecondNetModule();g.Showcase(0,0);g.State.NetInventory=1;
            hands=new[]{g.Hand}.Concat(g.ExtraPeople).Where(p=>p.Contract.Role==CrewRole.Deckhand).ToArray();
            foreach(var h in hands){h.Stop();g.SetDeckhandWork(h.Contract,DeckhandWork.Nets);}
            Check(g.TryNetWork(hands[0])&&!g.TryNetWork(hands[1]),"one physical net stock cannot fill two rigs");
            g.HeadHome();
            // The captain's second-net game survives the first hand finishing a haul.
            g.Cooler.Clear();g.Showcase(0,0);g.State.NetInventory=3;
            foreach(var h in hands)h.Stop();
            Check(g.TryNetWork(hands[0]),"set primary for independent manual test");Work(hands[0]);Call(g,"TickNet",GameData.ShallowNetSoakSeconds);
            Check(g.CaptainSecondNetAction(),"captain approaches second module");g.CancelNetHaulGame();
            Check(g.SecondNet==VoyageGame.NetState.Stowed&&g.Net==VoyageGame.NetState.Ready,"cancel during module approach preserves primary catch");
            Check(g.CaptainSecondNetAction(),"captain can retry secondary with primary ready");
            for(int i=0;i<3000&&!g.NetGameActive;i++)g.Captain.Tick(.02f, Quaternion.identity);
            Check(g.NetGameActive&&g.SecondNet==VoyageGame.NetState.Setting,"secondary has actual captain timing game");
            g.State.Rng=new System.Random(0);Check(g.TryNetWork(hands[0]),"hand hauls other net while captain works module");Work(hands[0]);
            Check(g.NetGameActive&&g.SecondNet==VoyageGame.NetState.Setting,"primary completion leaves captain secondary game intact");
            for(int i=0;i<3000&&g.NetGameActive;i++)
            {
                if(g.NetGamePhase>=.4f&&g.NetGamePhase<=.55f)g.TapNetGame();
                Call(g,"TickNet",.02f);Call(g,"TickSecondNet",.02f);
            }
            Check(g.SecondNet==VoyageGame.NetState.Soaking&&!g.NetGameActive,"three clean captain casts launch second net");
            g.HeadHome();
            g.Cooler.Clear();g.Showcase(-1,0);g.State.SelectedNet=NetKind.Deep;g.State.DeepNetUses.Clear();g.State.DeepNetUses.AddRange(new[]{3,3});g.Showcase(0,0);
            foreach(var h in hands)h.Stop();
            Check(g.TryNetWork(hands[0])&&g.TryNetWork(hands[1]),"two owned deep nets equip both modules");Work(hands[0]);Work(hands[1]);
            Call(g,"TickNet",GameData.DeepNetSoakSeconds);Call(g,"TickSecondNet",GameData.DeepNetSoakSeconds);float primaryDeep=g.NetCatchKg;
            Check(g.SecondNetCatchKg>0&&g.SecondNetCatchKg<=g.State.NetCapacityKg+.001f,"second deep net respects hard weight capacity");
            g.State.Rng=new FailedHaul();Check((bool)Call(g,"StartSecondNet",hands[1],true),"start second deep recovery");Work(hands[1]);
            Check(g.State.DeepNetUses.Sum()==5&&g.Net==VoyageGame.NetState.Ready&&g.NetCatchKg==primaryDeep,"second deep failure spends one use and keeps exact other catch");
            g.HeadHome();
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] MODULE042 CHECKS PASSED");Debug.Log("[Catchline] Snapshot written to Logs/module042");
        }
        public static void Run(){RunCore();NetHaulChecks.Run();}
        public static void ValidateAndBuild(){Run();PrepFisherChecks.BuildPreview();}
        public static void BuildPreview(){NetHaulChecks.Run();PrepFisherChecks.BuildPreview();}
    }
}
