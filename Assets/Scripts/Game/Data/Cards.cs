using System;
using System.Collections.Generic;

namespace Catchline.Game
{
    // Crew cards v2 (docs/plans/CREW-CARDS-V2.md). Stored as ints in SaveV2 version 3: append only from here on.
    public enum CardRarity { White, Green, Blue, Purple, Gold, Mythic }
    public enum CardRole { Fisher, Deckhand, Navigator, Engineer }

    // A card's speciality (skill 100) and, equally, the name of a job family a card can be asked to do
    // (CARDS-AND-SPEEDS section 3). Fishers: Rods/Nets/CagesLines/Jigs. Deckhands: Haul/Sort/Table.
    // Navigator: Navigation. Engineer: Power.
    public enum Speciality { None, Rods, Nets, CagesLines, Jigs, Haul, Sort, Table, Navigation, Power }

    // One ability row. Unlock is the rarity that switches it on: Green (passive), Purple (automatic) or
    // Mythic (strong automatic). All abilities trigger by themselves; the behaviour lives in the deck
    // simulation's ability engine, keyed by Id.
    public sealed class AbilityDef
    {
        public readonly string Id, Name, Text;
        public readonly CardRarity Unlock;
        public AbilityDef(string id, string name, string text, CardRarity unlock) { Id = id; Name = name; Text = text; Unlock = unlock; }
    }

    // One row of the crew card table (spec section 7 and 8). Content only.
    public sealed class CardDef
    {
        public readonly string Id;          // stable save key, lowercase name
        public readonly string Name;
        public readonly int TierGranted;    // 1..5: can be recruited (blueprints, crew chests) once the boat reaches this tier
        public readonly CardRole Role;
        public readonly Speciality Speciality;
        public readonly CardRarity StartRarity;
        public readonly AbilityDef Passive, Auto, Mythic;
        public readonly AbilityDef Trait;   // always on (Mira's First mate); null for everyone else
        public readonly string PortraitId;  // art plugs in by id

        public CardDef(string name, int tier, CardRole role, Speciality speciality, CardRarity start,
            string passiveName, string passiveText, string autoName, string autoText, string mythicName, string mythicText,
            string traitName = null, string traitText = null)
        {
            Name = name;
            Id = name.ToLowerInvariant();
            PortraitId = Id;
            TierGranted = tier;
            Role = role;
            Speciality = speciality;
            StartRarity = start;
            Passive = new AbilityDef(Id + ".passive", passiveName, passiveText, CardRarity.Green);
            Auto = new AbilityDef(Id + ".auto", autoName, autoText, CardRarity.Purple);
            Mythic = new AbilityDef(Id + ".mythic", mythicName, mythicText, CardRarity.Mythic);
            if (traitName != null) Trait = new AbilityDef(Id + ".trait", traitName, traitText, start);
        }

        public IEnumerable<AbilityDef> Abilities
        {
            get { if (Trait != null) yield return Trait; yield return Passive; yield return Auto; yield return Mythic; }
        }

        // The strongest ability unlocked at `rarity`, for one-line summaries; null below Green without a trait.
        public AbilityDef TopAbility(CardRarity rarity) =>
            rarity >= CardRarity.Mythic ? Mythic : rarity >= CardRarity.Purple ? Auto : rarity >= CardRarity.Green ? Passive : Trait;

        public string AbilityText(CardRarity rarity) { var a = TopAbility(rarity); return a == null ? "" : a.Name + ": " + a.Text; }
    }

