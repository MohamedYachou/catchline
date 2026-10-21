using System.Linq;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        CaughtFish captainPrepFish;
        bool captainPrepActive, captainPrepCutting;
        float captainPrepAge, captainPrepCooldown;
        string captainPrepMessage = "Tap in the green to prepare one fish.";
        public bool CaptainPrepActive => captainPrepActive;
        public float CaptainPrepPhase => Mathf.PingPong(captainPrepAge * .8f, 1f);
        public bool CanCaptainPrep => IsPrepFisher && CurrentMode == Mode.Fishing
            && Captain.Idle && Captain.Carrying == null && Manning == null && MinigameRod == null
            && !NetGameActive && !NetUnloadActive && !captainPrepActive
            && AvailableCaptainPrepFish() != null;
        CaughtFish AvailableCaptainPrepFish()
        {
            var fish = ProcessingInput.Where(f => !f.Prepared && f != captainPrepFish
                && State.PrepOrders.Allows(f, false) && !prepJobs.Any(j => j.Fish == f));
            return State.PrepOrders.PrepareHighestValue
                ? fish.OrderByDescending(f => State.ValueOf(f,SimTime)).ThenBy(f => f.StowedAt).FirstOrDefault()
                : fish.OrderBy(f => f.StowedAt).FirstOrDefault();
        }
        // Caller holds a reservation. Guard makes by-product and premium exactly once.
        void PrepareFish(CaughtFish fish)
        {
            if (fish == null || fish.Prepared || !ProcessingInput.Contains(fish)) return;
            fish.PreparedQuality = State.Freshness(fish, SimTime);
            fish.Prepared = true;
            Flow.Record(FlowTelemetry.Kind.Prepared, fish.Kg);
            MoveToProcessingOutput(fish);
            fish.PreparedBonus = IsTier5 ? 1.5f : 1.25f;
            if (!IsTier5 && CatchPresentation.Tier(fish.Species, fish.Kg) >= CatchTier.BigRare) State.Chum++;
        }
        public bool StartCaptainPrep()
        {
            if (!CanCaptainPrep) return false;
            captainPrepFish = AvailableCaptainPrepFish(); captainPrepActive = true;
            captainPrepCutting = false; captainPrepAge = captainPrepCooldown = 0;
            captainPrepMessage = "Tap in the green to prepare one fish.";
            PrepOrdersOpen = netOrdersOpen = false;
            void Wait() { if (captainPrepActive) { Captain.FacePoint(new Vector3(3.6f,.8f,1.4f));
                Captain.Do("Helping prepare", float.MaxValue, null, CancelCaptainPrep); } }
            if (!Captain.WalkTo(Grid, ProcessingAccess, Wait, CancelCaptainPrep)) { CancelCaptainPrep(); return false; }
            return true;
        }
        public void CancelCaptainPrep()
        {
            if (!captainPrepActive) return;
            captainPrepActive = false; captainPrepFish = null; captainPrepCutting = false;
            Captain.Stop();
        }
        void TickCaptainPrep(float dt)
        {
            if (!captainPrepActive) return;
            if (CurrentMode != Mode.Fishing  || captainPrepFish == null || !ProcessingInput.Contains(captainPrepFish))
            { CancelCaptainPrep(); return; }
            if (Captain.Walking || captainPrepCutting) return;
            captainPrepAge += dt; captainPrepCooldown = Mathf.Max(0,captainPrepCooldown-dt);
        }
        public bool TapCaptainPrep()
        {
            if (!captainPrepActive || captainPrepCutting || Captain.Walking || captainPrepCooldown > 0 ) return false;
            captainPrepCooldown = .3f;
            if (CaptainPrepPhase < .35f || CaptainPrepPhase > .65f)
            { captainPrepMessage = "Missed / try the green zone. Fish kept safe."; return false; }
            var fish = captainPrepFish;
            captainPrepCutting = true;
            // Clear Stop's previous waiting callback before starting the short cut.
            captainPrepActive = false; Captain.Stop(); captainPrepActive = true;
            Captain.Do("Preparing fish", .3f, () =>
            {
                if (!captainPrepActive || captainPrepFish != fish) return;
                PrepareFish(fish); captainPrepFish = null; captainPrepCutting = false;
                captainPrepFish = AvailableCaptainPrepFish();
                if (captainPrepFish == null ) { CancelCaptainPrep(); return; }
                captainPrepMessage = "Prepared! Tap in green for the next fish.";
                Captain.Do("Helping prepare",float.MaxValue,null,CancelCaptainPrep);
            }, CancelCaptainPrep);
            return true;
        }
        void InterfaceCaptainPrep()
        {
            if (!captainPrepActive) return;
            Block(new Rect(0,0,iw,ih));
            coastalUi.Box("prep/captain/shade",new Rect(0,0,iw,ih),"chip-dark",new Color(1,1,1,.65f));
            var p = new Rect((iw-550)/2,(ih-294)/2,550,294);
            coastalUi.Box("prep/captain/panel",p);
            coastalUi.Label("prep/captain/title",new Rect(p.x+20,p.y+12,510,38),"Help prepare incoming fish",25);
            string fish = captainPrepFish == null ? "" : GameData.Get(captainPrepFish.Species).Name + $" / {captainPrepFish.Kg:0.##}kg";
            coastalUi.Label("prep/captain/fish",new Rect(p.x+20,p.y+54,510,30),fish,20);
            var meter = new Rect(p.x+20,p.y+104,510,20);
            coastalUi.Bar("prep/captain/meter",meter,CaptainPrepPhase);
            coastalUi.Box("prep/captain/green",new Rect(meter.x+meter.width*.35f,meter.y,meter.width*.3f,meter.height),"",Palette.Good,blocks:false);
            coastalUi.Box("prep/captain/cursor",new Rect(meter.x+meter.width*CaptainPrepPhase-2,meter.y-4,4,28),"",SeaInk,blocks:false);
            coastalUi.Label("prep/captain/help",new Rect(p.x+20,p.y+140,510,52),Captain.Walking ? "Walking to the table..." : captainPrepCutting ? "Preparing fish..." : captainPrepMessage,17,SeaInk);
            IButton("prep/captain/tap",new Rect(p.x+20,p.y+214,324,54),"Cut / Space",()=>TapCaptainPrep(),true,!Captain.Walking&&!captainPrepCutting);
            IButton("prep/captain/leave",new Rect(p.x+360,p.y+214,170,54),"Leave table",CancelCaptainPrep,false);
        }
    }
}
