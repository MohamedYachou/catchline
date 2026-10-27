// Soft additive light for lamp glows and the lighthouse beam: colour times the mesh's vertex alpha, added over the
// scene, two-sided, no depth writes. Lives in Resources so builds keep it.
Shader "Catchline/GlowAdditive"
{
    Properties { _Color ("Colour", Color) = (1, .906, .639, 1) _Strength ("Strength", Float) = 1 }
    SubShader
    {
        Tags { "Queue" = "Transparent" "RenderType" = "Transparent" "IgnoreProjector" = "True" }
        Blend One One
        ZWrite Off
        Cull Off
        Pass
        {
            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"
            fixed4 _Color; float _Strength;
            struct appdata { float4 vertex : POSITION; fixed4 color : COLOR; };
            struct v2f { float4 pos : SV_POSITION; fixed4 color : COLOR; };
            v2f vert(appdata v) { v2f o; o.pos = UnityObjectToClipPos(v.vertex); o.color = v.color; return o; }
            fixed4 frag(v2f i) : SV_Target { return fixed4(_Color.rgb * i.color.a * _Strength, 0); }
            ENDCG
        }
    }
}
