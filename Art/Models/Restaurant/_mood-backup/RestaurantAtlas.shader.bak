Shader "Catchline/RestaurantAtlas"
{
    Properties { _BaseMap("Painted atlas",2D)="white"{} _SurfaceMap("R roughness G metal B glow",2D)="black"{} }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
        Pass
        {
            Tags { "LightMode"="UniversalForward" }
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _ADDITIONAL_LIGHTS
            #pragma multi_compile _ _FORWARD_PLUS
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            struct A { float4 vertex:POSITION; float3 normal:NORMAL; float2 uv:TEXCOORD0; float4 color:COLOR; };
            struct V { float4 position:SV_POSITION; float2 uv:TEXCOORD0; float3 normal:TEXCOORD1; float3 world:TEXCOORD2; float4 color:COLOR; };
            TEXTURE2D(_BaseMap);SAMPLER(sampler_BaseMap);
            TEXTURE2D(_SurfaceMap);SAMPLER(sampler_SurfaceMap);
            V Vert(A i){V o;o.world=TransformObjectToWorld(i.vertex.xyz);o.position=TransformWorldToHClip(o.world);o.normal=TransformObjectToWorldNormal(i.normal);o.uv=i.uv;o.color=i.color;return o;}
            half4 Frag(V i):SV_Target
            {
                half3 base=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,i.uv).rgb*i.color.rgb;
                half3 surface=SAMPLE_TEXTURE2D(_SurfaceMap,sampler_SurfaceMap,i.uv).rgb;
                half3 n=normalize(i.normal);Light sun=GetMainLight();
                half3 lighting=half3(.28,.33,.43)+sun.color*saturate(dot(n,sun.direction))*.65;
                // Warm practicals (lanterns, windows, candles); Forward+ on PC walks its light clusters instead of a per-object list.
                #if defined(_ADDITIONAL_LIGHTS) || defined(_FORWARD_PLUS)
                InputData inputData=(InputData)0;inputData.positionWS=i.world;inputData.normalizedScreenSpaceUV=GetNormalizedScreenSpaceUV(i.position);
                uint count=GetAdditionalLightsCount();
                LIGHT_LOOP_BEGIN(count)
                    Light l=GetAdditionalLight(lightIndex,i.world);lighting+=l.color*l.distanceAttenuation*saturate(dot(n,l.direction)*.75+.25);
                LIGHT_LOOP_END
                #endif
                half3 view=normalize(GetWorldSpaceViewDir(i.world));half3 h=normalize(sun.direction+view);
                half spec=pow(saturate(dot(n,h)),lerp(64,8,surface.r))*(.05+surface.g*.3);
                return half4(base*lighting+base*surface.b*2.8+spec,1);
            }
            ENDHLSL
        }
    }
}
