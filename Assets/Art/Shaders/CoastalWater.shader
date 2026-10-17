Shader "Catchline/Coastal Water"
{
 Properties
 {
  [MainColor] _BaseColor("Biome sea colour",Color)=(.04,.53,.61,1)
  _ShallowColor("Shallows",Color)=(.09,.72,.65,1)
  _DepthRange("Depth colour range (metres)",Float)=3.5
  [Normal] _Ripples("Ripples",2D)="bump"{}
  [Normal] _Crossing("Crossing ripples",2D)="bump"{}
  _NormalScale("Ripple tiling",Float)=.55
  _NormalStrength("Ripple strength",Range(0,2))=.35
  _WaveAmplitude("Wave height (metres)",Float)=.018
  _FoamColor("Foam",Color)=(.78,.97,.94,1)
  _FoamWidth("Shore foam width",Float)=.14
  _BoatCenter("Boat centre",Vector)=(1,0,.5,0)
  _BoatShape("Hull radii / travelling",Vector)=(2.1,1.2,0,0)
  _Clock("Voyage clock",Float)=0
  _Impact("Splash x/z/time/size",Vector)=(0,0,-100,0)
 }
 SubShader
 {
  Tags {"RenderPipeline"="UniversalPipeline" "RenderType"="Transparent" "Queue"="Transparent-20"}
  Pass
  {
   Name "CoastalWater"
   Tags {"LightMode"="UniversalForward"}
   ZWrite Off
   HLSLPROGRAM
   #pragma vertex Vert
   #pragma fragment Frag
   #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
   #pragma multi_compile_fragment _ _SHADOWS_SOFT
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"
   #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareOpaqueTexture.hlsl"
   #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Packing.hlsl"
   TEXTURE2D(_Ripples); SAMPLER(sampler_Ripples);
   TEXTURE2D(_Crossing); SAMPLER(sampler_Crossing);
   CBUFFER_START(UnityPerMaterial)
    half4 _BaseColor, _ShallowColor, _FoamColor;
    float4 _BoatCenter, _BoatShape, _Impact;
    float _DepthRange, _NormalScale, _NormalStrength, _WaveAmplitude, _FoamWidth, _Clock;
   CBUFFER_END
   struct A {float4 positionOS:POSITION;};
   struct V {float4 positionCS:SV_POSITION; float3 ws:TEXCOORD0;};
   V Vert(A input)
   {
    V o; float3 p=TransformObjectToWorld(input.positionOS.xyz);
    p.y += _WaveAmplitude*(sin(dot(p.xz,float2(.9,.42))*1.5+_Clock*.8)
            +.45*sin(dot(p.xz,float2(-.5,.9))*2.4-_Clock*.65));
    o.ws=p; o.positionCS=TransformWorldToHClip(p); return o;
   }
   half4 Frag(V i):SV_Target
   {
    float2 uv=GetNormalizedScreenSpaceUV(i.positionCS);
    float raw=SampleSceneDepth(uv);
    #if !UNITY_REVERSED_Z
     raw=lerp(UNITY_NEAR_CLIP_VALUE,1,raw);
    #endif
    float3 bed=ComputeWorldSpacePosition(uv,raw,UNITY_MATRIX_I_VP);
    float depth=max(0,i.ws.y-bed.y);
    float2 flow=float2(.018,.011)*_Clock;
    half3 a=UnpackNormal(SAMPLE_TEXTURE2D(_Ripples,sampler_Ripples,i.ws.xz*_NormalScale+flow));
    half3 b=UnpackNormal(SAMPLE_TEXTURE2D(_Crossing,sampler_Crossing,i.ws.xz*_NormalScale*.69-flow*.72));
    half2 slope=(a.xy+b.xy*.55)*_NormalStrength;
    half3 n=normalize(half3(slope.x,1,slope.y));
    half3 view=GetWorldSpaceNormalizeViewDir(i.ws);
    Light sun=GetMainLight(TransformWorldToShadowCoord(i.ws));
    half3 halfDir=SafeNormalize(view+sun.direction);
    half spec=pow(saturate(dot(n,halfDir)),72)*.30;
    half broad=pow(saturate(dot(n,halfDir)),12)*.035;
    half fresnel=pow(1-saturate(dot(n,view)),4);
    half absorb=1-exp(-depth/max(.1,_DepthRange));
    half3 sea=lerp(_ShallowColor.rgb*.8,_BaseColor.rgb*half3(.45,.73,.80),absorb);
    float2 refracted=uv+slope*.006*saturate(depth);
    float rDepth=SampleSceneDepth(refracted);
    #if !UNITY_REVERSED_Z
     rDepth=lerp(UNITY_NEAR_CLIP_VALUE,1,rDepth);
    #endif
    float3 rBed=ComputeWorldSpacePosition(refracted,rDepth,UNITY_MATRIX_I_VP);
    // Refraction must not pull an above-water hull or quay into the sea.
    half3 bottom=SampleSceneColor(rBed.y>i.ws.y ? uv : refracted);
    half visibility=exp(-depth*.75)*.72;
    half ridges=pow(saturate(1-abs(a.x+b.y)*2.3),9);
    bottom=bottom*half3(.42,.87,.80)+ridges*.065*exp(-depth*.8)*_ShallowColor.rgb;
    sea=lerp(sea,bottom,visibility);
    // Broad turquoise light patches sit below the small surface highlights.
    half facets=smoothstep(-.22,.32,a.x+b.y*.55);
    sea*=lerp(.83,1.06,facets);
    sea+=_ShallowColor.rgb*pow(saturate(a.y*.7+b.x*.3+.3),3)*.07*(1-absorb*.6);
    sea*=lerp(.58,1,sun.shadowAttenuation);
    sea+=sun.color*(spec+broad)*sun.shadowAttenuation;
    sea=lerp(sea,half3(.39,.69,.73),fresnel*.3);
    half edge=1-smoothstep(_FoamWidth*.15,_FoamWidth,depth);
    half broken=smoothstep(-.05,.30,a.x+b.y);
    half foam=edge*broken*.72;
    float2 relative=i.ws.xz-_BoatCenter.xz;
    float angle=_BoatShape.w;
    relative=float2(cos(angle)*relative.x-sin(angle)*relative.y,sin(angle)*relative.x+cos(angle)*relative.y);
    float ellipse=length(relative/max(_BoatShape.xy,float2(.1,.1)));
    half contact=(1-smoothstep(.006,.035,abs(ellipse-1)))*broken;
    foam=max(foam,contact*.38);
    float stern=relative.x;
    float width=.75+max(0,stern-1.4)*.38;
    float wake=exp(-pow((abs(relative.y)-width)*17,2))*smoothstep(1.4,2.0,stern)*(1-smoothstep(2.2,4.0,stern));
    foam=max(foam,wake*_BoatShape.z*broken*.3);
    float age=max(0,_Clock-_Impact.z), radius=length(i.ws.xz-_Impact.xy);
    float splash=exp(-pow((radius-age*.8)*24,2))*saturate(1-age/1.2)*_Impact.w;
    foam=max(foam,splash*.5);
    return half4(lerp(sea,_FoamColor.rgb,saturate(foam)),1);
   }
   ENDHLSL
  }
 }
}
