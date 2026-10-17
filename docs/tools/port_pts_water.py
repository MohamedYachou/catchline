"""Freeze PTS's water shading with the bounded/orthographic Catchline adapter.

Original PTS checkout is read-only. Run with an output Unity project path;
this does not install its camera passes, physics or change pipeline settings.
"""
from pathlib import Path
import hashlib
import json
import shutil
import sys

source = Path('C:/Users/momoy/Projects/Plunder_The_Seas/Plunder_The_Seas_Unity/Packages/com.unity.urp-water-system')
if sys.platform != 'win32':
    source = Path('/mnt/c/Users/momoy/Projects/Plunder_The_Seas/Plunder_The_Seas_Unity/Packages/com.unity.urp-water-system')
target = Path(sys.argv[1])
out = target / 'Assets/Art/Shaders/PtsWater'
out.mkdir(parents=True, exist_ok=True)


def replace_function(text, signature, replacement):
    start = text.index(signature)
    brace = text.index('{', start)
    end, level = brace + 1, 1
    while level:
        level += (text[end] == '{') - (text[end] == '}')
        end += 1
    return text[:start] + replacement + text[end:]


names = ['WaterCommon.hlsl', 'WaterInput.hlsl', 'WaterLighting.hlsl', 'CommonUtilities.hlsl', 'GerstnerWaves.hlsl']
receipt = {}
for name in names:
    raw = (source / 'Runtime/Shaders' / name).read_bytes()
    receipt[name] = hashlib.sha256(raw).hexdigest()
    text = raw.decode('utf-8-sig').replace('\r\n', '\n')
    text = text.replace('_Time.y', '_Clock').replace('_Time.x', '(_Clock / 20)').replace('_Time.z', '(_Clock * 2)')
    if name == 'WaterInput.hlsl':
        text = text.replace('half3 _AbsorptionColor;', 'float _Clock, _DetailScale, _WaveSteepness, _WaterSmoothness, _SpecularStrength;\nhalf3 _AbsorptionColor;')
    if name == 'GerstnerWaves.hlsl':
        text = text.replace('half peak = 2;', 'half peak = _WaveSteepness;')
        text = text.replace('float time = _Clock;', 'float time = _Clock * .55; // broad calm rolling waves')
    if name == 'WaterLighting.hlsl':
        text = text.replace('#elif _REFLECTION_PROBES', '#elif defined(_REFLECTION_PROBE) || defined(_REFLECTION_PROBES)')
    if name == 'WaterCommon.hlsl':
        text = replace_function(text, 'float2 AdjustedDepth(', '''float2 AdjustedDepth(float2 uvs, float4 additionalData)
{
    float rawD = SAMPLE_TEXTURE2D_LOD(_CameraDepthTexture, sampler_ScreenTextures_point_clamp, uvs, 0).r;
    float d;
    if (unity_OrthoParams.w > .5) {
        #if UNITY_REVERSED_Z
        d = lerp(_ProjectionParams.z, _ProjectionParams.y, rawD);
        #else
        d = lerp(_ProjectionParams.y, _ProjectionParams.z, rawD);
        #endif
    } else d = LinearEyeDepth(rawD, _ZBufferParams);
    return float2(d * additionalData.x - additionalData.y, rawD * -_ProjectionParams.x);
}''')
        text = replace_function(text, 'void BlendLods(', '''void BlendLods(inout float3 positionWS, float3 positionOS, float2 uv)
{
    // Catchline owns one dense, bounded mesh. It has no packed ocean-tile LOD.
}''')
        text = text.replace('data.x = length(viewPos / viewPos.z);', 'data.x = unity_OrthoParams.w > .5 ? 1 : length(viewPos / viewPos.z);')
        text = text.replace('data.y = length(GetCameraPositionWS().xyz - postionWS);', 'data.y = unity_OrthoParams.w > .5 ? -viewPos.z : length(GetCameraPositionWS().xyz - postionWS);')
        text = text.replace('SafeNormalize(GetCameraPositionWS().xyz - input.positionWS)', 'GetWorldSpaceNormalizeViewDir(input.positionWS)')
        text = text.replace('SafeNormalize(_WorldSpaceCameraPos - input.positionWS)', 'GetWorldSpaceNormalizeViewDir(input.positionWS)')
        text = text.replace('half opacity = depthWaveRamp;', 'half opacity = depthWaveRamp;\n\tif (unity_OrthoParams.w > .5) {\n\t    WaveStruct flat = (WaveStruct)0;\n\t    opacity = saturate(AdjustedDepth(screenUV.xy, AdditionalData(input.positionWS, flat)).x * 3);\n\t}')
        text = text.replace('surfaceData.foamMask = length(foam * mask);', 'surfaceData.foamMask = 0; // Mo: no shore wash or white wave foam.')
        text = text.replace('positionWS.xzxz * scale.xxyy', 'positionWS.xzxz * scale.xxyy * _DetailScale')
        text = text.replace('pow(dot(input.viewDirectionWS.xyz, -mainLight.direction) * additionalData.z, 3)', 'pow(saturate(dot(input.viewDirectionWS.xyz, -mainLight.direction) * additionalData.z), 3)')
        text = text.replace('half smoothness = 0.9;', 'half smoothness = _WaterSmoothness;')
        text = text.replace('spec *= radiance;', '''spec *= radiance * _SpecularStrength;
    spec = min(spec, half3(.018, .055, .085)); // restrained blue glints, no white streaks''')
        text = text.replace('half3 compA = lerp(refraction, reflection, fresnelTerm) + spec + sss;', '''half3 compA = lerp(refraction, reflection, fresnelTerm) + spec + sss;
    // Blue surface lighting reveals overlapping ripples from the fishing camera.
    // No height-based crest bands, foam mask or white crest line.
    half slope = saturate(.5 + dot(normalize(input.normalWS).xz, half2(-.7, .7)) * 2.0);
    compA *= lerp(half3(.78, .88, .96), half3(1.08, 1.13, 1.17), slope);''')
        text = text.replace('half distortionIntensity = 0.16;', 'half distortionIntensity = 0.035; // boat-scale refraction: avoid dragging hull pixels into the sea')
        text = text.replace('normalWS.xz *= 0.25;', 'normalWS.xz = unity_OrthoParams.w > .5 ? mul((float3x3)GetWorldToViewMatrix(), float3(normalWS.x, 0, normalWS.z)).xy * .25 : normalWS.xz * .25;')
    (out / name).write_text('// Adapted from PTS / Unity Boat Attack. See LICENSE.md and README.md.\n' + text, encoding='utf-8')

