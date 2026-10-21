using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Catchline.Game
{
    public partial class VoyageGame
    {
        public NetCatchReceipt LastNetReceipt { get; private set; }
        float netReceiptUntil;
        const float CatchDisplaySeconds = 6, NetReceiptSeconds = 11;
        static readonly Color RewardWhite = Palette.Hex("F4F1E8");
        static readonly Color RewardMuted = Palette.Hex("B3CAD2");

        void RecordStoredNet(IEnumerable<CaughtFish> stored)
        {
            var receipt = new NetCatchReceipt(stored, State, SimTime);
            if (receipt.Count == 0) return;
            LastNetReceipt = receipt;
            netReceiptUntil = SimTime + NetReceiptSeconds;
        }
        void ResetCatchReceipts() { LastNetReceipt = null; netReceiptUntil = 0; }
        void RewardSurface(string id, Rect r, Color accent, bool halo = false, float alpha = 1)
        {
            var rect = coastalUi.Box(id, r, "", Color.clear, blocks: false);
            // UGUI permits only one Graphic on each object. Keep the retained
            // element as its lifecycle/position owner and draw in a fill child.
            var surface = rect.Find("Reward surface") as RectTransform;
            if (surface == null)
            {
                surface = new GameObject("Reward surface", typeof(RectTransform), typeof(CanvasRenderer), typeof(CatchRewardGraphic)).GetComponent<RectTransform>();
                surface.gameObject.layer = 5;
                surface.SetParent(rect, false);
                surface.anchorMin = Vector2.zero; surface.anchorMax = Vector2.one;
                surface.offsetMin = surface.offsetMax = Vector2.zero;
            }
            var graphic = surface.GetComponent<CatchRewardGraphic>();
            graphic.Style(accent, halo, alpha);
        }
        void RewardText(string id, Rect r, string text, int size, Color color, TextAnchor anchor = TextAnchor.MiddleLeft)
            => coastalUi.Label(id, r, text, size, color, anchor, fitted: true);
        void InterfaceCatchRewards()
        {
            if (SimTime < catchUntil) InterfaceCatchSpecimen();
            if (LastNetReceipt == null) return;
            if (SimTime < netReceiptUntil) InterfaceNetReceipt();
            else
            {
                var review = new Rect(16, ih - 62, 238, 44);
                IButton("catch/net/review", review, $"Last net · {LastNetReceipt.Count} fish", () => netReceiptUntil = SimTime + NetReceiptSeconds, false);
            }
        }
        void InterfaceCatchSpecimen()
        {
            var tier=CatchPresentation.Tier(lastCatchSpecies,lastCatchKg);
            var accent=CatchPresentation.Accent(tier);
            float elapsed=CatchDisplaySeconds-(catchUntil-SimTime);
            float enter=1-Mathf.Pow(1-Mathf.Clamp01(elapsed/.28f),3);
            float width=compactInterface?344:376,height=width*288/688;
            var r=new Rect(16,ih-height-78+(1-enter)*12,width,height);
            string title=catchNew?"New species!":catchRecord?"Personal best!":"Nice catch!";
            DrawGeminiCatch("catch",r,lastCatchSpecies,lastCatchKg,title);
        }
        void DrawGeminiCatch(string id,Rect r,Species species,float kg,string title)
        {
            var tier=CatchPresentation.Tier(species,kg);
            float width=r.width;
            coastalUi.Art(id,r,GeminiUiSkin.Card(tier));Block(r);
            float k=width/688f;
            Rect Part(float x,float y,float w,float h)=>new Rect(r.x+x*k,r.y+y*k,w*k,h*k);
            void Text(string key,Rect box,string text,int size,Color color,TextAnchor align=TextAnchor.MiddleLeft) =>
                RewardText(key,box,text,Mathf.RoundToInt(size*width/376f),color,align);
            // All portrait pixels stay within the original left window; typography is live and hard-clipped.
            coastalUi.Art(id+"/portrait",Part(60,61,179,173),FishPortrait(species));
            var ink=tier==CatchTier.Mythical?RewardWhite:Palette.HullNavy;
            Text(id+"/tier",Part(286,50,201,26),CatchPresentation.Label(tier),12,Palette.Cream,TextAnchor.MiddleCenter);
            Text(id+"/achievement",Part(515,50,121,26),title,10,Palette.Cream,TextAnchor.MiddleCenter);
            Text(id+"/name",Part(282,86,353,48),GameData.Get(species).Name,23,ink);
            Text(id+"/weight",Part(290,147,150,36),$"{kg:0.00} kg",19,ink);
            Text(id+"/quality",Part(479,147,154,36),CatchPresentation.IsBig(species,kg)?"Big specimen":"Coastal catch",12,ink);
            Text(id+"/note",Part(284,205,165,33),"Est. sale value",11,tier==CatchTier.Mythical?RewardMuted:SeaInk);
            int value=State.ValueOf(new CaughtFish{Species=species,Kg=kg,StowedAt=SimTime},SimTime);
            coastalUi.Art(id+"/coin",Part(482,208,26,26),"icon-coin");
            Text(id+"/value",Part(518,204,112,33),$"~{value:N0}",20,Palette.Cream,TextAnchor.MiddleRight);
        }
        public void PrepareGeminiCardPreview(int width,int height,Species species,float kg)
        {
            if(coastalUi==null)coastalUi=CoastalCanvas.Create(transform,Cam);
            coastalUi.Begin(width,height,1,new Rect(0,0,width,height));
            iw=coastalUi.Width;ih=coastalUi.Height;
            DrawGeminiCatch("preview",new Rect(0,0,iw,ih),species,kg,"Nice catch!");coastalUi.End();
        }
        public void RenderGeminiPreview(RenderTexture target) => coastalUi.RenderCapture(target);
        void InterfaceNetReceipt()
        {
            var receipt = LastNetReceipt;
            var groups = receipt.Items.GroupBy(f => (f.Species, f.Tier)).OrderByDescending(g => g.Key.Tier).ThenBy(g => g.Key.Species).ToList();
            bool small = compactInterface;
            float row = small ? 30 : 40, header = small ? 42 : 54, footer = small ? 32 : 42;
            // A future five-species batch still clears the left instruments on phones.
            float available = ih - 26 - ReferenceRect(20, 416, 260, 72).yMax;
            if (small && groups.Count > 0) row = Mathf.Min(row, (available - header - footer) / groups.Count);
            float height = header + groups.Count * row + footer;
            float width = small ? 266 : 288;
            float elapsed = NetReceiptSeconds - (netReceiptUntil - SimTime);
            float enter = 1 - Mathf.Pow(1 - Mathf.Clamp01(elapsed / .28f), 3);
            var r = new Rect(16, ih - height - 14 + (1 - enter) * 12, width, height);
            RewardSurface("catch/net", r, Palette.Hex("78C8BB")); Block(r);
            coastalUi.Art("catch/net/icon", new Rect(r.x + 13, r.y + (small ? 9 : 14), 27, 27), "icon-net");
            RewardText("catch/net/title", new Rect(r.x + 49, r.y + 7, width - 65, small ? 27 : 29), "Net catch stowed", small ? 20 : 22, RewardWhite);
            if (!small) RewardText("catch/net/subtitle", new Rect(r.x + 49, r.y + 33, width - 65, 18), "Safely in your hold", 12, RewardMuted);
            for (int i = 0; i < groups.Count; i++)
            {
                var group = groups[i]; var tier = group.Key.Tier;
                float y = r.y + header + i * row;
                var accent = CatchPresentation.Accent(tier);
                RewardSurface($"catch/net/{i}/glow", new Rect(r.x + 8, y, 61, row), accent, true);
                coastalUi.Art($"catch/net/{i}/portrait", new Rect(r.x + 12, y + 3, 54, row - 6), FishPortrait(group.Key.Species));
                string label = GameData.Get(group.Key.Species).Name + (group.Count() > 1 ? $" ×{group.Count()}" : "");
                if (small)
                {
                    RewardText($"catch/net/{i}/name", new Rect(r.x + 76, y, width - 140, row), label, 15, RewardWhite);
                    RewardText($"catch/net/{i}/weight", new Rect(r.xMax - 62, y, 46, row), $"{group.Sum(f => f.Kg):0.00} kg", 12, RewardMuted, TextAnchor.MiddleRight);
                }
                else
                {
                    RewardText($"catch/net/{i}/name", new Rect(r.x + 76, y, width - 148, row * .6f), label, 17, RewardWhite);
                    RewardText($"catch/net/{i}/weight", new Rect(r.x + 76, y + row * .55f, width - 148, row * .45f), $"{group.Sum(f => f.Kg):0.00} kg", 12, RewardMuted);
                    RewardText($"catch/net/{i}/value", new Rect(r.xMax - 66, y, 50, row), $"~{group.Sum(f => f.Value)}", 18, accent, TextAnchor.MiddleRight);
                }
            }
            float fy = r.yMax - footer;
            coastalUi.Box("catch/net/divider", new Rect(r.x + 16, fy + 1, width - 32, 1), "", new Color(.7f, .85f, .87f, .16f), blocks: false);
            RewardText("catch/net/total", new Rect(r.x + 16, fy + 5, width - 103, footer - 9), $"{receipt.Count} fish · {receipt.Kg:0.00} kg", small ? 13 : 15, RewardMuted);
            coastalUi.Art("catch/net/coin", new Rect(r.xMax - 88, fy + (footer - 18) * .5f, 18, 18), "icon-coin");
            RewardText("catch/net/value", new Rect(r.xMax - 65, fy + 3, 49, footer - 6), $"~{receipt.Value}", small ? 18 : 21, RewardWhite, TextAnchor.MiddleRight);
        }
    }
}
