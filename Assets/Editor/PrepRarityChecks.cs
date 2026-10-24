using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace Catchline.EditorTools
{
    public static class PrepRarityChecks
    {
        const BindingFlags H=BindingFlags.Instance|BindingFlags.NonPublic;
        static void Check(bool ok,string why){if(!ok)throw new Exception("PREP047: "+why);}
        static object Call(VoyageGame g,string name,params object[] args)=>typeof(VoyageGame).GetMethod(name,H).Invoke(g,args);
        static void Work(Person p){for(int n=0;n<5000&&!p.Idle;n++)p.Tick(.02f, Quaternion.identity);Check(p.Idle,"worker action completed");}
        static Person[] Hands(VoyageGame g)=>new[]{g.Hand}.Concat(g.ExtraPeople).Where(p=>p.Contract.Role==CrewRole.Deckhand).ToArray();
        public static void Run()
        {
            Directory.CreateDirectory("Logs/prep047");ArtImport.BuildLibrary();
            var old=JsonUtility.FromJson<PrepOrderSettings>("{\"ChumMaxKg\":2,\"PrepareMinKg\":3}");
            Check(old.ChumClasses==1,"legacy filters migrate to safe rarity defaults");
            var depleted=new GameState(4703);
            for(int spot=0;spot<GameData.Spots.Length;spot++)
            {
                depleted.Richness[spot]=.3f;
                for(int sample=0;sample<20;sample++)Check(depleted.RollBiteWait(spot,1f)<=GameData.MaxBiteWait,"depleted-ground bite wait stays within15seconds");
            }
            Check(Mathf.Approximately(depleted.RollBiteWait(GameData.Spots.Length-1,1f),GameData.MaxBiteWait),"depleted deep-water bite wait is capped at15seconds");
            var samples=new[]{new CaughtFish{Species=Species.Herring,Kg=.2f},new CaughtFish{Species=Species.Herring,Kg=GameData.Get(Species.Herring).MaxKg},new CaughtFish{Species=Species.Conger,Kg=1},new CaughtFish{Species=Species.Conger,Kg=GameData.Get(Species.Conger).MaxKg},new CaughtFish{Species=Species.GoldTipShark,Kg=1},new CaughtFish{Species=Species.GiantSquid,Kg=1}};
            for(int c=0;c<6;c++)
            {
                Check((int)CatchPresentation.Tier(samples[c].Species,samples[c].Kg)==c,"six actual catch classes in order");
                var o=new PrepOrderSettings{HasClassFilters=true,ChumClassMask=1<<c,ChumMaxKg=.001f};
                for(int j=0;j<6;j++)Check(o.Allows(samples[j],true)==(c==j && c<3)&&o.Allows(samples[j],false),"exact chum classes, no hidden kg/value gate; sorting takes any class");
            }
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("PREP047 isolated").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();Check(g.StartPrepBoatTrial(),"trial");
            var hands=Hands(g);foreach(var h in hands){h.Stop();g.SetDeckhandWork(h.Contract,DeckhandWork.Prep);}
            g.State.PrepOrders.HasClassFilters=true;g.State.PrepOrders.ChumClassMask=0;
            g.DeliverCatch(samples[0]);Check(g.TryPrepWork(hands[0])&&g.ChumBeingMade==0,"all-off chum sorts instead of chumming");hands[0].Stop();
            g.PrepareInterface(844,390);Check(g.InvokeInterface("prep/open"),"open table");g.PrepareInterface(844,390);
            Check(!g.InvokeInterface("prep/worker/0")&&!g.InvokeInterface("prep/input")&&!g.InvokeInterface("prep/minimum")&&!g.InvokeInterface("prep/priority"),"prep table excludes worker, weight and priority controls");
            Check(g.InvokeInterface("prep/close"),"close prep table");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("net/orders"),"open crew duties");g.PrepareInterface(844,390);
            bool priority=g.State.PrepOrders.ChumFirst;
            Check(g.InvokeInterface("net/orders/prep-priority"),"prep work order appears in crew duties");
            Check(g.State.PrepOrders.ChumFirst!=priority,"crew duties changes saved prep work order");
            Check(g.InvokeInterface("net/orders/close"),"close crew duties");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("prep/open"),"reopen prep table");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("prep/chum/classes"),"chum dropdown opens");g.PrepareInterface(844,390);
            Check(g.InvokeInterface("prep/classes/chum/0"),"select actual Common row");g.PrepareInterface(844,390);Check(g.InvokeInterface("prep/classes/chum/done"),"close dropdown");
            Check(g.State.PrepOrders.ChumClasses==1,"chum choice independent");g.State.PrepOrders.ChumFirst=true;
            Check(g.TryPrepWork(hands[0]),"selected fish is processed");Work(hands[0]);Check(g.State.Chum==1&&!g.ProcessingInput.Contains(samples[0]),"chum consumes selected fish");
            var purple=samples[3];g.DeliverCatch(purple);
            Check(g.TryPrepWork(hands[1]),"unchummable purple is sorted");Work(hands[1]);Check(g.ProcessingOutput.Contains(purple)&&g.State.Chum==1,"sorting retains the fish and makes no by-product");
            g.State.Save("Logs/prep047/classes.json");var saved=GameState.Load("Logs/prep047/classes.json");Check(saved.PrepOrders.ChumClasses==1,"independent selections persist");
            Call(g,"ClearPrepWork");g.Cooler.Clear();Call(g,"ClearProcessingPipeline",false);g.Showcase(-1,0);g.State.SecondNetOwned=true;g.State.SecondNetEnabled=true;
            Call(g,"RebuildBoat",true);g.Showcase(0,0);hands=Hands(g);
            foreach(var h in hands){h.Stop();g.SetDeckhandWork(h.Contract,DeckhandWork.Nets);}
            g.State.NetInventory=3;Check(g.TryNetWork(hands[0])&&g.TryNetWork(hands[1]),"each sets own net");Work(hands[0]);Work(hands[1]);
            Check(g.AssignedNet(hands[0])==0&&g.AssignedNet(hands[1])==1,"stable distinct rig assignment");
            Call(g,"TickSecondNet",GameData.ShallowNetSoakSeconds);Check(g.SecondNet==VoyageGame.NetState.Ready&&g.Net==VoyageGame.NetState.Soaking,"only net2 ready");
            Check(!g.TryNetWork(hands[0])&&g.SecondNet==VoyageGame.NetState.Ready,"net1 worker never switches to ready net2");
            g.State.Rng=new System.Random(0);Check(g.TryNetWork(hands[1]),"net2 worker hauls own net");Work(hands[1]);
            var tile=(Vector2Int)typeof(VoyageGame).GetProperty("SecondNetAccess",H).GetValue(g);
            var primary=(Vector2Int)typeof(VoyageGame).GetProperty("NetAccess",H).GetValue(g);
            var catchFish=g.OnDeck.Where(f=>f.FromNetBasket).ToArray();Check(catchFish.Length>1&&catchFish.All(f=>f.Tile==tile&&f.Tile!=primary),"entire net2 catch stays at net2");
            Check(g.NetUnloadRig==1,"unloading status belongs to net2");
            Call(g,"TickDeckFish",.5f);var net2Deck=g.Grid.GetLocal(tile);Check(catchFish.All(f=>Vector3.Distance(f.Root.localPosition,f.RestPos)<.001f&&Vector2.Distance(new Vector2(f.RestPos.x,f.RestPos.z),new Vector2(net2Deck.x,net2Deck.z))<.8f),"drop settles beside net2, no teleport to net1");
            int stored=g.ProcessingInput.Count;bool batch=false;int gather=0,stow=0;string prev="";
            for(int n=0;n<5000&&g.NetUnloadActive;n++)
            {
                if(hands[0].Idle||hands[0].Loitering)Call(g,"HandThink",hands[0]);
                Call(g,"TickNetUnload",.02f);hands[0].Tick(.02f, Quaternion.identity);hands[1].Tick(.02f, Quaternion.identity);Call(g,"TickDeckFish",.02f);
                Check(hands[0].Carrying==null&&hands[1].Carrying==null,"no individual fish trips or stealing");
                batch|=hands[1].CarryingBatch;
                string label=hands[1].BusyLabel;if(label!=prev){if(label=="Gathering net catch")gather++;if(label=="Stowing net catch")stow++;prev=label;}
            }
            Check(batch&&gather==1&&stow==1&&g.ProcessingInput.Count==stored+catchFish.Length&&g.NetBasketCount==0,"whole net2 catch in one gather/carry/stow cycle");
            Check(g.NetUnloadRig==-1,"unloading status clears on storage");
            Check(g.AssignedNet(hands[0])==0&&g.AssignedNet(hands[1])==1,"ownership survives unload");
            Check(g.TryNetWork(hands[1]),"net2 worker resets own rig");Work(hands[1]);Call(g,"TickNet",GameData.ShallowNetSoakSeconds);
            Check(!g.TryNetWork(hands[1])&&g.Net==VoyageGame.NetState.Ready,"net2 worker never takes ready net1");
            g.HeadHome();UnityEngine.Object.DestroyImmediate(g.gameObject);
            Debug.Log("[Catchline] PREP047 CHECKS PASSED");
            Debug.Log("[Catchline] Snapshot written to Logs/prep047");
        }
        public static void ValidateAndBuild(){Run();Balance045Checks.Run();CrewCounterChecks.ValidateAndBuild();}
    }
}
