using System.Collections.Generic;

namespace Catchline.Game
{
    public enum NetKind { Shallow, Deep }
    public partial class GameState
    {
        public NetKind SelectedNet;
        // First entry is fitted, subsequent entries are reserves. No default free deep nets.
        public readonly List<int> DeepNetUses = new();
        public int ActiveNetStock => SelectedNet == NetKind.Deep ? DeepNetUses.Count : NetInventory;
        public string NetLoadoutLabel => SelectedNet == NetKind.Deep
            ? $"Deep net · {(DeepNetUses.Count > 0 ? DeepNetUses[0] : 0)}/3 uses · {DeepNetUses.Count} aboard · {NetCapacityKg:0}kg"
            : $"Shallow net · {NetInventory} aboard · {NetCapacityKg:0}kg";
        public bool BuyDeepNet()
        {
            if (DeepNetUses.Count >= GameData.DeepNetRackCapacity || Coins < GameData.DeepNetCost) return false;
            Coins -= GameData.DeepNetCost;
            DeepNetUses.Add(GameData.DeepNetUses);
            return true;
        }
        public void SpendDeepNetUse()
        {
            if (DeepNetUses.Count == 0) return;
            if (--DeepNetUses[0] <= 0) DeepNetUses.RemoveAt(0);
        }
    }
}
