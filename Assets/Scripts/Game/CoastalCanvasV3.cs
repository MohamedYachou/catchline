using System;
using UnityEngine;

namespace Catchline.Game
{
    public sealed partial class CoastalCanvas
    {
        // Explicit source-pixel borders keep pins and dash caps intact when new kit art stretches.
        public void KitSliceV3(string id, Rect r, string art, Vector4 border, Transform parent = null)
        {
            string key = art + ":kit-border:" + border;
            if (!sprites.TryGetValue(key, out var sprite))
            {
                var texture = ArtLibrary.Get()?.UiTex(art);
                if (texture != null) sprite = UnityEngine.Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), Vector2.one * .5f, 100, 0, SpriteMeshType.FullRect, border);
                sprites[key] = sprite;
            }
            var e = Get(id, r, parent);
            if (e.Image == null) e.Image = e.Rect.gameObject.AddComponent<UnityEngine.UI.Image>();
            e.Image.sprite = sprite; e.Image.type = UnityEngine.UI.Image.Type.Sliced;
            e.Image.pixelsPerUnitMultiplier = 2;
            e.Image.preserveAspect = false; e.Image.color = Color.white; e.Image.raycastTarget = false;
        }

        // Compose the kit's paper and navy header without falling back to the old titled panel.
        public RectTransform TitledSlabV3(string id, Rect r, Transform parent = null)
        {
            var slab = Slab(id, r, null, false, parent);
            Sliced(id + "/band", new Rect(3, 3, r.width - 6, Skin.HeaderBand + 6), "v2-slab-header", slab);
            return slab;
        }

        void TitledSurfaceV3(string id)
        {
            var e = elements[id];
            e.Image.sprite = V2("v2-slab");
            e.Image.type = UnityEngine.UI.Image.Type.Sliced;
            e.Image.pixelsPerUnitMultiplier = 2;
            var band = Sliced(id + "/band", new Rect(3, 3, e.Rect.rect.width - 6, Skin.HeaderBand + 6), "v2-slab-header", e.Rect);
            band.SetAsFirstSibling();
        }

        public RectTransform SlabV3(string id, Rect r, string title = null, bool nails = false, Transform parent = null)
        {
            var slab = Slab(id, r, title, nails, parent);
            if (title != null) TitledSurfaceV3(id);
            return slab;
        }

        public RectTransform CardV3(string id, Rect r, Skin.Card kind = Skin.Card.Soft, Transform parent = null, string headerTitle = null)
        {
            var card = Card(id, r, kind, parent, headerTitle);
            if (headerTitle != null) TitledSurfaceV3(id);
            return card;
        }

        public void StageCardV3(string id, Rect r, string title, string icon, string illustration, string number, string unit,
            Skin.Status status, int queue, Action details, string lockReason = null, string detailsId = null)
        {
            StageCard(id, r, title, icon, illustration, number, unit, status, queue, details, lockReason, detailsId);
            TitledSurfaceV3(id);
        }

        public RectTransform ModalV3(string id, string title, string body, string primaryLabel, Action primary, string secondaryLabel, Action secondary,
            Action dismiss = null, string primaryIcon = null, float width = 560, float height = 300)
        {
            var slab = Modal(id, title, body, primaryLabel, primary, secondaryLabel, secondary, dismiss, primaryIcon, width, height);
            TitledSurfaceV3(id);
            return slab;
        }

        public void PageSwitchV3(string id, Rect r, string[] labels, int active, Action<int> select, string[] ids = null, Transform parent = null, bool[] enabled = null)
        {
            var capsule = Sliced(id, r, "v2-inset", parent, null, true);
            float w = (r.width - 8) / labels.Length;
            for (int i = 0; i < labels.Length; i++)
            {
                int index = i; bool on = i == active;
                string pid = ids != null ? ids[i] : $"{id}/{i}";
                bool live = enabled == null || enabled[i];
                var e = Pressable(pid, new Rect(4 + i * w, 4, w, r.height - 8), capsule,
                    on ? "v2-btn-primary" : null, on ? "v2-btn-primary-pressed" : null, () => select(index), live);
                if (!on) e.Image.color = Color.clear;
                Text($"{pid}/label", new Rect(8, 0, w - 16, r.height - 8), labels[i], Skin.Type.Heading,
                    on ? Skin.Cream : live ? Skin.Ink : Skin.InkSoft, TextAnchor.MiddleCenter, e.Rect);
            }
        }

        public void DutySlotV3(string id, Rect r, string header, string icon, string name, Action cycle, string hint = "Tap to cycle", Transform parent = null)
        {
            if (!Phone) { DutySlot(id, r, header, icon, name, cycle, hint, parent); TitledSurfaceV3(id); return; }
            var slab = CardV3(id, r, Skin.Card.Ink, parent, "");
            Text(id + "/title", new Rect(Skin.CardPad + 4, 4, r.width - 32, Skin.HeaderBand), header.ToUpperInvariant(), Skin.Type.Heading, Skin.Cream, TextAnchor.MiddleLeft, slab);
            float y = Skin.HeaderBand + 6, h = r.height - y - (hint != null ? 28 : 10), bw = r.width - 24;
            var e = Pressable(id + "/body", new Rect(12, y, bw, h), slab, "v2-card", "v2-btn-card-pressed", cycle, cycle != null);
            float s = Mathf.Min(32, h - 8), cw = cycle != null ? 40 : 0;
            Icon(id + "/body/icon", new Rect(8, (h - s) / 2, s * 1.2f, s), icon, e.Rect);
            Text(id + "/body/name", new Rect(s * 1.2f + 16, 0, bw - s * 1.2f - 24 - cw, h), name, Skin.Type.Heading, Skin.Ink, TextAnchor.MiddleLeft, e.Rect);
            Sliced(id + "/body/cycle", cycle != null ? new Rect(bw - 36, (h - 32) / 2, 32, 32) : Rect.zero, cycle != null ? "v2-btn-card" : null, e.Rect);
            Icon(id + "/body/cycle/icon", cycle != null ? new Rect(bw - 32, (h - 24) / 2, 24, 24) : Rect.zero, "v2-icon-cycle", e.Rect);
            if (hint != null) Text(id + "/hint", new Rect(12, r.height - 26, r.width - 24, 22), hint, Skin.Type.Small, Skin.Teal, TextAnchor.MiddleCenter, slab);
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
