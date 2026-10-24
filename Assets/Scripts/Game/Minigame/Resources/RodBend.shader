Shader "Catchline/RodBend"
{
    Properties { _BaseColor("Color", Color) = (1,1,1,1) _BaseMap("Atlas", 2D) = "white" {} }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" }
        Pass
        {
            Tags { "LightMode"="UniversalForward" }
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
            CBUFFER_START(UnityPerMaterial)
            float4 _BaseColor; float4 _BaseMap_ST;
            CBUFFER_END
            float4x4 _WorldToRod, _RodToWorld; float _Bend;
            struct A { float4 positionOS:POSITION; float3 normalOS:NORMAL; float2 uv:TEXCOORD0; };
            struct V { float4 positionCS:SV_POSITION; float3 normalWS:TEXCOORD0; float2 uv:TEXCOORD1; float fog:TEXCOORD2; };
            V Vert(A i)
            {
                V o; float3 world = TransformObjectToWorld(i.positionOS.xyz);
                float3 p = mul(_WorldToRod, float4(world,1)).xyz;
                p.y -= _Bend * pow(max(0,p.z) / 2, 2);
                world = mul(_RodToWorld,float4(p,1)).xyz;
                o.positionCS = TransformWorldToHClip(world); o.normalWS = TransformObjectToWorldNormal(i.normalOS);
                o.uv = TRANSFORM_TEX(i.uv,_BaseMap); o.fog = ComputeFogFactor(o.positionCS.z); return o;
            }
            half4 Frag(V i):SV_Target
            {
                Light sun = GetMainLight(); half shade = .58 + .42 * saturate(dot(normalize(i.normalWS),sun.direction));
                half3 color = SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.uv).rgb * _BaseColor.rgb * shade;
                return half4(MixFog(color,i.fog),1);
            }
            ENDHLSL
        }
    }
}
