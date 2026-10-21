using System;
using System.IO;
using System.Linq;
using System.Reflection;
using Catchline.Game;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Catchline.EditorTools
{
    public static class PrepOrdersChecks
    {
        const BindingFlags H = BindingFlags.Instance | BindingFlags.NonPublic;
        static void Check(bool ok, string why) { if (!ok) throw new Exception("PREP035: " + why); }
        static void Call(VoyageGame g, string n, params object[] a) => typeof(VoyageGame).GetMethod(n, H).Invoke(g, a);
        static void Work(Person p) { for (int i = 0; i < 3000 && !p.Idle; i++) p.Tick(.05f, 1, Quaternion.identity); }
        static CaughtFish Small(VoyageGame g) { var f = new CaughtFish { Species = Species.Herring, Kg = .2f, StowedAt = g.SimTime }; g.DeliverCatch(f); return f; }

        public static void Run()
        {
            Directory.CreateDirectory("Logs/prep035");
            ArtImport.BuildLibrary();
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var g = new GameObject("PREP035 isolated check").AddComponent<VoyageGame>(); g.SessionOnly = true; g.Build();
            Check(g.StartPrepBoatTrial(), "trial starts");
            var hands = new[] { g.Hand }.Concat(g.ExtraPeople).Where(p => p.Contract.Role == CrewRole.Deckhand).ToArray();
            foreach (var h in hands) { h.Stop(); Check(g.SetDeckhandWork(h.Contract, DeckhandWork.Prep), "two prep duties allowed"); }
            g.State.Chum = 9; var f1 = Small(g); var f2 = Small(g); var f3 = Small(g);
            var before = g.HoldKg;
            Check(g.TryPrepWork(hands[0]) && g.TryPrepWork(hands[1]), "both start");
            Check(g.ChumBeingMade == 1 && g.PrepWorkersActive == 2 && g.HoldKg == before, "one chum slot left reserved atomically; cargo mass retained");
            Work(hands[0]); Work(hands[1]);
            Check(g.State.Chum == 10 && g.ProcessingInput.Count+g.ProcessingOutput.Count == 2 && g.ProcessingOutput.Count(f => f.Prepared) == 1, "stop exactly at ten; other hand prepares");
            Check(g.TryPrepWork(hands[0]), "at target falls back to prep"); Work(hands[0]);
            Check(g.ProcessingInput.Count==0 && g.ProcessingOutput.All(f => f.Prepared), "already prepared fish not processed twice");
            Check(!g.TryPrepWork(hands[0]), "no endless premium stacking");
            var prepared = g.ProcessingOutput[0];
            Check(g.State.Freshness(prepared, g.SimTime + 36000) == 1, "prepared never spoils without ice");
            int premium = g.State.ValueOf(prepared, g.SimTime + 36000);
            var raw = new CaughtFish { Species = prepared.Species, Kg = prepared.Kg, StowedAt = g.SimTime };
            Check(premium == Mathf.Max(1, Mathf.RoundToInt(raw.Kg * g.State.SpecimenPricePerKg(raw.Species, raw.Kg) * 1.25f)), "single 25 percent premium");
            Check(g.State.Freshness(raw, g.SimTime + 36000) == GameData.MinFreshness, "raw bucket fish still spoils");
            g.State.Owned.Add(UpgradeId.IceBox); Check(g.State.Freshness(raw, g.SimTime + 36000) == 1, "ice protects raw"); g.State.Owned.Remove(UpgradeId.IceBox);
            int worms = g.State.Bait, squidCount = g.State.Squid;
            Check(g.State.TakeBait(out bool squid, out bool chum) && chum && !squid && g.State.Chum == 9 && g.State.Bait == worms && g.State.Squid == squidCount, "premium chum really used before paid bait");
            var refill = Small(g); Check(g.TryPrepWork(hands[0]) && g.ChumBeingMade == 1, "consuming chum reactivates priority"); Work(hands[0]);
            Check(g.State.Chum == 10 && !g.ProcessingInput.Contains(refill), "refill consumes one raw fish");
            g.State.Chum = 0; var cancelled = Small(g); Check(g.TryPrepWork(hands[0]), "reserve cancellation test");
            g.SetDeckhandWork(hands[0].Contract, DeckhandWork.Fish);
            Check(g.PrepWorkersActive == 0 && g.ProcessingInput.Contains(cancelled) && !cancelled.Prepared && g.State.Chum == 0, "duty change releases reservation without consuming");
            g.SetDeckhandWork(hands[0].Contract, DeckhandWork.Prep);
            g.State.PrepOrders.HasClassFilters = true; g.State.PrepOrders.ChumClassMask = 0;
            Check(g.TryPrepWork(hands[0]) && g.ChumBeingMade == 0, "ineligible chum input falls back to preparation"); Work(hands[0]);
            g.State.PrepOrders.ChumClassMask = 1;
            g.ChangePrepPriority(); Small(g);
            Check(g.TryPrepWork(hands[0]) && g.ChumBeingMade == 0, "changed priority used by next job"); Work(hands[0]);
            // Preparation preserves existing deterioration; it never refreshes old fish.
            var old = Small(g); old.StowedAt = g.SimTime - 240;
            Check(g.TryPrepWork(hands[0]), "old fish can be prepared"); Work(hands[0]);
            float frozen = g.State.Freshness(old, g.SimTime);
            Check(old.Prepared && frozen < 1 && g.State.Freshness(old, 999999) == frozen, "preparation freezes existing quality rather than healing it");
            // Four temporary deckhands: third must be rejected by duty setter and job allocator.
            var spare = g.ExtraPeople.First(p => p.Contract.Role == CrewRole.Fisherman);
            spare.Contract.Role = CrewRole.Deckhand;
            Check(!g.SetDeckhandWork(spare.Contract, DeckhandWork.Prep), "third prep duty rejected");
            g.PrepareInterface(844,390); Check(g.InvokeInterface("prep/open"), "table opens in native UI");
            g.PrepareInterface(844,390); bool priority = g.State.PrepOrders.ChumFirst;
            Check(!g.InvokeInterface("prep/priority"), "prep table excludes worker priority");
            Check(g.InvokeInterface("prep/close"), "close prep table"); g.PrepareInterface(844,390);
            Check(g.InvokeInterface("net/orders"), "crew duties opens"); g.PrepareInterface(844,390);
            Check(g.InvokeInterface("net/orders/prep-priority") && g.State.PrepOrders.ChumFirst != priority, "native priority changes in crew duties");
            g.State.Chum = 10; Small(g); g.TryPrepWork(hands[0]);
            g.HeadHome();
            Check(g.PrepWorkersActive == 0 && g.Cooler.Any(f => !f.Prepared), "return cancels unfinished job and keeps raw cargo");
            for (int i = 0; i < 1500 && g.CurrentMode != VoyageGame.Mode.Harbour; i++) g.Tick(.05f);
            Check(g.State.Chum == 0 && g.State.UnsoldCatch.Any(f => f.Prepared), "chum expires on return; prepared status survives docking");
            var path = "Logs/prep035/isolated-state.json"; g.State.Save(path); var loaded = GameState.Load(path);
            Check(loaded.Chum == 0 && loaded.UnsoldCatch.Any(f => f.Prepared) && loaded.PrepOrders.ChumTarget == 10, "prepared fish and orders save; chum does not");
            var preserved = loaded.UnsoldCatch.First(f => f.Prepared);
            Check(loaded.Freshness(preserved, 999999) == 1 && loaded.ValueOf(preserved,0) == loaded.ValueOf(preserved,999999), "saved prepared fish never loses value");
            var quote = loaded.QuoteSale(loaded.UnsoldCatch, 0); var sale = loaded.Sell(loaded.UnsoldCatch,0);
            Check(quote.Coins == sale.Coins, "premium quote equals actual payout");
            UnityEngine.Object.DestroyImmediate(g.gameObject);
            PrepFisherChecks.Run();
            Debug.Log("[Catchline] PREP035 CHECKS PASSED");
            Debug.Log("[Catchline] Snapshot written to Logs/prep035");
        }
        public static void ValidateAndBuild() { Run(); PrepFisherChecks.BuildPreview(); }
    }
}
