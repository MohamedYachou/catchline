using System;
using System.IO;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Per-suite entry points for check.ps1's generic written-report completion marker.
    // Exceptions propagate; a report is written only after the entire suite returns.
    public static class StaleChecks
    {
        static void Run(string item, Action check)
        {
            if (!Application.dataPath.Replace('\\', '/').EndsWith("Catchline-sim/Assets", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("STALE-CHECKS-1 runs only in Catchline-sim");
            check();
            Directory.CreateDirectory("Logs/stale-checks-1");
            string report = "Logs/stale-checks-1/" + item + ".txt";
            File.WriteAllText(report, item + " suite PASSED\nUTC " + DateTime.UtcNow.ToString("O") + "\n");
            Debug.Log("[Catchline] Snapshot written to " + report);
        }
        public static void Hud() => Run("1-hud", ReferenceHudChecks.Run);
        public static void Skiff() => Run("2-skiff", SkiffChecks.Run);
        public static void WeightNet() => Run("3-weight-net", WeightNetChecks.Run);
        public static void FirstVoyage() => Run("4-first-voyage", FirstVoyageChecks.Run);
        public static void Chart() => Run("5-chart", ChartChecks.Run);
    }
}
