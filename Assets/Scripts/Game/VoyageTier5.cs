using System;
using System.Linq;
using System.Collections.Generic;
using Catchline.Prototype;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public bool IsTier5 => State != null && State.Hull == 4;
        Vector2Int[] buoyTiles = Array.Empty<Vector2Int>();
        Vector3[] buoyAnchors = Array.Empty<Vector3>();
        readonly float[] buoyTimers = new float[2];
        readonly Person[] buoyWorkers = new Person[2];
        Transform[] buoyModels = new Transform[2];
        bool tier5OperationsOpen;
        public int BuoyHauls { get; private set; }
        public float BuoySoakSeconds => 65f;
        public Vector3 PrepSurfaceLocal => IsTier5 ? new Vector3(4.5f,.7f,1.7f) : new Vector3(3.6f,.6f,1.4f);
        Vector3 PrepInputLocal => new(3.775f,.5f,1.7f);
        Vector3 PreparedOutputLocal => new(6.15f,.5f,1.7f);
        public Vector2Int[] BuoyWorkerTiles => buoyTiles;
        public float BuoyRemaining(int i) => Mathf.Max(0,BuoySoakSeconds-buoyTimers[i]);

        void ConfigureTier5(GameObject model)
        {
            ConfigureDeepLines(model);
            var module = ArtLibrary.Find(model,"NetModule2");
            if (module != null) module.gameObject.SetActive(SecondNetActive);
            for(int i=3;i<=4;i++)
            {
                var holder=ArtLibrary.Find(model,"RodHolder_"+i);if(holder!=null)holder.gameObject.SetActive(!SecondNetActive);
            }
            buoyTiles = new[]{"BuoyAccess_1","BuoyAccess_2"}.Select(n=>Grid.GetTile(Boat.InverseTransformPoint(ArtLibrary.Find(model,n).position))).ToArray();
            buoyAnchors = new[]{"BuoyAnchor_1","BuoyAnchor_2"}.Select(n=>Boat.InverseTransformPoint(ArtLibrary.Find(model,n).position)).ToArray();
            for(int i=0;i<2;i++){buoyTimers[i]=0;buoyWorkers[i]=null;}
            tier5OperationsOpen=false;
        }
        public bool RefitTier5()
        {
            if(CurrentMode!=Mode.Harbour || !State.RefitTier5())return false;
            RebuildBoat(false);SaveGame();Toast("Buoy fisher ready — six crew berths and both equipment layouts.");return true;
        }
        public bool TrialTier5()
        {
            if(!SessionOnly || CurrentMode!=Mode.Harbour)return false;
            State.Hull=4;State.Fuel=State.FuelCapacity;State.SecondNetOwned=true;State.SecondNetEnabled=false;
            State.EnsureCrewRoleOffers();RebuildBoat(false);return true;
        }
        public bool StartTier5Trial()
        {
            if(!SessionOnly)return false;
            NewGame();if(!TrialTier5())return false;
            State.Coins=4000;State.Bait=100;
            foreach(var role in new[]{CrewRole.Deckhand,CrewRole.Deckhand,CrewRole.Fisherman,CrewRole.Fisherman,CrewRole.Fisherman,CrewRole.Deckhand})
            {State.EnsureCrewRoleOffers();State.Hire(State.Board.First(c=>c.Role==role));}
            State.Deckhand.WorkPreference=DeckhandWork.Prep;
            State.ExtraCrew.First(c=>c.Role==CrewRole.Deckhand).WorkPreference=DeckhandWork.Nets;
            var netFisher = State.Crew.First(c=>c.Role==CrewRole.Fisherman);
            netFisher.HasFisherTasks=true; netFisher.AllowedTasks=FisherTask.Nets;
            State.PrepOrders.ChumTarget=10;
            SyncCrew();showTitle=paused=panelOpen=captureFreeze=false;
            ActiveSpot=SelectedSpot=0;voyageStart=SimTime;Showcase(0,0);toastUntil=0;
            return true;
        }
        void BuildTier5Buoys()
        {
            var lib=ArtLibrary.Get();
            for(int i=0;i<2;i++)
            {
                var root=new GameObject("Working buoy "+(i+1)).transform;root.SetParent(Boat,false);root.localPosition=buoyAnchors[i];
                ArtLibrary.Spawn(lib?.M("Buoy"),root,Vector3.up*.02f,Quaternion.identity);
                ArtLibrary.Spawn(lib?.M("EmptyPot"),root,new Vector3(0,-.55f,0),Quaternion.identity);
                var lineObject=new GameObject("Buoy mooring");lineObject.transform.SetParent(root,false);var line=lineObject.AddComponent<LineRenderer>();
                line.sharedMaterial=Visuals.Mat(Palette.Hex("D1AF76"));line.startWidth=line.endWidth=.018f;
                line.useWorldSpace=false;line.positionCount=3;
                line.SetPositions(new[]{new Vector3(0,0,0),new Vector3(0,-.32f,0),new Vector3(0,-.55f,0)});
                buoyModels[i]=root;
            }
        }
        void TickTier5(float dt)
        {
            if(!IsTier5 || CurrentMode!=Mode.Fishing)return;
            TickDeepLines(dt);
            for(int i=0;i<2;i++)
            {
                buoyTimers[i]=Mathf.Min(BuoySoakSeconds,buoyTimers[i]+dt);
                if(buoyModels[i]!=null)buoyModels[i].localPosition=buoyAnchors[i]+Vector3.up*(Mathf.Sin(SimTime*1.2f+i)*.025f);
            }
        }
        public bool TryBuoyWork(Person p)
        {
            if(!IsTier5 || CurrentMode!=Mode.Fishing || !AtFishingGround || p==null || !p.Idle || p.Carrying!=null || HoldFull
                || !p.IsCaptain && p.Contract?.Role!=CrewRole.Fisherman)return false;
            int i=Enumerable.Range(0,2).Where(n=>buoyTimers[n]>=BuoySoakSeconds&&buoyWorkers[n]==null).DefaultIfEmpty(-1).First();
            if(i<0)return false;
            buoyWorkers[i]=p;
            void Cancel(){if(buoyWorkers[i]==p)buoyWorkers[i]=null;}
            void Finish()
            {
                if(buoyWorkers[i]!=p)return;
                if(HoldFull){Cancel();return;}
                float kg=Mathf.Lerp(.5f,1.8f,(float)State.Rng.NextDouble());
                var fish=new CaughtFish{Species=Species.Crab,Kg=kg,StowedAt=SimTime};
                // Recovery lands aboard. A real carrying job then delivers it to processing.
                var landed=new DeckFish{Species=fish.Species,Kg=kg,Tile=buoyTiles[i],CaughtAt=SimTime,CaughtByCrew=!p.IsCaptain};
                landed.Root=DeckFish.BuildModel(fish.Species,kg,Boat);landed.RestPos=Grid.GetLocal(buoyTiles[i])+new Vector3(.08f,.08f,.08f);landed.SpawnFrom=landed.RestPos+Vector3.up*.3f;landed.Root.localPosition=landed.SpawnFrom;
                OnDeck.Add(landed);RecordLanding(FlowTelemetry.Kind.Trap,fish.Species,kg);State.OnCatch(ActiveSpot,kg);Stats.Landed++;BuoyHauls++;buoyTimers[i]=0;ShowCatch(fish.Species,kg);
                Cancel();
            }
            if(!p.WalkTo(Grid,buoyTiles[i],()=>{p.FacePoint(buoyAnchors[i]);p.Do("Recovering buoy catch",2f,Finish,Cancel);},Cancel)){Cancel();return false;}
            return true;
        }
        void InterfaceTier5Processing()
        {
            Block(new Rect(0,0,iw,ih));
            coastalUi.Box("tier5/prep/shade",new Rect(0,0,iw,ih),"chip-dark",new Color(1,1,1,.7f));
            var r=new Rect((iw-480)/2,(ih-360)/2,480,360);coastalUi.Box("tier5/prep/panel",r,"popup-panel");
            coastalUi.Label("tier5/prep/title",new Rect(r.x+22,r.y+12,370,38),"Fish processing",26,Palette.Cream);
            IButton("prep/close",new Rect(r.xMax-66,r.y+8,50,48),"X",()=>PrepOrdersOpen=false,false);
            coastalUi.Label("tier5/prep/help",new Rect(r.x+24,r.y+74,432,62),"Fish are sorted and stowed at full value.\nSelling never changes the price.",19,SeaInk);
            coastalUi.Label("tier5/prep/workers",new Rect(r.x+24,r.y+222,432,48),$"{ProcessingInput.Count} incoming / {ProcessingOutput.Count} ready / {PrepWorkersActive} processing",17,SeaInk);
        }
        void InterfaceTier5Operations()
        {
            if(!IsTier5 || CurrentMode!=Mode.Fishing || !AtFishingGround || PrepOrdersOpen || netOrdersOpen || baitSettingsCrew!=null)return;
            // Separate small actions from the seven-person crewrail to keep phone viewusable.
            // UI v2: duties and processing orders are reached through the Crew and Ops pages.
            for(int i=0;i<2;i++)
            {
                int rig=i;bool ready=BuoyRemaining(i)<=0;
                InterfaceBubble("tier5/buoy/"+i,Boat.TransformPoint(buoyAnchors[i]+Vector3.up*.8f),ready?"Collect":""+Mathf.CeilToInt(BuoyRemaining(i))+"s","icon-fish",()=>TryBuoyWork(Captain),ready);
            }
            if(!tier5OperationsOpen)return;
            Block(new Rect(0,0,iw,ih));
            coastalUi.Box("tier5/equipment/shade",new Rect(0,0,iw,ih),"chip-dark",new Color(1,1,1,.7f));
            float w=560,h=470;var p=new Rect((iw-w)/2,(ih-h)/2,w,h);coastalUi.Box("tier5/equipment",p,"popup-panel");
            coastalUi.Label("tier5/equipment/title",new Rect(p.x+24,p.y+12,w-90,40),"Boat duties",26,Palette.Cream);
            IButton("tier5/equipment/close",new Rect(p.xMax-70,p.y+8,52,50),"X",()=>tier5OperationsOpen=false,false);
            coastalUi.Label("tier5/gear/help",new Rect(p.x+24,p.y+90,w-48,150),
                "Fishers operate fishing gear. Deckhands collect and process catch.\n\nRods, hand nets and crab cages need no Engineer or maintenance.",22,SeaInk);
            IButton("tier5/crew/duties",new Rect(p.x+22,p.yMax-126,250,50),"Crew duties",()=>{tier5OperationsOpen=false;OpenManagement();managementTab=2;},false);
            IButton("tier5/processing",new Rect(p.x+284,p.yMax-126,254,50),"Processing orders",()=>{tier5OperationsOpen=false;netOrdersOpen=false;PrepOrdersOpen=true;},false);
            IButton("tier5/equipment/management",new Rect(p.x+22,p.yMax-64,w-44,50),"Management",()=>{tier5OperationsOpen=false;OpenManagement();},true);
        }
    }
}
