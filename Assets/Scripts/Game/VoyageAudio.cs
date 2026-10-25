using System;
using System.Collections.Generic;
using UnityEngine;

namespace Catchline.Game
{
    // Original, generated foley. No downloaded recordings or per-frame audio allocations.
    public sealed class VoyageAudio : MonoBehaviour
    {
        public enum Cue { Cast, Splash, Bite, Reel, Land, Stow, Moor, Sale, Select, Purchase, Gull, Bell, Creak, Horn, Click }
        readonly Dictionary<Cue, AudioClip> clips = new();
        AudioSource ambience, foley;
        AudioClip sea;
        float nextOar, nextGull;
        bool preview;
        float previewVolume = .65f;
        public float Volume
        {
            get => preview ? previewVolume : PlayerPrefs.GetFloat("catchline.sound", .65f);
            set { if (preview) previewVolume = value; else { PlayerPrefs.SetFloat("catchline.sound", value); PlayerPrefs.Save(); } }
        }

        public void Initialize(bool sessionOnly)
        {
            preview = sessionOnly;
            ambience = gameObject.AddComponent<AudioSource>();
            foley = gameObject.AddComponent<AudioSource>();
            ambience.spatialBlend = foley.spatialBlend = 0;
            ambience.loop = true;
            sea = MakeSea();
            ambience.clip = sea;
            foreach (Cue cue in Enum.GetValues(typeof(Cue))) clips[cue] = MakeCue(cue);
            ambience.volume = Volume * .23f;
            ambience.Play();
        }

        public void Play(Cue cue, float gain = 1f)
        {
            if (foley != null && Volume > .001f) foley.PlayOneShot(clips[cue], Volume * gain);
        }

        public void Mix(bool paused, bool harbour, bool rowing)
        {
            if (ambience == null) return;
            ambience.volume = Volume * (paused ? .06f : harbour ? .16f : .23f);
            foley.volume = paused ? 0 : 1;
            // Gulls over the harbour now and then.
            if (harbour && !paused && Time.time >= nextGull)
            {
                if (nextGull > 0) Play(Cue.Gull, .22f + UnityEngine.Random.value * .15f);
                nextGull = Time.time + 7f + UnityEngine.Random.value * 11f;
            }
            if (rowing && !paused && Time.time >= nextOar)
            {
                nextOar = Time.time + 1.96f;
                Play(Cue.Splash, .28f);
                Play(Cue.Moor, .12f);
            }
        }

