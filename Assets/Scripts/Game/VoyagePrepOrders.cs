using System.Collections;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using Catchline.Prototype;
using UnityEngine;

namespace Catchline.Game
{
    [System.Serializable]
    public class PrepOrderSettings
    {
        public bool ChumFirst = true;
        public int ChumTarget = 10;
        public float ChumMaxKg = 1;
        // Derived so old saves with the obsolete10c field cannot retain a dead filter.
        public int ChumMaxValue => ChumMaxKg <= .5f ? 6 : ChumMaxKg <= 1 ? 15 : 35;
        public bool PrepareHighestValue;
        public static int ChumYield(Species species,float kg) => CatchPresentation.Tier(species,kg) switch
        { CatchTier.Common=>1,CatchTier.BigCommon=>2,CatchTier.Rare=>3,_=>0 };
        public const float ChumWorkSeconds=3.5f,PrepareWorkSeconds=4.5f,HandlingSeconds=.3f;
        public float PrepareMinKg;
        // Missing flag in old saves deliberately migrates to safe, class-based defaults.
        public bool HasClassFilters;
        public int ChumClassMask = 1;
        public int PrepareClassMask = 63;
        public int ChumClasses => HasClassFilters ? ChumClassMask & 7 : 1;
        public int PrepareClasses => HasClassFilters ? PrepareClassMask & 63 : 63;
        public bool Allows(CaughtFish fish, bool chum) =>
            (((chum ? ChumClasses : PrepareClasses) >> (int)CatchPresentation.Tier(fish.Species, fish.Kg)) & 1) != 0;
        public void ToggleClass(bool chum, CatchTier tier)
        {
            if(chum && tier>CatchTier.Rare)return;
            ChumClassMask = ChumClasses; PrepareClassMask = PrepareClasses;
            HasClassFilters = true;
            if (chum) ChumClassMask ^= 1 << (int)tier;
            else PrepareClassMask ^= 1 << (int)tier;
        }
    }

    public partial class VoyageGame
    {
        sealed class PrepJob
        {
            public Person Worker;
            public CaughtFish Fish;
            public bool Chum;
            public int Yield;
            public int Slot;
            public Transform Visual;
        }
        readonly List<PrepJob> prepJobs = new();
        // A station belongs to a hand across jobs and empty-input periods.
        // Job completion releases the fish, never the worker's standing position.
        readonly Dictionary<Person, int> prepStations = new();
        public int PrepWorkersActive => prepJobs.Count;
        public int ChumBeingMade => prepJobs.Where(j => j.Chum).Sum(j => j.Yield);
        public bool PrepOrdersOpen;

        float EstimatedChumShare
        {
            get
            {
                float chum=Flow.CountRate(FlowTelemetry.Kind.Chum,60),prepared=Flow.CountRate(FlowTelemetry.Kind.Prepared,60);
                if(chum+prepared>0)return chum/(chum+prepared);
                return State.Chum<State.PrepOrders.ChumTarget && State.PrepOrders.ChumFirst
                    && ProcessingInput.Any(f=>State.PrepOrders.Allows(f,true)) ? 1 : 0;
            }
        }
        float TableFishCapacity => IsPrepFisher ? People.Where(p=>p.Contract?.Role==CrewRole.Deckhand&&p.Contract.WorkPreference==DeckhandWork.Prep).Take(2).Sum(p=>p.Speed)*WorkMult*60
            /(PrepOrderSettings.HandlingSeconds+Mathf.Lerp(PrepOrderSettings.PrepareWorkSeconds,PrepOrderSettings.ChumWorkSeconds,EstimatedChumShare)) : 0;

