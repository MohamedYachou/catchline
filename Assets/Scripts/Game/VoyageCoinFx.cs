using UnityEngine;

namespace Catchline.Game
{
    // Selling a haul pays out visibly: coins arc from the button that earned them into the wallet pill, which bumps as
    // each lands and counts up from the old balance. A purchase runs it backwards: a few coins leave the wallet (which
    // counts down) and land on what was bought, which flashes. Purely presentation; the coins are already in the state.
    public partial class VoyageGame
    {
        const int CoinFxCount = 14;
        const float CoinFxStagger = .05f, CoinFxFlight = .7f;
        Rect coinFxFrom;
        float coinFxStart = -100;
        int coinFxBefore;
        int coinFxLanded, coinFxN = CoinFxCount;
        bool coinFxSpend;
        string coinFxTarget;

        float CoinFxSeconds => CoinFxStagger * (coinFxN - 1) + CoinFxFlight;
        bool CoinFxActive => Time.unscaledTime - coinFxStart < CoinFxSeconds;

        void StartCoinFlight(string fromId, int before)
        {
            if (!coastalUi.TryFind(fromId, out coinFxFrom)) return;
            coinFxStart = Time.unscaledTime; coinFxBefore = before; coinFxLanded = 0; coinFxSpend = false; coinFxN = CoinFxCount;
        }

        // A purchase: coins fly from the wallet onto the bought item's card (toId), when anything was paid.
        void StartSpendFlight(string toId, int before)
        {
            if (State.Coins >= before || !coastalUi.TryFind(toId, out coinFxFrom)) return;
            coinFxStart = Time.unscaledTime; coinFxBefore = before; coinFxLanded = 0; coinFxSpend = true; coinFxTarget = toId; coinFxN = 8;
        }

        // The balance a wallet pill shows: counts up while the coins are in the air.
        int ShownCoins
        {
            get
            {
                if (!CoinFxActive) return State.Coins;
                // Paying, the balance drops as the coins leave; earning, it rises as they land.
                float t = Time.unscaledTime - coinFxStart - (coinFxSpend ? 0 : CoinFxFlight);
                float landed = Mathf.Clamp01(t / (CoinFxStagger * (coinFxN - 1) + .01f));
                return Mathf.RoundToInt(Mathf.Lerp(coinFxBefore, State.Coins, landed));
            }
        }

