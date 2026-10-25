namespace Catchline.Game
{
    // Renown road (spec section 6): account progression that survives a prestige.
    // Renown = crew levels + 5 per rank gained + 10 per star (CardState.Renown).
    public enum RenownRewardKind { BlueprintChoice, Tokens, Chest }

    public struct RenownReward
    {
        public RenownRewardKind Kind;
        public int Tokens;
        public ChestKind Chest;

        public string Label => Kind switch
        {
            RenownRewardKind.BlueprintChoice => "Blueprint of your choice",
            RenownRewardKind.Tokens => Tokens + " tokens",
            _ => Chests.Def(Chest).Name,
        };
    }

    public static class RenownRoad
    {
        // Renown needed for milestone n (1-based): 5, 10, 20, 30, 45, 60, 80, 100, 125, 150, 180, 210, ...
        // The gap grows by 5 every two milestones.
        public static int Threshold(int n)
        {
            int total = 0;
            for (int i = 0; i < n; i++) total += 5 * (i / 2 + 1);
            return total;
        }

        // Milestone 1 and every 5th: a blueprint of choice; every 10th: a Captain's chest; the rest rotate
        // tokens (20 + 5 x n), a crate and a sea chest.
        public static RenownReward Reward(int n)
        {
            if (n > 0 && n % 10 == 0) return new RenownReward { Kind = RenownRewardKind.Chest, Chest = ChestKind.CaptainsChest };
            if (n <= 1 || n % 5 == 0) return new RenownReward { Kind = RenownRewardKind.BlueprintChoice };
            int rest = n - 2 - (n - 1) / 5;
            return (rest % 3) switch
            {
                0 => new RenownReward { Kind = RenownRewardKind.Tokens, Tokens = 20 + 5 * n },
                1 => new RenownReward { Kind = RenownRewardKind.Chest, Chest = ChestKind.Crate },
                _ => new RenownReward { Kind = RenownRewardKind.Chest, Chest = ChestKind.SeaChest },
            };
        }
    }
}
