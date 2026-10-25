Shader "Catchline/RodViewCue"
{
    Properties { _Tint("Sea glass",Color)=(.67,.94,.91,.64) }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "Queue"="Transparent+110" "RenderType"="Transparent" }
        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha ZWrite Off ZTest Always Cull Off
            HLSLPROGRAM
            #pragma vertex Vert
            #pragma fragment Frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
            CBUFFER_START(UnityPerMaterial)
            half4 _Tint;
            CBUFFER_END
            struct V { float4 positionCS:SV_POSITION; float3 world:TEXCOORD0; };
            V Vert(float4 positionOS:POSITION)
            { V o; o.world=TransformObjectToWorld(positionOS.xyz); o.positionCS=TransformWorldToHClip(o.world); return o; }
            half4 Frag(V i):SV_Target
            {
                float depth=LinearEyeDepth(SampleSceneDepth(GetNormalizedScreenSpaceUV(i.positionCS)),_ZBufferParams);
                float eye=-TransformWorldToView(i.world).z;
                clip(depth-eye+.06);
                return _Tint;
            }
            ENDHLSL
        }
    }
}
