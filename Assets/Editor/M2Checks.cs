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
            Check(state.Roster.Count==5 && state.Deployment.SequenceEqual(new[]{"mira"}),"grants and fixed navigator");
            Check(!state.DeployCard("mira",false),"cannot stand navigator down");
            Check(state.DeployCard("noor",true) && state.DeployCard("sam",true),"deploy owned cards");
            Check(!state.DeployCard("dirk",true),"berth limit");
            state.Tokens=23;
            Check(state.LevelUpCardToCap("noor")==4 && state.Tokens==0 && CardRoster.Find(state.Roster,"noor").AtCap,"level to cap spends tokens");
            Check(!state.RankUpCard("noor"),"rank up needs a blueprint");
            Check(state.SetFocus("noor") && state.FocusCard=="noor" && !state.SetFocus("olaf"),"focus an owned card");
            // Tools on the state: class rules, slots, rod tier, merge keeps the slot.
            var rod=state.AddTool(ToolKind.Rod,CardRarity.Gold); var rod2=state.AddTool(ToolKind.Rod,CardRarity.Gold);
            var compass=state.AddTool(ToolKind.Compass,CardRarity.White); var gloves=state.AddTool(ToolKind.Gloves,CardRarity.White); var gloves2=state.AddTool(ToolKind.Gloves,CardRarity.White);
            Check(state.RodTier==0 && state.EquipTool(GameState.CaptainToolOwner,0,rod.Uid) && state.RodTier==2 && Mathf.Approximately(state.BiteWindow,1.4f),"captain's Gold rod gives carbon rods");
            Check(!state.EquipTool(GameState.CaptainToolOwner,1,compass.Uid) && state.EquipTool("mira",0,compass.Uid),"navigator tools only for the navigator");
            Check(state.EquipTool("noor",0,gloves.Uid) && !state.EquipTool("noor",1,gloves2.Uid),"White has one slot");
            Check(Mathf.Approximately(state.ToolBonus("noor",ToolKind.Gloves),.03f) && state.ToolOwner(gloves.Uid)=="noor","tool bonus and owner");
            Check(state.MergeTools(gloves.Uid,gloves2.Uid) && gloves.Rarity==CardRarity.Green && state.ToolOwner(gloves.Uid)=="noor" && state.FindTool(gloves2.Uid)==null,"merge keeps the equipped tool");
            Check(state.EquipTool("noor",0,rod2.Uid)==false,"deckhand cannot hold a rod");
            // Chests and tokens.
            int coinsBefore=state.Coins;
            Check(state.BuyChest(ChestKind.SeaChest) && state.Coins==coinsBefore-state.ChestPrice(ChestKind.SeaChest) && !state.BuyChest(ChestKind.CaptainsChest),"buy a sea chest, not a captain's chest");
            int toolsBefore=state.Tools.Count;
            var opened=state.OpenChest(ChestKind.SeaChest);
            Check(opened!=null && state.Tokens==opened.Tokens && state.Tools.Count==toolsBefore+2 && state.PendingChests.Count==0 && state.OpenChest(ChestKind.SeaChest)==null,"open banks the chest once");
            Check(state.GrantDailyCrate(new DateTime(2026,10,25)) && !state.GrantDailyCrate(new DateTime(2026,10,25,23,0,0)) && state.GrantDailyCrate(new DateTime(2026,10,26)),"one first-sale crate per day");
            Check(state.PendingChestCount(ChestKind.Crate)==2,"daily crates pending");
            Check(state.ClaimRenown(1,"noor") && CardRoster.Find(state.Roster,"noor").Blueprints>=1 && !state.ClaimRenown(1,"noor"),"renown milestone 1: blueprint of choice, once");
            Check(state.RankUpCard("noor") && CardRoster.Find(state.Roster,"noor").Rarity==CardRarity.Green,"rank Noor to Green");
            int wages=state.DepartureWages; int before=state.Coins;
            Check(state.PayDepartureWages() && state.Coins==before-wages && state.TripDeployment.Count==3,"departure charge, trip crew fixed");
            state.DeployCard("sam",false);
            int t0=state.Tokens; float cap=state.CoolerCapacity;
            Check(state.AwardHaulTokens(cap)==CardProgression.HaulTokens(2,3,1f) && state.Tokens==t0+6 && state.TripDeployment.Count==0,"haul tokens count the trip crew: 2 x 3 x 1.15 = 6");
            state.Bait=83; state.Fuel=6; state.UnsoldCatch.Add(new CaughtFish{Species=Species.Cod,Kg=4,ValueBonus=.1f});
            state.TripDeployment.Add("noor");
            string path=Path.Combine(Path.GetTempPath(),"catchline-m2-"+Guid.NewGuid()+".json");
            try
            {
                state.Save(path); var loaded=GameState.Load(path);
                Check(loaded!=null && loaded.Coins==state.Coins && loaded.Bait==83 && loaded.Fuel==6 && loaded.UnsoldCatch.Count==1 && Mathf.Approximately(loaded.UnsoldCatch[0].ValueBonus,.1f),"runtime v3 harbour roundtrip");
                Check(loaded.Deployment.SequenceEqual(state.Deployment) && loaded.Roster.Count==5 && loaded.TripDeployment.SequenceEqual(new[]{"noor"}),"v3 roster/manifest roundtrip");
                Check(loaded.Tokens==state.Tokens && loaded.Tools.Count==state.Tools.Count && loaded.RodTier==2 && loaded.FocusCard=="noor" && loaded.PendingChests.Count==2
                    && loaded.RenownClaimed==1 && loaded.ToolOwner(gloves.Uid)=="noor" && loaded.NextToolUid==state.NextToolUid,"v3 card economy roundtrip");
                Check(CardRoster.Find(loaded.Roster,"noor").Rarity==CardRarity.Green && CardRoster.Find(loaded.Roster,"noor").Level==5,"v3 rarity and level");
            }
            finally { if(File.Exists(path)) File.Delete(path); }
            Abilities(); LiveWages();
            Debug.Log("[Catchline] M2 CHECKS PASSED");
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
            // Noor's and Sam's v2 abilities are timed or conditional: the ability engine suite checks them.
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
            Check(g.CurrentMode==VoyageGame.Mode.Harbour && g.State.UnsoldCatch.Count>0 && g.State.TripDeployment.Count==2,"return keeps the haul and trip crew");
            int crates=g.State.PendingChests.Count;
            Check(g.SellHaul() && g.State.TripDeployment.Count==0 && g.State.PendingChests.Count>=crates,"sale pays tokens to the trip crew");
            Check(!g.SellHaul(),"cannot sell or award twice");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
        }
    }
}