        static AudioClip MakeSea()
        {
            const int rate = 22050, seconds = 16;
            var samples = new float[rate * seconds * 2];
            var random = new System.Random(4106);
            float lowL = 0, lowR = 0, smoothL = 0, smoothR = 0;
            for (int n = 0; n < rate * seconds; n++)
            {
                float t = n / (float)rate;
                lowL = Mathf.Lerp(lowL, (float)random.NextDouble() * 2 - 1, .055f);
                lowR = Mathf.Lerp(lowR, (float)random.NextDouble() * 2 - 1, .055f);
                smoothL = Mathf.Lerp(smoothL, lowL, .1f);
                smoothR = Mathf.Lerp(smoothR, lowR, .1f);
                float lap = .35f + .65f * Mathf.Pow(.5f + .5f * Mathf.Sin(t * Mathf.PI * .5f), 2);
                // Bring both ends to silence for a click-free looping bed.
                float seam = Mathf.Min(1f, Mathf.Min(t * 2, (seconds - t) * 2));
                samples[n * 2] = smoothL * lap * seam * 1.8f;
                samples[n * 2 + 1] = smoothR * lap * seam * 1.8f;
            }
            var clip = AudioClip.Create("Catchline coastal water", rate * seconds, 2, rate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        static AudioClip MakeCue(Cue cue)
        {
            const int rate = 22050;
            float duration = cue switch
            {
                Cue.Reel => 1.2f, Cue.Splash or Cue.Sale => .65f, Cue.Gull => 1.05f, Cue.Bell => 1.8f,
                Cue.Creak => .5f, Cue.Horn => 1.9f, Cue.Click => .14f, _ => .32f,
            };
            var samples = new float[(int)(rate * duration)];
            var random = new System.Random(730 + (int)cue);
            float low = 0;
            for (int n = 0; n < samples.Length; n++)
            {
                float t = n / (float)rate, noise = (float)random.NextDouble() * 2 - 1;
                low = Mathf.Lerp(low, noise, .16f);
                float envelope = Mathf.Min(1, t * 180) * Mathf.Exp(-t * 10);
                float sample;
                switch (cue)
                {
                    case Cue.Select:
                        sample = (Mathf.Sin(6.283f * 220 * t) * .12f + low * .2f) * envelope; break;
                    case Cue.Purchase:
                        // Paper rustle and a short coin touch, not a musical reward jingle.
                        sample = low * Mathf.Exp(-t * 22) * .32f + Mathf.Sin(6.283f * 1740 * t) * envelope * .055f; break;
                    case Cue.Cast: sample = low * Mathf.Sin(Mathf.PI * t / duration) * .65f; break;
                    case Cue.Splash:
                        sample = low * Mathf.Exp(-t * 5) * .9f + Mathf.Sin(6.283f * (320 * t - 110 * t * t)) * envelope * .07f; break;
                    case Cue.Bite:
                        sample = (Mathf.Sin(6.283f * (600 * t - 260 * t * t)) * .19f + low * .35f) * envelope; break;
                    case Cue.Reel:
                        float tooth = t % .065f;
                        sample = (Mathf.Sin(6.283f * 850 * tooth) * .15f + low * .5f) * Mathf.Exp(-tooth * 180) * Mathf.Min(1, (duration - t) * 8); break;
                    case Cue.Sale:
                        float coin = t % .14f;
                        sample = (Mathf.Sin(6.283f * 2110 * coin) + .4f * Mathf.Sin(6.283f * 3263 * coin)) * Mathf.Exp(-coin * 75) * .11f * (1 - t / duration); break;
                    case Cue.Gull:
                    {
                        // Three falling "kyow" calls: a rising-then-falling squeal with a rough, nasal edge.
                        float call = t < .36f ? t : t < .64f ? t - .36f : t - .64f, len = t < .64f ? .3f : .38f;
                        float u = Mathf.Clamp01(call / len), f = 1250 + 520 * Mathf.Sin(u * Mathf.PI) - 380 * u;
                        float body = Mathf.Sin(6.283f * f * call) + .45f * Mathf.Sin(6.283f * f * 2 * call) + .2f * Mathf.Sin(6.283f * f * 3 * call);
                        sample = body * (.8f + .2f * Mathf.Sin(6.283f * 38 * t)) * Mathf.Sin(Mathf.PI * u) * (t < .64f ? .06f : .075f) + low * .02f;
                        break;
                    }
                    case Cue.Bell:
                    {
                        // A struck buoy bell: inharmonic partials with a long ring and a soft clapper knock.
                        float ring = Mathf.Exp(-t * 2.1f);
                        sample = (Mathf.Sin(6.283f * 523 * t) * .5f + Mathf.Sin(6.283f * 1255 * t) * .28f * Mathf.Exp(-t * 3)
                            + Mathf.Sin(6.283f * 1602 * t) * .18f * Mathf.Exp(-t * 4) + Mathf.Sin(6.283f * 2093 * t) * .1f * Mathf.Exp(-t * 6)) * ring * .16f
                            + low * Mathf.Exp(-t * 60) * .3f;
                        break;
                    }
                    case Cue.Creak:
                    {
                        // Rope over wood: stick-slip pulses whose rate wanders.
                        float rate2 = 38 + 14 * Mathf.Sin(t * 9);
                        float pulse = (t * rate2) % 1f;
                        sample = (low * .6f + Mathf.Sin(6.283f * 160 * t) * .3f) * Mathf.Exp(-pulse * 9) * Mathf.Sin(Mathf.PI * t / duration) * .5f;
                        break;
                    }
                    case Cue.Horn:
                    {
                        // A distant foghorn: low reedy tone, slow swell and fade.
                        float swell = Mathf.Clamp01(t / .25f) * Mathf.Clamp01((duration - t) / .6f);
                        float f = 98 * (1 + .004f * Mathf.Sin(6.283f * 5 * t));
                        sample = (Mathf.Sin(6.283f * f * t) * .55f + Mathf.Sin(6.283f * f * 2 * t) * .3f + Mathf.Sin(6.283f * f * 3 * t) * .15f + low * .05f) * swell * .2f;
                        break;
                    }
                    case Cue.Click:
                        sample = (low * .8f + Mathf.Sin(6.283f * 3100 * t) * .2f) * (Mathf.Exp(-t * 160) + Mathf.Exp(-Mathf.Abs(t - .07f) * 220) * .7f) * .35f; break;
                    default:
                        float pitch = cue == Cue.Moor ? 135 : cue == Cue.Land ? 280 : 190;
                        sample = (Mathf.Sin(6.283f * pitch * t) * .21f + Mathf.Sin(6.283f * pitch * 2.73f * t) * .08f + low * .3f) * envelope; break;
                }
                samples[n] = sample * Mathf.Clamp01((duration - t) * 100);
            }
            var clip = AudioClip.Create("Catchline " + cue, samples.Length, 1, rate, false);
            clip.SetData(samples, 0);
            return clip;
        }

        void OnDestroy()
        {
            if (sea != null) Destroy(sea);
            foreach (var clip in clips.Values) Destroy(clip);
        }
    }
}
