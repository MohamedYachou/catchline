using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class HandlingPaceChecks
    {
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string why) { if (!ok) throw new Exception("PACE036: " + why); }
        static void Call(VoyageGame g, string n, params object[] a) => typeof(VoyageGame).GetMethod(n,H).Invoke(g,a);
        static float Until(Person p, Func<bool> done)
        {
            float t = 0;
            for (; t < 30 && !done(); t += .002f) p.Tick(.002f,1,Quaternion.identity);
            Check(done(), "action completes"); return t;
        }
        static void Work(Person p) => Until(p, () => p.Idle);
        static void Still(Person h, Vector3 pos)
        {
            var now = h.Root.localPosition;
            Check(!h.Walking && !h.Loitering && Vector2.Distance(new Vector2(now.x,now.z),new Vector2(pos.x,pos.z)) < .001f,
                "prep hand stays planted during work / empty input / refill");
        }
        public static void Run()
        {
            Directory.CreateDirectory("Logs/pace036"); ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g = new GameObject("PACE036 isolated check").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();
            Check(g.StartPrepBoatTrial(), "trial starts");
            var hands = new[]{g.Hand}.Concat(g.ExtraPeople).Where(p=>p.Contract.Role==CrewRole.Deckhand).ToArray();
            var carrier=hands[0]; carrier.Stop();carrier.Speed=1;
            g.LandFish(g.Rods[0],Species.Herring,.2f);
            var fish=g.OnDeck.Single();carrier.Place(fish.Tile);Call(g,"Fetch",carrier,fish);
            float pickup=Until(carrier,()=>carrier.Carrying!=null);
            Check(pickup<=GameData.CompactPickupTime/3f+.01f,"actual delivery hand pickup at least3xfaster");
            carrier.Place(g.PrepWorkerTiles[0]);Call(g,"Stow",carrier);
            float release=Until(carrier,()=>carrier.Carrying==null);
            Check(release<=GameData.CompactStowTime/3f+.01f && g.ProcessingInput.Count==1,"actual release3xfaster and fish safely stored");
            Check(VoyageGame.FishHandlingSeconds(g.Captain,GameData.CompactStowTime)==GameData.CompactStowTime,"captain timing preserved");
            Debug.Log($"[Catchline] PACE036 measured grade1 actions: pickup={pickup:0.000}s release={release:0.000}s (previous1.4s/3s, same pace multiplier)");
            foreach(var h in hands) { h.Stop();h.Speed=1;g.SetDeckhandWork(h.Contract,DeckhandWork.Prep); }
            g.Cooler.Clear();Call(g,"ClearProcessingPipeline",false);g.State.Chum=0;
            // Empty input: walk once to distinct assigned positions, then stay there.
            foreach(var h in hands) { Call(g,"HandThink",h); Work(h);h.Tick(0,1,Quaternion.identity); }
            Check(hands[0].Tile!=hands[1].Tile,"distinct permanent work positions");
            var positions=hands.Select(h=>h.Root.localPosition).ToArray();
            for(int n=0;n<400;n++) for(int i=0;i<2;i++) { Call(g,"HandThink",hands[i]);hands[i].Tick(.02f,1,Quaternion.identity);Still(hands[i],positions[i]); }
            for(int n=0;n<24;n++) g.DeliverCatch(new CaughtFish{Species=Species.Herring,Kg=.2f,StowedAt=g.SimTime});
            bool take=false,cut=false,put=false;
            for(int n=0;n<4000 && (g.ProcessingInput.Any(f=>!f.Prepared)||g.PrepWorkersActive>0);n++)
                for(int i=0;i<2;i++)
                {
                    var h=hands[i]; if(h.Idle)Call(g,"HandThink",h);
                    h.Tick(.02f,1,Quaternion.identity);Still(h,positions[i]);
                    take |= h.BusyLabel=="Taking fish";cut |= h.BusyLabel is "Making chum" or "Preparing fish";put |= h.BusyLabel=="Putting fish away";
                }
            Check(take&&cut&&put,"real take / cut / place phases run without a walk");
            Check(g.State.Chum==10 && g.ProcessingOutput.Count==14 && g.ProcessingOutput.All(f=>f.Prepared),"stationary crew fill ten then prepare remainder");
            g.State.TakeBait(out _,out _);g.DeliverCatch(new CaughtFish{Species=Species.Herring,Kg=.2f,StowedAt=g.SimTime});
            Call(g,"HandThink",hands[1]);
            Check(!hands[1].Walking && hands[1].Busy,"refill starts immediately at same standing position");
            while(!hands[1].Idle){hands[1].Tick(.02f,1,Quaternion.identity);Still(hands[1],positions[1]);}
            Check(g.State.Chum==10,"stationary refill completes");
            // Releasing the other station must not move the remaining worker.
            g.SetDeckhandWork(hands[0].Contract,DeckhandWork.Fish);
            g.DeliverCatch(new CaughtFish{Species=Species.Cod,Kg=5,StowedAt=g.SimTime});
            Call(g,"HandThink",hands[1]);Check(!hands[1].Walking,"remaining prep hand keeps own slot when other leaves");Work(hands[1]);Still(hands[1],positions[1]);
            Check(g.ProcessingInput.Count==0 && g.ProcessingOutput.All(f=>f.Prepared) && g.ProcessingOutput.All(f=>g.State.Freshness(f,999999)==1),"prepared no-spoil preserved");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            PrepOrdersChecks.Run();
            Debug.Log("[Catchline] PACE036 CHECKS PASSED");
            Debug.Log("[Catchline] Snapshot written to Logs/pace036");
        }
        public static void ValidateAndBuild(){Run();PrepFisherChecks.BuildPreview();}
    }
}
