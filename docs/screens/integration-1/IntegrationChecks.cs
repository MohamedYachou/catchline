using System;
using System.IO;
using UnityEngine;
namespace Catchline.EditorTools {
 public static class IntegrationChecks {
  public static void Run() {
   var output=Path.GetFullPath("../Catchline/docs/screens/integration-1");
   Directory.CreateDirectory(output);
   File.WriteAllText(Path.Combine(output,"suites.tsv"),"suite\tresult\n");
   Test("CrewCardsAbilityChecks.Regression",CrewCardsAbilityChecks.Regression);
   Test("WhaleShelfMapChecks.Run",WhaleShelfMapChecks.Run);
   Test("SealCliffsMapChecks.Run",SealCliffsMapChecks.Run);
   Test("StrikeFxCapture.Run",StrikeFxCapture.Run);
   Test("PetsCapture.Run",PetsCapture.Run);
   SealCliffsMapChecks.BuildNative();
   Debug.Log("[Catchline] INTEGRATION DRIVER COMPLETE. Snapshot written to "+output);
   void Test(string name,Action run) {
    try {run();File.AppendAllText(Path.Combine(output,"suites.tsv"),name+"\tPASS\n");}
    catch(Exception ex) {File.AppendAllText(Path.Combine(output,"suites.tsv"),name+"\tFAIL "+ex.Message.Replace('\n',' ')+"\n"); Debug.Log("[Catchline] INTEGRATION QUESTION "+name+": "+ex);}
   }
  }
 }
}