        // Reserved fish remain in the input queue until processing commits.
        public bool TryPrepWork(Person hand)
        {
            if (!IsPrepFisher || CurrentMode != Mode.Fishing || hand == null || hand.Contract == null
                || hand.Contract.Role != CrewRole.Deckhand || hand.Contract.WorkPreference != DeckhandWork.Prep
                || hand.Carrying != null || (!hand.Idle && !hand.Loitering) || prepJobs.Count >= 2
                || prepJobs.Any(j => j.Worker == hand) || PrepWorkerTiles.Length != 2) return false;
            if (!prepStations.TryGetValue(hand, out int slot))
            {
                if (prepStations.Count >= 2) return false;
                slot = Enumerable.Range(0, 2).First(i => !prepStations.Values.Contains(i));
                prepStations.Add(hand, slot);
            }
            var order = State.PrepOrders;
            CaughtFish Pick(bool chum)
            {
                var eligible = ProcessingInput.Where(f => !f.Prepared && f != captainPrepFish && !prepJobs.Any(j => j.Fish == f)
                    && (chum ? State.Chum + ChumBeingMade < Mathf.Clamp(order.ChumTarget, 0, 99)
                        && order.Allows(f, true)
                        : order.Allows(f, false)));
                // Chum keeps its existing input order. Preparation reserves independently.
                return chum ? eligible.FirstOrDefault() : order.PrepareHighestValue
                    ? eligible.OrderByDescending(f => State.ValueOf(f, SimTime)).ThenBy(f => f.StowedAt).FirstOrDefault()
                    : eligible.OrderBy(f => f.StowedAt).FirstOrDefault();
            }
            bool isChum = order.ChumFirst;
            var fish = Pick(isChum);
            if (fish == null) { isChum = !isChum; fish = Pick(isChum); }
            if (fish == null)
            {
                // Go to the table once, then wait there instead of wandering.
                if (hand.Tile != PrepWorkerTiles[slot])
                    hand.WalkTo(Grid, PrepWorkerTiles[slot], () => hand.FacePoint(PrepSurfaceLocal));
                else { hand.Stop(); hand.FacePoint(PrepSurfaceLocal); }
                return false;
            }
            // Stop a prior patrol before claiming; no path is queued for table work.
            hand.Stop();
            var job = new PrepJob { Worker = hand, Fish = fish, Chum = isChum,
                Slot = slot, Yield = isChum ? PrepOrderSettings.ChumYield(fish.Species,fish.Kg) : 0 };
            prepJobs.Add(job);
            void Release()
            {
                prepJobs.Remove(job);
                if(pipelineVisuals.TryGetValue(fish,out var queued) && queued!=null)queued.gameObject.SetActive(true);
                if (job.Visual != null) Visuals.Kill(job.Visual.gameObject);
            }
            void Finish()
            {
                // A return/duty change cancels reservations; never consume twice.
                if (prepJobs.Contains(job) && ProcessingInput.Contains(fish) && !fish.Prepared)
                {
                    if (job.Chum)
                    {
                        if (State.Chum < Mathf.Clamp(State.PrepOrders.ChumTarget, 0, 99))
                        { Flow.Record(FlowTelemetry.Kind.Chum, fish.Kg); ProcessingInput.Remove(fish); RemovePipelineVisual(fish); State.Chum += job.Yield; }
                    }
                    else
                    {
                        PrepareFish(fish);
                    }
                }
                Release();
                hand.FacePoint(PrepSurfaceLocal);
            }
            void Begin()
            {
                if(pipelineVisuals.TryGetValue(fish,out var queued) && queued!=null)queued.gameObject.SetActive(false);
                float side = slot == 0 ? 1.76f : 1.04f;
                hand.FacePoint(PrepSurfaceLocal);
                job.Visual = DeckFish.BuildModel(fish.Species, fish.Kg, Boat);
                job.Visual.localScale *= .65f;
                job.Visual.localPosition = IsTier5 ? PrepInputLocal : new Vector3(2.94f, .5f, side);
                hand.Do("Taking fish", .15f, () =>
                {
                    job.Visual.localPosition = IsTier5 ? PrepSurfaceLocal : new Vector3(3.6f, .8f, side);
                    hand.Do(job.Chum ? "Making chum" : "Preparing fish", job.Chum ? PrepOrderSettings.ChumWorkSeconds : PrepOrderSettings.PrepareWorkSeconds, () =>
                    {
                        // Turn/reach to the box behind; feet stay on the same tile.
                        hand.FacePoint(IsTier5 ? PreparedOutputLocal : new Vector3(4.84f, .5f, side));
                        job.Visual.localPosition = IsTier5 ? PreparedOutputLocal : new Vector3(4.84f, .5f, side);
                        hand.Do("Putting fish away", .15f, Finish, Release);
                    }, Release);
                }, Release);
            }
            if (hand.Tile == PrepWorkerTiles[slot]) Begin();
            else if (!hand.WalkTo(Grid, PrepWorkerTiles[slot], Begin, Release)) { Release(); return false; }
            return true;
        }

        void ClearPrepWork()
        {
            CancelCaptainPrep();
            foreach (var hand in prepStations.Keys.ToArray()) hand.Stop();
            prepJobs.Clear();
            prepStations.Clear();
            PrepOrdersOpen = false;
            prepClassDropdown = 0;
        }

