using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Prototype
{
    // A pile of one item type at a station. Reserved and Incoming are promises made
    // by workers on their way, so two workers never grab the same crab or the last free slot.
    public class ItemBuffer
    {
        public readonly ItemType Type;
        public readonly int Capacity;
        public int Count { get; private set; }
        public int Reserved;
        public int Incoming;

        public int Available => Count - Reserved;
        public int Space => Capacity - Count - Incoming;
        public float Fill => (float)Count / Capacity;

        readonly Transform anchor;
        readonly List<GameObject> pile = new();

        public ItemBuffer(ItemType type, int capacity, Transform anchor)
        {
            Type = type;
            Capacity = capacity;
            this.anchor = anchor;
        }

        // A worker picks up an item they reserved.
        public void Take() { Reserved--; Count--; Refresh(); }
        // A worker drops an item into a slot they reserved.
        public void Deliver() { Incoming--; Count++; Refresh(); }
        // Station work consumes a reserved input.
        public void Consume() { Reserved--; Count--; Refresh(); }
        // Station work produces n items into space it reserved for `promised`.
        public void Produce(int n, int promised) { Incoming -= promised; Count = Mathf.Min(Capacity, Count + n); Refresh(); }

        public void Clear() { Count = 0; Reserved = 0; Refresh(); }

        void Refresh()
        {
            if (anchor == null) return;
            while (pile.Count < Count) pile.Add(Spawn(pile.Count));
            while (pile.Count > Count)
            {
                Visuals.Kill(pile[^1]);
                pile.RemoveAt(pile.Count - 1);
            }
        }

        GameObject Spawn(int i)
        {
            var size = Items.SizeOf(Type);
            int per = Items.PerLayer(Type);
            int layer = i / per, slot = i % per;
            var pos = new Vector3(0f, layer * (size.y + 0.01f) + size.y / 2f, 0f);
            if (per == 4)
            {
                pos.x = ((slot % 2) - 0.5f) * (size.x + 0.03f);
                pos.z = ((slot / 2) - 0.5f) * (size.z + 0.03f);
            }
            return Visuals.Box(Type.ToString(), anchor, pos, size, Items.ColorOf(Type));
        }
    }
}
