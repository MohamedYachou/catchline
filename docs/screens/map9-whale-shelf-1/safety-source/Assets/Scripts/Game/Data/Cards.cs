using System;
using System.Collections.Generic;

namespace Catchline.Game
{
    // Append only: stored as ints in SaveV2 (CardState.Rarity, Wildcards index).
    public enum CardRarity { Blue, Purple, Gold }
    public enum CardRole { Fisher, Deckhand, Navigator, Engineer }

    // A card's speciality (skill 100) and, equally, the name of a job family a card can be asked to do
    // (CARDS-AND-SPEEDS section 3). Fishers: Rods/Nets/CagesLines/Jigs. Deckhands: Haul/Sort/Table.
    // Navigator: Navigation. Engineer: Power.
    public enum Speciality { None, Rods, Nets, CagesLines, Jigs, Haul, Sort, Table, Navigation, Power }

    // One row of the crew card table (BLUEPRINT section 14, MASTER-PLAN M2). Content only; the ability
    // behaviour itself lives in the ability classes keyed by these ids.
    public sealed class CardDef
    {
        public readonly string Id;          // stable save key, lowercase name
        public readonly string Name;
        public readonly int TierGranted;    // 1..5: granted at blue level 1 on reaching this tier
        public readonly CardRole Role;
        public readonly Speciality Speciality;
        public readonly string BlueId, BlueText;
        public readonly string PurpleId, PurpleText;
        public readonly string GoldId, GoldText;
        public readonly string PortraitId;  // art plugs in by id

        public CardDef(string name, int tier, CardRole role, Speciality speciality,
            string blueId, string blueText, string purpleId, string purpleText, string goldId, string goldText)
        {
            Name = name;
            Id = name.ToLowerInvariant();
            PortraitId = Id;
            TierGranted = tier;
            Role = role;
            Speciality = speciality;
            BlueId = blueId; BlueText = blueText;
            PurpleId = purpleId; PurpleText = purpleText;
            GoldId = goldId; GoldText = goldText;
        }

        public string AbilityId(CardRarity rarity) => rarity == CardRarity.Blue ? BlueId : rarity == CardRarity.Purple ? PurpleId : GoldId;
        public string AbilityText(CardRarity rarity) => rarity == CardRarity.Blue ? BlueText : rarity == CardRarity.Purple ? PurpleText : GoldText;
    }

    public static class Cards
    {
        public static readonly CardDef[] All =
        {
            new CardDef("Mira", 1, CardRole.Navigator, Speciality.Navigation,
                "mira.early_readout", "Richness readout 30 s earlier.",
                "mira.fast_stow", "Crew stow gear 2x faster on a relocation call.",
                "mira.radio", "Radio: price spikes and rush contracts at sea."),
            new CardDef("Noor", 1, CardRole.Deckhand, Speciality.Sort,
                "noor.quick_sort", "+10% sort.",
                "noor.pre_stack", "Pre-stacks for the hauler on her route (+20% his walk).",
                "noor.bucket_brigade", "Bucket brigade: sorts a whole net basket as one job."),
            new CardDef("Dirk", 2, CardRole.Fisher, Speciality.Rods,
                "dirk.wide_window", "Strike window +15%.",
                "dirk.self_hook", "Neighbouring unmanned rods self-hook for 5 s after his bite.",
                "dirk.two_rods", "Two rods."),
            new CardDef("Sam", 2, CardRole.Deckhand, Speciality.Haul,
                "sam.extra_fish", "Carries +1 fish.",
                "sam.team_haul", "Two haulers on one route both +30%.",
                "sam.power_lifter", "Power lifter: carries any single fish alone."),
            new CardDef("Kofi", 3, CardRole.Fisher, Speciality.Nets,
                "kofi.fast_set", "Sets 20% faster.",
                "kofi.tend_second", "Tends a second fisher's net while his soaks (+15% both).",
                "kofi.back_to_back", "Back-to-back: haul and reset in one job."),
            new CardDef("Ana", 3, CardRole.Deckhand, Speciality.Haul,
                "ana.quick_walk", "+10% walk.",
                "ana.arm_sort", "Her deliveries arm one half-time sort job.",
                "ana.clear_deck", "Clear deck: clears every loose fish on deck in one sweep."),
            new CardDef("Mats", 4, CardRole.Deckhand, Speciality.Table,
                "mats.quick_table", "+10% table.",
                "mats.offcuts", "Offcuts: every product job yields one chum.",
                "mats.batch_cut", "Batch cut: processes a basket as one job."),
            // Lise per MASTER-PLAN M2 correction: Fisher, Jigs (night).
            new CardDef("Lise", 4, CardRole.Fisher, Speciality.Jigs,
                "lise.lamp_eye", "Lamp eye: jig cycle +10%.",
                "lise.shares_light", "Shares the light: the neighbouring station counts as lit at night.",
                "lise.ink_run", "Ink run: her jig pulls two squid per cycle."),
            new CardDef("Olaf", 5, CardRole.Engineer, Speciality.Power,
                "olaf.steady_power", "Faults 20% rarer.",
                "olaf.night_sorting", "Lights also raise night sort speed to 100%.",
                "olaf.overclock", "Overclock: +50% power for 30 s, breaker risk."),
            new CardDef("Pim", 5, CardRole.Fisher, Speciality.CagesLines,
                "pim.fast_bait", "Baits 30% faster.",
                "pim.free_rebait", "His raised line arms a free cage rebait.",
                "pim.double_drop", "Double drop: baits two lines with one chum."),
            new CardDef("Tove", 5, CardRole.Deckhand, Speciality.Sort,
                "tove.quick_sort", "+10% sort.",
                "tove.steady_hands", "Crab pinches never take her out.",
                "tove.grader", "Grader: her sorted purple+ fish yield 2 special products."),
            // TODO(BLUEPRINT): Rosa, Ines and Tess are planned art-only characters; add rows here once
            // BLUEPRINT section 14 gives them a role, tier and abilities. Do not invent stats.
        };

        public static CardDef ById(string id)
        {
            if (string.IsNullOrEmpty(id)) return null;
            for (int i = 0; i < All.Length; i++)
                if (All[i].Id == id) return All[i];
            return null;
        }

        public static List<CardDef> ForTier(int tier)
        {
            var list = new List<CardDef>();
            for (int i = 0; i < All.Length; i++)
                if (All[i].TierGranted == tier) list.Add(All[i]);
            return list;
        }
    }
}
