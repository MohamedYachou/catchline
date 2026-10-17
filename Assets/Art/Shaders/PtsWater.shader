Shader "Catchline/PTS Water"
{
    Properties
    {
        [MainColor] _BaseColor("Voyage colour", Color) = (.06,.76,.8,1)
        _Clock("Voyage clock", Float) = 0
        _DetailScale("Map scale for surface detail", Float) = 4
        _WaveSteepness("Gentle wave steepness", Range(0,1)) = .55
        _WaterSmoothness("Water smoothness", Range(0,1)) = .78
        _SpecularStrength("Sun reflection strength", Range(0,1)) = .12
        _AbsorptionColor("PTS absorption (linear)", Vector) = (.06,.76,.8,1)
        _ScatteringColor("PTS scattering (linear)", Vector) = (.025,.31,.43,1)
        _MaxDepth("Visibility in metres", Float) = 3
        _MaxWaveHeight("Wave height", Float) = .12
        _BoatAttack_Water_DistanceBlend("Surface range", Float) = 256
        _BoatAttack_Water_MicroWaveIntensity("Surface ripples", Float) = .14
        _BoatAttack_water_FoamIntensity("Foam disabled", Float) = 0
        _SurfaceNormals("PTS packed surface normals", 2D) = "gray" {}
        _DitherPattern("PTS shadow dither", 2D) = "gray" {}
        _WaterBufferA("Neutral interaction buffer", 2D) = "gray" {}
        _WaterBufferB("Neutral depth buffer", 2D) = "gray" {}
        _FoamMap("Unused foam", 2D) = "black" {}
        _BoatAttack_RampTexture("Wave profile", 2D) = "white" {}
        _CubemapTexture("Coastal sky reflection", Cube) = "" {}
        [Toggle(_STATIC_SHADER)] _Static ("Static", Float) = 0
    }
    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent-100" "RenderPipeline" = "UniversalPipeline" }
        ZWrite On
        Cull off

        Blend SrcAlpha OneMinusSrcAlpha // Traditional transparency

        Pass
        {
            Name "WaterShading"
            Tags{"LightMode" = "UniversalForward"}

            HLSLPROGRAM
            #pragma target 3.5
            #pragma multi_compile _ _CLUSTER_LIGHT_LOOP
            #pragma prefer_hlslcc gles
            /////////////////SHADER FEATURES//////////////////
            #define _REFLECTION_CUBEMAP 1
            // Bounded adapter: unused open-ocean variant omitted.
            // Bounded adapter: unused open-ocean variant omitted.
            #pragma shader_feature_local _STATIC_SHADER
            // Bounded adapter: unused open-ocean variant omitted.

            // Bounded adapter: unused open-ocean variant omitted. 
            // Bounded adapter: unused open-ocean variant omitted. 

            // Universal Pipeline keywords/
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            // Bounded adapter: unused open-ocean variant omitted.
            // Bounded adapter: unused open-ocean variant omitted.
            // Bounded adapter: unused open-ocean variant omitted.
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fragment _ _LIGHT_COOKIES
            // Bounded adapter: unused open-ocean variant omitted.
            
            #if UNITY_VERSION >= 202330
            #include_with_pragmas "Packages/com.unity.render-pipelines.core/ShaderLibrary/FoveatedRenderingKeywords.hlsl"
            // Bounded adapter: unused open-ocean variant omitted.
            #endif

            //--------------------------------------
            // GPU Instancing
            #pragma multi_compile_instancing			
            #pragma multi_compile_fog

            ////////////////////INCLUDES//////////////////////
            #include "PtsWater/WaterCommon.hlsl"

            //non-tess
            #pragma vertex WaterVertex
            #pragma fragment WaterFragment

            ENDHLSL
        }
    }
    FallBack "Hidden/InternalErrorShader"
}
