using System.Linq;
using Catchline.Game.Deck;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public CrewAbilityEngine Abilities { get; private set; }
        public System.Collections.Generic.IReadOnlyList<CrewAbilityEngine.Status> ActiveAbilities(Person person) =>
            Abilities?.Query(person?.Contract?.CardId) ?? System.Array.Empty<CrewAbilityEngine.Status>();
        string AbilityOwner(Person person) => person == null || person.IsCaptain ? null : person.Contract?.CardId;
        void TickAbilities(float dt)
        {
            if (CurrentMode == Mode.Harbour) return;
            Abilities ??= new CrewAbilityEngine(State);
            float start = Abilities.Time;
            Abilities.Tick(dt, State.NightVoyage);
            float frozen = Abilities.FrozenSeconds(start);
            if (frozen > 0) foreach (var fish in Cooler) fish.StowedAt += frozen;
        }
        public float AbilityBiteDuration(Person person, bool line = false) => Abilities?.BiteDuration(AbilityOwner(person), line) ?? 1;
        public float AbilityStrike(Person person) => Abilities?.Strike(AbilityOwner(person)) ?? 1;
        public float AbilityReel(Person person) => (Abilities?.Reel(AbilityOwner(person)) ?? 1)
            * (person == null || person.IsCaptain ? 1 : Abilities?.TeamWork ?? 1);
        public float AbilityRodWork(Person person)
        {
            var c = CardFor(person?.Contract);
            return c == null ? 1 : WorkSpeed.Rate(CardProgression.Skill(c.Def, c.Rarity, Catchline.Game.Speciality.Rods), CardProgression.WorkMult(c));
        }
        float AbilityTravel => Abilities?.Travel ?? 1;
        public (Species, float) RollAbilityRod(Rod rod)
        {
            float power = rod.Power + (rod.Squid ? GameData.SquidPowerBonus : 0);
            var caught = State.RollFish(ActiveSpot, power, rod.Scraps, rod.Squid, rod.Chum);
            string id = AbilityOwner(rod.Fisher);
            if (Abilities?.PredatorNext(id) == true && !rod.Scraps)
            {
                var legal = State.FishTable(ActiveSpot).Where(e => e.weight > 0 && State.Tier >= GameData.MinimumHull(e.species)
                    && BiteModel.StyleOf(e.species) == FishStyle.Heavy).ToArray();
                if (legal.Length > 0)
                {
                    caught.Item1 = legal[State.Rng.Next(legal.Length)].species;
                    var predator = GameData.Get(caught.Item1);
                    caught.Item2 = Mathf.Lerp(predator.MinKg, predator.MaxKg, (float)State.Rng.NextDouble());
                }
            }
            var def = GameData.Get(caught.Item1);
            float Draw()
            {
                float sample = rod.Scraps ? (float)State.Rng.NextDouble() * .2f
                    : Mathf.Pow((float)State.Rng.NextDouble(), 1.5f - Mathf.Clamp(power, 0, 1.4f));
                if (!rod.Scraps && rod.Squid) sample = Mathf.Lerp(.35f, 1, sample);
                if (!rod.Scraps && rod.Chum) sample = Mathf.Lerp(.75f, 1, sample);
                return Mathf.Lerp(def.MinKg, def.MaxKg, sample);
            }
            caught.Item2 = Mathf.Clamp(caught.Item2, def.MinKg, def.MaxKg);
            if (Abilities?.DoubleWeight == true) caught.Item2 = Mathf.Max(caught.Item2, Draw());
            if (Abilities?.TrophyNext(id) == true || Abilities?.PredatorNext(id) == true)
                caught.Item2 = Mathf.Max(caught.Item2, Mathf.Lerp(def.MinKg, def.MaxKg, rod.Scraps ? .15f : .75f));
            return caught;
        }
        float AbilityWeight(Species species, float kg, float min, float max)
        {
            if (Abilities?.DoubleWeight == true) kg = Mathf.Max(kg, Mathf.Lerp(min, max, (float)State.Rng.NextDouble()));
            return kg;
        }
        // Keep the core's source-specific depletion semantics; this wrapper owns only the crew multiplier.
        void AbilityCatch(int spot, float kg, Species species, bool net)
        {
            float mult = Abilities?.Thinning ?? 1;
            if (mult == 1) { State.OnCatch(spot, kg, species, net); return; }
            if (State.CurrentGround < 0 || Grounds.Get(spot, State.CurrentGround) == null)
            {
                State.Richness[spot] = Mathf.Max(.3f, State.Richness[spot] - mult * (State.Tier >= 2 ? .0035f * kg : GameData.RichnessPerCatch));
                return;
            }
            Grounds.Drain(State.GroundRich, spot, State.CurrentGround, species, mult * (net ? Grounds.NetDrainPerKg * kg : Grounds.RodDrain));
            State.RefreshLegacyRichness();
        }
        CardState CardFor(CrewMember crew) => crew == null ? null : CardRoster.Find(State.Roster, crew.CardId);
        float CardStrikeChance(CrewMember crew)
        {
            var c = CardFor(crew);
            return c == null ? GameData.StrikeChance(crew.Grade) : CardProgression.StrikeChance(c.Rarity,c.Level);
        }
        void ConfigureCardPeople()
        {
            foreach (var p in People)
            {
                var c = CardFor(p.Contract);
                p.LevelMult = c == null ? 1 : CardProgression.WorkMult(c);
                p.Skill = 100;
                void Skill(Catchline.Game.Speciality job) { p.Skill = c == null ? 100 : CardProgression.Skill(c.Def, c.Rarity, job); }
                p.PrepareWalk = () => Skill(c?.Def.Role == CardRole.Fisher || c?.Def.Role == CardRole.Navigator
                    ? c.Def.Speciality : Catchline.Game.Speciality.Haul);
                p.PrepareAction = label => Skill(label switch
                {
                    "Sorting" or "Sorting fish" => Catchline.Game.Speciality.Sort,
                    "Processing" or "Making chum" => Catchline.Game.Speciality.Table,
                    "Baiting" or "Casting" => Catchline.Game.Speciality.Rods,
                    "Setting net" or "Hauling net" => Catchline.Game.Speciality.Nets,
                    "Baiting deep line" or "Recovering buoy catch" or "Hauling cage" => Catchline.Game.Speciality.CagesLines,
                    "Repairing" or "Engine work" => Catchline.Game.Speciality.Power,
                    _ => Catchline.Game.Speciality.Haul
                });
                p.ActionMultiplier = label => Abilities?.Work(AbilityOwner(p), label) ?? 1;
                p.WalkMultiplier = () => (p.IsCaptain ? 1 : Abilities?.TeamWork ?? 1)
                    * (Abilities?.Walk(AbilityOwner(p), p.Carrying != null || workers.TryGetValue(p, out var w) && w.Hands.Count > 0) ?? 1);
            }
        }
    }
}
