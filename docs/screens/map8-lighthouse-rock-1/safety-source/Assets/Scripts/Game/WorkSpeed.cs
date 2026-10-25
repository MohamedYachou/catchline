using UnityEngine;
namespace Catchline.Game
{
    // The one work-speed model (docs/CARDS-AND-SPEEDS.md section 1). Every timed action and every walk on the boat
    // goes through here:  duration = base / (skill / 100) / levelMult,  walk = 2.2 m/s * (skill / 100) * levelMult.
    // The captain is level 1 with skill 100 at every deck job, so he is exactly as fast as a speciality hand.
    public static class WorkSpeed
    {
        public const float SpecialitySkill = 100f, CaptainSkill = 100f, BaseLevelMult = 1f;

        // Work rate: 1 at skill 100, level 1. Progress per second of an action whose base duration is in seconds.
        public static float Rate(float skill, float levelMult = BaseLevelMult) => Mathf.Max(0.01f, skill / 100f) * Mathf.Max(0.01f, levelMult);
        public static float Rate(Person person) => person == null ? 1f : Rate(person.Skill, person.LevelMult);

        public static float Duration(float baseSeconds, float skill = SpecialitySkill, float levelMult = BaseLevelMult) => baseSeconds / Rate(skill, levelMult);
        public static float Duration(float baseSeconds, Person person) => baseSeconds / Rate(person);

        public static float Walk(float skill = SpecialitySkill, float levelMult = BaseLevelMult) => GameData.WalkSpeed * Rate(skill, levelMult);
        public static float Walk(Person person) => GameData.WalkSpeed * Rate(person);
    }
}