    public static class Cards
    {
        public static readonly CardDef[] All =
        {
            new CardDef("Mira", 1, CardRole.Navigator, Speciality.Navigation, CardRarity.Gold,
                "Chart reader", "Fishing grounds thin out 15% slower while she is aboard.",
                "Shoal call", "Every 2 min, bites come 30% sooner at every rod and line for 20 s.",
                "Mate's eye", "Every 4 min, for 30 s, every fish caught rolls its weight twice and keeps the heavier.",
                "First mate", "Every crew member aboard works 5% faster (8% once she is Mythic)."),
            new CardDef("Noor", 1, CardRole.Deckhand, Speciality.Sort, CardRarity.White,
                "Quick sort", "Sorts 10% faster.",
                "Same again", "Sorting the same species twice in a row makes her next sort 30% faster.",
                "Bucket brigade", "When a net basket lands, she sorts its first 5 fish instantly."),
            new CardDef("Sam", 1, CardRole.Deckhand, Speciality.Haul, CardRarity.White,
                "Extra fish", "Carries 1 more fish per trip.",
                "Heavy lifter", "Fish over 3 kg don't slow him, and he carries 2 of them.",
                "Shoulder load", "Every 2 min he carries a whole net basket in one trip."),
            new CardDef("Dirk", 2, CardRole.Fisher, Speciality.Rods, CardRarity.Green,
                "Steady strike", "His strike window is 15% longer.",
                "Rod line", "When he lands a fish, the other rods bite 20% sooner for 15 s.",
                "Trophy hunter", "Every 3rd fish he lands is in the top quarter of its weight range."),
            new CardDef("Kofi", 2, CardRole.Fisher, Speciality.Nets, CardRarity.Green,
                "Fast set", "Sets nets 15% faster.",
                "Good spot", "When his net comes up over 80% full, the next soak is 25% shorter.",
                "Back-to-back", "Every 3rd net he hauls is reset instantly."),
            new CardDef("Rosa", 2, CardRole.Fisher, Speciality.Nets, CardRarity.Green,
                "Strong back", "Hauls nets 15% faster.",
                "Full bag", "Every 3 min, the next net she hauls comes up 30% fuller.",
                "Shake out", "When she hauls a net, its first 6 fish go straight to the hold, already sorted."),
            new CardDef("Tess", 3, CardRole.Fisher, Speciality.Rods, CardRarity.Blue,
                "Quick reel", "Reels 15% faster.",
                "Feathers", "20% of her herring, mackerel and whiting catches bring up a second fish.",
                "String of feathers", "Every 2 min, her next herring, mackerel or whiting catch brings up 3 fish."),
            new CardDef("Ana", 3, CardRole.Deckhand, Speciality.Haul, CardRarity.Blue,
                "Quick walk", "Walks 10% faster.",
                "Hand-off", "Each fish she brings to the sort table makes the next sort there 20% faster.",
                "Clear deck", "Once a minute, when 6 or more fish wait on deck, she takes them all in one sweep."),
            // Lise fishes rods at night until the jig boat lands; then her speciality becomes Jigs.
            new CardDef("Lise", 3, CardRole.Fisher, Speciality.Rods, CardRarity.Blue,
                "Night eyes", "At night her bites come 20% sooner.",
                "Lamp lure", "At night, every 2 min, every rod and line bites 25% sooner for 30 s.",
                "Deep night", "At night every 4th fish she lands is a heavy predator in the top quarter of its weight."),
            new CardDef("Mats", 4, CardRole.Deckhand, Speciality.Table, CardRarity.Purple,
                "Quick knife", "Table work 10% faster.",
                "Offcuts", "Every product job also makes 1 chum.",
                "Batch cut", "Every 3rd product job processes two fish at once."),
            new CardDef("Ines", 4, CardRole.Engineer, Speciality.Power, CardRarity.Purple,
                "Headlamp", "At night the whole crew works 5% faster.",
                "Ice watch", "When the hold passes half full, the catch stops losing freshness for 3 min.",
                "Floodlights", "At night, every 3 min, bites come 25% sooner and deck work is 15% faster for 40 s."),
            new CardDef("Tove", 4, CardRole.Deckhand, Speciality.Sort, CardRarity.Purple,
                "Steady hands", "Sorts crabs and fish over 3 kg 20% faster.",
                "Grader", "Fish she sorts in the top quarter of their weight sell for 10% more.",
                "Keen eye", "Every 10th fish she sorts sells for double."),
            new CardDef("Olaf", 5, CardRole.Engineer, Speciality.Power, CardRarity.Gold,
                "Tuned engine", "The boat uses 10% less fuel.",
                "Winch tune", "Every 2 min, nets and pots winch up 25% faster for 30 s.",
                "Full steam", "Trips out and home are 25% faster."),
            new CardDef("Pim", 5, CardRole.Fisher, Speciality.CagesLines, CardRarity.Gold,
                "Fast bait", "Baits deep lines and clears pots 25% faster.",
                "Chum saver", "30% of his deep-line baits don't use up the chum.",
                "Pot luck", "Every 5 min, the next pot or line he raises brings up an extra catch."),
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
