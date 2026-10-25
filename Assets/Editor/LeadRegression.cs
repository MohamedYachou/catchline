using System;
using System.Linq;
using UnityEngine;

namespace Catchline.EditorTools
{
    // Runs every parameterless static Run() on the *Checks classes and logs one REG line each, so one batch
    // shows what a change broke. Batch: -executeMethod Catchline.EditorTools.LeadRegression.Run
    public static class LeadRegression
    {
        public static void Run()
        {
            var only = Environment.GetEnvironmentVariable("CATCHLINE_CHECKS");
            var types = typeof(LeadRegression).Assembly.GetTypes()
                .Where(t => t.Name.EndsWith("Checks") && (only == null || only.Split(',').Contains(t.Name)))
                .OrderBy(t => t.Name);
            int pass = 0, fail = 0;
            foreach (var t in types)
            {
                var run = t.GetMethod("Run", Type.EmptyTypes);
                if (run == null || !run.IsStatic) continue;
                try { run.Invoke(null, null); pass++; Debug.Log($"REG {t.Name} PASS"); }
                catch (Exception e) { fail++; Debug.Log($"REG {t.Name} FAIL {(e.InnerException ?? e).Message.Replace('\n', ' ')}"); }
            }
            Debug.Log($"REG SUMMARY pass {pass} fail {fail}");
        }
    }
}
