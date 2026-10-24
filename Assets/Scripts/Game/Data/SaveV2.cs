using System;
using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    // MASTER-PLAN B6 save model v2, including harbour runtime state.
    // Fields marked placeholder reserve the slot for later milestones (buyers, contracts, quota,
    // grounds, chests, day, settings) and carry no behaviour yet.
    [Serializable]
    public class SaveV2
    {
        public const int CurrentVersion = 2;

        public int Version = CurrentVersion;
        public GameState.HarbourSave Runtime;
        public float PendingXpKg;
        public List<string> TripDeployment = new List<string>();
        public List<CrewMember> CrewSettings = new List<CrewMember>();
        public int Coins;
        public int Hull;
        public List<int> Owned = new List<int>();            // UpgradeId values, same ints as v1
        public List<CardState> Cards = new List<CardState>();
        public int[] Wildcards = new int[4];                 // indexed by (int)CardRole
        public List<string> Deployment = new List<string>(); // deployed card ids; navigator always present once owned

        // Placeholders (M5/M6/M9 and settings).
        public List<int> BuyerRep = new List<int>();
        public List<string> Contracts = new List<string>();
        public string Quota = "";
        public List<float> GroundRichness = new List<float>();
        public int ChestPity;
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
            if (save.Wildcards == null || save.Wildcards.Length < 4)
            {
                var fixedUp = new int[4];
                if (save.Wildcards != null) Array.Copy(save.Wildcards, fixedUp, save.Wildcards.Length);
                save.Wildcards = fixedUp;
            }
            return save;
        }
    }
}
