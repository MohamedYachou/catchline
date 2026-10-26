// Codex 2's painted night sea under the restaurant: the blue ripples tile in world space and drift slowly; the gold
// lantern streaks are a second, additive layer in front of the quay that shimmers a little.
Shader "Catchline/RestaurantSea"
{
    Properties { _BaseMap("Painted water",2D)="black"{} _Repeat("Metres per tile",Float)=8 _Gain("Gain",Float)=1 _Drift("Drift",Vector)=(.02,.01,0,0)
        [Enum(UnityEngine.Rendering.BlendMode)] _Src("Src",Float)=1 [Enum(UnityEngine.Rendering.BlendMode)] _Dst("Dst",Float)=0 _ZWrite("ZWrite",Float)=1 _Shimmer("Shimmer",Float)=0 }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" "Queue"="Geometry" }
        Pass
        {
            Tags { "LightMode"="UniversalForward" }
            Blend [_Src] [_Dst] ZWrite [_ZWrite]
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            struct A { float4 vertex:POSITION; float2 uv:TEXCOORD0; };
            struct V { float4 position:SV_POSITION; float2 uv:TEXCOORD0; float3 world:TEXCOORD1; };
            TEXTURE2D(_BaseMap);SAMPLER(sampler_BaseMap);
            float _Repeat,_Gain,_Shimmer;float4 _Drift;
            V Vert(A i){V o;o.world=TransformObjectToWorld(i.vertex.xyz);o.position=TransformWorldToHClip(o.world);o.uv=i.uv;return o;}
            half4 Frag(V i):SV_Target
            {
                float2 uv=_Repeat>0?i.world.xz/_Repeat+_Drift.xy*_Time.y:i.uv*float2(2,1); // the streak sheet repeats twice across the quay
                half3 c=SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,uv).rgb*_Gain;
                c*=1+_Shimmer*sin(_Time.y*2.3+i.world.x*3.1)*sin(_Time.y*1.7+i.world.z*2.3);
                return half4(c,1);
            }
            ENDHLSL
        }
    }
}
