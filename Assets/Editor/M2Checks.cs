using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using Catchline.Game.Deck;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace Catchline.EditorTools
{
    public static class M2Checks
    {
        static void Check(bool ok,string text) { if (!ok) throw new Exception("M2: "+text); }
        sealed class Actor : IDeckActor
        {
            public Vector2Int Tile { get; set; }
            Action next;
            public bool WalkTo(Vector2Int tile,Action done,Action cancel) { next=()=>{ Tile=tile; done(); }; return true; }
            public void Act(string label,float seconds,Action done,Action cancel) { next=done; }
            public void Stop() { next=null; }
            public void Step() { var n=next; next=null; n?.Invoke(); }
        }
        public static void Run()
        {
            ArtImport.BuildLibrary(); M2DataChecks.Run();
            var state=new GameState(42) { Hull=2,Coins=10000 };
            state.EnsureCards();
            Check(state.Roster.Count==4 && state.Deployment.SequenceEqual(new[]{"mira"}),"grants and fixed navigator");
            Check(!state.DeployCard("mira",false),"cannot stand navigator down");
            Check(state.DeployCard("noor",true) && state.DeployCard("sam",true),"deploy owned cards");
            Check(!state.DeployCard("dirk",true),"berth limit");
            state.Wildcards[(int)CardRole.Deckhand]=10;
            Check(state.UpgradeCard("sam") && CardRoster.Find(state.Roster,"sam").Rarity==CardRarity.Purple,"runtime rarity purchase");
            int before=state.Coins,wages=state.DepartureWages;
            Check(state.PayDepartureWages() && state.Coins==before-wages,"departure charge");
            state.PendingXpKg=113;
            state.DeployCard("sam",false); state.DeployCard("dirk",true);
            state.AwardSaleXp(); state.AwardSaleXp();
            Check(CardRoster.Find(state.Roster,"sam").Xp==113 && CardRoster.Find(state.Roster,"sam").Level==3 && CardRoster.Find(state.Roster,"dirk").Xp==0,"manifest XP once, includes stood-down card, excludes replacement");
            state.PendingXpKg=7; state.TripDeployment.Add("noor");
            state.Bait=83; state.Fuel=6; state.UnsoldCatch.Add(new CaughtFish{Species=Species.Cod,Kg=4});
            string path=Path.Combine(Path.GetTempPath(),"catchline-m2-"+Guid.NewGuid()+".json");
            try
            {
                state.Save(path); var loaded=GameState.Load(path);
                Check(loaded!=null && loaded.Coins==state.Coins && loaded.Bait==83 && loaded.Fuel==6 && loaded.UnsoldCatch.Count==1,"runtime v2 harbour roundtrip");
                Check(loaded.Deployment.SequenceEqual(state.Deployment) && loaded.Roster.Count==4 && loaded.PendingXpKg==7 && loaded.TripDeployment.SequenceEqual(new[]{"noor"}),"v2 roster/manifest roundtrip");
                Check(CardRoster.Find(loaded.Roster,"sam").Rarity==CardRarity.Purple && CardRoster.Find(loaded.Roster,"sam").Xp==113,"v2 rarity XP");
            }
            finally { if(File.Exists(path)) File.Delete(path); }
            Abilities(); LiveWages();
            Debug.Log("[Catchline] M2 CHECKS PASSED (tier-5 berth ambiguity intentionally skipped)");
        }
        static void Abilities()
        {
            var deck=DeckGraph.Load(GameData.Hulls[2]); var sched=new DeckScheduler(deck);
            var a=new Actor {Tile=deck.Access(deck.Hold)};
            var sam=new Worker {Name="Sam",Role=CrewRole.Deckhand,Card=new CardState("sam"),Actor=a};
            sched.Workers.Add(sam);
            sched.Land(deck.OfKind(StationKind.Rod).First(),new CaughtFish {Species=Species.Cod,Kg=20});
            Check(sched.Pick(sam)==null,"blue Sam cannot lift 20kg solo");
            sam.Card.Rarity=CardRarity.Gold;
            sched.Tick(); Check(sam.Current?.Fish.Single().Kg==20,"gold Sam claims 20kg solo");
            for(int i=0;i<8;i++)a.Step();
            Check(sched.Stowed==1 && sched.Balanced,"gold Sam delivers 20kg solo");
            deck=DeckGraph.Load(GameData.Hulls[2]);sched=new DeckScheduler(deck);
            var sort=deck.OfKind(StationKind.SortTable).First();
            for(int i=0;i<4;i++) sort.In.Put(new CaughtFish{Species=Species.Mackerel,Kg=.8f},false);
            sched.Landed=4;
            var noor=new Worker {Role=CrewRole.Deckhand,Card=new CardState("noor"){Rarity=CardRarity.Gold},Primary=Duty.Sort,Actor=a};
            sched.Workers.Add(noor);sched.Tick();
            Check(noor.Current?.Fish.Count==4,"Noor whole basket one job");
            for(int i=0;i<3;i++)a.Step();
            Check(sort.Out.Count==4 && noor.Idle && sched.Balanced,"Noor whole basket finishes losslessly");
            var source=deck.OfKind(StationKind.Rod).First().Out;
            var target=new Drop{Hold=true,Station=deck.Hold};
            sam.Card.Rarity=CardRarity.Purple; sam.Current=new Job{Kind=JobKind.Haul,Source=source,Target=target};
            var other=new Worker{Role=CrewRole.Deckhand,Current=new Job{Kind=JobKind.Haul,Source=source,Target=target}};
            sched.Workers.Clear();sched.Workers.Add(sam);sched.Workers.Add(other);
            Check(Mathf.Approximately(sched.HaulWalkMultiplier(sam),1.3f) && Mathf.Approximately(sched.HaulWalkMultiplier(other),1.3f),"Sam purple bonus both haulers");
            other.Current.Source=sort.Out;
            Check(sched.HaulWalkMultiplier(sam)==1 && sched.HaulWalkMultiplier(other)==1,"different route no bonus");
        }
        static void LiveWages()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var g=new GameObject("M2 live voyage").AddComponent<VoyageGame>();g.SessionOnly=true;g.Build();
            g.State.Hull=1;g.State.Coins=100;g.State.Fuel=10;
            typeof(VoyageGame).GetMethod("RebuildBoat",System.Reflection.BindingFlags.Instance|System.Reflection.BindingFlags.NonPublic).Invoke(g,new object[]{false});
            Check(g.DeployCard("noor",true),"live deploy");
            int wage=g.State.DepartureWages,coins=g.State.Coins;
            g.State.Coins=0;g.SetSail();Check(g.CurrentMode==VoyageGame.Mode.Harbour,"unaffordable wages block departure");
            g.State.Coins=coins;g.SetSail();g.SetSail();
            Check(g.CurrentMode==VoyageGame.Mode.SailingOut && g.State.Coins==coins-wage,"live charge once");
            Check(!g.DeployCard("noor",false),"cannot redeploy at sea");
            for(float t=0;t<120 && g.CurrentMode!=VoyageGame.Mode.Fishing;t+=.05f)g.Tick(.05f);
            g.LandFish(g.Rods[0],Species.Mackerel,.8f);
            g.HeadHome();
            for(float t=0;t<120 && g.CurrentMode!=VoyageGame.Mode.Harbour;t+=.05f)g.Tick(.05f);
            Check(g.CurrentMode==VoyageGame.Mode.Harbour && g.State.PendingXpKg>=.8f,"return retains landed XP");
            Check(g.SellHaul() && CardRoster.Find(g.State.Roster,"noor").Xp>=.8f,"sale awards live XP");
            Check(!g.SellHaul(),"cannot sell or award twice");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
    }
}
