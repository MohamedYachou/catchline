using System.Linq;
using Catchline.Game.Sea;
using UnityEngine;

namespace Catchline.Game
{
    // M4 fishing grounds: richness per ground, one moving school per ground, the visible cues and the navigator's report.
    public partial class VoyageGame
    {
        public Schools GroundSchools { get; private set; }
        public GroundCues Cues { get; private set; }
        public GroundReport LastReport { get; private set; }
        string reportedGround, reportedMove;
        float reportClock;

        public int ActiveGroundIndex => ActiveGroundId == null ? -1 : Grounds.IndexOf(ActiveSpot, ActiveGroundId);

        // The navigator card is fixed once owned; without one the player still has the gulls and ring colour.
        public bool NavigatorDeployed => State.Deployment.Any(id => Cards.ById(id)?.Role == CardRole.Navigator);

        int GroundIndexFor(int navIndex) => Grounds.IndexOf(ActiveSpot, Navigation.Grounds[navIndex].Id);
        public float GroundScoreFor(int navIndex)
        {
            int ground = GroundIndexFor(navIndex);
            return ground < 0 ? 1f : Grounds.Score(State.GroundRich, ActiveSpot, ground);
        }

        public GroundReport NavigatorReport() => ActiveGroundIndex < 0 ? null : Grounds.Report(State.GroundRich, ActiveSpot, ActiveGroundIndex);

        void TickGrounds(float dt)
        {
            if (Navigation == null || Sailor == null)
            {
                if (GroundSchools != null) { Cues?.Destroy(); Cues = null; GroundSchools = null; reportedGround = reportedMove = null; }
                State.CurrentGround = -1; State.SchoolBonus = 1f;
                return;
            }
            if (GroundSchools == null || GroundSchools.Nav != Navigation)
            {
                Cues?.Destroy();
                GroundSchools = new Schools(Navigation, 7919 * (State.Voyage + 1) + ActiveSpot);
                Cues = new GroundCues(world, GroundSchools, WaterY);
            }
            GroundSchools.Tick(dt, GroundScoreFor);
            Cues.Update(dt, GroundScoreFor);
            int ground = CurrentMode == Mode.Fishing && AtFishingGround ? ActiveGroundIndex : -1;
            State.CurrentGround = ground;
            State.SchoolBonus = ground < 0 ? 1f : GroundSchools.Bonus(Navigation.Grounds.FindIndex(g => g.Id == ActiveGroundId), Sailor.Position);
            ReportToNavigator(dt, ground);
        }

        // One short navigator line when anchoring and whenever a move suggestion appears or changes.
        void ReportToNavigator(float dt, int ground)
        {
            reportClock += dt;
            if (ground < 0) { reportedGround = reportedMove = null; return; }
            if (reportClock < 5f && reportedGround == ActiveGroundId) return;
            reportClock = 0;
            LastReport = Grounds.Report(State.GroundRich, ActiveSpot, ground);
            if (!NavigatorDeployed) return;
            bool arrival = reportedGround != ActiveGroundId;
            if (arrival || LastReport.BetterGroundId != reportedMove)
            {
                if (arrival || LastReport.ShouldMove) Toast(LastReport.Line);
                reportedMove = LastReport.BetterGroundId;
            }
            reportedGround = ActiveGroundId;
        }
    }
}