shader = (source / 'Runtime/Shaders/Water.shader').read_text(encoding='utf-8-sig')
shader = shader.replace('Shader "Boat Attack/Water"', 'Shader "Catchline/PTS Water"')
shader = shader.replace('[Toggle(_STATIC_SHADER)]', '''[MainColor] _BaseColor("Voyage colour", Color) = (.06,.76,.8,1)
        _Clock("Voyage clock", Float) = 0
        _DetailScale("Map scale for surface detail", Float) = 4
        _WaveSteepness("Gentle wave steepness", Range(0,1)) = .55
        _WaterSmoothness("Water smoothness", Range(0,1)) = .78
        _SpecularStrength("Sun reflection strength", Range(0,1)) = .12
        _AbsorptionColor("PTS absorption (linear)", Vector) = (.06,.76,.8,1)
        _ScatteringColor("PTS scattering (linear)", Vector) = (.025,.31,.43,1)
        _MaxDepth("Visibility in metres", Float) = 3
        _MaxWaveHeight("Wave height", Float) = .12
        _BoatAttack_Water_DistanceBlend("Surface range", Float) = 256
        _BoatAttack_Water_MicroWaveIntensity("Surface ripples", Float) = .14
        _BoatAttack_water_FoamIntensity("Foam disabled", Float) = 0
        _SurfaceNormals("PTS packed surface normals", 2D) = "gray" {}
        _DitherPattern("PTS shadow dither", 2D) = "gray" {}
        _WaterBufferA("Neutral interaction buffer", 2D) = "gray" {}
        _WaterBufferB("Neutral depth buffer", 2D) = "gray" {}
        _FoamMap("Unused foam", 2D) = "black" {}
        _BoatAttack_RampTexture("Wave profile", 2D) = "white" {}
        _CubemapTexture("Coastal sky reflection", Cube) = "" {}
        [Toggle(_STATIC_SHADER)]''')
