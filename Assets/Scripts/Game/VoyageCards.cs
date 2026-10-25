using System.Linq;
using Catchline.Game.Deck;
using UnityEngine;
namespace Catchline.Game
{
    public partial class VoyageGame
    {
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
                p.WalkMultiplier = () => workers.TryGetValue(p,out var w) ? Scheduler?.HaulWalkMultiplier(w) ?? 1 : 1;
            }
        }
    }
}
