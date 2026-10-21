using System;
using System.Linq;
using Catchline.Prototype;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        readonly DeepLineCycle[] deepLines = { new(), new(), new() };
        readonly Person[] deepLineWorkers = new Person[3];
        readonly Vector2Int[] deepLineTiles = new Vector2Int[3];
        readonly Vector3[] deepLineTips = new Vector3[3];
        readonly LineRenderer[] deepLineRopes = new LineRenderer[3];
        bool deepLineAnchorsPresent;
        Vector2Int? tier5RearNetAccess, tier5SideNetAccess;
        public bool DeepLinesActive => IsTier5 && !SecondNetActive && deepLineAnchorsPresent;
        public int FittedDeepLineCount => DeepLinesActive ? State.Has(UpgradeId.ThirdDeepLine) ? 3 : 2 : 0;
        int ConfiguredDeepLineCount => State.Has(UpgradeId.ThirdDeepLine) ? 3 : 2;
        public int DeepLineHauls { get; private set; }
        public DeepLinePhase DeepLineStatus(int rig) => deepLines[rig].Phase;
        public float DeepLineRemaining(int rig) => deepLines[rig].Remaining;
        public Vector2Int DeepLineWorkerTile(int rig) => deepLineTiles[rig];

        void ConfigureDeepLines(GameObject model)
        {
            ResetDeepLines();
            var rearNet = ArtLibrary.Find(model, "NetWorker_1");
            var sideNet = ArtLibrary.Find(model, "NetWorker_2");
            tier5RearNetAccess = rearNet != null ? Grid.GetTile(Boat.InverseTransformPoint(rearNet.position)) : null;
            tier5SideNetAccess = sideNet != null ? Grid.GetTile(Boat.InverseTransformPoint(sideNet.position)) : null;
            var module = ArtLibrary.Find(model, "DeepLineModule");
            var optional = ArtLibrary.Find(model, "OptionalRodModule");
            if (module != null) module.gameObject.SetActive(!SecondNetActive);
            if (optional != null) optional.gameObject.SetActive(!SecondNetActive);
            if(module!=null && State.Has(UpgradeId.ThirdDeepLine))
            {
                var source=ArtLibrary.Find(model,"DeepLineRig_1");
                var third=Instantiate(source.gameObject,module);third.name="DeepLineRig_3";
                var shift=Boat.TransformVector(new Vector3(-1.6f,0,0));third.transform.position+=shift;
                foreach(var child in third.GetComponentsInChildren<Transform>(true))child.name=child.name.Replace("Deep 1 ","Deep 3 ").Replace("DeepLineReelPivot_1","DeepLineReelPivot_3");
                foreach(var stem in new[]{"DeepLineWorker_","DeepLineTip_","DeepLineBase_"})
                {
                    var anchor=new GameObject(stem+3).transform;anchor.SetParent(module,false);
                    anchor.position=ArtLibrary.Find(model,stem+1).position+shift;
                }
            }
            deepLineAnchorsPresent = module != null;
            for (int i = 0; i < ConfiguredDeepLineCount; i++)
            {
                var worker = ArtLibrary.Find(model, "DeepLineWorker_" + (i + 1));
                var tip = ArtLibrary.Find(model, "DeepLineTip_" + (i + 1));
                if (worker == null || tip == null) { deepLineAnchorsPresent = false; continue; }
                deepLineTiles[i] = Grid.GetTile(Boat.InverseTransformPoint(worker.position));
                deepLineTips[i] = Boat.InverseTransformPoint(tip.position);
                if (SecondNetActive) continue;
                foreach (var child in module.GetComponentsInChildren<Transform>(true))
                    if (child.name == "Deep " + (i + 1) + " hanging fishing line") child.gameObject.SetActive(false);
                var line = new GameObject("Deep line " + (i + 1)).AddComponent<LineRenderer>();
                line.transform.SetParent(Boat, false); line.useWorldSpace = false;
                line.sharedMaterial = Visuals.Mat(Palette.Hex("D1AF76"));
                line.startWidth = line.endWidth = .012f; line.positionCount = 2; deepLineRopes[i] = line;
            }
            UpdateDeepLineRopes();
        }
        void ResetDeepLines(bool clearVisuals = true)
        {
            for (int i = 0; i < deepLines.Length; i++)
            {
                deepLines[i].Reset(); deepLineWorkers[i] = null;
                if (clearVisuals)
                {
                    if (deepLineRopes[i] != null) Visuals.Kill(deepLineRopes[i].gameObject);
                    deepLineRopes[i] = null;
                }
            }
            if (clearVisuals) deepLineAnchorsPresent = false;
            else UpdateDeepLineRopes();
        }
        public void SetFisherWork(CrewMember crew, FisherWork work)
        {
            if (crew == null || crew.Role != CrewRole.Fisherman || !State.Crew.Contains(crew) || !Enum.IsDefined(typeof(FisherWork), work)) return;
            crew.HasFisherWork = true; crew.FisherPreference = work; crew.HasFisherTasks = false;
            forecastSignature = flowCrewSignature = null; SaveGame();
        }
        public void ToggleFisherTask(CrewMember crew, FisherTask task)
        {
            if (crew == null || crew.Role != CrewRole.Fisherman || !State.Crew.Contains(crew)) return;
            crew.AllowedTasks = crew.FishingTasks ^ (task & FisherTask.All); crew.HasFisherTasks = true;
            forecastSignature = flowCrewSignature = null; SaveGame();
        }
        public bool TryDeepLineWork(Person fisher)
        {
            if (!DeepLinesActive || CurrentMode != Mode.Fishing || fisher == null || !fisher.Idle || fisher.Carrying != null
                || fisher.Contract?.Role != CrewRole.Fisherman || HoldFull || !fisher.Contract.Allows(FisherTask.DeepLines)
                || State.SelectDeepLineBait(fisher.Contract)==BaitPermission.None) return false;
            int rig = Enumerable.Range(0, FittedDeepLineCount).Where(i => deepLines[i].Phase == DeepLinePhase.Empty && deepLineWorkers[i] == null).DefaultIfEmpty(-1).First();
            if (rig < 0) return false;
            deepLineWorkers[rig] = fisher;
            bool Owns() => deepLineWorkers[rig] == fisher;
            void Cancel() { if (Owns()) deepLineWorkers[rig] = null; }
            void Finish()
            {
                if (!Owns()) return;
                if (!DeepLinesActive || CurrentMode != Mode.Fishing || HoldFull) { Cancel(); return; }
                var bait = State.SelectDeepLineBait(fisher.Contract);
                if (bait != BaitPermission.None && deepLines[rig].Phase == DeepLinePhase.Empty
                    && State.TakeDeepLineBait(fisher.Contract)) deepLines[rig].Deploy(bait);
                Cancel();
            }
            bool started = fisher.WalkTo(Grid, deepLineTiles[rig], () =>
            {
                if (!Owns()) return;
                fisher.FacePoint(deepLineTips[rig]); fisher.Do("Baiting deep line", DeepLineRules.BaitSeconds, Finish, Cancel);
            }, Cancel);
            if (!started) Cancel(); return started;
        }
        bool FisherSpecialThink(Person fisher)
        {
            if (!IsTier5) return false;
            if (!fisher.Idle) return true;
            var work = fisher.Contract.FishingWork; var rod = Rods.FirstOrDefault(r => r.Fisher == fisher);
            // Finish an already committed cast/strike/reel before applying a new preference.
            bool safe = rod == null || rod.State == RodState.Unbaited || rod.State == RodState.Ready
                || fisher.Contract.Allows(FisherTask.Rods) && rod.State == RodState.Waiting && rod.WaitRemaining > 9f;
            if (!safe) return false;
            fisher.Pose = "Idle";
            if (fisher.Contract.Allows(FisherTask.Nets))
            {
                int net=AssignedNet(fisher);
                if ((net==0 && Net==NetState.Ready || net==1 && SecondNet==NetState.Ready) && TryNetWork(fisher)) return true;
            }
            if (fisher.Contract.Allows(FisherTask.Crabs) && TryBuoyWork(fisher)) return true;
            if (fisher.Contract.Allows(FisherTask.DeepLines) && TryDeepLineWork(fisher)) return true;
            if (fisher.Contract.Allows(FisherTask.Nets) && TryNetWork(fisher)) return true;
            if (fisher.Contract.Allows(FisherTask.Rods)) return false;
            if (rod != null) rod.Fisher = null;
            IdlePatrol(fisher); return true;
        }
        void TickDeepLines(float dt)
        {
            if (!DeepLinesActive || CurrentMode != Mode.Fishing || dt <= 0) return;
            for (int rig = 0; rig < FittedDeepLineCount; rig++)
            {
                var cycle = deepLines[rig];
                if (cycle.Phase == DeepLinePhase.CatchOnDeck && !OnDeck.Any(f => f.DeepLineRig == rig)) cycle.Collected();
                if (!cycle.Tick(dt)) continue;
                for (int n = 0; n < DeepLineRules.CatchCount(rig); n++)
                {
                    var bait = cycle.Bait;
                    var caught = DeepLineRules.Roll(State,ActiveSpot,bait);
                    var fish = new DeckFish { Species = caught.Item1, Kg = caught.Item2, Tile = deepLineTiles[rig], CaughtAt = SimTime, CaughtByCrew = true, DeepLineRig = rig };
                    fish.Root = DeckFish.BuildModel(fish.Species, fish.Kg, Boat);
                    fish.RestPos = Grid.GetLocal(fish.Tile) + new Vector3(.08f + n * .10f, .08f, .08f);
                    fish.SpawnFrom = deepLineTips[rig]; fish.Root.localPosition = fish.SpawnFrom;
                    OnDeck.Add(fish); Stats.Landed++; State.OnCatch(ActiveSpot, fish.Kg);
                    RecordLanding(FlowTelemetry.Kind.DeepLine, fish.Species, fish.Kg);
                }
                DeepLineHauls++;
            }
            UpdateDeepLineRopes();
        }
        void UpdateDeepLineRopes()
        {
            for (int rig = 0; rig < FittedDeepLineCount; rig++)
            {
                var line = deepLineRopes[rig]; if (line == null) continue; var cycle = deepLines[rig];
                float dropped = cycle.Phase == DeepLinePhase.Soaking ? 1
                    : cycle.Phase == DeepLinePhase.Dropping ? 1 - cycle.Remaining / DeepLineRules.DropSeconds
                    : cycle.Phase == DeepLinePhase.Raising ? cycle.Remaining / DeepLineRules.RaiseSeconds : 0;
                line.SetPosition(0, deepLineTips[rig]);
                line.SetPosition(1, Vector3.Lerp(deepLineTips[rig] - Vector3.up * .2f, new Vector3(deepLineTips[rig].x, -.5f, deepLineTips[rig].z), dropped));
            }
        }
    }
}
