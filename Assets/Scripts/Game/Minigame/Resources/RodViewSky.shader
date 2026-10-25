Shader "Catchline/RodViewSky"
{
    SubShader
    {
        // Draw after URP's skybox, before the transparent sea. The dome writes no depth.
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Transparent-400" "RenderType"="Background" }
        Pass
        {
            Tags { "LightMode"="UniversalForward" }
            Cull Off ZWrite Off ZTest LEqual
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            float _Clock, _CloudHeading;
            struct V { float4 positionCS:SV_POSITION; float3 direction:TEXCOORD0; };
            V Vert(float4 positionOS:POSITION)
            {
                V o; o.direction = TransformObjectToWorld(positionOS.xyz) - _WorldSpaceCameraPos;
                o.positionCS = TransformWorldToHClip(TransformObjectToWorld(positionOS.xyz)); return o;
            }
            float Puff(float2 p, float2 centre, float2 radius)
            { return 1-smoothstep(.56, 1, length((p-centre)/radius)); }
            half4 Frag(V i):SV_Target
            {
                float3 d = normalize(i.direction);
                float elevation = max(0,d.y);
                half3 sky = lerp(half3(.40,.66,.80),half3(.12,.40,.66),smoothstep(0,.30,elevation));
                sky = lerp(half3(.76,.86,.84),sky,smoothstep(0,.055,elevation));
                float angle = atan2(d.z,d.x);
                float2 p = float2(angle + _Clock*.0008, d.y);
                float cloud = 0;
                // Three quiet, broad cloud banks, each with a low faceted silhouette and soft edges.
                for (int n=0;n<3;n++)
                {
                    float x = _CloudHeading - .42+n*.4;
                    float2 q = float2(atan2(sin(p.x-x),cos(p.x-x)),p.y);
                    float h = .105 + .025*sin(n*2.3);
                    float bank = max(Puff(q,float2(-.065,h),float2(.11,.022)),
                        max(Puff(q,float2(.01,h+.012),float2(.095,.03)),Puff(q,float2(.09,h),float2(.12,.018))));
                    cloud = max(cloud,bank);
                }
                sky = lerp(sky,half3(.94,.95,.89),cloud*.72*smoothstep(.025,.07,elevation));
                return half4(sky,1);
            }
            ENDHLSL
        }
    }
}
