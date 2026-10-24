Shader "Catchline/Fish Shadow"
{
    Properties
    {
        _BodyColor("Submerged ink", Color) = (.025,.14,.18,1)
        _RimColor("Water-filtered rim", Color) = (.39,.74,.72,1)
    }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Transparent" "Queue"="Transparent+100" }
        Pass
        {
            Name "Underwater silhouette"
            Tags { "LightMode"="UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            // PTS water writes depth. Test the opaque camera depth explicitly instead,
            // so the water cannot hide the fish but the boat and rocks still occlude it.
            ZTest Always
            Cull Back
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma target 3.5
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
            CBUFFER_START(UnityPerMaterial)
                half4 _BodyColor, _RimColor;
                float4x4 _WorldToFish, _FishToWorld;
                float _Length, _Phase, _Depth, _Visibility;
            CBUFFER_END
            struct Attributes { float4 positionOS : POSITION; float3 normalOS : NORMAL; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 world : TEXCOORD0; half3 normal : TEXCOORD1; };
            Varyings Vert(Attributes input)
            {
                Varyings o;
                float3 p = mul(_WorldToFish, mul(unity_ObjectToWorld, input.positionOS)).xyz;
                float3 normal = mul((float3x3)_WorldToFish, TransformObjectToWorldNormal(input.normalOS));
                float tail = saturate(.5 - p.z / max(_Length, .001));
                float angle = _Phase - tail * 5;
                float wave = sin(angle) * tail * tail * _Length * .075;
                // Correct normals with the derivative of the centreline bend.
                float derivative = -.075 * (2 * tail * sin(angle) - 5 * tail * tail * cos(angle));
                normal.z -= derivative * normal.x;
                p.x += wave;
                o.world = mul(_FishToWorld, float4(p, 1)).xyz;
                o.normal = normalize(mul((float3x3)_FishToWorld, normal));
                o.positionCS = TransformWorldToHClip(o.world);
                return o;
            }
            half4 Frag(Varyings input) : SV_Target
            {
                float2 uv = GetNormalizedScreenSpaceUV(input.positionCS);
                float opaqueDepth = SampleSceneDepth(uv);
                #if UNITY_REVERSED_Z
                    clip(input.positionCS.z - opaqueDepth + .000001);
                #else
                    clip(opaqueDepth - input.positionCS.z + .000001);
                #endif
                float3 view = GetWorldSpaceNormalizeViewDir(input.world);
                half rim = pow(1 - saturate(abs(dot(normalize(input.normal), view))), 2.5);
                half fade = lerp(.86, .16, smoothstep(0, 1, _Depth)) * _Visibility;
                half3 color = lerp(_BodyColor.rgb, _RimColor.rgb, rim * .83);
                return half4(color, fade);
            }
            ENDHLSL
        }
    }
}
