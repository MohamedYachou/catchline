using System;
using System.Collections.Generic;
using System.Reflection;
using Catchline.Game;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Net repair: the zigzag trace grades clean / ragged / none, a clean mend puts a torn net back on the rack, and the
    // harbour offers it only with a torn net and rack space.
    // Batch: -executeMethod Catchline.EditorTools.RepairChecks.Run
    public static class RepairChecks
    {
        static void Check(bool ok, string what) { if (!ok) throw new Exception("REPAIR: " + what); }

        public static List<Vector2> Trace(float offset = 0, float upTo = 1)
        {
            var trace = new List<Vector2>();
            var p = MendRules.Path;
            for (int i = 1; i < p.Length; i++)
                for (int k = 0; k < 10; k++)
                {
                    var d = (p[i] - p[i - 1]).normalized; // offset square to each leg
                    var q = Vector2.Lerp(p[i - 1], p[i], k / 10f) + new Vector2(-d.y, d.x) * offset;
                    if ((i - 1 + k / 10f) / (p.Length - 1) <= upTo) trace.Add(q);
                }
            if (upTo >= 1) trace.Add(p[p.Length - 1]);
            return trace;
        }

        public static VoyageGame Fixture()
        {
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("Repair check").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
            typeof(VoyageGame).GetField("showTitle", BindingFlags.Instance | BindingFlags.NonPublic).SetValue(g, false);
            g.State.Hull = 2; g.State.NetInventory = 2; g.State.TornNets = 1;
            typeof(VoyageGame).GetMethod("RebuildBoat", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(g, new object[] { false });
            for (int i = 0; i < 40; i++) g.Tick(.05f);
            return g;
        }

        public static void Run()
        {
            try
            {
                Check(MendRules.Grade(Trace()) == MendGrade.Clean, "a trace along the zigzag is clean");
                Check(MendRules.Grade(Trace(.09f)) == MendGrade.Ragged, "a trace well off the zigzag is ragged");
                Check(MendRules.Grade(Trace(0, .2f)) == MendGrade.None, "a short scratch does not count");
                Check(MendRules.Grade(new List<Vector2> { MendRules.Path[0], MendRules.Path[MendRules.Path.Length - 1] }) != MendGrade.Clean, "a straight line across the hole is not a mend");
                Check(MendRules.Grade(Trace(0, .7f)) == MendGrade.Ragged, "stopping two thirds of the way is not a mend");

                ArtImport.BuildLibrary();
                Check(ArtLibrary.Get().M("RepairKit") != null, "RepairKit model");
                var g = Fixture();
                Check(g.BeginMend(), "mend opens in harbour with a torn net");
                for (int i = 0; i < 12; i++) g.Tick(.05f);
                Check(g.RepairViewActive, "repair view open");
                Check(g.TraceMend(Trace(.09f)) == MendGrade.Ragged && g.State.TornNets == 1 && g.State.NetInventory == 2, "a ragged mend keeps the net torn");
                Check(g.TraceMend(Trace()) == MendGrade.Clean, "clean mend");
                Check(g.State.TornNets == 0 && g.State.NetInventory == 3, "the mended net is back on the rack: " + g.State.NetInventory);
                for (int i = 0; i < 60; i++) g.Tick(.05f);
                Check(!g.RepairViewActive, "the view returns to the harbour after a mend");
                Check(!g.BeginMend(), "nothing to mend without a torn net");
                g.State.TornNets = 1; g.State.NetInventory = GameData.NetInventoryCapacity;
                Check(!g.BeginMend(), "no mending onto a full rack");
                UnityEngine.Object.DestroyImmediate(g.gameObject);
                Debug.Log("REPAIR PASS · clean/ragged/short/straight/partial grades, mend restores a net, harbour gating");
                EditorApplication.Exit(0);
            }
            catch (Exception e) { Debug.LogError(e); EditorApplication.Exit(1); }
        }
    }
}