        public void ChangePrepPriority()
        {
            State.PrepOrders.ChumFirst = !State.PrepOrders.ChumFirst;
            SaveGame(); // Current jobs finish; new orders choose the new priority.
        }

        IEnumerator CapturePrepOrders(string directory)
        {
            Directory.CreateDirectory(directory);
            Application.runInBackground = true;
            captureFreeze = true;
            Cooler.Clear();
            State.Chum = 9;
            for (int i = 0; i < 14; i++) Cooler.Add(new CaughtFish { Species = Species.Herring, Kg = .2f, StowedAt = SimTime });
            Cooler.Add(new CaughtFish { Species = Species.Cod, Kg = 5, StowedAt = SimTime });
            var hands = People.Where(p => p.Contract?.Role == CrewRole.Deckhand).ToArray();
            foreach (var h in hands) SetDeckhandWork(h.Contract, DeckhandWork.Prep);
            foreach (var h in hands) TryPrepWork(h);
            // Drive real walks until both hands reach their actual table anchors.
            for (int i = 0; i < 1600 && hands.Any(h => h.BusyLabel is not ("Making chum" or "Preparing fish")); i++)
                foreach (var h in hands) if (h.BusyLabel is not ("Making chum" or "Preparing fish")) h.Tick(.025f, 1, Cam.transform.rotation);
            foreach (var size in new[] { new Vector2Int(1440,900), new Vector2Int(844,390) })
            {
                Screen.SetResolution(size.x, size.y, FullScreenMode.Windowed);
                for (int i = 0; i < 16; i++) yield return null;
                PrepOrdersOpen = netOrdersOpen = false; toastUntil = 0;
                yield return null;
                yield return CaptureFrame(directory, "prep-working-" + size.x);
                PrepOrdersOpen = true;
                yield return null;
                yield return CaptureFrame(directory, "prep-orders-" + size.x);
                PrepOrdersOpen = false; netOrdersOpen = true;
                yield return null;
                yield return CaptureFrame(directory, "prep-duties-" + size.x);
                netOrdersOpen = false;
            }
            Debug.Log("[Catchline] PREP035 NATIVE CAPTURES COMPLETE");
            Application.Quit(0);
        }

