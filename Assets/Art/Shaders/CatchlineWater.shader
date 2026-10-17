Shader "Catchline/Illustrated Water"
{
    Properties
    {
        [MainColor] _BaseColor("Sea colour", Color) = (0.086,0.56,0.62,1)
        _WaterTile("Broad water pattern", 2D) = "white" {}
        _BoatCenter("Boat centre", Vector) = (1,0,0.5,0)
        _BoatShape("Hull radii / travelling", Vector) = (2.1,1.2,0,0)
        _Clock("Voyage clock", Float) = 0
        _Impact("Splash x/z/time/size", Vector) = (0,0,-100,0)
    }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" "Queue"="Geometry" }
        Pass
        {
            Name "IllustratedSea"
            Tags { "LightMode"="UniversalForward" }
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            TEXTURE2D(_WaterTile); SAMPLER(sampler_WaterTile);
            CBUFFER_START(UnityPerMaterial)
                half4 _BaseColor;
                float4 _BoatCenter, _BoatShape, _Impact;
                float _Clock;
            CBUFFER_END
            struct Attributes { float4 positionOS : POSITION; };
            struct Varyings { float4 positionCS : SV_POSITION; float3 positionWS : TEXCOORD0; };
            Varyings Vert(Attributes i)
            {
                Varyings o; o.positionWS = TransformObjectToWorld(i.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(o.positionWS); return o;
            }
            float Hash(float2 p) { return frac(sin(dot(p,float2(127.1,311.7)))*43758.5453); }
            float Noise(float2 p)
            {
                float2 cell=floor(p), f=frac(p); f=f*f*(3-2*f);
                return lerp(lerp(Hash(cell),Hash(cell+float2(1,0)),f.x),lerp(Hash(cell+float2(0,1)),Hash(cell+1),f.x),f.y);
            }
            half4 Frag(Varyings i) : SV_Target
            {
                float2 p=i.positionWS.xz; float t=_Clock;
                float broad=Noise(p*.13+float2(t*.012,-t*.008));
                float2 uv=p*.105+float2(t*.008,t*.003);
                half3 tex=SAMPLE_TEXTURE2D(_WaterTile,sampler_WaterTile,uv).rgb;
                float pattern=dot(tex,half3(.2126,.7152,.0722));
                half3 deep=_BaseColor.rgb*half3(.65,.80,.85);
                half3 light=_BaseColor.rgb*half3(1.50,1.35,1.20);
                half3 water=lerp(deep,light,saturate(broad*.72+pattern*.34));
                float flow=sin(p.x*.82+p.y*.42+t*.30)+sin(p.y*1.17-p.x*.20-t*.22);
                float glint=smoothstep(1.70,1.96,flow)*.10;
                water=lerp(water,half3(.55,.83,.80),glint);
                float2 drift=(p+float2(t*.065,t*.018))/3.8;
                float2 cell=floor(drift), local=frac(drift)-.5;
                float curve=local.y-sin(local.x*7+Hash(cell)*6.28)*.045;
                float stroke=(1-smoothstep(.003,.012,abs(curve)))*(1-smoothstep(.17,.31,abs(local.x)))*step(.65,Hash(cell));
                water=lerp(water,light*1.18,stroke*.35);
                float2 delta=p-_BoatCenter.xz;
                float ellipse=length(delta/max(_BoatShape.xy,float2(.1,.1)));
                float broken=smoothstep(.30,.74,Noise(p*3.5+float2(t*.12,0)));
                float foam=(1-smoothstep(.004,.027,abs(ellipse-1)))*broken;
                // The bow points along -X; the travelling wake opens behind the stern.
                float wakeX=delta.x-_BoatShape.x;
                float wakeBand=abs(abs(delta.y)-wakeX*.30);
                float wake=(1-smoothstep(.03,.15,wakeBand))*saturate(1-wakeX/6)*step(.1,wakeX)*_BoatShape.z*.5;
                float age=t-_Impact.z;
                float ring=abs(length(p-_Impact.xy)-age*1.3);
                float splash=(1-smoothstep(.025,.11,ring))*saturate(1-age/1.3)*step(0,age)*_Impact.w;
                Light sun=GetMainLight(TransformWorldToShadowCoord(i.positionWS));
                water*=lerp(.83,1,sun.shadowAttenuation);
                water=lerp(water,half3(.83,.94,.86),saturate(foam*.32+wake+splash*.7));
                return half4(water,1);
            }
            ENDHLSL
        }
    }
}
