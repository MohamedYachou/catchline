namespace Catchline.Game
{
    public partial class GameState
    {
        public float NetCapacityKg => Hull >= 3 ? Has(UpgradeId.NetSystem) ? 44f : 30f : Has(UpgradeId.NetSystem) ? 30f : 20f;
        public const int PrepFisherCost = 9500;
        public const float PrepFisherKgGoal = 100f;
        public bool CanRefitPrep => Hull == 2 && BestVoyageKg >= PrepFisherKgGoal && Coins >= PrepFisherCost;
        public bool RefitPrep()
        {
            if (!CanRefitPrep) return false;
            Coins -= PrepFisherCost; Hull = 3; Fuel = FuelCapacity;
            EnsureCrewRoleOffers(); return true;
        }
        public bool UpgradeAvailable(UpgradeId id) => (id != UpgradeId.ThirdDeepLine || Hull == 4) && (id != UpgradeId.NetSystem || Hull >= 2) && (id != UpgradeId.RodHolder || Hull == 0);
        public const int CompactFisherCost = 4000;
        public bool CanRefitCompact => Hull == 1 && Coins >= CompactFisherCost;
        public bool RefitCompact()
        {
            if (!CanRefitCompact) return false;
            Coins -= CompactFisherCost; Hull = 2; Fuel = FuelCapacity;
            EnsureCrewRoleOffers(); return true;
        }
        public int UpgradeCost(UpgradeId id)
        {
            if (id == UpgradeId.NetSystem) return 5000;
            if (Hull < 2) return GameData.Upgrade(id).Cost;
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
            ? Hull == 0 ? "Expand the hold from 20 kg to 35 kg."
                : $"Expand the hold from {HullDef.Capacity} kg to {HullDef.Capacity * 1.5f:0} kg."
            : id == UpgradeId.NetSystem ? $"Raise net capacity from {(Hull >= 3 ? 30 : 20)} kg to {(Hull >= 3 ? 44 : 30)} kg."
            : GameData.Upgrade(id).Desc;
    }
}