        int prepClassDropdown; // 0 closed, 1 chum, 2 preparation.
        static string PrepClassSummary(int mask)
        {
            if (mask == 63) return "All classes";
            if (mask == 0) return "None selected";
            var selected = Enumerable.Range(0, 6).Where(i => (mask & (1 << i)) != 0).ToArray();
            return selected.Length == 1 ? CatchPresentation.Label((CatchTier)selected[0]) : $"{selected.Length} classes selected";
        }
        void InterfacePrepClassDropdown(Rect column, bool chum)
        {
            string id = "prep/classes/" + (chum ? "chum" : "prepare");
            var p = new Rect(column.x, column.y - 136, column.width, 424);
            // Real overlay buttons intercept taps on the controls below them.
            coastalUi.Box(id + "/panel", p, "chip-dark");
            coastalUi.Label(id + "/title", new Rect(p.x+14,p.y+8,p.width-106,52),
                chum ? "Fish to chum" : "Fish to prepare", 21, Palette.Cream);
            IButton(id + "/done",new Rect(p.xMax-86,p.y+8,74,54),"Done",()=>prepClassDropdown=0,false);
            coastalUi.Label(id+"/hint",new Rect(p.x+14,p.y+55,p.width-28,20),"Tap classes to include or exclude.",15,Palette.Cream);
            for (int i=0; i<6; i++)
            {
                var tier=(CatchTier)i;
                var row=new Rect(p.x+8,p.y+76+i*55,p.width-16,54);
                bool selected=(((chum ? State.PrepOrders.ChumClasses : State.PrepOrders.PrepareClasses) >> i)&1)!=0;
                string rowId=id+"/"+i;
                Block(row);
                coastalUi.Button(rowId,row,"",()=>{State.PrepOrders.ToggleClass(chum,tier);SaveGame();},"chip-dark",!chum || tier<=CatchTier.Rare);
                coastalUi.Box(rowId+"/color",new Rect(row.x+10,row.y+18,16,16),"",CatchPresentation.Accent(tier),blocks:false);
                coastalUi.Label(rowId+"/name",new Rect(row.x+38,row.y,row.width-100,50),CatchPresentation.Label(tier),19,CatchPresentation.Accent(tier));
                coastalUi.Label(rowId+"/state",new Rect(row.xMax-60,row.y,50,50),chum && tier>CatchTier.Rare ? "N/A" : selected ? "On" : "Off",17,
                    selected ? Palette.Cream : Palette.Hex("98AFB7"),TextAnchor.MiddleCenter);
            }
        }
        void InterfacePrepOrders()
        {
            if (!IsPrepFisher) return;
            MaybeCapturePrepRarity();
            if (!IsTier5) IButton("prep/open",FishingFooter(1,1),$"Prep table / chum {State.Chum}",()=>
                {PrepOrdersOpen=true;prepClassDropdown=0;netOrdersOpen=false;toastUntil=0;},false);
            if (!PrepOrdersOpen) return;
            Block(new Rect(0,0,iw,ih));
            coastalUi.Box("prep/shade",new Rect(0,0,iw,ih),"chip-dark",new Color(1,1,1,.7f));
            var p=new Rect((iw-800)/2,(ih-448)/2,800,448);
            coastalUi.Box("prep/panel",p);
            coastalUi.Label("prep/title",new Rect(p.x+20,p.y+8,620,38),"Prep table",27);
            IButton("prep/close",new Rect(p.xMax-74,p.y+8,54,54),"X",()=>{PrepOrdersOpen=false;prepClassDropdown=0;},false);
            coastalUi.Label("prep/status",new Rect(p.x+20,p.y+48,700,28),
                $"{ProcessingOutput.Count(f=>f.Prepared)} fish prepared",17,SeaInk);
            var o=State.PrepOrders;
            coastalUi.Label("prep/worker-hint",new Rect(p.x+20,p.y+82,IsTier5?360:760,44),
                "Deckhands follow these choices when assigned Prep in Crew duties.",16,SeaInk);
            if(IsTier5) IButton("prep/priority",new Rect(p.x+420,p.y+72,360,54),State.PrepOrders.ChumFirst?"Make chum first":"Prepare fish first",ChangePrepPriority,false);
            float left=p.x+20,right=p.x+420,w=360;
            coastalUi.Box("prep/divider",new Rect(p.x+399,p.y+150,2,278),"",Palette.Hex("D8DED5"),blocks:false);
            coastalUi.Label("prep/chum/title",new Rect(left,p.y+146,w,32),"Chum settings",25);
            coastalUi.Label("prep/prepare/title",new Rect(right,p.y+146,w,32),"Fish preparation",25);
            coastalUi.Label("prep/chum/help",new Rect(left,p.y+182,w,44),"Turn selected incoming fish into bait.\nThese fish leave the processing queue.",17,SeaInk);
            coastalUi.Label("prep/prepare/help",new Rect(right,p.y+182,w,44),IsTier5?"Keep the fish. Sell for 50% more.\nPrepared fish never spoil.":"Keep the fish. Sell for 25% more.\nPrepared fish never spoil.",17,SeaInk);
            IButton("prep/chum/classes",new Rect(left,p.y+232,w,54),"Fish to chum: "+PrepClassSummary(o.ChumClasses)+"  v",()=>prepClassDropdown=prepClassDropdown==1?0:1,false);
            IButton("prep/prepare/classes",new Rect(right,p.y+232,w,54),"Fish to prepare: "+PrepClassSummary(o.PrepareClasses)+"  v",()=>prepClassDropdown=prepClassDropdown==2?0:2,false);
            IButton("prep/target",new Rect(left,p.y+294,w,54),o.ChumTarget==0 ? "Make chum: Off" : $"Keep {o.ChumTarget} chum ready",
                ()=>{o.ChumTarget=o.ChumTarget==10?20:o.ChumTarget==20?0:10;SaveGame();},false);
            IButton("prep/sort",new Rect(right,p.y+294,w,54),o.PrepareHighestValue ? "Prepare most valuable fish first" : "Prepare oldest fish first",
                ()=>{o.PrepareHighestValue=!o.PrepareHighestValue;SaveGame();},false);
            coastalUi.Label("prep/chum/stock",new Rect(left,p.y+350,w,26),$"{State.Chum} chum ready  /  {ChumBeingMade} being made",17,SeaInk);
            coastalUi.Label("prep/chum/yield",new Rect(left,p.y+382,w,46),"White 1 · Green 2 · Blue 3 chum.\nPurple, gold and red cannot be chummed.",16,SeaInk);
            IButton("prep/captain/start",new Rect(right,p.y+382,w,54),"Help prepare incoming fish",
                ()=>StartCaptainPrep(),true,CanCaptainPrep);
            if (prepClassDropdown!=0)
                InterfacePrepClassDropdown(new Rect(prepClassDropdown==1?left:right,p.y+148,w,280),prepClassDropdown==1);
        }
    }
}
