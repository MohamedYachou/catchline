using UnityEngine;

namespace Catchline.Game
{
    // References to the imported models (filled by Catchline > Rebuild Art Library).
    // Anything left empty falls back to the primitive placeholder.
    [CreateAssetMenu(menuName = "Catchline/Art Library")]
    public class ArtLibrary : ScriptableObject
    {
        public GameObject Rowboat, FishingRod, Bobber, Cooler, IceBox, BaitBucket, LunchTin;
        public GameObject Quay, QuayLadder, Bollard, LampPost, HouseA, HouseB, Lighthouse, RockA, RockB, RockC, Kelp;
        public GameObject[] Fish = new GameObject[7]; // indexed by Species
        public Texture2D[] Ui;                         // Codex's UI kit, looked up by file name
        public Font UiFont;
        public Font DisplayFont;                       // Lilita One: UI v2 display, numbers, headings
        public GameObject[] Models;                    // every FBX under Assets/Art/Models, looked up by file name
        public AnimationClip[] CrewClips;
        public Shader WaterShader;
        public Texture2D WaterRipples, WaterCrossing;
        public Texture2D PtsWaterNormals, PtsWaterDither;
        public Texture2D[] WaterTextures;
        public Texture2D WaterTex(string name) => WaterTextures == null ? null : System.Array.Find(WaterTextures, t => t != null && t.name == name);
        public TextAsset[] NavigationFiles;            // map ids are read from JSON; real files preferred over interim
        public TextAsset[] StationFiles;               // Assets/Art/Models/Boats/<Model>.stations.json (deck graph, MASTER-PLAN B2)
        public TextAsset StationFile(string model) => StationFiles == null ? null : System.Array.Find(StationFiles, t => t != null && t.name == model + ".stations");

        System.Collections.Generic.Dictionary<string, Texture2D> uiByName;
        System.Collections.Generic.Dictionary<string, GameObject> modelByName;

        // Any model by its FBX file name ("Barrel", "ShopFront_Chandlery"); null when Codex hasn't delivered it yet.
        public GameObject M(string name)
        {
            if (modelByName == null)
            {
                modelByName = new();
                if (Models != null)
                    foreach (var m in Models)
                        if (m != null) modelByName[m.name] = m;
            }
            return modelByName.TryGetValue(name, out var go) ? go : null;
        }

        public Texture2D UiTex(string name)
        {
            if (uiByName == null)
            {
                uiByName = new();
                if (Ui != null)
                    foreach (var t in Ui)
                        if (t != null) uiByName[t.name] = t;
            }
            string replacement = GeminiUiSkin.Asset(name);
            if (replacement != null && uiByName.TryGetValue(replacement, out var skin)) return skin;
            return uiByName.TryGetValue(name, out var tex) ? tex : null;
        }

        static ArtLibrary cached;
        static bool looked;

        public static ArtLibrary Get()
        {
            if (!looked || cached == null)
            {
                looked = true;
                cached = Resources.Load<ArtLibrary>("ArtLibrary");
            }
            return cached;
        }

        public GameObject FishFor(Species s) => Fish != null && (int)s < Fish.Length ? Fish[(int)s] : null;

        public static GameObject Spawn(GameObject prefab, Transform parent, Vector3 localPos, Quaternion localRot, float scale = 1f)
        {
            if (prefab == null) return null;
            var go = Instantiate(prefab, parent, false);
            go.name = prefab.name;
            go.transform.localPosition = localPos;
            go.transform.localRotation = localRot;
            go.transform.localScale = Vector3.one * scale;
            foreach (var c in go.GetComponentsInChildren<Collider>()) Prototype.Visuals.Kill(c);
            RemapMaterials(go);
            return go;
        }