        void InterfaceCoinFx()
        {
            // Keep the last contact visible through its short tail, without extending the balance count.
            float elapsed = Time.unscaledTime - coinFxStart;
            float tail = coinFxSpend ? (HasUi("fx-buy-burst") ? Mathf.Max(CoinFxSeconds, CoinFxFlight + .45f) : CoinFxSeconds)
                : CoinFxSeconds + (HasUi("fx-coin-glint") ? .2f : 0);
            if (elapsed >= tail) return;
            string walletId = coastalUi.TryFind("shop/coins", out _) ? "shop/coins" : "port/coins";
            if (!coastalUi.TryFind(walletId, out var wallet)) return;
            float t = Time.unscaledTime - coinFxStart, size = compactInterface ? 26 : 34;
            Vector2 coinSlot = new Vector2(wallet.x + wallet.height * .55f, wallet.center.y);
            if (coinFxSpend && coastalUi.TryFind(coinFxTarget, out var target)) coinFxFrom = target;
            Rect source = coinFxSpend ? new Rect(coinSlot.x - 20, coinSlot.y - 10, 40, 20) : coinFxFrom;
            Vector2 to = coinFxSpend ? coinFxFrom.center : coinSlot;
            int landed = 0;
            for (int i = 0; i < CoinFxCount; i++)
            {
                string id = "coinfx/" + i;
                float k = (t - i * CoinFxStagger) / CoinFxFlight;
                if (i >= coinFxN || k < 0 || k >= 1) { if (i < coinFxN && k >= 1) landed++; coastalUi.Icon(id, Rect.zero, null); continue; }
                // Each coin leaves from a spread across the button and arcs up and over into the wallet.
                float spread = ((i * 37) % CoinFxCount) / (float)(CoinFxCount - 1) - .5f;
                var from = new Vector2(source.center.x + spread * source.width * .6f, source.center.y);
                // Paying, they fan out of the wallet and fall in a shallow arc onto the item instead of climbing first.
                var control = coinFxSpend
                    ? new Vector2(Mathf.Lerp(from.x, to.x, .3f) + spread * 70, Mathf.Lerp(from.y, to.y, .15f) - 30)
                    : new Vector2(Mathf.Lerp(from.x, to.x, .35f) + spread * 80, Mathf.Min(from.y, to.y) - 90 - 40 * Mathf.Abs(spread));
                float e = Ease.InCubic(k) * .45f + k * .55f, u = 1 - e;
                var p = u * u * from + 2 * u * e * control + e * e * to;
                float s = size * (k < .2f ? Mathf.Lerp(.6f, 1.1f, k / .2f) : Mathf.Lerp(1.1f, .7f, (k - .2f) / .8f));
                coastalUi.Icon(id, new Rect(p.x - s / 2, p.y - s / 2, s, s), "v2-icon-coin", null, null, "icon-coin");
                coastalUi.Pose(id, (1 - k) * 220 * (spread < 0 ? -1 : 1));
            }
            if (CoinFxActive && landed > coinFxLanded) { coinFxLanded = landed; audio?.Play(VoyageAudio.Cue.CoinLand, .12f); }
            // Earning, the wallet bumps on each landing; paying, the bought item glows as the coins arrive.
            float since = landed == 0 ? 1 : (t - (landed - 1) * CoinFxStagger - CoinFxFlight) / .15f;
            if (!coinFxSpend) coastalUi.Pose(walletId, 0, 1 + .07f * (1 - Ease.Clamp(since)));
            else coastalUi.Icon("coinfx/flash", landed == 0 ? Rect.zero : new Rect(coinFxFrom.x - coinFxFrom.width * .15f, coinFxFrom.y - coinFxFrom.height * .15f, coinFxFrom.width * 1.3f, coinFxFrom.height * 1.3f),
                "fx-glow", null, new Color(1f, .85f, .4f, .8f * (1 - Ease.Clamp((t - CoinFxFlight) / CoinFxSeconds))));
            // One retained glint restarts on each contact; overlapping coins never stack flashes.
            if (!coinFxSpend && landed > 0 && HasUi("fx-coin-glint"))
            {
                float age = t - CoinFxFlight - (landed - 1) * CoinFxStagger;
                if (age >= 0 && age < .2f)
                {
                    // Follow the wallet's current bump, including its scaled coin slot.
                    coastalUi.TryFind(walletId, out var posedWallet);
                    var glintSlot = coastalUi.TryFind(walletId + "/coin", out var coinIcon) ? coinIcon.center
                        : new Vector2(posedWallet.x + posedWallet.height * .55f, posedWallet.center.y);
                    float k = age / .2f, s = (compactInterface ? 30 : 40) * Mathf.Lerp(.6f, 1.15f, Ease.OutCubic(k));
                    coastalUi.Icon("coinfx/glint", new Rect(glintSlot.x - s / 2, glintSlot.y - s / 2, s, s),
                        "fx-coin-glint", null, new Color(1, 1, 1, 1 - k));
                    coastalUi.Pose("coinfx/glint", Mathf.Lerp(-12, 12, k));
                }
            }
            // The first purchase contact owns the burst clock, above the existing gold glow.
            float burst = (t - CoinFxFlight) / .45f;
            if (coinFxSpend && burst >= 0 && burst < 1 && HasUi("fx-buy-burst"))
            {
                float basis = Mathf.Clamp(Mathf.Min(coinFxFrom.width, coinFxFrom.height) * 1.8f, compactInterface ? 80 : 110, compactInterface ? 140 : 200);
                float s = basis * Mathf.Lerp(.6f, 1.3f, Ease.OutCubic(burst));
                coastalUi.Icon("coinfx/burst", new Rect(to.x - s / 2, to.y - s / 2, s, s),
                    "fx-buy-burst", null, new Color(1, 1, 1, 1 - burst));
            }
        }
    }
}
