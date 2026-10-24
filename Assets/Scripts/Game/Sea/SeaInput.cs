using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public bool SailMode { get; private set; }
        bool seaHaulModal;
        bool SeaGearDeployed => Net != NetState.Stowed || SecondNetActive && SecondNet != NetState.Stowed
            || Enumerable.Range(0, FittedDeepLineCount).Any(i => DeepLineStatus(i) != DeepLinePhase.Empty);
        Sea.SeaNav.Ground StoppedSeaGround => Sailor != null && Sailor.Arrived && !Navigation.InShallows(Sailor.Position)
            ? Navigation.Grounds.FirstOrDefault(g => g.Contains(Sailor.Position)) : null;

        public bool RequestSailMode()
        {
            if (Navigation == null || CurrentMode != Mode.Fishing || ManagementOpen || NetGameActive) return false;
            if (SeaGearDeployed) { seaHaulModal = true; return false; }
            if (Captain.Carrying != null) { Toast("Stow the captain's fish first, skipper."); return false; }
            StowSeaGear(); SailMode = true;
            Toast("Sail · tap water or a ground. Tap the boat to stop.");
            return true;
        }
        void ForfeitSeaGear()
        {
            // Stop gear actors before invalidating their claims/callbacks; landed deck fish stay aboard.
            foreach (var person in People)
                if (person == netWorker || person == secondNetWorker || deepLineWorkers.Contains(person)) person.Stop();
            ResetPrimaryNet(); ResetSecondNet(); ResetDeepLines(false);
            seaHaulModal = false; RequestSailMode();
        }
        public void StopSeaBoat()
        {
            if (!SailMode || Sailor == null || CurrentMode == Mode.SailingHome) return;
            Sailor.Stop(); UpdateSeaTravel(); Captain.Rowing = false; SetRowing(false);
            ActiveGroundId = Navigation.Grounds.FirstOrDefault(g => g.Contains(Sailor.Position))?.Id;
            CurrentMode = Mode.Fishing; seaRelocating = false;
            Toast(StoppedSeaGround != null ? "Stopped over a ground. Fish here to drop anchor." : "Stopped · tap another destination.");
        }
        public bool FishHere()
        {
            var ground = SailMode ? StoppedSeaGround : null;
            if (ground == null) return false;
            SailMode = false; ActiveGroundId = ground.Id; CurrentMode = Mode.Fishing;
            if (Scheduler != null) Scheduler.Sailing = false;
            AnchorSeaBoat(); Toast("Anchored at " + ground.Name + "."); return true;
        }
        void AnchorSeaBoat()
        {
            audio?.Play(VoyageAudio.Cue.Moor, .32f);
            Splash(new Vector3(Sailor.Position.x, WaterY, Sailor.Position.y), .22f);
        }
        void InterfaceSeaNavigation()
        {
            if (Navigation == null || ManagementOpen || CurrentMode == Mode.SailingHome) return;
            if (SailMode)
                foreach (var ground in Navigation.Grounds)
                {
                    var target = ground;
                    var view = Cam.WorldToViewportPoint(new Vector3(target.Centre.x, WaterY + .5f, target.Centre.y));
                    float x = view.x * iw, y = (1 - view.y) * ih;
                    float left = CurrentMode == Mode.Fishing ? HudGapLeft : Edge;
                    float right = CurrentMode == Mode.Fishing ? HudGapRight : iw - Edge;
                    // Offscreen pins must not be clamped over coins, crew or voyage controls.
                    if (view.z <= 0 || x < left + 100 || x > right - 100 || y < Edge + 130 || y > ih - Edge - HudButtonHeight - 80) continue;
                    InterfaceBubble("sea/ground/" + target.Id, new Vector3(target.Centre.x, WaterY + .5f, target.Centre.y),
                        target.Name ?? target.Id, "icon-map-pin", () => SailTo(target.Centre));
                }
            // The free lower-left corner of the open-water area, beside the existing voyage actions.
            float h = compactInterface ? Skin.PrimaryHeightPhone : Skin.PrimaryHeight + 16;
            var r = new Rect(Edge + HudLeftWidth + 12, ih - Edge - h, compactInterface ? 192 : 220, h);
            if (SailMode)
            {
                bool canFish = StoppedSeaGround != null;
                coastalUi.Primary("sea/fish", r, canFish ? "Fish here" : "No ground here", () => FishHere(), "v2-icon-fish", canFish);
            }
            else if (CurrentMode == Mode.Fishing)
                coastalUi.Secondary("sea/sail", r, "Sail", () => RequestSailMode(), "v2-icon-wheel");
            Block(r);
            if (!seaHaulModal) return;
            Block(new Rect(0, 0, iw, ih));
            coastalUi.Modal("sea/haul", "Gear still in the water", "Haul your gear before sailing, or forfeit the catch still in the water.",
                "Forfeit and go", ForfeitSeaGear, "Haul it first", () => seaHaulModal = false,
                () => seaHaulModal = false, "v2-icon-wheel", 620, 300);
        }
    }
}
