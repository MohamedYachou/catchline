using System;
using UnityEngine;

namespace Catchline.Game
{
    public sealed partial class CoastalCanvas
    {
        // Compose the kit's paper and navy header without falling back to the old titled panel.
        public RectTransform TitledSlabV3(string id, Rect r, Transform parent = null)
        {
            var slab = Slab(id, r, null, false, parent);
            Sliced(id + "/band", new Rect(3, 3, r.width - 6, Skin.HeaderBand + 6), "v2-slab-header", slab);
            return slab;
        }

        public void TabBarV3(string id, Rect r, string[] labels, string[] icons, int active, Action<int> select, string[] ids = null)
        {
            float gap = 12, w = (r.width - gap * (labels.Length - 1)) / labels.Length;
            for (int i = 0; i < labels.Length; i++)
            {
                int index = i; bool on = i == active;
                var tr = new Rect(r.x + i * (w + gap), r.y - (on ? 4 : 0), w, r.height);
                var e = Pressable($"{id}/{i}", tr, null, on ? "v2-btn-primary" : "v2-btn-card", on ? "v2-btn-primary-pressed" : "v2-btn-card-pressed", () => select(index), true);
                if (ids != null) Alias(ids[i], $"{id}/{i}");
                float iconSize = Phone ? 32 : 40;
                bool beside = tr.width > tr.height * 2.2f;
                if (beside)
                {
                    Icon($"{id}/{i}/icon", new Rect(16, (tr.height - 4 - iconSize) / 2, iconSize, iconSize), icons[i], e.Rect);
                    Text($"{id}/{i}/label", new Rect(24 + iconSize, 0, tr.width - 36 - iconSize, tr.height - 4), labels[i], Skin.Type.Heading, on ? Skin.Cream : Skin.Ink, TextAnchor.MiddleLeft, e.Rect);
                }
                else
                {
                    // A short phone tab still keeps its word under a smaller icon.
                    if (tr.height - iconSize - 14 < 26) iconSize = Mathf.Max(22, tr.height - 42);
                    Icon($"{id}/{i}/icon", new Rect((tr.width - iconSize) / 2, 5, iconSize, iconSize), icons[i], e.Rect);
                    Text($"{id}/{i}/label", new Rect(4, iconSize + 4, tr.width - 8, tr.height - iconSize - 10), labels[i], Skin.Type.Heading, on ? Skin.Cream : Skin.Ink, TextAnchor.MiddleCenter, e.Rect);
                }
            }
        }

        readonly TextGenerator wrappedMeasure = new();

        // Match Text's actual font, line spacing and accessibility scale when reserving notebook rows.
        public float WrappedHeight(string value, float width, Skin.Type type)
        {
            var face = Skin.IsDisplayFace(type) ? DisplayFont : BodyOverride ?? font;
            int size = Mathf.RoundToInt(Skin.Size(type) * TypeScale);
            return Mathf.Ceil(wrappedMeasure.GetPreferredHeight(value, new TextGenerationSettings
            {
                font = face, fontSize = size, fontStyle = FontStyle.Normal, lineSpacing = .9f,
                scaleFactor = 1, textAnchor = TextAnchor.UpperLeft, color = Color.white,
                generationExtents = new Vector2(width, 0), horizontalOverflow = HorizontalWrapMode.Wrap,
                verticalOverflow = VerticalWrapMode.Overflow, pivot = Vector2.zero
            })) + 4;
        }
    }
}
