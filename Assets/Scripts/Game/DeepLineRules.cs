using System;

namespace Catchline.Game
{
    [Flags] public enum FisherTask { None = 0, Rods = 1, Nets = 2, Crabs = 4, DeepLines = 8, All = 15 }
    public enum FisherWork { RodsOnly, CrabAndDeepFirst, CrabsOnly, DeepLinesOnly }
    public enum DeepLinePhase { Empty, Dropping, Soaking, Raising, CatchOnDeck }

    // Shared first-pass rules. Catch tuning is deliberately separate from physical rig count.
    public static class DeepLineRules
    {
        public const int StandardRigCount = 2, MaximumRigCount = 3;
        public const float BaitSeconds = 2f, DropSeconds = 1f, SoakSeconds = 60f, RaiseSeconds = 2f;
        public static int CatchCount(int rig) => rig >= 0 && rig < MaximumRigCount ? 1 : 0;
        public static readonly float[] ClassWeights = { .05f,.05f,.10f,.75f,.03f,.02f };
        public sealed class Option
        {
            public Species Species; public CatchTier Tier; public float Min,Max,Weight,Probability;
        }
        public static System.Collections.Generic.List<Option> Options(GameState state,int spot,BaitPermission bait)
        {
            var result=new System.Collections.Generic.List<Option>();
            if(bait!=BaitPermission.Chum)return result;
            float power=.55f+(bait==BaitPermission.Squid?GameData.SquidPowerBonus:0);
            foreach(var entry in state.FishTable(spot))
            {
                if(state.Tier<GameData.MinimumHull(entry.species))continue;
                var fish=GameData.Get(entry.species);float h=fish.Heaviness;
                float weight=entry.weight*UnityEngine.Mathf.Lerp(1-.7f*h,1+1.6f*h,power);
                if(bait==BaitPermission.Chum)weight*=.01f+h*h*8;
                if(bait==BaitPermission.Squid)weight*=h<.35f?.04f:.65f+h*1.6f;
                var low=CatchPresentation.Tier(entry.species,fish.MinKg);var high=CatchPresentation.Tier(entry.species,fish.MaxKg);
                void Add(CatchTier tier,float min,float max)
                { if(max>=min)result.Add(new Option{Species=entry.species,Tier=tier,Min=min,Max=max,Weight=weight}); }
                if(low==high)Add(low,fish.MinKg,fish.MaxKg);
                else
                {
                    float threshold=fish.MaxKg*.75f;
                    Add(low,fish.MinKg,threshold-.00001f);Add(high,threshold,fish.MaxKg);
                }
            }
            float available=0;
            for(int tier=0;tier<6;tier++)if(result.Exists(o=>(int)o.Tier==tier))available+=ClassWeights[tier];
            foreach(var option in result)
            {
                float sum=0;foreach(var other in result)if(other.Tier==option.Tier)sum+=other.Weight;
                option.Probability=ClassWeights[(int)option.Tier]/available*option.Weight/sum;
            }
            return result;
        }
        public static (Species species,float kg) Roll(GameState state,int spot,BaitPermission bait,bool heavier = false)
        {
            var options=Options(state,spot,bait);if(options.Count==0)throw new InvalidOperationException("No local deep-line catch available");
            float roll=(float)state.Rng.NextDouble();var selected=options[options.Count-1];
            foreach(var option in options){roll-=option.Probability;if(roll<=0){selected=option;break;}}
            float sample=(float)state.Rng.NextDouble();
            if(heavier)sample=UnityEngine.Mathf.Max(sample,(float)state.Rng.NextDouble());
            float kg=UnityEngine.Mathf.Lerp(selected.Min,selected.Max,sample);return(selected.Species,kg);
        }
        public static CatchExpectation.RodMix Expectation(GameState state,int spot,BaitPermission bait)
        {
            var mix=new CatchExpectation.RodMix();
            foreach(var option in Options(state,spot,bait))
            {
                if(!mix.Probabilities.ContainsKey(option.Species))mix.Probabilities[option.Species]=0;
                mix.Probabilities[option.Species]+=option.Probability;
                for(int n=0;n<512;n++)
                {
                    float kg=UnityEngine.Mathf.Lerp(option.Min,option.Max,(n+.5f)/512);
                    mix.Kg+=option.Probability*kg/512;
                    mix.Value+=option.Probability*CatchExpectation.NominalValue(option.Species,kg)/512;
                }
            }
            return mix;
        }
        public static bool AllowsRods(FisherWork work) => work == FisherWork.RodsOnly || work == FisherWork.CrabAndDeepFirst;
        public static bool AllowsCrabs(FisherWork work) => work == FisherWork.CrabsOnly || work == FisherWork.CrabAndDeepFirst;
        public static bool AllowsDeepLines(FisherWork work) => work == FisherWork.DeepLinesOnly || work == FisherWork.CrabAndDeepFirst;
    }

    // One paid deployment, one automatic return, then collection backpressure.
    // Person/path claims and actual specimen ownership remain in VoyageGame.
    public sealed class DeepLineCycle
    {
        public DeepLinePhase Phase { get; private set; }
        public float Remaining { get; private set; }
        public BaitPermission Bait { get; private set; }
        public bool Deploy(BaitPermission bait)
        {
            if (Phase != DeepLinePhase.Empty || bait != BaitPermission.Chum) return false;
            Bait = bait; Phase = DeepLinePhase.Dropping; Remaining = DeepLineRules.DropSeconds;
            return true;
        }
        public bool Tick(float dt, float soakDuration = 1)
        {
            if (dt <= 0 || float.IsNaN(dt) || float.IsInfinity(dt)) return false;
            while (Phase == DeepLinePhase.Dropping || Phase == DeepLinePhase.Soaking || Phase == DeepLinePhase.Raising)
            {
                float rate = Phase == DeepLinePhase.Soaking ? 1 / UnityEngine.Mathf.Max(.4f, soakDuration) : 1;
                float seconds = Remaining / rate;
                if (dt < seconds) { Remaining -= dt * rate; return false; }
                dt -= seconds;
                if (Phase == DeepLinePhase.Dropping) { Phase = DeepLinePhase.Soaking; Remaining = DeepLineRules.SoakSeconds; }
                else if (Phase == DeepLinePhase.Soaking) { Phase = DeepLinePhase.Raising; Remaining = DeepLineRules.RaiseSeconds; }
                else { Phase = DeepLinePhase.CatchOnDeck; Remaining = 0; return true; }
            }
            return false;
        }
        public void Collected()
        {
            if (Phase == DeepLinePhase.CatchOnDeck) Reset();
        }
        public void Reset() { Phase = DeepLinePhase.Empty; Remaining = 0; Bait = BaitPermission.None; }
    }
}
