Shader "Hidden/Catchline/Coastal UI Composite"
{
    Properties { _MainTex("Native UI", 2D) = "black" {} }
    SubShader
    {
        Tags { "RenderType"="Transparent" }
        Pass
        {
            ZWrite Off ZTest Always Cull Off
            Blend One OneMinusSrcAlpha
            HLSLPROGRAM
            #pragma vertex vert_img
            #pragma fragment frag
            #include "UnityCG.cginc"
            sampler2D _MainTex;
            half4 frag(v2f_img i) : SV_Target { return tex2D(_MainTex, i.uv); }
            ENDHLSL
        }
    }
}
