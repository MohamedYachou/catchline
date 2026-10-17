namespace Catchline.Game
{
    public partial class GameState
    {
        public float NetCapacityKg => Has(UpgradeId.NetSystem) ? 15f : 10f;
        public bool UpgradeAvailable(UpgradeId id) => (id != UpgradeId.NetSystem || Hull >= 2) && (id != UpgradeId.RodHolder || Hull == 0);
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
        public string UpgradeDescription(UpgradeId id) => id == UpgradeId.BigCooler && Hull >= 2
            ? "Expand the fish hold from100kg to150kg. More room for rods and repeated net hauls."
            : GameData.Upgrade(id).Desc;
    }
}
