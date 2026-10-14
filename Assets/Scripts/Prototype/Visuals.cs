using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Prototype
{
    // Placeholder art: every object is a coloured primitive.
    public static class Visuals
    {
        static readonly Dictionary<Color, Material> cache = new();
        static Material baseMaterial;
        static Font font;

        public static Material Mat(Color c)
        {
            if (cache.TryGetValue(c, out var m) && m != null) return m;
            if (baseMaterial == null)
            {
                baseMaterial = new Material(Shader.Find("Universal Render Pipeline/Lit"));
                baseMaterial.SetFloat("_Smoothness", 0.2f);
            }
            m = new Material(baseMaterial) { color = c };
            cache[c] = m;
            return m;
        }

        public static GameObject Prim(PrimitiveType type, string name, Transform parent, Vector3 localPos, Vector3 scale, Color c, bool keepCollider = false)
        {
            var go = GameObject.CreatePrimitive(type);
            go.name = name;
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos;
            go.transform.localScale = scale;
            go.GetComponent<Renderer>().sharedMaterial = Mat(c);
            if (!keepCollider) Kill(go.GetComponent<Collider>());
            return go;
        }

        public static GameObject Box(string name, Transform parent, Vector3 localPos, Vector3 size, Color c, bool keepCollider = false)
            => Prim(PrimitiveType.Cube, name, parent, localPos, size, c, keepCollider);

        public static TextMesh Label(string name, Transform parent, Vector3 localPos, float size)
        {
            if (font == null) font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = localPos;
            var tm = go.AddComponent<TextMesh>();
            tm.font = font;
            tm.fontSize = 64;
            tm.characterSize = size;
            tm.anchor = TextAnchor.LowerCenter;
            tm.alignment = TextAlignment.Center;
            tm.color = Color.white;
            go.GetComponent<MeshRenderer>().sharedMaterial = font.material;
            return tm;
        }

        public static void Kill(Object o)
        {
            if (o == null) return;
            if (Application.isPlaying) Object.Destroy(o);
            else Object.DestroyImmediate(o);
        }
    }
}
