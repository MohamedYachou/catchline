using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using Catchline.Prototype;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public readonly List<CaughtFish> ProcessingInput = new();
        public readonly List<CaughtFish> ProcessingOutput = new();
        readonly Dictionary<Person, CaughtFish> outputClaims = new();
        readonly Dictionary<CaughtFish, Transform> pipelineVisuals = new();
        public float ProcessingKg => ProcessingInput.Concat(ProcessingOutput).Sum(f => f.Kg);
        public bool ProcessingFull => ProcessingKg >= State.CoolerCapacity;
        Vector2Int ProcessingAccess => PrepWorkerTiles.Length > 0 ? PrepWorkerTiles[0] : CoolerAccess;
        Vector2Int ProcessingOutputAccess => PrepWorkerTiles.Length > 1 ? PrepWorkerTiles[1] : CoolerAccess;
        Vector2Int InboundAccess => IsPrepFisher ? ProcessingAccess : CoolerAccess;
        public bool DeliverCatch(CaughtFish fish, bool carried = true)
        {
            if (!IsPrepFisher || flowReturning) return TryStore(fish, carried);
            if (fish == null || !float.IsFinite(fish.Kg) || fish.Kg <= 0 || ProcessingFull
                || ProcessingInput.Contains(fish) || ProcessingOutput.Contains(fish) || Cooler.Contains(fish)) return false;
            // All landed methods pass through the table on processing-equipped hulls.
            ProcessingInput.Add(fish);
            Flow.Record(FlowTelemetry.Kind.PrepInput, fish.Kg, carried: carried);
            var visual = DeckFish.BuildModel(fish.Species, fish.Kg, Boat);
            visual.localScale *= .45f;
            visual.localPosition = IsTier5 ? PrepInputLocal : new Vector3(2.94f,.5f,1.4f);
            pipelineVisuals[fish] = visual;
            return true;
        }
        void MoveToProcessingOutput(CaughtFish fish)
        {
            if (!ProcessingInput.Remove(fish)) return;
            ProcessingOutput.Add(fish);
            if (pipelineVisuals.TryGetValue(fish,out var visual) && visual != null)
            { visual.gameObject.SetActive(true);visual.localPosition = IsTier5 ? PreparedOutputLocal : new Vector3(4.84f,.5f,1.4f); }
        }
        void RemovePipelineVisual(CaughtFish fish)
        {
            if (pipelineVisuals.Remove(fish,out var v) && v != null) Visuals.Kill(v.gameObject);
        }
        public bool TryCarryProcessed(Person hand)
        {
            if (!IsPrepFisher || CurrentMode != Mode.Fishing || hand == null || HoldFull
                || hand.Carrying != null || outputClaims.ContainsKey(hand) || (!hand.Idle && !hand.Loitering)) return false;
            var fish = ProcessingOutput.FirstOrDefault(f => !outputClaims.ContainsValue(f));
            if (fish == null) return false;
            hand.Stop(); outputClaims.Add(hand,fish);
            void Cancel()
            {
                outputClaims.Remove(hand);
                if(pipelineVisuals.TryGetValue(fish,out var v) && v != null)
                { v.SetParent(Boat,false);v.localPosition=IsTier5?PreparedOutputLocal:new Vector3(4.84f,.5f,1.4f); }
            }
            void Finish()
            {
                if (outputClaims.TryGetValue(hand,out var claimed) && claimed == fish && ProcessingOutput.Contains(fish)
                    && TryStore(fish, false))
                { ProcessingOutput.Remove(fish);RemovePipelineVisual(fish);lidPop=1; }
                Cancel();
            }
            void Collect()
            {
                hand.FacePoint(IsTier5?PreparedOutputLocal:new Vector3(4.84f,.5f,1.4f));
                hand.Do("Picking up", FishHandlingSeconds(hand,GameData.CompactPickupTime),()=>
                {
                    if(pipelineVisuals.TryGetValue(fish,out var v) && v != null)
                    { v.SetParent(hand.Root,false);v.localPosition=new Vector3(0,.6f,.2f); }
                    if(!hand.WalkTo(Grid,CoolerAccess,()=>
                    {FaceHold(hand);hand.Do("Stowing",FishHandlingSeconds(hand,GameData.CompactStowTime),Finish,Cancel);},Cancel)) Cancel();
                },Cancel);
            }
            if(!hand.WalkTo(Grid,ProcessingOutputAccess,Collect,Cancel)) { Cancel();return false; }
            return true;
        }
        public bool HelpCarryProcessed() => TryCarryProcessed(Captain);
        void ClearProcessingPipeline(bool salvage = false)
        {
            foreach(var hand in outputClaims.Keys.ToArray()) hand.Stop();
            outputClaims.Clear();
            foreach(var fish in ProcessingInput.Concat(ProcessingOutput).ToArray())
            {
                if(salvage && !TryStore(fish,false)) Flow.Lose(fish.Kg);
                RemovePipelineVisual(fish);
            }
            ProcessingInput.Clear();ProcessingOutput.Clear();
        }
    }
}
