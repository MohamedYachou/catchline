using UnityEngine;

namespace Catchline.Game
{
    // Supplies the original PTS shading without its open-ocean managers/passes.
    public static class PtsWater
    {
        public const float MotionSpeed = .65f;
        public static float Clock(float simulationTime) => simulationTime * MotionSpeed;

        // Same five Gerstner height terms as the GPU; hull-sized sampling filters
        // short ripples rather than making the whole boat follow each small crest.
        public static float Height(Vector3 position, float simulationTime)
        {
            float height = 0;
            for (int i = 0; i < 5; i++)
            {
                float scale = Mathf.Lerp(.65f, 1.45f, i / 4f);
                float direction = (35f + (i - 2) * 23f) * Mathf.Deg2Rad;
                float frequency = 2 * Mathf.PI / (1.5f * scale);
                float phase = (Mathf.Sin(direction) * position.x + Mathf.Cos(direction) * position.z) * frequency
                    - Clock(simulationTime) * .55f * Mathf.Sqrt(9.8f * frequency);
                height += Mathf.Sin(phase) * .035f * scale / 5;
            }
            return height;
        }

        public static void HullPose(Vector3 center, float heading, bool skiff, float time, out float heave, out Quaternion tilt)
        {
            var yaw = Quaternion.Euler(0, heading, 0);
            Vector3 along = yaw * Vector3.right * (skiff ? 2.2f : 1.4f);
            Vector3 across = yaw * Vector3.forward * (skiff ? 1f : .65f);
            float bow = Height(center + along, time), stern = Height(center - along, time);
            float port = Height(center + across, time), starboard = Height(center - across, time);
            heave = (Height(center, time) * 2 + bow + stern + port + starboard) / 6;
            float pitch = -Mathf.Atan2(port - starboard, across.magnitude * 2) * Mathf.Rad2Deg;
            float roll = Mathf.Atan2(bow - stern, along.magnitude * 2) * Mathf.Rad2Deg;
            tilt = Quaternion.Euler(Mathf.Clamp(pitch, -.8f, .8f), 0, Mathf.Clamp(roll, -.8f, .8f));
        }

        static Texture2D neutral;
        static Cubemap sky;

        public static void Configure(Material material, Texture2D packedNormals, Texture2D dither)
        {
            if (!material.HasProperty("_AbsorptionColor")) return;
            material.SetTexture("_SurfaceNormals", packedNormals);
            material.SetTexture("_DitherPattern", dither);
            if (neutral == null)
            {
                neutral = new Texture2D(1, 1, TextureFormat.RGBA32, false, true) { name = "Neutral PTS interaction buffer" };
                neutral.SetPixel(0, 0, new Color(0, .5f, .5f, .5f));
                neutral.Apply(false, true);
            }
            material.SetTexture("_WaterBufferA", neutral);
            material.SetTexture("_WaterBufferB", neutral);
            if (sky == null)
            {
                const int size = 32;
                sky = new Cubemap(size, TextureFormat.RGBA32, true) { name = "Coastal daylight reflection" };
                for (int face = 0; face < 6; face++)
                {
                    var pixels = new Color[size * size];
                    for (int y = 0; y < size; y++)
                        for (int x = 0; x < size; x++)
                        {
                            float u = 2f * (x + .5f) / size - 1f, v = 2f * (y + .5f) / size - 1f;
                            Vector3 direction = face switch
                            {
                                0 => new Vector3(1, -v, -u), 1 => new Vector3(-1, -v, u),
                                2 => new Vector3(u, 1, v), 3 => new Vector3(u, -1, -v),
                                4 => new Vector3(u, -v, 1), _ => new Vector3(-u, -v, -1)
                            };
                            float elevation = direction.normalized.y;
                            pixels[y * size + x] = Color.Lerp(new Color(.80f, .88f, .87f), new Color(.28f, .57f, .76f), Mathf.Pow(Mathf.Max(0, elevation), .45f));
                        }
                    sky.SetPixels(pixels, (CubemapFace)face);
                }
                sky.Apply(true, true);
            }
            material.SetTexture("_CubemapTexture", sky);
            material.EnableKeyword("_REFLECTION_CUBEMAP");
            material.DisableKeyword("USE_STRUCTURED_BUFFER");
            material.SetFloat("_BoatAttack_Water_DistanceBlend", 256);
            material.SetFloat("_BoatAttack_water_FoamIntensity", 0);
            material.SetFloat("_DetailScale", .8f);
            material.SetFloat("_WaterSmoothness", .76f);
            material.SetFloat("_SpecularStrength", .085f);
            material.SetFloat("_WaveSteepness", .18f);
            SetBiome(material, 0);
        }

        public static void SetBiome(Material material, int kind)
        {
            // PTS optical model, calibrated to each existing boat-sized location.
            material.SetVector("_AbsorptionColor", new Vector4(.06f, .66f, .84f, 1));
            material.SetVector("_ScatteringColor", kind == 4 ? new Vector4(.018f, .26f, .43f, 1)
                : kind == 1 ? new Vector4(.025f, .32f, .43f, 1)
                : kind == 2 ? new Vector4(.025f, .34f, .48f, 1) : new Vector4(.025f, .31f, .43f, 1));
            material.SetFloat("_MaxDepth", kind == 2 ? 3.5f : kind == 4 ? 1.3f : 3f);
            material.SetFloat("_BoatAttack_Water_MicroWaveIntensity", .22f);
            const int count = 5;
            var waves = new Vector4[20];
            for (int i = 0; i < count; i++)
            {
                float scale = Mathf.Lerp(.65f, 1.45f, i / 4f);
                waves[i] = new Vector4(.035f * scale, 35f + (i - 2) * 23f, 1.5f * scale, 0);
            }
            material.SetInt("_WaveCount", count);
            material.SetVectorArray("waveData", waves);
            material.SetFloat("_MaxWaveHeight", .055f);
        }
    }
}
