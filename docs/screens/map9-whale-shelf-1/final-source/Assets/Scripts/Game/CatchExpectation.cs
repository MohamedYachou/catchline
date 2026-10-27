using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace Catchline.Game
{
    // Pure probability work. Forecast callers supply their own RNG; gameplay supplies its RNG.
    public static class CatchExpectation
    {
        public sealed class RodMix
        {
            public float Kg, Value, ReelSeconds;
            public readonly Dictionary<Species,float> Probabilities = new();
        }
        public static int NominalValue(Species species,float kg)
        {
            var d=GameData.Get(species);
            return Mathf.Max(1,Mathf.RoundToInt(kg*d.PricePerKg*(1+.5f*Mathf.InverseLerp(d.MinKg,d.MaxKg,kg))));
        }
        public static RodMix Rod(GameState state,int spot,float castPower,BaitPermission bait)
        {
            var result=new RodMix();if(bait==BaitPermission.None)return result;
            float power=Mathf.Clamp(castPower+(bait==BaitPermission.Squid?GameData.SquidPowerBonus:0),0,1.4f);
            if(bait==BaitPermission.Scraps){result.Probabilities[Species.Herring]=.5f;result.Probabilities[Species.Mackerel]=.5f;}
            else
            {
                foreach(var e in state.FishTable(spot))
                {
                    if(state.Hull<GameData.MinimumHull(e.species))continue;
                    float h=GameData.Get(e.species).Heaviness;
                    float weight=e.weight*Mathf.Lerp(1-.7f*h,1+1.6f*h,power);
                    if(bait==BaitPermission.Chum)weight*=.01f+h*h*8;
                    if(bait==BaitPermission.Squid)weight*=h<.35f?.04f:.65f+h*1.6f;
                    result.Probabilities[e.species]=weight;
                }
                float total=result.Probabilities.Values.Sum();
                if(total<=0)return result;
                foreach(var s in result.Probabilities.Keys.ToArray())result.Probabilities[s]/=total;
            }
            foreach(var e in result.Probabilities)
            {
                var d=GameData.Get(e.Key);
                for(int n=0;n<512;n++)
                {
                    float specimen=bait==BaitPermission.Scraps?(n+.5f)/512*.2f:Mathf.Pow((n+.5f)/512,1.5f-power);
                    if(bait==BaitPermission.Squid)specimen=Mathf.Lerp(.35f,1,specimen);
                    if(bait==BaitPermission.Chum)specimen=Mathf.Lerp(.75f,1,specimen);
                    float kg=Mathf.Lerp(d.MinKg,d.MaxKg,specimen),p=e.Value/512;
                    result.Kg+=kg*p;result.Value+=NominalValue(e.Key,kg)*p;
                    result.ReelSeconds+=Mathf.Clamp(.8f+kg*.3f,.8f,2.5f)*p;
                }
            }
            return result;
        }
        public static float BiteWait(GameState state,int spot,float power,bool learning=false)
        {
            float sum=0;
            for(int n=0;n<512;n++)
            {
                float wait=Mathf.Min(GameData.MaxBiteWait,(5+(n+.5f)/512*4+power*5)*GameData.Spots[spot].BiteWait/Mathf.Max(.3f,state.BiteRichness(spot)));
                sum+=(learning?Mathf.Clamp(wait,4,6):wait)/512;
            }
            return sum;
        }
        public static bool SmallSchool(Species s) => s==Species.Herring||s==Species.Mackerel||s==Species.Whiting||s==Species.Pollock;
        // Extracted unchanged from the actual net roll, including float RNG arithmetic and fallback.
        public static List<(Species species,float kg)> RollNet(int hull,int spot,bool deep,float target,System.Random rng,(Species species,float weight)[] table=null)
        {
            var result=new List<(Species species,float kg)>();bool large=deep;float mass=0;
            table??=GameData.Spots[spot].Table;
            while(true)
            {
                float remaining=target-mass,total=0;
                foreach(var e in table)
                {
                    if(hull<GameData.MinimumHull(e.species))continue;
                    var d=GameData.Get(e.species);if(!large&&!SmallSchool(e.species))continue;
                    float min=Mathf.Lerp(d.MinKg,d.MaxKg,large?.65f:.05f);if(min>remaining)continue;
                    total+=e.weight*(large?.08f+6f*d.Heaviness*d.Heaviness:1);
                }
                if(total<=0){if(large){large=false;continue;}break;}
                float roll=(float)rng.NextDouble()*total;Species species=table[0].species;
                foreach(var e in table)
                {
                    if(hull<GameData.MinimumHull(e.species))continue;
                    var d=GameData.Get(e.species);if(!large&&!SmallSchool(e.species))continue;
                    float min=Mathf.Lerp(d.MinKg,d.MaxKg,large?.65f:.05f);if(min>remaining)continue;
                    species=e.species;roll-=e.weight*(large?.08f+6f*d.Heaviness*d.Heaviness:1);if(roll<=0)break;
                }
                var fish=GameData.Get(species);float low=Mathf.Lerp(fish.MinKg,fish.MaxKg,large?.65f:.05f);
                float high=Mathf.Min(remaining,Mathf.Lerp(fish.MinKg,fish.MaxKg,large?1:.25f));
                float kg=Mathf.Lerp(low,high,(float)rng.NextDouble());if(kg<=0||mass+kg>target+.00001f)break;
                result.Add((species,kg));mass+=kg;
            }
            return result;
        }
        public static int[] Shares(params float[] values)
        {
            var shares=new int[values.Length];float sum=values.Sum();if(sum<=0)return shares;
            var exact=values.Select(v=>100*Mathf.Max(0,v)/sum).ToArray();
            for(int i=0;i<values.Length;i++)shares[i]=Mathf.FloorToInt(exact[i]);
            foreach(int i in Enumerable.Range(0,values.Length).OrderByDescending(i=>exact[i]-shares[i]).ThenBy(i=>i).Take(100-shares.Sum()))shares[i]++;
            return shares;
        }
    }
}
