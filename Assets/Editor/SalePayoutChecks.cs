using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Catchline.Game;
using UnityEngine;
namespace Catchline.EditorTools
{
    public static class SalePayoutChecks
    {
        static void Check(bool ok,string message)
        {
            if(!ok)throw new Exception("[Catchline] First voyage check failed: sale payout "+message);
        }
        public static void Run()
        {
            var state=new GameState(9);
            state.Coins=5;
            var pollock=new Contract {Species=Species.Pollock,Count=5,Delivered=0,VoyagesLeft=2,Reward=125};
            state.Active.Add(pollock);
            var haul=new List<CaughtFish>();
            for(int i=0;i<3;i++)haul.Add(new CaughtFish {Species=Species.Pollock,Kg=1.2f});
            int originalCoins=state.Coins;
            float originalPrice=state.Market[(int)Species.Pollock];
            var quote=state.QuoteSale(haul,0);
            Check(quote.Coins>0 && quote.ToContracts==3 && quote.ContractCoins==0,"partial contract haul still earns market coins");
            Check(state.Coins==originalCoins && pollock.Delivered==0 && state.Market[(int)Species.Pollock]==originalPrice,"counter quote does not consume progress or money");
            var sale=state.Sell(haul,0);
            Check(sale.Coins==quote.Coins && state.Coins==originalCoins+quote.Coins && sale.FishSold==3,"every fish paid, including contract fish");
            state.EndVoyage(sale);
            Check(pollock.Delivered==3 && pollock.VoyagesLeft==1,"partial contract persists alongside real payout");
            haul.RemoveAt(0);
            quote=state.QuoteSale(haul,0);
            originalCoins=state.Coins;
            sale=state.Sell(haul,0);
            Check(sale.Coins>0 && sale.ContractCoins==125 && sale.Coins+sale.ContractCoins==quote.Coins+quote.ContractCoins,"completion pays market plus bonus, exact counter");
            Check(state.Coins==originalCoins+sale.Coins+125 && !state.Active.Contains(pollock),"completion bonus paid once");
            sale=state.Sell(new List<CaughtFish>(),0);
            Check(sale.Coins==0 && sale.ContractCoins==0,"empty sale cannot pay completion twice");
            state.Active.Add(new Contract {Species=Species.Mackerel,Count=8,VoyagesLeft=1,Reward=100});
            haul.Clear();haul.Add(new CaughtFish {Species=Species.Mackerel,Kg=.3f});
            sale=state.Sell(haul,10000);state.EndVoyage(sale);
            Check(sale.Coins>=1 && state.Active.Count==0,"even degrading fish on expiring partial contract earn coins");
            // A live state made before Mo's credit must preserve that credit on its next save.
            string path=Path.GetFullPath("Logs/sale-payout-credit-test.json");
            try
            {
                var live=new GameState(7);live.Coins=5;live.Save(path);
                var credited=GameState.Load(path);credited.Coins+=100;
                credited.CoinCredits.Add(new GameState.CoinCredit {Id="test-credit-once",Amount=100});credited.Save(path);
                live.Save(path);
                Check(live.Coins==105 && live.CoinCredits.Count==1,"stale live save preserves authorized credit");
                live.Save(path);
                var reloaded=GameState.Load(path);
                Check(reloaded.Coins==105 && reloaded.CoinCredits.Count==1,"credit does not duplicate on save/reload");
            }
            finally {if(File.Exists(path))File.Delete(path);}
            Debug.Log("[Catchline] SALE PAYOUT CHECKS PASSED: unfinished/finished/expired contracts pay every fish; quote exact; bonus/credit once");
        }
    }
}