shader = shader.replace('#include "WaterCommon.hlsl"', '#include "PtsWater/WaterCommon.hlsl"')
shader = shader.replace('#pragma multi_compile_fragment _REFLECTION_CUBEMAP _REFLECTION_PROBE _REFLECTION_PLANARREFLECTION _REFLECTION_SSR', '#define _REFLECTION_CUBEMAP 1')
for pragma in [
    '#pragma multi_compile_fragment _ _DISPERSION',
    '#pragma multi_compile _ USE_STRUCTURED_BUFFER',
    '#pragma multi_compile _ BOAT_ATTACK_WATER_DEBUG_DISPLAY',
    '#pragma multi_compile_fragment _ _SSR_SAMPLES_LOW _SSR_SAMPLES_MEDIUM _SSR_SAMPLES_HIGH',
    '#pragma multi_compile_fragment _ _SHADOW_SAMPLES_LOW _SHADOW_SAMPLES_MEDIUM _SHADOW_SAMPLES_HIGH',
    '#pragma multi_compile _ _ADDITIONAL_LIGHTS_VERTEX _ADDITIONAL_LIGHTS',
    '#pragma multi_compile_fragment _ _ADDITIONAL_LIGHT_SHADOWS',
    '#pragma multi_compile_fragment _ _REFLECTION_PROBE_BLENDING',
    '#pragma multi_compile _ SHADOWS_SHADOWMASK',
    '#pragma multi_compile _ _FORWARD_PLUS',
]:
    shader = shader.replace(pragma, '// Bounded adapter: unused open-ocean variant omitted.')
shader = shader.replace('#pragma prefer_hlslcc gles', '#pragma target 3.5\n            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP\n            #pragma prefer_hlslcc gles')
(target / 'Assets/Art/Shaders/PtsWater.shader').write_text(shader, encoding='utf-8')
shutil.copy2(source / 'LICENSE.md', out / 'LICENSE.md')
(out / 'source-sha256.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
(out / 'README.md').write_text('''# PTS water, bounded Catchline adapter

Source: the local Plunder The Seas `com.unity.urp-water-system` package,
2.0.0-preview.5, Unity Boat Attack water. Original checkout remains unchanged.
Copyright and Unity Companion License are in LICENSE.md. Original shader hashes
are recorded in source-sha256.json; docs/tools/port_pts_water.py reproduces this.

Keeps PTS Gerstner waves, packed moving surface normals, absorption/scattering,
refraction, Fresnel and water lighting. Adapter changes: orthographic eye depth
and view direction; bounded mesh instead of perspective tile LOD; camera-depth
wave mask instead of its absent authored depth buffer; voyage clock; map detail
scale/optical calibration; capped wave steepness and sun glint strength; probe
keyword typo; safe nonnegative SSS power; foam forced off. Unused reflection,
structured-buffer, volumetric-shadow and debug variants are omitted. The
runtime supplies small wave arrays, neutral interaction buffers and coastal sky.
WATER-006 uses blue ripple lighting, original moving packed normals and tiny
crossing displacement. Large swells/height-based colour bands are removed;
sun glints stay blue-capped and foam is disabled, following Mo's supplied game refs.

Does not install the original package managers, physics, legacy camera passes or
change the render pipeline. Uses ordinary URP opaque and depth textures. The old
coastal shader remains available as a fallback until native review is complete.
''', encoding='utf-8')

textures = target / 'Assets/Art/Water/PTS'
textures.mkdir(parents=True, exist_ok=True)
for name in ['WaterNormals.tif', 'normalNoise.png']:
    matches = list((source / 'Runtime/Textures').rglob(name))
    if not matches:
        continue
    shutil.copy2(matches[0], textures / name)
    # New GUIDs: never alias the original package's asset identifiers.
    meta = matches[0].with_suffix(matches[0].suffix + '.meta')
    if meta.exists() and not (textures / (name + '.meta')).exists():
        import uuid
        import re
        content = re.sub(r'guid: [0-9a-f]{32}', 'guid: ' + uuid.uuid4().hex, meta.read_text(), count=1)
        (textures / (name + '.meta')).write_text(content, encoding='utf-8')
print('Frozen PTS water shader adapter in', target)
