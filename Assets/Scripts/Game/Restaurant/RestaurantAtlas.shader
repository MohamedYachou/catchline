Shader "Catchline/RestaurantAtlas"
{
    Properties { _BaseMap("Painted atlas",2D)="white"{} _SurfaceMap("R roughness G metal B glow",2D)="black"{} }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" "Queue"="Geometry" }

        // Lit pass: real shadows, shaped ambient from the scene probe, environment reflections and the atlas glow.
        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForward" }
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
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
                half rough=surface.r,metal=surface.g,glow=surface.b;
                half3 n=normalize(i.normal);half3 view=normalize(GetWorldSpaceViewDir(i.world));
                // Main light with a soft shadow so furniture, crew and guests ground on the floor.
                float4 shadowCoord=TransformWorldToShadowCoord(i.world);
                Light sun=GetMainLight(shadowCoord);
                // Shaped ambient from the scene probe (the warm/cool Trilight set in RestaurantWorld) instead of a flat constant.
                half3 ambient=SampleSH(n);
                half3 lighting=ambient+sun.color*saturate(dot(n,sun.direction))*sun.shadowAttenuation*.9;
                // Warm practicals (lanterns, windows, candles); Forward+ on PC walks its light clusters instead of a per-object list.
                #if defined(_ADDITIONAL_LIGHTS) || defined(_FORWARD_PLUS)
                InputData inputData=(InputData)0;inputData.positionWS=i.world;inputData.normalizedScreenSpaceUV=GetNormalizedScreenSpaceUV(i.position);
                uint count=GetAdditionalLightsCount();
                LIGHT_LOOP_BEGIN(count)
                    Light l=GetAdditionalLight(lightIndex,i.world);lighting+=l.color*l.distanceAttenuation*l.shadowAttenuation*saturate(dot(n,l.direction)*.75+.25);
                LIGHT_LOOP_END
                #endif
                half3 col=base*lighting;
                // Sun specular.
                half3 h=normalize(sun.direction+view);
                col+=sun.color*pow(saturate(dot(n,h)),lerp(64,8,rough))*(.05+metal*.3)*sun.shadowAttenuation;
                // Environment reflection (the room's realtime probe): life on glass, plates, metal and polished wood. Adds only.
                half fres=pow(1-saturate(dot(n,view)),4);
                half3 refl=GlossyEnvironmentReflection(reflect(-view,n),rough,1);
                col+=refl*(metal*.6+fres*.25)*(1-rough*.6);
                // Glow (lanterns / windows) pushes past 1.0 into HDR so the grade's bloom catches it.
                col+=base*glow*2.8;
                return half4(col,1);
            }
            ENDHLSL
        }

        // Cast shadows into the main light's shadowmap.
        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode"="ShadowCaster" }
            ZWrite On ZTest LEqual ColorMask 0
            HLSLPROGRAM
            #pragma vertex SVert
            #pragma fragment SFrag
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Shadows.hlsl"
            float3 _LightDirection;float3 _LightPosition;
            struct SA{float4 vertex:POSITION;float3 normal:NORMAL;};
            struct SV{float4 position:SV_POSITION;};
            SV SVert(SA i)
            {
                SV o;
                float3 positionWS=TransformObjectToWorld(i.vertex.xyz);
                float3 normalWS=TransformObjectToWorldNormal(i.normal);
                #if _CASTING_PUNCTUAL_LIGHT_SHADOW
                    float3 lightDir=normalize(_LightPosition-positionWS);
                #else
                    float3 lightDir=_LightDirection;
                #endif
                float4 positionCS=TransformWorldToHClip(ApplyShadowBias(positionWS,normalWS,lightDir));
                #if UNITY_REVERSED_Z
                    positionCS.z=min(positionCS.z,UNITY_NEAR_CLIP_VALUE);
                #else
                    positionCS.z=max(positionCS.z,UNITY_NEAR_CLIP_VALUE);
                #endif
                o.position=positionCS;return o;
            }
            half4 SFrag(SV i):SV_Target{return 0;}
            ENDHLSL
        }

        // Write into the camera depth texture so SSAO grounds the room and the far sea reads behind it.
        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode"="DepthOnly" }
            ZWrite On ColorMask R
            HLSLPROGRAM
            #pragma vertex DVert
            #pragma fragment DFrag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            struct DA{float4 vertex:POSITION;};
            struct DV{float4 position:SV_POSITION;};
            DV DVert(DA i){DV o;o.position=TransformObjectToHClip(i.vertex.xyz);return o;}
            half4 DFrag(DV i):SV_Target{return 0;}
            ENDHLSL
        }
    }
}
