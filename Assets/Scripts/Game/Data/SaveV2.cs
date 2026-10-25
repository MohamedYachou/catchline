using System;
using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    // MASTER-PLAN B6 save model, including harbour runtime state. Version 3 is crew cards v2
    // (docs/plans/CREW-CARDS-V2.md); older saves are discarded by design (Mo, 2026-10-25).
    // Fields marked placeholder reserve the slot for later milestones and carry no behaviour yet.
    [Serializable]
    public class SaveV2
    {
        public const int CurrentVersion = 3;

        public int Version = CurrentVersion;
        public GameState.HarbourSave Runtime;
        public List<string> TripDeployment = new List<string>();
        public List<CrewMember> CrewSettings = new List<CrewMember>();
        public int Coins;
        public int Hull;
        public List<int> Owned = new List<int>();            // UpgradeId values, same ints as v1
        public List<CardState> Cards = new List<CardState>();
        public List<string> Deployment = new List<string>(); // deployed card ids; navigator always present once owned

        // Crew cards v2.
        public int Tokens;
        public List<ToolState> Tools = new List<ToolState>();
        public int[] CaptainTools = new int[CardProgression.MaxToolSlots];
        public int NextToolUid = 1;
        public string FocusCard = "";
        public int ChestPity;                                // legacy single counter; read into the sea chest's
        public int[] ChestPities = new int[0];               // per ChestKind: chests since that kind's last blueprint
        public List<string> CrewChests = new List<string>(); // "id:n": crew chests bought from each crew offer
        public int FreeBlueprints;
        public int RenownClaimed;
        public List<int> PendingChests = new List<int>();    // ChestKind values
        public string LastCrateDay = "";

        // Placeholders (M5/M6/M9 and settings).
        public List<int> BuyerRep = new List<int>();
        public List<string> Contracts = new List<string>();
        public string Quota = "";
        public List<float> GroundRichness = new List<float>();
        public int Day;
        public string Settings = "";

        public string ToJson() => JsonUtility.ToJson(this);

        // Returns null for empty/invalid JSON or a different version.
        public static SaveV2 FromJson(string json)
        {
            if (string.IsNullOrEmpty(json)) return null;
            SaveV2 save;
            try { save = JsonUtility.FromJson<SaveV2>(json); }
            catch (Exception) { return null; }
            if (save == null || save.Version != CurrentVersion) return null;
            if (save.CaptainTools == null || save.CaptainTools.Length != CardProgression.MaxToolSlots)
            {
                var slots = new int[CardProgression.MaxToolSlots];
                if (save.CaptainTools != null) Array.Copy(save.CaptainTools, slots, Math.Min(save.CaptainTools.Length, slots.Length));
                save.CaptainTools = slots;
            }
            return save;
        }
    }
}
