using System;
using UnityEditor;
using UnityEngine;

namespace Catchline.EditorTools
{
    // HIFI import (HifiImport.cs): the probe crate in Assets/Art/Models/Hifi/_Probe must come out of import on a URP Lit
    // material carrying its baked BaseColor, Normal and Mask sets, with the right texture import types.
    static class HifiImportChecks
    {
        static void Check(bool pass, string label) { if (!pass) throw new Exception("HIFI import check failed: " + label); }

        public static void Run()
        {
            const string dir = HifiImport.Root + "/_Probe";
            HifiImport.Sync();
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(dir + "/HifiProbe.fbx");
            Check(model != null, "probe model imported");
            var r = model.GetComponentInChildren<Renderer>();
            Check(r != null, "probe has a renderer");
            var mat = r.sharedMaterial;
            Check(mat != null && mat.name == "MH_Probe", "remapped onto MH_Probe, got " + (mat == null ? "none" : mat.name));
            Check(AssetDatabase.GetAssetPath(mat) == dir + "/Materials/MH_Probe.mat", "material lives beside the model");
            Check(mat.shader.name == "Universal Render Pipeline/Lit", "URP Lit, got " + mat.shader.name);
            Check(mat.GetTexture("_BaseMap") != null && mat.GetTexture("_BaseMap").name == "Probe_BaseColor", "base colour set");
            Check(mat.GetTexture("_BumpMap") != null && mat.IsKeywordEnabled("_NORMALMAP"), "normal map on");
            Check(mat.GetTexture("_MetallicGlossMap") != null && mat.IsKeywordEnabled("_METALLICSPECGLOSSMAP"), "mask drives metallic and smoothness");
            Check(mat.GetTexture("_OcclusionMap") != null && mat.IsKeywordEnabled("_OCCLUSIONMAP"), "mask drives occlusion");
            var normal = (TextureImporter)AssetImporter.GetAtPath(dir + "/Textures/Probe_Normal.png");
            var mask = (TextureImporter)AssetImporter.GetAtPath(dir + "/Textures/Probe_Mask.png");
            var baseColor = (TextureImporter)AssetImporter.GetAtPath(dir + "/Textures/Probe_BaseColor.png");
            Check(normal.textureType == TextureImporterType.NormalMap, "normal imported as a normal map");
            Check(!mask.sRGBTexture && baseColor.sRGBTexture, "mask linear, base colour sRGB");
            Debug.Log("[Catchline] HIFI IMPORT CHECKS PASSED");
        }
    }
}
