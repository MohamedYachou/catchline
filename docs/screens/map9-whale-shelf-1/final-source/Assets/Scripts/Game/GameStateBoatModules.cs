namespace Catchline.Game
{
    public partial class GameState
    {
        public const int SecondNetModuleCost = 2000;
        public bool SecondNetOwned, SecondNetEnabled;
        public bool SecondNetActive => Hull >= 3 && SecondNetOwned && SecondNetEnabled;
        public bool BuySecondNetModule()
        {
            if (Hull < 3 || SecondNetOwned || Coins < SecondNetModuleCost) return false;
            Coins -= SecondNetModuleCost;
            SecondNetOwned = SecondNetEnabled = true;
            return true;
        }
    }
}