        // Codex names every material after a STYLE.md palette colour. Swap them for the game's own URP
        // materials so models look right regardless of FBX import settings or import order.
        static readonly System.Collections.Generic.Dictionary<string, string> PaletteHex = new()
        {
            ["M_HullNavy"] = "173F57", ["M_SafetyOrange"] = "E36A35", ["M_RailIvory"] = "F3F0DC", ["M_Rope"] = "D1AF76",
            ["M_Steel"] = "8FA6AC", ["M_Rubber"] = "28343B", ["M_SeaTeal"] = "168F9F", ["M_BandIvory"] = "F3DEA1",
            ["M_DeckWood"] = "C58B50", ["M_WoodHighlight"] = "DFB77A", ["M_WoodRecess"] = "8C5A36", ["M_HullBlue"] = "2A6685",
            ["M_OilskinYellow"] = "E6AD38", ["M_Skin"] = "B9784B", ["M_KelpGreen"] = "477A56", ["M_FishSilver"] = "BAC9C6",
            ["M_HairChestnut"] = "50392E", ["M_HairSilver"] = "ADB6AF",
            ["M_SpotBlue"] = "38B6FF", ["M_Crimson"] = "A9433C",
            ["M_CoastStone"] = "A99A7C", ["M_CoastStoneLight"] = "C9B89A", ["M_CoastWet"] = "696F64",
            ["M_CoastGrass"] = "729053", ["M_CoastGrassLight"] = "98A96B", ["M_CoastSand"] = "D9C393", ["M_SeabedSand"] = "BEA77D",
        };

        static void RemapMaterials(GameObject go)
        {
            foreach (var r in go.GetComponentsInChildren<Renderer>())
            {
                var mats = r.sharedMaterials;
                for (int i = 0; i < mats.Length; i++)
                {
                    if (mats[i] == null)
                    {
                        mats[i] = Prototype.Visuals.Mat(Palette.Steel);
                        continue;
                    }
                    string n = mats[i].name.Replace(" (Instance)", "");
                    int m = n.IndexOf("M_", System.StringComparison.Ordinal);
                    if (m > 0) n = n.Substring(m); // imported as "Rowboat-M_DeckWood"
                    int dot = n.IndexOf('.');
                    if (dot > 0) n = n.Substring(0, dot); // Blender duplicates: M_Rope.001
                    if (PaletteHex.TryGetValue(n, out var hex)) mats[i] = Prototype.Visuals.Mat(Palette.Hex(hex));
                }
                r.sharedMaterials = mats;
            }
        }

        // Points a long model (like the rod) from its pivot along a local direction with a given length,
        // whatever axis it was modelled along: the longest side of its bounds is taken as "along".
        public static void AimAlong(GameObject go, Vector3 localDir, float length)
        {
            go.transform.localRotation = Quaternion.identity;
            go.transform.localScale = Vector3.one;
            // Bounds of all meshes in the model's own space (pure math: no dependency on renderer updates).
            var toLocal = go.transform.worldToLocalMatrix;
            bool any = false;
            var b = new Bounds();
            foreach (var mf in go.GetComponentsInChildren<MeshFilter>())
            {
                if (mf.sharedMesh == null) continue;
                var m = toLocal * mf.transform.localToWorldMatrix;
                var mb = mf.sharedMesh.bounds;
                for (int i = 0; i < 8; i++)
                {
                    var corner = mb.center + Vector3.Scale(mb.extents, new Vector3((i & 1) == 0 ? -1 : 1, (i & 2) == 0 ? -1 : 1, (i & 4) == 0 ? -1 : 1));
                    var p = m.MultiplyPoint3x4(corner);
                    if (!any) { b = new Bounds(p, Vector3.zero); any = true; }
                    else b.Encapsulate(p);
                }
            }
            if (!any) return;
            var ext = b.extents;
            Vector3 axis = ext.x >= ext.y && ext.x >= ext.z ? Vector3.right : ext.y >= ext.z ? Vector3.up : Vector3.forward;
            if (Vector3.Dot(b.center, axis) < 0f) axis = -axis; // the long side runs away from the pivot (the butt)
            float size = 2f * Vector3.Dot(ext, new Vector3(Mathf.Abs(axis.x), Mathf.Abs(axis.y), Mathf.Abs(axis.z)));
            go.transform.localRotation = Quaternion.FromToRotation(axis, localDir.normalized);
            if (size > 0.01f) go.transform.localScale = Vector3.one * (length / size);
        }

        public static Transform Find(GameObject root, string name)
        {
            if (root == null) return null;
            foreach (var t in root.GetComponentsInChildren<Transform>(true))
                if (t.name == name) return t;
            return null;
        }
    }
}
