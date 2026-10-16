// Install ONLY in Catchline-sim/Assets/Editor for a bounded delivery check.
// Never batchmode the main project. This source is not a runtime dependency.
using System;
using System.IO;
using System.Linq;
using Catchline.Game;
using Catchline.Prototype;
using UnityEditor.SceneManagement;
using UnityEngine;
namespace Catchline.EditorTools
{
    public static class EnvironmentDeliveryCheck
    {
        static void Check(bool ok, string message)
        {
            if (!ok) throw new Exception("Environment delivery failed: " + message);
        }
        public static void Run()
        {
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var game = new GameObject("Environment delivery check").AddComponent<VoyageGame>();
            game.SessionOnly = true; game.Build(); game.SetSail();
            for (int i=0; i<1000 && game.CurrentMode!=VoyageGame.Mode.Fishing; i++) game.Tick(.05f);
            Check(game.CurrentMode==VoyageGame.Mode.Fishing, "first spot arrival");
            game.Tick(4f);
            var env=UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsSortMode.None)
                .FirstOrDefault(t=>t.name=="GullHarbourMouth");
            Check(env!=null,"authored first spot instantiated");
            Check((env.localPosition-new Vector3(0,-.32f,0)).sqrMagnitude<.000001f,"waterline placement");
            Check(env.localScale==Vector3.one && Quaternion.Angle(env.localRotation,Quaternion.identity)<.001f,"identity placement");
            var names=env.GetComponentsInChildren<Transform>().Select(t=>t.name).ToArray();
            foreach(var name in new[]{"Shoreline","Seabed","Details","WorkingQuay_PlankedDeck_Joists","WorkingQuay_StackedSlattedCrates","WorkingQuay_DrapedFishingNet"})
                Check(names.Contains(name),"imported hierarchy: "+name);
            foreach(var t in env.GetComponentsInChildren<Transform>())
                if(t.name=="HarbourBeacon_IvoryOrange" || t.name=="WorkingQuay_PlankedDeck_Joists")
                    Debug.Log("[Catchline] ENV LANDMARK "+t.name+" center="+t.GetComponent<Renderer>().bounds.center.ToString("F5")+" local="+t.localPosition+" rotation="+t.localEulerAngles+" scale="+t.localScale);
            var beacon=env.GetComponentsInChildren<Transform>().First(t=>t.name=="HarbourBeacon_IvoryOrange").GetComponent<Renderer>();
            Check((beacon.bounds.center-new Vector3(5.253493f,.62080f,-.588815f)).sqrMagnitude<.000001f,"actual Unity handedness matches canonical landmark (no mirrored coast)");
            var quay=env.GetComponentsInChildren<Transform>().First(t=>t.name=="WorkingQuay_PlankedDeck_Joists").GetComponent<Renderer>();
            Check((quay.bounds.center-new Vector3(4.447486f,.2205f,2.450436f)).sqrMagnitude<.000001f,"quay world landmark matches authored camera plan");
            var meshes=env.GetComponentsInChildren<MeshFilter>();
            Check(meshes.Length==33,"33 imported model parts");
            ulong indices=0;
            foreach(var filter in meshes)
                for(int i=0;i<filter.sharedMesh.subMeshCount;i++)indices+=filter.sharedMesh.GetIndexCount(i);
            Check(indices/3<35000 && indices/3>30000,"bounded imported triangle count");
            var expected=Visuals.Mat(Palette.Steel).shader;
            foreach(var renderer in env.GetComponentsInChildren<Renderer>())
                Check(renderer.sharedMaterials.All(m=>m!=null && m.shader==expected),"all materials remapped to runtime shader: "+renderer.name);
            Directory.CreateDirectory("Logs/art011-working-quay");
            PrototypeTools.Render(game.Cam,Path.GetFullPath("Logs/art011-working-quay/Unity-desktop.png"),1440,900);
            PrototypeTools.Render(game.Cam,Path.GetFullPath("Logs/art011-working-quay/Unity-phone.png"),844,390);
            Debug.Log($"[Catchline] ENVIRONMENT DELIVERY PASSED: {meshes.Length} meshes, {indices/3} triangles; first-spot placement/materials; camera stills only (no IMGUI).");
        }
    }
}
