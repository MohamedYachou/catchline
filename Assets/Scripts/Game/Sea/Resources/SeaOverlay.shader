Shader "Catchline/Sea Overlay"
{
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent+10" "RenderPipeline"="UniversalPipeline" }
        Pass
        {
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            struct Attributes { float4 positionOS : POSITION; half4 color : COLOR; };
            struct Varyings { float4 positionCS : SV_POSITION; half4 color : COLOR; };
            Varyings vert(Attributes input)
            {
                Varyings o; o.positionCS = TransformObjectToHClip(input.positionOS.xyz); o.color = input.color; return o;
            }
            half4 frag(Varyings input) : SV_Target { return input.color; }
            ENDHLSL
        }
    }
}
