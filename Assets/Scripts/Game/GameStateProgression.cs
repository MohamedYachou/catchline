namespace Catchline.Game
{
    public partial class GameState
    {
        public float NetCapacityKg => Tier >= 4 ? Has(UpgradeId.NetSystem) ? 44f : 30f : Has(UpgradeId.NetSystem) ? 30f : 20f;
        public const int JigBoatCost = 6500;
        public bool CanRefitJig => Tier == 2 && Coins >= JigBoatCost;
        public bool RefitJig()
        {
            if (!CanRefitJig) return false;
            Coins -= JigBoatCost; Hull = 5; Fuel = FuelCapacity;
            EnsureCrewRoleOffers(); return true;
        }
        public const int PrepFisherCost = 9500;
        public const float PrepFisherKgGoal = 100f;
        public bool CanRefitPrep => Tier == 3 && BestVoyageKg >= PrepFisherKgGoal && Coins >= PrepFisherCost;
        public bool RefitPrep()
        {
            if (!CanRefitPrep) return false;
            Coins -= PrepFisherCost; Hull = 3; Fuel = FuelCapacity;
            EnsureCrewRoleOffers(); return true;
        }
        public bool UpgradeAvailable(UpgradeId id) => (id != UpgradeId.ThirdDeepLine || Tier == 5) && (id != UpgradeId.NetSystem || Tier >= 2) && (id != UpgradeId.RodHolder || Tier == 0);
        public const int CompactFisherCost = 4000;
        public bool CanRefitCompact => Tier == 1 && Coins >= CompactFisherCost;
        public bool RefitCompact()
        {
            if (!CanRefitCompact) return false;
            Coins -= CompactFisherCost; Hull = 2; Fuel = FuelCapacity;
            EnsureCrewRoleOffers(); return true;
        }
        public int UpgradeCost(UpgradeId id)
        {
            if (id == UpgradeId.NetSystem) return 5000;
            if (Tier < 2) return GameData.Upgrade(id).Cost;
            return id switch
            {
                UpgradeId.RodHolder => 1500,
                UpgradeId.LunchTin => 1500,
                UpgradeId.RodFibreglass => 1800,
                UpgradeId.IceBox => 2500,
                UpgradeId.BigCooler => 3000,
                UpgradeId.RodCarbon => 3500,
                _ => GameData.Upgrade(id).Cost
            };
        }
        public string UpgradeDescription(UpgradeId id) => id == UpgradeId.BigCooler
            ? Tier == 0 ? $"Expand the hold from {GameData.RowboatHoldKg:0} kg to {GameData.RowboatBigCoolerKg:0} kg."
                : $"Expand the hold from {HullDef.Capacity} kg to {HullDef.Capacity * 1.5f:0} kg."
            : id == UpgradeId.NetSystem ? $"Raise net capacity from {(Tier >= 4 ? 30 : 20)} kg to {(Tier >= 4 ? 44 : 30)} kg."
            : GameData.Upgrade(id).Desc;
    }
}
