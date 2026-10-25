using UnityEngine;

namespace Catchline.Game
{
    // Selling a haul pays out visibly: coins arc from the button that earned them into the wallet pill, which bumps as
    // each lands and counts up from the old balance. Purely presentation; the coins are already in the state.
    public partial class VoyageGame
    {
        const int CoinFxCount = 14;
        const float CoinFxStagger = .05f, CoinFxFlight = .7f;
        Rect coinFxFrom;
        float coinFxStart = -100;
        int coinFxBefore;
        int coinFxLanded;

        float CoinFxSeconds => CoinFxStagger * (CoinFxCount - 1) + CoinFxFlight;
        bool CoinFxActive => Time.unscaledTime - coinFxStart < CoinFxSeconds;

        void StartCoinFlight(string fromId, int before)
        {
            if (!coastalUi.TryFind(fromId, out coinFxFrom)) return;
            coinFxStart = Time.unscaledTime; coinFxBefore = before; coinFxLanded = 0;
        }

        // The balance a wallet pill shows: counts up while the coins are in the air.
        int ShownCoins
        {
            get
            {
                if (!CoinFxActive) return State.Coins;
                float landed = Mathf.Clamp01((Time.unscaledTime - coinFxStart - CoinFxFlight) / (CoinFxStagger * (CoinFxCount - 1) + .01f));
                return Mathf.RoundToInt(Mathf.Lerp(coinFxBefore, State.Coins, landed));
            }
        }

        void InterfaceCoinFx()
        {
            if (!CoinFxActive) return;
            string walletId = coastalUi.TryFind("shop/coins", out _) ? "shop/coins" : "port/coins";
            if (!coastalUi.TryFind(walletId, out var wallet)) return;
            float t = Time.unscaledTime - coinFxStart, size = compactInterface ? 26 : 34;
            Vector2 to = new Vector2(wallet.x + wallet.height * .55f, wallet.center.y);
            int landed = 0;
            for (int i = 0; i < CoinFxCount; i++)
            {
                string id = "coinfx/" + i;
                float k = (t - i * CoinFxStagger) / CoinFxFlight;
                if (k < 0 || k >= 1) { if (k >= 1) landed++; coastalUi.Icon(id, Rect.zero, null); continue; }
                // Each coin leaves from a spread across the button and arcs up and over into the wallet.
                float spread = ((i * 37) % CoinFxCount) / (float)(CoinFxCount - 1) - .5f;
                var from = new Vector2(coinFxFrom.center.x + spread * coinFxFrom.width * .6f, coinFxFrom.center.y);
                var control = new Vector2(Mathf.Lerp(from.x, to.x, .35f) + spread * 80, Mathf.Min(from.y, to.y) - 90 - 40 * Mathf.Abs(spread));
                float e = Ease.InCubic(k) * .45f + k * .55f, u = 1 - e;
                var p = u * u * from + 2 * u * e * control + e * e * to;
                float s = size * (k < .2f ? Mathf.Lerp(.6f, 1.1f, k / .2f) : Mathf.Lerp(1.1f, .7f, (k - .2f) / .8f));
                coastalUi.Icon(id, new Rect(p.x - s / 2, p.y - s / 2, s, s), "v2-icon-coin", null, null, "icon-coin");
                coastalUi.Pose(id, (1 - k) * 220 * (spread < 0 ? -1 : 1));
            }
            if (landed > coinFxLanded) { coinFxLanded = landed; audio?.Play(VoyageAudio.Cue.Coins, .12f); }
            // The wallet bumps on each landing.
            float since = landed == 0 ? 1 : (t - (landed - 1) * CoinFxStagger - CoinFxFlight) / .15f;
            coastalUi.Pose(walletId, 0, 1 + .07f * (1 - Ease.Clamp(since)));
        }
    }
}
